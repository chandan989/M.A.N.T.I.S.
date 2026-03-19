"""
M.A.N.T.I.S. — Hedera Skill
On-chain reads and writes via the Hedera JSON-RPC Relay (web3.py) and Mirror Node REST API.

This skill handles:
  - Reading vault / contract state from the Hedera mirror node
  - Querying account HBAR and token balances
  - Signing and submitting Bonzo Vault transactions via the Hedera JSON-RPC Relay
    (EVM-compatible calls using web3.py)

Network configuration:
  - Testnet RPC:   https://testnet.hashio.io/api
  - Testnet Mirror: https://testnet.mirrornode.hedera.com
  - Mainnet RPC:   https://mainnet.hashio.io/api
  - Mainnet Mirror: https://mainnet.mirrornode.hedera.com
"""

from __future__ import annotations

import time
from typing import Any

import httpx
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

from mantis.config import get_settings
from mantis.contracts import BONZO_VAULT_ABI
from mantis.logging import get_agent_logger, get_tx_logger
from mantis.skills import Skill
from mantis.types import ExecutionResult, VaultState

logger = get_agent_logger()
tx_logger = get_tx_logger()


def _account_id_to_evm_address(account_id: str) -> str | None:
    """
    Convert a Hedera account ID (0.0.XXXXX) to its EVM address
    using the mirror node.
    """
    settings = get_settings()
    try:
        import httpx as _httpx
        resp = _httpx.get(
            f"{settings.resolved_mirror_url}/api/v1/accounts/{account_id}",
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            evm_address = data.get("evm_address", "")
            if evm_address:
                return Web3.to_checksum_address(evm_address)
    except Exception as exc:
        logger.warning(f"Hedera: Failed to resolve EVM address for {account_id}: {exc}")
    return None


class HederaSkill(Skill):
    name = "hedera"
    version = "2.0.0"

    def __init__(self) -> None:
        self._settings = get_settings()
        self._configured = bool(
            self._settings.hedera_account_id and self._settings.hedera_private_key
        )

        # ── Web3.py setup with Hedera JSON-RPC Relay ─────────────────────
        rpc_url = self._settings.resolved_rpc_url
        self._w3 = Web3(Web3.HTTPProvider(rpc_url))
        # Hedera uses PoA-style extra data in blocks
        self._w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        self._account: Any = None

        if self._configured:
            pk = self._settings.hedera_private_key
            # Ensure 0x prefix for hex private keys
            if not pk.startswith("0x"):
                pk = "0x" + pk
            try:
                self._account = self._w3.eth.account.from_key(pk)
                logger.info(
                    f"Hedera Skill: Initialized on {self._settings.hedera_network} — "
                    f"RPC={rpc_url}, "
                    f"account={self._settings.hedera_account_id}, "
                    f"EVM={self._account.address}"
                )
            except Exception as exc:
                logger.error(f"Hedera Skill: Failed to load private key — {exc}")
                self._configured = False
        else:
            logger.warning(
                f"Hedera Skill: Credentials not set — running in read-only mode. "
                f"RPC={rpc_url}"
            )

        # Check RPC connectivity
        try:
            chain_id = self._w3.eth.chain_id
            logger.info(f"Hedera Skill: Connected to chain ID {chain_id}")
        except Exception as exc:
            logger.warning(f"Hedera Skill: RPC not reachable — {exc}")

    # ── Read Operations ──────────────────────────────────────────────────

    async def collect(self) -> VaultState:
        """Read current vault state from mirror node and/or RPC."""
        vault_ids = self._settings.vault_id_list
        vault_id = vault_ids[0] if vault_ids else ""

        if vault_id:
            state = await self._read_vault_state(vault_id)
            if state:
                return state

        # Fallback: if no vault configured or read failed, use mock data
        logger.debug("Hedera Skill: Using mock vault data (no vault configured or read failed)")
        return VaultState(
            vault_id=vault_id or "0.0.0000000",
            strategy="HBAR/USDC CLMM",
            in_range=True,
            range_lower=0.075,
            range_upper=0.115,
            pending_rewards_usd=24.50,
            last_harvest_hours_ago=3.8,
            current_apy=14.2,
        )

    async def _read_vault_state(self, vault_id: str) -> VaultState | None:
        """
        Query vault state from the Hedera mirror node REST API.
        Tries to read contract state; falls back gracefully.
        """
        mirror = self._settings.resolved_mirror_url
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                # Check if the contract exists
                resp = await client.get(f"{mirror}/api/v1/contracts/{vault_id}")
                if resp.status_code != 200:
                    logger.warning(f"Hedera: Vault contract {vault_id} not found on mirror node")
                    return None

                contract_info = resp.json()
                evm_address = contract_info.get("evm_address", "")

                # Try to read contract state via web3 if we have the EVM address
                if evm_address and self._w3.is_connected():
                    return await self._read_vault_via_rpc(
                        vault_id, Web3.to_checksum_address(evm_address)
                    )

                logger.info(f"Hedera: Contract {vault_id} exists, EVM addr: {evm_address}")
                return VaultState(
                    vault_id=vault_id,
                    strategy="HBAR/USDC CLMM",
                    in_range=True,
                )

        except Exception as exc:
            logger.error(f"Hedera: Mirror node query failed — {exc}")
            return None

    async def _read_vault_via_rpc(
        self, vault_id: str, evm_address: str
    ) -> VaultState | None:
        """Read vault contract state via JSON-RPC using web3.py."""
        try:
            contract = self._w3.eth.contract(
                address=evm_address,
                abi=BONZO_VAULT_ABI,
            )

            # Try reading functions that may exist on the vault
            # These will fail gracefully if the ABI doesn't match
            vault_state = VaultState(vault_id=vault_id, strategy="HBAR/USDC CLMM")

            try:
                total = contract.functions.totalSupply().call()
                logger.debug(f"Hedera: Vault total supply = {total}")
            except Exception:
                pass  # ABI mismatch — expected until real ABI is configured

            try:
                lower, upper = contract.functions.getCurrentRange().call()
                vault_state.range_lower = lower / 1e18  # Adjust decimals per contract
                vault_state.range_upper = upper / 1e18
                vault_state.in_range = True
            except Exception:
                pass

            try:
                r0, r1 = contract.functions.getPendingRewards().call()
                vault_state.pending_rewards_usd = (r0 + r1) / 1e8  # Adjust per token decimals
            except Exception:
                pass

            return vault_state

        except Exception as exc:
            logger.warning(f"Hedera: RPC vault read failed — {exc}")
            return None

    async def get_balance(self) -> dict:
        """Get HBAR balance and token balances for the operator account."""
        account_id = self._settings.hedera_account_id
        mirror = self._settings.resolved_mirror_url

        if not account_id:
            return {"hbar": 0, "tokens": []}

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                # HBAR balance
                resp = await client.get(f"{mirror}/api/v1/balances?account.id={account_id}")
                hbar_balance = 0
                if resp.status_code == 200:
                    data = resp.json()
                    balances = data.get("balances", [])
                    if balances:
                        hbar_balance = balances[0].get("balance", 0) / 1e8  # tinybars to HBAR

                # Token balances
                resp = await client.get(f"{mirror}/api/v1/accounts/{account_id}/tokens")
                tokens = []
                if resp.status_code == 200:
                    data = resp.json()
                    tokens = data.get("tokens", [])

                logger.debug(f"Hedera: Balance — {hbar_balance:.4f} HBAR, {len(tokens)} tokens")
                return {"hbar": hbar_balance, "tokens": tokens}

        except Exception as exc:
            logger.error(f"Hedera: Balance query failed — {exc}")
            return {"hbar": 0, "tokens": [], "error": str(exc)}

    # ── Write Operations ─────────────────────────────────────────────────

    async def execute(self, params: dict) -> ExecutionResult:
        """Dispatch an action to the appropriate write method."""
        action = params.get("action", "")
        vault_id = params.get("vault_id", "")

        if not self._configured:
            return ExecutionResult(
                success=False,
                error="Hedera credentials not configured — cannot execute transactions",
            )

        if not self._account:
            return ExecutionResult(
                success=False,
                error="Hedera account not initialized — check private key format",
            )

        if action == "HARVEST":
            return await self.harvest(vault_id)
        elif action == "HARVEST_AND_SWAP":
            return await self.harvest_and_swap(vault_id)
        elif action in ("TIGHTEN_RANGE", "WIDEN_RANGE"):
            return await self.rebalance(
                vault_id,
                params.get("new_range_lower", 0),
                params.get("new_range_upper", 0),
            )
        elif action == "WITHDRAW_ALL":
            return await self.withdraw(vault_id, 100)
        else:
            return ExecutionResult(success=True, message=f"No-op action: {action}")

    async def _send_contract_tx(
        self, vault_evm_address: str, function_name: str, args: list | None = None
    ) -> ExecutionResult:
        """
        Build, sign, and send a contract transaction via the Hedera JSON-RPC Relay.
        """
        if not self._account:
            return ExecutionResult(success=False, error="No account configured")

        try:
            contract = self._w3.eth.contract(
                address=Web3.to_checksum_address(vault_evm_address),
                abi=BONZO_VAULT_ABI,
            )

            # Build transaction
            fn = getattr(contract.functions, function_name)
            if args:
                tx_data = fn(*args)
            else:
                tx_data = fn()

            nonce = self._w3.eth.get_transaction_count(self._account.address)
            gas_price = self._w3.eth.gas_price

            tx = tx_data.build_transaction({
                "from": self._account.address,
                "nonce": nonce,
                "gas": 300_000,  # Hedera default gas limit
                "gasPrice": gas_price,
                "chainId": self._w3.eth.chain_id,
            })

            # Sign transaction
            signed = self._w3.eth.account.sign_transaction(tx, self._account.key)

            # Submit via JSON-RPC relay
            tx_hash = self._w3.eth.send_raw_transaction(signed.raw_transaction)
            tx_hex = tx_hash.hex()

            logger.info(f"Hedera: Tx submitted — hash={tx_hex}")
            tx_logger.info(f"{function_name} | vault:{vault_evm_address} | tx:{tx_hex}")

            # Wait for receipt
            try:
                receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
                if receipt["status"] == 1:
                    logger.info(f"Hedera: Tx confirmed — hash={tx_hex}, block={receipt['blockNumber']}")
                    return ExecutionResult(
                        success=True,
                        tx_id=tx_hex,
                        message=f"{function_name} executed successfully (block {receipt['blockNumber']})",
                    )
                else:
                    logger.error(f"Hedera: Tx reverted — hash={tx_hex}")
                    return ExecutionResult(
                        success=False,
                        tx_id=tx_hex,
                        error=f"Transaction reverted on-chain",
                    )
            except Exception as exc:
                # Tx was submitted but we couldn't confirm — it may still succeed
                logger.warning(f"Hedera: Tx receipt timeout — hash={tx_hex}: {exc}")
                return ExecutionResult(
                    success=True,
                    tx_id=tx_hex,
                    message=f"{function_name} submitted (pending confirmation)",
                )

        except Exception as exc:
            logger.error(f"Hedera: Contract call failed — {exc}")
            return ExecutionResult(success=False, error=str(exc))

    async def _resolve_vault_evm_address(self, vault_id: str) -> str | None:
        """Resolve a Hedera contract ID to its EVM address via mirror node."""
        mirror = self._settings.resolved_mirror_url
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{mirror}/api/v1/contracts/{vault_id}")
                if resp.status_code == 200:
                    return resp.json().get("evm_address", "")
        except Exception as exc:
            logger.error(f"Hedera: Failed to resolve EVM address for {vault_id}: {exc}")
        return None

    async def harvest(self, vault_id: str) -> ExecutionResult:
        """Harvest pending rewards from a Bonzo Vault on-chain."""
        logger.info(f"Hedera: Executing HARVEST on vault {vault_id}")

        evm_addr = await self._resolve_vault_evm_address(vault_id)
        if not evm_addr:
            return ExecutionResult(
                success=False,
                error=f"Could not resolve EVM address for vault {vault_id}",
            )

        return await self._send_contract_tx(evm_addr, "harvest")

    async def harvest_and_swap(
        self, vault_id: str, to_token: str = "USDC"
    ) -> ExecutionResult:
        """Harvest rewards and swap them to a stablecoin."""
        logger.info(f"Hedera: Executing HARVEST_AND_SWAP on vault {vault_id} → {to_token}")

        # Step 1: Harvest
        harvest_result = await self.harvest(vault_id)
        if not harvest_result.success:
            return harvest_result

        # Step 2: Swap (requires SaucerSwap router integration)
        # TODO: Integrate SaucerSwap V2 router for on-chain swap
        logger.info(f"Hedera: Swap step pending — SaucerSwap integration required")
        return ExecutionResult(
            success=True,
            tx_id=harvest_result.tx_id,
            message=f"Harvested from vault {vault_id}. Swap to {to_token} pending SaucerSwap integration.",
        )

    async def rebalance(
        self, vault_id: str, new_lower: float, new_upper: float
    ) -> ExecutionResult:
        """Rebalance vault liquidity range on-chain."""
        logger.info(
            f"Hedera: Executing REBALANCE on vault {vault_id} "
            f"range=[{new_lower}, {new_upper}]"
        )

        evm_addr = await self._resolve_vault_evm_address(vault_id)
        if not evm_addr:
            return ExecutionResult(
                success=False,
                error=f"Could not resolve EVM address for vault {vault_id}",
            )

        # Convert price range to tick values (simplified — real impl depends on pool specifics)
        # TODO: Proper tick math based on SaucerSwap V2 tick spacing
        tick_lower = int(new_lower * 1e18)
        tick_upper = int(new_upper * 1e18)

        return await self._send_contract_tx(evm_addr, "rebalance", [tick_lower, tick_upper])

    async def withdraw(self, vault_id: str, percentage: int = 100) -> ExecutionResult:
        """Withdraw funds from a Bonzo Vault on-chain."""
        logger.info(f"Hedera: Executing WITHDRAW ({percentage}%) on vault {vault_id}")

        evm_addr = await self._resolve_vault_evm_address(vault_id)
        if not evm_addr:
            return ExecutionResult(
                success=False,
                error=f"Could not resolve EVM address for vault {vault_id}",
            )

        # Get user's vault shares to calculate withdrawal amount
        if self._account:
            try:
                contract = self._w3.eth.contract(
                    address=Web3.to_checksum_address(evm_addr),
                    abi=BONZO_VAULT_ABI,
                )
                shares = contract.functions.balanceOf(self._account.address).call()
                withdraw_shares = shares * percentage // 100
                return await self._send_contract_tx(evm_addr, "withdraw", [withdraw_shares])
            except Exception as exc:
                logger.error(f"Hedera: Failed to read shares — {exc}")
                return ExecutionResult(success=False, error=str(exc))

        return ExecutionResult(success=False, error="No account configured for withdrawal")

"""
M.A.N.T.I.S. — Bonzo Lend Skill
Reads and writes to Bonzo Finance's lending protocol (Aave v2 fork on Hedera).

This skill handles:
  - Reading user lending position (health factor, collateral, debt)
  - Reading reserve/market data (supply APY, borrow APY, TVL)
  - Executing lending operations: supply, withdraw, borrow, repay

Bonzo Lend is based on Aave v2, adapted for Hedera EVM + HTS.
Docs: https://docs.bonzo.finance
"""

from __future__ import annotations

import time
from typing import Any

import httpx
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

from mantis.config import get_settings
from mantis.contracts import BONZO_LENDING_POOL_ABI, BONZO_LENDING_TOKENS
from mantis.logging import get_agent_logger, get_tx_logger
from mantis.skills import Skill
from mantis.types import ExecutionResult, LendingPosition, LendingReserve

logger = get_agent_logger()
tx_logger = get_tx_logger()

# Aave v2 interest rate modes
RATE_MODE_STABLE = 1
RATE_MODE_VARIABLE = 2

# RAY = 10^27  (Aave v2 uses RAY for rate precision)
RAY = 10**27


class BonzoLendSkill(Skill):
    """
    Bonzo Finance Lending Protocol integration.
    Provides read/write access to the Aave v2-based lending pool on Hedera.
    """

    name = "bonzo_lend"
    version = "1.0.0"

    def __init__(self) -> None:
        self._settings = get_settings()
        self._enabled = self._settings.bonzo_lending_enabled
        self._configured = bool(
            self._settings.bonzo_lending_pool_id
            and self._settings.hedera_account_id
            and self._settings.hedera_private_key
        )

        # ── Web3.py setup ────────────────────────────────────────────────
        rpc_url = self._settings.resolved_rpc_url
        self._w3 = Web3(Web3.HTTPProvider(rpc_url))
        self._w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        self._account: Any = None

        if self._configured and self._enabled:
            pk = self._settings.hedera_private_key
            if not pk.startswith("0x"):
                pk = "0x" + pk
            try:
                self._account = self._w3.eth.account.from_key(pk)
                logger.info(
                    f"BonzoLend Skill: Initialized — "
                    f"pool={self._settings.bonzo_lending_pool_id}, "
                    f"EVM={self._account.address}"
                )
            except Exception as exc:
                logger.error(f"BonzoLend Skill: Failed to load key — {exc}")
                self._configured = False
        elif not self._enabled:
            logger.info("BonzoLend Skill: Disabled via config")
        else:
            logger.warning(
                "BonzoLend Skill: Not fully configured — "
                "running in read-only/mock mode"
            )

    # ── Read Operations ──────────────────────────────────────────────────

    async def collect(self) -> LendingPosition:
        """Read the user's lending position from Bonzo Lend."""
        if not self._enabled:
            return LendingPosition()

        if self._configured and self._account:
            position = await self._read_lending_position()
            if position:
                return position

        # Fallback: try Data API
        position = await self._read_from_data_api()
        if position:
            return position

        # Final fallback: mock data
        logger.debug("BonzoLend Skill: Using mock lending data")
        return LendingPosition(
            total_collateral_usd=1000.0,
            total_debt_usd=0.0,
            available_borrows_usd=750.0,
            liquidation_threshold=80.0,
            ltv=75.0,
            health_factor=999.0,
            net_apy=3.5,
        )

    async def _read_lending_position(self) -> LendingPosition | None:
        """Read user account data from the LendingPool contract via RPC."""
        pool_evm = await self._resolve_pool_evm_address()
        if not pool_evm or not self._account:
            return None

        try:
            contract = self._w3.eth.contract(
                address=Web3.to_checksum_address(pool_evm),
                abi=BONZO_LENDING_POOL_ABI,
            )

            result = contract.functions.getUserAccountData(
                self._account.address
            ).call()

            # Aave v2 returns values in ETH (HBAR on Hedera) with 18 decimals
            # Health factor is in WAD (18 decimals)
            total_collateral = result[0] / 1e18
            total_debt = result[1] / 1e18
            available_borrows = result[2] / 1e18
            liq_threshold = result[3] / 100  # basis points to percentage
            ltv = result[4] / 100
            health_factor = result[5] / 1e18

            logger.info(
                f"BonzoLend: Position — "
                f"collateral=${total_collateral:.2f}, "
                f"debt=${total_debt:.2f}, "
                f"health={health_factor:.2f}"
            )

            return LendingPosition(
                total_collateral_usd=total_collateral,
                total_debt_usd=total_debt,
                available_borrows_usd=available_borrows,
                liquidation_threshold=liq_threshold,
                ltv=ltv,
                health_factor=health_factor,
            )

        except Exception as exc:
            logger.warning(f"BonzoLend: RPC position read failed — {exc}")
            return None

    async def _read_from_data_api(self) -> LendingPosition | None:
        """Try to read position data from the Bonzo Data API."""
        api_url = self._settings.bonzo_data_api_url
        account_id = self._settings.hedera_account_id
        if not api_url or not account_id:
            return None

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{api_url}/accounts/{account_id}"
                )
                if resp.status_code != 200:
                    return None

                data = resp.json()
                return LendingPosition(
                    total_collateral_usd=float(data.get("totalCollateralUSD", 0)),
                    total_debt_usd=float(data.get("totalDebtUSD", 0)),
                    available_borrows_usd=float(data.get("availableBorrowsUSD", 0)),
                    health_factor=float(data.get("healthFactor", 999)),
                    ltv=float(data.get("ltv", 0)),
                )
        except Exception as exc:
            logger.debug(f"BonzoLend: Data API not available — {exc}")
            return None

    async def get_reserves(self) -> list[LendingReserve]:
        """Fetch reserve/market data for all supported assets."""
        if not self._enabled:
            return []

        # Try Data API first
        reserves = await self._read_reserves_from_api()
        if reserves:
            return reserves

        # Try on-chain read
        reserves = await self._read_reserves_on_chain()
        if reserves:
            return reserves

        # Mock fallback
        return [
            LendingReserve(
                asset="WHBAR",
                supply_apy=4.2,
                variable_borrow_apy=6.8,
                total_supplied_usd=5_000_000,
                total_borrowed_usd=2_000_000,
            ),
            LendingReserve(
                asset="USDC",
                supply_apy=3.1,
                variable_borrow_apy=5.5,
                total_supplied_usd=8_000_000,
                total_borrowed_usd=4_500_000,
            ),
        ]

    async def _read_reserves_from_api(self) -> list[LendingReserve] | None:
        """Try reading reserve data from the Bonzo Data API."""
        api_url = self._settings.bonzo_data_api_url
        if not api_url:
            return None

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{api_url}/markets")
                if resp.status_code != 200:
                    return None

                data = resp.json()
                reserves = []
                for market in data if isinstance(data, list) else data.get("markets", []):
                    reserves.append(LendingReserve(
                        asset=market.get("symbol", ""),
                        asset_address=market.get("evm_address", ""),
                        supply_apy=float(market.get("supplyAPY", 0)),
                        variable_borrow_apy=float(market.get("variableBorrowAPY", 0)),
                        stable_borrow_apy=float(market.get("stableBorrowAPY", 0)),
                        total_supplied_usd=float(market.get("totalSuppliedUSD", 0)),
                        total_borrowed_usd=float(market.get("totalBorrowedUSD", 0)),
                    ))
                return reserves if reserves else None
        except Exception as exc:
            logger.debug(f"BonzoLend: Reserve API not available — {exc}")
            return None

    async def _read_reserves_on_chain(self) -> list[LendingReserve] | None:
        """Read reserve list and data from on-chain contracts."""
        pool_evm = await self._resolve_pool_evm_address()
        if not pool_evm:
            return None

        try:
            contract = self._w3.eth.contract(
                address=Web3.to_checksum_address(pool_evm),
                abi=BONZO_LENDING_POOL_ABI,
            )

            reserve_addresses = contract.functions.getReservesList().call()
            reserves = []

            for addr in reserve_addresses[:10]:  # Limit to first 10
                try:
                    data = contract.functions.getReserveData(addr).call()
                    # currentLiquidityRate and currentVariableBorrowRate are in RAY
                    supply_apy = (data[3] / RAY) * 100  # Convert from RAY to %
                    borrow_apy = (data[4] / RAY) * 100

                    reserves.append(LendingReserve(
                        asset_address=addr,
                        supply_apy=round(supply_apy, 4),
                        variable_borrow_apy=round(borrow_apy, 4),
                    ))
                except Exception:
                    pass  # Skip reserves that fail to read

            return reserves if reserves else None

        except Exception as exc:
            logger.warning(f"BonzoLend: On-chain reserve read failed — {exc}")
            return None

    # ── Write Operations ─────────────────────────────────────────────────

    async def execute(self, params: dict) -> ExecutionResult:
        """Dispatch a lending action."""
        action = params.get("action", "")

        if not self._enabled:
            return ExecutionResult(
                success=False,
                error="Bonzo Lend is disabled in configuration",
            )

        if not self._configured or not self._account:
            return ExecutionResult(
                success=False,
                error="Bonzo Lend credentials not configured",
            )

        if action == "SUPPLY":
            return await self.supply(
                asset=params.get("asset", "WHBAR"),
                amount=params.get("amount", 0),
            )
        elif action == "WITHDRAW_SUPPLY":
            return await self.withdraw_supply(
                asset=params.get("asset", "WHBAR"),
                amount=params.get("amount", 0),
            )
        elif action == "BORROW":
            return await self.borrow(
                asset=params.get("asset", "USDC"),
                amount=params.get("amount", 0),
                rate_mode=params.get("rate_mode", RATE_MODE_VARIABLE),
            )
        elif action == "REPAY":
            return await self.repay(
                asset=params.get("asset", "USDC"),
                amount=params.get("amount", 0),
                rate_mode=params.get("rate_mode", RATE_MODE_VARIABLE),
            )
        else:
            return ExecutionResult(
                success=False,
                error=f"Unknown lending action: {action}",
            )

    async def supply(self, asset: str, amount: float) -> ExecutionResult:
        """Supply (deposit) assets into Bonzo Lend to earn yield."""
        logger.info(f"BonzoLend: SUPPLY {amount} {asset}")

        pool_evm = await self._resolve_pool_evm_address()
        asset_evm = self._resolve_token_address(asset)

        if not pool_evm or not asset_evm:
            return ExecutionResult(
                success=False,
                error=f"Cannot resolve addresses — pool={pool_evm}, asset={asset_evm}",
            )

        amount_wei = int(amount * 1e8)  # Hedera tokens typically use 8 decimals

        return await self._send_lending_tx(
            pool_evm,
            "deposit",
            [
                Web3.to_checksum_address(asset_evm),
                amount_wei,
                self._account.address,
                0,  # referralCode
            ],
        )

    async def withdraw_supply(self, asset: str, amount: float) -> ExecutionResult:
        """Withdraw supplied assets from Bonzo Lend."""
        logger.info(f"BonzoLend: WITHDRAW_SUPPLY {amount} {asset}")

        pool_evm = await self._resolve_pool_evm_address()
        asset_evm = self._resolve_token_address(asset)

        if not pool_evm or not asset_evm:
            return ExecutionResult(
                success=False,
                error=f"Cannot resolve addresses — pool={pool_evm}, asset={asset_evm}",
            )

        amount_wei = int(amount * 1e8)

        return await self._send_lending_tx(
            pool_evm,
            "withdraw",
            [
                Web3.to_checksum_address(asset_evm),
                amount_wei,
                self._account.address,
            ],
        )

    async def borrow(
        self, asset: str, amount: float, rate_mode: int = RATE_MODE_VARIABLE
    ) -> ExecutionResult:
        """Borrow assets from Bonzo Lend against supplied collateral."""
        logger.info(f"BonzoLend: BORROW {amount} {asset} (mode={rate_mode})")

        pool_evm = await self._resolve_pool_evm_address()
        asset_evm = self._resolve_token_address(asset)

        if not pool_evm or not asset_evm:
            return ExecutionResult(
                success=False,
                error=f"Cannot resolve addresses — pool={pool_evm}, asset={asset_evm}",
            )

        amount_wei = int(amount * 1e8)

        return await self._send_lending_tx(
            pool_evm,
            "borrow",
            [
                Web3.to_checksum_address(asset_evm),
                amount_wei,
                rate_mode,
                0,  # referralCode
                self._account.address,
            ],
        )

    async def repay(
        self, asset: str, amount: float, rate_mode: int = RATE_MODE_VARIABLE
    ) -> ExecutionResult:
        """Repay borrowed assets to Bonzo Lend."""
        logger.info(f"BonzoLend: REPAY {amount} {asset} (mode={rate_mode})")

        pool_evm = await self._resolve_pool_evm_address()
        asset_evm = self._resolve_token_address(asset)

        if not pool_evm or not asset_evm:
            return ExecutionResult(
                success=False,
                error=f"Cannot resolve addresses — pool={pool_evm}, asset={asset_evm}",
            )

        amount_wei = int(amount * 1e8)

        return await self._send_lending_tx(
            pool_evm,
            "repay",
            [
                Web3.to_checksum_address(asset_evm),
                amount_wei,
                rate_mode,
                self._account.address,
            ],
        )

    # ── Internal Helpers ─────────────────────────────────────────────────

    async def _send_lending_tx(
        self, pool_evm_address: str, function_name: str, args: list
    ) -> ExecutionResult:
        """Build, sign, and send a LendingPool transaction via Hedera JSON-RPC."""
        if not self._account:
            return ExecutionResult(success=False, error="No account configured")

        try:
            contract = self._w3.eth.contract(
                address=Web3.to_checksum_address(pool_evm_address),
                abi=BONZO_LENDING_POOL_ABI,
            )

            fn = getattr(contract.functions, function_name)
            tx_data = fn(*args)

            nonce = self._w3.eth.get_transaction_count(self._account.address)
            gas_price = self._w3.eth.gas_price

            tx = tx_data.build_transaction({
                "from": self._account.address,
                "nonce": nonce,
                "gas": 500_000,  # Lending ops: higher gas than simple tx
                "gasPrice": gas_price,
                "chainId": self._w3.eth.chain_id,
            })

            signed = self._w3.eth.account.sign_transaction(tx, self._account.key)
            tx_hash = self._w3.eth.send_raw_transaction(signed.raw_transaction)
            tx_hex = tx_hash.hex()

            logger.info(f"BonzoLend: Tx submitted — hash={tx_hex}")
            tx_logger.info(f"LEND:{function_name} | pool:{pool_evm_address} | tx:{tx_hex}")

            try:
                receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
                if receipt["status"] == 1:
                    logger.info(
                        f"BonzoLend: Tx confirmed — hash={tx_hex}, "
                        f"block={receipt['blockNumber']}"
                    )
                    return ExecutionResult(
                        success=True,
                        tx_id=tx_hex,
                        message=f"Lend:{function_name} executed (block {receipt['blockNumber']})",
                    )
                else:
                    logger.error(f"BonzoLend: Tx reverted — hash={tx_hex}")
                    return ExecutionResult(
                        success=False,
                        tx_id=tx_hex,
                        error="Transaction reverted on-chain",
                    )
            except Exception as exc:
                logger.warning(f"BonzoLend: Tx receipt timeout — {tx_hex}: {exc}")
                return ExecutionResult(
                    success=True,
                    tx_id=tx_hex,
                    message=f"Lend:{function_name} submitted (pending confirmation)",
                )

        except Exception as exc:
            logger.error(f"BonzoLend: Contract call failed — {exc}")
            return ExecutionResult(success=False, error=str(exc))

    async def _resolve_pool_evm_address(self) -> str | None:
        """Resolve the Bonzo LendingPool Hedera contract ID to its EVM address."""
        pool_id = self._settings.bonzo_lending_pool_id
        if not pool_id:
            return None

        mirror = self._settings.resolved_mirror_url
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{mirror}/api/v1/contracts/{pool_id}")
                if resp.status_code == 200:
                    evm_addr = resp.json().get("evm_address", "")
                    if evm_addr:
                        return evm_addr
        except Exception as exc:
            logger.error(f"BonzoLend: Failed to resolve pool EVM address — {exc}")
        return None

    def _resolve_token_address(self, token_symbol: str) -> str | None:
        """Get the EVM address for a token symbol."""
        network = self._settings.hedera_network
        tokens = BONZO_LENDING_TOKENS.get(network, {})
        addr = tokens.get(token_symbol.upper())
        if addr and addr != "0x0000000000000000000000000000000000000000":
            return addr
        logger.warning(f"BonzoLend: Token address not configured for {token_symbol}")
        return None

"""
M.A.N.T.I.S. — Bonzo Finance ABI Stubs
Placeholder ABI definitions for Bonzo Finance contracts:
  - Bonzo Vault (CLMM) — concentrated liquidity vaults
  - Bonzo Lend (Aave v2 fork) — lending pool

TODO: Replace with actual ABIs once contract addresses and
      interface specifications are confirmed.
"""

# Placeholder ABI — matches expected Bonzo Vault interface
# Based on docs: https://docs.bonzo.finance/hub/bonzo-vaults-beta/bonzo-vaults-quickstart

BONZO_VAULT_ABI = [
    {
        "name": "deposit",
        "type": "function",
        "inputs": [
            {"name": "amount0", "type": "uint256"},
            {"name": "amount1", "type": "uint256"},
        ],
        "outputs": [{"name": "shares", "type": "uint256"}],
    },
    {
        "name": "withdraw",
        "type": "function",
        "inputs": [{"name": "shares", "type": "uint256"}],
        "outputs": [
            {"name": "amount0", "type": "uint256"},
            {"name": "amount1", "type": "uint256"},
        ],
    },
    {
        "name": "harvest",
        "type": "function",
        "inputs": [],
        "outputs": [],
    },
    {
        "name": "rebalance",
        "type": "function",
        "inputs": [
            {"name": "newLowerTick", "type": "int24"},
            {"name": "newUpperTick", "type": "int24"},
        ],
        "outputs": [],
    },
    {
        "name": "balanceOf",
        "type": "function",
        "inputs": [{"name": "account", "type": "address"}],
        "outputs": [{"name": "balance", "type": "uint256"}],
    },
    {
        "name": "totalSupply",
        "type": "function",
        "inputs": [],
        "outputs": [{"name": "supply", "type": "uint256"}],
    },
    {
        "name": "getPendingRewards",
        "type": "function",
        "inputs": [],
        "outputs": [
            {"name": "reward0", "type": "uint256"},
            {"name": "reward1", "type": "uint256"},
        ],
    },
    {
        "name": "getCurrentRange",
        "type": "function",
        "inputs": [],
        "outputs": [
            {"name": "lowerTick", "type": "int24"},
            {"name": "upperTick", "type": "int24"},
        ],
    },
]

# Known vault contract IDs (testnet / mainnet)
# TODO: Replace with actual Bonzo vault contract IDs
BONZO_VAULT_CONTRACTS = {
    "testnet": {
        "HBAR_USDC": "0.0.0000000",  # placeholder
    },
    "mainnet": {
        "HBAR_USDC": "0.0.0000000",  # placeholder
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# BONZO LEND — Aave v2 LendingPool ABI
# Based on: https://docs.aave.com/developers/v/2.0
# Adapted for Hedera EVM + Hedera Token Service (HTS)
# ═══════════════════════════════════════════════════════════════════════════════

BONZO_LENDING_POOL_ABI = [
    # ── User-facing write operations ─────────────────────────────────────
    {
        "name": "deposit",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "asset", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "onBehalfOf", "type": "address"},
            {"name": "referralCode", "type": "uint16"},
        ],
        "outputs": [],
    },
    {
        "name": "withdraw",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "asset", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "to", "type": "address"},
        ],
        "outputs": [{"name": "", "type": "uint256"}],
    },
    {
        "name": "borrow",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "asset", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "interestRateMode", "type": "uint256"},
            {"name": "referralCode", "type": "uint16"},
            {"name": "onBehalfOf", "type": "address"},
        ],
        "outputs": [],
    },
    {
        "name": "repay",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "asset", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "rateMode", "type": "uint256"},
            {"name": "onBehalfOf", "type": "address"},
        ],
        "outputs": [{"name": "", "type": "uint256"}],
    },
    # ── Read operations ──────────────────────────────────────────────────
    {
        "name": "getUserAccountData",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "user", "type": "address"}],
        "outputs": [
            {"name": "totalCollateralETH", "type": "uint256"},
            {"name": "totalDebtETH", "type": "uint256"},
            {"name": "availableBorrowsETH", "type": "uint256"},
            {"name": "currentLiquidationThreshold", "type": "uint256"},
            {"name": "ltv", "type": "uint256"},
            {"name": "healthFactor", "type": "uint256"},
        ],
    },
    {
        "name": "getReserveData",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "asset", "type": "address"}],
        "outputs": [
            {"name": "configuration", "type": "uint256"},
            {"name": "liquidityIndex", "type": "uint128"},
            {"name": "variableBorrowIndex", "type": "uint128"},
            {"name": "currentLiquidityRate", "type": "uint128"},
            {"name": "currentVariableBorrowRate", "type": "uint128"},
            {"name": "currentStableBorrowRate", "type": "uint128"},
            {"name": "lastUpdateTimestamp", "type": "uint40"},
            {"name": "aTokenAddress", "type": "address"},
            {"name": "stableDebtTokenAddress", "type": "address"},
            {"name": "variableDebtTokenAddress", "type": "address"},
            {"name": "interestRateStrategyAddress", "type": "address"},
            {"name": "id", "type": "uint8"},
        ],
    },
    {
        "name": "getReservesList",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "address[]"}],
    },
]

# Known LendingPool contract IDs (testnet / mainnet)
# TODO: Replace with actual Bonzo LendingPool contract IDs
BONZO_LENDING_CONTRACTS = {
    "testnet": {
        "lending_pool": "0.0.0000000",  # placeholder
    },
    "mainnet": {
        "lending_pool": "0.0.0000000",  # placeholder
    },
}

# Known Hedera token EVM addresses for lending operations
# TODO: Replace with actual token addresses
BONZO_LENDING_TOKENS = {
    "testnet": {
        "WHBAR": "0x0000000000000000000000000000000000000000",  # placeholder
        "USDC": "0x0000000000000000000000000000000000000000",   # placeholder
        "BONZO": "0x0000000000000000000000000000000000000000",  # placeholder
    },
    "mainnet": {
        "WHBAR": "0x0000000000000000000000000000000000000000",  # placeholder
        "USDC": "0x0000000000000000000000000000000000000000",   # placeholder
        "BONZO": "0x0000000000000000000000000000000000000000",  # placeholder
    },
}

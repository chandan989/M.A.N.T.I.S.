# M.A.N.T.I.S. — Agent Decision Loop

> How M.A.N.T.I.S. evaluates market conditions and decides whether to act.

---

## The Core Loop

Every `SENTRY_INTERVAL_SECONDS` (default: **60 seconds**), the agent runs this sequence:

```
┌──────────────────────────────────────────────────────────────────┐
│  TICK START (every 60s)                                         │
│                                                                  │
│  1. SENSE    → Collect data from all active Skills              │
│  2. THINK    → LLM evaluates context against thresholds         │
│  3. DECIDE   → Action selected (or NO-OP)                      │
│  4. EXECUTE  → Hedera Skill submits signed transaction          │
│  5. LOG      → Action & metrics written to dashboard log        │
│  6. REMEMBER → Memory Skill updates persistent state            │
│                                                                  │
│  TICK END → sleep until next interval                           │
└──────────────────────────────────────────────────────────────────┘
```

---

## Step 1: SENSE — Building Context

The runtime calls each enabled Skill's `collect()` method in parallel:

```typescript
const [sentryData, oracleData, vaultData] = await Promise.all([
  sentrySkill.collect(),   // Sentiment score, trending topics
  oracleSkill.collect(),   // Price, realized volatility, funding rate
  hederaSkill.readVault(), // Current range, in-range status, pending rewards
]);
```

**Resulting context object:**
```json
{
  "timestamp": 1710001260,
  "sentiment": {
    "score": -0.62,
    "label": "BEARISH",
    "top_signals": ["HBAR whale dump", "Crypto Fear Index: 28"],
    "source_count": 47
  },
  "market": {
    "hbar_price_usd": 0.084,
    "hbar_change_24h": -0.089,
    "realized_vol_24h": 0.82,
    "vol_label": "HIGH"
  },
  "vault": {
    "vault_id": "0.0.1234567",
    "strategy": "HBAR/USDC",
    "in_range": true,
    "range_lower": 0.075,
    "range_upper": 0.115,
    "pending_rewards_usd": 24.50,
    "last_harvest_hours_ago": 3.8,
    "current_apy": 14.2
  },
  "user": {
    "risk_profile": "moderate"
  }
}
```

---

## Step 2: THINK — LLM Reasoning

The context is serialized and sent to the LLM with a structured system prompt.

**System Prompt (excerpt):**
```
You are M.A.N.T.I.S., an intelligent DeFi keeper agent managing a user's 
Bonzo Finance vault on Hedera. Your job is to protect their capital and 
maximize risk-adjusted yield.

AVAILABLE ACTIONS:
- NO_OP: Do nothing this tick.
- HARVEST: Trigger an early harvest of pending vault rewards.
- HARVEST_AND_SWAP: Harvest rewards and swap to USDC immediately.
- TIGHTEN_RANGE: Narrow the liquidity range (more fees, more IL risk).
- WIDEN_RANGE: Expand the liquidity range (less fees, less IL risk).
- WITHDRAW_ALL: Full emergency withdrawal to single-sided stablecoin.
- LOG_ONLY: No on-chain action, but record developing situation to the log.

RISK PROFILE CONSTRAINTS for 'moderate':
- Max single-tx value: $10,000
- Min hours between harvests: 2
- Max volatility for tightening range: 0.35
- Require vol > 0.60 to widen range
- Require vol > 0.90 or sentiment < -0.80 to consider WITHDRAW_ALL

Return your decision as structured JSON.
```

**LLM Output:**
```json
{
  "action": "WIDEN_RANGE",
  "confidence": 0.87,
  "rationale": "Realized volatility at 0.82 exceeds the 0.60 threshold for widening. Sentiment at -0.62 is bearish. Current position is in-range but risk of going out-of-range in next 30-60 minutes is high given momentum. Widening range from ±15% to ±28% reduces immediate IL risk at cost of lower fee concentration. Moderate profile supports this protective action.",
  "urgency": "HIGH",
  "parameters": {
    "vault_id": "0.0.1234567",
    "new_range_lower": 0.062,
    "new_range_upper": 0.110
  },
  "log_message": "⚠️ HIGH VOLATILITY: Widened Bonzo HBAR/USDC range to prevent impermanent loss. Vol: 82% | Sentiment: Bearish | New range: $0.062 – $0.110"
}
```

---

## Step 3: DECIDE — Thresholds & Guards

Before execution, a **guard layer** validates the LLM's plan:

| Guard | Check | Fail Behavior |
|---|---|---|
| Min harvest interval | `last_harvest < 2h` → block HARVEST | Downgrade to NO_OP |
| Risk profile ceiling | Action exceeds risk profile | Downgrade to safer action |
| Cooldown | Same action taken 3× in a row | Force LOG_ONLY |
| Sanity check | `new_range_lower >= new_range_upper` | Error + NO_OP |
| Balance check | Sufficient gas/HBAR in wallet | Log alert if low |

---

## Step 4: EXECUTE — On-Chain Interaction

If the action is not `NO_OP`, the Hedera Skill builds and signs the transaction:

```typescript
// Example: WIDEN_RANGE
const tx = await hederaAgentKit
  .bonzoVault(params.vault_id)
  .rebalance({
    newLower: params.new_range_lower,
    newUpper: params.new_range_upper,
  })
  .sign(serverPrivateKey)
  .execute();

await tx.getReceipt(client); // Wait for confirmation
```

---

## Step 5 & 6: LOG & REMEMBER

```typescript
// Log to dashboard
await dashboardLogger.write({
  action: plan.action,
  message: plan.log_message,
  txId: tx.transactionId,
  timestamp: Date.now(),
});

// Persist state
await memorySkill.update({
  last_action: plan.action,
  last_action_ts: Date.now(),
  last_harvest_ts: plan.action.includes("HARVEST") ? Date.now() : prev.last_harvest_ts,
  apy_snapshot: currentApy,
});
```

---

## Decision Matrix (Quick Reference)

| Volatility | Sentiment | Rewards Age | Action |
|---|---|---|---|
| LOW (< 0.35) | Any | > 4h | `HARVEST` |
| LOW (< 0.35) | Any | Any | `TIGHTEN_RANGE` |
| MEDIUM (0.35–0.60) | Neutral+ | > 2h | `HARVEST` |
| MEDIUM (0.35–0.60) | Bearish | > 2h | `HARVEST_AND_SWAP` |
| HIGH (> 0.60) | Any | Any | `WIDEN_RANGE` |
| HIGH (> 0.60) | Very bearish (< -0.70) | > 2h | `HARVEST_AND_SWAP` + `WIDEN_RANGE` |
| EXTREME (> 0.90) | Bearish | Any | `WITHDRAW_ALL` *(moderate/conservative)* |

> Note: This matrix is a simplified override. The LLM may deviate with appropriate reasoning. Guards enforce hard limits regardless of LLM output.

---

## User-Defined Overrides (Dashboard Controls)

Users can set custom override conditions through the M.A.N.T.I.S. web dashboard:

| Dashboard Action | Agent Interpretation | Condition Type |
|---|---|---|
| Set price alert: HBAR < $0.08 → withdraw | Monitored price trigger with auto-action | Price trigger |
| Switch to Conservative mode | Override risk profile to `conservative` | Profile override |
| Trigger harvest now | Immediate manual harvest (bypasses interval guard) | Instant action |
| View current position | Read-only status fetch | Query |
| Pause execution | Set `execution_paused = true` | Mode override |

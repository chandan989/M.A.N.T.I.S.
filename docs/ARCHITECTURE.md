# M.A.N.T.I.S. — System Architecture

> **Market Analysis & Network Tactical Integration System**
> Full technical architecture reference for contributors and auditors.

---

## Table of Contents

1. [High-Level Overview](#1-high-level-overview)
2. [Layer Breakdown](#2-layer-breakdown)
   - [User Interface Layer](#21-user-interface-layer)
   - [Core Agent Runtime](#22-core-agent-runtime)
   - [Skills Layer](#23-skills-layer)
   - [On-Chain Layer](#24-on-chain-layer)
3. [Data Flow Diagram](#3-data-flow-diagram)
4. [Component Interactions](#4-component-interactions)
5. [Technology Choices & Rationale](#5-technology-choices--rationale)
6. [Deployment Model](#6-deployment-model)

---

## 1. High-Level Overview

M.A.N.T.I.S. is a **four-layer autonomous agent** that bridges off-chain intelligence with on-chain DeFi execution on the Hedera network. It runs as a **hosted, always-online service** — users interact with it through a web dashboard without installing or running anything locally.

```
┌─────────────────────────────────────────────────────────┐
│                USER INTERFACE LAYER                     │
│              Web Dashboard (always online)             │
└─────────────────────┬───────────────────────────────────┘
                      │ Override Commands / Status Queries
┌─────────────────────▼───────────────────────────────────┐
│               CORE AGENT RUNTIME                        │
│     Memory Store · LLM Reasoner · Scheduler · Logger   │
└──────┬──────────────────────────────────────────────────┘
       │ Tool Calls (read + write)
┌──────▼──────────────────────────────────────────────────┐
│                   SKILLS LAYER                          │
│       Sentry · Oracle · Hedera · Memory Skills         │
└──────┬──────────────────────────────────────────────────┘
       │ Signed Hedera Transactions
┌──────▼──────────────────────────────────────────────────┐
│                  ON-CHAIN LAYER                         │
│       Bonzo Vault Contracts · SaucerSwap Pools         │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Layer Breakdown

### 2.1 User Interface Layer

M.A.N.T.I.S. uses a **web-first** interface. Users access a live dashboard to monitor agent decisions, vault positions, APY history, and system logs — from any browser, with no local software required.

**Dashboard Features:**
| Feature | Description |
|---|---|
| Live agent log | Real-time stream of every decision the agent makes |
| Vault position view | Current liquidity range, in-range status, pending rewards |
| APY history chart | Historical yield performance over time |
| Risk profile settings | Switch between Conservative / Moderate / Aggressive |
| Manual override controls | Trigger harvest, pause execution, or set price alerts |

**Interaction Types:**
- **Status Views** — Continuously updated vault and agent state
- **Override Controls** — User-initiated actions surfaced through the dashboard UI
- **Alert Panel** — Recent agent actions and market events highlighted in the dashboard

---

### 2.2 Core Agent Runtime

The runtime is the **central orchestrator**. It runs as a persistent cloud process, waking every `SENTRY_INTERVAL_SECONDS` (default: 60s) to execute the decision loop.

#### Sub-components:

**Scheduler**
```
setInterval(async () => {
  const context = await buildContext();   // Fetch all skill data
  const plan    = await reasoner.think(context); // LLM decides action
  await executor.run(plan);              // Execute if action required
}, SENTRY_INTERVAL_SECONDS * 1000);
```

**Memory Store**
The agent persists state in a cloud database so it can make decisions based on history, not just the current snapshot.

```json
{
  "user": {
    "risk_profile": "moderate",
    "wallets": ["0.0.XXXXXX"]
  },
  "vaults": [
    {
      "vault_id": "0.0.1234567",
      "strategy": "HBAR/USDC CLMM",
      "last_harvest_ts": 1710000000,
      "last_range_lower": 0.075,
      "last_range_upper": 0.115,
      "apy_history": [14.2, 13.8, 15.1]
    }
  ],
  "agent": {
    "last_action": "WIDEN_RANGE",
    "last_action_ts": 1710001200,
    "consecutive_no_ops": 5
  }
}
```

**Reasoning Engine (LLM)**
The runtime passes a structured context object to the LLM with a system prompt that defines:
- Agent personality ("You are a cautious DeFi keeper agent...")
- Available actions and their preconditions
- Risk profile constraints
- Current market state

The LLM returns a structured `ActionPlan`:

```json
{
  "action": "WIDEN_RANGE",
  "rationale": "Realized volatility hit 82%. Risk profile is moderate. Widening range from ±15% to ±25% to prevent out-of-range event.",
  "urgency": "HIGH",
  "parameters": {
    "vault_id": "0.0.1234567",
    "new_range_lower": 0.065,
    "new_range_upper": 0.125
  },
  "log_message": "High volatility detected. Widened Bonzo range to prevent impermanent loss."
}
```

---

### 2.3 Skills Layer

Skills are **modular, self-contained plugins** that expose a standard interface to the runtime. Each skill can be enabled/disabled independently.

```typescript
interface Skill {
  name: string;
  version: string;
  collect(): Promise<SkillData>;     // Pull current data
  execute(params: any): Promise<ExecutionResult>; // Perform an action
}
```

See [**SKILLS.md**](SKILLS.md) for full skill specifications.

---

### 2.4 On-Chain Layer

M.A.N.T.I.S. interacts with two primary contract systems:

**Bonzo Finance Vaults**
- Concentrated Liquidity Market Maker (CLMM) vaults on Hedera
- Key operations: `deposit()`, `withdraw()`, `rebalance()`, `harvest()`
- ABI definitions stored in `src/contracts/bonzo/`
- Docs: [docs.bonzo.finance](https://docs.bonzo.finance/hub/bonzo-vaults-beta/bonzo-vaults-quickstart)

**SaucerSwap Liquidity Pools**
- Underlying AMM for Bonzo CLMM vaults
- Accessed indirectly through Bonzo Vault contracts

**Hedera Agent Kit**
The bridge between the Skills Layer and on-chain execution. It handles:
- Server-side key signing (private key stored in encrypted secret store)
- Transaction building and submission
- Receipt confirmation and error handling
- Mirror node queries for state reads

---

## 3. Data Flow Diagram

```
[Twitter API] ──────────────────────────────┐
[CryptoPanic RSS] ──────────────────────────┤
[Polymarket API] ──────────────────────────→│ Sentry Skill
                                            │   sentiment_score: -0.62
                                            │
[SupraOracles Feed] ───────────────────────→│ Oracle Skill
[Pyth Network] ────────────────────────────┤   price: $0.084
                                            │   realized_vol: 0.82
                                            │
                                            ▼
                                    ┌───────────────┐
                                    │  LLM Reasoner │
                                    │  (GPT-4/Claude)│
                                    └───────┬───────┘
                                            │ ActionPlan: HARVEST_AND_SWAP
                                            ▼
                                    ┌───────────────┐
                                    │  Hedera Skill │
                                    │  Agent Kit    │
                                    └───────┬───────┘
                                            │ Signed Txn
                                            ▼
                                    ┌───────────────┐
                                    │ Bonzo Vault   │
                                    │ (Hedera EVM)  │
                                    └───────────────┘
                                            │ Tx Hash
                                            ▼
                                    ┌───────────────┐
                                    │  Dashboard    │
                                    │  "Harvested ✅"│
                                    └───────────────┘
```

---

## 4. Component Interactions

### Harvest Decision Flow

```
Sentry: sentiment = -0.72 (very bearish on HBAR)
Oracle: price dropped 8% in 2h
Memory: last harvest was 3.5 hours ago (normally every 4h)

LLM Reasoning:
  "Sentiment is strongly negative. Price is declining.
   Reward token (HBAR) will likely depreciate further.
   Harvesting now locks in value. Risk profile: moderate.
   → TRIGGER EARLY HARVEST + SWAP TO USDC"

Hedera Skill:
  1. Call vault.harvest()  → Tx 0xaaa
  2. Call swap(HBAR→USDC) → Tx 0xbbb

Dashboard Log:
  "🟡 EARLY HARVEST TRIGGERED
   Sentiment score: -0.72 (very bearish)
   Harvested 142 HBAR → swapped to 11.94 USDC
   Saved ~$1.20 vs waiting for scheduled harvest.
   Txns: 0xaaa 0xbbb ✅"
```

---

## 5. Technology Choices & Rationale

| Choice | Alternative Considered | Rationale |
|---|---|---|
| **Hedera Agent Kit** | Direct SDK calls | Pre-built abstractions for agent-friendly DeFi ops |
| **LLM-based reasoning** | Rule-based if/else | Handles nuance, edge cases, and natural language |
| **Web dashboard for UX** | Messaging bots | Always accessible from any browser; centralised status view |
| **Hosted cloud execution** | User-run local agent | 24/7 uptime without user managing infrastructure |
| **Modular Skills** | Monolithic agent | Individual skills can be upgraded/replaced independently |
| **SupraOracles + Pyth** | Chainlink (EVM) | Native Hedera oracle integrations, lower latency |

---

## 6. Deployment Model

M.A.N.T.I.S. runs as a **hosted cloud service** managed by Elykid Private Limited. Users do not need to install, configure, or run anything on their own machines.

### Infrastructure

| Component | Hosting |
|---|---|
| Agent Runtime | Cloud VM (always-on, auto-restart via process manager) |
| Memory / State | Managed cloud database (PostgreSQL / SQLite) |
| Private Key Storage | Encrypted cloud secret store (AWS Secrets Manager / HashiCorp Vault) |
| Web Dashboard | Static frontend served via CDN |
| Hedera RPC | Hedera mirror node + mainnet/testnet endpoints |

> ⚠️ **Security note:** Private keys are stored exclusively in the encrypted server-side secret store and are never exposed via the dashboard, API responses, or logs.

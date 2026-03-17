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
6. [Deployment Models](#6-deployment-models)

---

## 1. High-Level Overview

M.A.N.T.I.S. is a **four-layer autonomous agent** that bridges off-chain intelligence with on-chain DeFi execution on the Hedera network.

```
┌─────────────────────────────────────────────────────────┐
│                USER INTERFACE LAYER                     │
│         Telegram · WhatsApp · Signal · CLI             │
└─────────────────────┬───────────────────────────────────┘
                      │ Natural Language Commands / Alerts
┌─────────────────────▼───────────────────────────────────┐
│               CORE AGENT RUNTIME                        │
│     Memory Store · LLM Reasoner · Scheduler · Logger   │
└──────┬──────────────────────────────────────────────────┘
       │ Tool Calls (read + write)
┌──────▼──────────────────────────────────────────────────┐
│                   SKILLS LAYER                          │
│   Sentry · Oracle · Hedera · Comms · Memory Skills     │
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

M.A.N.T.I.S. uses a **messaging-first** interface philosophy. Users should not need to open a dashboard, connect a wallet browser extension, or run CLI commands to monitor their positions during market hours.

**Supported Channels:**
| Channel | Role |
|---|---|
| Telegram | Primary notification + command channel |
| WhatsApp | Alternative notification channel (via WhatsApp Business API) |
| Signal | Privacy-focused alternative |
| CLI (`mantis chat`) | Local developer/power-user interface |

**Interaction Types:**
- **Proactive Alerts** — Agent pushes notifications when it takes action (e.g., rebalance, harvest)
- **Natural Language Commands** — User sends plain-English instructions the LLM interprets into vault operations
- **Status Queries** — "What's my current APY?" → Agent fetches and responds

---

### 2.2 Core Agent Runtime

The runtime is the **central orchestrator**. It runs as a persistent Node.js / Python process, waking every `SENTRY_INTERVAL_SECONDS` (default: 60s) to execute the decision loop.

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
The agent persists state locally so it can make decisions based on history, not just the current snapshot.

```json
{
  "user": {
    "risk_profile": "moderate",
    "telegram_chat_id": "123456",
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
  "notify_user": true,
  "message": "High volatility detected. I widened your Bonzo range to prevent impermanent loss."
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
- Local key signing (private key never leaves the machine)
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
                                    │  Comms Skill  │
                                    │ "Harvested ✅" │
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

Comms Skill:
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
| **Telegram for UX** | Web dashboard | Always accessible, no wallet connection required |
| **Local execution** | Cloud-hosted bot | User retains key custody; no centralized risk |
| **Modular Skills** | Monolithic agent | Individual skills can be upgraded/replaced independently |
| **SupraOracles + Pyth** | Chainlink (EVM) | Native Hedera oracle integrations, lower latency |

---

## 6. Deployment Models

### Option A: Personal Laptop / Desktop
Run `npm start` on your Mac/PC. Agent runs 24/7 while machine is on. Simple; keys stay on your device.

### Option B: Raspberry Pi / Home Server
Always-on local server. Recommended for production use. Set up as a `systemd` service for auto-restart.

### Option C: Private VPS (Advanced)
Run on a private VPS (e.g., Hetzner, DigitalOcean). Use encrypted key storage (e.g., HashiCorp Vault or OS keychain). **Do NOT use shared hosting.**

> ⚠️ **Never** host M.A.N.T.I.S. on a platform that requires uploading your `.env` or private keys to a web interface (e.g., Heroku, Vercel, Railway with env vars exposed in CI logs).

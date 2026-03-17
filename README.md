# M.A.N.T.I.S.
### Market Analysis & Network Tactical Integration System

> **An Intelligent Keeper Agent for Hedera DeFi** — autonomously managing Bonzo Finance vault positions using real-time oracle data, sentiment analysis, and on-chain execution via the Hedera Agent Kit.

[![Hedera](https://img.shields.io/badge/Network-Hedera%20Testnet%2FMainnet-3EC6FF?style=flat-square&logo=hedera)](https://hedera.com)
[![Bonzo Finance](https://img.shields.io/badge/Protocol-Bonzo%20Finance-FF6B35?style=flat-square)](https://bonzo.finance)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

---

## 🦟 What Is M.A.N.T.I.S.?

Traditional DeFi vaults are **reactive** — they harvest rewards on a schedule, rebalance only after impermanent loss has already occurred, and rely entirely on human intervention during volatile market events.

**M.A.N.T.I.S.** flips this paradigm. It is a **continuously running, always-online intelligent agent** that:

- 📡 **Senses** the market via on-chain oracle feeds (SupraOracles / Pyth) and off-chain sentiment (Twitter/X, news, Polymarket)
- 🧠 **Reasons** about what action to take using an LLM reasoning engine (Claude / GPT)
- ⚡ **Executes** signed Hedera transactions autonomously via the **Hedera Agent Kit** — no human approval required
- 🖥️ **Visualises** agent activity, decisions and vault status through a **live web dashboard**

> M.A.N.T.I.S. is a **hosted service** — it runs 24/7 in the cloud. You interact with it via the web dashboard; there is nothing to install or run on your local machine.

---

## 🏗️ Architecture: The "Claw-Fi" Stack

```
======================================================================
                     [ USER INTERFACE LAYER ]
                    (Web Dashboard — always online)

    Real-time agent logs · Vault position · APY history ·
    Manual override controls · Risk profile settings
======================================================================
                               ▲  │
         (Status / Logs)       │  │ (Override Commands)
                               │  ▼
======================================================================
                    [ THE CORE AGENT RUNTIME ]
         (Hosted / Cloud Node / Continuous Execution 24/7)

  [ Memory & Context ]                 [ Reasoning Engine ]
  - User Risk Profile (Aggressive/Safe)- LLM (Claude/GPT/DeepSeek)
  - Persistent Vault State             - Evaluates triggers & intents
  - Historical APY Logs                - Generates execution plans
======================================================================
                               │  ▲
           (Tool Calls)        │  │ (Data / Success Logs)
                               ▼  │
======================================================================
                       [ THE SKILLS LAYER ]
     (Modular Plugins — each Skill is a self-contained module)

  [ Sentry Skill ]        [ Oracle Skill ]        [ Hedera Skill ]
  - Scans Twitter/News    - Fetches Pyth/       - HEDERA AGENT KIT
  - Monitors Hedera HCS     SupraOracles Data   - Wallet Signer
  - Tracks Polymarket     - Calculates 24h      - Bonzo Contract ABI
    sentiment               Volatility            Integration
======================================================================
                                  │
                          (Signed Txns via RPC)
                                  ▼
======================================================================
                         [ ON-CHAIN LAYER ]
                      (Hedera Mainnet / Testnet)

                       - Bonzo Vault Contracts
                       - SaucerSwap Liquidity Pools
======================================================================
```

For a deeper dive, see [**`docs/ARCHITECTURE.md`**](docs/ARCHITECTURE.md).

---

## 🧩 Core Skills

| Skill | Purpose | Key APIs |
|---|---|---|
| **Sentry Skill** | Social & narrative intelligence | Twitter/X API, CryptoPanic, Polymarket |
| **Oracle Skill** | On-chain price & volatility feeds | SupraOracles, Pyth Network, Hedera HCS |
| **Hedera Skill** | Transaction signing & execution | Hedera Agent Kit, Bonzo Finance ABIs |
| **Memory Skill** | Persistent state & user profiles | Cloud database / SQLite store |

---

## 🔄 Agent Decision Loop

```
Every 60s:
  1. [Sentry]  → Pull sentiment score (Twitter, news headlines)
  2. [Oracle]  → Fetch HBAR/USDC price + 24h realized volatility
  3. [Reason]  → LLM evaluates: "Should I act?"
  4. [Execute] → If threshold crossed → call Bonzo Vault via Hedera Skill
  5. [Log]     → Record action & metrics to dashboard
```

See [**`docs/DECISION_LOOP.md`**](docs/DECISION_LOOP.md) for the full logic tree.

---

## 🛡️ Security Design

> **Your keys are protected through secure cloud key management.**

M.A.N.T.I.S. is a hosted service. Private keys are stored in encrypted, access-controlled cloud secret stores (e.g., AWS Secrets Manager / HashiCorp Vault) — never in plaintext and never exposed to the dashboard or external services. The Hedera Agent Kit signs transactions server-side, and only the signed transaction bytes are broadcast to the Hedera network.

- ✅ Private keys held in encrypted server-side secret store
- ✅ No plaintext key exposure at any layer
- ✅ All Hedera transactions are auditable on [HashScan](https://hashscan.io)
- ✅ Guard layer validates every LLM action plan before execution

See [**`docs/SECURITY.md`**](docs/SECURITY.md) for the full threat model.

---

## 📂 Project Structure

```
mantis/
├── README.md
├── docs/
│   ├── ARCHITECTURE.md       # Full system design
│   ├── DECISION_LOOP.md      # Agent logic & thresholds
│   ├── SKILLS.md             # Skill module reference
│   └── SECURITY.md           # Key management & threat model
├── src/
│   ├── agent/
│   │   ├── runtime.ts        # Core agent loop (every 60s)
│   │   ├── memory.ts         # Persistent state management
│   │   └── reasoner.ts       # LLM reasoning engine
│   ├── skills/
│   │   ├── sentry/           # Twitter/news sentiment scanner
│   │   ├── oracle/           # Price & volatility feeds
│   │   ├── hedera/           # Hedera Agent Kit integration
│   │   └── memory/           # User profile & vault state
│   └── contracts/
│       └── bonzo/            # Bonzo Vault ABI definitions
├── dashboard/                # Web dashboard (React)
├── config/
│   └── risk-profiles.json    # Preset risk parameters
├── .env.example
└── package.json
```

---

## 🗺️ Roadmap

- [x] Architecture design & documentation
- [ ] Hedera Agent Kit integration + wallet signer
- [ ] Oracle Skill (SupraOracles + Pyth feeds)
- [ ] Sentry Skill (Twitter/X sentiment + CryptoPanic)
- [ ] Hedera Skill (Bonzo Vault contract integration)
- [ ] Core reasoning loop with LLM
- [ ] User risk profile configuration
- [ ] Persistent memory / state management
- [ ] Web dashboard (live agent logs & vault stats)
- [ ] Mainnet deployment

---

## 📚 References

- [Bonzo Finance Docs](https://docs.bonzo.finance/hub/bonzo-vaults-beta/bonzo-vaults-quickstart)
- [Hedera Agent Kit](https://github.com/hedera-dev/hedera-agent-kit)
- [SupraOracles](https://supraoracles.com)
- [HashScan Explorer](https://hashscan.io)

---

## 📄 License

MIT © 2025 Elykid Private Limited

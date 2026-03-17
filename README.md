# M.A.N.T.I.S.
### Market Analysis & Network Tactical Integration System

> **An Intelligent Keeper Agent for Hedera DeFi** — autonomously managing Bonzo Finance vault positions using real-time oracle data, sentiment analysis, and on-chain execution via the Hedera Agent Kit.

[![Hedera](https://img.shields.io/badge/Network-Hedera%20Testnet%2FMainnet-3EC6FF?style=flat-square&logo=hedera)](https://hedera.com)
[![Bonzo Finance](https://img.shields.io/badge/Protocol-Bonzo%20Finance-FF6B35?style=flat-square)](https://bonzo.finance)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

---

## 🦟 What Is M.A.N.T.I.S.?

Traditional DeFi vaults are **reactive** — they harvest rewards on a schedule, rebalance only after impermanent loss has already occurred, and rely entirely on human intervention during volatile market events.

**M.A.N.T.I.S.** flips this paradigm. It is a **continuously running, self-hosted intelligent agent** that:

- 📡 **Senses** the market via on-chain oracle feeds (SupraOracles / Pyth) and off-chain sentiment (Twitter/X, news, Polymarket)
- 🧠 **Reasons** about what action to take using an LLM reasoning engine (Claude / GPT)
- ⚡ **Executes** signed Hedera transactions autonomously via the **Hedera Agent Kit** — no human approval required
- 💬 **Communicates** outcomes and alerts to the user via **Telegram / WhatsApp** in plain English

---

## 🏗️ Architecture: The "Claw-Fi" Stack

```
======================================================================
                     [ USER INTERFACE LAYER ]
            (Messaging-First: Telegram / WhatsApp / Signal)

  "Hey, a whale just dumped HBAR. I preemptively narrowed
   your Bonzo Vault range to minimize impermanent loss.
   Current APY: 14%. Reply 'withdraw' if you want out."
======================================================================
                               ▲  │
         (Push Notifications)  │  │ (Natural Language Commands)
                               │  ▼
======================================================================
                    [ THE CORE AGENT RUNTIME ]
         (Self-Hosted / Local Node / Continuous Execution)

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
  - Monitors Hedera HCS     SupraOracles Data   - Wallet Signer (Local)
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
| **Memory Skill** | Persistent state & user profiles | Local JSON / SQLite store |
| **Comms Skill** | User notifications & NL commands | Telegram Bot API, Signal |

---

## 🔄 Agent Decision Loop

```
Every 60s:
  1. [Sentry]  → Pull sentiment score (Twitter, news headlines)
  2. [Oracle]  → Fetch HBAR/USDC price + 24h realized volatility
  3. [Reason]  → LLM evaluates: "Should I act?"
  4. [Execute] → If threshold crossed → call Bonzo Vault via Hedera Skill
  5. [Comms]   → Notify user of action or status update
```

See [**`docs/DECISION_LOOP.md`**](docs/DECISION_LOOP.md) for the full logic tree.

---

## 🚀 Quickstart

### Prerequisites

- Node.js ≥ 18 / Python ≥ 3.11
- A funded Hedera testnet account (get one at [portal.hedera.com](https://portal.hedera.com))
- Hedera Agent Kit installed
- API keys: LLM provider + Telegram Bot + data feeds

### 1. Clone & Install

```bash
git clone https://github.com/your-org/mantis.git
cd mantis
npm install        # or: pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Hedera
HEDERA_ACCOUNT_ID=0.0.XXXXXX
HEDERA_PRIVATE_KEY=302e...          # Stored locally — never sent to cloud

# LLM Reasoning Engine
OPENAI_API_KEY=sk-...               # Or ANTHROPIC_API_KEY / DEEPSEEK_API_KEY

# Data Feeds
SUPRA_ORACLE_API_KEY=...
TWITTER_BEARER_TOKEN=...

# User Comms
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...

# Agent Behavior
RISK_PROFILE=moderate               # conservative | moderate | aggressive
VOLATILITY_THRESHOLD=0.15           # 15% 24h move triggers rebalance
SENTIMENT_THRESHOLD=-0.4            # Negative score below -0.4 triggers harvest
SENTRY_INTERVAL_SECONDS=60
```

### 3. Run the Agent

```bash
npm run start      # or: python main.py
```

M.A.N.T.I.S. will begin its sentry loop and send you a Telegram confirmation message.

---

## 🛡️ Security Design

> **Your keys never leave your machine.**

M.A.N.T.I.S. is designed to be **self-hosted**. Unlike cloud-based DeFi bots that require uploading your private key to a server, M.A.N.T.I.S. runs on *your* hardware. The Hedera Agent Kit signs transactions locally, and only the signed transaction bytes are broadcast to the Hedera network.

- ✅ Private keys stored in local `.env` (encrypted at rest — see [docs/SECURITY.md](docs/SECURITY.md))
- ✅ No centralized key custody
- ✅ Minimal external permissions (read-only for data feeds, write-only for Telegram)
- ✅ All Hedera transactions are auditable on [HashScan](https://hashscan.io)

---

## 💬 Messaging Interface Examples

M.A.N.T.I.S. communicates with you in plain English via Telegram:

**Agent → User (proactive alert):**
```
🔴 HIGH VOLATILITY DETECTED
HBAR dropped 12% in 90 minutes. Realized vol: 82%.
Action taken: Widened your Bonzo HBAR/USDC range by 40%.
This prevents your position from going out-of-range.
Current APY: 11.2% | Tx: 0xabc...def ✅
```

**User → Agent (natural language command):**
```
User:  "I'm going to sleep. If HBAR drops below $0.08, 
        move my Bonzo position to USDC."

Agent: "Confirmed. Monitoring HBAR price continuously.
        Threshold set: $0.08 → auto-withdraw to USDC.
        I'll message you if triggered. Sleep well 🌙"
```

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
│   │   ├── comms/            # Telegram/WhatsApp notifications
│   │   └── memory/           # User profile & vault state
│   └── contracts/
│       └── bonzo/            # Bonzo Vault ABI definitions
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
- [ ] Telegram Comms Skill
- [ ] User risk profile configuration
- [ ] Persistent memory / state management
- [ ] Web dashboard (optional)
- [ ] Mainnet deployment guide

---

## 📚 References

- [Bonzo Finance Docs](https://docs.bonzo.finance/hub/bonzo-vaults-beta/bonzo-vaults-quickstart)
- [Hedera Agent Kit](https://github.com/hedera-dev/hedera-agent-kit)
- [SupraOracles](https://supraoracles.com)
- [HashScan Explorer](https://hashscan.io)

---

## 📄 License

MIT © 2025 Elykid Private Limited

# M.A.N.T.I.S. — Skills Reference

> Each Skill is a self-contained module that exposes a standard `collect()` and optionally `execute()` interface to the Core Agent Runtime.

---

## Skill Interface

```typescript
interface Skill {
  name: string;
  version: string;
  enabled: boolean;

  /** Pull current data from this skill's data sources */
  collect(): Promise<SkillData>;

  /** Perform an action (only for action-capable skills) */
  execute?(params: Record<string, unknown>): Promise<ExecutionResult>;
}

interface ExecutionResult {
  success: boolean;
  txId?: string;
  message?: string;
  error?: string;
}
```

---

## 1. Sentry Skill

**Purpose:** Monitors off-chain sentiment to detect narrative shifts before they hit price.

**Sources:**
- Twitter/X API (keyword: HBAR, Hedera, Bonzo Finance, reward token tickers)
- CryptoPanic RSS feed (crypto news aggregator)
- Polymarket (prediction market sentiment for macro events)
- Hedera HCS (on-chain governance announcements)

**Output:**
```typescript
interface SentryData {
  score: number;          // -1.0 (very bearish) to +1.0 (very bullish)
  label: "VERY_BEARISH" | "BEARISH" | "NEUTRAL" | "BULLISH" | "VERY_BULLISH";
  top_signals: string[];  // Human-readable top 3 signals
  source_count: number;   // Number of data points analyzed
  trending_topics: string[];
}
```

**Configuration (`.env`):**
```env
TWITTER_BEARER_TOKEN=...
CRYPTOPANIC_API_KEY=...
SENTRY_KEYWORDS=HBAR,Hedera,Bonzo,SaucerSwap
SENTRY_LOOKBACK_MINUTES=30
```

**Sentiment Scoring:**
Sentiment is calculated as a weighted average:
- Twitter (weight: 0.5) — VADER sentiment analysis on recent tweets
- News (weight: 0.3) — CryptoPanic `bullish`/`bearish` votes ratio
- Polymarket (weight: 0.2) — Implied probability shift for macro outcomes

---

## 2. Oracle Skill

**Purpose:** Fetches real-time on-chain price data and computes volatility metrics.

**Sources:**
- [SupraOracles](https://supraoracles.com) — Primary Hedera native price feeds
- [Pyth Network](https://pyth.network) — High-frequency price updates
- SaucerSwap TWAP — On-chain 1h time-weighted average price (fallback)

**Output:**
```typescript
interface OracleData {
  hbar_price_usd: number;
  hbar_change_1h: number;    // % change over past hour
  hbar_change_24h: number;   // % change over past 24h
  realized_vol_24h: number;  // Annualized realized volatility (0.0–1.0+)
  vol_label: "LOW" | "MEDIUM" | "HIGH" | "EXTREME";
  funding_rate?: number;     // Perp funding rate (if available)
  data_source: string;
}
```

**Volatility Labels:**
| `realized_vol_24h` | Label |
|---|---|
| < 0.35 | LOW |
| 0.35 – 0.60 | MEDIUM |
| 0.60 – 0.90 | HIGH |
| > 0.90 | EXTREME |

**Configuration (`.env`):**
```env
SUPRA_ORACLE_ENDPOINT=https://api.supraoracles.com/...
SUPRA_ORACLE_API_KEY=...
ORACLES_HBAR_PAIR=HBAR_USDC
```

---

## 3. Hedera Skill

**Purpose:** All on-chain reads and writes. The only skill that submits transactions.

**Dependencies:**
- [Hedera Agent Kit](https://github.com/hedera-dev/hedera-agent-kit)
- Bonzo Finance Vault ABI (stored in `src/contracts/bonzo/`)
- Local private key (from `.env`, never transmitted)

**Read Operations:**
```typescript
// Get current vault state
await hederaSkill.readVault(vaultId: string): Promise<VaultState>

// Get pending rewards
await hederaSkill.getPendingRewards(vaultId: string): Promise<number>

// Get wallet balance
await hederaSkill.getBalance(accountId: string): Promise<Balances>
```

**Write Operations (require private key):**
```typescript
// Harvest pending rewards
await hederaSkill.harvest(vaultId: string): Promise<ExecutionResult>

// Harvest + swap rewards to USDC
await hederaSkill.harvestAndSwap(vaultId: string, toToken: "USDC"): Promise<ExecutionResult>

// Rebalance: widen or tighten liquidity range
await hederaSkill.rebalance(vaultId: string, newLower: number, newUpper: number): Promise<ExecutionResult>

// Full withdrawal
await hederaSkill.withdraw(vaultId: string, percentage: number): Promise<ExecutionResult>
```

**Supported Bonzo Vault Contract Addresses:**
> See [Bonzo Finance Docs](https://docs.bonzo.finance/hub/bonzo-vaults-beta/bonzo-vaults-quickstart) for current contract addresses on testnet and mainnet.

**Configuration (`.env`):**
```env
HEDERA_ACCOUNT_ID=0.0.XXXXXX
HEDERA_PRIVATE_KEY=302e...
HEDERA_NETWORK=testnet                # testnet | mainnet
BONZO_VAULT_ID=0.0.XXXXXXX
```

---

## 4. Comms Skill

**Purpose:** Bidirectional communication with the user. Sends proactive alerts and receives natural language commands.

**Supported Channels:**
- **Telegram** (primary, fully implemented)
- **WhatsApp Business API** (secondary)
- **Signal** (future)

**Outbound (Agent → User):**
```typescript
await commsSkill.sendMessage(text: string): Promise<void>
await commsSkill.sendAlert(level: "INFO" | "WARNING" | "CRITICAL", text: string): Promise<void>
```

**Inbound (User → Agent):**
Commands received via Telegram webhook are parsed by the LLM into structured intents:

| Raw Command | Parsed Intent |
|---|---|
| "what's my apy?" | `{ intent: "QUERY_APY" }` |
| "harvest now" | `{ intent: "MANUAL_HARVEST" }` |
| "if hbar drops below 0.07 withdraw" | `{ intent: "SET_PRICE_ALERT", threshold: 0.07, action: "WITHDRAW_ALL" }` |
| "be conservative tonight" | `{ intent: "OVERRIDE_RISK_PROFILE", profile: "conservative", duration: "until_next_message" }` |
| "stop trading" | `{ intent: "PAUSE_EXECUTION" }` |

**Configuration (`.env`):**
```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
COMMS_CHANNEL=telegram               # telegram | whatsapp
```

---

## 5. Memory Skill

**Purpose:** Persists agent state across restarts and provides context for decision-making.

**Storage:**
- Development: Local JSON file (`data/state.json`)
- Production: SQLite (`data/mantis.db`)

**Stored State:**
```typescript
interface AgentState {
  user: UserProfile;
  vaults: VaultState[];
  agent: AgentMeta;
  alerts: ActiveAlert[];
  apy_log: APYSnapshot[];
}
```

**Configuration (`.env`):**
```env
MEMORY_BACKEND=sqlite                # json | sqlite
MEMORY_DB_PATH=./data/mantis.db
```

---

## Adding a Custom Skill

1. Create a new directory under `src/skills/my-skill/`
2. Implement the `Skill` interface in `index.ts`
3. Register the skill in `src/agent/runtime.ts`:
   ```typescript
   import { MySkill } from "./skills/my-skill";
   const skills = [sentrySkill, oracleSkill, hederaSkill, mySkill];
   ```
4. The runtime will automatically call `collect()` on each registered skill every tick.

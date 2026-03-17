export type AgentStatus = "ACTIVE" | "PAUSED" | "ACTION_REQUIRED";

export type RiskProfile = "conservative" | "moderate" | "aggressive";

export type ActionType =
  | "HARVEST"
  | "HARVEST_AND_SWAP"
  | "WIDEN_RANGE"
  | "TIGHTEN_RANGE"
  | "WITHDRAW_ALL"
  | "NO_OP"
  | "NOTIFY_ONLY";

export type VolLabel = "LOW" | "MEDIUM" | "HIGH" | "EXTREME";

export type SentimentLabel = "VERY_BEARISH" | "BEARISH" | "NEUTRAL" | "BULLISH" | "VERY_BULLISH";

export interface AgentState {
  status: AgentStatus;
  lastAction: ActionType;
  lastActionTs: number;
  consecutiveNoOps: number;
  executionPaused: boolean;
  riskProfile: RiskProfile;
  tickIntervalSeconds: number;
}

export interface OracleData {
  hbar_price_usd: number;
  hbar_change_1h: number;
  hbar_change_24h: number;
  realized_vol_24h: number;
  vol_label: VolLabel;
  data_source: string;
  updatedAt: number;
}

export interface SentryData {
  score: number;
  label: SentimentLabel;
  top_signals: string[];
  source_count: number;
  trending_topics: string[];
  updatedAt: number;
}

export interface ActionLogEntry {
  id: string;
  timestamp: number;
  action: ActionType;
  rationale: string;
  txId: string | null;
  success: boolean;
}

export interface APYDataPoint {
  timestamp: string;
  apy: number;
  harvestOccurred: boolean;
}

export interface VaultPosition {
  strategy: string;
  inRange: boolean;
  rangeLow: number;
  rangeHigh: number;
  currentAPY: number;
  pendingRewards: number;
  pendingRewardToken: string;
  lastHarvestHoursAgo: number;
}

export interface ChatMessage {
  id: string;
  sender: "agent" | "user";
  content: string;
  timestamp: number;
}

export interface ThresholdConfig {
  volatilityThreshold: number;
  sentimentThreshold: number;
  sentryIntervalSeconds: number;
  minHarvestIntervalHours: number;
}

export type GlowColor = "purple" | "magenta" | "green" | "amber";

export type AgentAction =
  | { type: "SET_STATUS"; payload: AgentStatus }
  | { type: "SET_LAST_ACTION"; payload: { action: ActionType; timestamp: number } }
  | { type: "SET_PAUSED"; payload: boolean }
  | { type: "SET_RISK_PROFILE"; payload: RiskProfile }
  | { type: "ADD_LOG_ENTRY"; payload: ActionLogEntry }
  | { type: "SET_ORACLE_DATA"; payload: OracleData }
  | { type: "SET_SENTRY_DATA"; payload: SentryData }
  | { type: "INCREMENT_NO_OPS" }
  | { type: "RESET_NO_OPS" };

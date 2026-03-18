export interface LogEntry {
  id: string;
  timestamp: string;
  phase: 'SENSE' | 'THINK' | 'ACT' | 'ERR' | 'SYS';
  message: string;
  action?: string;
  status?: 'OK' | 'WARN' | 'FAIL';
}

export interface OracleData {
  pair: string;
  price: number;
  volatility: number;
  trend: number[];
  change1h: number;
}

export interface SentryData {
  score: number;
  label: string;
  sources: number;
  signals: string[];
}

export interface VaultState {
  id: string;
  name: string;
  protocol: string;
  strategy: string;
  rangeLow: number;
  rangeHigh: number;
  inRange: boolean;
  positionPct: number;
  apy24h: number;
  apy7d: number;
  rewardPending: number;
  lastHarvest: string;
  deposited: number;
  pnlAllTime: number;
}

export interface AgentMeta {
  lastAction: string;
  lastActionTs: number;
  consecutiveNoOps: number;
  walletId: string;
  hbarBalance: number;
  usdcBalance: number;
}

export interface Transaction {
  hash: string;
  action: string;
  status: 'OK' | 'WARN' | 'FAIL';
  value: string;
  age: string;
}

let logCounter = 0;
let cyclePhase = 0;

const SENSE_MSGS = [
  'Pulling Sentry data...',
  'Querying oracle feeds...',
  'Scanning mempool activity...',
  'Fetching HCS topic messages...',
  'Polling CryptoPanic sentiment...',
  'Aggregating volatility signals...',
];
const THINK_MSGS = [
  'LLM reasoning complete.',
  'Evaluating position risk...',
  'Analyzing range boundaries...',
  'Computing optimal action vector...',
  'Assessing rebalance urgency...',
  'Cross-referencing sentiment data...',
];
const ACTIONS = ['WIDEN_RANGE', 'NARROW_RANGE', 'HARVEST', 'HARVEST_SWAP', 'NO_OP', 'NO_OP', 'NO_OP', 'REBALANCE'];

function pad2(n: number) { return n.toString().padStart(2, '0'); }

function currentTime(): string {
  const d = new Date();
  return `${pad2(d.getHours())}:${pad2(d.getMinutes())}:${pad2(d.getSeconds())}`;
}

function pick<T>(arr: T[]): T { return arr[Math.floor(Math.random() * arr.length)]; }

export function generateLogEntry(): LogEntry {
  const phase = cyclePhase;
  cyclePhase = (cyclePhase + 1) % 3;
  logCounter++;
  const id = `log-${logCounter}`;
  const ts = currentTime();

  if (phase === 0) {
    return { id, timestamp: ts, phase: 'SENSE', message: pick(SENSE_MSGS) };
  } else if (phase === 1) {
    return { id, timestamp: ts, phase: 'THINK', message: pick(THINK_MSGS) };
  } else {
    const action = pick(ACTIONS);
    const status: 'OK' | 'WARN' = Math.random() > 0.15 ? 'OK' : 'WARN';
    return { id, timestamp: ts, phase: 'ACT', message: action, action, status };
  }
}

let currentPrice = 0.084;

export function generateOracleSnapshot(): OracleData {
  const drift = (Math.random() - 0.5) * 0.003;
  currentPrice = Math.max(0.05, Math.min(0.15, currentPrice + drift));
  const volatility = 0.4 + Math.random() * 0.6;
  const trend: number[] = [];
  let p = currentPrice - 0.005;
  for (let i = 0; i < 12; i++) {
    p += (Math.random() - 0.48) * 0.002;
    trend.push(p);
  }
  return {
    pair: 'HBAR/USDC',
    price: Math.round(currentPrice * 10000) / 10000,
    volatility: Math.round(volatility * 100) / 100,
    trend,
    change1h: drift > 0 ? 1 : -1,
  };
}

export const MOCK_VAULTS: VaultState[] = [
  {
    id: '0.0.1234567',
    name: 'BONZO_HBAR/USDC_001',
    protocol: 'BONZO FINANCE',
    strategy: 'HBAR/USDC CLMM',
    rangeLow: 0.075,
    rangeHigh: 0.115,
    inRange: true,
    positionPct: 0.75,
    apy24h: 14.2,
    apy7d: 13.8,
    rewardPending: 24.5,
    lastHarvest: '3.8 HOURS AGO',
    deposited: 4820.0,
    pnlAllTime: 182.4,
  },
  {
    id: '0.0.2345678',
    name: 'BONZO_SAUCE/HBAR_002',
    protocol: 'BONZO FINANCE',
    strategy: 'SAUCE/HBAR CLMM',
    rangeLow: 0.012,
    rangeHigh: 0.028,
    inRange: true,
    positionPct: 0.62,
    apy24h: 22.7,
    apy7d: 19.3,
    rewardPending: 11.8,
    lastHarvest: '1.2 HOURS AGO',
    deposited: 2150.0,
    pnlAllTime: 97.2,
  },
];

export const MOCK_AGENT: AgentMeta = {
  lastAction: 'WIDEN_RANGE',
  lastActionTs: Date.now() - 47 * 60 * 1000,
  consecutiveNoOps: 3,
  walletId: '0.0.4815162',
  hbarBalance: 4201.84,
  usdcBalance: 1014.22,
};

export const MOCK_SENTRY: SentryData = {
  score: -0.72,
  label: 'BEARISH',
  sources: 47,
  signals: [
    'HBAR whale dump detected (14 sources)',
    'Crypto Fear Index: 28 (FEARFUL)',
    'Polymarket: 62% expect HBAR price decline',
  ],
};

export const APY_HISTORY_7D: number[] = (() => {
  const data: number[] = [];
  let v = 12;
  for (let i = 0; i < 168; i++) {
    v += (Math.random() - 0.48) * 1.5;
    v = Math.max(3, Math.min(25, v));
    data.push(Math.round(v * 10) / 10);
  }
  return data;
})();

export const TX_HISTORY: Transaction[] = [
  { hash: '0x8f9c3b1a4e2d7c5f', action: 'WIDEN_RANGE', status: 'OK', value: '---', age: '2h ago' },
  { hash: '0x3b1a9c2d4e7f8a5b', action: 'HARVEST_SWAP', status: 'OK', value: '$42.10', age: '6h ago' },
  { hash: '0x7e4f1a5b3c9d2e8f', action: 'HARVEST', status: 'WARN', value: '$18.50', age: '1d ago' },
  { hash: '0xa2c4e6f8b1d3e5a7', action: 'NARROW_RANGE', status: 'OK', value: '---', age: '1d ago' },
  { hash: '0xd5e7f9a1b3c5d7e9', action: 'HARVEST_SWAP', status: 'OK', value: '$31.20', age: '2d ago' },
  { hash: '0x1a3b5c7d9e2f4a6b', action: 'NO_OP', status: 'OK', value: '---', age: '2d ago' },
  { hash: '0xf8e6d4c2b0a9e7d5', action: 'REBALANCE', status: 'OK', value: '---', age: '3d ago' },
  { hash: '0x2b4d6f8a1c3e5a7b', action: 'HARVEST', status: 'OK', value: '$22.80', age: '3d ago' },
  { hash: '0xc9e1a3b5d7f9e2a4', action: 'WIDEN_RANGE', status: 'FAIL', value: '---', age: '4d ago' },
  { hash: '0x5d7f9a1b3c5e7a9b', action: 'HARVEST_SWAP', status: 'OK', value: '$55.30', age: '4d ago' },
  { hash: '0xe2a4c6d8f1b3d5e7', action: 'NO_OP', status: 'OK', value: '---', age: '5d ago' },
  { hash: '0x8a2c4e6f8b1d3e5a', action: 'HARVEST', status: 'OK', value: '$19.90', age: '5d ago' },
  { hash: '0xb4d6f8a1c3e5a7b9', action: 'NARROW_RANGE', status: 'OK', value: '---', age: '6d ago' },
  { hash: '0x6f8a1c3e5a7b9d2e', action: 'HARVEST_SWAP', status: 'WARN', value: '$28.40', age: '6d ago' },
  { hash: '0x3e5a7b9d2e4f6a8c', action: 'REBALANCE', status: 'OK', value: '---', age: '7d ago' },
];

export function generateInitialLogs(): LogEntry[] {
  const logs: LogEntry[] = [];
  for (let i = 0; i < 12; i++) {
    logs.push(generateLogEntry());
  }
  return logs;
}

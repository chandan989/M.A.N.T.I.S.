import React, { createContext, useContext, useReducer, type Dispatch } from 'react';
import type { LogEntry, OracleData, SentryData, VaultState } from '../data/mockData';
import { MOCK_AGENT, MOCK_SENTRY, MOCK_VAULTS, generateOracleSnapshot, generateInitialLogs } from '../data/mockData';

export interface AgentContextState {
  agentRunning: boolean;
  safeMode: boolean;
  autoRebalance: boolean;
  riskProfile: 'conservative' | 'moderate' | 'aggressive';
  activeVaultId: string;
  executionLog: LogEntry[];
  lastActionTs: number;
  lastAction: string;
  oracleData: OracleData;
  sentryData: SentryData;
  vaultData: VaultState[];
  walletId: string;
  hbarBalance: number;
  usdcBalance: number;
  network: 'mainnet' | 'testnet';
  actionInFlight: boolean;
}

type Action =
  | { type: 'TOGGLE_AGENT' }
  | { type: 'TOGGLE_SAFE_MODE' }
  | { type: 'TOGGLE_AUTO_REBALANCE' }
  | { type: 'SET_RISK_PROFILE'; payload: AgentContextState['riskProfile'] }
  | { type: 'SET_ACTIVE_VAULT'; payload: string }
  | { type: 'ADD_LOG'; payload: LogEntry }
  | { type: 'UPDATE_ORACLE'; payload: OracleData }
  | { type: 'SET_ACTION_IN_FLIGHT'; payload: boolean }
  | { type: 'UPDATE_LAST_ACTION'; payload: { action: string; ts: number } }
  | { type: 'SET_WALLET'; payload: { walletId: string; hbarBalance: number; usdcBalance: number; network: 'mainnet' | 'testnet' } };

const initialState: AgentContextState = {
  agentRunning: true,
  safeMode: false,
  autoRebalance: true,
  riskProfile: 'moderate',
  activeVaultId: MOCK_VAULTS[0].id,
  executionLog: generateInitialLogs(),
  lastActionTs: MOCK_AGENT.lastActionTs,
  lastAction: MOCK_AGENT.lastAction,
  oracleData: generateOracleSnapshot(),
  sentryData: MOCK_SENTRY,
  vaultData: MOCK_VAULTS,
  walletId: '---',
  hbarBalance: 0,
  usdcBalance: 0,
  network: 'testnet',
  actionInFlight: false,
};

function reducer(state: AgentContextState, action: Action): AgentContextState {
  switch (action.type) {
    case 'TOGGLE_AGENT':
      return { ...state, agentRunning: !state.agentRunning };
    case 'TOGGLE_SAFE_MODE':
      return { ...state, safeMode: !state.safeMode };
    case 'TOGGLE_AUTO_REBALANCE':
      return { ...state, autoRebalance: !state.autoRebalance };
    case 'SET_RISK_PROFILE':
      return { ...state, riskProfile: action.payload };
    case 'SET_ACTIVE_VAULT':
      return { ...state, activeVaultId: action.payload };
    case 'ADD_LOG': {
      const logs = [...state.executionLog, action.payload];
      if (logs.length > 200) logs.shift();
      return { ...state, executionLog: logs };
    }
    case 'UPDATE_ORACLE':
      return { ...state, oracleData: action.payload };
    case 'SET_ACTION_IN_FLIGHT':
      return { ...state, actionInFlight: action.payload };
    case 'UPDATE_LAST_ACTION':
      return { ...state, lastAction: action.payload.action, lastActionTs: action.payload.ts };
    case 'SET_WALLET':
      return {
        ...state,
        walletId: action.payload.walletId,
        hbarBalance: action.payload.hbarBalance,
        usdcBalance: action.payload.usdcBalance,
        network: action.payload.network,
      };
    default:
      return state;
  }
}

const AgentContext = createContext<{ state: AgentContextState; dispatch: Dispatch<Action> } | null>(null);

export function AgentProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  return <AgentContext.Provider value={{ state, dispatch }}>{children}</AgentContext.Provider>;
}

export function useAgent() {
  const ctx = useContext(AgentContext);
  if (!ctx) throw new Error('useAgent must be used within AgentProvider');
  return ctx;
}

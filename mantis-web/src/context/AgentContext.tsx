import React, { createContext, useContext, useReducer, ReactNode } from "react";
import {
  AgentState,
  OracleData,
  SentryData,
  ActionLogEntry,
  AgentAction,
  AgentStatus,
  ActionType,
  RiskProfile,
} from "@/types/mantis";
import { mockAgentState } from "@/data/mockAgentState";
import { mockOracleData } from "@/data/mockOracleData";
import { mockSentryData } from "@/data/mockSentryData";
import { mockActionLog } from "@/data/mockActionLog";

interface AgentContextState {
  agent: AgentState;
  oracle: OracleData;
  sentry: SentryData;
  actionLog: ActionLogEntry[];
}

interface AgentContextValue extends AgentContextState {
  dispatch: React.Dispatch<AgentAction>;
  setStatus: (status: AgentStatus) => void;
  setLastAction: (action: ActionType) => void;
  setPaused: (paused: boolean) => void;
  setRiskProfile: (profile: RiskProfile) => void;
  addLogEntry: (entry: ActionLogEntry) => void;
}

const initialState: AgentContextState = {
  agent: mockAgentState,
  oracle: mockOracleData,
  sentry: mockSentryData,
  actionLog: [...mockActionLog],
};

function agentReducer(state: AgentContextState, action: AgentAction): AgentContextState {
  switch (action.type) {
    case "SET_STATUS":
      return { ...state, agent: { ...state.agent, status: action.payload } };
    case "SET_LAST_ACTION":
      return {
        ...state,
        agent: {
          ...state.agent,
          lastAction: action.payload.action,
          lastActionTs: action.payload.timestamp,
        },
      };
    case "SET_PAUSED":
      return {
        ...state,
        agent: {
          ...state.agent,
          executionPaused: action.payload,
          status: action.payload ? "PAUSED" : "ACTIVE",
        },
      };
    case "SET_RISK_PROFILE":
      return { ...state, agent: { ...state.agent, riskProfile: action.payload } };
    case "ADD_LOG_ENTRY":
      return { ...state, actionLog: [action.payload, ...state.actionLog] };
    case "SET_ORACLE_DATA":
      return { ...state, oracle: action.payload };
    case "SET_SENTRY_DATA":
      return { ...state, sentry: action.payload };
    case "INCREMENT_NO_OPS":
      return { ...state, agent: { ...state.agent, consecutiveNoOps: state.agent.consecutiveNoOps + 1 } };
    case "RESET_NO_OPS":
      return { ...state, agent: { ...state.agent, consecutiveNoOps: 0 } };
    default:
      return state;
  }
}

const AgentContext = createContext<AgentContextValue | null>(null);

export function AgentProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(agentReducer, initialState);

  const value: AgentContextValue = {
    ...state,
    dispatch,
    setStatus: (status) => dispatch({ type: "SET_STATUS", payload: status }),
    setLastAction: (action) =>
      dispatch({ type: "SET_LAST_ACTION", payload: { action, timestamp: Date.now() } }),
    setPaused: (paused) => dispatch({ type: "SET_PAUSED", payload: paused }),
    setRiskProfile: (profile) => dispatch({ type: "SET_RISK_PROFILE", payload: profile }),
    addLogEntry: (entry) => dispatch({ type: "ADD_LOG_ENTRY", payload: entry }),
  };

  return <AgentContext.Provider value={value}>{children}</AgentContext.Provider>;
}

export function useAgent() {
  const ctx = useContext(AgentContext);
  if (!ctx) throw new Error("useAgent must be used within AgentProvider");
  return ctx;
}

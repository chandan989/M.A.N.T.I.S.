import { AgentState } from "@/types/mantis";

export const mockAgentState: AgentState = {
  status: "ACTIVE",
  lastAction: "WIDEN_RANGE",
  lastActionTs: Date.now() - 3 * 60 * 1000,
  consecutiveNoOps: 2,
  executionPaused: false,
  riskProfile: "moderate",
  tickIntervalSeconds: 60,
};

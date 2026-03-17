import { useState, useEffect, useCallback } from "react";
import { useAgent } from "@/context/AgentContext";
import { ActionType, ActionLogEntry } from "@/types/mantis";

const ACTION_WEIGHTS: { action: ActionType; weight: number }[] = [
  { action: "NO_OP", weight: 40 },
  { action: "HARVEST", weight: 25 },
  { action: "WIDEN_RANGE", weight: 10 },
  { action: "TIGHTEN_RANGE", weight: 10 },
  { action: "HARVEST_AND_SWAP", weight: 10 },
  { action: "NOTIFY_ONLY", weight: 5 },
];

const RATIONALES: Record<ActionType, string[]> = {
  NO_OP: [
    "All conditions nominal. Position in-range. No action required.",
    "Market stable. Vol: 22% (LOW). Continuing to monitor.",
    "Sentiment neutral, volatility low. Standing by.",
  ],
  HARVEST: [
    "Pending rewards exceeded threshold. Harvesting now.",
    "Low volatility window detected. Optimal harvest timing.",
    "Scheduled harvest triggered. Collecting pending HBAR.",
  ],
  WIDEN_RANGE: [
    "Volatility spike detected. Widening range to prevent IL.",
    "Price approaching range boundary. Preemptive range expansion.",
  ],
  TIGHTEN_RANGE: [
    "Volatility dropped significantly. Tightening for fee concentration.",
    "Stable conditions. Narrowing range to maximize yield.",
  ],
  HARVEST_AND_SWAP: [
    "Bearish sentiment detected. Harvesting and converting to USDC.",
    "Risk conditions elevated. Securing rewards in stablecoin.",
  ],
  NOTIFY_ONLY: [
    "Unusual on-chain activity detected. Monitoring closely.",
    "Large transfer spotted. No action needed yet.",
  ],
  WITHDRAW_ALL: ["Emergency conditions met. Full withdrawal initiated."],
};

function pickWeightedAction(): ActionType {
  const total = ACTION_WEIGHTS.reduce((s, w) => s + w.weight, 0);
  let r = Math.random() * total;
  for (const { action, weight } of ACTION_WEIGHTS) {
    r -= weight;
    if (r <= 0) return action;
  }
  return "NO_OP";
}

function generateTxId(): string {
  const hex = "0123456789abcdef";
  const start = Array.from({ length: 4 }, () => hex[Math.floor(Math.random() * 16)]).join("");
  const end = Array.from({ length: 4 }, () => hex[Math.floor(Math.random() * 16)]).join("");
  return `0x${start}...${end}`;
}

export function useSimulatedTick() {
  const { agent, addLogEntry, dispatch } = useAgent();
  const [countdown, setCountdown] = useState(60);

  const performTick = useCallback(() => {
    if (agent.executionPaused) return;

    const action = pickWeightedAction();
    const rationales = RATIONALES[action];
    const rationale = rationales[Math.floor(Math.random() * rationales.length)];
    const hasTx = action !== "NO_OP" && action !== "NOTIFY_ONLY";

    const entry: ActionLogEntry = {
      id: `tick-${Date.now()}`,
      timestamp: Date.now(),
      action,
      rationale,
      txId: hasTx ? generateTxId() : null,
      success: true,
    };

    addLogEntry(entry);
    dispatch({ type: "SET_LAST_ACTION", payload: { action, timestamp: Date.now() } });

    if (action === "NO_OP") {
      dispatch({ type: "INCREMENT_NO_OPS" });
    } else {
      dispatch({ type: "RESET_NO_OPS" });
    }
  }, [agent.executionPaused, addLogEntry, dispatch]);

  useEffect(() => {
    const interval = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          performTick();
          return 60;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [performTick]);

  return { countdown, performTick };
}

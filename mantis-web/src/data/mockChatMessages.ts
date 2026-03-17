import { ChatMessage } from "@/types/mantis";

const baseTime = Date.now() - 10 * 60 * 1000;

export const mockChatMessages: ChatMessage[] = [
  {
    id: "c1",
    sender: "agent",
    timestamp: baseTime,
    content: `🔴 HIGH VOLATILITY DETECTED\nHBAR dropped 12% in 90 minutes. Realized vol: 82%.\nAction taken: Widened your Bonzo HBAR/USDC range by 40%.\nThis prevents your position from going out-of-range.\nCurrent APY: 11.2% | Tx: 0x7a2f...4d91 ✅`,
  },
  {
    id: "c2",
    sender: "user",
    timestamp: baseTime + 2 * 60 * 1000,
    content: "What's my current APY?",
  },
  {
    id: "c3",
    sender: "agent",
    timestamp: baseTime + 2 * 60 * 1000 + 3000,
    content: `Your current APY is 14.2% on the HBAR/USDC CLMM vault.\nPending rewards: $24.50 in HBAR (last harvested 3.8 hours ago).\nAt current rates, auto-harvest will trigger in ~12 minutes.`,
  },
  {
    id: "c4",
    sender: "user",
    timestamp: baseTime + 4 * 60 * 1000,
    content: "If HBAR drops below $0.08, move my position to USDC",
  },
  {
    id: "c5",
    sender: "agent",
    timestamp: baseTime + 4 * 60 * 1000 + 2000,
    content: `✅ Confirmed. Price alert set.\nMonitoring HBAR continuously. If price < $0.08, I will:\n1. Harvest all pending HBAR rewards\n2. Swap 100% to USDC\n3. Withdraw from vault to safety\nI'll notify you immediately if triggered. Sleep well 🌙`,
  },
];

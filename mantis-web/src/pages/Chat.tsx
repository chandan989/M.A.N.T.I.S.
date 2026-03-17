import { useState, useRef, useEffect, KeyboardEvent } from "react";
import Layout from "@/components/layout/Layout";
import { useAgent } from "@/context/AgentContext";
import { ChatMessage } from "@/types/mantis";
import { mockChatMessages } from "@/data/mockChatMessages";
import { mockVaultPosition } from "@/data/mockVaultPosition";
import { Bug, User, Send } from "lucide-react";
import PulseIndicator from "@/components/shared/PulseIndicator";

const SUGGESTIONS = [
  "Show my position",
  "Harvest now",
  "Be conservative",
  "Pause trading",
];

export default function Chat() {
  const { agent, setPaused, setRiskProfile, setLastAction } = useAgent();
  const [messages, setMessages] = useState<ChatMessage[]>(mockChatMessages);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, typing]);

  function addAgentResponse(content: string) {
    setTyping(true);
    setTimeout(() => {
      setTyping(false);
      setMessages((prev) => [
        ...prev,
        { id: `m-${Date.now()}`, sender: "agent", content, timestamp: Date.now() },
      ]);
    }, 1500);
  }

  function handleSend() {
    const text = input.trim();
    if (!text) return;

    setMessages((prev) => [
      ...prev,
      { id: `m-${Date.now()}`, sender: "user", content: text, timestamp: Date.now() },
    ]);
    setInput("");

    const lower = text.toLowerCase();
    if (lower.includes("harvest")) {
      setLastAction("HARVEST");
      addAgentResponse(
        "✅ Manual harvest triggered.\nCollecting pending HBAR rewards from your Bonzo vault.\nTx submitted — awaiting confirmation..."
      );
    } else if (lower.includes("status") || lower.includes("position")) {
      const v = mockVaultPosition;
      addAgentResponse(
        `📊 Current Position:\nStrategy: ${v.strategy}\nAPY: ${v.currentAPY}%\nRange: $${v.rangeLow} — $${v.rangeHigh}\nPending Rewards: $${v.pendingRewards} ${v.pendingRewardToken}\nStatus: ${v.inRange ? "IN RANGE ✓" : "OUT OF RANGE ⚠"}`
      );
    } else if (lower.includes("pause") || lower.includes("stop")) {
      setPaused(true);
      addAgentResponse("⏸ Agent paused.\nI will stop executing on-chain actions until you resume.\nMonitoring continues in read-only mode.");
    } else if (lower.includes("resume") || lower.includes("start")) {
      setPaused(false);
      addAgentResponse("▶ Agent resumed.\nReturning to active monitoring and execution mode.");
    } else if (lower.includes("conservative")) {
      setRiskProfile("conservative");
      addAgentResponse("🛡 Risk profile updated to CONSERVATIVE.\nI will prioritize capital protection. Wider ranges, faster harvests, quicker exits.");
    } else if (lower.includes("aggressive")) {
      setRiskProfile("aggressive");
      addAgentResponse("🔥 Risk profile updated to AGGRESSIVE.\nMaximizing yield. Tighter ranges, longer hold times.");
    } else {
      addAgentResponse("✅ Acknowledged. I'll factor that into my next evaluation cycle.\nMonitoring continues.");
    }
  }

  function handleKey(e: KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <Layout>
      <div className="h-[calc(100vh-64px)] md:h-screen flex flex-col md:flex-row">
        {/* Agent info sidebar */}
        <div className="hidden md:flex flex-col w-64 border-r border-border bg-card p-4 gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 border border-synthetic-purple flex items-center justify-center animate-pulse-glow-purple">
              <Bug className="w-6 h-6 text-synthetic-purple" />
            </div>
            <div>
              <p className="font-display text-sm text-foreground">M.A.N.T.I.S.</p>
              <div className="flex items-center gap-1.5">
                <PulseIndicator color="green" />
                <span className="text-xs text-muted-foreground">ONLINE · MONITORING</span>
              </div>
            </div>
          </div>
          <div className="space-y-2 text-xs text-muted-foreground">
            <p>Vault: HBAR/USDC CLMM</p>
            <p>Risk: <span className="text-foreground uppercase">{agent.riskProfile}</span></p>
            <p>Consecutive NO_OPs: {agent.consecutiveNoOps}</p>
          </div>
        </div>

        {/* Chat area */}
        <div className="flex-1 flex flex-col">
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[80%] p-3 text-sm font-body whitespace-pre-line ${
                    msg.sender === "agent"
                      ? "bg-card border-l-2 border-overdrive-magenta text-foreground"
                      : "bg-synthetic-purple text-primary-foreground"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    {msg.sender === "agent" ? (
                      <Bug className="w-3 h-3 text-synthetic-purple" />
                    ) : (
                      <User className="w-3 h-3" />
                    )}
                    <span className="text-[10px] text-muted-foreground">
                      {new Date(msg.timestamp).toLocaleTimeString("en-US", {
                        hour: "2-digit",
                        minute: "2-digit",
                        hour12: false,
                      })}
                    </span>
                  </div>
                  {msg.content}
                </div>
              </div>
            ))}
            {typing && (
              <div className="flex justify-start">
                <div className="bg-card border-l-2 border-overdrive-magenta p-3 text-sm">
                  <span className="text-muted-foreground animate-pulse-dot">● ● ●</span>
                </div>
              </div>
            )}
          </div>

          {/* Suggestions */}
          <div className="px-4 py-2 flex gap-2 flex-wrap">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => setInput(s)}
                className="text-xs border border-border px-2 py-1 text-muted-foreground hover:border-synthetic-purple hover:text-foreground transition-colors bg-transparent"
              >
                {s}
              </button>
            ))}
          </div>

          {/* Input */}
          <div className="border-t border-border p-3 flex items-center gap-2 bg-card">
            <span className="text-xs text-synthetic-purple font-display">mantis &gt;</span>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Enter command..."
              className="flex-1 bg-transparent text-sm text-foreground font-body outline-none placeholder:text-muted-foreground"
            />
            <button
              onClick={handleSend}
              className="border border-synthetic-purple px-3 py-1.5 text-xs font-display text-synthetic-purple hover:bg-synthetic-purple hover:text-primary-foreground transition-colors flex items-center gap-1.5"
            >
              <Send className="w-3 h-3" />
              EXECUTE
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
}

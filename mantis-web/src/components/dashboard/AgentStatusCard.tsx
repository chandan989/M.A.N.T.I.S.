import { useAgent } from "@/context/AgentContext";
import { useSimulatedTick } from "@/hooks/useSimulatedTick";
import GlowCard from "@/components/shared/GlowCard";
import PulseIndicator from "@/components/shared/PulseIndicator";
import StatusBadge from "@/components/shared/StatusBadge";

function formatTimeAgo(ts: number): string {
  const diff = Math.floor((Date.now() - ts) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)} mins ago`;
  return `${(diff / 3600).toFixed(1)}h ago`;
}

export default function AgentStatusCard() {
  const { agent } = useAgent();
  const { countdown } = useSimulatedTick();

  const mins = Math.floor(countdown / 60);
  const secs = countdown % 60;
  const timeStr = `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;

  return (
    <GlowCard glowColor="purple" pulsing={!agent.executionPaused} className="col-span-full glow-primary">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="flex items-center gap-5">
          <h1 className="font-display text-2xl md:text-3xl font-medium tracking-widest text-foreground" style={{ letterSpacing: '0.2em' }}>
            M.A.N.T.I.S.
          </h1>
          <div className="flex items-center gap-3">
            <PulseIndicator color={agent.executionPaused ? "amber" : "green"} size="md" />
            <StatusBadge status={agent.status} />
          </div>
        </div>

        <div className="flex items-center gap-8 text-sm bg-black/20 px-6 py-3 rounded-2xl border border-white/5">
          <div className="flex flex-col items-center">
            <span className="text-xs text-muted font-display tracking-widest mb-1">NEXT SCAN</span>
            <span className="font-display text-lg text-primary glow-text">{timeStr}</span>
          </div>
          <div className="w-px h-10 bg-white/10"></div>
          <div className="flex flex-col">
            <span className="text-xs text-muted font-display tracking-widest mb-1">LAST ACTION</span>
            <div className="flex items-center gap-3">
              <StatusBadge action={agent.lastAction} />
              <span className="text-xs text-muted/70 font-sans">{formatTimeAgo(agent.lastActionTs)}</span>
            </div>
          </div>
        </div>
      </div>
    </GlowCard>
  );
}

import { useAgent } from "@/context/AgentContext";
import GlowCard from "@/components/shared/GlowCard";
import StatusBadge from "@/components/shared/StatusBadge";

function formatTime(ts: number): string {
  return new Date(ts).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

export default function RecentActionsLog() {
  const { actionLog } = useAgent();

  return (
    <GlowCard className="col-span-full md:col-span-1">
      <h2 className="font-display text-sm tracking-widest text-muted mb-4 border-b border-white/5 pb-3">
        RECENT ACTIONS
      </h2>
      <div className="space-y-3 max-h-80 overflow-y-auto pr-2">
        {actionLog.slice(0, 10).map((entry) => (
          <div
            key={entry.id}
            className="flex flex-col gap-1.5 p-3 rounded-xl bg-white/5 border border-white/5 animate-slide-in-up hover:bg-white/10 transition-smooth"
          >
            <div className="flex items-center gap-3">
              <span className="text-[10px] font-display tracking-widest text-muted">
                {formatTime(entry.timestamp)}
              </span>
              <StatusBadge action={entry.action} />
            </div>
            <p className="text-[13px] font-sans text-textMain/80 font-light leading-relaxed">
              {entry.rationale}
            </p>
            {entry.txId && (
              <span className="text-[11px] font-display tracking-widest text-accent mt-1 flex items-center gap-1.5 p-1.5 rounded-lg bg-black/20 w-fit">
                <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse"></span>
                TX: {entry.txId}
              </span>
            )}
          </div>
        ))}
      </div>
    </GlowCard>
  );
}

import { useAgent } from "@/context/AgentContext";
import GlowCard from "@/components/shared/GlowCard";

export default function SentimentGauge() {
  const { sentry } = useAgent();
  const score = sentry.score;

  // Map -1..+1 to angle -90..+90 degrees
  const angle = score * 90;
  // SVG: arc from -90 to +90 degrees, center at (100,100), radius 80
  const needleX = 100 + 70 * Math.cos(((angle - 90) * Math.PI) / 180);
  const needleY = 100 + 70 * Math.sin(((angle - 90) * Math.PI) / 180);

  const labelColor =
    score < -0.3
      ? "text-overdrive-magenta"
      : score > 0.3
        ? "text-neon-green"
        : "text-warning-amber";

  return (
    <GlowCard glowColor={score < -0.3 ? "magenta" : score > 0.3 ? "green" : "amber"}>
      <h2 className="font-display text-sm tracking-widest text-muted mb-4 border-b border-white/5 pb-3">
        SENTRY — SENTIMENT
      </h2>

      <div className="flex justify-center">
        <svg width="200" height="120" viewBox="0 0 200 120">
          {/* Background arc */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="hsl(var(--cyber-metal))"
            strokeWidth="8"
          />
          {/* Colored segments */}
          <path
            d="M 20 100 A 80 80 0 0 1 60 34"
            fill="none"
            stroke="hsl(var(--overdrive-magenta))"
            strokeWidth="8"
            opacity="0.6"
          />
          <path
            d="M 60 34 A 80 80 0 0 1 140 34"
            fill="none"
            stroke="hsl(var(--warning-amber))"
            strokeWidth="8"
            opacity="0.6"
          />
          <path
            d="M 140 34 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="hsl(var(--neon-green))"
            strokeWidth="8"
            opacity="0.6"
          />
          {/* Needle */}
            x1="100"
            y1="100"
            x2={needleX}
            y2={needleY}
            stroke="hsl(var(--foreground))"
            strokeWidth="3"
            strokeLinecap="round"
          <circle cx="100" cy="100" r="4" fill="hsl(var(--foreground))" />
        </svg>
      </div>

      <div className="text-center mt-3">
        <span className={`font-display text-3xl font-medium tracking-tight ${labelColor}`}>{score.toFixed(2)}</span>
        <span className={`block text-xs uppercase tracking-widest mt-1 font-display ${labelColor}`}>
          {sentry.label}
        </span>
      </div>

      <div className="mt-5 space-y-2 bg-black/20 p-3 rounded-xl border border-white/5">
        {sentry.top_signals.map((sig, i) => (
          <p key={i} className="text-[13px] font-sans text-muted font-light flex items-start gap-2">
            <span className="text-primary mt-0.5">•</span> {sig}
          </p>
        ))}
        <p className="text-[11px] font-display tracking-widest text-muted/60 mt-3 pt-2 border-t border-white/5 uppercase">
          {sentry.source_count} signals analyzed
        </p>
      </div>
    </GlowCard>
  );
}

import { useAgent } from "@/context/AgentContext";
import GlowCard from "@/components/shared/GlowCard";
import StatusBadge from "@/components/shared/StatusBadge";
import DataLabel from "@/components/shared/DataLabel";

export default function OracleDataCard() {
  const { oracle } = useAgent();

  const change1hColor = oracle.hbar_change_1h < 0 ? "text-overdrive-magenta" : "text-neon-green";
  const volPercent = Math.min(oracle.realized_vol_24h * 100, 100);

  return (
    <GlowCard>
      <h2 className="font-display text-sm tracking-widest text-muted mb-4 border-b border-white/5 pb-3">
        ORACLE — PRICE FEED
      </h2>

      <div className="space-y-4">
        <div className="flex items-baseline gap-3 bg-black/20 p-4 rounded-xl border border-white/5 justify-center">
          <span className="font-display text-4xl text-foreground font-medium tracking-tight">
            ${oracle.hbar_price_usd.toFixed(4)}
          </span>
          <span className={`text-sm font-sans font-medium px-2 py-1 rounded-md bg-white/5 ${change1hColor}`}>
            {oracle.hbar_change_1h > 0 ? "+" : ""}
            {(oracle.hbar_change_1h * 100).toFixed(1)}% 1h
          </span>
        </div>

        <div className="flex items-center justify-between gap-2 px-1 mt-2">
          <DataLabel
            label="24h Realized Vol"
            value={`${(oracle.realized_vol_24h * 100).toFixed(0)}%`}
          />
          <StatusBadge volLabel={oracle.vol_label} />
        </div>

        {/* Volatility bar */}
        <div className="w-full h-1.5 bg-surface-light rounded-full overflow-hidden border border-white/5">
          <div
            className="h-full transition-all duration-500 rounded-full"
            style={{
              width: `${volPercent}%`,
              backgroundColor:
                oracle.vol_label === "LOW"
                  ? "hsl(var(--neon-green))"
                  : oracle.vol_label === "MEDIUM"
                    ? "hsl(var(--warning-amber))"
                    : "hsl(var(--overdrive-magenta))",
            }}
          />
        </div>

        <p className="text-[11px] font-display tracking-widest text-muted/60 flex justify-end uppercase mt-2">
          Source: {oracle.data_source} <span className="text-neon-green ml-1">✓</span>
        </p>
      </div>
    </GlowCard>
  );
}

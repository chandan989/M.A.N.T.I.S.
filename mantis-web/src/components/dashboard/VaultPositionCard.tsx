import GlowCard from "@/components/shared/GlowCard";
import DataLabel from "@/components/shared/DataLabel";
import { mockVaultPosition } from "@/data/mockVaultPosition";
import { CheckCircle, XCircle } from "lucide-react";

export default function VaultPositionCard() {
  const v = mockVaultPosition;

  return (
    <GlowCard glowColor={v.inRange ? "green" : "magenta"} pulsing={!v.inRange} className="group">
      <div className="flex flex-col gap-5">
        <div className="flex items-center justify-between border-b border-white/5 pb-3 group-hover:border-primary/20 transition-smooth">
          <h2 className="font-display text-sm tracking-widest text-muted group-hover:text-primary transition-smooth">VAULT POSITION</h2>
          <span className="text-[11px] font-sans px-2 py-1 bg-white/5 rounded-md text-muted border border-white/5">{v.strategy}</span>
        </div>

        <div className="flex items-center gap-2 bg-black/20 p-3 rounded-xl border border-white/5">
          {v.inRange ? (
            <CheckCircle className="w-5 h-5 text-neon-green/80" />
          ) : (
            <XCircle className="w-5 h-5 text-secondary" />
          )}
          <span className={`text-sm font-medium tracking-wide ${v.inRange ? "text-neon-green" : "text-secondary"}`}>
            {v.inRange ? "IN RANGE" : "OUT OF RANGE"}
          </span>
        </div>

        <div className="text-center py-4 bg-surface-light/30 rounded-2xl border border-white/5 mt-2">
          <span className="font-display text-5xl text-foreground tracking-tight">{v.currentAPY}%</span>
          <span className="block text-xs uppercase tracking-widest text-muted mt-2 font-display">Current APY</span>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <DataLabel label="Range" value={`$${v.rangeLow} — $${v.rangeHigh}`} />
          <DataLabel label="Pending Rewards" value={`$${v.pendingRewards} ${v.pendingRewardToken}`} valueColor="text-neon-green" />
          <DataLabel label="Last Harvest" value={`${v.lastHarvestHoursAgo}h ago`} />
        </div>
      </div>
    </GlowCard>
  );
}

import { useState } from "react";
import Layout from "@/components/layout/Layout";
import { useAgent } from "@/context/AgentContext";
import { RiskProfile, ThresholdConfig } from "@/types/mantis";
import { Shield, Zap, Flame, AlertTriangle, Power } from "lucide-react";
import PulseIndicator from "@/components/shared/PulseIndicator";
import GlowCard from "@/components/shared/GlowCard";

const PROFILES: { value: RiskProfile; label: string; desc: string; icon: typeof Shield }[] = [
  { value: "conservative", label: "CONSERVATIVE", desc: "Protect capital above all", icon: Shield },
  { value: "moderate", label: "MODERATE", desc: "Balance yield and safety", icon: Zap },
  { value: "aggressive", label: "AGGRESSIVE", desc: "Maximize yield, accept higher risk", icon: Flame },
];

export default function Settings() {
  const { agent, setPaused, setRiskProfile } = useAgent();
  const [thresholds, setThresholds] = useState<ThresholdConfig>({
    volatilityThreshold: 0.15,
    sentimentThreshold: -0.4,
    sentryIntervalSeconds: 60,
    minHarvestIntervalHours: 2,
  });
  const [showWithdrawModal, setShowWithdrawModal] = useState(false);

  return (
    <Layout>
      <div className="p-4 md:p-6 space-y-6 max-w-3xl">
        <h1 className="font-display text-lg tracking-widest text-foreground">Settings</h1>

        {/* Risk Profile */}
        <GlowCard>
          <h2 className="font-display text-xs tracking-wider text-muted-foreground mb-4">
            Risk Profile
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {PROFILES.map(({ value, label, desc, icon: Icon }) => (
              <button
                key={value}
                onClick={() => setRiskProfile(value)}
                className={`border p-4 text-left transition-all ${
                  agent.riskProfile === value
                    ? "border-synthetic-purple bg-secondary animate-pulse-glow-purple"
                    : "border-border hover:border-synthetic-purple"
                }`}
              >
                <Icon className={`w-5 h-5 mb-2 ${agent.riskProfile === value ? "text-synthetic-purple" : "text-muted-foreground"}`} />
                <p className="font-display text-xs text-foreground">{label}</p>
                <p className="text-xs text-muted-foreground mt-1">{desc}</p>
              </button>
            ))}
          </div>
        </GlowCard>

        {/* Thresholds */}
        <GlowCard>
          <h2 className="font-display text-xs tracking-wider text-muted-foreground mb-4">
            Thresholds
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {(
              [
                ["volatilityThreshold", "VOLATILITY_THRESHOLD"],
                ["sentimentThreshold", "SENTIMENT_THRESHOLD"],
                ["sentryIntervalSeconds", "SENTRY_INTERVAL_SECONDS"],
                ["minHarvestIntervalHours", "MIN_HARVEST_INTERVAL_HOURS"],
              ] as const
            ).map(([key, label]) => (
              <div key={key} className="flex flex-col gap-1">
                <label className="text-xs text-muted-foreground font-display">{label}</label>
                <input
                  type="number"
                  step="0.01"
                  value={thresholds[key]}
                  onChange={(e) =>
                    setThresholds((t) => ({ ...t, [key]: parseFloat(e.target.value) || 0 }))
                  }
                  className="bg-secondary border border-border px-3 py-2 text-sm font-body text-foreground outline-none focus:border-synthetic-purple"
                />
              </div>
            ))}
          </div>
        </GlowCard>

        {/* Vault Config */}
        <GlowCard>
          <h2 className="font-display text-xs tracking-wider text-muted-foreground mb-4">
            Vault Configuration
          </h2>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Hedera Account ID</span>
              <span className="text-foreground font-body">0.0.XXXX●●●</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Network</span>
              <span className="text-neon-green font-body">MAINNET</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Bonzo Vault ID</span>
              <span className="text-foreground font-body">vault-hbar-usdc-001</span>
            </div>
          </div>
        </GlowCard>

        {/* Notifications */}
        <GlowCard>
          <h2 className="font-display text-xs tracking-wider text-muted-foreground mb-4">
            Notification Channels
          </h2>
          <div className="space-y-2 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-foreground">Telegram</span>
              <div className="flex items-center gap-2">
                <PulseIndicator color="green" />
                <span className="text-neon-green text-xs">CONNECTED</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-foreground">WhatsApp</span>
              <span className="text-muted-foreground text-xs">NOT CONFIGURED</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-foreground">Signal</span>
              <span className="text-muted-foreground text-xs">NOT CONFIGURED</span>
            </div>
          </div>
        </GlowCard>

        {/* Danger Zone */}
        <GlowCard glowColor="magenta">
          <h2 className="font-display text-xs tracking-wider text-overdrive-magenta mb-4">
            Danger Zone
          </h2>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => setPaused(!agent.executionPaused)}
              className="border border-warning-amber text-warning-amber px-4 py-2 text-xs font-display hover:bg-warning-amber hover:text-warning-foreground transition-colors flex items-center gap-2"
            >
              <Power className="w-4 h-4" />
              {agent.executionPaused ? "RESUME AGENT" : "PAUSE AGENT"}
            </button>
            <button
              onClick={() => setShowWithdrawModal(true)}
              className="border border-overdrive-magenta text-overdrive-magenta px-4 py-2 text-xs font-display hover:bg-overdrive-magenta hover:text-primary-foreground transition-colors flex items-center gap-2"
            >
              <AlertTriangle className="w-4 h-4" />
              EMERGENCY WITHDRAW ALL
            </button>
          </div>
        </GlowCard>
      </div>

      {/* Confirmation Modal */}
      {showWithdrawModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-background/80">
          <div className="border border-overdrive-magenta bg-card p-6 max-w-sm w-full mx-4 animate-pulse-glow-magenta">
            <h3 className="font-display text-sm text-overdrive-magenta mb-3">
              ⚠ EMERGENCY WITHDRAWAL
            </h3>
            <p className="text-xs text-muted-foreground mb-4 font-body">
              This will immediately withdraw ALL funds from the Bonzo vault and convert to USDC.
              This action cannot be undone.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowWithdrawModal(false)}
                className="flex-1 border border-border px-3 py-2 text-xs font-display text-muted-foreground hover:text-foreground transition-colors"
              >
                CANCEL
              </button>
              <button
                onClick={() => setShowWithdrawModal(false)}
                className="flex-1 border border-overdrive-magenta bg-overdrive-magenta text-primary-foreground px-3 py-2 text-xs font-display hover:opacity-90 transition-opacity"
              >
                CONFIRM WITHDRAW
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}

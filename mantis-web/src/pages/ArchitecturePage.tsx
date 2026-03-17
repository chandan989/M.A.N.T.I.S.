import { useState } from "react";
import { motion } from "framer-motion";
import Layout from "@/components/layout/Layout";
import {
  Bug,
  Brain,
  Radar,
  Radio,
  Database,
  MessageCircle,
  Globe,
  Smartphone,
  Terminal,
  Hexagon,
} from "lucide-react";

const LAYERS = [
  {
    id: "ui",
    label: "User Interface Layer",
    color: "var(--hedera-blue)",
    icons: [
      { icon: Smartphone, label: "Telegram" },
      { icon: MessageCircle, label: "WhatsApp" },
      { icon: Terminal, label: "CLI" },
    ],
  },
  {
    id: "runtime",
    label: "Core Agent Runtime",
    color: "var(--synthetic-purple)",
    isCore: true,
  },
  {
    id: "skills",
    label: "Skills Layer",
    color: "var(--overdrive-magenta)",
    nodes: [
      { icon: Radar, label: "SENTRY", desc: "Twitter / News / Polymarket" },
      { icon: Globe, label: "ORACLE", desc: "SupraOracles / Pyth" },
      { icon: Hexagon, label: "HEDERA", desc: "Agent Kit / Bonzo ABI" },
      { icon: Database, label: "MEMORY", desc: "SQLite State" },
      { icon: Radio, label: "COMMS", desc: "Telegram Bot" },
    ],
  },
  {
    id: "chain",
    label: "On-Chain Layer",
    color: "var(--neon-green)",
  },
];

const containerVariants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.15 } },
};

const layerVariants = {
  hidden: { opacity: 0, y: 30 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

export default function ArchitecturePage() {
  const [simulating, setSimulating] = useState(false);
  const [thinkingText, setThinkingText] = useState("");

  function triggerSimulation() {
    if (simulating) return;
    setSimulating(true);
    setThinkingText("");

    const reasoning =
      "Analyzing... Vol: 82% (HIGH). Sentiment: -0.62 (BEARISH). Evaluating WIDEN_RANGE action. Confidence: 0.87. Executing...";
    let i = 0;
    const typeInterval = setInterval(() => {
      if (i < reasoning.length) {
        setThinkingText(reasoning.slice(0, i + 1));
        i++;
      } else {
        clearInterval(typeInterval);
        setTimeout(() => setSimulating(false), 2000);
      }
    }, 30);
  }

  return (
    <Layout>
      <div className="p-4 md:p-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="font-display text-lg tracking-widest text-foreground">
            X-RAY VIEW — CLAW-FI ARCHITECTURE
          </h1>
          <button
            onClick={triggerSimulation}
            disabled={simulating}
            className={`border px-4 py-2 text-xs font-display tracking-wider transition-colors ${
              simulating
                ? "border-overdrive-magenta text-overdrive-magenta animate-pulse-glow-magenta"
                : "border-synthetic-purple text-synthetic-purple hover:bg-synthetic-purple hover:text-primary-foreground"
            }`}
          >
            {simulating ? "SIMULATING..." : "TRIGGER SIMULATION"}
          </button>
        </div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="show"
          className="flex flex-col gap-4 relative"
        >
          {/* Connection lines SVG */}
          <svg
            className="absolute inset-0 w-full h-full pointer-events-none z-0"
            style={{ overflow: "visible" }}
          >
            {simulating && (
              <>
                <line
                  x1="50%"
                  y1="15%"
                  x2="50%"
                  y2="35%"
                  stroke="hsl(var(--overdrive-magenta))"
                  strokeWidth="1"
                  strokeDasharray="4 4"
                  className="animate-pulse-dot"
                />
                <line
                  x1="50%"
                  y1="45%"
                  x2="50%"
                  y2="65%"
                  stroke="hsl(var(--overdrive-magenta))"
                  strokeWidth="1"
                  strokeDasharray="4 4"
                  className="animate-pulse-dot"
                />
                <line
                  x1="50%"
                  y1="75%"
                  x2="50%"
                  y2="90%"
                  stroke="hsl(var(--overdrive-magenta))"
                  strokeWidth="1"
                  strokeDasharray="4 4"
                  className="animate-pulse-dot"
                />
              </>
            )}
          </svg>

          {/* Layer 1: UI */}
          <motion.div variants={layerVariants} className="relative z-10">
            <div className="border border-border p-4 bg-card">
              <h3
                className="font-display text-xs tracking-wider mb-3"
                style={{ color: `hsl(${LAYERS[0].color})` }}
              >
                {LAYERS[0].label}
              </h3>
              <div className="flex gap-4 justify-center">
                {LAYERS[0].icons?.map(({ icon: Icon, label }) => (
                  <div
                    key={label}
                    className={`flex flex-col items-center gap-1 p-3 border border-border ${
                      simulating ? "animate-pulse-glow-purple" : ""
                    }`}
                  >
                    <Icon className="w-6 h-6 text-hedera-blue" />
                    <span className="text-[10px] text-muted-foreground">{label}</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Layer 2: Runtime */}
          <motion.div variants={layerVariants} className="relative z-10">
            <div
              className={`border p-4 bg-card ${
                simulating
                  ? "border-synthetic-purple animate-pulse-glow-purple"
                  : "border-border"
              }`}
            >
              <h3 className="font-display text-xs tracking-wider mb-3 text-synthetic-purple">
                Core Agent Runtime
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="border border-border p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <Database className="w-4 h-4 text-muted-foreground" />
                    <span className="text-xs text-muted-foreground font-display">Memory & Context</span>
                  </div>
                  <pre className="text-[10px] text-muted-foreground font-body overflow-hidden">
{`{
  "risk_profile": "moderate",
  "last_action": "WIDEN_RANGE",
  "consecutive_no_ops": 2,
  "vault_apy": 14.2
}`}
                  </pre>
                </div>
                <div className="border border-border p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <Brain className="w-4 h-4 text-synthetic-purple" />
                    <span className="text-xs text-muted-foreground font-display">Reasoning Engine</span>
                  </div>
                  {simulating ? (
                    <p className="text-xs text-foreground font-body">
                      {thinkingText}
                      <span className="animate-blink">▊</span>
                    </p>
                  ) : (
                    <p className="text-xs text-muted-foreground font-body">
                      LLM: Claude Sonnet — Awaiting next tick...
                    </p>
                  )}
                </div>
              </div>
            </div>
          </motion.div>

          {/* Layer 3: Skills */}
          <motion.div variants={layerVariants} className="relative z-10">
            <div className="border border-border p-4 bg-card">
              <h3 className="font-display text-xs tracking-wider mb-3 text-overdrive-magenta">
                Skills Layer
              </h3>
              <div className="flex flex-wrap gap-3 justify-center">
                {LAYERS[2].nodes?.map(({ icon: Icon, label, desc }) => (
                  <div
                    key={label}
                    className={`group relative flex flex-col items-center gap-2 p-4 border border-border w-28 transition-colors hover:border-overdrive-magenta ${
                      simulating && (label === "SENTRY" || label === "ORACLE" || label === "HEDERA")
                        ? "animate-pulse-glow-magenta border-overdrive-magenta"
                        : ""
                    }`}
                  >
                    <div className="w-10 h-10 border border-border flex items-center justify-center" style={{ borderRadius: "50%" }}>
                      <Icon className="w-5 h-5 text-overdrive-magenta" />
                    </div>
                    <span className="text-xs font-display text-foreground">{label}</span>
                    <span className="text-[9px] text-muted-foreground text-center">{desc}</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Layer 4: On-Chain */}
          <motion.div variants={layerVariants} className="relative z-10">
            <div
              className={`border border-border p-4 bg-card ${
                simulating ? "animate-pulse-glow-green" : ""
              }`}
            >
              <h3 className="font-display text-xs tracking-wider mb-3 text-neon-green">
                On-Chain Layer
              </h3>
              <div className="flex items-center justify-center gap-8">
                <div className="text-center">
                  <Bug className="w-6 h-6 text-neon-green mx-auto mb-1" />
                  <span className="text-xs text-foreground font-display">Bonzo Finance</span>
                </div>
                <div className="text-center">
                  <span className="text-xs text-foreground font-display">SaucerSwap</span>
                </div>
                <div className="text-center">
                  <Hexagon className="w-6 h-6 text-hedera-blue mx-auto mb-1" />
                  <span className="text-xs text-foreground font-display">HEDERA MAINNET</span>
                </div>
              </div>
              <p className="text-center text-xs text-muted-foreground mt-3 font-body">
                Last Tx: 0x7a2f...4d91
              </p>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </Layout>
  );
}

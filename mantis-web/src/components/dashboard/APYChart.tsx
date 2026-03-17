import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceDot } from "recharts";
import { mockAPYHistory } from "@/data/mockAPYHistory";
import GlowCard from "@/components/shared/GlowCard";

export default function APYChart() {
  const harvests = mockAPYHistory.filter((d) => d.harvestOccurred);

  return (
    <GlowCard className="col-span-full md:col-span-2">
      <h2 className="font-display text-sm tracking-widest text-muted mb-4 border-b border-white/5 pb-3">
        APY HISTORY — 7 DAYS
      </h2>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={mockAPYHistory}>
          <XAxis
            dataKey="timestamp"
            xKey="timestamp"
            tick={{ fill: "hsl(253, 16%, 44%)", fontSize: 11, fontFamily: "Outfit" }}
            axisLine={{ stroke: "rgba(255, 255, 255, 0.1)" }}
            tickLine={false}
          />
          <YAxis
            domain={[10, 16]}
            tick={{ fill: "hsl(253, 16%, 44%)", fontSize: 11, fontFamily: "Outfit" }}
            axisLine={{ stroke: "rgba(255, 255, 255, 0.1)" }}
            tickLine={false}
            tickFormatter={(v: number) => `${v}%`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "rgba(26, 21, 37, 0.9)",
              border: "1px solid rgba(131, 61, 206, 0.3)",
              borderRadius: "12px",
              fontFamily: "Outfit",
              fontSize: 13,
              boxShadow: "0 4px 20px rgba(0, 0, 0, 0.4)",
              backdropFilter: "blur(10px)"
            }}
            labelStyle={{ color: "hsl(268, 45%, 61%)", fontFamily: "Orbitron", fontSize: 11, letterSpacing: "0.1em", marginBottom: "4px" }}
          />
          <Line
            type="monotone"
            dataKey="apy"
            stroke="hsl(269, 61%, 52%)"
            strokeWidth={3}
            dot={false}
            activeDot={{ r: 6, fill: "hsl(268, 45%, 61%)", stroke: "rgba(255, 255, 255, 0.5)", strokeWidth: 2 }}
          />
          {harvests.map((h) => (
            <ReferenceDot
              key={h.timestamp}
              x={h.timestamp}
              y={h.apy}
              r={4}
              fill="hsl(157, 100%, 50%)"
              stroke="none"
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </GlowCard>
  );
}

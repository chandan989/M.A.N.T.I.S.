interface PulseIndicatorProps {
  color: "green" | "magenta" | "amber" | "purple";
  size?: "sm" | "md";
}

const colorMap = {
  green: "bg-neon-green",
  magenta: "bg-overdrive-magenta",
  amber: "bg-warning-amber",
  purple: "bg-synthetic-purple",
};

export default function PulseIndicator({ color, size = "sm" }: PulseIndicatorProps) {
  const dim = size === "sm" ? "w-2 h-2" : "w-3 h-3";
  return <span className={`inline-block ${dim} ${colorMap[color]} animate-pulse-dot`} />;
}

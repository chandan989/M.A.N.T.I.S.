import { ReactNode } from "react";
import { GlowColor } from "@/types/mantis";

interface GlowCardProps {
  children: ReactNode;
  glowColor?: GlowColor;
  pulsing?: boolean;
  className?: string;
}

const glowClasses: Record<GlowColor, string> = {
  purple: "animate-pulse-glow-purple",
  magenta: "animate-pulse-glow-magenta",
  green: "animate-pulse-glow-green",
  amber: "animate-pulse-glow-green",
};

const borderHoverClasses: Record<GlowColor, string> = {
  purple: "hover:border-primary/50",
  magenta: "hover:border-secondary/50",
  green: "hover:border-neon-green/50",
  amber: "hover:border-warning-amber/50",
};

export default function GlowCard({ children, glowColor, pulsing, className = "" }: GlowCardProps) {
  const glow = glowColor && pulsing ? glowClasses[glowColor] : "";
  const hover = glowColor ? borderHoverClasses[glowColor] : "hover:border-primary/50";

  return (
    <div
      className={`glass-panel transition-smooth p-6 rounded-3xl ${hover} ${glow} ${className}`}
    >
      {children}
    </div>
  );
}

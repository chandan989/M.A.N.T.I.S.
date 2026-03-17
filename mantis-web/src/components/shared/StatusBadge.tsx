import { ActionType, AgentStatus, VolLabel, SentimentLabel } from "@/types/mantis";

interface StatusBadgeProps {
  status?: AgentStatus;
  action?: ActionType;
  volLabel?: VolLabel;
  sentimentLabel?: SentimentLabel;
  label?: string;
}

function getColorClass(props: StatusBadgeProps): string {
  if (props.status) {
    switch (props.status) {
      case "ACTIVE": return "border-neon-green text-neon-green";
      case "PAUSED": return "border-warning-amber text-warning-amber";
      case "ACTION_REQUIRED": return "border-overdrive-magenta text-overdrive-magenta";
    }
  }
  if (props.action) {
    switch (props.action) {
      case "HARVEST": return "border-neon-green text-neon-green";
      case "WIDEN_RANGE":
      case "TIGHTEN_RANGE": return "border-synthetic-purple text-synthetic-purple";
      case "WITHDRAW_ALL": return "border-overdrive-magenta text-overdrive-magenta";
      case "NO_OP": return "border-muted-grey text-muted-grey";
      case "NOTIFY_ONLY": return "border-warning-amber text-warning-amber";
      case "HARVEST_AND_SWAP": return "border-neon-green text-neon-green";
    }
  }
  if (props.volLabel) {
    switch (props.volLabel) {
      case "LOW": return "border-neon-green text-neon-green";
      case "MEDIUM": return "border-warning-amber text-warning-amber";
      case "HIGH":
      case "EXTREME": return "border-overdrive-magenta text-overdrive-magenta";
    }
  }
  if (props.sentimentLabel) {
    switch (props.sentimentLabel) {
      case "VERY_BULLISH":
      case "BULLISH": return "border-neon-green text-neon-green";
      case "NEUTRAL": return "border-warning-amber text-warning-amber";
      case "BEARISH":
      case "VERY_BEARISH": return "border-overdrive-magenta text-overdrive-magenta";
    }
  }
  return "border-muted-grey text-muted-grey";
}

function getLabel(props: StatusBadgeProps): string {
  return props.label || props.status || props.action || props.volLabel || props.sentimentLabel || "";
}

export default function StatusBadge(props: StatusBadgeProps) {
  return (
    <span className={`inline-flex items-center gap-1.5 border px-2 py-0.5 text-xs font-body uppercase tracking-wider ${getColorClass(props)}`}>
      {getLabel(props)}
    </span>
  );
}

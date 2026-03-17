interface DataLabelProps {
  label: string;
  value: string | number;
  valueColor?: string;
  large?: boolean;
}

export default function DataLabel({ label, value, valueColor, large }: DataLabelProps) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs text-muted-foreground uppercase tracking-wider">{label}</span>
      <span className={`font-display ${large ? "text-2xl" : "text-sm"} ${valueColor || "text-foreground"}`}>
        {value}
      </span>
    </div>
  );
}

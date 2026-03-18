export function Sparkline({ data }: { data: number[] }) {
  const BLOCKS = ' ▁▂▃▄▅▆▇█';
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  return (
    <span style={{ fontFamily: 'var(--font-mono)', letterSpacing: '0' }}>
      {data.map((v, i) => {
        const idx = Math.round(((v - min) / range) * 8);
        const color = v / max > 0.8 ? 'var(--color-error)' : 'var(--color-primary)';
        return <span key={i} style={{ color }}>{BLOCKS[idx]}</span>;
      })}
    </span>
  );
}

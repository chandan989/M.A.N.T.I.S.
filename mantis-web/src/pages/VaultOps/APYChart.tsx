import { APY_HISTORY_7D } from '../../data/mockData';
import { PanelBox } from '../../components/primitives/PanelBox';

const BLOCKS = ' ▁▂▃▄▅▆▇█';

export function APYChart() {
  // Downsample to ~60 points
  const sampled: number[] = [];
  const step = Math.floor(APY_HISTORY_7D.length / 60);
  for (let i = 0; i < APY_HISTORY_7D.length; i += step) {
    sampled.push(APY_HISTORY_7D[i]);
  }

  const max = Math.max(...sampled);
  const min = Math.min(...sampled);
  const range = max - min || 1;

  const levels = [20, 15, 10, 5];
  const rows: string[] = [];

  for (const level of levels) {
    let row = `${level.toString().padStart(3)}% ┤`;
    for (const v of sampled) {
      if (v >= level - 2.5 && v < level + 2.5) {
        const idx = Math.round(((v - min) / range) * 8);
        row += BLOCKS[idx];
      } else {
        row += ' ';
      }
    }
    rows.push(row);
  }

  const axisLine = '     ┼' + '─'.repeat(sampled.length);
  const labels = '      -7D' + ' '.repeat(Math.max(0, sampled.length - 28)) + 'NOW';

  return (
    <PanelBox title="APY HISTORY [7D]">
      <pre className="apy-chart">
        {rows.join('\n')}
        {'\n'}{axisLine}
        {'\n'}{labels}
      </pre>
    </PanelBox>
  );
}

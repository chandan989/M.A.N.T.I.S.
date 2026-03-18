import { useRef, useEffect, useMemo } from 'react';
import { useAgent } from '../../context/AgentContext';
import { useTypewriter } from '../../hooks/useTypewriter';
import { StatusTag } from '../../components/primitives/StatusTag';

export function ExecutionLog() {
  const { state } = useAgent();
  const logs = state.executionLog;
  const containerRef = useRef<HTMLDivElement>(null);
  const userScrolledUp = useRef(false);

  const lastEntry = logs[logs.length - 1];
  const prevEntries = useMemo(() => logs.slice(0, -1), [logs]);

  const lastText = lastEntry
    ? `${lastEntry.timestamp} > ${lastEntry.phase.padEnd(5)}: ${lastEntry.message}${lastEntry.action ? ' ' + lastEntry.action : ''}`
    : '';

  const { displayed, done } = useTypewriter(lastText, 8);

  const handleScroll = () => {
    const el = containerRef.current;
    if (!el) return;
    const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 30;
    userScrolledUp.current = !atBottom;
  };

  useEffect(() => {
    if (!userScrolledUp.current && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs, displayed]);

  return (
    <div ref={containerRef} className="execution-log" onScroll={handleScroll}>
      {prevEntries.map(entry => (
        <div key={entry.id} className="execution-log__entry">
          <span className="log-timestamp">{entry.timestamp}</span>
          {' > '}
          <span className={`log-phase ${entry.phase === 'ERR' ? 'log-phase--err' : ''}`}>
            {entry.phase.padEnd(5)}
          </span>
          {': '}
          {entry.message}
          {entry.action && <> {entry.action}</>}
          {entry.status && <> <StatusTag status={entry.status} /></>}
        </div>
      ))}
      {lastEntry && (
        <div className="execution-log__entry">
          <span>{displayed}</span>
          {done && lastEntry.status && <> <StatusTag status={lastEntry.status} /></>}
          <span className="cursor">█</span>
        </div>
      )}
    </div>
  );
}

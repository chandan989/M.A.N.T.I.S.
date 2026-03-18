import { useState, useEffect } from 'react';

export function useLiveTick(lastActionTs: number): string {
  const [now, setNow] = useState(Date.now());

  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, []);

  const diff = Math.floor((now - lastActionTs) / 1000);
  const mins = Math.floor(diff / 60).toString().padStart(2, '0');
  const secs = (diff % 60).toString().padStart(2, '0');
  return `${mins}:${secs}`;
}

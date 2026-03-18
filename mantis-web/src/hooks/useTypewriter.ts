import { useState, useEffect } from 'react';

export function useTypewriter(text: string, speed = 8): { displayed: string; done: boolean } {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    setIndex(0);
  }, [text]);

  useEffect(() => {
    if (index >= text.length) return;
    const timer = setInterval(() => {
      setIndex(prev => {
        if (prev >= text.length) { clearInterval(timer); return prev; }
        return prev + 1;
      });
    }, speed);
    return () => clearInterval(timer);
  }, [text, speed, index]);

  return { displayed: text.slice(0, index), done: index >= text.length };
}

import React from 'react';
import { TabNav } from '../TabNav/TabNav';
import { StatusBar } from '../StatusBar/StatusBar';
import './AppShell.css';

const HEADER = `╔═══════════════════════════════════════════════════════════════════════════════╗
║  M.A.N.T.I.S. // MARKET ANALYSIS & TACTICAL INTEGRATION SYSTEM  v1.0.0      ║
╚═══════════════════════════════════════════════════════════════════════════════╝`;

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <>
      <div className="width-warning">
        [ ERR ] TERMINAL WIDTH INSUFFICIENT. MINIMUM: 900px. RESIZE TO CONTINUE.
      </div>
      <div className="app-shell">
        <pre className="app-shell__header">{HEADER}</pre>
        <TabNav />
        <div className="app-shell__content">
          {children}
        </div>
      </div>
      <StatusBar />
    </>
  );
}

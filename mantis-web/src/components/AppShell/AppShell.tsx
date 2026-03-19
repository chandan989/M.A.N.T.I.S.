import React from 'react';
import { TabNav } from '../TabNav/TabNav';
import { StatusBar } from '../StatusBar/StatusBar';
import './AppShell.css';

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <>
      <div className="width-warning">
        [ ERR ] TERMINAL WIDTH INSUFFICIENT. MINIMUM: 900px. RESIZE TO CONTINUE.
      </div>
      <div className="app-shell">
        <div className="app-shell__header">
          <img src="/Logo.svg" alt="MANTIS Logo" className="app-shell__logo" />
          <div className="app-shell__title">
            <span className="app-shell__name">M.A.N.T.I.S. //</span>
            <span className="app-shell__desc">MARKET ANALYSIS & TACTICAL INTEGRATION SYSTEM v1.0.0</span>
          </div>
        </div>
        <div className="app-shell__line"></div>
        <TabNav />
        <div className="app-shell__content">
          {children}
        </div>
      </div>
      <StatusBar />
    </>
  );
}

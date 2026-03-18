import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import './Landing.css';

const ASCII_LOGO = `
 ╔══════════════════════════════════════════════════════════════════════════════════════════════╗
 ║ ███╗   ███╗ █████╗ ███╗   ██╗████████╗██╗███████╗                                            ║
 ║ ████╗ ████║██╔══██╗████╗  ██║╚══██╔══╝██║██╔════╝   MARKET ANALYSIS &                        ║
 ║ ██╔████╔██║███████║██╔██╗ ██║   ██║   ██║███████╗   NETWORK TACTICAL                         ║
 ║ ██║╚██╔╝██║██╔══██║██║╚██╗██║   ██║   ██║╚════██║   INTEGRATION SYSTEM                       ║
 ║ ██║ ╚═╝ ██║██║  ██║██║ ╚████║   ██║   ██║███████║                                            ║
 ║ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚══════╝   v1.0.0 // HEDERA MAINNET                 ║
 ╚══════════════════════════════════════════════════════════════════════════════════════════════╝`;

export default function Landing() {
  const navigate = useNavigate();
  const [bootText, setBootText] = useState("");
  const fullText = `> INITIALIZING SECURE CONNECTION...
> CONNECTING TO HEDERA MAINNET... [ OK ]
> LOADING BONZO VAULT CONTRACTS... [ OK ]
> WAKING REASONING ENGINE... [ OK ]
> SYNCING SAUCERSWAP LIQUIDITY POOLS... [ OK ]
> FETCHING INTEL: SUPRA ORACLES, PYTH NETWORK... [ OK ]
> SYSTEM READY.`;

  useEffect(() => {
    let currentIndex = 0;
    const interval = setInterval(() => {
      if (currentIndex <= fullText.length) {
        setBootText(fullText.slice(0, currentIndex));
        currentIndex++;
      } else {
        clearInterval(interval);
      }
    }, 15);
    return () => clearInterval(interval);
  }, [fullText]);

  return (
    <div className="landing">
      <div className="scanline"></div>
      <div className="landing__content">
        <pre className="landing__ascii">{ASCII_LOGO}</pre>

        <div className="landing__panels">
          <pre className="landing__panel">
{`┌─ [ ARCHITECTURE ] ──────────────────────────────────────────┐
│ TYPE      : 4-LAYER AUTONOMOUS AGENT                        │
│ GOAL      : BRIDGE OFF-CHAIN INTEL WITH ON-CHAIN EXECUTION  │
│ TARGETS   : BONZO FINANCE CLMM, SAUCERSWAP AMM              │
│ DEPLOY    : 24/7 HOSTED CLOUD EXECUTION                     │
└─────────────────────────────────────────────────────────────┘██
  ██████████████████████████████████████████████████████████████`}
          </pre>

          <pre className="landing__panel">
{`┌─ [ CAPABILITIES ] ──────────────────────────────────────────┐
│ > REAL-TIME VOLATILITY & PRICE TRACKING                     │
│ > AUTOMATED CONCENTRATED LIQUIDITY REBALANCING              │
│ > SENTIMENT-DRIVEN EARLY HARVEST DECISIONS                  │
│ > SEAMLESS HEDERA AGENT KIT INTEGRATION                     │
└─────────────────────────────────────────────────────────────┘██
  ██████████████████████████████████████████████████████████████`}
          </pre>
        </div>

        <div className="landing__boot-sequence">
          <pre>{bootText}<span className="cursor">█</span></pre>
        </div>

        <div className="landing__actions">
          <button className="landing__enter" onClick={() => navigate('/dashboard')}>
            {`>[ INITIALIZE TERMINAL ]<`}
          </button>
        </div>

        <div className="landing__footer">
          [!] WARNING: UNAUTHORIZED ACCESS PROHIBITED.
        </div>
      </div>
    </div>
  );
}

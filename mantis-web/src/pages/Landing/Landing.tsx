import { useNavigate } from 'react-router-dom';
import { useEffect, useState, useRef } from 'react';
import { useWallet } from '../../context/WalletContext';
import { PanelBox } from '../../components/primitives/PanelBox';
import { StatusTag } from '../../components/primitives/StatusTag';
import './Landing.css';

export default function Landing() {
  const navigate = useNavigate();
  const { status, wallet, connect } = useWallet();
  const [bootText, setBootText] = useState('');
  const [bootDone, setBootDone] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  const fullText = `> INITIALIZING SECURE CLOUD CONNECTION...
> CONNECTING TO HEDERA MAINNET... [ OK ]
> LOADING BONZO VAULT CONTRACTS... [ OK ]
> WAKING REASONING ENGINE... [ OK ]
> SYNCING SAUCERSWAP LIQUIDITY POOLS... [ OK ]
> FETCHING INTEL: SUPRA ORACLES, PYTH NETWORK... [ OK ]
> INGESTING SOCIAL SENTIMENT MODEL... [ OK ]
> SYSTEM READY. AWAITING OPERATOR INPUT.`;

  // Boot sequence typewriter
  useEffect(() => {
    let currentIndex = 0;
    const interval = setInterval(() => {
      if (currentIndex <= fullText.length) {
        setBootText(fullText.slice(0, currentIndex));
        currentIndex++;
        endRef.current?.scrollIntoView({ behavior: 'smooth' });
      } else {
        clearInterval(interval);
        setBootDone(true);
      }
    }, 15);
    return () => clearInterval(interval);
  }, [fullText]);

  // Auto-navigate once wallet is connected
  useEffect(() => {
    if (status === 'connected') {
      const t = setTimeout(() => navigate('/dashboard'), 1800);
      return () => clearTimeout(t);
    }
  }, [status, navigate]);

  const handleConnect = () => {
    if (!bootDone || status === 'connecting') return;
    connect();
  };

  const btnLabel = () => {
    if (!bootDone) return `>[ AWAITING BOOT... ]<`;
    if (status === 'connecting') return `>[ CONNECTING... ]<`;
    if (status === 'connected') return `>[ AUTHENTICATED ✓ ENTERING... ]<`;
    return `>[ CONNECT WALLET ]<`;
  };

  return (
    <div className="landing">
      <div className="scanline"></div>
      <div className="landing__content">

        <div className="landing__grid">

          {/* Main Left Column */}
          <div className="landing__col">
            <PanelBox title="WHAT IS M.A.N.T.I.S.?" doubleLine>
              <div className="term-text">
                <p>Traditional DeFi vaults are reactive—harvesting strictly on a schedule.</p>
                <p>M.A.N.T.I.S. is a <strong>continuously running, always-online</strong> intelligent agent bridging off-chain intelligence with on-chain autonomous execution via the Hedera Agent Kit.</p>
              </div>
            </PanelBox>

            <PanelBox title="CORE SKILLS">
              <div className="skills-list">
                <div className="skill-row">
                  <div className="skill-row-title"><span>SENTRY</span> <StatusTag status="ACTIVE" /></div>
                  <div className="skill-row-desc">Social/narrative sentiment vs Twitter &amp; Polymarket</div>
                </div>
                <div className="skill-row">
                  <div className="skill-row-title"><span>ORACLE</span> <StatusTag status="ACTIVE" /></div>
                  <div className="skill-row-desc">On-chain 24h realized volatility via SupraOracles</div>
                </div>
                <div className="skill-row">
                  <div className="skill-row-title"><span>HEDERA</span> <StatusTag status="ACTIVE" /></div>
                  <div className="skill-row-desc">Autonomous Tx execution via Hedera Agent Kit</div>
                </div>
                <div className="skill-row">
                  <div className="skill-row-title"><span>MEMORY</span> <StatusTag status="ACTIVE" /></div>
                  <div className="skill-row-desc">Intelligent state management &amp; history logging</div>
                </div>
              </div>
            </PanelBox>
          </div>

          {/* Center Column: Logo & Core Interactions */}
          <div className="landing__col landing__col--center">

            <div className="landing__header">
              <img src="/Logo.svg" alt="MANTIS Logo" className="landing__logo" />
              <div className="landing__title-block">
                <h1 className="landing__title">M.A.N.T.I.S. //</h1>
                <div className="landing__subtitle">MARKET ANALYSIS &amp; TACTICAL INTEGRATION SYSTEM v1.0.0</div>
              </div>
            </div>

            <PanelBox title="BOOT SEQUENCE" style={{ width: '100%', minHeight: '160px' }}>
              <div className="landing__boot-sequence">
                <pre>{bootText}<span className="cursor">█</span></pre>
                <div ref={endRef} />
              </div>
            </PanelBox>

            {/* Wallet connected info */}
            {status === 'connected' && wallet && (
              <div className="landing__wallet-connected">
                <pre className="landing__wallet-info">
{`┌─ [ WALLET AUTHENTICATED ] ──────────────────────────────────┐
│ ACCOUNT   : ${wallet.accountId.padEnd(45)}│
│ NETWORK   : HEDERA ${wallet.network.toUpperCase().padEnd(37)}│
│ STATUS    : VERIFIED ✓                                       │
└─────────────────────────────────────────────────────────────┘`}
                </pre>
              </div>
            )}

            <div className="landing__actions">
              <button
                id="connect-wallet-btn"
                className={[
                  'btn landing__enter',
                  !bootDone || status === 'connecting' ? 'landing__enter--disabled' : '',
                  status === 'connected' ? 'landing__enter--glow' : '',
                ]
                  .filter(Boolean)
                  .join(' ')}
                onClick={handleConnect}
                disabled={!bootDone || status === 'connecting' || status === 'connected'}
              >
                {btnLabel()}
              </button>
            </div>

            <div className="landing__footer">
              [!] WARNING: UNAUTHORIZED ACCESS PROHIBITED. WALLET SIGNATURE REQUIRED.
              {` | POWERED BY WALLETCONNECT`}
            </div>

          </div>

          {/* Side Right Column */}
          <div className="landing__col">
            <PanelBox title="ARCHITECTURE">
              <div className="tech-specs">
                <div className="spec-row">
                  <span className="spec-label">TYPE</span>
                  <span className="spec-value">4-LAYER AUTONOMOUS AGENT</span>
                </div>
                <div className="spec-row">
                  <span className="spec-label">GOAL</span>
                  <span className="spec-value">BRIDGE OFF-CHAIN INTEL WITH ON-CHAIN EXECUTION</span>
                </div>
                <div className="spec-row">
                  <span className="spec-label">TARGETS</span>
                  <span className="spec-value">BONZO FINANCE CLMM, SAUCERSWAP AMM</span>
                </div>
                <div className="spec-row">
                  <span className="spec-label">DEPLOY</span>
                  <span className="spec-value">24/7 HOSTED CLOUD EXECUTION</span>
                </div>
              </div>
            </PanelBox>

            <PanelBox title="CAPABILITIES">
              <ul className="term-list">
                <li>{'>'} REAL-TIME VOLATILITY &amp; PRICE TRACKING</li>
                <li>{'>'} AUTOMATED CONCENTRATED LIQUIDITY REBALANCING</li>
                <li>{'>'} SENTIMENT-DRIVEN EARLY HARVEST DECISIONS</li>
                <li>{'>'} SEAMLESS HEDERA AGENT KIT INTEGRATION</li>
              </ul>
            </PanelBox>

            <PanelBox title="DECISION LOOP">
              <div className="decision-loop">
                <div style={{ color: 'var(--color-primary)', marginBottom: '8px' }}>EVERY 60 SECONDS:</div>
                <ul className="term-list term-list--numbered">
                  <li><span>1. [SENSE]</span>   → Pull sentiment &amp; news headlines</li>
                  <li><span>2. [ORACLE]</span>  → Fetch price &amp; 24h volatility</li>
                  <li><span>3. [REASON]</span>  → LLM evaluates trigger rules</li>
                  <li><span>4. [EXECUTE]</span> → Fire Tx to Bonzo if criteria met</li>
                  <li><span>5. [LOG]</span>     → Record action to dashboard</li>
                </ul>
              </div>
            </PanelBox>
          </div>

        </div>
      </div>
    </div>
  );
}

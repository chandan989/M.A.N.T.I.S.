import { useNavigate } from 'react-router-dom';
import { useEffect, useState, useRef } from 'react';
import { PanelBox } from '../../components/primitives/PanelBox';
import { StatusTag } from '../../components/primitives/StatusTag';
import { HederaSessionEvent, HederaJsonRpcMethod, DAppConnector, HederaChainId } from '@hashgraph/hedera-wallet-connect';
import { LedgerId } from '@hiero-ledger/sdk';
import './Landing.css';

export default function Landing() {
  const navigate = useNavigate();
  const [bootText, setBootText] = useState("");
  const endRef = useRef<HTMLDivElement>(null);
  const dappConnectorRef = useRef<DAppConnector | null>(null);
  const fullText = `> INITIALIZING SECURE CLOUD CONNECTION...
> CONNECTING TO HEDERA MAINNET... [ OK ]
> LOADING BONZO VAULT CONTRACTS... [ OK ]
> WAKING REASONING ENGINE... [ OK ]
> SYNCING SAUCERSWAP LIQUIDITY POOLS... [ OK ]
> FETCHING INTEL: SUPRA ORACLES, PYTH NETWORK... [ OK ]
> INGESTING SOCIAL SENTIMENT MODEL... [ OK ]
> SYSTEM READY. AWAITING OPERATOR INPUT.`;

  useEffect(() => {
    let currentIndex = 0;
    const interval = setInterval(() => {
      if (currentIndex <= fullText.length) {
        setBootText(fullText.slice(0, currentIndex));
        currentIndex++;
        endRef.current?.scrollIntoView({ behavior: 'smooth' });
      } else {
        clearInterval(interval);
      }
    }, 15);
    return () => clearInterval(interval);
  }, [fullText]);

  const handleConnect = async () => {
    try {
      if (!dappConnectorRef.current) {
        const metadata = {
          name: "M.A.N.T.I.S.",
          description: "Market Analysis & Tactical Integration System",
          icons: ["https://your-domain.com/Logo.svg"], 
          url: window.location.origin
        };
        const projectId = "3abdd966c2db1ed45a2213ec37c0d7f4";

        dappConnectorRef.current = new DAppConnector(
          metadata,
          LedgerId.MAINNET,
          projectId,
          Object.values(HederaJsonRpcMethod),
          [HederaSessionEvent.ChainChanged, HederaSessionEvent.AccountsChanged],
          [HederaChainId.Mainnet]
        );
        
        await dappConnectorRef.current.init({ logger: 'error' });
      }
      
      const dAppConnector = dappConnectorRef.current;

      dAppConnector.onSessionIframeCreated = () => {
         // Handle session iframe event if needed
      };

      await dAppConnector.openModal();
      
      if (dAppConnector.signers.length > 0) {
        navigate('/dashboard');
      }
      
    } catch (error: any) {
      console.error("Hedera WalletConnect Connection Error:", error);
      alert("Error initializing Hedera WalletConnect: " + error.message);
    }
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
                  <div className="skill-row-desc">Social/narrative sentiment vs Twitter & Polymarket</div>
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
                  <div className="skill-row-desc">Intelligent state management & history logging</div>
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
                <div className="landing__subtitle">MARKET ANALYSIS & TACTICAL INTEGRATION SYSTEM v1.0.0</div>
              </div>
            </div>

            <PanelBox title="BOOT SEQUENCE" style={{ width: '100%', minHeight: '160px' }}>
              <div className="landing__boot-sequence">
                <pre>{bootText}<span className="cursor">█</span></pre>
                <div ref={endRef} />
              </div>
            </PanelBox>

            <div className="landing__actions">
              <button className="btn landing__enter" onClick={handleConnect}>
                {`>[ CONNECT WALLET ]<`}
              </button>
            </div>

            <div className="landing__footer">
              [!] WARNING: UNAUTHORIZED ACCESS PROHIBITED.
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
                <li>{'>'} REAL-TIME VOLATILITY & PRICE TRACKING</li>
                <li>{'>'} AUTOMATED CONCENTRATED LIQUIDITY REBALANCING</li>
                <li>{'>'} SENTIMENT-DRIVEN EARLY HARVEST DECISIONS</li>
                <li>{'>'} SEAMLESS HEDERA AGENT KIT INTEGRATION</li>
              </ul>
            </PanelBox>

            <PanelBox title="DECISION LOOP">
              <div className="decision-loop">
                <div style={{ color: 'var(--color-primary)', marginBottom: '8px' }}>EVERY 60 SECONDS:</div>
                <ul className="term-list term-list--numbered">
                  <li><span>1. [SENSE]</span>   → Pull sentiment & news headlines</li>
                  <li><span>2. [ORACLE]</span>  → Fetch price & 24h volatility</li>
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

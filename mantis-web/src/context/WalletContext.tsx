import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  type Dispatch,
  type SetStateAction,
} from 'react';
import {
  DAppConnector,
  HederaJsonRpcMethod,
  HederaSessionEvent,
  HederaChainId,
} from '@hashgraph/hedera-wallet-connect';
import { LedgerId } from '@hashgraph/sdk';

// ─── Types ───────────────────────────────────────────────────────────────────

export type WalletStatus = 'disconnected' | 'connecting' | 'connected';

export interface WalletInfo {
  accountId: string;
  network: string;
}

export interface WalletContextValue {
  status: WalletStatus;
  wallet: WalletInfo | null;
  connect: () => Promise<void>;
  disconnect: () => Promise<void>;
  connector: DAppConnector | null;
}

// ─── Context ─────────────────────────────────────────────────────────────────

const WalletContext = createContext<WalletContextValue | null>(null);

const PROJECT_ID =
  import.meta.env.VITE_WALLETCONNECT_PROJECT_ID ?? '6ef1bda914f4ea32a5b3f820bc8940c1';

const APP_METADATA = {
  name: 'M.A.N.T.I.S.',
  description: 'Market Analysis & Network Tactical Integration System — Hedera AI Agent',
  icons: ['https://avatars.githubusercontent.com/u/37784886'],
  url: window.location.origin,
};

// ─── Provider ─────────────────────────────────────────────────────────────────

export function WalletProvider({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = useState<WalletStatus>('disconnected');
  const [wallet, setWallet] = useState<WalletInfo | null>(null);
  const connectorRef = useRef<DAppConnector | null>(null);

  // Initialize DAppConnector once on mount
  useEffect(() => {
    let mounted = true;

    const init = async () => {
      // Support both Testnet and Mainnet so the wallet can show
      // whichever accounts the user has (Testnet for hackathon dev,
      // Mainnet for production).
      const connector = new DAppConnector(
        APP_METADATA,
        LedgerId.TESTNET,            // default ledger for pairing
        PROJECT_ID,
        Object.values(HederaJsonRpcMethod),
        [HederaSessionEvent.ChainChanged, HederaSessionEvent.AccountsChanged],
        [HederaChainId.Testnet, HederaChainId.Mainnet],   // accept both
      );

      await connector.init({ logger: 'error' });

      if (!mounted) return;

      connectorRef.current = connector;

      // Restore existing session if any
      const signers = connector.signers;
      if (signers.length > 0) {
        const signer = signers[0];
        const accountId = signer.getAccountId().toString();
        // Detect network from the signer's ledger ID
        const ledger = signer.getLedgerId?.();
        const network = ledger?.toString().includes('testnet') ? 'testnet' : 'mainnet';
        setWallet({ accountId, network });
        setStatus('connected');
      }

      // Listen for pairing events
      connector.walletConnectClient?.on('session_delete', () => {
        if (mounted) {
          setWallet(null);
          setStatus('disconnected');
        }
      });
    };

    init().catch((err) => {
      console.warn('[WalletContext] Init error:', err);
    });

    return () => {
      mounted = false;
    };
  }, []);

  const connect = async () => {
    const connector = connectorRef.current;
    if (!connector) {
      console.warn('[WalletContext] Connector not ready');
      return;
    }

    try {
      setStatus('connecting');

      const session = await connector.openModal();

      const signers = connector.signers;
      if (signers.length > 0) {
        const signer = signers[0];
        const accountId = signer.getAccountId().toString();
        // Detect network from the signer's ledger ID
        const ledger = signer.getLedgerId?.();
        const network = ledger?.toString().includes('testnet') ? 'testnet' : 'mainnet';
        setWallet({ accountId, network });
        setStatus('connected');
      } else {
        // Fallback: parse network from WalletConnect session namespace key
        // Hedera namespace accounts look like: "hedera:testnet:0.0.XXXXX"
        const accounts = Object.values(session.namespaces)
          .flatMap((ns) => ns.accounts ?? []);
        if (accounts.length > 0) {
          const parts = accounts[0].split(':');   // ["hedera", "testnet", "0.0.XXX"]
          const accountId = parts.pop() ?? '';
          const network = parts[1]?.includes('testnet') ? 'testnet' : 'mainnet';
          setWallet({ accountId, network });
          setStatus('connected');
        } else {
          setStatus('disconnected');
        }
      }
    } catch (err: unknown) {
      console.warn('[WalletContext] Connection cancelled or failed:', err);
      setStatus('disconnected');
    }
  };

  const disconnect = async () => {
    const connector = connectorRef.current;
    if (!connector) return;
    try {
      await connector.disconnectAll();
    } catch (_) {
      // ignore
    }
    setWallet(null);
    setStatus('disconnected');
  };

  return (
    <WalletContext.Provider
      value={{ status, wallet, connect, disconnect, connector: connectorRef.current }}
    >
      {children}
    </WalletContext.Provider>
  );
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useWallet(): WalletContextValue {
  const ctx = useContext(WalletContext);
  if (!ctx) throw new Error('useWallet must be used inside <WalletProvider>');
  return ctx;
}

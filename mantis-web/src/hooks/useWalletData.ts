/**
 * useWalletData
 * Fetches real account data from the Hedera Mirror Node REST API.
 * - HBAR balance (in tinybars → converted to HBAR)
 * - USDC token balance (if account holds it)
 * No API key required — Mirror Node is public.
 */

import { useEffect, useCallback } from 'react';
import { useWallet } from '../context/WalletContext';
import { useAgent } from '../context/AgentContext';

// Hedera Mirror Node endpoints
const MIRROR_MAINNET = 'https://mainnet-public.mirrornode.hedera.com';
const MIRROR_TESTNET = 'https://testnet.mirrornode.hedera.com';

// USDC on Hedera Mainnet (official Hedera USDC token)
const USDC_TOKEN_ID_MAINNET = '0.0.456858';
// USDC on Testnet — use a known testnet USDC or just show 0
const USDC_TOKEN_ID_TESTNET = '0.0.429274';

const TINYBARS_PER_HBAR = 100_000_000;

interface MirrorAccountResponse {
  balance?: {
    balance?: number;       // tinybars
    tokens?: Array<{
      token_id: string;
      balance: number;
    }>;
  };
}

export function useWalletData() {
  const { wallet, status } = useWallet();
  const { dispatch } = useAgent();

  const fetchAccountData = useCallback(async () => {
    if (status !== 'connected' || !wallet) return;

    const baseUrl = wallet.network === 'testnet' ? MIRROR_TESTNET : MIRROR_MAINNET;
    const usdcTokenId = wallet.network === 'testnet' ? USDC_TOKEN_ID_TESTNET : USDC_TOKEN_ID_MAINNET;

    try {
      const res = await fetch(
        `${baseUrl}/api/v1/accounts/${wallet.accountId}?limit=100`,
        { headers: { Accept: 'application/json' } }
      );

      if (!res.ok) {
        console.warn('[useWalletData] Mirror node error:', res.status);
        return;
      }

      const data: MirrorAccountResponse = await res.json();

      // HBAR balance
      const tinybars = data.balance?.balance ?? 0;
      const hbarBalance = Math.round((tinybars / TINYBARS_PER_HBAR) * 100) / 100;

      // USDC balance (find matching token)
      const usdcEntry = data.balance?.tokens?.find(t => t.token_id === usdcTokenId);
      // USDC has 6 decimals on Hedera
      const usdcBalance = usdcEntry ? Math.round((usdcEntry.balance / 1_000_000) * 100) / 100 : 0;

      dispatch({
        type: 'SET_WALLET',
        payload: {
          walletId: wallet.accountId,
          hbarBalance,
          usdcBalance,
          network: wallet.network as 'mainnet' | 'testnet',
        },
      });
    } catch (err) {
      console.warn('[useWalletData] Fetch error:', err);
    }
  }, [wallet, status, dispatch]);

  // Fetch on connect and every 30s while connected
  useEffect(() => {
    if (status !== 'connected') return;
    fetchAccountData();
    const interval = setInterval(fetchAccountData, 30_000);
    return () => clearInterval(interval);
  }, [status, fetchAccountData]);
}

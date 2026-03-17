import { SentryData } from "@/types/mantis";

export const mockSentryData: SentryData = {
  score: -0.62,
  label: "BEARISH",
  top_signals: [
    "HBAR whale dump spotted on-chain",
    "Crypto Fear Index: 28 (Extreme Fear)",
    "CryptoPanic: 82% bearish votes",
  ],
  source_count: 47,
  trending_topics: ["#HBAR", "#DeFi", "#Hedera", "BonzoFinance"],
  updatedAt: Date.now(),
};

import { VaultPosition } from "@/types/mantis";

export const mockVaultPosition: VaultPosition = {
  strategy: "HBAR / USDC CLMM",
  inRange: true,
  rangeLow: 0.075,
  rangeHigh: 0.115,
  currentAPY: 14.2,
  pendingRewards: 24.5,
  pendingRewardToken: "HBAR",
  lastHarvestHoursAgo: 3.8,
};

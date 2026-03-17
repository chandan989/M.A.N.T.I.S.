import { APYDataPoint } from "@/types/mantis";

export const mockAPYHistory: APYDataPoint[] = [
  { timestamp: "2025-03-10", apy: 12.1, harvestOccurred: false },
  { timestamp: "2025-03-11", apy: 13.4, harvestOccurred: true },
  { timestamp: "2025-03-12", apy: 11.8, harvestOccurred: false },
  { timestamp: "2025-03-13", apy: 14.2, harvestOccurred: true },
  { timestamp: "2025-03-14", apy: 15.1, harvestOccurred: false },
  { timestamp: "2025-03-15", apy: 13.7, harvestOccurred: false },
  { timestamp: "2025-03-16", apy: 14.2, harvestOccurred: true },
];

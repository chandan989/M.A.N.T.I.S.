import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
    hmr: {
      overlay: false,
    },
  },
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      // Required: hedera-wallet-connect imports @hiero-ledger/proto which lives
      // nested inside @hashgraph/sdk's own node_modules
      "@hiero-ledger/proto": path.resolve(
        __dirname,
        "node_modules/@hashgraph/sdk/node_modules/@hiero-ledger/proto"
      ),
    },
  },
  define: {
    // WalletConnect / Hedera SDK needs a global Buffer
    global: "globalThis",
  },
  optimizeDeps: {
    include: [],
  },
}));

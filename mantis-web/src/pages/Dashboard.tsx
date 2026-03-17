import Layout from "@/components/layout/Layout";
import AgentStatusCard from "@/components/dashboard/AgentStatusCard";
import VaultPositionCard from "@/components/dashboard/VaultPositionCard";
import SentimentGauge from "@/components/dashboard/SentimentGauge";
import OracleDataCard from "@/components/dashboard/OracleDataCard";
import RecentActionsLog from "@/components/dashboard/RecentActionsLog";
import APYChart from "@/components/dashboard/APYChart";

export default function Dashboard() {
  return (
    <Layout>
      <div className="p-4 md:p-6 space-y-4">
        <AgentStatusCard />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <VaultPositionCard />
          <SentimentGauge />
          <OracleDataCard />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <APYChart />
          <RecentActionsLog />
        </div>
      </div>
    </Layout>
  );
}

import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AgentProvider } from "@/context/AgentContext";
import Dashboard from "@/pages/Dashboard";
import Chat from "@/pages/Chat";
import ArchitecturePage from "@/pages/ArchitecturePage";
import Settings from "@/pages/Settings";
import NotFound from "@/pages/NotFound";

const App = () => (
  <AgentProvider>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/architecture" element={<ArchitecturePage />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  </AgentProvider>
);

export default App;

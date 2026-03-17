import { NavLink, useLocation } from "react-router-dom";
import { LayoutDashboard, MessageSquare, Hexagon, Settings, Bug } from "lucide-react";
import PulseIndicator from "@/components/shared/PulseIndicator";
import { useAgent } from "@/context/AgentContext";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/chat", icon: MessageSquare, label: "Chat" },
  { to: "/architecture", icon: Hexagon, label: "X-Ray View" },
  { to: "/settings", icon: Settings, label: "Settings" },
];

export default function Sidebar() {
  const location = useLocation();
  const { agent } = useAgent();

  const statusColor = agent.executionPaused ? "amber" : "green";

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden md:flex flex-col w-16 hover:w-56 transition-all duration-300 glass-panel border-r border-white/5 h-screen fixed left-0 top-0 z-50 overflow-hidden group rounded-none">
        <div className="flex items-center gap-3 px-4 h-14 border-b border-white/5">
          <div className="p-1.5 rounded-full bg-primary/20 border border-primary/30 shadow-[0_0_15px_rgba(131,61,206,0.2)] shrink-0">
            <Bug className="w-5 h-5 text-primary" />
          </div>
          <span className="font-display font-medium tracking-widest text-sm text-foreground whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity flex-1 ml-1" style={{ letterSpacing: '0.15em' }}>
            M.A.N.T.I.S.
          </span>
        </div>

        <nav className="flex-1 flex flex-col gap-2 p-3 mt-2">
          {navItems.map(({ to, icon: Icon, label }) => {
            const isActive = location.pathname === to;
            return (
              <NavLink
                key={to}
                to={to}
                className={`flex items-center gap-3 px-3 py-3 rounded-xl text-sm transition-smooth relative overflow-hidden group/link ${
                  isActive
                    ? "bg-primary/20 text-foreground border border-primary/30 shadow-[0_0_15px_rgba(131,61,206,0.15)] glow-primary"
                    : "text-muted-foreground hover:text-foreground hover:bg-white/5 border border-transparent"
                }`}
              >
                {isActive && (
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary shadow-[0_0_10px_rgba(131,61,206,0.8)]"></div>
                )}
                <Icon className={`w-5 h-5 shrink-0 ${isActive ? 'text-primary' : 'group-hover/link:text-accent transition-smooth'}`} />
                <span className="font-sans whitespace-nowrap opacity-0 group-[.hover\\:w-56]:opacity-100 transition-opacity">
                  {label}
                </span>
              </NavLink>
            );
          })}
        </nav>

        <div className="p-4 border-t border-white/5 flex items-center gap-3">
          <PulseIndicator color={statusColor} />
          <span className="text-xs uppercase whitespace-nowrap opacity-0 group-[.hover\\:w-56]:opacity-100 transition-opacity text-muted tracking-widest font-display">
            {agent.executionPaused ? "PAUSED" : "ACTIVE"}
          </span>
        </div>
      </aside>

      {/* Mobile bottom tab bar */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 glass-panel border-t border-white/5 flex rounded-none">
        {navItems.map(({ to, icon: Icon, label }) => {
          const isActive = location.pathname === to;
          return (
            <NavLink
              key={to}
              to={to}
              className={`flex-1 flex flex-col items-center gap-1 py-3 text-[10px] font-sans transition-smooth ${
                isActive ? "text-primary bg-primary/10 border-t-2 border-primary" : "text-muted hover:text-textMain hover:bg-white/5 border-t-2 border-transparent"
              }`}
            >
              <Icon className="w-5 h-5" />
              {label}
            </NavLink>
          );
        })}
      </nav>
    </>
  );
}

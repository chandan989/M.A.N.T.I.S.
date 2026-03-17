import { ReactNode } from "react";
import Sidebar from "./Sidebar";

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-background relative overflow-hidden text-foreground">
      <Sidebar />
      <main className="md:ml-16 pb-16 md:pb-0 min-h-screen relative z-10 w-full transition-smooth">
        {children}
      </main>
    </div>
  );
}

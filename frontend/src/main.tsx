import React from "react";
import ReactDOM from "react-dom/client";
import {
  Activity,
  Bell,
  Building2,
  Headphones,
  LineChart,
  Pause,
  PhoneCall,
  Settings,
  ShieldCheck,
  Users,
} from "lucide-react";
import "./styles.css";

type AgentStatus = "available" | "paused" | "in_call" | "offline" | "wrap_up";

type Agent = {
  id: string;
  name: string;
  extension: string;
  status: AgentStatus;
  queue: string;
  tenant: string;
};

const agents: Agent[] = [
  { id: "1", name: "Ana Martins", extension: "1001", status: "in_call", queue: "Vendas", tenant: "Tenant A" },
  { id: "2", name: "Bruno Silva", extension: "1002", status: "available", queue: "Suporte", tenant: "Tenant A" },
  { id: "3", name: "Carla Souza", extension: "2001", status: "paused", queue: "Financeiro", tenant: "Tenant B" },
  { id: "4", name: "Diego Lima", extension: "2002", status: "wrap_up", queue: "Vendas", tenant: "Tenant B" },
  { id: "5", name: "Elisa Rocha", extension: "3001", status: "offline", queue: "Retencao", tenant: "Tenant C" },
];

const statusLabel: Record<AgentStatus, string> = {
  available: "Disponivel",
  paused: "Pausa",
  in_call: "Em chamada",
  offline: "Offline",
  wrap_up: "Wrap-up",
};

function Stat({ label, value, icon }: { label: string; value: string; icon: React.ReactNode }) {
  return (
    <section className="stat">
      <div className="statIcon">{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
    </section>
  );
}

function App() {
  return (
    <div className="appShell">
      <aside className="sidebar">
        <div className="brand">
          <Headphones size={24} />
          <div>
            <strong>Call Center Control</strong>
            <span>FusionPBX Multi-tenant</span>
          </div>
        </div>

        <nav>
          <button className="navActive" title="Operacao"><Activity size={18} /> Operacao</button>
          <button title="Agentes"><Users size={18} /> Agentes</button>
          <button title="Tenants"><Building2 size={18} /> Tenants</button>
          <button title="Relatorios"><LineChart size={18} /> Relatorios</button>
          <button title="Configuracoes"><Settings size={18} /> Configuracoes</button>
        </nav>
      </aside>

      <main>
        <header className="topbar">
          <div>
            <h1>Supervisao em tempo real</h1>
            <p>Visao consolidada de filas, agentes e tenants.</p>
          </div>
          <button className="alertButton" title="Alertas"><Bell size={18} /> 3</button>
        </header>

        <section className="statsGrid">
          <Stat label="Agentes ativos" value="87 / 100" icon={<Users size={22} />} />
          <Stat label="Chamadas na fila" value="14" icon={<PhoneCall size={22} />} />
          <Stat label="SLA atual" value="92%" icon={<ShieldCheck size={22} />} />
          <Stat label="Em pausa" value="9" icon={<Pause size={22} />} />
        </section>

        <section className="workArea">
          <div className="panel wide">
            <div className="panelHeader">
              <h2>Agentes</h2>
              <div className="segmented">
                <button className="selected">Todos</button>
                <button>Online</button>
                <button>Pausa</button>
              </div>
            </div>
            <table>
              <thead>
                <tr>
                  <th>Agente</th>
                  <th>Ramal</th>
                  <th>Fila</th>
                  <th>Tenant</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {agents.map((agent) => (
                  <tr key={agent.id}>
                    <td>{agent.name}</td>
                    <td>{agent.extension}</td>
                    <td>{agent.queue}</td>
                    <td>{agent.tenant}</td>
                    <td><span className={`status ${agent.status}`}>{statusLabel[agent.status]}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="panel">
            <div className="panelHeader">
              <h2>Filas criticas</h2>
            </div>
            <div className="queueList">
              <div><strong>Vendas</strong><span>8 aguardando</span></div>
              <div><strong>Suporte</strong><span>4 aguardando</span></div>
              <div><strong>Retencao</strong><span>2 aguardando</span></div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(<App />);


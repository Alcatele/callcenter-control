import React, { FormEvent, useEffect, useMemo, useState } from "react";
import ReactDOM from "react-dom/client";
import {
  Activity,
  Building2,
  Headphones,
  LineChart,
  LogOut,
  Pause,
  PhoneCall,
  Plus,
  RefreshCw,
  Settings,
  ShieldCheck,
  Users,
} from "lucide-react";
import "./styles.css";

const API_BASE = "/api";

type AgentStatus = "available" | "paused" | "ringing" | "in_call" | "offline" | "wrap_up";

type Agent = {
  id: string;
  tenant_id: string;
  name: string;
  extension: string;
  status: AgentStatus;
  active: boolean;
};

type Queue = {
  id: string;
  tenant_id: string;
  name: string;
  extension: string | null;
  active: boolean;
};

type Tenant = {
  id: string;
  name: string;
  domain_name: string;
  fusionpbx_domain_uuid: string | null;
  active: boolean;
};

type Session = {
  access_token: string;
  role: string;
  tenant_id: string | null;
  name: string;
};

type ActiveView = "operation" | "agents" | "tenants" | "reports" | "settings";

const statusLabel: Record<AgentStatus, string> = {
  available: "Disponivel",
  paused: "Pausa",
  ringing: "Tocando",
  in_call: "Em chamada",
  offline: "Offline",
  wrap_up: "Wrap-up",
};

function apiHeaders(session: Session) {
  return {
    Authorization: `Bearer ${session.access_token}`,
    "Content-Type": "application/json",
  };
}

async function apiRequest<T>(path: string, session: Session, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      ...apiHeaders(session),
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Erro HTTP ${response.status}`);
  }

  return response.json() as Promise<T>;
}

function Stat({ label, value, icon }: { label: string; value: string; icon: React.ReactNode }) {
  return (
    <section className="stat">
      <div className="statIcon">{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
    </section>
  );
}

function Login({ onLogin }: { onLogin: (session: Session) => void }) {
  const [email, setEmail] = useState("pedro@alcatele.com.br");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");

    const form = new URLSearchParams();
    form.set("username", email);
    form.set("password", password);

    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: form,
      });

      if (!response.ok) {
        throw new Error("Email ou senha invalidos.");
      }

      const session = (await response.json()) as Session;
      localStorage.setItem("cc_session", JSON.stringify(session));
      onLogin(session);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha no login.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="loginScreen">
      <form className="loginPanel" onSubmit={submit}>
        <div className="loginBrand">
          <Headphones size={30} />
          <div>
            <strong>Call Center Control</strong>
            <span>FusionPBX Multi-tenant</span>
          </div>
        </div>

        <label>
          Email
          <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required />
        </label>

        <label>
          Senha
          <input
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            type="password"
            required
          />
        </label>

        {error ? <p className="formError">{error}</p> : null}

        <button className="primaryButton" disabled={loading} type="submit">
          {loading ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </main>
  );
}

function App() {
  const [session, setSession] = useState<Session | null>(() => {
    const raw = localStorage.getItem("cc_session");
    return raw ? (JSON.parse(raw) as Session) : null;
  });
  const [agents, setAgents] = useState<Agent[]>([]);
  const [queues, setQueues] = useState<Queue[]>([]);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeView, setActiveView] = useState<ActiveView>("operation");
  const [agentForm, setAgentForm] = useState({ name: "", extension: "", tenant_id: "" });
  const [queueForm, setQueueForm] = useState({ name: "", extension: "", tenant_id: "" });

  const tenantMap = useMemo(
    () => new Map(tenants.map((tenant) => [tenant.id, tenant.name])),
    [tenants],
  );

  async function loadData(activeSession = session) {
    if (!activeSession) return;
    setLoading(true);
    setMessage("");
    try {
      const [agentData, queueData] = await Promise.all([
        apiRequest<Agent[]>("/agents", activeSession),
        apiRequest<Queue[]>("/queues", activeSession),
      ]);
      setAgents(agentData);
      setQueues(queueData);

      if (activeSession.role === "admin") {
        const tenantData = await apiRequest<Tenant[]>("/tenants", activeSession);
        setTenants(tenantData);
        const firstTenant = tenantData[0]?.id ?? "";
        setAgentForm((current) => ({ ...current, tenant_id: current.tenant_id || firstTenant }));
        setQueueForm((current) => ({ ...current, tenant_id: current.tenant_id || firstTenant }));
      }
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Erro ao carregar dados.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, [session]);

  async function createAgent(event: FormEvent) {
    event.preventDefault();
    if (!session) return;
    await apiRequest<Agent>("/agents", session, {
      method: "POST",
      body: JSON.stringify(agentForm),
    });
    setAgentForm((current) => ({ ...current, name: "", extension: "" }));
    setMessage("Agente criado com sucesso.");
    await loadData(session);
  }

  async function createQueue(event: FormEvent) {
    event.preventDefault();
    if (!session) return;
    await apiRequest<Queue>("/queues", session, {
      method: "POST",
      body: JSON.stringify(queueForm),
    });
    setQueueForm((current) => ({ ...current, name: "", extension: "" }));
    setMessage("Fila criada com sucesso.");
    await loadData(session);
  }

  async function importTenantsFromFusionPbx() {
    if (!session) return;
    const result = await apiRequest<{ created: number; updated: number; total: number }>(
      "/fusionpbx/import-tenants",
      session,
      { method: "POST" },
    );
    setMessage(
      `FusionPBX importado: ${result.created} criados, ${result.updated} atualizados, ${result.total} encontrados.`,
    );
    await loadData(session);
  }

  function logout() {
    localStorage.removeItem("cc_session");
    setSession(null);
  }

  if (!session) {
    return <Login onLogin={setSession} />;
  }

  const available = agents.filter((agent) => agent.status === "available").length;
  const paused = agents.filter((agent) => agent.status === "paused").length;
  const inCall = agents.filter((agent) => agent.status === "in_call").length;
  const pageTitle = {
    operation: "Supervisao em tempo real",
    agents: "Agentes e filas",
    tenants: "Tenants",
    reports: "Relatorios",
    settings: "Configuracoes",
  }[activeView];

  const pageSubtitle = {
    operation: "Visao operacional consolidada dos tenants.",
    agents: "Cadastro operacional integrado a API.",
    tenants: "Dominios mapeados para o FusionPBX.",
    reports: "Indicadores iniciais do ambiente.",
    settings: "Parametros de acesso e integracao.",
  }[activeView];

  return (
    <div className="appShell">
      <aside className="sidebar">
        <div className="brand">
          <Headphones size={24} />
          <div>
            <strong>Call Center Control</strong>
            <span>{session.name}</span>
          </div>
        </div>

        <nav>
          <button className={activeView === "operation" ? "navActive" : ""} onClick={() => setActiveView("operation")} title="Operacao"><Activity size={18} /> Operacao</button>
          <button className={activeView === "agents" ? "navActive" : ""} onClick={() => setActiveView("agents")} title="Agentes"><Users size={18} /> Agentes</button>
          <button className={activeView === "tenants" ? "navActive" : ""} onClick={() => setActiveView("tenants")} title="Tenants"><Building2 size={18} /> Tenants</button>
          <button className={activeView === "reports" ? "navActive" : ""} onClick={() => setActiveView("reports")} title="Relatorios"><LineChart size={18} /> Relatorios</button>
          <button className={activeView === "settings" ? "navActive" : ""} onClick={() => setActiveView("settings")} title="Configuracoes"><Settings size={18} /> Configuracoes</button>
        </nav>
      </aside>

      <main>
        <header className="topbar">
          <div>
            <h1>{pageTitle}</h1>
            <p>{pageSubtitle}</p>
          </div>
          <div className="topbarActions">
            <button className="iconButton" onClick={() => loadData()} title="Atualizar">
              <RefreshCw size={18} />
            </button>
            <button className="iconButton" onClick={logout} title="Sair">
              <LogOut size={18} />
            </button>
          </div>
        </header>

        {message ? <div className="notice">{message}</div> : null}

        {(activeView === "operation" || activeView === "reports") && (
          <section className="statsGrid">
            <Stat label="Agentes cadastrados" value={String(agents.length)} icon={<Users size={22} />} />
            <Stat label="Disponiveis" value={String(available)} icon={<ShieldCheck size={22} />} />
            <Stat label="Em chamada" value={String(inCall)} icon={<PhoneCall size={22} />} />
            <Stat label="Em pausa" value={String(paused)} icon={<Pause size={22} />} />
          </section>
        )}

        {activeView === "agents" && (
          <section className="formsGrid">
            <form className="panel formPanel" onSubmit={createAgent}>
              <div className="panelHeader">
                <h2>Novo agente</h2>
                <Plus size={18} />
              </div>
              <label>
                Tenant
                <select
                  value={agentForm.tenant_id}
                  onChange={(event) => setAgentForm({ ...agentForm, tenant_id: event.target.value })}
                  required
                >
                  {tenants.map((tenant) => (
                    <option key={tenant.id} value={tenant.id}>{tenant.name}</option>
                  ))}
                </select>
              </label>
              <label>
                Nome
                <input
                  value={agentForm.name}
                  onChange={(event) => setAgentForm({ ...agentForm, name: event.target.value })}
                  required
                />
              </label>
              <label>
                Ramal
                <input
                  value={agentForm.extension}
                  onChange={(event) => setAgentForm({ ...agentForm, extension: event.target.value })}
                  required
                />
              </label>
              <button className="primaryButton" disabled={loading} type="submit">Criar agente</button>
            </form>

            <form className="panel formPanel" onSubmit={createQueue}>
              <div className="panelHeader">
                <h2>Nova fila</h2>
                <Plus size={18} />
              </div>
              <label>
                Tenant
                <select
                  value={queueForm.tenant_id}
                  onChange={(event) => setQueueForm({ ...queueForm, tenant_id: event.target.value })}
                  required
                >
                  {tenants.map((tenant) => (
                    <option key={tenant.id} value={tenant.id}>{tenant.name}</option>
                  ))}
                </select>
              </label>
              <label>
                Nome
                <input
                  value={queueForm.name}
                  onChange={(event) => setQueueForm({ ...queueForm, name: event.target.value })}
                  required
                />
              </label>
              <label>
                Ramal da fila
                <input
                  value={queueForm.extension}
                  onChange={(event) => setQueueForm({ ...queueForm, extension: event.target.value })}
                />
              </label>
              <button className="primaryButton" disabled={loading} type="submit">Criar fila</button>
            </form>
          </section>
        )}

        {(activeView === "operation" || activeView === "agents") && (
          <section className="workArea">
            <div className="panel wide">
              <div className="panelHeader">
                <h2>Agentes</h2>
              </div>
              <table>
                <thead>
                  <tr>
                    <th>Agente</th>
                    <th>Ramal</th>
                    <th>Tenant</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {agents.map((agent) => (
                    <tr key={agent.id}>
                      <td>{agent.name}</td>
                      <td>{agent.extension}</td>
                      <td>{tenantMap.get(agent.tenant_id) ?? agent.tenant_id}</td>
                      <td><span className={`status ${agent.status}`}>{statusLabel[agent.status]}</span></td>
                    </tr>
                  ))}
                  {agents.length === 0 ? (
                    <tr><td colSpan={4}>Nenhum agente cadastrado ainda.</td></tr>
                  ) : null}
                </tbody>
              </table>
            </div>

            <div className="panel">
              <div className="panelHeader">
                <h2>Filas</h2>
              </div>
              <div className="queueList">
                {queues.map((queue) => (
                  <div key={queue.id}>
                    <strong>{queue.name}</strong>
                    <span>{queue.extension || "sem ramal"}</span>
                  </div>
                ))}
                {queues.length === 0 ? <p>Nenhuma fila cadastrada ainda.</p> : null}
              </div>
            </div>
          </section>
        )}

        {activeView === "tenants" && (
          <section className="panel wide">
            <div className="panelHeader">
              <h2>Tenants cadastrados</h2>
              <button className="secondaryButton" onClick={importTenantsFromFusionPbx} type="button">
                <RefreshCw size={16} />
                Importar FusionPBX
              </button>
            </div>
            <table>
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>Dominio</th>
                  <th>FusionPBX domain_uuid</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {tenants.map((tenant) => (
                  <tr key={tenant.id}>
                    <td>{tenant.name}</td>
                    <td>{tenant.domain_name}</td>
                    <td>{tenant.fusionpbx_domain_uuid || "nao vinculado"}</td>
                    <td>{tenant.active ? "Ativo" : "Inativo"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}

        {activeView === "reports" && (
          <section className="panel">
            <div className="panelHeader">
              <h2>Resumo operacional</h2>
            </div>
            <div className="summaryGrid">
              <div><strong>{tenants.length}</strong><span>tenants</span></div>
              <div><strong>{queues.length}</strong><span>filas</span></div>
              <div><strong>{agents.length}</strong><span>agentes</span></div>
            </div>
          </section>
        )}

        {activeView === "settings" && (
          <section className="panel settingsPanel">
            <div className="panelHeader">
              <h2>Ambiente</h2>
            </div>
            <div className="settingsList">
              <div><strong>Perfil</strong><span>{session.role}</span></div>
              <div><strong>API</strong><span>/api</span></div>
              <div><strong>Realtime</strong><span>/api/realtime/ws</span></div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(<App />);

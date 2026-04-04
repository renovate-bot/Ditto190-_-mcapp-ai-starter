/**
 * A.D.A.M. Dashboard — Agentic Development and Agent Management
 *
 * A multi-tab MCP App UI covering:
 *   • Agent Factory  — register, list, and run agents
 *   • Skills Catalog — browse available MCP tools/skills
 *   • ETL Pipelines  — create and monitor data pipelines
 *   • Knowledge Base — ingest and search knowledge items
 */
import { useApp } from "@modelcontextprotocol/ext-apps/react";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import { StrictMode, useCallback, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import styles from "./mcp-app.module.css";

// ---------------------------------------------------------------------------
// Types mirroring the server-side interfaces
// ---------------------------------------------------------------------------

interface Agent {
  id: string;
  name: string;
  description: string;
  capabilities: string[];
  model: string;
  status: "idle" | "running" | "error";
  createdAt: string;
  lastRun?: string;
}

interface Skill {
  id: string;
  name: string;
  category: string;
  description: string;
}

interface Pipeline {
  id: string;
  name: string;
  source: string;
  transform: string;
  destination: string;
  status: "pending" | "running" | "completed" | "failed";
  createdAt: string;
  completedAt?: string;
  recordsProcessed?: number;
}

interface KnowledgeItem {
  id: string;
  title: string;
  content: string;
  type: "code" | "doc" | "schema" | "workflow";
  tags: string[];
  createdAt: string;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function extractText(result: CallToolResult): string {
  return result.content?.find((c) => c.type === "text")?.text ?? "";
}

function parseJson<T>(text: string): T | null {
  try {
    return JSON.parse(text) as T;
  } catch {
    return null;
  }
}

function StatusBadge({ status }: { status: string }) {
  const cls =
    status === "idle"
      ? styles.statusIdle
      : status === "running"
        ? styles.statusRunning
        : status === "completed"
          ? styles.statusCompleted
          : status === "failed"
            ? styles.statusFailed
            : status === "pending"
              ? styles.statusPending
              : styles.statusError;
  const dot =
    status === "running"
      ? "⏳"
      : status === "completed"
        ? "✅"
        : status === "failed"
          ? "❌"
          : status === "pending"
            ? "🕐"
            : status === "error"
              ? "⚠️"
              : "●";
  return (
    <span className={`${styles.status} ${cls}`}>
      {dot} {status}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Tab: Agent Factory
// ---------------------------------------------------------------------------

function AgentFactory({
  callTool,
}: {
  callTool: (
    name: string,
    args: Record<string, unknown>,
  ) => Promise<CallToolResult>;
}) {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(false);
  const [runResult, setRunResult] = useState<string>("");

  // Register form state
  const [regName, setRegName] = useState("");
  const [regDesc, setRegDesc] = useState("");
  const [regCaps, setRegCaps] = useState("");
  const [regModel, setRegModel] = useState("gpt-4o-mini");

  const loadAgents = useCallback(async () => {
    setLoading(true);
    try {
      const res = await callTool("list-agents", { filter: "all" });
      const data = parseJson<Agent[]>(extractText(res));
      if (data) setAgents(data);
    } finally {
      setLoading(false);
    }
  }, [callTool]);

  useEffect(() => {
    loadAgents().catch(console.error);
  }, [loadAgents]);

  const handleRegister = useCallback(async () => {
    if (!regName.trim()) return;
    const res = await callTool("register-agent", {
      name: regName,
      description: regDesc,
      capabilities: regCaps
        .split(",")
        .map((c) => c.trim())
        .filter(Boolean),
      model: regModel || undefined,
    });
    setRunResult(extractText(res));
    setRegName("");
    setRegDesc("");
    setRegCaps("");
    setRegModel("gpt-4o-mini");
    await loadAgents();
  }, [callTool, regName, regDesc, regCaps, regModel, loadAgents]);

  const handleRun = useCallback(
    async (agentId: string) => {
      const task = prompt(`Task for agent ${agentId}:`);
      if (!task) return;
      const res = await callTool("run-agent", { agentId, task });
      setRunResult(extractText(res));
      await loadAgents();
    },
    [callTool, loadAgents],
  );

  return (
    <div>
      <div className={styles.statsBar}>
        <div className={styles.stat}>
          <div className={styles.statValue}>{agents.length}</div>
          <div className={styles.statLabel}>Total Agents</div>
        </div>
        <div className={styles.stat}>
          <div className={styles.statValue}>
            {agents.filter((a) => a.status === "idle").length}
          </div>
          <div className={styles.statLabel}>Idle</div>
        </div>
        <div className={styles.stat}>
          <div className={styles.statValue}>
            {agents.filter((a) => a.status === "running").length}
          </div>
          <div className={styles.statLabel}>Running</div>
        </div>
      </div>

      <div
        style={{ display: "flex", gap: "var(--spacing-xl)", flexWrap: "wrap" }}
      >
        {/* Agent list */}
        <div style={{ flex: "1 1 320px" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "var(--spacing-md)",
            }}
          >
            <h2 className={styles.sectionTitle} style={{ margin: 0 }}>
              Registered Agents
            </h2>
            <button
              className={styles.btn}
              onClick={loadAgents}
              disabled={loading}
            >
              {loading ? "Loading…" : "↻ Refresh"}
            </button>
          </div>
          {agents.length === 0 ? (
            <div className={styles.empty}>No agents registered yet.</div>
          ) : (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "var(--spacing-sm)",
              }}
            >
              {agents.map((a) => (
                <div key={a.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <h3 className={styles.cardTitle}>{a.name}</h3>
                    <StatusBadge status={a.status} />
                  </div>
                  <p className={styles.cardDescription}>{a.description}</p>
                  <div className={styles.tags}>
                    {a.capabilities.map((c) => (
                      <span key={c} className={styles.tag}>
                        {c}
                      </span>
                    ))}
                  </div>
                  <div
                    style={{
                      display: "flex",
                      gap: "var(--spacing-xs)",
                      alignItems: "center",
                    }}
                  >
                    <span
                      style={{
                        fontSize: "0.75rem",
                        color: "light-dark(#6b7280, #9ca3af)",
                      }}
                    >
                      🤖 {a.model}
                    </span>
                    <button
                      className={`${styles.btn} ${styles.btnSm} ${styles.btnPrimary}`}
                      style={{ marginLeft: "auto" }}
                      onClick={() => handleRun(a.id)}
                    >
                      ▶ Run
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Register form */}
        <div style={{ flex: "0 0 300px" }}>
          <h2 className={styles.sectionTitle}>Register New Agent</h2>
          <div className={styles.form}>
            <div className={styles.formRow}>
              <label className={styles.label}>Name *</label>
              <input
                className={styles.input}
                value={regName}
                onChange={(e) => setRegName(e.target.value)}
                placeholder="Learning Agent"
              />
            </div>
            <div className={styles.formRow}>
              <label className={styles.label}>Description</label>
              <textarea
                className={styles.textarea}
                value={regDesc}
                onChange={(e) => setRegDesc(e.target.value)}
                placeholder="Absorbs and integrates external knowledge…"
              />
            </div>
            <div className={styles.formRow}>
              <label className={styles.label}>
                Capabilities (comma-separated)
              </label>
              <input
                className={styles.input}
                value={regCaps}
                onChange={(e) => setRegCaps(e.target.value)}
                placeholder="web-search, summarize, embed"
              />
            </div>
            <div className={styles.formRow}>
              <label className={styles.label}>Model</label>
              <select
                className={styles.select}
                value={regModel}
                onChange={(e) => setRegModel(e.target.value)}
              >
                <option value="gpt-4o-mini">gpt-4o-mini</option>
                <option value="gpt-4o">gpt-4o</option>
                <option value="claude-3-5-sonnet">claude-3-5-sonnet</option>
                <option value="claude-3-haiku">claude-3-haiku</option>
                <option value="gemini-2.0-flash">gemini-2.0-flash</option>
              </select>
            </div>
            <button
              className={`${styles.btn} ${styles.btnPrimary}`}
              onClick={handleRegister}
              disabled={!regName.trim()}
            >
              + Register Agent
            </button>
          </div>
          {runResult && <div className={styles.result}>{runResult}</div>}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Tab: Skills Catalog
// ---------------------------------------------------------------------------

function SkillsCatalog({
  callTool,
}: {
  callTool: (
    name: string,
    args: Record<string, unknown>,
  ) => Promise<CallToolResult>;
}) {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    callTool("list-skills", {})
      .then((res) => {
        const data = parseJson<Skill[]>(extractText(res));
        if (data) setSkills(data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [callTool]);

  const categories = [...new Set(skills.map((s) => s.category))];

  return (
    <div>
      <h2 className={styles.sectionTitle}>Skills Catalog</h2>
      {loading ? (
        <div className={styles.empty}>Loading skills…</div>
      ) : (
        categories.map((cat) => (
          <div key={cat} style={{ marginBottom: "var(--spacing-lg)" }}>
            <h3
              style={{
                margin: "0 0 var(--spacing-sm)",
                fontSize: "var(--font-heading-sm-size)",
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                color: "var(--color-text-info)",
              }}
            >
              {cat}
            </h3>
            <div className={styles.grid}>
              {skills
                .filter((s) => s.category === cat)
                .map((skill) => (
                  <div key={skill.id} className={styles.card}>
                    <h4
                      className={styles.cardTitle}
                      style={{
                        margin: "0 0 4px",
                        fontFamily: "var(--font-mono)",
                      }}
                    >
                      {skill.name}
                    </h4>
                    <p className={styles.cardDescription}>
                      {skill.description}
                    </p>
                    <span className={styles.tag}>{skill.category}</span>
                  </div>
                ))}
            </div>
          </div>
        ))
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Tab: ETL Pipelines
// ---------------------------------------------------------------------------

function Pipelines({
  callTool,
}: {
  callTool: (
    name: string,
    args: Record<string, unknown>,
  ) => Promise<CallToolResult>;
}) {
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState("");

  const [pipeName, setPipeName] = useState("");
  const [pipeSource, setPipeSource] = useState("");
  const [pipeTransform, setPipeTransform] = useState("");
  const [pipeDest, setPipeDest] = useState("");

  const loadPipelines = useCallback(async () => {
    setLoading(true);
    try {
      const res = await callTool("pipeline-status", {});
      const data = parseJson<Pipeline[]>(extractText(res));
      if (data) setPipelines(data);
    } finally {
      setLoading(false);
    }
  }, [callTool]);

  useEffect(() => {
    loadPipelines().catch(console.error);
  }, [loadPipelines]);

  const handleCreate = useCallback(async () => {
    if (!pipeName.trim()) return;
    const res = await callTool("create-pipeline", {
      name: pipeName,
      source: pipeSource,
      transform: pipeTransform,
      destination: pipeDest,
    });
    setResult(extractText(res));
    setPipeName("");
    setPipeSource("");
    setPipeTransform("");
    setPipeDest("");
    await loadPipelines();
  }, [callTool, pipeName, pipeSource, pipeTransform, pipeDest, loadPipelines]);

  return (
    <div>
      <div
        style={{ display: "flex", gap: "var(--spacing-xl)", flexWrap: "wrap" }}
      >
        <div style={{ flex: "1 1 320px" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "var(--spacing-md)",
            }}
          >
            <h2 className={styles.sectionTitle} style={{ margin: 0 }}>
              ETL Pipelines
            </h2>
            <button
              className={styles.btn}
              onClick={loadPipelines}
              disabled={loading}
            >
              {loading ? "Loading…" : "↻ Refresh"}
            </button>
          </div>
          {pipelines.length === 0 ? (
            <div className={styles.empty}>No pipelines defined yet.</div>
          ) : (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "var(--spacing-sm)",
              }}
            >
              {pipelines.map((p) => (
                <div key={p.id} className={styles.pipeline}>
                  <div className={styles.pipelineRow}>
                    <span className={styles.pipelineName}>{p.name}</span>
                    <StatusBadge status={p.status} />
                  </div>
                  <div className={styles.pipelineMeta}>
                    📥 {p.source} → 🔄 {p.transform} → 📤 {p.destination}
                  </div>
                  {p.recordsProcessed !== undefined && (
                    <div className={styles.pipelineMeta}>
                      {p.recordsProcessed} records processed
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <div style={{ flex: "0 0 300px" }}>
          <h2 className={styles.sectionTitle}>Create Pipeline</h2>
          <div className={styles.form}>
            <div className={styles.formRow}>
              <label className={styles.label}>Name *</label>
              <input
                className={styles.input}
                value={pipeName}
                onChange={(e) => setPipeName(e.target.value)}
                placeholder="GitHub → Knowledge Base"
              />
            </div>
            <div className={styles.formRow}>
              <label className={styles.label}>Source</label>
              <input
                className={styles.input}
                value={pipeSource}
                onChange={(e) => setPipeSource(e.target.value)}
                placeholder="github:owner/repo"
              />
            </div>
            <div className={styles.formRow}>
              <label className={styles.label}>Transform</label>
              <select
                className={styles.select}
                value={pipeTransform}
                onChange={(e) => setPipeTransform(e.target.value)}
              >
                <option value="">Select transform…</option>
                <option value="extract-code-patterns">
                  extract-code-patterns
                </option>
                <option value="mdx-to-zod-schema">mdx-to-zod-schema</option>
                <option value="to-composable-tools">to-composable-tools</option>
                <option value="summarize-and-embed">summarize-and-embed</option>
                <option value="code-to-mcp-tool">code-to-mcp-tool</option>
              </select>
            </div>
            <div className={styles.formRow}>
              <label className={styles.label}>Destination</label>
              <input
                className={styles.input}
                value={pipeDest}
                onChange={(e) => setPipeDest(e.target.value)}
                placeholder="knowledge-base"
              />
            </div>
            <button
              className={`${styles.btn} ${styles.btnPrimary}`}
              onClick={handleCreate}
              disabled={!pipeName.trim()}
            >
              + Create Pipeline
            </button>
          </div>
          {result && <div className={styles.result}>{result}</div>}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Tab: Knowledge Base
// ---------------------------------------------------------------------------

function KnowledgeBase({
  callTool,
}: {
  callTool: (
    name: string,
    args: Record<string, unknown>,
  ) => Promise<CallToolResult>;
}) {
  const [items, setItems] = useState<KnowledgeItem[]>([]);
  const [query, setQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [result, setResult] = useState("");

  const [kbTitle, setKbTitle] = useState("");
  const [kbContent, setKbContent] = useState("");
  const [kbType, setKbType] = useState<"code" | "doc" | "schema" | "workflow">(
    "doc",
  );
  const [kbTags, setKbTags] = useState("");

  const handleSearch = useCallback(async () => {
    if (!query.trim()) return;
    const res = await callTool("search-knowledge", { query, type: typeFilter });
    const data = parseJson<KnowledgeItem[]>(extractText(res));
    if (data) setItems(data);
    else setItems([]);
  }, [callTool, query, typeFilter]);

  const handleIngest = useCallback(async () => {
    if (!kbTitle.trim() || !kbContent.trim()) return;
    const res = await callTool("ingest-knowledge", {
      title: kbTitle,
      content: kbContent,
      type: kbType,
      tags: kbTags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean),
    });
    setResult(extractText(res));
    setKbTitle("");
    setKbContent("");
    setKbTags("");
  }, [callTool, kbTitle, kbContent, kbType, kbTags]);

  return (
    <div>
      <div
        style={{ display: "flex", gap: "var(--spacing-xl)", flexWrap: "wrap" }}
      >
        {/* Search */}
        <div style={{ flex: "1 1 320px" }}>
          <h2 className={styles.sectionTitle}>Search Knowledge</h2>
          <div
            style={{
              display: "flex",
              gap: "var(--spacing-xs)",
              marginBottom: "var(--spacing-md)",
              flexWrap: "wrap",
            }}
          >
            <input
              className={styles.input}
              style={{ flex: 1 }}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search title, content, or tags…"
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            />
            <select
              className={styles.select}
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
            >
              <option value="all">All types</option>
              <option value="code">Code</option>
              <option value="doc">Doc</option>
              <option value="schema">Schema</option>
              <option value="workflow">Workflow</option>
            </select>
            <button
              className={`${styles.btn} ${styles.btnPrimary}`}
              onClick={handleSearch}
              disabled={!query.trim()}
            >
              🔍 Search
            </button>
          </div>
          {items.length === 0 ? (
            <div className={styles.empty}>
              Enter a query above to search the knowledge base.
            </div>
          ) : (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "var(--spacing-sm)",
              }}
            >
              {items.map((item) => (
                <div key={item.id} className={styles.kbItem}>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "var(--spacing-xs)",
                    }}
                  >
                    <span
                      className={`${styles.kbTypeBadge} ${
                        item.type === "code"
                          ? styles.kbTypeCode
                          : item.type === "doc"
                            ? styles.kbTypeDoc
                            : item.type === "schema"
                              ? styles.kbTypeSchema
                              : styles.kbTypeWorkflow
                      }`}
                    >
                      {item.type}
                    </span>
                    <span className={styles.kbItemTitle}>{item.title}</span>
                  </div>
                  <p className={styles.kbItemContent}>{item.content}</p>
                  {item.tags.length > 0 && (
                    <div className={styles.tags}>
                      {item.tags.map((t) => (
                        <span key={t} className={styles.tag}>
                          {t}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Ingest */}
        <div style={{ flex: "0 0 300px" }}>
          <h2 className={styles.sectionTitle}>Ingest Knowledge</h2>
          <div className={styles.form}>
            <div className={styles.formRow}>
              <label className={styles.label}>Title *</label>
              <input
                className={styles.input}
                value={kbTitle}
                onChange={(e) => setKbTitle(e.target.value)}
                placeholder="ETL Pattern: API Polling"
              />
            </div>
            <div className={styles.formRow}>
              <label className={styles.label}>Content *</label>
              <textarea
                className={styles.textarea}
                value={kbContent}
                onChange={(e) => setKbContent(e.target.value)}
                placeholder="Describe the knowledge item…"
              />
            </div>
            <div className={styles.formRow}>
              <label className={styles.label}>Type</label>
              <select
                className={styles.select}
                value={kbType}
                onChange={(e) => setKbType(e.target.value as typeof kbType)}
              >
                <option value="doc">doc</option>
                <option value="code">code</option>
                <option value="schema">schema</option>
                <option value="workflow">workflow</option>
              </select>
            </div>
            <div className={styles.formRow}>
              <label className={styles.label}>Tags (comma-separated)</label>
              <input
                className={styles.input}
                value={kbTags}
                onChange={(e) => setKbTags(e.target.value)}
                placeholder="etl, api, polling"
              />
            </div>
            <button
              className={`${styles.btn} ${styles.btnPrimary}`}
              onClick={handleIngest}
              disabled={!kbTitle.trim() || !kbContent.trim()}
            >
              + Ingest
            </button>
          </div>
          {result && <div className={styles.result}>{result}</div>}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Root Dashboard
// ---------------------------------------------------------------------------

type TabId = "agents" | "skills" | "pipelines" | "knowledge";

const TABS: { id: TabId; label: string; icon: string }[] = [
  { id: "agents", label: "Agent Factory", icon: "🤖" },
  { id: "skills", label: "Skills Catalog", icon: "🛠️" },
  { id: "pipelines", label: "ETL Pipelines", icon: "🔄" },
  { id: "knowledge", label: "Knowledge Base", icon: "📚" },
];

function ADAMDashboard() {
  const [activeTab, setActiveTab] = useState<TabId>("agents");

  const { app, error } = useApp({
    appInfo: { name: "A.D.A.M. Dashboard", version: "1.0.0" },
    capabilities: {},
    onAppCreated: (app) => {
      app.onerror = console.error;
    },
  });

  const callTool = useCallback(
    async (
      name: string,
      args: Record<string, unknown>,
    ): Promise<CallToolResult> => {
      if (!app) throw new Error("App not connected");
      return app.callServerTool({ name, arguments: args });
    },
    [app],
  );

  if (error)
    return (
      <div style={{ padding: "1rem" }}>
        <strong>ERROR:</strong> {error.message}
      </div>
    );
  if (!app)
    return <div style={{ padding: "1rem" }}>Connecting to A.D.A.M.…</div>;

  return (
    <div className={styles.dashboard}>
      <header className={styles.header}>
        <div className={styles.headerIcon}>⚡</div>
        <div className={styles.headerText}>
          <h1>A.D.A.M.</h1>
          <p>
            Agentic Development and Agent Management · Dynamic Capabilities
            Framework
          </p>
        </div>
      </header>

      <nav className={styles.tabs}>
        {TABS.map(({ id, label, icon }) => (
          <button
            key={id}
            className={`${styles.tab} ${activeTab === id ? styles.tabActive : ""}`}
            onClick={() => setActiveTab(id)}
          >
            {icon} {label}
          </button>
        ))}
      </nav>

      <main className={styles.content}>
        {activeTab === "agents" && <AgentFactory callTool={callTool} />}
        {activeTab === "skills" && <SkillsCatalog callTool={callTool} />}
        {activeTab === "pipelines" && <Pipelines callTool={callTool} />}
        {activeTab === "knowledge" && <KnowledgeBase callTool={callTool} />}
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ADAMDashboard />
  </StrictMode>,
);

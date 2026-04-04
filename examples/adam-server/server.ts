import {
  registerAppResource,
  registerAppTool,
  RESOURCE_MIME_TYPE,
} from "@modelcontextprotocol/ext-apps/server";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type {
  CallToolResult,
  ReadResourceResult,
} from "@modelcontextprotocol/sdk/types.js";
import fs from "node:fs/promises";
import path from "node:path";
import { z } from "zod";

// Works both from source (server.ts) and compiled (dist/server.js)
const DIST_DIR = import.meta.filename.endsWith(".ts")
  ? path.join(import.meta.dirname, "dist")
  : import.meta.dirname;

// ---------------------------------------------------------------------------
// In-memory stores (replace with a real DB in production)
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

interface KnowledgeItem {
  id: string;
  title: string;
  content: string;
  type: "code" | "doc" | "schema" | "workflow";
  tags: string[];
  createdAt: string;
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

const agents: Agent[] = [
  {
    id: "agent-001",
    name: "Sensing Agent",
    description:
      "Identifies and assesses opportunities in the external environment using web scraping, API monitoring, and anomaly detection.",
    capabilities: [
      "web-scraping",
      "api-monitoring",
      "anomaly-detection",
      "trend-analysis",
    ],
    model: "gpt-4o-mini",
    status: "idle",
    createdAt: new Date(Date.now() - 86400000 * 3).toISOString(),
  },
  {
    id: "agent-002",
    name: "Seizing Agent",
    description:
      "Mobilizes resources to capture opportunities — orchestrates sub-agents, allocates compute, and schedules workflows.",
    capabilities: [
      "workflow-orchestration",
      "resource-allocation",
      "agent-spawning",
      "scheduling",
    ],
    model: "gpt-4o",
    status: "idle",
    createdAt: new Date(Date.now() - 86400000 * 2).toISOString(),
  },
  {
    id: "agent-003",
    name: "Transforming Agent",
    description:
      "Reconfigures and renews resources — converts code into composable tools, evolves schemas, and refactors pipelines.",
    capabilities: [
      "code-to-tool",
      "schema-evolution",
      "refactoring",
      "ci-cd-integration",
    ],
    model: "claude-3-5-sonnet",
    status: "idle",
    createdAt: new Date(Date.now() - 86400000).toISOString(),
  },
];

const knowledgeBase: KnowledgeItem[] = [
  {
    id: "kb-001",
    title: "Dynamic Capabilities Framework",
    content:
      "The DCF defines organizational capabilities across four dimensions: Sensing, Seizing, Transforming, and Integrative Learning.",
    type: "doc",
    tags: ["framework", "theory", "capabilities"],
    createdAt: new Date(Date.now() - 86400000 * 5).toISOString(),
  },
  {
    id: "kb-002",
    title: "MCP Tool Registration Pattern",
    content:
      "Use registerAppTool(server, name, schema, handler) to register a tool with UI metadata. The _meta.ui.resourceUri links the tool to its HTML resource.",
    type: "code",
    tags: ["mcp", "pattern", "tool"],
    createdAt: new Date(Date.now() - 86400000 * 2).toISOString(),
  },
];

const pipelines: Pipeline[] = [
  {
    id: "pipe-001",
    name: "GitHub → Knowledge Base",
    source: "github:Ditto190/mcapp-ai-starter",
    transform: "extract-code-patterns",
    destination: "knowledge-base",
    status: "completed",
    createdAt: new Date(Date.now() - 86400000 * 2).toISOString(),
    completedAt: new Date(Date.now() - 86400000).toISOString(),
    recordsProcessed: 42,
  },
  {
    id: "pipe-002",
    name: "MCP Spec → Zod Schemas",
    source: "specification/2026-01-26/apps.mdx",
    transform: "mdx-to-zod-schema",
    destination: "src/generated/",
    status: "completed",
    createdAt: new Date(Date.now() - 86400000).toISOString(),
    completedAt: new Date(Date.now() - 3600000).toISOString(),
    recordsProcessed: 18,
  },
];

let agentCounter = agents.length;
let kbCounter = knowledgeBase.length;
let pipeCounter = pipelines.length;

// ---------------------------------------------------------------------------
// Server factory
// ---------------------------------------------------------------------------

/**
 * Creates the A.D.A.M. MCP server with all tools and resources registered.
 */
export function createServer(): McpServer {
  const server = new McpServer({
    name: "A.D.A.M. — Agentic Development and Agent Management",
    version: "1.0.0",
  });

  const resourceUri = "ui://adam/mcp-app.html";

  // ------------------------------------------------------------------
  // Tool: list-agents
  // ------------------------------------------------------------------
  registerAppTool(
    server,
    "list-agents",
    {
      title: "List Agents",
      description:
        "Returns all registered agents and their current status in the A.D.A.M. factory.",
      inputSchema: {
        filter: z
          .enum(["active", "idle", "all"])
          .optional()
          .describe("Filter agents by status. Defaults to 'all'."),
      },
      _meta: { ui: { resourceUri } },
    },
    async (input): Promise<CallToolResult> => {
      const filter = (input.filter as string | undefined) ?? "all";
      const filtered =
        filter === "all" ? agents : agents.filter((a) => a.status === filter);
      return {
        content: [{ type: "text", text: JSON.stringify(filtered, null, 2) }],
      };
    },
  );

  // ------------------------------------------------------------------
  // Tool: register-agent
  // ------------------------------------------------------------------
  registerAppTool(
    server,
    "register-agent",
    {
      title: "Register Agent",
      description:
        "Registers a new agent in the A.D.A.M. factory with its name, description, capabilities, and preferred model.",
      inputSchema: {
        name: z.string().describe("Human-readable agent name."),
        description: z.string().describe("What the agent does."),
        capabilities: z
          .array(z.string())
          .describe(
            "List of capability tags (e.g. 'web-scraping', 'code-gen').",
          ),
        model: z
          .string()
          .optional()
          .describe("Preferred LLM model (default: gpt-4o-mini)."),
      },
      _meta: { ui: { resourceUri } },
    },
    async (input): Promise<CallToolResult> => {
      agentCounter += 1;
      const agent: Agent = {
        id: `agent-${String(agentCounter).padStart(3, "0")}`,
        name: input.name as string,
        description: input.description as string,
        capabilities: input.capabilities as string[],
        model: (input.model as string | undefined) ?? "gpt-4o-mini",
        status: "idle",
        createdAt: new Date().toISOString(),
      };
      agents.push(agent);
      return {
        content: [
          {
            type: "text",
            text: `Agent '${agent.name}' registered with ID ${agent.id}.\n\n${JSON.stringify(agent, null, 2)}`,
          },
        ],
      };
    },
  );

  // ------------------------------------------------------------------
  // Tool: run-agent
  // ------------------------------------------------------------------
  registerAppTool(
    server,
    "run-agent",
    {
      title: "Run Agent",
      description:
        "Executes an agent by ID with the given task description. Returns a simulated execution trace.",
      inputSchema: {
        agentId: z
          .string()
          .describe("ID of the agent to run (e.g. 'agent-001')."),
        task: z
          .string()
          .describe("Natural language task description for the agent."),
      },
      _meta: { ui: { resourceUri } },
    },
    async (input): Promise<CallToolResult> => {
      const agent = agents.find((a) => a.id === input.agentId);
      if (!agent) {
        return {
          content: [
            { type: "text", text: `Agent '${input.agentId}' not found.` },
          ],
          isError: true,
        };
      }
      agent.status = "running";
      agent.lastRun = new Date().toISOString();

      // Simulate async execution
      await new Promise((r) => setTimeout(r, 100));
      agent.status = "idle";

      const trace = {
        agentId: agent.id,
        agentName: agent.name,
        task: input.task,
        startedAt: agent.lastRun,
        completedAt: new Date().toISOString(),
        steps: [
          { step: 1, action: "Parse task", result: "Task parsed successfully" },
          {
            step: 2,
            action: "Select capabilities",
            result: agent.capabilities.slice(0, 2).join(", "),
          },
          { step: 3, action: "Execute", result: `Completed: ${input.task}` },
        ],
        status: "completed",
      };

      return {
        content: [{ type: "text", text: JSON.stringify(trace, null, 2) }],
      };
    },
  );

  // ------------------------------------------------------------------
  // Tool: list-skills
  // ------------------------------------------------------------------
  registerAppTool(
    server,
    "list-skills",
    {
      title: "List Skills",
      description:
        "Lists all available tools and skills in the A.D.A.M. skill catalog.",
      inputSchema: {
        category: z
          .string()
          .optional()
          .describe(
            "Optional category filter (e.g. 'sensing', 'seizing', 'transforming', 'learning').",
          ),
      },
      _meta: { ui: { resourceUri } },
    },
    async (): Promise<CallToolResult> => {
      const catalog = [
        {
          id: "skill-001",
          name: "list-agents",
          category: "factory",
          description: "List all registered agents",
        },
        {
          id: "skill-002",
          name: "register-agent",
          category: "factory",
          description: "Register a new agent",
        },
        {
          id: "skill-003",
          name: "run-agent",
          category: "factory",
          description: "Execute an agent",
        },
        {
          id: "skill-004",
          name: "list-skills",
          category: "catalog",
          description: "Browse skill catalog",
        },
        {
          id: "skill-005",
          name: "ingest-knowledge",
          category: "learning",
          description: "Ingest a knowledge item",
        },
        {
          id: "skill-006",
          name: "search-knowledge",
          category: "learning",
          description: "Search knowledge base",
        },
        {
          id: "skill-007",
          name: "create-pipeline",
          category: "transforming",
          description: "Define an ETL pipeline",
        },
        {
          id: "skill-008",
          name: "pipeline-status",
          category: "transforming",
          description: "Get pipeline status",
        },
      ];
      return {
        content: [{ type: "text", text: JSON.stringify(catalog, null, 2) }],
      };
    },
  );

  // ------------------------------------------------------------------
  // Tool: ingest-knowledge
  // ------------------------------------------------------------------
  registerAppTool(
    server,
    "ingest-knowledge",
    {
      title: "Ingest Knowledge",
      description:
        "Ingests a knowledge item (code, doc, schema, or workflow) into the A.D.A.M. knowledge base.",
      inputSchema: {
        title: z.string().describe("Title of the knowledge item."),
        content: z.string().describe("The content to store."),
        type: z
          .enum(["code", "doc", "schema", "workflow"])
          .describe("Type of knowledge item."),
        tags: z
          .array(z.string())
          .optional()
          .describe("Optional list of tags for categorization."),
      },
      _meta: { ui: { resourceUri } },
    },
    async (input): Promise<CallToolResult> => {
      kbCounter += 1;
      const item: KnowledgeItem = {
        id: `kb-${String(kbCounter).padStart(3, "0")}`,
        title: input.title as string,
        content: input.content as string,
        type: input.type as KnowledgeItem["type"],
        tags: (input.tags as string[] | undefined) ?? [],
        createdAt: new Date().toISOString(),
      };
      knowledgeBase.push(item);
      return {
        content: [
          {
            type: "text",
            text: `Knowledge item '${item.title}' ingested with ID ${item.id}.`,
          },
        ],
      };
    },
  );

  // ------------------------------------------------------------------
  // Tool: search-knowledge
  // ------------------------------------------------------------------
  registerAppTool(
    server,
    "search-knowledge",
    {
      title: "Search Knowledge",
      description:
        "Searches the knowledge base for items matching the query (title, content, or tags).",
      inputSchema: {
        query: z.string().describe("Search query string."),
        type: z
          .enum(["code", "doc", "schema", "workflow", "all"])
          .optional()
          .describe("Filter by knowledge type. Defaults to 'all'."),
      },
      _meta: { ui: { resourceUri } },
    },
    async (input): Promise<CallToolResult> => {
      const q = (input.query as string).toLowerCase();
      const typeFilter = (input.type as string | undefined) ?? "all";
      const results = knowledgeBase.filter((item) => {
        const matchesType = typeFilter === "all" || item.type === typeFilter;
        const matchesQuery =
          item.title.toLowerCase().includes(q) ||
          item.content.toLowerCase().includes(q) ||
          item.tags.some((t) => t.toLowerCase().includes(q));
        return matchesType && matchesQuery;
      });
      return {
        content: [
          {
            type: "text",
            text:
              results.length > 0
                ? JSON.stringify(results, null, 2)
                : `No results found for query '${input.query}'.`,
          },
        ],
      };
    },
  );

  // ------------------------------------------------------------------
  // Tool: create-pipeline
  // ------------------------------------------------------------------
  registerAppTool(
    server,
    "create-pipeline",
    {
      title: "Create Pipeline",
      description: "Defines a new ETL data pipeline in the A.D.A.M. platform.",
      inputSchema: {
        name: z.string().describe("Human-readable pipeline name."),
        source: z
          .string()
          .describe(
            "Data source URI or identifier (e.g. 'github:owner/repo', 'file:data.csv').",
          ),
        transform: z
          .string()
          .describe(
            "Transformation to apply (e.g. 'extract-code-patterns', 'to-zod-schema').",
          ),
        destination: z
          .string()
          .describe(
            "Destination for transformed data (e.g. 'knowledge-base', 'src/generated/').",
          ),
      },
      _meta: { ui: { resourceUri } },
    },
    async (input): Promise<CallToolResult> => {
      pipeCounter += 1;
      const pipeline: Pipeline = {
        id: `pipe-${String(pipeCounter).padStart(3, "0")}`,
        name: input.name as string,
        source: input.source as string,
        transform: input.transform as string,
        destination: input.destination as string,
        status: "pending",
        createdAt: new Date().toISOString(),
      };
      pipelines.push(pipeline);

      // Simulate pipeline start
      setTimeout(() => {
        pipeline.status = "running";
        setTimeout(() => {
          pipeline.status = "completed";
          pipeline.completedAt = new Date().toISOString();
          pipeline.recordsProcessed = Math.floor(Math.random() * 100) + 1;
        }, 2000);
      }, 500);

      return {
        content: [
          {
            type: "text",
            text: `Pipeline '${pipeline.name}' created with ID ${pipeline.id}. Status: pending.\n\n${JSON.stringify(pipeline, null, 2)}`,
          },
        ],
      };
    },
  );

  // ------------------------------------------------------------------
  // Tool: pipeline-status
  // ------------------------------------------------------------------
  registerAppTool(
    server,
    "pipeline-status",
    {
      title: "Pipeline Status",
      description:
        "Gets the status of all ETL pipelines, or a specific pipeline by ID.",
      inputSchema: {
        pipelineId: z
          .string()
          .optional()
          .describe("Optional pipeline ID. If omitted, returns all pipelines."),
      },
      _meta: { ui: { resourceUri } },
    },
    async (input): Promise<CallToolResult> => {
      if (input.pipelineId) {
        const pipeline = pipelines.find((p) => p.id === input.pipelineId);
        if (!pipeline) {
          return {
            content: [
              {
                type: "text",
                text: `Pipeline '${input.pipelineId}' not found.`,
              },
            ],
            isError: true,
          };
        }
        return {
          content: [{ type: "text", text: JSON.stringify(pipeline, null, 2) }],
        };
      }
      return {
        content: [{ type: "text", text: JSON.stringify(pipelines, null, 2) }],
      };
    },
  );

  // ------------------------------------------------------------------
  // Resource: serves the bundled React UI
  // ------------------------------------------------------------------
  registerAppResource(
    server,
    resourceUri,
    resourceUri,
    { mimeType: RESOURCE_MIME_TYPE },
    async (): Promise<ReadResourceResult> => {
      const html = await fs.readFile(
        path.join(DIST_DIR, "mcp-app.html"),
        "utf-8",
      );
      return {
        contents: [
          { uri: resourceUri, mimeType: RESOURCE_MIME_TYPE, text: html },
        ],
      };
    },
  );

  return server;
}

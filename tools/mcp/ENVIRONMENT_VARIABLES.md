# Environment Variables

Complete reference for MCP Gateway environment variables.

## Required for Production (Containerized Mode)

When running in a container (`run_containerized.sh`), these variables **must** be set:

| Variable | Description | Example |
|----------|-------------|---------|
| `MCP_GATEWAY_PORT` | The port the gateway listens on (used for `--listen` address) | `8080` |
| `MCP_GATEWAY_DOMAIN` | The domain name for the gateway | `localhost` |
| `MCP_GATEWAY_API_KEY` | API key checked by `run_containerized.sh` as a deployment gate; must be referenced in your JSON config via `"${MCP_GATEWAY_API_KEY}"` to enable authentication | `your-secret-key` |

## Optional (Non-Containerized Mode)

When running locally (`run.sh`), these variables are optional (warnings shown if missing):

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_GATEWAY_PORT` | Gateway listening port | `8000` |
| `MCP_GATEWAY_DOMAIN` | Gateway domain | `localhost` |
| `MCP_GATEWAY_API_KEY` | Informational only — not read directly by the binary; must be referenced in your config via `"${MCP_GATEWAY_API_KEY}"` to enable authentication | (disabled) |
| `MCP_GATEWAY_LOG_DIR` | Log file directory (sets default for `--log-dir` flag) | `/tmp/gh-aw/mcp-logs` |
| `MCP_GATEWAY_PAYLOAD_DIR` | Large payload storage directory (sets default for `--payload-dir` flag) | `/tmp/jq-payloads` |
| `MCP_GATEWAY_PAYLOAD_PATH_PREFIX` | Path prefix for remapping payloadPath returned to clients (sets default for `--payload-path-prefix` flag) | (empty - use actual filesystem path) |
| `MCP_GATEWAY_PAYLOAD_SIZE_THRESHOLD` | Size threshold in bytes for payload storage (sets default for `--payload-size-threshold` flag) | `524288` |
| `MCP_GATEWAY_WASM_GUARDS_DIR` | Root directory for per-server WASM guards (`<root>/<serverID>/*.wasm`, first match is loaded) | (disabled) |
| `MCP_GATEWAY_GUARDS_MODE` | Guards enforcement mode: `strict` (deny violations), `filter` (remove denied tools), `propagate` (auto-adjust agent labels) (sets default for `--guards-mode`) | `strict` |
| `MCP_GATEWAY_GUARDS_SINK_SERVER_IDS` | Comma-separated sink server IDs for JSONL guards tag enrichment (sets default for `--guards-sink-server-ids`) | (disabled) |
| `DEBUG` | Enable debug logging with pattern matching (e.g., `*`, `server:*,launcher:*`) | (disabled) |
| `DEBUG_COLORS` | Control colored debug output (0 to disable, auto-disabled when piping) | Auto-detect |
| `RUNNING_IN_CONTAINER` | Manual override; set to `"true"` to force container detection when `/.dockerenv` and cgroup detection are unavailable | (unset) |

**Note:** `PORT`, `HOST`, and `MODE` are not read by the `awmg` binary directly. However, `run.sh` uses `HOST` (default: `0.0.0.0`), `MODE` (default: `--routed`), and falls back to `PORT` (when `MCP_GATEWAY_PORT` is unset) to set the bind address and routing mode. Use the `--listen` and `--routed`/`--unified` flags when running `awmg` directly.

## Containerized Deployment Variables

When using `run_containerized.sh`, these additional variables are available:

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_GATEWAY_HOST` | Bind address for the gateway | `0.0.0.0` |
| `MCP_GATEWAY_MODE` | Routing mode flag passed to `awmg` (e.g., `--routed`, `--unified`) | `--routed` |

## Docker Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `DOCKER_HOST` | Docker daemon socket path | `/var/run/docker.sock` |
| `DOCKER_API_VERSION` | Docker API version (set by helper scripts, Docker client auto-negotiates) | Set by querying Docker daemon's current API version; falls back to `1.44` if detection fails |

## Proxy Mode Variables

When running `awmg proxy`, these variables configure the upstream GitHub API:

| Variable | Description | Default |
|----------|-------------|---------|
| `GITHUB_API_URL` | Explicit GitHub API endpoint (e.g., `https://copilot-api.mycompany.ghe.com`); used by proxy to set upstream target | (auto-derived) |
| `GITHUB_SERVER_URL` | GitHub server URL; proxy auto-derives API endpoint: `*.ghe.com` → `copilot-api.*.ghe.com`, GHES → `<host>/api/v3`, `github.com` → `api.github.com` | (falls back to `api.github.com`) |
| `GH_TOKEN` / `GITHUB_TOKEN` / `GITHUB_PERSONAL_ACCESS_TOKEN` | GitHub auth token for the proxy to forward requests (checked in priority order) | (required for upstream auth) |

## GitHub Actions OIDC Variables

When any HTTP server uses `auth.type = "github-oidc"`, the gateway reads these environment variables (set automatically by the GitHub Actions runner when `permissions: { id-token: write }` is granted):

| Variable | Description | Default |
|----------|-------------|---------|
| `ACTIONS_ID_TOKEN_REQUEST_URL` | GitHub Actions OIDC token endpoint. Required when any HTTP server uses `auth.type = "github-oidc"`. | (set by GitHub Actions) |
| `ACTIONS_ID_TOKEN_REQUEST_TOKEN` | Bearer token used to authenticate the OIDC token request. Used alongside `ACTIONS_ID_TOKEN_REQUEST_URL`. | (set by GitHub Actions) |

## DIFC / Guard Policy Configuration

These environment variables configure guard policies (e.g., AllowOnly policies for restricting tool access to specific GitHub repositories):

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_GATEWAY_GUARD_POLICY_JSON` | Guard policy JSON (e.g., `{"allow-only":{"repos":"public","min-integrity":"none"}}`) (sets default for `--guard-policy-json`) | (disabled) |
| `MCP_GATEWAY_ALLOWONLY_SCOPE_PUBLIC` | Use public AllowOnly scope (sets default for `--allowonly-scope-public`) | `false` |
| `MCP_GATEWAY_ALLOWONLY_SCOPE_OWNER` | AllowOnly owner scope value (sets default for `--allowonly-scope-owner`) | (disabled) |
| `MCP_GATEWAY_ALLOWONLY_SCOPE_REPO` | AllowOnly repo name (requires owner) (sets default for `--allowonly-scope-repo`) | (disabled) |
| `MCP_GATEWAY_ALLOWONLY_MIN_INTEGRITY` | AllowOnly integrity level: `none`, `unapproved`, `approved`, `merged` (sets default for `--allowonly-min-integrity`) | (disabled) |

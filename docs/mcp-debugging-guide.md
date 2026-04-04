# MCP Server Configuration Debugging Guide

## Overview
This guide documents common MCP server configuration issues and their solutions, based on real debugging sessions.

## Issue #1: SIGHUP Signal Causing Immediate Shutdown

### Symptoms
- MCP server starts successfully (logs show "Server startup completed")
- Server immediately shuts down with "Shutdown initiated by: SIGHUP"
- Server never becomes available to clients

### Root Cause
When using `bash -lc` or `bash -c` as the command wrapper, bash spawns the server process as a child, then exits. When bash exits, it sends SIGHUP (hangup signal) to all child processes, causing them to terminate.

### Example of Broken Configuration
```json
{
  "servers": {
    "n8n-mcp": {
      "type": "stdio",
      "command": "bash",
      "args": [
        "-lc",
        "if [ -f \"${workspaceFolder}/node_modules/n8n-mcp/dist/mcp/index.js\" ]; then node \"${workspaceFolder}/node_modules/n8n-mcp/dist/mcp/index.js\"; else npx n8n-mcp; fi"
      ]
    }
  }
}
```

### Why This Fails
1. Bash executes the conditional command
2. The command spawns `npx n8n-mcp` or `node ...` as a subprocess
3. Bash considers the command "complete" after spawning
4. Bash exits (exit code 0)
5. On exit, bash sends SIGHUP to all child processes
6. n8n-mcp receives SIGHUP and shuts down gracefully

### Solution 1: Use Direct Command (Recommended)
Remove bash wrapper entirely and use the command directly:

```json
{
  "servers": {
    "n8n-mcp": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "n8n-mcp"
      ],
      "envFile": "${workspaceFolder}/.env",
      "env": {
        "MCP_MODE": "stdio",
        "N8N_MODE": "true",
        "LOG_LEVEL": "info"
      }
    }
  }
}
```

### Solution 2: Use `exec` to Replace Bash Process
If you must use bash (e.g., for complex setup), use `exec` to replace the bash process:

```json
{
  "servers": {
    "my-server": {
      "type": "stdio",
      "command": "bash",
      "args": [
        "-c",
        "cd /path/to/server && exec npx my-mcp-server"
      ]
    }
  }
}
```

The `exec` keyword replaces the bash process with the server process, so there's no parent bash to send SIGHUP.

### Solution 3: Keep Bash Alive
If you need bash to remain (e.g., for cleanup), ensure the command runs in foreground:

```json
{
  "servers": {
    "my-server": {
      "type": "stdio",
      "command": "bash",
      "args": [
        "-c",
        "cd /path/to/server && uv run python server.py"
      ]
    }
  }
}
```

The `uv run python server.py` keeps bash alive as the python process runs in foreground.

## Issue #2: Complex Bash Commands Without Error Handling

### Symptoms
- Server fails silently
- No clear error messages
- Client reports "server not available"

### Root Cause
Complex bash commands (cloning repos, building projects) can fail at any step, but without proper error handling, the failure is silent.

### Example of Broken Configuration
```json
{
  "servers": {
    "awesome-copilot": {
      "type": "stdio",
      "command": "bash",
      "args": [
        "-lc",
        "if [ ! -d /workspaces/mcp-dotnet-samples ]; then git clone https://github.com/microsoft/mcp-dotnet-samples /workspaces/mcp-dotnet-samples; fi && dotnet run --project /workspaces/mcp-dotnet-samples/awesome-copilot/src/McpSamples.AwesomeCopilot.HybridApp --no-launch-profile"
      ]
    }
  }
}
```

### Problems
1. Uses `-lc` (login shell) which can cause SIGHUP issue
2. No `set -e` to exit on errors
3. No error messages if git clone fails
4. No error messages if dotnet run fails
5. No `exec` to replace bash process

### Solution: Add Proper Error Handling
```json
{
  "servers": {
    "awesome-copilot": {
      "type": "stdio",
      "command": "bash",
      "args": [
        "-c",
        "set -e; if [ ! -d /workspaces/mcp-dotnet-samples ]; then echo 'Cloning mcp-dotnet-samples...'; git clone --depth 1 https://github.com/microsoft/mcp-dotnet-samples /workspaces/mcp-dotnet-samples || exit 1; fi; cd /workspaces/mcp-dotnet-samples/awesome-copilot/src/McpSamples.AwesomeCopilot.HybridApp && exec dotnet run --no-launch-profile"
      ],
      "env": {
        "DOTNET_CLI_TELEMETRY_OPTOUT": "1"
      }
    }
  }
}
```

### Improvements
1. Changed `-lc` to `-c` (non-login shell, faster)
2. Added `set -e` to exit on any command failure
3. Added `echo` to provide feedback during setup
4. Added `|| exit 1` to explicit error handling
5. Used `git clone --depth 1` for faster clone
6. Added `exec` to replace bash with dotnet process
7. Added `cd` before `exec dotnet run` to ensure correct working directory
8. Added environment variable to disable telemetry

## Debugging Best Practices

### 1. Check Logs
For n8n-mcp, logs are typically in `/tmp/n8n-mcp.log` (if using nohup or redirected stderr).

Look for:
- "Server startup completed" = server initialized correctly
- "Shutdown initiated by: SIGHUP" = parent process terminated
- Error messages about missing dependencies, ports, etc.

### 2. Test Commands Manually
Before putting commands in MCP config, test them in a terminal:

```bash
# Test if npx command works
npx n8n-mcp

# Test if path exists
ls -la "${workspaceFolder}/node_modules/n8n-mcp/dist/mcp/index.js"

# Test bash script logic
bash -c "set -e; echo 'Testing...'; exit 1"  # Should fail
```

### 3. Simplify First
Start with the simplest possible configuration:

```json
{
  "servers": {
    "my-server": {
      "type": "stdio",
      "command": "npx",
      "args": ["my-mcp-server"]
    }
  }
}
```

Then add complexity (environment variables, bash wrappers, etc.) only as needed.

### 4. Use Appropriate Shell Flags
- `-c` = Execute command string (most common)
- `-lc` = Login shell + execute command (slower, may have different PATH)
- `set -e` = Exit on any command failure (critical for error handling)
- `set -x` = Print commands as they execute (useful for debugging)

### 5. Environment Variables
- Use `envFile` for loading .env files
- Use `env` object for specific overrides
- Ensure PATH includes necessary directories
- Consider PYTHONPATH, NODE_PATH, etc. for language-specific tools

### 6. Validate JSON Syntax
VS Code will show errors for invalid JSON, but watch for:
- Unescaped quotes in command strings
- Missing commas between properties
- Trailing commas (not allowed in strict JSON)

## Common Patterns

### Pattern 1: Direct NPX Command (Simplest)
```json
{
  "type": "stdio",
  "command": "npx",
  "args": ["my-server"]
}
```

### Pattern 2: Python with UV (Recommended for Python servers)
```json
{
  "type": "stdio",
  "command": "bash",
  "args": ["-c", "cd /path/to/server && uv run python server.py"],
  "env": {
    "PYTHONPATH": "/path/to/project"
  }
}
```

### Pattern 3: Docker Container
```json
{
  "type": "stdio",
  "command": "docker",
  "args": [
    "run",
    "-i",
    "--rm",
    "-e", "ENV_VAR=value",
    "my-mcp-image:latest"
  ]
}
```

### Pattern 4: Node.js Project
```json
{
  "type": "stdio",
  "command": "node",
  "args": ["/path/to/server/index.js"]
}
```

## Testing Checklist

After configuring an MCP server, verify:

- [ ] Server starts without errors
- [ ] Server stays running (doesn't immediately exit)
- [ ] No SIGHUP or SIGTERM signals in logs
- [ ] Client can connect and list tools
- [ ] Tools can be invoked successfully
- [ ] Error messages are clear and actionable
- [ ] Configuration survives VS Code restart
- [ ] Environment variables are loaded correctly

## Additional Resources

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [VS Code MCP Integration](https://code.visualstudio.com/docs/copilot/mcp)
- [Bash Signal Handling](https://www.gnu.org/software/bash/manual/html_node/Signals.html)
- [Process Management in Linux](https://www.kernel.org/doc/html/latest/admin-guide/process-lifecycle.html)

## Summary

The key takeaways:

1. **Avoid bash wrappers** unless absolutely necessary
2. **Use `exec`** if you must use bash
3. **Add error handling** (`set -e`, `|| exit 1`)
4. **Test commands manually** before adding to config
5. **Check logs** for SIGHUP and other termination signals
6. **Start simple**, add complexity incrementally

These patterns apply to all MCP server configurations across VS Code, Claude Desktop, Cline, and other MCP clients.

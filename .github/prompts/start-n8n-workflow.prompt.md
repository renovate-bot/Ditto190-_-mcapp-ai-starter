---
name: start-n8n-workflow
description: "Help start the n8n demo stack, verify n8n is reachable, and run or create a workflow via API."
argument-hint: Provide optional workflow name or path to workflow JSON
agent: agent
---

Steps:

1. Show the docker compose command to start the stack and the health-check to confirm n8n is running.
2. If given a workflow JSON or name, show the API request (HTTP method, URL, headers) to create the workflow using `N8N_HOST` and `N8N_API_KEY` environment variables.
3. Provide the curl command to execute the workflow once created and how to poll for execution results.
4. If n8n is not reachable, list 3 probable causes and quick fixes (container not running, wrong `N8N_HOST`, `N8N_API_KEY` missing).

Return only the exact commands and minimal explanatory text. Do not print secrets; use placeholders like `<N8N_API_KEY>`.

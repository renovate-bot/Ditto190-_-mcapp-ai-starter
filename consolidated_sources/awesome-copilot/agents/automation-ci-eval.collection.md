---
collection: "automation-ci-eval"
title: "Automation, CI/CD & Evaluation Agents Collection"
description: "A loadable collection of software agents and code repair agents specialized in automation, CI/CD workflow design, and repository evaluation pipelines. Use this collection to bootstrap agentic workflows that analyze repos, propose CI/CD changes, and implement evaluation harnesses."
version: 1.0.0
agents:
  - path: "awesome-copilot/agents/create-agentsmd.agent.md"
    name: "AgentsMd Creator"
    role: "Repository analysis & AGENTS.md generator"
  - path: "awesome-copilot/agents/ci-cd-evaluator.agent.md"
    name: "CI/CD & Evaluation Architect"
    role: "CI/CD pipeline design, automation, and repair"
---

## Overview

This collection groups two complementary agent personas:

- AgentsMd Creator — analyzes a repository to extract architecture, conventions, and generates an AGENTS.md or AGENTSpec that documents recommended workflows and automation.
- CI/CD & Evaluation Architect — proposes, repairs, and implements CI/CD workflows and evaluation pipelines (tests, benchmarks, release gates) and can generate PR-ready changes.

## How to use

1. Load this collection into your agent runner (or MCP server) using the host's collection loader.
2. Invoke the AgentsMd Creator to produce a repo overview and list of recommended automation changes.
3. Invoke the CI/CD & Evaluation Architect to produce pipeline definitions (GitHub Actions / n8n / GitLab CI), tests, and a PR with applied fixes.

## Security & constraints

- Agents must never leak secrets; when making changes that require credentials, surface instructions and placeholders rather than embedding keys.
- When creating or pushing changes, prefer creating draft PRs and include a clear changelog entry.

## Examples

Quick load example:

- load_collection: automation-ci-eval

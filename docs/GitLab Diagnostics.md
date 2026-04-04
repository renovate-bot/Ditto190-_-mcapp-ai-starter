# GitLab Diagnostics

## Versions

- IDE: Visual Studio Code (1.114.0)
- Extension: GitLab version (6.72.0)
- Language Server version: 8.79.0
- GitLab instance version: 18.11.0-pre

## GitLab Duo Code Suggestions (On)

- [x] User is authenticated (true)
- [x] Code Suggestions is enabled in settings (true)
- [x] Code Suggestions API connection is working (true)
- [x] The GitLab instance version supports Code Suggestions (true)
- [x] Valid GitLab license (true)
- [x] User has enough credits to continue Code Suggestions usage for this billing period (true)
- [x] GitLab Duo is enabled for the open project(s) (true)
- [x] Current file is not excluded by project exclusion rules (true)

## GitLab Duo Non-Agentic Chat (On)

- [x] User is authenticated (true)
- [x] Non-Agentic Chat is enabled in settings (true)
- [x] Valid GitLab license (true)
- [x] GitLab Duo is enabled for the open project(s) (true)

## Terminal Context (On)

- [x] User is authenticated (true)
- [x] Non-Agentic Chat is enabled in settings (true)
- [x] Valid GitLab license (true)
- [x] GitLab Duo is enabled for the open project(s) (true)
- [x] Include terminal context is enabled for user (true)

## GitLab Duo Agentic Chat (On)

- [x] User is authenticated (true)
- [x] Agentic Chat feature flag is enabled on the GitLab instance (true)
- [x] Agentic Chat is supported for the current project (true)
- [x] Agent Platform is enabled in settings (true)

## GitLab Flows (On)

- [x] User is authenticated (true)
- [x] Flows feature flag is enabled on the GitLab instance (true)
- [x] Agent Platform is enabled in settings (true)

## GitLab Duo Agent Platform settings

### Feature flags

- [x] flowBuilder (enabled)

### JSON Settings

These are modified settings combined from your global `settings.json` and project-specific `settings.json`:

```json
{
  "gitlab.duoCodeSuggestions.additionalLanguages": [
    "markdown"
  ],
  "gitlab.duoAgentPlatform.defaultNamespace": "Modifyme_glabs",
  "gitlab.debug": true,
  "gitlab.real-timeSecurityScan.enabled": true,
  "gitlab.featureFlags.flowBuilder": true
}
```

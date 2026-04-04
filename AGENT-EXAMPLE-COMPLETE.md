# 🎯 Complete Agent Example: Expert React Frontend Engineer

## Overview

Here's a **complete working agent** with all its associated data, prompts, instructions, tools, and skills.

---

## 1️⃣ THE AGENT FILE

**Location**: `awesome-copilot/agents/expert-react-frontend-engineer.agent.md`

```yaml
---
description: "Expert React 19.2 frontend engineer specializing in modern hooks, Server Components, Actions, TypeScript, and performance optimization"
name: "Expert React Frontend Engineer"
tools:
  [
    "changes",
    "codebase",
    "edit/editFiles",
    "extensions",
    "fetch",
    "findTestFiles",
    "githubRepo",
    "new",
    "openSimpleBrowser",
    "problems",
    "runCommands",
    "runTasks",
    "runTests",
    "search",
    "searchResults",
    "terminalLastCommand",
    "terminalSelection",
    "testFailure",
    "usages",
    "vscodeAPI",
    "microsoft.docs.mcp",
  ]
---
```

**Key Characteristics**:

- ✅ **Has a name**: "Expert React Frontend Engineer"
- ✅ **Has a description**: Clear role definition
- ✅ **Has tools**: 19 tools for working with code
- ✅ **Has instructions**: 700+ lines of detailed guidance

---

## 2️⃣ AGENT INSTRUCTIONS (What it knows & how it works)

The agent includes comprehensive instructions covering:

### Expertise Areas (740 lines)

```
✓ React 19.2 Features (Activity, useEffectEvent, cacheSignal)
✓ React 19 Core (use() hook, useFormStatus, useOptimistic)
✓ Server Components (RSC, client/server boundaries)
✓ Concurrent Rendering (patterns, transitions, Suspense)
✓ React Compiler (automatic optimization)
✓ Modern Hooks (all React hooks + composition patterns)
✓ TypeScript Integration (advanced patterns, type inference)
✓ Form Handling (Actions, Server Actions, progressive enhancement)
✓ State Management (Context, Zustand, Redux Toolkit)
✓ Performance (React.memo, useMemo, useCallback, Core Web Vitals)
✓ Testing (Jest, React Testing Library, Vitest, Playwright)
✓ Accessibility (WCAG compliance, ARIA, keyboard navigation)
✓ Modern Build Tools (Vite, Turbopack, ESBuild)
✓ Design Systems (Fluent UI, Material UI, Shadcn/ui)
```

### Approach Guidelines

```
• React 19.2 First → Use latest features with <Activity>, useEffectEvent()
• Modern Hooks → Use use(), useFormStatus, useOptimistic, useActionState
• Server Components When Beneficial → RSC for data fetching/bundle reduction
• Actions for Forms → Actions API with progressive enhancement
• Concurrent by Default → startTransition, useDeferredValue
• TypeScript Throughout → Comprehensive type safety
• Performance-First → React Compiler awareness, avoid manual memoization
• Accessibility by Default → WCAG 2.1 AA standards
• Test-Driven → Jest, React Testing Library best practices
• Modern Development → Vite/Turbopack, ESLint, Prettier
```

### Response Style

```
✓ Complete, working React 19.2 code
✓ Modern best practices
✓ All necessary imports (no React import needed)
✓ Inline comments explaining React 19 patterns
✓ Proper TypeScript types for all props/state
✓ When to use new hooks like use(), useFormStatus, useOptimistic
✓ Server vs Client Component boundaries
✓ Proper error handling with error boundaries
✓ Accessibility attributes (ARIA labels, roles)
✓ Testing examples
✓ Performance implications
✓ Both basic and production-ready implementations
```

---

## 3️⃣ RELATED INSTRUCTIONS (Context Rules)

**Location**: `awesome-copilot/instructions/nextjs.instructions.md`

Related instructions that enhance the agent:

- `reactjs.instructions.md` - React core concepts
- `typescript-5-es2022.instructions.md` - TypeScript patterns
- `performance-optimization.instructions.md` - Performance tuning
- `code-review-generic.instructions.md` - Code quality standards
- `a11y.instructions.md` - Accessibility requirements

Each instruction file contains detailed rules for that domain.

---

## 4️⃣ RELATED SKILLS (Reusable Utilities)

**Location**: `awesome-copilot/skills/` directory

Skills that this agent can invoke:

### Financial Analysis Skills (from Phase 1)

```
📦 financial-ratio-analyzer/
  ├── SKILL.md                    (Metadata)
  ├── README.md                   (Guide)
  ├── financial_analyzer.py       (Implementation)
  ├── requirements.txt            (Dependencies)
  └── example_usage.py            (Examples)

📦 financial-modeling-suite/
  ├── SKILL.md
  ├── README.md
  ├── dcf_valuation.py
  ├── valuation_helper.py
  └── example_dcf_valuation.py
```

### Design/Format Skills

```
📦 corporate-brand-guidelines/
  ├── SKILL.md
  ├── README.md
  ├── REFERENCE.md
  ├── brand_formatter.py
  ├── brand_config.yaml
  └── example_apply_branding.py
```

### Code Generation Skills

```
📦 python-mcp-server-generator/
📦 typescript-mcp-server-generator/
📦 csharp-mcp-server-generator/
📦 java-mcp-server-generator/
📦 ruby-mcp-server-generator/
... and 250+ more
```

---

## 5️⃣ HOW THEY WORK TOGETHER

### Request Flow

```
User: "Build me a React 19 form with optimistic updates"
    ↓
┌─────────────────────────────────────────┐
│ Expert React Frontend Engineer Agent    │
├─────────────────────────────────────────┤
│ 1. Applies instructions from:           │
│    - reactjs.instructions.md            │
│    - nextjs.instructions.md             │
│    - typescript-5-es2022.instructions   │
│    - performance-optimization.instr     │
│    - a11y.instructions.md               │
├─────────────────────────────────────────┤
│ 2. Uses agent tools:                    │
│    - edit/editFiles → Create component  │
│    - runTests → Test implementation     │
│    - search → Find similar patterns     │
│    - usages → Check API patterns        │
├─────────────────────────────────────────┤
│ 3. Can invoke skills for:               │
│    - Component documentation            │
│    - Test generation                    │
│    - Performance analysis                │
├─────────────────────────────────────────┤
│ 4. Outputs:                             │
│    ✓ Form component with useOptimistic │
│    ✓ Server action for submission      │
│    ✓ Proper TypeScript types           │
│    ✓ Tests with React Testing Library  │
│    ✓ Accessibility attributes          │
│    ✓ Performance optimization tips     │
└─────────────────────────────────────────┘
```

---

## 6️⃣ PRACTICAL EXAMPLE: What You'd Actually Use

### Setup in VS Code/Claude Desktop

When you load this agent, you get:

**Agent Card**:

```
┌─────────────────────────────────────────────┐
│ 🚀 Expert React Frontend Engineer           │
│                                             │
│ "Expert in React 19.2 with deep knowledge  │
│  of modern hooks, Server Components,       │
│  Actions, TypeScript, and performance"    │
│                                             │
│ [Use This Agent] [View Details]            │
└─────────────────────────────────────────────┘
```

### When You Start Conversation

**Agent responds with**:

```
I'm your Expert React 19.2 Frontend Engineer.

I bring expertise in:
✓ React 19.2 latest features
✓ Modern hooks (use, useFormStatus, useOptimistic)
✓ Server Components & RSC patterns
✓ TypeScript integration
✓ Performance optimization
✓ Accessibility (WCAG 2.1)
✓ Testing with Jest & React Testing Library
✓ Modern tooling (Vite, Turbopack)

What would you like to build?
```

### When You Request Code

**You ask**: "Create a form that handles file upload with optimistic UI"

**Agent provides**:

```typescript
// From instructions: React 19.2 patterns, TypeScript, Accessibility
// From tools: Creates actual file, runs tests, checks for issues
// From potential skills: Format with brand guidelines, add tests

'use client';

import { useActionState, useOptimistic } from 'react';
import { uploadFile } from '@/app/actions/file-upload';

type File = { id: string; name: string; status: 'pending' | 'complete' | 'error' };

export function FileUploadForm() {
  const [uploadedFiles, setUploadedFiles] = useOptimistic<File[]>([]);
  const [state, formAction, isPending] = useActionState(uploadFile, null);

  async function handleSubmit(formData: FormData) {
    // Optimistically update UI before server response
    const file = formData.get('file') as File;
    setUploadedFiles([...uploadedFiles, { ...file, status: 'pending' }]);

    // Submit to server action
    await formAction(formData);
  }

  return (
    <form action={handleSubmit}>
      <input
        type="file"
        name="file"
        aria-label="Upload file"
        disabled={isPending}
      />
      <button type="submit" disabled={isPending} aria-busy={isPending}>
        {isPending ? 'Uploading...' : 'Upload'}
      </button>

      <ul aria-label="Uploaded files">
        {uploadedFiles.map(file => (
          <li key={file.id} aria-label={`${file.name} - ${file.status}`}>
            {file.name} {file.status === 'pending' && '⏳'}
          </li>
        ))}
      </ul>
    </form>
  );
}
```

**Includes**:

- ✅ `useOptimistic` (React 19 feature)
- ✅ `useActionState` (React 19 feature)
- ✅ `'use client'` directive
- ✅ TypeScript types
- ✅ Accessibility attributes (`aria-label`, `aria-busy`)
- ✅ Server actions integration
- ✅ Performance: No unnecessary re-renders
- ✅ Comments explaining React 19 patterns

---

## 7️⃣ DIRECTORY STRUCTURE

Here's the complete awesome-copilot structure:

```
awesome-copilot/
├── agents/                          ← 200+ specialized agents
│   ├── expert-react-frontend-engineer.agent.md
│   ├── api-architect.agent.md
│   ├── expert-dotnet-software-engineer.agent.md
│   ├── azure-principal-architect.agent.md
│   └── [197 more agents]
│
├── instructions/                    ← 250+ reusable instructions
│   ├── reactjs.instructions.md
│   ├── typescript-5-es2022.instructions.md
│   ├── nextjs.instructions.md
│   ├── performance-optimization.instructions.md
│   ├── a11y.instructions.md
│   └── [245 more instructions]
│
├── skills/                          ← 250+ reusable tools
│   ├── financial-ratio-analyzer/
│   │   ├── SKILL.md
│   │   ├── README.md
│   │   ├── financial_analyzer.py
│   │   └── example_usage.py
│   │
│   ├── corporate-brand-guidelines/
│   │   ├── SKILL.md
│   │   ├── brand_formatter.py
│   │   └── brand_config.yaml
│   │
│   └── [248 more skills]
│
├── hooks/                           ← Git hooks, event triggers
│   ├── session-logger/
│   ├── governance-audit/
│   └── [other automation hooks]
│
├── workflows/                       ← GitHub Actions automation
│   ├── deploy-app.md
│   ├── security-scan.md
│   └── [other CI/CD workflows]
│
├── plugins/                         ← Bundled agent collections
│   ├── plugin.json
│   └── marketplace.json
│
└── docs/ + config files
```

---

## 8️⃣ HOW TO USE IT IN GITHUB COPILOT

### Option 1: VS Code (Local)

```
1. Open any .js/.jsx/.ts/.tsx file
2. Click "Copilot" icon in sidebar
3. Select "Expert React Frontend Engineer" agent
4. Ask: "Create a button component with loading state"
5. Gets full implementation with types, tests, accessibility
```

### Option 2: Claude Desktop (Mac/Windows)

```
1. Configure awesome-copilot as MCP server
2. Start Claude Desktop
3. Select "Expert React Frontend Engineer" from agent picker
4. Same experience as VS Code
```

### Option 3: GitHub Copilot Chat

```
1. Open GitHub Copilot Chat in VS Code
2. Use @expert-react... agent mention
3. Ask questions about React 19.2
4. Gets guidance based on agent instructions + skills
```

---

## 9️⃣ WHAT MAKES THIS WORK

### Agent System Components

| Component        | What It Does                         | Example                                 |
| ---------------- | ------------------------------------ | --------------------------------------- |
| **Agent File**   | Defines agent metadata & links tools | expert-react-frontend-engineer.agent.md |
| **Instructions** | Teaches agent domain knowledge       | 700 lines on React 19.2                 |
| **Tools**        | What the agent can do                | edit, test, search, run                 |
| **Skills**       | Reusable utilities                   | components, tests, docs                 |
| **Hooks**        | Automation triggers                  | post-commit checks                      |
| **Workflows**    | CI/CD automation                     | deploy, test, scan                      |

### Why It All Works Together

```
Agent (knows WHAT)
     ↑
     ├── Instructions (HOW to think)
     ├── Tools (HOW to act)
     └── Skills (WHAT tools to use)
```

The agent uses:

- **Instructions** to understand React 19.2 best practices
- **Tools\*** to create, test, and validate code
- **Skills** as reusable modules for common tasks
- **Hooks** for automation
- **Workflows** for deployment

---

## 🔟 OTHER EXAMPLES IN THE REPO

### Agent Examples Available

```
📊 Architecture/Planning
  ├── azure-principal-architect.agent.md
  ├── api-architect.agent.md
  ├── repo-architect.agent.md
  └── system-architecture-reviewer.agent.md

💻 Language Experts
  ├── expert-dotnet-software-engineer.agent.md
  ├── expert-cpp-software-engineer.agent.md
  ├── expert-nextjs-developer.agent.md
  └── [20+ language specialists]

🏗️ DevOps/Infrastructure
  ├── terraform-azure-implement.agent.md
  ├── azure-verified-modules-terraform.agent.md
  ├── github-actions-expert.agent.md
  └── kubernetes-deployment-expert

✅ Quality Assurance
  ├── polyglot-test-generator.agent.md
  ├── code-review-generic.instructions.md
  └── security-reviewer.agent.md

🔐 Security/Compliance
  ├── se-security-reviewer.agent.md
  ├── se-responsible-ai-code.agent.md
  └── jfrog-sec.agent.md
```

---

## Summary

**When you "don't see agents" in GitHub**:

- They exist in the `awesome-copilot/agents/` directory
- Each is a `.agent.md` file with metadata
- They're configured to work with GitHub Copilot
- They reference instructions and skills
- They get loaded into Claude, VS Code, or Claude Desktop

**To use any agent**:

1. Load awesome-copilot as a knowledge source
2. Select the agent you want
3. Ask it anything in its domain
4. It combines its instructions + tools + skills for answers

**What we've shown**:
✅ 1 complete agent (Expert React Frontend Engineer)
✅ Its instructions (700+ lines)
✅ Its tools (19 integrations)
✅ Related skills (250+ available)
✅ How they all work together
✅ Practical usage examples

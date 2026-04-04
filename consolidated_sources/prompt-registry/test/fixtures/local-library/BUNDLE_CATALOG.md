# Test Bundle Catalog

This directory contains **6 diverse example bundles** inspired by [github/awesome-copilot](https://github.com/github/awesome-copilot) for testing the marketplace and different content compositions.

---

## 📦 Bundle Overview

| Bundle                         | Version | Prompts | Instructions | Chat Modes | Agents | Total  |
| ------------------------------ | ------- | ------- | ------------ | ---------- | ------ | ------ |
| **Web Development Essentials** | 1.0.0   | 4       | 1            | 0          | 0      | **5**  |
| **Backend Development Pro**    | 1.2.0   | 3       | 1            | 1          | 0      | **5**  |
| **DevOps Toolkit**             | 1.3.0   | 3       | 0            | 0          | 1      | **4**  |
| **Security Essentials**        | 1.1.0   | 2       | 1            | 1          | 0      | **4**  |
| **Testing Pro Suite**          | 2.0.0   | 3       | 1            | 0          | 1      | **5**  |
| **Accessibility Champions**    | 1.0.0   | 2       | 1            | 1          | 1      | **5**  |
| **TOTAL**                      |         | **17**  | **5**        | **3**      | **3**  | **28** |

---

## 1️⃣ Web Development Essentials

**Focus:** Modern frontend development with React, TypeScript, and CSS

### Content Breakdown

- 💬 **4 Prompts**
  - Create React Component
  - Optimize CSS
  - Add Accessibility Features
  - Make Responsive
- 📋 **1 Instructions**
  - TypeScript Best Practices

### Tags

`web`, `react`, `typescript`, `css`, `frontend`, `ui`, `responsive`

### Use Cases

- React component generation
- CSS optimization and modernization
- Responsive design conversion
- TypeScript code standards

---

## 2️⃣ Backend Development Pro

**Focus:** API development, databases, and server-side logic

### Content Breakdown

- 💬 **3 Prompts**
  - Create REST API Endpoint
  - Design Database Schema
  - Add Input Validation
- 📋 **1 Instructions**
  - Node.js Standards
- 🎭 **1 Chat Mode**
  - API Architect Mode

### Tags

`backend`, `api`, `database`, `rest`, `graphql`, `nodejs`

### Use Cases

- RESTful API endpoint generation
- Database schema design
- Input validation implementation
- API architecture consulting

---

## 3️⃣ DevOps Toolkit

**Focus:** CI/CD, containerization, and infrastructure as code

### Content Breakdown

- 💬 **3 Prompts**
  - Create Dockerfile
  - GitHub Actions Workflow
  - Terraform Module
- 🤖 **1 Agent**
  - DevOps Engineer

### Tags

`devops`, `cicd`, `docker`, `kubernetes`, `terraform`, `automation`

### Use Cases

- Multi-stage Dockerfile creation
- CI/CD pipeline automation
- Infrastructure as Code
- DevOps consulting and automation

---

## 4️⃣ Security Essentials

**Focus:** Security best practices and vulnerability detection

### Content Breakdown

- 💬 **2 Prompts**
  - Security Code Review
  - Fix Security Vulnerability
- 📋 **1 Instructions**
  - Secure Coding Standards
- 🎭 **1 Chat Mode**
  - Security Expert Mode

### Tags

`security`, `vulnerability`, `owasp`, `penetration-testing`

### Use Cases

- OWASP Top 10 security reviews
- Vulnerability remediation
- Secure coding enforcement
- Security consulting and threat modeling

---

## 5️⃣ Testing Pro Suite

**Focus:** Comprehensive testing strategies and automation

### Content Breakdown

- 💬 **3 Prompts**
  - Write Unit Tests
  - Create E2E Tests
  - Improve Test Coverage
- 📋 **1 Instructions**
  - TDD Best Practices
- 🤖 **1 Agent**
  - QA Engineer Agent

### Tags

`testing`, `jest`, `cypress`, `tdd`, `quality`

### Use Cases

- Unit test generation (Jest/Vitest)
- End-to-end test creation (Playwright/Cypress)
- Test coverage analysis
- QA automation and strategy

---

## 6️⃣ Accessibility Champions

**Focus:** WCAG 2.1 compliance and inclusive design

### Content Breakdown

- 💬 **2 Prompts**
  - Accessibility Audit
  - Fix Accessibility Issues
- 📋 **1 Instructions**
  - WCAG Compliance Standards
- 🎭 **1 Chat Mode**
  - Accessibility Expert Mode
- 🤖 **1 Agent**
  - Screen Reader Testing Agent

### Tags

`accessibility`, `a11y`, `wcag`, `inclusive`, `aria`

### Use Cases

- WCAG 2.1 AA/AAA audits
- Accessibility issue remediation
- Inclusive design consulting
- Screen reader compatibility testing

---

## 🎯 Testing Coverage

These bundles provide excellent coverage for testing the marketplace:

### Content Type Distribution

- **Prompts (17)**: Most common type, various implementations
- **Instructions (5)**: Coding standards and best practices
- **Chat Modes (3)**: Expert consultant modes
- **Agents (3)**: Specialized AI assistants

### Composition Variety

- **Prompt-heavy**: Web Dev (4 prompts)
- **Mixed**: Backend, Testing (prompts + instructions + modes/agents)
- **Balanced**: Security, Accessibility (equal distribution)
- **Minimal**: DevOps (focused on specific workflows)

### Tag Diversity

- **Technology-specific**: `react`, `nodejs`, `docker`, `terraform`
- **Domain-specific**: `security`, `testing`, `accessibility`, `devops`
- **Skill-level**: `standards`, `best-practices`, `expert`

---

## 📊 Marketplace Testing Scenarios

### Scenario 1: Content Breakdown Display

Install any bundle → Marketplace should show accurate counts:

```
Web Dev Bundle:
💬 4 Prompts  📋 1 Instructions
🎭 0 Modes    🤖 0 Agents
```

### Scenario 2: Filter by Type

- **Filter: Prompts** → Shows all 6 bundles
- **Filter: Instructions** → Shows all 6 bundles
- **Filter: Chat Modes** → Shows Backend, Security, Accessibility (3)
- **Filter: Agents** → Shows DevOps, Testing, Accessibility (3)

### Scenario 3: Search Functionality

- **Search: "react"** → Shows Web Dev Bundle
- **Search: "security"** → Shows Security Bundle
- **Search: "testing"** → Shows Testing Bundle
- **Search: "api"** → Shows Backend, DevOps Bundles

### Scenario 4: Details View

Click "Details" on any bundle → Should show:

- Full description
- Content breakdown with counts
- Tags
- Bundle metadata
- **If installed**: List of all included prompts

### Scenario 5: Install/Uninstall

- Install bundle → Card shows "✓ Installed" badge
- Prompts sync to `~/.config/Code/User/prompts/`
- Uninstall → Badge removed, files cleaned up

---

## 🔧 Installation

These bundles are local fixtures for testing. To use them:

1. **Open Extension Development Host** (F5)
2. **Add Local Source:**
   ```
   Source Type: Local
   Path: /path/to/vscode-genai-apps-shared-context-installer/test/fixtures/local-library
   ```
3. **Browse Marketplace** → Should show all 6 bundles
4. **Test filtering, search, install, details**

---

## 📝 Inspiration

These bundles are inspired by real-world examples from:

- [github/awesome-copilot](https://github.com/github/awesome-copilot)
- Community-contributed prompts and instructions
- WCAG 2.1 guidelines
- OWASP security standards
- Industry best practices

---

## ✨ Summary

**6 diverse bundles** with **28 total items** covering:

- ✅ Frontend & Backend development
- ✅ DevOps & Infrastructure
- ✅ Security & Testing
- ✅ Accessibility & Compliance

Perfect for testing the marketplace with various content compositions! 🎉

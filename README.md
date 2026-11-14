# Agent Skills Repository

A universal, agent-agnostic repository of skills for AI coding agents. Supports **OpenCode**, **Claude Code**, **GitHub Copilot**, **Cursor**, and any agent that can read Markdown skill definitions.

## Install from a URL (any agent)

Tell your agent:

> Install the skills from `https://github.com/digodps/agent-skills` into this environment.

The agent runs one command, no cloning needed:

```bash
curl -fsSL https://raw.githubusercontent.com/digodps/agent-skills/master/install-remote.sh | bash -s <agent> [skill ...] [--tag tags]
```

Agents supported by `<agent>`: `opencode`, `claude`, `copilot`, `cursor`, `all`.
Omit skill names to install everything.

Examples:

```bash
# OpenCode: all skills
curl -fsSL https://raw.githubusercontent.com/digodps/agent-skills/master/install-remote.sh | bash -s opencode

# Claude Code: python + backend only
curl -fsSL https://raw.githubusercontent.com/digodps/agent-skills/master/install-remote.sh | bash -s claude --tag python,backend

# Project-local Copilot rules
curl -fsSL https://raw.githubusercontent.com/digodps/agent-skills/master/install-remote.sh | bash -s copilot commit create-skill
```

## Quick Start (local clone)

```bash
# Clone the repository
git clone https://github.com/digodps/agent-skills.git
cd agent-skills

# Install skills for your agent
./install.sh opencode          # OpenCode (~/.config/opencode/skills)
./install.sh claude            # Claude Code (~/.claude/skills)
./install.sh copilot           # GitHub Copilot (.github/skills)
./install.sh cursor            # Cursor (.cursor/skills)
./install.sh all               # Install to all supported agents
```

## Structure

```
agent-skills/
├── skills/                 # Skill definitions (universal format)
│   ├── <skill-name>/
│   │   ├── SKILL.md       # Skill definition (frontmatter + markdown)
│   │   └── scripts/       # Optional helper scripts
├── install.sh             # Universal installer
├── scripts/
│   ├── install-opencode.sh
│   ├── install-claude.sh
│   ├── install-copilot.sh
│   └── install-cursor.sh
└── registry.json          # Skill registry with metadata
```

## Skill Format

Each skill is a directory with a `SKILL.md` file using OpenCode-compatible frontmatter:

```markdown
---
name: skill-name
description: Brief description of what the skill does
allowed-tools: Bash(*)  # or specific tools
license: MIT
metadata:
  author: your-name
  version: "1.0"
  tags: [backend, python, async]
---

# Skill `skill-name`

Markdown documentation...
```

## Available Skills (66)

### Core Workflow
- `commit` - Conventional Commits with emoji
- `create-skill` - Create skills from OpenSpec proposals
- `code-review` - Automated code review
- `deploy` - Build & deploy pipeline
- `dev-spec` - Multi-agent OpenSpec development
- `mcp-dev` - MCP development server tools

### OpenSpec
- `openspec-propose` - Propose new changes
- `openspec-explore` - Explore ideas before implementing
- `openspec-apply-change` - Implement changes
- `openspec-update-change` - Update change plans
- `openspec-sync-specs` - Sync delta specs to main
- `openspec-archive-change` - Archive completed changes
- `egm-openspec` - EGM + OpenSpec workflow

### Language/Framework Experts
- `python-pro`, `async-python-patterns`, `python-testing-patterns`, `python-packaging`, `python-performance-optimization`, `python-development-python-scaffold`
- `typescript-pro`, `typescript-advanced-types`, `javascript-pro`, `modern-javascript-patterns`, `javascript-testing-patterns`, `javascript-typescript-typescript-scaffold`
- `golang-pro`, `go-concurrency-patterns`
- `rust-pro`, `rust-async-patterns`, `systems-programming-rust-project`
- `java-pro`, `csharp-pro`, `dotnet-architect`, `dotnet-backend-patterns`
- `ruby-pro`, `php-pro`
- `django-pro`, `fastapi-pro`, `fastapi-templates`, `nodejs-backend-patterns`
- `flutter-expert`, `react-native-architecture`, `ios-developer`, `mobile-developer`
- `react-modernization`, `react-state-management`, `nextjs-app-router-patterns`, `frontend-developer`, `frontend-mobile-development-component-scaffold`
- `uv-package-manager`

### Architecture & Patterns
- `backend-architect`, `backend-development-feature-development`, `backend-security-coder`
- `frontend-security-coder`, `frontend-mobile-security-xss-scan`
- `mobile-security-coder`
- `api-design-principles`, `api-documenter`, `api-testing-observability-api-mock`, `openapi-spec-generation`
- `react-native-architecture`

### Testing & Quality
- `teste-aceitacao` - E2E acceptance testing
- `teste-auth` - Auth testing via OpenSpec

### Utilities
- `antigravity-skills-manager` - Manage skills from Skill Vault
- `report` - Report OpenCode issues

## Custom Installation

Install specific skills only:

```bash
# Install single skill
./install.sh opencode commit create-skill

# Install by tag
./install.sh opencode --tag python
./install.sh opencode --tag backend,security
```

## Adding Skills

1. Create `skills/my-skill/SKILL.md` with frontmatter
2. Add optional scripts in `skills/my-skill/scripts/`
3. Run `./scripts/update-registry.sh` to update `registry.json`
4. Commit and push

## Project-Specific Skills

Some skills in this repo originate from a specific project (plex-autoplay) and contain hardcoded paths:

- `deploy` - references `scripts/build.sh`, `DEVELOPMENT_GUIDE.md`
- `dev-spec` - references `DEVELOPMENT_GUIDE.md`, uses mcp-dev
- `mcp-dev` - references plex-autoplay project structure
- `teste-aceitacao` / `teste-auth` - project-specific test patterns

These work as-is in their original project. For other projects, either fork and adapt, or skip them with `--tag` filters.

## Source

- 49 global skills from `~/.config/opencode/skills` (Antigravity Skill Vault)
- 14 project skills from `plex-autoplay/.agent-source/skills`
- 3 unique project skills: deploy, dev-spec, mcp-dev

## License

MIT - Individual skills may have their own licenses (specified in SKILL.md frontmatter).
# Aristotle Lean Skill

A reusable workflow for delegating Lean proof work to the [Aristotle](https://aristotle.harmonic.fun/) CLI.

The skill is agent-agnostic: the instructions in `SKILL.md` are plain text that Claude, Codex, or a human can follow directly. The repo is also laid out as a Claude Code plugin — the repo root doubles as its own plugin marketplace, so `/plugin marketplace add tangentstorm/aristotle-skill` plus `/plugin install aristotle-lean@aristotle-skill` is enough to install it. A bundled MCP server exposes Aristotle's submit/list/result/cancel/diff operations as tools.

## Layout

```
aristotle-skill/
├── .claude-plugin/
│   ├── plugin.json               # Plugin manifest (registers the MCP server)
│   └── marketplace.json          # Marketplace manifest so this repo is installable
├── mcp/
│   └── aristotle_mcp.py          # Bundled stdio MCP server wrapping the CLI
├── skills/
│   └── aristotle-lean/           # The skill itself
│       ├── SKILL.md              # Workflow and operating instructions
│       ├── agents/openai.yaml    # Codex UI metadata
│       └── references/
│           └── submitting-projects.md
├── build-plugin.sh               # POSIX build script
├── LICENSE
└── README.md
```

## Install

### Claude Cowork (plugin)

Build the plugin, then drop the resulting `.plugin` file into Cowork's plugin prompt.

Windows:

```powershell
.\build-plugin.ps1
```

macOS/Linux:

```bash
./build-plugin.sh
```

The script produces `aristotle-lean.plugin` in the repo root.

### Claude Code CLI

Install from GitHub with two slash commands inside a Claude Code session:

```
/plugin marketplace add tangentstorm/aristotle-skill
/plugin install aristotle-lean@aristotle-skill
```

The first command registers this repo as a plugin marketplace (one-time, persists in your user settings). The second enables the plugin — the skill auto-discovers, and the bundled `aristotle` MCP server registers on first load (Claude Code will prompt once to trust it).

To scope the install to a single project, add to `<project>/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "aristotle-lean@aristotle-skill": true
  }
}
```

Pull in marketplace updates later with `/plugin marketplace update aristotle-skill`.

For live local development (work on the plugin while testing it), point Claude Code at the checkout directly:

```
claude --plugin-dir C:\path\to\aristotle-skill
```

### Codex

From the repo root, paste these two lines into PowerShell. The first removes any existing install (including a plain copy from an earlier install), and the second creates a directory junction so Codex picks up repo edits live. Junctions work without admin rights.

```powershell
Remove-Item -Recurse -Force "$HOME\.codex\skills\aristotle-lean" -ErrorAction SilentlyContinue
New-Item -ItemType Junction -Path "$HOME\.codex\skills\aristotle-lean" -Target "$PWD\skills\aristotle-lean" | Out-Null
```

Invoke the skill in Codex as `$aristotle-lean`. The `agents/openai.yaml` alongside `SKILL.md` supplies Codex UI metadata.

## MCP server

When installed as a Claude Code plugin, `plugin.json` registers an `aristotle` MCP server (`mcp/aristotle_mcp.py`) that wraps the CLI as JSON-RPC tools: `submit`, `list`, `result`, `cancel`, `diff_result`. The server shells out to the `aristotle` binary, so the CLI still needs to be on `PATH`.

Path resolution is cwd-based with env overrides:

- `ARISTOTLE_LEAN_DIR` — Lean project dir passed as `--project-dir` to submit. Default: `./lean` if present, else the current dir.
- `ARISTOTLE_STAGING_DIR` — where result tarballs are downloaded and extracted. Default: `./aristotle-staging`.
- `ARISTOTLE_API_KEY` — read from the environment first; if unset, the server reads an `export ARISTOTLE_API_KEY=...` line from `./aristotle-key.sh`.

The server is Python-3-only and has no dependencies outside the standard library. The default command is `python`; edit `plugin.json` if your system uses `python3`.

## Requirements

This repo does not bundle the CLI or credentials. To use the skill at runtime the environment needs:

- the `aristotle` CLI on `PATH`
- an `ARISTOTLE_API_KEY` environment variable (or equivalent authenticated CLI configuration)
- a Lean project directory when using project-based submission (`lakefile.toml` or `lakefile.lean`, `lean-toolchain`, and `.lean` sources with valid imports)
- Python 3.7+ on `PATH` as `python`, if you want the bundled MCP server

## Notes

- The skill is designed for small, parallelizable Lean tasks with explicit write scopes.
- It is especially useful for theorem refactors, helper-lemma extraction, file-scoped proof repair, and document formalization.
- Keep API keys out of this repository.

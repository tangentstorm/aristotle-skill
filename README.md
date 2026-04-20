# Aristotle Lean Skill

A reusable workflow for delegating Lean proof work to the [Aristotle](https://aristotle.harmonic.fun/) CLI.

The skill is agent-agnostic: the instructions in `SKILL.md` are plain text that Claude, Codex, or a human can follow directly. The repo is also laid out as a Cowork plugin so it can be installed with one click into Claude Cowork.

## Layout

```
aristotle-skill/
├── .claude-plugin/
│   └── plugin.json               # Cowork plugin manifest
├── skills/
│   └── aristotle-lean/           # The skill itself
│       ├── SKILL.md              # Workflow and operating instructions
│       ├── agents/openai.yaml    # Codex UI metadata
│       └── references/
│           └── submitting-projects.md
├── build-plugin.ps1              # Windows build script (produces .plugin)
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

Copy the skill folder into your personal skills directory:

```powershell
Copy-Item -Recurse skills\aristotle-lean "$HOME\.claude\skills\aristotle-lean"
```

```bash
cp -r skills/aristotle-lean ~/.claude/skills/aristotle-lean
```

### Codex

From the repo root, paste these two lines into PowerShell. The first removes any existing install (including a plain copy from an earlier install), and the second creates a directory junction so Codex picks up repo edits live. Junctions work without admin rights.

```powershell
Remove-Item -Recurse -Force "$HOME\.codex\skills\aristotle-lean" -ErrorAction SilentlyContinue
New-Item -ItemType Junction -Path "$HOME\.codex\skills\aristotle-lean" -Target "$PWD\skills\aristotle-lean" | Out-Null
```

Invoke the skill in Codex as `$aristotle-lean`. The `agents/openai.yaml` alongside `SKILL.md` supplies Codex UI metadata.

## Requirements

This repo does not bundle the CLI or credentials. To use the skill at runtime the environment needs:

- the `aristotle` CLI on `PATH`
- an `ARISTOTLE_API_KEY` environment variable (or equivalent authenticated CLI configuration)
- a Lean project directory when using project-based submission (`lakefile.toml` or `lakefile.lean`, `lean-toolchain`, and `.lean` sources with valid imports)

## Notes

- The skill is designed for small, parallelizable Lean tasks with explicit write scopes.
- It is especially useful for theorem refactors, helper-lemma extraction, file-scoped proof repair, and document formalization.
- Keep API keys out of this repository.

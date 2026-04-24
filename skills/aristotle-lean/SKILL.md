---
name: aristotle-lean
description: Submit, monitor, and retrieve Aristotle Lean formalization jobs via the `aristotle` CLI. Use when delegating Lean proof work to Aristotle — filling sorries in a Lean project, formalizing a natural-language math document (.tex/.md/.txt), running parallel file-scoped proof tasks, polling or listing in-flight jobs, downloading results, or cancelling jobs. Triggers include mentions of Aristotle, `aristotle submit`, `aristotle formalize`, `aristotle result`, `aristotle list`, `aristotle cancel`, Lean formalization jobs, or delegating proofs/sorries to a remote Lean worker.
---

# Aristotle Lean

Use the Aristotle CLI as a remote Lean worker. Prefer small, file-scoped tasks with explicit success criteria, then poll and retrieve results.

Read `references/submitting-projects.md` when you need:

- exact project submission patterns
- Aristotle prompt cookbook examples
- project layout requirements
- document formalization guidance
- comment-based proof sketch guidance

## MCP tools (if available)

When this skill is installed as a Claude Code plugin, an `aristotle` MCP server is registered and the CLI is also available as tools: `submit`, `list`, `result`, `cancel`, `diff_result`. Prefer the MCP tools when they appear — they handle tarball extraction and diffing for you. Fall back to the CLI when running outside the plugin (Codex, plain shell, etc.).

## Quick Start

Run all Aristotle commands from the Lean project root when possible. In this repo that usually means `C:\ver\turyn\lean`.

Check CLI shape:

```powershell
aristotle --help
```

Available subcommands from `aristotle --help`:

- `submit`
- `formalize`
- `result`
- `list`
- `cancel`

Authentication:

- Prefer `ARISTOTLE_API_KEY` in the environment.
- In this repo, `aristotle-key.sh` exports the key. If needed, source or replicate that environment before calling the CLI.

## Workflow

1. Split work into small independent Lean tasks.
2. Prefer one Aristotle job per target file or per tightly scoped theorem family.
3. Include precise instructions in the job description: target file, theorem names, allowed write scope, proof style constraints, and whether automation should be minimized.
4. Submit jobs in parallel when they have disjoint write scopes.
5. Use `aristotle list` or saved project ids to track status.
6. Use `aristotle result` to wait for and download finished work.
7. Review the patch locally before integrating it with nearby changes.

## Task Design

Prefer tasks like:

- "Refactor helper lemmas in `Turyn/Equivalence.lean` for `doRevD` and `doNegRevD` only."
- "Replace automation in `step2_condition2` with direct mirror-index lemmas, without changing later steps."
- "Add conversion lemmas between `TurynTypeSeq` and `TurynType` in a new helper file, no theorem rewrites."

Avoid tasks like:

- "Clean up `Equivalence.lean`."
- "Refactor the whole Lean library."

Each task should specify:

- working directory
- target file paths
- exact lemma or theorem names to touch
- files that must not change
- expected proof style
- whether the result should be a patch, file download, or just a status report

## Commands

List jobs:

```powershell
aristotle list
```

Submit or formalize:

```powershell
aristotle submit --help
aristotle formalize --help
```

Wait for and download a result:

```powershell
aristotle result --help
```

Cancel a job:

```powershell
aristotle cancel --help
```

Because Aristotle CLI flags may evolve, inspect each subcommand with `--help` before first use in a session when exact syntax matters.

## Submission Patterns

For whole-project proof work, prefer `submit` with a Lean project directory.

For natural-language math documents, prefer `formalize`.

For Lean project jobs, expect Aristotle to require a normal Lean project layout with:

- `lakefile.toml` or `lakefile.lean`
- `lean-toolchain`
- Lean source files with proper imports

When using `--project-dir`, Aristotle can use Lean files and text notes in that directory as context. It will resolve dependencies but should not be assumed to rewrite arbitrary context files unless the task explicitly asks for modifications in the target scope.

Use header comments with `PROVIDED SOLUTION` when you want to guide proof search from a theorem statement. Do not rely on comments inside proof blocks.

## Lean-Specific Guidance

When delegating Lean work:

- State whether direct proofs are required instead of `aesop`, `grind`, or large `simp_all`.
- State whether theorem names and statement order must remain stable.
- Prefer introducing reusable helper lemmas before rewriting large normalization proofs.
- Keep write scopes disjoint across parallel jobs.
- Ask for result retrieval by project id if multiple jobs are in flight.
- For `Equivalence.lean`, prefer step-scoped prompts such as "rewrite `step4_condition4` using direct lemmas" over file-wide cleanup prompts.
- If you want direct proofs, say so explicitly. Aristotle prompt wording matters.

## Output Expectations

For each Aristotle task, keep a local note containing:

- the prompt sent
- the project id
- target files
- expected integration point

This makes it easier to poll with `list`, fetch with `result`, and merge multiple proof tasks safely.

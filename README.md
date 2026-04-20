# Aristotle Lean Skill

This repository packages a reusable workflow for delegating Lean proof work to the Aristotle CLI.

It is primarily written in Codex skill format, but the contents are plain text and can be used by other agents or humans as an instruction pack.

Aristotle site:

- https://aristotle.harmonic.fun/

## Files

- `SKILL.md`: the main workflow and operating instructions
- `agents/openai.yaml`: Codex UI metadata
- `references/submitting-projects.md`: CLI usage patterns, project requirements, and prompt examples

## How To Use

For Codex:

- install or copy this folder as a skill
- invoke it as `$aristotle-lean`

For Claude or other agents:

- read `SKILL.md`
- read `references/submitting-projects.md` when you need concrete CLI patterns or prompt examples
- follow the workflow directly as ordinary instructions

## Requirements

This repo does not include Aristotle credentials.

To use it, the environment should provide:

- the `aristotle` CLI
- an `ARISTOTLE_API_KEY` environment variable, or equivalent authenticated CLI configuration
- a Lean project directory when using project-based submission

## Notes

- The skill is designed for small, parallelizable Lean tasks with explicit write scopes.
- It is especially useful for theorem refactors, helper-lemma extraction, file-scoped proof repair, and document formalization.
- Keep API keys out of this repository.

# Submitting Projects

Use these patterns when delegating Lean work to Aristotle.

## Whole Lean Project

Fill all `sorry` placeholders in a Lean project:

```powershell
aristotle submit "Fill in the sorries" --project-dir ./my-lean-project --wait
```

General project submission:

```powershell
aristotle submit "Formalize the main theorems" --project-dir ./my-paper --wait
```

Use `submit` when the task depends on a Lean project, nearby `.lean` files, or supporting notes in the same directory.

## Formalize a Document

Formalize a natural-language math document:

```powershell
aristotle formalize paper.tex --wait --destination output.tar.gz
```

Use `formalize` for `.tex`, `.txt`, or `.md` sources when the main input is prose mathematics rather than an existing Lean project.

## Result Handling

Inspect outstanding jobs:

```powershell
aristotle list
```

Wait for and download a result:

```powershell
aristotle result --help
```

Cancel a job:

```powershell
aristotle cancel --help
```

## Project Requirements

Expect a normal Lean project layout:

```text
my-lean-project/
|- lakefile.toml
|- lean-toolchain
|- lake-manifest.json
`- MyLeanProject/
   |- Basic.lean
   `- Main.lean
```

Required inputs:

- `lakefile.toml` or `lakefile.lean`
- `lean-toolchain`
- `.lean` files with valid imports

Build artifacts should not be required as input.

## Context Rules

When submitting with `--project-dir`, the directory can include:

- Lean files containing definitions, structures, and theorem statements
- Text files containing notes, hints, or paper excerpts

Use this for:

- local API context
- theorem naming conventions
- proof sketches
- downstream file structure

## Proof Sketch Guidance

Aristotle can use natural-language hints in theorem header comments when tagged with `PROVIDED SOLUTION`.

Pattern:

```lean
/--
Statement summary.

PROVIDED SOLUTION
Natural-language proof sketch here.
-/
theorem target : ... := by
  sorry
```

Do not rely on comments inside proof blocks.

## Counterexamples

Aristotle can sometimes disprove false statements and leave a negation proof comment on the theorem. Use this when checking whether a conjecture or imported statement is even true before spending time on proof cleanup.

## Prompt Cookbook

Use short direct prompts when possible.

Sorry filling:

```text
Fill in all the sorries in this project
```

Restricted proof style:

```text
Prove this using only `ring` and `omega`, avoiding heavy automation
```

Documentation:

```text
Fill in the sorries and add detailed docstrings explaining each definition, theorem, and proof step for Lean beginners
```

Modularity:

```text
Refactor this file into a modular structure: extract helper lemmas, group related definitions, and minimize imports
```

Proof optimization:

```text
Golf all the proofs in this project: minimize tactic count and simplify where possible
```

Proof repair:

```text
Fix all compilation errors and linter warnings in this project
```

Auxiliary lemmas:

```text
Build auxiliary lemmas that would help prove the main sorry'd goal in this file
```

API development:

```text
Develop API lemmas for the main structure in this file: coercions, simp lemmas, and basic properties
```

Formal skeleton:

```text
Build a formal sorry'd skeleton closely following my paper, with theorem statements matching each result
```

Code quality:

```text
Formalize this paper and make sure the code quality closely follows Mathlib standards
```

## Lean Delegation Advice

For this repository, prefer prompts that pin:

- exact file paths under `lean/`
- exact theorem names
- allowed write scope
- whether automation should be minimized
- whether the output should be helper lemmas, direct proof rewrites, or a theorem skeleton

Prefer one Aristotle job per disjoint file or per disjoint theorem cluster.

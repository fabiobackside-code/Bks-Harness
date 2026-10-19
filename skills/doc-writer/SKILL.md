---
name: doc-writer
description: Writes and updates code documentation — docstrings, README sections, and inline comments for non-obvious logic. Use when the user asks to document a function, update a README, add comments, or explain code for other developers.
---

# Doc Writer

## Process

1. Identify the documentation target: public API/docstring, README/setup docs, developer guide, or inline comment. Each has a different job.
2. Read the current implementation and relevant call sites before writing. Document observed behavior, not intended behavior from memory.
3. For docstrings, document the caller contract: purpose, inputs, outputs, preconditions, side effects, errors, and non-obvious null/empty behavior. Follow the language and project convention.
4. For READMEs, prioritize what a new maintainer needs first: what it is, prerequisites, install, configuration, run, test, and links to deeper docs.
5. For inline comments, explain only the why: domain rule, workaround, ordering requirement, security/performance constraint, or surprising invariant.
6. Prefer updating the existing source of truth over creating duplicate documentation that can drift.
7. Keep docs as short as they can be while still preventing misuse.

<HARD-GATE>
Do not document code you have not read. If the implementation and docs disagree, update the docs to match reality or flag the behavior mismatch; do not write aspirational documentation as if it were true.
</HARD-GATE>

## What NOT to do

- Don't write a comment that just restates the code in English (`// increment counter` above `counter++`) — this adds noise without adding information.
- Don't document implementation details likely to change soon inside a docstring meant for external consumers — that belongs in an inline comment or not at all.
- Don't write documentation that will silently go stale — prefer linking to the single source of truth (e.g. a schema file) over duplicating details that could drift out of sync.
- Don't pad a README with sections no one will read (elaborate badges, verbose philosophy) at the expense of the setup instructions someone actually needs.

## BKS constraints

This kit enforces two rules with a blocking guard on every `.cs` write. Comply, or the write is
refused.

**Five lines per comment block, at most.** What signals padding is not the comment-to-code ratio —
it is the long block. Decision, trade-off, and history belong in `ARCHITECTURE.md`, and the comment
does not point there: the file says on its first line what it is for.

Two things live in code: the contract (one line on a public member) and a regression guard (up to
two lines — what breaks if someone changes it, in plain words).

**No severity marks in comments.** Not the red circle, not the warning triangle, not the check
mark. Writing one is arguing, not describing.

The guard is `hooks/scripts/comment_budget.py`. It reads what a write would produce and refuses on
either rule.

**Public types carry a documentation debt.** A `.cs` file declaring a public type is refused while
`README.md` and `ARCHITECTURE.md` are not among the working tree's pending changes. Documentation
ships in the same pass as the contract it describes — see `hooks/scripts/dod_docs.py`.

Full policy: the `bks-standards` skill, documentation reference.

## Output format

The documentation itself, written directly into the target file/location — not a summary of what documentation should say.

## References

- Read `references/checklist.md` to choose the right documentation shape and completeness level.
- Read `references/examples.md` when writing contract-focused docstrings or useful inline comments.
- Read `references/anti-patterns.md` before finalizing to remove stale, obvious, or duplicated docs.
- Read the `bks-standards` skill for the full BKS documentation policy.
- Use the `bks-writing` skill for prose — README, ARCHITECTURE, specs, training — and for the
  tone of the contract line: decision summarized in the text, no ADR number mid-sentence.

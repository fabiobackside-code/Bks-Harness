# Input Sources — BKS-SDD Reference

This document defines how the bks-sdd skill collects and documents input sources
before and during PRD generation.

---

## Source types

### 1. Local files (primary inputs)

Scan the user's current working directory for:
- `.pdf` — research articles, competitor docs, product briefs, technical specs
- `.md` — notes, prior specs, wiki exports, README files
- `.txt` — raw notes, transcripts, brainstorm dumps

**How to read PDFs:** Use the `pdf` skill or the Read tool with page range if the file
is large. Extract key ideas, constraints, and requirements. Do not copy text verbatim
into the PRD — synthesize.

**How to read .md / .txt:** Use the Read tool directly. Note the file name in the
Sources section of the PRD.

**Priority:** Files named `requirements`, `spec`, `brief`, `research`, or `notes`
should be read first as they are likely the most intentional inputs.

### 2. links.md (supplementary inputs)

If a `links.md` file exists in the working directory, treat it as a curated reading list.

**Expected format** (flexible — handle variations gracefully):
```markdown
# Links de referência

- https://example.com/article-1
- https://docs.platform.com/feature
https://another-source.io/blog/post
```

Parse all URLs from the file (one per line, with or without list markers, with or
without labels). For each URL:
1. Fetch with WebFetch
2. Extract relevant ideas, patterns, or constraints
3. Note the URL in the PRD's Sources section (§13)

If a URL fails to fetch, log it as "unreachable" in the Sources section and skip it.
Do not block PRD generation on failed URL fetches.

**What to look for in fetched content:**
- Patterns that inform architecture decisions
- Terminology used in the domain
- Constraints mentioned (regulatory, technical, UX)
- Prior art or competitive signals

### 3. Conversation context

The current session may contain additional inputs:
- User stated goals or constraints directly in chat
- Corrections or clarifications made during the session
- Named personas, success metrics, or non-negotiables

Treat these with the highest priority — they represent the user's explicit intent.

---

## How to document sources in the PRD

In Section §13 (Sources) of `PRD.md`, list every source used. Format:

```markdown
## 13. Sources

- `requirements.md` (local file): primary requirements and user personas
- `research/competitor-analysis.pdf` (local file, pages 3–7): competitive landscape
- https://docs.example.com/api (links.md): API contract reference
- Conversation context: goal statement and primary success metric
```

If no local files and no `links.md` were found, write:
```markdown
## 13. Sources

- Conversation context only: no local files or links.md found in working directory
```

---

## Checklist before writing the PRD

Before generating any PRD content, verify:

- [ ] Listed all `.pdf`, `.md`, `.txt` files in the working directory
- [ ] Read each file (or extracted key sections for large PDFs)
- [ ] Read `links.md` and fetched all reachable URLs
- [ ] Noted unreachable URLs
- [ ] Captured user's stated intent from conversation
- [ ] Ready to populate §13 with full source list

Only after this checklist is complete should PRD writing begin.

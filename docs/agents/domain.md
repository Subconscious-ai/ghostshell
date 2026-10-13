# Domain docs

## Read existing sources first

- `REPO-MAP.md`
- `README.md`

Read the sources relevant to the requested change. Use their terms and existing decision records.
Treat dated evidence and operational snapshots as historical; verify mutable claims before reuse.

## Context layout

Use the existing documentation layout. If a root `CONTEXT-MAP.md` exists, follow its pointers for the relevant context.
Otherwise read root `CONTEXT.md` and relevant `docs/adr/` entries when present.
If those paths are absent, continue from the sources above without creating placeholder glossaries or ADRs.
The `domain-modeling` skill creates new domain records only when an actual term or decision needs recording.
Surface conflicts with existing decisions before changing their behavior.

# Domain docs

Use one root domain context for this repository. Before domain modeling or
changing terminology, read `GLOSSARY.md` when present, or follow
`GLOSSARY-MAP.md` if the repository later introduces multiple contexts.
Read ADRs under `docs/adr/` that concern the change.

Existing context, architecture, and decision documents named in the repository's
agent instructions remain authoritative. Reuse those documents before adding
another glossary or decision record. Workspace packages alone do not require
separate domain contexts.

Missing glossary or ADR files are allowed. Continue with the repository's
existing documentation; create domain documents lazily when `/domain-modeling`
resolves terminology or a consequential decision.

Use the glossary's vocabulary in issues, specifications, and code. Surface a
conflict with an existing ADR before changing the decision it records.

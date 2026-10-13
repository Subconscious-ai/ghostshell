# Issue tracker: GitHub

Repository engineering issues and specs belong in `Subconscious-ai/ghostshell`. Use `gh` from this clone, or pass `--repo Subconscious-ai/ghostshell`.
Read the root agent instructions before publishing or claiming work. Existing issue forms, approval gates, and closure rules take precedence.

## Create an executable issue

Use the matching Task, Bug, or Feature form in `.github/ISSUE_TEMPLATE/` when present.
Otherwise read the organization's forms in `Subconscious-ai/.github`, under `.github/ISSUE_TEMPLATE/`.
For CLI creation, reproduce every required field from that form in a temporary body file.
Task fields include Job, Exit criterion, Prerequisites, Files in scope, Reuse first, and Out of scope.
Keep any additional required fields, including proof, authorization, and rollback fields.

```bash
gh issue create --repo Subconscious-ai/ghostshell --title "<title>" --body-file <body-file>
gh api --method PATCH repos/Subconscious-ai/ghostshell/issues/<number> -f type=Task
gh issue view <number> --repo Subconscious-ai/ghostshell --json number,title,body,state,labels,assignees
gh api repos/Subconscious-ai/ghostshell/issues/<number> --jq '.type.name'
```

Use `Bug` or `Feature` for those types. Verify the body and type before agent handoff.
For root instructions requiring a Roadmap project, use the existing organization Roadmap and its field ownership.
Do not create a second status tracker. Existing Linear references remain in Linear; link them when relevant.

## Read and maintain issues

```bash
gh issue view <number> --repo Subconscious-ai/ghostshell --json number,title,body,state,labels,assignees,comments
gh issue list --repo Subconscious-ai/ghostshell --state open --limit 1000 --json number,title,body,labels,assignees
gh issue edit <number> --repo Subconscious-ai/ghostshell --add-label "<label>"
gh issue edit <number> --repo Subconscious-ai/ghostshell --remove-label "<label>"
```

Create missing labels with `gh label create` before applying them. Use `triage-labels.md` for role mappings.
Issue closure requires the repository's acceptance evidence, completed delivery, and required approvals.
Posting an answer, passing a local check, or merging a helper alone does not establish customer behavior.

## Pull requests as a triage surface

**PRs as a request surface: no.** Existing PR review and merge rules still apply.
If this flag is later enabled, obtain `author_association` with `gh api repos/Subconscious-ai/ghostshell/pulls --paginate`.
External associations include `CONTRIBUTOR`, `FIRST_TIMER`, `FIRST_TIME_CONTRIBUTOR`, and `NONE`.

## Wayfinding operations

Use a map only when requested or when the effort spans sessions. The map and child tickets are GitHub issues.
Child tickets must satisfy the same issue-form and issue-type rules above.
Link children through GitHub sub-issues. If unavailable, use a task list and `Part of #<map>` in each child.
Use `wayfinder:map` and `wayfinder:<type>` labels only when needed; create missing labels first.

Native blocking edges use numeric database IDs:

```bash
gh api repos/Subconscious-ai/ghostshell/issues/<blocker> --jq .id
gh api --method POST repos/Subconscious-ai/ghostshell/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>
```

`-F` converts a numeric value to a JSON number. If native dependencies are unavailable, use `Blocked by: #<number>`.
Read the map's children in map order. A frontier ticket must be open, unassigned, and have no open blocker.

Assignment alone is not an exclusive lock. Coordinate one driving session per ticket before claiming it.
Re-read assignees immediately before `gh issue edit <number> --add-assignee @me` and verify afterward.
If another assignee or session owns the ticket, stop and coordinate instead of starting duplicate execution.
Two sessions using the same GitHub account must use their existing session coordinator; assignment cannot distinguish them.

Record the result in the child and update the map's decisions. Close the child only after its acceptance and repository closure rules pass.

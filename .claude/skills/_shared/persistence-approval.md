# Persistence preview and approval contract

Every write-capable Atlas workflow uses one preview and one explicit approval for one unchanged persistence scope.

## Required preview

Show, in compact plain language:

1. what Claude found;
2. what will be saved or changed;
3. evidence and provenance;
4. scope, confidence and remaining uncertainty;
5. existing, pending or conflicting Atlas knowledge;
6. decisions only the user can make;
7. what will not be saved;
8. validation and operational-state effects, including any intake checkpoint update.

The preview identifies the concrete files or records to be written. Approval such as “yes”, “save it” or “proceed” is valid only for that displayed scope.

## Handoffs

- Pass the approval and exact preview scope through internal skill/agent handoffs.
- Do not ask again merely because another Atlas skill performs the write.
- If the proposed claims, target records, files, evidence boundary, destructive effect or checkpoint range changes materially, stop and show a revised preview.
- A request to keep investigating, answer another question or inspect a diff is not persistence approval.

## Completion summary

Report: saved or changed; already covered; left unknown; deferred for human input; excluded; validation; and next publication step. Audit details may add staging IDs, lifecycle codes and internal dispositions without making them prerequisites for ordinary use.

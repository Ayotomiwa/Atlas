# Service onboarding questionnaire

Ask only material gaps and consolidate the first clarification round. Prioritise:

- What is the actual repository boundary, and is it a monorepo, nested repository or ordinary repository?
- Which primary domain owns the repository and each candidate component? Ask rather than infer when several are plausible.
- Which source roots represent independently addressable components, and which are only folders or internal modules?
- What responsibility and operational boundary makes each candidate component independently useful?
- Where is the authoritative infrastructure definition if it is not in this repository?
- Which upstream/downstream systems are known but not provable from the accessible code?
- What end-to-end flow boundary/name should be used when several paths are plausible?
- Who is the owner/SME who can review the staged context?
- Which explicitly referenced docs/repos are required but currently inaccessible?

A second targeted question round is allowed only when an unanswered item blocks correct staging. Optional unknowns should remain `not-covered` or `possible` rather than triggering an interrogation.

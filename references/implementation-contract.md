# Implementation completion contract

When modifying a repository:

1. Inspect the repository before choosing files.
2. Detect the language, framework, package manager, lockfile, and installed SDK versions.
3. Identify the real runtime entrypoint and frontend call component.
4. Read existing abstractions before adding new ones.
5. Preserve existing coding style, naming, abstractions, dependency manager, and error-handling patterns.
6. Make the smallest complete implementation.
7. When implementation is requested, edit real imported entrypoints; do not create an isolated example the application never uses.
8. Do not stop at sample code, a plan, or pseudocode when edits were requested.
9. Keep credentials in trusted server/agent code and preserve application authorization.
10. Distinguish product documentation, raw OpenAPI, rendered endpoint pages, and installed SDK signatures as separate contract surfaces.
11. Never transfer a field from one integration surface to another without verification.
12. When alternatives are described with `oneOf`, implement exactly-one validation rather than combining every alternative's requirements.
13. Preserve separate request media types; do not infer multipart support from a JSON example or vice versa.
14. Do not encode pricing, concurrency, call-length, resolution, model-access, or account-entitlement claims without current verification.
15. Preserve existing STT, VAD/turn detection, LLM, TTS, tools, conversation state, and frontend architecture unless the user asks to change them.
16. Distinguish provider acknowledgement, pipeline readiness, participant connection, placeholder display, and first rendered frame.
17. Implement cleanup and reconciliation for partial failure, abandoned clients, retries, and process shutdown.
18. Run the available formatter, type checker, unit tests, and production build.
19. Report:
    - files changed;
    - commands run;
    - validation results;
    - remaining documentation/version conflicts.
20. Never claim a command passed if it was not run.
21. When current documentation and the installed package disagree, preserve known-working behavior where safe, inspect package signatures/source, and report the conflict.

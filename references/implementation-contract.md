# Implementation completion contract

When modifying a repository:

1. Inspect the repository before choosing files.
2. Detect the language, framework, package manager, lockfile, and installed SDK versions.
3. Identify the real runtime entrypoint and the frontend call component.
4. Read existing abstractions before adding new ones.
5. Make the smallest complete implementation.
6. Do not stop at sample code, a plan, or pseudocode when edits were requested.
7. Keep credentials in trusted server/agent code and preserve application authorization.
8. Run the available formatter, type checker, unit tests, and build.
9. Report:
   - files changed,
   - commands run,
   - validation results,
   - remaining documentation/version conflicts.
10. Never claim a command passed if it was not run.
11. When current documentation and the installed package disagree, preserve known-working behavior, inspect package signatures/source, and report the conflict.

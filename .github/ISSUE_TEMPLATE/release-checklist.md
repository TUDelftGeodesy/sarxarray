---
name: Release Checklist
about: Create a checklist for making a new release.
title: Release checklist vX.Y.Z
labels: ''
assignees: ''
type: Task

---

I will make a new release by preforming the following steps:

- [ ] Step1: Update version in pyproject.toml
- [ ] Step2: Update `docs/CHANGELOG.md` with new change information
- [ ] Step3: Create release/tag at https://github.com/TUDelftGeodesy/sarxarray/releases

Hints:
- Step 1 and 2 can be done semi-automatically by calling agent skill, see [release-changelog](.github/skills/release-changelog). However the changes will always be reviewed and commited by human.
- The agent skill can be executed in GenAI prompt, e.g. GitHub Copilot Chat, by `/release-changelog vX.Y.Z` command, where `vX.Y.Z` is the new version label.
- Alternatively, one can run the helper script `bash .github/skills/release-changelog/scripts/generate_release_section.sh vX.Y.Z` to get bullets for the new release section.
---
name: release-changelog
description: 'Generate and update changelog entries from git tags and commit history. Use when preparing a new release, creating release notes, or backfilling missing changelog sections.'
argument-hint: '[new_tag] [previous_tag_optional]'
user-invocable: true
---

# Release Changelog Skill

Use this skill to generate a changelog section and insert it into docs/CHANGELOG.md before creating a GitHub release.

## When To Use

- You are preparing a new release and want to generate a new section in the changelog.
- You want consistent release-note sections across versions.

## Inputs

- new_tag: release label in semantic versioning format, for example v0.3.18.
  - If this tag already exists, the script compares previous tag to this tag.
  - If this tag does not exist yet, the script generates a pre-tag draft from previous tag to HEAD.
- previous_tag_optional: previous release tag. If omitted, helper script auto-detects it.

## Procedure

1. Update the version number in pyproject.toml to new_tag.
2. Run helper script at ./scripts/generate_release_section.sh using the next version label.
3. Review generated bullets and adjust wording for user-facing clarity.
4. Insert generated section below Unreleased in docs/CHANGELOG.md.

## Commands

- Generate using auto-detected previous tag:
  - bash .github/skills/release-changelog/scripts/generate_release_section.sh vX.Y.Z
- Generate with explicit range:
  - bash .github/skills/release-changelog/scripts/generate_release_section.sh vX.Y.Z vX.Y.(Z-1)

## Output Style Rules

- Use headings in this order when relevant: Added, Changed, Fixed, Docs, CI.
- Keep bullets short and user-facing.
- Avoid raw commit hashes in the changelog body.
- If a section has no meaningful content, omit it.

## References

- Suggested template: ./references/CHANGELOG_ENTRY_TEMPLATE.md

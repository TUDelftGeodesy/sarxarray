#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <new_tag_or_version> [previous_tag]" >&2
  echo "Examples:" >&2
  echo "  $0 v1.2.3" >&2
  echo "  $0 v1.2.4 v1.2.3" >&2
  exit 1
fi

target_label="$1"
prev_tag="${2:-}"
target_is_existing_tag=0

if git rev-parse -q --verify "refs/tags/$target_label" >/dev/null; then
  target_is_existing_tag=1
fi

if [[ -z "$prev_tag" ]]; then
  mapfile -t semver_tags < <(git tag --sort=creatordate | grep '^v' || true)
  found_index=-1
  for i in "${!semver_tags[@]}"; do
    if [[ "${semver_tags[$i]}" == "$target_label" ]]; then
      found_index="$i"
      break
    fi
  done

  if [[ "$target_is_existing_tag" -eq 1 ]]; then
    if [[ "$found_index" -eq -1 ]]; then
      echo "Error: tag '$target_label' is not part of the semver v* tag list." >&2
      exit 1
    fi

    if [[ "$found_index" -gt 0 ]]; then
      prev_tag="${semver_tags[$((found_index - 1))]}"
    fi
  else
    if [[ ${#semver_tags[@]} -gt 0 ]]; then
      prev_tag="${semver_tags[$((${#semver_tags[@]} - 1))]}"
    fi
  fi
elif ! git rev-parse -q --verify "refs/tags/$prev_tag" >/dev/null; then
  echo "Error: previous tag '$prev_tag' does not exist." >&2
  exit 1
fi

range="HEAD"
if [[ "$target_is_existing_tag" -eq 1 ]]; then
  range="$target_label"
  if [[ -n "$prev_tag" ]]; then
    range="$prev_tag..$target_label"
  fi
  release_date="$(git for-each-ref "refs/tags/$target_label" --format='%(creatordate:short)')"
else
  if [[ -n "$prev_tag" ]]; then
    range="$prev_tag..HEAD"
  fi
  release_date="$(date +%F)"
fi

mapfile -t subjects < <(git log --no-merges --pretty='%s' "$range")

declare -A used=()

print_section() {
  local title="$1"
  local regex="$2"
  local printed=0

  for line in "${subjects[@]}"; do
    local cleaned="$line"
    if [[ "$cleaned" =~ $regex ]]; then
      if [[ -z "${used[$cleaned]+x}" ]]; then
        if [[ $printed -eq 0 ]]; then
          echo
          echo "### $title"
          printed=1
        fi
        echo "- $cleaned"
        used["$cleaned"]=1
      fi
    fi
  done
}

echo "## [$target_label] - $release_date"
if [[ -n "$prev_tag" ]]; then
  echo
  if [[ "$target_is_existing_tag" -eq 1 ]]; then
    echo "Compared to: $prev_tag"
  else
    echo "Compared to: $prev_tag..HEAD (pre-tag draft)"
  fi
fi

print_section "Added" '(add|added|new|support|feature|introduc|reader|api reference)'
print_section "Changed" '(update|updated|change|changed|rename|refactor|release|bump|improve|regulat|standard|metadata|parsing|precision|conversion|workflow|sonar|lint|format)'
print_section "Fixed" '(fix|fixed|bug|error|correct|nan|warning)'
print_section "Docs" '(doc|readme|changelog|contributing|mkdocs|citation|zenodo)'
print_section "CI" '(github action|workflow|pypi|build|test|pre-commit|sonar)'

if [[ ${#subjects[@]} -eq 0 ]]; then
  echo
  echo "### Changed"
  echo "- No commits found in range $range."
elif [[ ${#used[@]} -eq 0 ]]; then
  echo
  echo "### Changed"
  echo "- Internal maintenance and versioning updates."
fi

#!/usr/bin/env bash
set -uo pipefail

# Clone everything into rag-app/docs, regardless of the caller's cwd
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
docs_dir="$script_dir/../docs"
mkdir -p "$docs_dir"
cd "$docs_dir"

repos=(
    # Core Top 10 series
    "Top10"
    "API-Security"
    "www-project-top-10-for-large-language-model-applications"
    "www-project-top-10-ci-cd-security-risks"
    "www-project-machine-learning-security-top-10"

    # Verification standards
    "ASVS"
    "AISVS"
    "www-project-proactive-controls"
    "www-project-llm-verification-standard"
    "www-project-mlsecops-verification-standard"

    # Testing & code review
    "wstg"
    "CodeReviewGuide"
    "www-project-ai-testing-guide"

    # Reference content
    "CheatSheetSeries"
    "DevGuide"
    "www-project-secure-coding-practices-quick-reference-guide"
    "www-community"

    # AI/ML security
    "GenAI-Security-Project/GenAI-Agent-Security-Initiative"
    "GenAI-Security-Project/GenAI-LLM-Top10"
    "GenAI-Security-Project/GenAI-Data-Security-Initiative"
    "GenAI-Security-Project/GenAI-Top-10-Governance"
    "GenAI-Security-Project/GenAI-Red-Team-Lab"
    "www-project-ai-security-and-privacy-guide"
    "www-project-llm-prompt-hacking"
    "www-project-data-security-top-10"

    # Threat modeling
    "www-project-threat-modeling-playbook"

    # Cloud & modern
    "www-project-cloud-native-application-security-top-10"

    # Specialized (for breadth)
    "www-project-mobile-top-10"
    "www-project-kubernetes-top-ten"
)

successful=()
failed=()

for repo in "${repos[@]}"; do
    echo ""
    echo "Cloning $repo..."

    # Directory name is the part after the last slash (handles "org/repo" entries)
    dir="${repo##*/}"

    # Entries without an explicit org (no "/") live under the OWASP org
    if [[ "$repo" == */* ]]; then
        full_repo="$repo"
    else
        full_repo="OWASP/$repo"
    fi

    # No incremental pull here: .git is stripped after checkout (see below), so a
    # prior run's directory has no history to pull from. Refresh means re-fetch.
    if [ -d "$dir" ]; then
        echo "  Already exists, refreshing..."
        rm -rf "$dir"
    fi

    # Partial clone (--filter=blob:none) + non-cone sparse-checkout limited to
    # "*.md" so only markdown blobs are ever fetched (no images/code/binaries),
    # then the .git dir is deleted so no history is kept either. The default
    # branch is still whatever the remote's HEAD points to, so this is just as
    # resilient to repos using "main" vs "master" vs anything else.
    if result=$( (
        set -e
        git clone --quiet --depth 1 --filter=blob:none --no-checkout \
            "https://github.com/$full_repo.git" "$dir"
        cd "$dir"
        git sparse-checkout init --no-cone
        git sparse-checkout set '*.md'
        git checkout --quiet
        rm -rf .git
        python3 "$script_dir/filter_markdown.py" "."
    ) 2>&1 ); then
        md_count=$(echo "$result" | tail -1 | cut -d' ' -f1)
        dropped_count=$(echo "$result" | tail -1 | cut -d' ' -f2)
        echo "  Success ($md_count markdown files kept, $dropped_count filtered out)"
        successful+=("$repo")
    else
        echo "  Failed: $result"
        rm -rf "$dir"
        failed+=("$repo")
    fi
done

# Summary
echo ""
printf '=%.0s' {1..60}
echo ""
echo "Summary:"
echo "  Successful: ${#successful[@]}"
echo "  Failed: ${#failed[@]}"

if [ "${#failed[@]}" -gt 0 ]; then
    echo ""
    echo "Failed repos:"
    for repo in "${failed[@]}"; do
        echo "  - $repo"
    done
fi

echo ""
echo "Total markdown files:"
find . -name '*.md' -type f | wc -l | awk '{print "  " $1}'

echo ""
echo "Total disk usage:"
du -sh . | awk '{print "  " $1}'

# User Guide

This guide covers detailed usage of ImpactScope, including command-line options, output formats, and common workflows.

## Basic Usage

### Analyzing a Commit

```bash
uv run -m src.main --repo-path ../your-c-project --commit HEAD
```

### Analyzing a Specific Commit

```bash
uv run -m src.main --repo-path ../your-c-project --commit abc1234
```

### Analyzing a Branch or Tag

```bash
uv run -m src.main --repo-path ../your-c-project --commit main
uv run -m src.main --repo-path ../your-c-project --commit v1.2.0
```

## Command-Line Options

### Required Options

- `--repo-path PATH`: Path to the target Git repository
- `--commit REF`: Commit hash, branch name, or tag to analyze

### Analysis Options

- `--depth N`: Call graph traversal depth (default: 1)
  - `0`: Only show directly changed functions
  - `1`: Show direct callers/callees (default)
  - `2`: Show second-level dependencies
  - Higher values increase analysis scope but may include more noise

### Output Options

- `--output FORMAT`: Output format
  - `text`: Human-readable terminal output (default)
  - `json`: Machine-readable JSON for automation
- `--visualize`: Generate HTML call graph visualization

### Advanced Options

- `--quiet`: Reduce output verbosity
- `--verbose`: Increase output verbosity

## Understanding Output

### Text Output Format

ImpactScope shows impact analysis per file with a tree structure:

```text
src/auth/auth.c  Changed lines: [(5, 10)]
login_user
┣━━ Upstream (calls this function)
┃   ┗━━ handle_request
┗━━ Downstream (called by this function)
    ┣━━ connect_db
    ┣━━ printf
    ┗━━ query_user
```

**Interpretation:**
- **Upstream**: Functions that call the changed function (who depends on this code)
- **Downstream**: Functions called by the changed function (what this code depends on)
- **Changed lines**: Line ranges modified in the commit

### JSON Output Format

For automation and CI/CD integration, use JSON output:

```bash
uv run -m src.main --repo-path ../your-c-project --commit HEAD --output json
```

The JSON structure includes:
- Repository and commit metadata
- Per-file impact analysis
- Function-level upstream/downstream relationships
- Change line ranges

## Common Workflows

### Pre-Review Analysis

Before reviewing a pull request:

```bash
# Analyze the latest commit on a branch
uv run -m src.main --repo-path ../my-project --commit feature-branch

# Use depth 2 for broader context
uv run -m src.main --repo-path ../my-project --commit feature-branch --depth 2
```

### Testing Impact Assessment

Determine which tests to run after a change:

```bash
# Get JSON output for test selection
uv run -m src.main --repo-path ../my-project --commit HEAD --output json > impact.json

# Process with your test runner
python -c "
import json
with open('impact.json') as f:
    data = json.load(f)
    impacted_functions = set()
    for file_data in data['files']:
        impacted_functions.update(file_data['changed_functions'])
        impacted_functions.update(file_data['downstream'])
    print('Impacted functions:', sorted(impacted_functions))
"
```

### CI/CD Integration

Incorporate into your CI pipeline:

```bash
#!/bin/bash
# ci-integration.sh

# Run impact analysis
uv run -m src.main --repo-path . --commit $COMMIT_SHA --output json > impact.json

# Check if critical functions are impacted
if jq -e '.files[] | select(.changed_functions[] | contains("security_check"))' impact.json > /dev/null; then
    echo "Security function impacted - requiring additional review"
    exit 1
fi

# Generate visualization for artifacts
uv run -m src.main --repo-path . --commit $COMMIT_SHA --visualize
```

### Visual Analysis

Generate interactive call graphs for complex changes:

```bash
# Create HTML visualization
uv run -m src.main --repo-path ../my-project --commit HEAD --visualize

# The visualization will be saved to artifacts/your-repo-commit/call_graph.html
# Open this file in a browser to explore the call graph interactively
```

## Best Practices

### Choosing Analysis Depth

- **Depth 0**: Quick overview of direct changes
- **Depth 1**: Balanced analysis for most reviews (default)
- **Depth 2**: Comprehensive analysis for critical changes
- **Depth 3+**: May include too much noise for large codebases

### When to Use Different Output Formats

- **Text output**: Human review, quick assessment
- **JSON output**: Automation, CI/CD, test selection
- **Visualization**: Complex changes, architectural understanding

### Repository Structure Considerations

ImpactScope works best with:
- Well-structured C projects with clear function boundaries
- Consistent naming conventions
- Modular architecture with explicit dependencies

## Examples

### Analyzing a Security Fix

```bash
uv run -m src.main --repo-path ../auth-service --commit security-patch-2024 --depth 2 --visualize
```

This would show:
- Which authentication functions were changed
- What other functions depend on the security logic
- Visual call graph for stakeholder communication

### Refactoring Impact Assessment

```bash
uv run -m src.main --repo-path ../data-processor --commit refactor-db-layer --output json
```

Use the JSON output to:
- Identify all affected data processing functions
- Plan regression testing scope
- Update documentation and interfaces

### Continuous Integration

```yaml
# .github/workflows/impact-analysis.yml
name: Impact Analysis
on: [pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Impact Analysis
        run: |
          uv run -m src.main --repo-path . --commit ${{ github.sha }} --output json > impact.json
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: impact-analysis
          path: impact.json
```

## Troubleshooting

If you encounter issues:

1. **No changes detected**: Ensure the commit actually modifies C source files
2. **Empty output**: Check that the repository path is correct and accessible
3. **Parser errors**: Verify the C code is syntactically valid
4. **Performance issues**: Try reducing analysis depth for large codebases

For detailed troubleshooting, see [troubleshooting.md](troubleshooting.md).

# API Reference

This reference covers all command-line options, JSON output schema, and programmatic interfaces.

## Command-Line Interface

### Basic Syntax

```bash
uv run -m src.main [OPTIONS]
```

### Options

#### Required Options

| Option | Type | Description |
|--------|------|-------------|
| `--repo-path PATH` | Path | Path to the target Git repository |
| `--commit REF` | String | Commit hash, branch name, or tag to analyze |

#### Analysis Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--depth N` | Integer | 1 | Call graph traversal depth<br>• `0`: Only changed functions<br>• `1`: Direct dependencies<br>• `2+`: Extended dependencies |
| `--include-pattern PATTERN` | String | `*.c,*.h` | File patterns to include in analysis |
| `--exclude-pattern PATTERN` | String | None | File patterns to exclude from analysis |

#### Output Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--output FORMAT` | Choice | text | Output format<br>• `text`: Human-readable terminal output<br>• `json`: Machine-readable JSON |
| `--visualize` | Flag | False | Generate HTML call graph visualization |
| `--output-file PATH` | Path | None | Write output to file instead of stdout |
| `--quiet` | Flag | False | Suppress progress messages |
| `--verbose` | Flag | False | Enable verbose logging |

#### Development Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--debug` | Flag | False | Enable debug mode with stack traces |
| `--profile` | Flag | False | Enable performance profiling |

### Examples

```bash
# Basic analysis
uv run -m src.main --repo-path ../my-project --commit HEAD

# Deep analysis with visualization
uv run -m src.main --repo-path ../my-project --commit abc123 --depth 3 --visualize

# JSON output for automation
uv run -m src.main --repo-path ../my-project --commit HEAD --output json --output-file results.json

# Custom file patterns
uv run -m src.main --repo-path ../my-project --commit HEAD --include-pattern "src/**/*.c" --exclude-pattern "**/test/**"
```

## JSON Output Schema

When using `--output json`, ImpactScope emits a structured JSON document suitable for CI, automation, and downstream tooling.

### Schema Version

Current schema version: `1.0.0`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "schema_version": {
      "type": "string",
      "description": "Version of the output schema"
    },
    "repo_path": {
      "type": "string",
      "description": "Repository path that was analyzed"
    },
    "commit": {
      "type": "string",
      "description": "Commit hash or ref that was analyzed"
    },
    "depth": {
      "type": "integer",
      "description": "Analysis depth used"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of analysis"
    },
    "files": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/file_analysis"
      },
      "description": "Array of per-file impact analysis results"
    }
  },
  "required": ["schema_version", "repo_path", "commit", "depth", "files"]
}
```

### File Analysis Object

```json
{
  "file_analysis": {
    "type": "object",
    "properties": {
      "file": {
        "type": "string",
        "description": "Source file path relative to repository root"
      },
      "changed_functions": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Functions directly affected by the commit"
      },
      "downstream": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Functions potentially impacted downstream (called by changed functions)"
      },
      "upstream": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Functions calling into the changed code"
      },
      "depth": {
        "type": "integer",
        "description": "Analysis depth for this file"
      },
      "changed_lines": {
        "type": "array",
        "items": {
          "$ref": "#/definitions/line_range"
        },
        "description": "Line ranges that changed (optional)"
      },
      "parsing_errors": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Any parsing errors encountered for this file"
      }
    },
    "required": ["file", "changed_functions", "downstream", "upstream", "depth"]
  }
}
```

### Line Range Object

```json
{
  "line_range": {
    "type": "object",
    "properties": {
      "start": {
        "type": "integer",
        "description": "Starting line number (1-indexed)"
      },
      "end": {
        "type": "integer",
        "description": "Ending line number (1-indexed)"
      }
    },
    "required": ["start", "end"]
  }
}
```

### Complete Example

```json
{
  "schema_version": "1.0.0",
  "repo_path": "../your-c-project",
  "commit": "HEAD",
  "depth": 1,
  "timestamp": "2024-01-15T10:30:00Z",
  "files": [
    {
      "file": "src/auth/auth.c",
      "changed_functions": ["login_user"],
      "downstream": ["connect_db", "printf", "query_user"],
      "upstream": ["handle_request"],
      "depth": 1,
      "changed_lines": [
        {"start": 5, "end": 10},
        {"start": 20, "end": 25}
      ]
    },
    {
      "file": "src/net/net.c",
      "changed_functions": ["handle_request"],
      "downstream": ["login_user", "printf"],
      "upstream": ["main"],
      "depth": 1,
      "changed_lines": [
        {"start": 3, "end": 8}
      ]
    }
  ]
}
```

## Programmatic Usage

### Python API

ImpactScope can be used programmatically in Python scripts:

```python
from src.core.git_diff import get_commit_diff
from src.core.parser import parse_file
from src.core.impact_mapper import compute_impact

# Get diff for a commit
diff_data = get_commit_diff("/path/to/repo", "HEAD")

# Parse changed files
parsed_files = {}
for file_path in diff_data.changed_files:
    parsed_files[file_path] = parse_file(file_path)

# Compute impact
impact_result = compute_impact(diff_data, parsed_files, depth=1)

# Process results
for file_analysis in impact_result.files:
    print(f"File: {file_analysis.file}")
    print(f"Changed functions: {file_analysis.changed_functions}")
    print(f"Upstream impact: {file_analysis.upstream}")
    print(f"Downstream impact: {file_analysis.downstream}")
```

### Integration Patterns

#### Test Selection

```python
import json
import subprocess

# Run impact analysis
result = subprocess.run([
    "uv", "run", "-m", "src.main",
    "--repo-path", "/path/to/repo",
    "--commit", "HEAD",
    "--output", "json"
], capture_output=True, text=True)

impact_data = json.loads(result.stdout)

# Extract impacted functions for test selection
impacted_functions = set()
for file_data in impact_data["files"]:
    impacted_functions.update(file_data["changed_functions"])
    impacted_functions.update(file_data["downstream"])

# Map to test cases
test_mapping = {
    "login_user": ["test_auth.py::test_login"],
    "connect_db": ["test_db.py::test_connection"],
    # ... more mappings
}

tests_to_run = []
for func in impacted_functions:
    tests_to_run.extend(test_mapping.get(func, []))

print(f"Tests to run: {tests_to_run}")
```

#### CI/CD Integration

```python
import os
import json

def analyze_impact(repo_path, commit):
    """Analyze impact and return structured data."""
    cmd = [
        "uv", "run", "-m", "src.main",
        "--repo-path", repo_path,
        "--commit", commit,
        "--output", "json"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Impact analysis failed: {result.stderr}")

    return json.loads(result.stdout)

def check_security_impact(impact_data):
    """Check if security-critical functions are impacted."""
    security_functions = {"authenticate", "authorize", "encrypt", "validate_token"}

    for file_data in impact_data["files"]:
        impacted = set(file_data["changed_functions"]) | set(file_data["downstream"])
        if impacted & security_functions:
            return True
    return False

# Usage in CI
impact_data = analyze_impact(".", os.environ["COMMIT_SHA"])
if check_security_impact(impact_data):
    print("Security functions impacted - additional review required")
    exit(1)
```

## Exit Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | Analysis completed successfully |
| 1 | Error | General error occurred |
| 2 | Invalid Arguments | Command-line arguments are invalid |
| 3 | Repository Error | Git repository issues (not found, not accessible) |
| 4 | Parsing Error | C code parsing failed |
| 5 | Analysis Error | Impact analysis failed |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `IMPACTSCOPE_CACHE_DIR` | Directory for caching parsed ASTs | `~/.cache/impactscope` |
| `IMPACTSCOPE_LOG_LEVEL` | Logging verbosity | `INFO` |
| `IMPACTSCOPE_MAX_WORKERS` | Maximum parallel workers for parsing | CPU count |

## File Formats

### Visualization Output

When using `--visualize`, ImpactScope generates:

- **HTML file**: Interactive call graph (`artifacts/repo-commit/visualization.html`)
- **JavaScript**: Graph rendering and interaction logic
- **CSS**: Styling for the visualization
- **JSON data**: Graph data embedded in the HTML

The HTML file is self-contained and can be opened in any modern browser.

### Log Files

Debug logging is written to stderr. For persistent logging:

```bash
uv run -m src.main --repo-path ../repo --commit HEAD --verbose 2> impactscope.log
```

## Compatibility

### Git Versions

- Minimum: Git 2.0+
- Recommended: Git 2.30+

### Python Versions

- Supported: Python 3.10, 3.11, 3.12
- Minimum: Python 3.10.0

### Operating Systems

- **Linux**: Fully supported
- **macOS**: Fully supported
- **Windows**: Supported (with Git Bash or WSL recommended)

## Limitations

### Known Limitations

- **Preprocessor directives**: Complex `#ifdef` usage may affect analysis accuracy
- **Function pointers**: Indirect calls through function pointers are not fully tracked
- **External libraries**: Analysis is limited to project source code
- **Template/generic code**: C preprocessor templates may cause parsing issues

### Performance Considerations

- **Large codebases**: Use appropriate depth limits
- **Memory usage**: Scales with codebase size and analysis depth
- **Disk I/O**: Git operations may be slow on network filesystems

## Changelog

### Version 1.0.0

- Initial stable API
- JSON schema version 1.0.0
- CLI interface stabilization
- Core analysis algorithms finalized

# Contributing to ImpactScope

Thank you for your interest in contributing to ImpactScope! This document covers development setup, coding standards, testing, and contribution workflows.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- A C repository for testing (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/impactscope.git
   cd impactscope
   ```

2. **Install dependencies**
   ```bash
   # Recommended: uv for dependency management
   uv sync

   # Alternative: pip with virtual environment
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # or .\.venv\Scripts\activate on Windows
   pip install -e .
   ```

3. **Install development dependencies**
   ```bash
   uv sync --extra test --extra dev
   # or
   pip install -e ".[test,dev]"
   ```

### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**

3. **Run tests**
   ```bash
   # Run the full test suite
   uv run run_tests.py

   # Or run directly with pytest
   uv run pytest

   # Run specific tests
   uv run pytest tests/test_parser.py -v
   ```

4. **Run linting and type checking**
   ```bash
   # Type checking
   uv run mypy src/

   # Code formatting (if configured)
   uv run black src/
   uv run isort src/
   ```

5. **Test your changes**
   ```bash
   # Test with the sample project
   uv run -m src.main --repo-path examples/sample-c-project-1 --commit HEAD

   # Test with your own C project
   uv run -m src.main --repo-path /path/to/your/c/project --commit HEAD
   ```

## Code Organization

### Directory Structure

```
impactscope/
├── src/
│   ├── core/           # Core analysis logic
│   ├── cli/            # Command-line interface
│   ├── output/         # Output formatters
│   ├── visualization/  # HTML visualization
│   └── utils/          # Shared utilities
├── tests/              # Unit tests
├── examples/           # Sample projects and scripts
├── docs/               # Documentation
├── artifacts/          # Generated outputs
└── htmlcov/            # Test coverage reports
```

### Key Modules

- **`src/core/`**: Core analysis pipeline
  - `git_diff.py`: Git integration and diff parsing
  - `parser.py`: AST parsing with Tree-sitter
  - `impact_mapper.py`: Impact analysis algorithms
  - `call_graph.py`: Graph construction and algorithms
  - `call_mapper.py`: Function call extraction
  - `constants.py`: Shared constants

- **`src/cli/`**: Command-line interface
  - `cli.py`: Main CLI application

- **`src/output/`**: Output formatting
  - `json_output.py`: JSON serialization

- **`src/visualization/`**: Visualization generation
  - `visualization.py`: HTML call graph generation

## Coding Standards

### Python Style

- **PEP 8** compliance
- **Type hints** for all function parameters and return values
- **Docstrings** for all public functions and classes
- **Descriptive variable names**
- **Consistent formatting**

### Example Function

```python
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

def analyze_impact(
    repo_path: str,
    commit: str,
    depth: int = 1,
    include_patterns: Optional[List[str]] = None
) -> Dict[str, any]:
    """
    Analyze the impact of a Git commit on a C codebase.

    Args:
        repo_path: Path to the Git repository
        commit: Commit hash or reference to analyze
        depth: Call graph traversal depth
        include_patterns: File patterns to include in analysis

    Returns:
        Dictionary containing impact analysis results

    Raises:
        ValueError: If repository path is invalid
        GitError: If commit cannot be found
    """
    if not os.path.exists(repo_path):
        raise ValueError(f"Repository path does not exist: {repo_path}")

    logger.info(f"Analyzing commit {commit} in {repo_path}")

    # Implementation here...
    return {}
```

### Error Handling

- **Specific exceptions** over generic `Exception`
- **Meaningful error messages**
- **Logging** for debugging information
- **Graceful degradation** when possible

```python
class ImpactScopeError(Exception):
    """Base exception for ImpactScope errors."""
    pass

class GitError(ImpactScopeError):
    """Git-related errors."""
    pass

class ParseError(ImpactScopeError):
    """C code parsing errors."""
    pass
```

## Testing

### Test Structure

Tests are organized by module in the `tests/` directory:

```
tests/
├── test_git_diff.py      # Git diff parsing tests
├── test_parser.py        # AST parser tests
├── test_impact_mapper.py # Impact analysis tests
├── test_call_graph.py    # Graph construction tests
├── test_path_utils.py    # Utility function tests
└── __init__.py
```

### Writing Tests

- **Unit tests** for individual functions
- **Integration tests** for end-to-end workflows
- **Property-based tests** where appropriate
- **Mock external dependencies** (Git, file system)

```python
import pytest
from unittest.mock import Mock, patch
from src.core.parser import parse_file, ParseError

class TestParser:
    def test_parse_valid_c_file(self):
        """Test parsing a valid C file."""
        # Arrange
        c_code = """
        #include <stdio.h>

        int main() {
            printf("Hello, world!\\n");
            return 0;
        }
        """

        # Act
        with patch('builtins.open', mock_open(read_data=c_code)):
            result = parse_file("test.c")

        # Assert
        assert len(result.functions) == 1
        assert "main" in result.functions

    def test_parse_invalid_c_file(self):
        """Test parsing an invalid C file raises ParseError."""
        # Arrange
        invalid_code = "this is not c code {{{"

        # Act & Assert
        with patch('builtins.open', mock_open(read_data=invalid_code)):
            with pytest.raises(ParseError):
                parse_file("invalid.c")

    @pytest.mark.parametrize("code,expected_functions", [
        ("void func1() {}", ["func1"]),
        ("int func2() { return 0; }", ["func2"]),
        ("void func1() {} void func2() {}", ["func1", "func2"]),
    ])
    def test_extract_functions(self, code, expected_functions):
        """Test function extraction with various inputs."""
        # Implementation...
        pass
```

### Running Tests

```bash
# Run all tests
uv run run_tests.py

# Run specific test file
uv run pytest tests/test_parser.py

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run tests in verbose mode
uv run pytest -v

# Run only failing tests from previous run
uv run pytest --lf
```

### Test Coverage

- **Minimum 80% coverage** for new code
- **All public APIs** must be tested
- **Error conditions** must be tested
- **Edge cases** must be covered

## Documentation

### Code Documentation

- **Docstrings** for all public functions, classes, and modules
- **Type hints** for parameters and return values
- **Usage examples** in docstrings where helpful

### User Documentation

- Update relevant docs in `docs/` when adding features
- Update examples if new functionality is demonstrated
- Keep API reference current

## Pull Request Process

### Before Submitting

1. **Run tests** and ensure they pass
2. **Run linting** and fix any issues
3. **Update documentation** if needed
4. **Write tests** for new functionality
5. **Test manually** with sample projects

### PR Template

```markdown
## Description
Brief description of the changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed
- [ ] All tests pass

## Documentation
- [ ] API documentation updated
- [ ] User guide updated
- [ ] Examples updated

## Checklist
- [ ] Code follows style guidelines
- [ ] Commit messages are descriptive
- [ ] No breaking changes without discussion
- [ ] Performance impact considered
```

### Review Process

1. **Automated checks** run on CI
2. **Code review** by maintainers
3. **Testing** verification
4. **Documentation** review
5. **Merge** after approval

## Commit Guidelines

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes
- **refactor**: Code refactoring
- **test**: Test additions/changes
- **chore**: Maintenance tasks

### Examples

```
feat(parser): add support for function pointer analysis

fix(impact_mapper): handle empty call graphs gracefully

docs(api): update JSON schema documentation

test(parser): add tests for complex function declarations
```

## Issue Tracking

### Bug Reports

When reporting bugs, please include:

- **ImpactScope version**
- **Python version**
- **Operating system**
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Sample code/repository** if applicable

### Feature Requests

For feature requests, please include:

- **Use case description**
- **Proposed solution**
- **Alternatives considered**
- **Impact on existing functionality**

## Release Process

### Version Numbering

ImpactScope follows [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update changelog
- [ ] Run full test suite
- [ ] Test with sample projects
- [ ] Update documentation
- [ ] Create git tag
- [ ] Publish to package repository

## Community

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn and contribute
- Maintain professional communication

### Getting Help

- **Documentation**: Check `docs/` first
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Discord/Slack**: Join community chat for real-time help

## Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- GitHub repository insights

Thank you for contributing to ImpactScope! 🚀

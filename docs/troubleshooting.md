# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with ImpactScope. If you encounter problems, start here before creating an issue.

## Quick Diagnosis

### Run the Diagnostic Script

```bash
#!/bin/bash
# diagnostic.sh - Quick ImpactScope health check

echo "=== ImpactScope Diagnostic Report ==="
echo "Date: $(date)"
echo "Python version: $(python --version)"
echo "Git version: $(git --version)"
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not in a Git repository"
    exit 1
fi

echo "✅ Git repository detected"

# Check for C files
c_files=$(find . -name "*.c" -type f | wc -l)
h_files=$(find . -name "*.h" -type f | wc -l)

echo "C files found: $c_files"
echo "Header files found: $h_files"

if [ "$c_files" -eq 0 ]; then
    echo "❌ No C source files found"
    echo "ImpactScope requires C source files to analyze"
    exit 1
fi

echo "✅ C source files found"

# Try basic ImpactScope command
echo ""
echo "Testing basic ImpactScope command..."
if command -v uv > /dev/null 2>&1; then
    if uv run python -c "import impactscope" 2>/dev/null; then
        echo "✅ ImpactScope import successful"
    else
        echo "❌ ImpactScope import failed"
        echo "Try: uv sync"
    fi
elif python -c "import impactscope" 2>/dev/null; then
    echo "✅ ImpactScope import successful"
else
    echo "❌ ImpactScope import failed"
    echo "Try: pip install -e ."
fi

echo ""
echo "=== End Diagnostic Report ==="
```

Run this script in your project directory to quickly identify common issues.

## Installation Issues

### Import Error: `No module named 'impactscope'`

**Symptoms:**
```
ModuleNotFoundError: No module named 'impactscope'
```

**Solutions:**

1. **Check if ImpactScope is installed:**
   ```bash
   # Using uv
   uv sync

   # Using pip
   pip install -e .
   ```

2. **Verify Python path:**
   ```bash
   python -c "import sys; print('\n'.join(sys.path))"
   ```

3. **Check virtual environment:**
   ```bash
   # Make sure you're in the right virtual environment
   which python
   which pip
   ```

### Dependency Installation Fails

**Symptoms:**
```
ERROR: Could not build wheels for tree-sitter-c
```

**Solutions:**

1. **Install system dependencies:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install build-essential python3-dev

   # macOS
   xcode-select --install

   # Windows (using conda)
   conda install -c conda-forge tree-sitter
   ```

2. **Use pre-compiled wheels:**
   ```bash
   pip install --only-binary=all impactscope
   ```

3. **Check Python version compatibility:**
   ```bash
   python --version  # Should be 3.10+
   ```

## Analysis Issues

### "No changes detected" or Empty Output

**Symptoms:**
- ImpactScope reports no changes found
- Empty impact analysis results
- No files analyzed

**Possible Causes & Solutions:**

1. **No C files in commit:**
   ```bash
   # Check what files changed in the commit
   git show --name-only HEAD | grep -E '\.(c|h)$'
   ```
   **Solution:** Make sure your commit includes C source files.

2. **Wrong commit reference:**
   ```bash
   # Verify the commit exists
   git show --oneline <commit-hash>
   ```
   **Solution:** Use correct commit hash or reference.

3. **Repository path issues:**
   ```bash
   # Check if path is correct
   ls -la <repo-path>
   git -C <repo-path> status
   ```
   **Solution:** Use absolute paths or verify relative path correctness.

4. **File pattern mismatch:**
   ```bash
   # Check if your files match include patterns
   find . -name "*.c" | head -10
   ```
   **Solution:** Adjust `--include-pattern` if needed.

### Parser Errors

**Symptoms:**
```
ERROR: Failed to parse file.c: SyntaxError at line 42
WARNING: Skipping file.c due to parse errors
```

**Possible Causes & Solutions:**

1. **Invalid C syntax:**
   ```bash
   # Check file syntax
   gcc -fsyntax-only file.c
   ```
   **Solution:** Fix C syntax errors in your code.

2. **Unsupported C features:**
   - Complex preprocessor macros
   - Assembly code blocks
   - Compiler-specific extensions

   **Solution:** ImpactScope supports standard C. Simplify complex constructs.

3. **Encoding issues:**
   ```bash
   # Check file encoding
   file file.c
   ```
   **Solution:** Ensure files are UTF-8 encoded.

4. **Large files:**
   - Files over 10MB may cause parsing timeouts
   **Solution:** Split large files or exclude them.

### Call Graph Issues

**Symptoms:**
- Missing function calls in analysis
- Incorrect call relationships
- Functions not connected as expected

**Possible Causes & Solutions:**

1. **Indirect calls:**
   ```c
   // These patterns may not be fully tracked:
   func_ptr = get_function();
   func_ptr();  // Indirect call

   (*func_table[index])();  // Function pointer array
   ```
   **Solution:** ImpactScope focuses on direct calls. Indirect calls require deeper analysis.

2. **Macro expansions:**
   ```c
   #define CALL_FUNC() func()
   CALL_FUNC();  // May not be recognized as func() call
   ```
   **Solution:** Macros are expanded by the preprocessor, not the parser.

3. **Conditional compilation:**
   ```c
   #ifdef FEATURE_X
   func();
   #endif
   ```
   **Solution:** ImpactScope analyzes all code paths. Use `--depth` to control analysis scope.

## Performance Issues

### Analysis Takes Too Long

**Symptoms:**
- Analysis runs for more than 5-10 minutes
- High memory usage
- Process appears to hang

**Solutions:**

1. **Reduce analysis depth:**
   ```bash
   impactscope --repo-path . --commit HEAD --depth 1
   ```

2. **Limit file scope:**
   ```bash
   impactscope --repo-path . --commit HEAD \
              --include-pattern "src/**/*.c" \
              --exclude-pattern "test/**"
   ```

3. **Use incremental analysis:**
   ```bash
   # Only analyze changed files
   git diff --name-only HEAD~1 | grep '\.c$' > changed_files.txt
   impactscope --repo-path . --commit HEAD \
              --include-pattern "@changed_files.txt"
   ```

4. **Check system resources:**
   ```bash
   # Monitor memory and CPU
   top -p $(pgrep -f impactscope)
   ```

### Out of Memory Errors

**Symptoms:**
```
MemoryError: Unable to allocate memory
```

**Solutions:**

1. **Increase system memory** or use a machine with more RAM

2. **Reduce batch size:**
   ```bash
   # Process fewer files at once
   impactscope --repo-path . --commit HEAD --batch-size 10
   ```

3. **Use streaming analysis:**
   ```bash
   # Process files one at a time
   impactscope --repo-path . --commit HEAD --stream
   ```

4. **Exclude large files:**
   ```bash
   find . -name "*.c" -size +1M -exec echo "Large file: {}" \;
   impactscope --repo-path . --commit HEAD \
              --exclude-pattern "**/large-file.c"
   ```

## Visualization Issues

### HTML Visualization Not Generated

**Symptoms:**
- No `artifacts/` directory created
- Missing `call_graph.html` file
- Visualization command doesn't produce output

**Solutions:**

1. **Check visualization dependencies:**
   ```bash
   python -c "import pyvis; print('PyVis available')"
   ```

2. **Verify output permissions:**
   ```bash
   mkdir -p artifacts
   touch artifacts/test.html  # Should work
   ```

3. **Run with verbose output:**
   ```bash
   impactscope --repo-path . --commit HEAD --visualize --verbose
   ```

### Visualization Too Slow/Large

**Symptoms:**
- Browser is unresponsive with large graphs
- Visualization takes too long to load

**Solutions:**

1. **Reduce graph size:**
   ```bash
   impactscope --repo-path . --commit HEAD \
              --depth 1 --visualize \
              --max-nodes 200
   ```

2. **Filter the graph:**
   ```bash
   # Only show impacted functions
   impactscope --repo-path . --commit HEAD \
              --visualize --impact-only
   ```

3. **Use different layout:**
   - Try hierarchical layout for better readability
   - Use filtering controls in the visualization

## CI/CD Integration Issues

### Pipeline Fails in CI

**Symptoms:**
- Works locally but fails in CI
- Different results between local and CI

**Common Issues:**

1. **Git state differences:**
   ```bash
   # In CI, ensure full clone
   git clone --depth=50 <repository>  # Not --depth=1
   ```

2. **Dependency differences:**
   ```bash
   # Ensure same Python version and dependencies
   python --version
   pip list | grep -E "(impactscope|tree-sitter)"
   ```

3. **Path differences:**
   ```bash
   # Use absolute paths in CI
   impactscope --repo-path $(pwd) --commit $COMMIT_SHA
   ```

### Quality Gates Too Sensitive

**Symptoms:**
- False positives blocking legitimate changes
- Quality gates failing unexpectedly

**Solutions:**

1. **Adjust thresholds:**
   ```yaml
   # Increase limits based on your codebase
   MAX_IMPACTED_FUNCTIONS: 100
   MAX_FILES: 20
   ```

2. **Refine patterns:**
   ```yaml
   # Be more specific about critical functions
   CRITICAL_PATTERNS: "auth_core,security_validate,payment_process"
   ```

3. **Exclude generated code:**
   ```yaml
   EXCLUDE_PATTERNS: "**/generated/**,**/build/**"
   ```

## Git-Related Issues

### Commit Not Found

**Symptoms:**
```
ERROR: Commit <hash> not found in repository
```

**Solutions:**

1. **Verify commit exists:**
   ```bash
   git log --oneline | grep <hash>
   git branch -a --contains <hash>
   ```

2. **Fetch more history:**
   ```bash
   git fetch --all --deepen=100
   ```

3. **Check repository state:**
   ```bash
   git status
   git remote -v
   ```

### Repository Access Issues

**Symptoms:**
```
ERROR: Could not access repository at <path>
```

**Solutions:**

1. **Check permissions:**
   ```bash
   ls -la <repo-path>
   git -C <repo-path> status
   ```

2. **Verify Git repository:**
   ```bash
   git -C <repo-path> rev-parse --git-dir
   ```

3. **Check for corruption:**
   ```bash
   git -C <repo-path> fsck
   ```

## Output and Formatting Issues

### JSON Parsing Errors

**Symptoms:**
- JSON output is malformed
- Downstream tools can't parse the output

**Solutions:**

1. **Validate JSON:**
   ```bash
   python -c "import json; json.load(open('impact.json'))"
   ```

2. **Check encoding:**
   ```bash
   file impact.json
   # Should be UTF-8
   ```

3. **Use correct options:**
   ```bash
   impactscope --repo-path . --commit HEAD --output json --pretty
   ```

### Text Output Issues

**Symptoms:**
- Garbled text output
- Incorrect tree formatting
- Missing colors in terminal

**Solutions:**

1. **Check terminal encoding:**
   ```bash
   echo $LANG
   echo $LC_ALL
   locale
   ```

2. **Use plain output:**
   ```bash
   impactscope --repo-path . --commit HEAD --output text --no-color
   ```

3. **Redirect to file:**
   ```bash
   impactscope --repo-path . --commit HEAD > impact.txt
   ```

## Debugging Techniques

### Enable Debug Logging

```bash
# Verbose output
impactscope --repo-path . --commit HEAD --verbose

# Debug mode
impactscope --repo-path . --commit HEAD --debug

# Log to file
impactscope --repo-path . --commit HEAD --log-file debug.log
```

### Isolate the Problem

1. **Test with minimal case:**
   ```bash
   # Use sample project
   uv run -m src.main --repo-path examples/sample-c-project-1 --commit HEAD
   ```

2. **Test individual components:**
   ```bash
   # Test Git diff extraction
   python -c "
   from src.core.git_diff import get_commit_diff
   diff = get_commit_diff('.', 'HEAD')
   print('Files changed:', len(diff.changed_files))
   "

   # Test parsing
   python -c "
   from src.core.parser import parse_file
   result = parse_file('test.c')
   print('Functions found:', len(result.functions))
   "
   ```

3. **Profile performance:**
   ```bash
   python -c "
   import cProfile
   cProfile.run('from src.main import main; main()', 'profile.stats')
   "
   ```

### Common Debug Commands

```bash
# Check Git state
git log --oneline -10
git status
git diff --name-only HEAD~1

# Check file structure
find . -name "*.c" | wc -l
find . -name "*.h" | wc -l

# Test Python environment
python --version
python -c "import sys; print(sys.path)"
python -c "import tree_sitter, tree_sitter_c; print('Tree-sitter OK')"

# Check ImpactScope installation
python -c "import impactscope; print(impactscope.__version__)"
```

## Getting Help

### Before Creating an Issue

1. **Check this troubleshooting guide**
2. **Run the diagnostic script** above
3. **Try the sample project** to verify basic functionality
4. **Search existing issues** on GitHub

### Information to Include in Bug Reports

When creating an issue, please include:

- **ImpactScope version:** `python -c "import impactscope; print(impactscope.__version__)"`
- **Python version:** `python --version`
- **Operating system:** `uname -a` or system info
- **Git version:** `git --version`
- **Command used:** Exact command that failed
- **Error output:** Full error message and traceback
- **Sample repository:** Minimal example that reproduces the issue (if possible)

### Performance Issues

For performance problems, include:

- **Repository size:** `find . -name "*.c" -exec wc -l {} + | tail -1`
- **Analysis time:** Time taken for the analysis
- **Memory usage:** Peak memory consumption
- **System specs:** CPU, RAM, disk type

### Feature Requests

When requesting features:

- **Use case:** What problem are you trying to solve?
- **Current workaround:** How do you handle this now?
- **Proposed solution:** Specific feature you'd like
- **Alternatives considered:** Other approaches you've thought of

## Known Limitations

### Current Constraints

1. **C language only:** ImpactScope currently only analyzes C code
2. **Direct calls only:** Indirect function calls through pointers are not fully tracked
3. **Preprocessor limitations:** Complex macro expansions may not be analyzed correctly
4. **Standard library:** Library functions are analyzed but may have incomplete call graphs

### Workarounds

1. **For indirect calls:** Use direct call patterns where possible
2. **For macros:** Consider using inline functions instead
3. **For large codebases:** Use depth limits and file filtering
4. **For performance:** Run analysis incrementally or on subsets

## Contributing Fixes

If you find a bug and have a fix:

1. **Create a minimal reproduction case**
2. **Write a test case** that fails before your fix
3. **Implement the fix** with clear code and comments
4. **Verify the fix** works with your reproduction case
5. **Submit a pull request** with the fix and test

See the [contributing guide](contributing.md) for detailed instructions.

---

If this troubleshooting guide doesn't resolve your issue, please [create an issue](https://github.com/your-org/impactscope/issues) on GitHub with the information requested above. The ImpactScope community will help you resolve the problem!

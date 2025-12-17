# Visualization Guide

ImpactScope can generate interactive HTML call graph visualizations to help you understand the relationships between functions and the impact of your changes. This guide explains how to create, interpret, and use these visualizations effectively.

## Generating Visualizations

### Basic Visualization

To generate an HTML call graph alongside your analysis:

```bash
uv run -m src.main --repo-path ../your-project --commit HEAD --visualize
```

This creates a visualization in the `artifacts/` directory:
```
artifacts/
└── your-project_HEAD/
    ├── call_graph.html    # Interactive visualization
    ├── call_graph.json    # Raw graph data
    └── visualization.log  # Generation log
```

### Advanced Options

```bash
# Generate with deeper analysis
uv run -m src.main --repo-path ../your-project --commit HEAD --depth 2 --visualize

# Specify custom output directory
uv run -m src.main --repo-path ../your-project --commit HEAD --visualize --output-dir ./my-visualizations

# Combine with JSON output
uv run -m src.main --repo-path ../your-project --commit HEAD --output json --visualize
```

## Understanding the Visualization

### Interface Overview

The HTML visualization opens in your browser and shows:

1. **Interactive Graph**: Function call relationships as a network
2. **Legend**: Color and shape coding for different node types
3. **Controls**: Zoom, pan, search, and filtering options
4. **Information Panel**: Details about selected nodes and edges

### Node Types and Colors

#### Function Nodes

- **🟢 Green**: Functions directly changed in the commit
- **🟡 Yellow**: Functions with upstream impact (call changed functions)
- **🔴 Red**: Functions with downstream impact (called by changed functions)
- **⚪ Gray**: Functions in the call graph but not impacted

#### Special Nodes

- **🔷 Blue Diamond**: Entry points (main, public APIs)
- **🔺 Red Triangle**: Error handling functions
- **⬜ White Square**: Library/external functions

### Edge Types

- **Solid lines**: Direct function calls
- **Dashed lines**: Indirect relationships (through multiple calls)
- **Arrow direction**: Shows call flow (A → B means A calls B)

## Using the Visualization

### Navigation

#### Basic Controls

- **Zoom**: Mouse wheel or zoom buttons
- **Pan**: Click and drag the background
- **Select nodes**: Click on any node to highlight it and show details
- **Multi-select**: Hold Ctrl/Cmd and click multiple nodes

#### Search and Filter

- **Search box**: Type function names to find specific functions
- **Filter dropdowns**: Show/hide different types of nodes and edges
- **Impact filter**: Focus only on impacted functions
- **Depth filter**: Limit display to specific analysis depths

### Exploring Impact

#### Understanding Impact Flow

1. **Start with changed functions** (green nodes)
2. **Follow upstream arrows** to see what calls the changed code
3. **Follow downstream arrows** to see what the changed code calls
4. **Look for clusters** of connected nodes to identify tightly coupled code

#### Common Patterns

**Direct Impact**:
```
main → process_request → validate_input → authenticate_user (changed)
```

**Cascade Effect**:
```
authenticate_user (changed) → log_auth_attempt → write_to_db → update_cache
```

**Fan-out Pattern**:
```
core_function (changed) → handler_A
                        → handler_B
                        → handler_C
```

### Analysis Techniques

#### Code Review Focus

1. **Identify high-impact functions**: Look for nodes with many connections
2. **Find critical paths**: Trace from entry points to changed functions
3. **Spot potential issues**: Look for unexpected dependencies
4. **Understand coupling**: See which modules are tightly interconnected

#### Testing Strategy

1. **Unit tests**: Test functions directly connected to changes
2. **Integration tests**: Test paths from entry points through changes
3. **Regression tests**: Test functions that might be affected indirectly

## Advanced Features

### Graph Analysis

#### Metrics Display

The visualization can show various metrics:

- **Degree centrality**: How connected a function is
- **Betweenness centrality**: How important a function is for connectivity
- **Impact score**: Custom scoring based on change impact

#### Path Finding

- **Shortest paths**: Find the shortest connection between two functions
- **All paths**: See all possible routes between functions
- **Bottleneck analysis**: Identify functions that create single points of failure

### Export and Sharing

#### Export Options

- **PNG/SVG export**: Save static images of the graph
- **JSON export**: Get the raw graph data for custom analysis
- **URL sharing**: Generate shareable links with specific views

#### Integration

```javascript
// Access graph data programmatically
const graphData = window.impactScopeData;

// Find impacted functions
const impactedNodes = graphData.nodes.filter(node =>
  node.impact_type !== 'unchanged'
);

// Calculate impact metrics
const impactMetrics = {
  totalFunctions: graphData.nodes.length,
  impactedFunctions: impactedNodes.length,
  maxConnections: Math.max(...graphData.nodes.map(n => n.connections))
};
```

## Best Practices

### When to Use Visualizations

**Use visualizations for:**

- **Complex changes**: When text output is too dense to understand
- **Architecture reviews**: Understanding system structure
- **Code reviews**: Visualizing impact scope for reviewers
- **Debugging**: Tracing unexpected dependencies
- **Documentation**: Creating visual system diagrams

**Use text output for:**

- **Simple changes**: Quick impact assessment
- **CI/CD automation**: Machine-readable results
- **Scripting**: Programmatic analysis
- **Performance**: Faster generation and parsing

### Optimization Tips

#### Large Codebases

- **Use depth limits**: Start with `--depth 1` and increase as needed
- **Filter by module**: Focus on specific directories or modules
- **Pre-filter**: Use `--include-pattern` to limit analysis scope

```bash
# Focus on authentication module
uv run -m src.main --repo-path ../project --commit HEAD \
  --include-pattern "src/auth/**/*.c" \
  --depth 2 \
  --visualize
```

#### Performance Analysis

- **Node count**: Aim for < 500 nodes for smooth interaction
- **Connection density**: Sparse graphs are easier to understand
- **Incremental analysis**: Analyze specific modules rather than entire codebase

### Interpretation Guidelines

#### Reading the Graph

1. **Changed functions are the starting point** - everything flows from them
2. **Arrow direction shows dependency** - A → B means A depends on B
3. **Node size often indicates importance** - larger nodes have more connections
4. **Clusters show coupling** - tightly connected groups may need coordinated changes

#### Common Misinterpretations

- **Don't assume all connections are equally important** - some are just utility calls
- **Don't ignore indirect impact** - downstream effects can be significant
- **Don't focus only on direct changes** - upstream callers may break
- **Don't assume visual complexity = code complexity** - graphs can be dense but simple

## Troubleshooting

### Common Issues

#### Graph Too Complex

**Problem**: Visualization shows too many nodes to be useful

**Solutions**:
- Reduce depth: `--depth 1` instead of `--depth 3`
- Filter patterns: `--include-pattern "src/feature/**/*.c"`
- Focus on impact: Use impact-only filtering in the UI

#### Missing Functions

**Problem**: Expected functions don't appear in the graph

**Solutions**:
- Check parsing: Ensure C code is syntactically valid
- Verify patterns: Make sure include patterns match your files
- Check depth: Functions might be beyond your depth limit

#### Performance Issues

**Problem**: Browser is slow or unresponsive

**Solutions**:
- Reduce node count (< 200 nodes recommended)
- Use Chrome/Firefox instead of other browsers
- Close other browser tabs
- Try static export instead of interactive view

#### Layout Problems

**Problem**: Graph layout is tangled or hard to read

**Solutions**:
- Use different layout algorithms (force-directed, hierarchical, circular)
- Adjust physics settings in the control panel
- Manually reposition important nodes
- Zoom into specific areas of interest

### Browser Compatibility

- **Chrome/Edge**: Full support, best performance
- **Firefox**: Full support, good performance
- **Safari**: Basic support, may have layout issues
- **Mobile browsers**: Limited support, use desktop for best experience

## Examples

### Security Review

```bash
# Analyze authentication changes with visualization
uv run -m src.main --repo-path ../auth-service --commit security-fix-123 \
  --depth 2 --visualize --include-pattern "src/**/*.c"
```

**What to look for:**
- How widely is the authentication function used?
- Are there bypass paths around security checks?
- What downstream systems depend on authentication results?

### Refactoring Impact

```bash
# Visualize impact of database layer refactoring
uv run -m src.main --repo-path ../app --commit db-refactor \
  --depth 3 --visualize
```

**Analysis approach:**
1. Find the changed database functions (green nodes)
2. Trace upstream to see what breaks if interfaces change
3. Trace downstream to see what needs testing
4. Identify clusters that may need coordinated updates

### Performance Investigation

```bash
# Analyze performance-critical function changes
uv run -m src.main --repo-path ../high-performance-app --commit perf-optimization \
  --depth 1 --visualize
```

**Focus areas:**
- Hot path functions (frequently called)
- Bottleneck functions (high betweenness centrality)
- Cascade effects from performance changes

## Integration Examples

### CI/CD Pipeline

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
          uv run -m src.main --repo-path . --commit ${{ github.sha }} \
            --depth 2 --visualize --output json > impact.json
      - name: Upload Visualization
        uses: actions/upload-artifact@v3
        with:
          name: impact-visualization
          path: artifacts/
```

### Documentation Generation

```bash
#!/bin/bash
# generate-docs.sh

# Generate visualization for documentation
uv run -m src.main --repo-path ../project --commit main \
  --depth 2 --visualize --output-dir docs/diagrams

# Copy to documentation site
cp artifacts/project_main/call_graph.html docs/diagrams/architecture.html
```

## Advanced Customization

### Custom Styling

The HTML visualization can be customized by modifying the generated files:

```html
<!-- Add custom CSS -->
<style>
  .impact-changed {
    border: 3px solid #ff6b6b !important;
  }

  .custom-legend {
    position: absolute;
    top: 10px;
    right: 10px;
    background: white;
    padding: 10px;
    border-radius: 5px;
  }
</style>
```

### API Integration

```javascript
// Custom analysis on graph data
window.addEventListener('load', function() {
  const graph = window.impactScopeGraph;

  // Find all security-related functions
  const securityFunctions = graph.nodes.filter(node =>
    node.label.toLowerCase().includes('auth') ||
    node.label.toLowerCase().includes('security')
  );

  // Highlight security functions
  securityFunctions.forEach(node => {
    node.color = '#ff4444';
  });

  // Update visualization
  graph.redraw();
});
```

## Getting Help

### Common Questions

**Q: Why is my graph empty?**
A: Check that your C files are syntactically valid and match the include patterns.

**Q: The visualization is too slow**
A: Reduce the depth or filter to fewer files. Try `--depth 1` first.

**Q: I can't find a specific function**
A: Use the search box, or check if the function is within your analysis depth/patterns.

**Q: How do I share visualizations?**
A: The HTML files are self-contained - just share the `.html` file.

For additional help, see the [troubleshooting guide](troubleshooting.md) or create an issue on GitHub.

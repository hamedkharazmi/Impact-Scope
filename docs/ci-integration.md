# CI/CD Integration Guide

ImpactScope integrates seamlessly into modern CI/CD pipelines to provide automated change impact analysis. This guide covers setup, configuration, and best practices for integrating ImpactScope into your development workflow.

## Quick Start

### Basic CI Integration

Add ImpactScope to your CI pipeline to analyze every commit:

```yaml
# .github/workflows/impact-analysis.yml
name: Impact Analysis
on: [pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install ImpactScope
        run: |
          pip install git+https://github.com/your-org/impactscope.git
      - name: Run Impact Analysis
        run: |
          impactscope --repo-path . --commit ${{ github.sha }} --output json > impact.json
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: impact-analysis
          path: impact.json
```

## Installation Methods

### Method 1: PyPI Package (Recommended)

```yaml
# Install from PyPI (when available)
- name: Install ImpactScope
  run: pip install impactscope
```

### Method 2: Direct Git Install

```yaml
# Install directly from Git
- name: Install ImpactScope
  run: pip install git+https://github.com/your-org/impactscope.git
```

### Method 3: Local Build

```yaml
# Build and install locally
- name: Install ImpactScope
  run: |
    git clone https://github.com/your-org/impactscope.git
    cd impactscope
    pip install -e .
```

### Method 4: Docker Container

```yaml
# Use Docker image (when available)
- name: Run ImpactScope
  run: |
    docker run --rm -v $(pwd):/workspace \
      your-org/impactscope:latest \
      --repo-path /workspace --commit ${{ github.sha }}
```

## Pipeline Integration

### GitHub Actions

#### Basic Setup

```yaml
name: Impact Analysis
on:
  pull_request:
    branches: [ main, develop ]
  push:
    branches: [ main ]

jobs:
  impact-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full git history

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install ImpactScope
        run: pip install impactscope

      - name: Run Impact Analysis
        id: impact
        run: |
          impactscope --repo-path . --commit ${{ github.sha }} \
                     --output json \
                     --depth 2 > impact.json

      - name: Upload Impact Report
        uses: actions/upload-artifact@v3
        with:
          name: impact-analysis
          path: impact.json

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const impact = JSON.parse(fs.readFileSync('impact.json', 'utf8'));

            const summary = `## Impact Analysis Results
            - Files analyzed: ${impact.files.length}
            - Total impacted functions: ${impact.files.reduce((sum, f) => sum + f.changed_functions.length + f.downstream.length, 0)}
            - Analysis depth: ${impact.depth}

            [View detailed results](https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }})`;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: summary
            });
```

#### Advanced GitHub Actions Setup

```yaml
name: Comprehensive Impact Analysis
on:
  pull_request:
    branches: [ main, develop ]

jobs:
  impact-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Cache ImpactScope
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-impactscope-${{ hashFiles('**/requirements*.txt') }}

      - name: Install ImpactScope
        run: pip install impactscope

      - name: Run Impact Analysis
        id: analyze
        run: |
          # Run analysis with visualization
          impactscope --repo-path . --commit ${{ github.sha }} \
                     --output json \
                     --depth 2 \
                     --visualize > impact.json

      - name: Quality Gate Check
        id: quality
        run: |
          python -c "
          import json
          import sys

          with open('impact.json') as f:
              data = json.load(f)

          # Check for high-impact changes
          high_impact = False
          for file_data in data['files']:
              impacted_count = len(file_data['changed_functions']) + len(file_data['downstream'])
              if impacted_count > 10:  # Threshold for high impact
                  high_impact = True
                  break

          if high_impact:
              print('High impact change detected - additional review required')
              sys.exit(1)
          else:
              print('Change impact within acceptable limits')
          "

      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: impact-analysis-${{ github.sha }}
          path: |
            impact.json
            artifacts/

      - name: Update PR Status
        uses: actions/github-script@v6
        if: always()
        with:
          script: |
            const status = '${{ steps.quality.outcome }}' === 'success' ? 'success' : 'failure';
            const description = status === 'success'
              ? 'Impact analysis passed'
              : 'High impact change detected';

            github.rest.repos.createCommitStatus({
              owner: context.repo.owner,
              repo: context.repo.repo,
              sha: context.sha,
              state: status,
              context: 'impact-analysis',
              description: description,
              target_url: `https://github.com/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId}`
            });
```

### GitLab CI/CD

```yaml
# .gitlab-ci.yml
stages:
  - test
  - impact-analysis
  - deploy

impact_analysis:
  stage: impact-analysis
  image: python:3.10
  before_script:
    - pip install impactscope
  script:
    - impactscope --repo-path . --commit $CI_COMMIT_SHA --output json > impact.json
  artifacts:
    reports:
      metrics: impact.json
    paths:
      - impact.json
    expire_in: 1 week
  only:
    - merge_requests

# Quality gate example
quality_gate:
  stage: impact-analysis
  image: python:3.10
  before_script:
    - pip install impactscope
  script:
    - |
      impactscope --repo-path . --commit $CI_COMMIT_SHA --output json > impact.json
      python -c "
      import json
      import sys

      with open('impact.json') as f:
          data = json.load(f)

      # Your quality criteria here
      max_impacted = 20
      total_impacted = sum(
          len(f['changed_functions']) + len(f['downstream'])
          for f in data['files']
      )

      if total_impacted > max_impacted:
          print(f'Impact too high: {total_impacted} > {max_impacted}')
          sys.exit(1)
      "
  allow_failure: false
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any

    stages {
        stage('Impact Analysis') {
            steps {
                script {
                    // Install ImpactScope
                    sh 'pip install impactscope'

                    // Run analysis
                    sh "impactscope --repo-path . --commit ${env.GIT_COMMIT} --output json > impact.json"

                    // Parse results
                    def impactData = readJSON file: 'impact.json'

                    // Quality gate
                    def totalImpacted = impactData.files.sum { file ->
                        file.changed_functions.size() + file.downstream.size()
                    }

                    if (totalImpacted > 15) {
                        echo "High impact change detected: ${totalImpacted} functions impacted"
                        currentBuild.result = 'UNSTABLE'
                    }

                    // Archive artifacts
                    archiveArtifacts artifacts: 'impact.json', fingerprint: true
                }
            }
        }
    }

    post {
        always {
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'artifacts',
                reportFiles: 'call_graph.html',
                reportName: 'Impact Visualization'
            ])
        }
    }
}
```

### Azure DevOps

```yaml
# azure-pipelines.yml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.10'

  - script: pip install impactscope
    displayName: 'Install ImpactScope'

  - script: |
      impactscope --repo-path . --commit $(Build.SourceVersion) \
                 --output json \
                 --depth 2 > impact.json
    displayName: 'Run Impact Analysis'

  - task: PublishBuildArtifacts@1
    inputs:
      pathToPublish: 'impact.json'
      artifactName: 'impact-analysis'
    displayName: 'Publish Impact Report'

  - task: PublishBuildArtifacts@1
    condition: succeeded()
    inputs:
      pathToPublish: 'artifacts'
      artifactName: 'visualizations'
    displayName: 'Publish Visualizations'
```

## Quality Gates and Policies

### Basic Quality Gates

```python
#!/usr/bin/env python3
# quality_gate.py

import json
import sys
import os

def check_quality_gates(impact_file, config):
    """Check impact analysis against quality gates."""

    with open(impact_file) as f:
        data = json.load(f)

    violations = []

    # Gate 1: Maximum impacted functions
    total_impacted = sum(
        len(f['changed_functions']) + len(f['downstream'])
        for f in data['files']
    )

    if total_impacted > config.get('max_impacted_functions', 50):
        violations.append(f"Too many impacted functions: {total_impacted}")

    # Gate 2: Critical functions check
    critical_patterns = config.get('critical_patterns', [])
    for file_data in data['files']:
        all_functions = set(file_data['changed_functions'] + file_data['downstream'])
        for pattern in critical_patterns:
            if any(pattern in func for func in all_functions):
                violations.append(f"Critical function impacted: {pattern}")

    # Gate 3: File count limits
    if len(data['files']) > config.get('max_files', 10):
        violations.append(f"Too many files impacted: {len(data['files'])}")

    return violations

if __name__ == '__main__':
    impact_file = sys.argv[1] if len(sys.argv) > 1 else 'impact.json'

    # Load configuration
    config = {
        'max_impacted_functions': int(os.environ.get('MAX_IMPACTED_FUNCTIONS', '50')),
        'max_files': int(os.environ.get('MAX_FILES', '10')),
        'critical_patterns': os.environ.get('CRITICAL_PATTERNS', 'auth,security,encrypt').split(',')
    }

    violations = check_quality_gates(impact_file, config)

    if violations:
        print("Quality gate violations:")
        for violation in violations:
            print(f"  - {violation}")
        sys.exit(1)
    else:
        print("All quality gates passed")
```

### Progressive Quality Gates

```yaml
# Different rules for different branches
name: Progressive Quality Gates
on:
  pull_request:
    branches: [ main, develop ]

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    steps:
      - name: Set Quality Thresholds
        id: thresholds
        run: |
          if [[ "${{ github.base_ref }}" == "main" ]]; then
            echo "max_impacted=20" >> $GITHUB_OUTPUT
            echo "require_visualization=true" >> $GITHUB_OUTPUT
          else
            echo "max_impacted=50" >> $GITHUB_OUTPUT
            echo "require_visualization=false" >> $GITHUB_OUTPUT
          fi

      - name: Run Impact Analysis
        run: |
          impactscope --repo-path . --commit ${{ github.sha }} \
                     --output json \
                     --depth 2 > impact.json

      - name: Check Quality Gates
        run: |
          python -c "
          import json
          import os

          with open('impact.json') as f:
              data = json.load(f)

          max_impacted = int(os.environ['MAX_IMPACTED'])
          total_impacted = sum(
              len(f['changed_functions']) + len(f['downstream'])
              for f in data['files']
          )

          if total_impacted > max_impacted:
              print(f'Quality gate failed: {total_impacted} > {max_impacted}')
              exit(1)
          "
        env:
          MAX_IMPACTED: ${{ steps.thresholds.outputs.max_impacted }}
```

## Test Selection Integration

### Impact-Based Test Selection

```python
#!/usr/bin/env python3
# test_selector.py

import json
import subprocess
import os

def select_tests(impact_file, test_mapping):
    """Select tests based on impact analysis."""

    with open(impact_file) as f:
        data = json.load(f)

    impacted_functions = set()

    # Collect all impacted functions
    for file_data in data['files']:
        impacted_functions.update(file_data['changed_functions'])
        impacted_functions.update(file_data['downstream'])
        impacted_functions.update(file_data['upstream'])

    # Map functions to tests
    selected_tests = set()
    for func in impacted_functions:
        if func in test_mapping:
            selected_tests.update(test_mapping[func])

    return sorted(selected_tests)

def run_selected_tests(tests, test_command):
    """Run the selected tests."""

    if not tests:
        print("No specific tests selected, running full suite")
        subprocess.run(test_command, shell=True)
        return

    # Filter test command to run only selected tests
    test_args = " ".join(f"--test {test}" for test in tests)
    full_command = f"{test_command} {test_args}"

    print(f"Running selected tests: {tests}")
    subprocess.run(full_command, shell=True)

if __name__ == '__main__':
    impact_file = os.environ.get('IMPACT_FILE', 'impact.json')

    # Your function-to-test mapping
    test_mapping = {
        'authenticate_user': ['test_auth.py::test_login', 'test_auth.py::test_logout'],
        'process_payment': ['test_payment.py', 'test_integration.py::test_payment_flow'],
        'validate_input': ['test_validation.py'],
        # Add more mappings...
    }

    selected_tests = select_tests(impact_file, test_mapping)
    run_selected_tests(selected_tests, "pytest")
```

### CI Integration with Test Selection

```yaml
name: Impact-Aware Testing
on: [pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Dependencies
        run: |
          pip install impactscope
          pip install -r test-requirements.txt

      - name: Run Impact Analysis
        run: |
          impactscope --repo-path . --commit ${{ github.sha }} \
                     --output json > impact.json

      - name: Select and Run Tests
        run: |
          python test_selector.py
        env:
          IMPACT_FILE: impact.json
```

## Notification and Alerting

### Slack Integration

```yaml
name: Impact Analysis with Slack Notification
on: [pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - name: Run Impact Analysis
        run: |
          impactscope --repo-path . --commit ${{ github.sha }} \
                     --output json > impact.json

      - name: Send Slack Notification
        if: always()
        uses: rtCamp/action-slack-notify@v2
        env:
          SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
          SLACK_MESSAGE: |
            Impact Analysis for ${{ github.event.pull_request.title }}

            Files impacted: $(jq '.files | length' impact.json)
            Functions changed: $(jq '[.files[].changed_functions | length] | add' impact.json)

            View details: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
```

### Email Notifications

```python
#!/usr/bin/env python3
# email_notifier.py

import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_impact_notification(impact_file, config):
    """Send email notification with impact analysis results."""

    with open(impact_file) as f:
        data = json.load(f)

    # Generate summary
    total_files = len(data['files'])
    total_changed = sum(len(f['changed_functions']) for f in data['files'])
    total_impacted = sum(len(f['downstream']) for f in data['files'])

    subject = f"Impact Analysis: {total_files} files, {total_changed} functions changed"

    body = f"""
    Impact Analysis Results

    Repository: {data.get('repo_path', 'Unknown')}
    Commit: {data.get('commit', 'Unknown')}
    Analysis Depth: {data.get('depth', 'Unknown')}

    Summary:
    - Files analyzed: {total_files}
    - Functions directly changed: {total_changed}
    - Functions impacted downstream: {total_impacted}

    Detailed results attached.
    """

    # Send email
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = config['from_email']
    msg['To'] = config['to_email']

    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(config['smtp_server']) as server:
        server.login(config['username'], config['password'])
        server.send_message(msg)

if __name__ == '__main__':
    # Configuration from environment
    config = {
        'smtp_server': os.environ['SMTP_SERVER'],
        'username': os.environ['SMTP_USERNAME'],
        'password': os.environ['SMTP_PASSWORD'],
        'from_email': os.environ['FROM_EMAIL'],
        'to_email': os.environ['TO_EMAIL']
    }

    send_impact_notification('impact.json', config)
```

## Advanced Configuration

### Configuration Files

```yaml
# impactscope-config.yml
analysis:
  depth: 2
  include_patterns:
    - "src/**/*.c"
    - "include/**/*.h"
  exclude_patterns:
    - "**/test/**"
    - "**/vendor/**"

quality_gates:
  max_impacted_functions: 50
  max_files: 10
  critical_patterns:
    - "auth_"
    - "security_"
    - "encrypt_"

notifications:
  slack_webhook: "${SLACK_WEBHOOK}"
  email_to: "dev-team@company.com"

test_mapping:
  authenticate_user: ["test_auth.py"]
  process_payment: ["test_payment.py", "test_integration.py"]
```

### Environment-Based Configuration

```bash
# Set configuration via environment variables
export IMPACTSCOPE_DEPTH=2
export IMPACTSCOPE_MAX_IMPACTED=50
export IMPACTSCOPE_CRITICAL_PATTERNS="auth,security,payment"

# Run with configuration
impactscope --repo-path . --commit HEAD --output json
```

## Monitoring and Metrics

### Collecting Metrics

```python
#!/usr/bin/env python3
# metrics_collector.py

import json
import time
from datetime import datetime

def collect_metrics(impact_file, run_id):
    """Collect and store impact analysis metrics."""

    with open(impact_file) as f:
        data = json.load(f)

    metrics = {
        'run_id': run_id,
        'timestamp': datetime.now().isoformat(),
        'repo_path': data.get('repo_path'),
        'commit': data.get('commit'),
        'depth': data.get('depth'),
        'files_analyzed': len(data['files']),
        'functions_changed': sum(len(f['changed_functions']) for f in data['files']),
        'functions_upstream': sum(len(f['upstream']) for f in data['files']),
        'functions_downstream': sum(len(f['downstream']) for f in data['files']),
        'analysis_time': time.time()  # Would need to be passed in
    }

    # Store metrics (could be database, file, monitoring system)
    with open(f'metrics-{run_id}.json', 'w') as f:
        json.dump(metrics, f, indent=2)

    return metrics

def generate_report(metrics_history):
    """Generate trend reports from metrics history."""

    # Calculate trends
    avg_files = sum(m['files_analyzed'] for m in metrics_history) / len(metrics_history)
    avg_functions = sum(m['functions_changed'] for m in metrics_history) / len(metrics_history)

    report = {
        'period': f"{metrics_history[0]['timestamp']} to {metrics_history[-1]['timestamp']}",
        'total_runs': len(metrics_history),
        'average_files_analyzed': avg_files,
        'average_functions_changed': avg_functions,
        'trends': 'stable'  # Could implement trend analysis
    }

    return report
```

## Best Practices

### Pipeline Organization

1. **Separate Analysis from Testing**: Run impact analysis before tests
2. **Fail Fast**: Stop pipeline on critical impact violations
3. **Parallel Execution**: Run impact analysis in parallel with other checks
4. **Caching**: Cache analysis results for similar commits

### Quality Gate Strategy

1. **Start Simple**: Begin with basic thresholds and refine over time
2. **Progressive Strictness**: Different rules for different branches
3. **False Positive Management**: Regularly review and adjust thresholds
4. **Stakeholder Communication**: Explain quality gates to the team

### Performance Optimization

1. **Incremental Analysis**: Analyze only changed files when possible
2. **Caching**: Cache parsed ASTs between runs
3. **Parallel Processing**: Use multiple cores for large codebases
4. **Selective Depth**: Use appropriate depth for different scenarios

### Monitoring and Alerting

1. **Track Metrics**: Monitor analysis performance and results over time
2. **Alert on Anomalies**: Set up alerts for unusual impact patterns
3. **Review Regularly**: Periodically review and update quality gates
4. **Team Communication**: Keep the team informed about impact analysis results

## Troubleshooting

### Common Issues

**Analysis Takes Too Long**
- Reduce depth or limit to specific directories
- Use incremental analysis for CI
- Cache results between runs

**Too Many False Positives**
- Adjust quality gate thresholds
- Add exclusion patterns for generated code
- Review and refine critical function patterns

**Integration Fails**
- Verify Python version compatibility
- Check file permissions for artifacts
- Ensure Git repository is accessible

**Quality Gates Too Strict/Restrictive**
- Start with higher thresholds and gradually lower them
- Review violations to understand patterns
- Involve team in setting appropriate limits

For detailed troubleshooting, see the [troubleshooting guide](troubleshooting.md).

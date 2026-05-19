#!/usr/bin/env bash
# PostToolUse hook: log_bash.sh
# Logs every Bash command (with exit code) to docs/hooks_log.txt.
#
# Legacy optional hook. This project is Codex-only and does not invoke Codex
# through a nested CLI command.
#
# Configuration:
#   PLAYBOOK_HOOKS_LOG   path to the log file (default: docs/hooks_log.txt)

set -euo pipefail

INPUT=$(cat)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
cmd = d.get('tool_input', {}).get('command', 'unknown')
print(cmd[:200])
" 2>/dev/null || echo "unknown")

EXIT_CODE=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('tool_response', {}).get('exit_code', '?'))
" 2>/dev/null || echo "?")

LOG_FILE="${PLAYBOOK_HOOKS_LOG:-docs/hooks_log.txt}"
mkdir -p "$(dirname "$LOG_FILE")"

# Status prefix
if [ "$EXIT_CODE" != "0" ] && [ "$EXIT_CODE" != "?" ]; then
  STATUS="FAIL"
else
  STATUS="    "
fi

# Task tag — set CURRENT_TASK env var in the orchestrator Execute block to annotate log lines
TASK_TAG="${CURRENT_TASK:-?}"

echo "[$TIMESTAMP] [TASK:${TASK_TAG}] EXIT=${EXIT_CODE}  ${STATUS}  ${COMMAND}" >> "$LOG_FILE"

exit 0

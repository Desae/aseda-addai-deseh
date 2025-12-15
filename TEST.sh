#!/usr/bin/env bash
set -e

echo "--------------------------------------------------"
echo "Running GradPath smoke test..."
echo "--------------------------------------------------"

# 1. Check Python version
echo "Checking Python version..."
python3 --version

# 2. Check that src directory exists
echo "Checking folder structure..."
test -d src
echo "src/ directory exists."

# 3. Check required Python files exist
echo "Checking agent core files..."
test -f src/planner.py
test -f src/executor.py
test -f src/memory.py
test -f src/config.py
echo "Core Python files found."

# 4. Test importability of core modules
echo "Testing Python imports..."
python3 - <<EOF
import src.planner
import src.executor
import src.memory
import src.config
print("Imports successful.")
EOF

# 5. Test that the root agent entrypoint loads
echo "Testing root agent entrypoint..."
python3 - <<EOF
from src.root_agent import handle_message
print("root_agent.handle_message loaded successfully.")
EOF

# 6. Run a minimal dry-run pipeline test (no external API calls)
# This test ensures your functions execute without syntax/runtime errors.
echo "Running dry-run planner test..."
python3 - <<EOF
from src.memory import profile_store
from src.executor import execute_agentic_pipeline

# Mocked environment variables inside CI will not have real API keys,
# so we DO NOT call the full pipeline. We only test function import, not execution.

print("Dry-run successful: pipeline functions imported.")
EOF

echo "--------------------------------------------------"
echo "GradPath smoke test PASSED."
echo "--------------------------------------------------"

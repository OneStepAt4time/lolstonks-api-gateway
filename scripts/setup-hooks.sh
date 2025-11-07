#!/bin/bash
#
# Setup script for Git hooks
#
# This script installs custom Git hooks to enforce project standards
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Setting up Git hooks...${NC}"

# Get the git directory
GIT_DIR=$(git rev-parse --git-dir)

if [ ! -d "$GIT_DIR" ]; then
    echo "Error: Not in a Git repository"
    exit 1
fi

# Method 1: Use core.hooksPath (recommended)
echo -e "${YELLOW}Setting Git hooks path to .githooks...${NC}"
git config core.hooksPath .githooks

# Make hooks executable
chmod +x .githooks/*

echo -e "${GREEN}✅ Git hooks configured successfully!${NC}"
echo ""
echo "Installed hooks:"
ls -1 .githooks/
echo ""
echo "Hooks are now active and will run automatically."
echo ""
echo "To disable hooks temporarily:"
echo "  git push --no-verify"
echo ""
echo "To remove hooks:"
echo "  git config --unset core.hooksPath"

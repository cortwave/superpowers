#!/bin/bash

set -ex

rm -rf ~/.config/opencode/superpowers

# skills
rm -rf ~/.config/opencode/skills
cp -r skills ~/.config/opencode/skills

# Copy OpenCode config
cp .opencode/opencode.jsonc ~/.config/opencode/opencode.jsonc

# Copy agents
rm -rf ~/.config/opencode/agents
cp -r agents ~/.config/opencode/agents

# Update agent placeholders and append instructions
./scripts/update-opencode-agents.sh

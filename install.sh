#!/usr/bin/env bash
set -euo pipefail

# Ultimate Best Seller Studio installer for macOS/Linux.
# Installs full skill folders, agents, and the knowledge base to ~/.claude/, plus
# the complete Better Humanizer (/humanizer-pro) from the git submodule.

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$REPO_DIR/skills"
KNOWLEDGE_DIR="$REPO_DIR/knowledge"
AGENTS_DIR="$REPO_DIR/agents"
HUMANIZER_DIR="$REPO_DIR/external/better-humanizer"
TARGET_SKILLS="$HOME/.claude/skills"
TARGET_KNOWLEDGE="$HOME/.claude/knowledge"
TARGET_AGENTS="$HOME/.claude/agents"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo -e "${BLUE}Ultimate Best Seller Studio${NC}"
echo -e "${YELLOW}File-backed book pipeline + measured human-band gate (Better Humanizer)${NC}"
echo ""

if [ ! -d "$SKILLS_DIR" ]; then
  echo -e "${RED}Error: skills/ directory not found. Run this script from the repository root.${NC}"
  exit 1
fi

# Make sure the Better Humanizer submodule is present (single source of truth).
if [ ! -f "$HUMANIZER_DIR/scripts/stylo.py" ]; then
  echo -e "${YELLOW}Better Humanizer submodule not initialized — fetching...${NC}"
  if git -C "$REPO_DIR" submodule update --init --recursive; then
    echo -e "  ${GREEN}+${NC} external/better-humanizer"
  else
    echo -e "  ${RED}!${NC} could not initialize the submodule (private repo? check access)."
    echo -e "  ${YELLOW}  /humanizer-pro will be installed as a pointer only.${NC}"
  fi
fi
echo ""

mkdir -p "$TARGET_SKILLS" "$TARGET_KNOWLEDGE" "$TARGET_AGENTS"

echo -e "${YELLOW}Installing skills, agents, and knowledge base${NC}"
count=0
for skill_dir in "$SKILLS_DIR"/*/; do
  skill_name=$(basename "$skill_dir")
  if [ -f "$skill_dir/SKILL.md" ]; then
    rm -rf "$TARGET_SKILLS/$skill_name"
    mkdir -p "$TARGET_SKILLS/$skill_name"
    cp -R "$skill_dir". "$TARGET_SKILLS/$skill_name/"
    echo -e "  ${GREEN}+${NC} $skill_name"
    count=$((count + 1))
  fi
done

# Overlay the COMPLETE Better Humanizer on top of the humanizer-pro bridge, so that
# /humanizer-pro in Claude Code is the full measured tool (scorer + corpora + judges),
# not just the in-repo pointer.
if [ -f "$HUMANIZER_DIR/SKILL.md" ]; then
  rm -rf "$TARGET_SKILLS/humanizer-pro"
  mkdir -p "$TARGET_SKILLS/humanizer-pro"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --exclude '.git' "$HUMANIZER_DIR"/ "$TARGET_SKILLS/humanizer-pro/"
  else
    cp -R "$HUMANIZER_DIR"/. "$TARGET_SKILLS/humanizer-pro/"
    rm -rf "$TARGET_SKILLS/humanizer-pro/.git"
  fi
  echo -e "  ${GREEN}+${NC} humanizer-pro ${BLUE}(full Better Humanizer)${NC}"
fi

kb_count=0
if [ -d "$KNOWLEDGE_DIR" ]; then
  for kb_file in "$KNOWLEDGE_DIR"/*.md; do
    if [ -f "$kb_file" ]; then
      cp "$kb_file" "$TARGET_KNOWLEDGE/"
      kb_count=$((kb_count + 1))
    fi
  done
fi

agent_count=0
if [ -d "$AGENTS_DIR" ]; then
  for agent_file in "$AGENTS_DIR"/*.md; do
    if [ -f "$agent_file" ]; then
      cp "$agent_file" "$TARGET_AGENTS/"
      agent_count=$((agent_count + 1))
    fi
  done
fi

echo ""
echo -e "${GREEN}Done.${NC} $count skills + $agent_count agents + $kb_count knowledge files installed"
echo ""
echo -e "Skills:    ${BLUE}$TARGET_SKILLS${NC}"
echo -e "Agents:    ${BLUE}$TARGET_AGENTS${NC}"
echo -e "Knowledge: ${BLUE}$TARGET_KNOWLEDGE${NC}"
echo ""
echo "Next: run  python3 -m runner.cli doctor  to confirm the checkout is ready."
echo "Then open Claude Code and type /book-genesis-codex to start writing,"
echo "or /humanizer-pro to measure and de-AI a chapter."
echo ""

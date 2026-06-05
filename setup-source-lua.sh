#!/bin/bash

REPO_URL="https://github.com/AzurLaneTools/AzurLaneLuaScripts.git"
TARGET_DIR="AzurLaneDataLua"

# Remove old
echo "Recreating $TARGET_DIR"
rm -rf "$TARGET_DIR"
mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR" || exit

# Init git
git init
git remote add origin "$REPO_URL"
git config core.sparseCheckout true
git config core.sparseCheckoutCone false

# Set required files
cat <<EOF >> .git/info/sparse-checkout
/CN/GameCfg/story/
/EN/GameCfg/story/
/JP/GameCfg/storyjp/
/KR/GameCfg/story/
/TW/GameCfg/story/
/CN/ShareCfg/ship_skin_template.lua
/EN/ShareCfg/ship_skin_template.lua
/JP/ShareCfg/ship_skin_template.lua
/KR/ShareCfg/ship_skin_template.lua
/TW/ShareCfg/ship_skin_template.lua
/CN/ShareCfg/memory_template.lua
/EN/ShareCfg/memory_template.lua
/JP/ShareCfg/memory_template.lua
/KR/ShareCfg/memory_template.lua
/TW/ShareCfg/memory_template.lua
/CN/ShareCfg/memory_group.lua
/EN/ShareCfg/memory_group.lua
/JP/ShareCfg/memory_group.lua
/KR/ShareCfg/memory_group.lua
/TW/ShareCfg/memory_group.lua
/CN/ShareCfg/name_code.lua
/EN/ShareCfg/name_code.lua
/JP/ShareCfg/name_code.lua
/KR/ShareCfg/name_code.lua
/TW/ShareCfg/name_code.lua
EOF

git pull --depth=1 origin main

COMMIT_ID=$(git rev-parse HEAD)
COMMIT_TIME=$(git log -1 --format=%cd --date=iso)
echo "Sauce Commit ID: $COMMIT_ID"
echo "Sauce Commit Time: $COMMIT_TIME"

cd ..
mkdir -p "output"
echo "$COMMIT_ID" > "output/commit_id.txt"
echo "$COMMIT_TIME" > "output/commit_time.txt"

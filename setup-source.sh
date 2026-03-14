#!/bin/bash

REPO_URL="https://github.com/AzurLaneTools/AzurLaneData.git"
TARGET_DIR="AzurLaneData"

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
/CN/GameCfg/story.json
/EN/GameCfg/story.json
/JP/GameCfg/storyjp.json
/KR/GameCfg/story.json
/TW/GameCfg/story.json
/CN/ShareCfg/ship_skin_template.json
/EN/ShareCfg/ship_skin_template.json
/JP/ShareCfg/ship_skin_template.json
/KR/ShareCfg/ship_skin_template.json
/TW/ShareCfg/ship_skin_template.json
/CN/ShareCfg/memory_template.json
/EN/ShareCfg/memory_template.json
/JP/ShareCfg/memory_template.json
/KR/ShareCfg/memory_template.json
/TW/ShareCfg/memory_template.json
/CN/ShareCfg/memory_group.json
/EN/ShareCfg/memory_group.json
/JP/ShareCfg/memory_group.json
/KR/ShareCfg/memory_group.json
/TW/ShareCfg/memory_group.json
/CN/ShareCfg/name_code.json
/EN/ShareCfg/name_code.json
/JP/ShareCfg/name_code.json
/KR/ShareCfg/name_code.json
/TW/ShareCfg/name_code.json
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

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
/CN/gamecfg/story/
/EN/gamecfg/story/
/JP/gamecfg/storyjp/
/KR/gamecfg/story/
/TW/gamecfg/story/
/CN/sharecfgdata/ship_skin_template.lua
/EN/sharecfgdata/ship_skin_template.lua
/JP/sharecfgdata/ship_skin_template.lua
/KR/sharecfgdata/ship_skin_template.lua
/TW/sharecfgdata/ship_skin_template.lua
/CN/sharecfg/memory_template.lua
/EN/sharecfg/memory_template.lua
/JP/sharecfg/memory_template.lua
/KR/sharecfg/memory_template.lua
/TW/sharecfg/memory_template.lua
/CN/sharecfg/memory_group.lua
/EN/sharecfg/memory_group.lua
/JP/sharecfg/memory_group.lua
/KR/sharecfg/memory_group.lua
/TW/sharecfg/memory_group.lua
/CN/sharecfg/name_code.lua
/EN/sharecfg/name_code.lua
/JP/sharecfg/name_code.lua
/KR/sharecfg/name_code.lua
/TW/sharecfg/name_code.lua
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

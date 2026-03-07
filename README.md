# AZL_ScriptSite

## Implementation

### Git Sparse checkout init

```bash
git clone --filter=blob:none --no-checkout https://github.com/AzurLaneTools/AzurLaneData.git
cd AzurLaneData
git sparse-checkout init --cone
git sparse-checkout set CN/GameCfg/story.json EN/GameCfg/story.json JP/GameCfg/storyjp.json KR/GameCfg/story.json TW/GameCfg/story.json                               CN/ShareCfg/ship_skin_template.json EN/ShareCfg/ship_skin_template.json JP/ShareCfg/ship_skin_template.json KR/ShareCfg/ship_skin_template.json TW/ShareCfg/ship_skin_template.json
git checkout main
```

#### to add new files/folders:

```bash
git sparse-checkout add <folder_name>
```

#### to update all files/folders:

```bash
git pull
```

## Data Sources

- [AzurLaneData by AzurLaneTools](https://github.com/AzurLaneTools/AzurLaneData)
- [Azur Lane Resources by Fernando2603](https://github.com/Fernando2603/AzurLane/tree/main)

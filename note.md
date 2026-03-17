# AZL_ScriptSite dev notes

## todo

- fix missing character img (e.g. story 338, character 900315 (ヘレナ(META), 900232 (オブザーバー))
- group timeline

## Terms

```
Group       |  [1, 2, ..., 298, ...]
↓                          ^^^
Memories    |  [3911, 3912, 3913, ..., 3923]
↓                     ^^^^
Stories     |  [..., MAIZANGYUBIANZHIHUA1, ...]
```

## check

```
(story.html?id=158)
(story.html?id=219)

吟ずる瑠璃の楽章 (story.html?id=215) Chap30 "記録の反撃" -> STORY=2110
軍神の帰還

CHAR=900236 (story.html?id=185)
CHAR=403036 (story.html?id=285)
CHAR=303190 雲仙 | factiontag  ワタツミの心 (story.html?id=257)

900232 オブザーバー & 900315 ヘレナ(META) (story.html?id=338)
```

## Implementation

### Git Sparse checkout init

```bash
git clone --filter=blob:none --no-checkout https://github.com/AzurLaneTools/AzurLaneData.git
cd AzurLaneData
git sparse-checkout init --cone
git sparse-checkout set "/CN/GameCfg/story.json" "/EN/GameCfg/story.json" "/JP/GameCfg/storyjp.json" "/KR/GameCfg/story.json" "/TW/GameCfg/story.json"
git sparse-checkout add "/CN/ShareCfg/ship_skin_template.json" "/EN/ShareCfg/ship_skin_template.json" "/JP/ShareCfg/ship_skin_template.json" "/KR/ShareCfg/ship_skin_template.json" "/TW/ShareCfg/ship_skin_template.json"
git sparse-checkout add "/CN/ShareCfg/memory_template.json" "/EN/ShareCfg/memory_template.json" "/JP/ShareCfg/memory_template.json" "/KR/ShareCfg/memory_template.json" "/TW/ShareCfg/memory_template.json"
git sparse-checkout add "/CN/ShareCfg/memory_group.json" "/EN/ShareCfg/memory_group.json" "/JP/ShareCfg/memory_group.json" "/KR/ShareCfg/memory_group.json" "/TW/ShareCfg/memory_group.json"
git sparse-checkout add "/CN/ShareCfg/name_code.json" "/EN/ShareCfg/name_code.json" "/JP/ShareCfg/name_code.json" "/KR/ShareCfg/name_code.json" "/TW/ShareCfg/name_code.json"
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

#### to reset

```bash
git sparse-checkout set
```

## Data Sources

- [AzurLaneData by AzurLaneTools](https://github.com/AzurLaneTools/AzurLaneData)
- [Azur Lane Resources by Fernando2603](https://github.com/Fernando2603/AzurLane/tree/main)
  - [bgm list](https://raw.githubusercontent.com/Fernando2603/AzurLane/main/bgm_link.json)
  - [skin list](https://raw.githubusercontent.com/Fernando2603/AzurLane/refs/heads/main/skin.json)
- [Azur Lane Utility on azurlane.nagami.moe](https://azurlane.nagami.moe/)
  - cdn

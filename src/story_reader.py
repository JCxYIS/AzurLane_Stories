import json
import os
import re

class StoryReader:
    def __init__(self, data_dir=None, region="JP"):
        # default read path: `../AzurLaneData`
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "AzurLaneData")
        self.data_dir = data_dir
        self.region = region
        story_filename = "storyjp.json" if region == "JP" else "story.json"
        
        self.story_filepath = os.path.join(data_dir, region, "GameCfg", story_filename)
        self.ship_skin_filepath = os.path.join(data_dir, region, "ShareCfg", "ship_skin_template.json")
        self.memory_group_filepath = os.path.join(data_dir, region, "ShareCfg", "memory_group.json")
        self.memory_template_filepath = os.path.join(data_dir, region, "ShareCfg", "memory_template.json")
        
        self.stories = {}
        self.skin_templates = {}
        self.memory_groups = {}
        self.memory_templates = {}
        self.name_codes = {}
        self._load_data()

    def _load_data(self):
        try:
            with open(self.story_filepath, 'r', encoding='utf-8') as f:
                self.stories = json.load(f)
            
            with open(self.ship_skin_filepath, 'r', encoding='utf-8') as f:
                self.skin_templates = json.load(f)
                
            with open(self.memory_group_filepath, 'r', encoding='utf-8') as f:
                self.memory_groups = json.load(f)
                
            with open(self.memory_template_filepath, 'r', encoding='utf-8') as f:
                self.memory_templates = json.load(f)
                
            name_code_filepath = os.path.join(self.data_dir, self.region, "ShareCfg", "name_code.json")
            if os.path.exists(name_code_filepath):
                with open(name_code_filepath, 'r', encoding='utf-8') as f:
                    self.name_codes = json.load(f)
                    
        except Exception as e:
            print(f"Error loading JSON data for {self.region}: {e}")

    def get_parsed_stories(self):
        """
        Parses memory_group and memory_template to organize stories.
        Returns a dict: { story_group_title: { chapter_title: [scripts...] } }
        Maintains order based on memory_group definitions.
        """
        parsed = {}
        used_stories = set()
        
        # We need to sort groups by integer ID or they will be random from JSON
        # Most of the IDs are numbers, so we try numeric sort first.
        sorted_group_keys = sorted(self.memory_groups.keys(), key=lambda k: int(k) if k.isdigit() else float('inf'))

        for g_id in sorted_group_keys:
            group_data = self.memory_groups[g_id]
            group_title = group_data.get('title', f"Group_{g_id}")
            
            # Avoid empty keys in dicts just in case, though they usually have a title
            if not group_title:
                group_title = f"Group_{g_id}"
            group_title = self.replace_namecodes(group_title)
                
            memories = group_data.get('memories', [])
            
            chapters_dict = {}
            for mem_id in memories:
                mem_key = str(mem_id)
                template_data = self.memory_templates.get(mem_key)
                if not template_data:
                    continue
                    
                chapter_title = template_data.get('title', f"Memory_{mem_id}")
                chapter_title = self.replace_namecodes(chapter_title)
                story_ref = str(template_data.get('story', "NON_EXISTENT")).lower()
                
                # The story mapping often uses lowercase keys in `story.json`
                if story_ref in self.stories:
                    val = self.stories[story_ref]
                    if isinstance(val, dict) and 'scripts' in val:
                        chapters_dict[chapter_title] = val['scripts']
                        used_stories.add(story_ref)

            # Cleanup empty groups
            if not chapters_dict:
                continue
                
            # Use the icon from the first valid memory_template chapter as the group icon, or fallback to group_data.icon
            first_mem_icon = None
            for mem_id in memories:
                tmpl = self.memory_templates.get(str(mem_id))
                if tmpl and tmpl.get("icon"):
                    first_mem_icon = tmpl["icon"]
                    break
            group_icon = first_mem_icon or group_data.get("icon", "title_event")

            parsed[str(g_id)] = {
                "title": group_title,
                "type": group_data.get("type", 0),
                "subtype": group_data.get("subtype", 0),
                "icon": group_icon,
                "chapters": chapters_dict
            }

        # Handle Orphans
        orphan_group_title = "non-archived"
        parsed["non-archived"] = {
            "title": orphan_group_title,
            "type": "non-archived",
            "chapters": {}
        }
        
        for story_key, val in self.stories.items():
            if not isinstance(val, dict) or 'scripts' not in val:
                continue
                
            # Exclude primarily numeric keys like 1, 2, 3 as they are usually irrelevant fragments if not linked
            if story_key.isdigit():
                continue
                
            if story_key.lower() not in used_stories:
                # Use the key itself as the chapter title
                chapter_title = story_key
                parsed["non-archived"]["chapters"][chapter_title] = val['scripts']
                
        if not parsed["non-archived"]["chapters"]:
            del parsed["non-archived"]
            
        return parsed

    def resolve_actor_name(self, actor_id):
        """Resolves a numeric actor ID using ship_skin_template.json"""
        actor_id_str = str(actor_id)

        # given id not found in dict: return the id directly
        if actor_id_str not in self.skin_templates:
            return actor_id_str
        
        # fetch from dict: this could be real name or skin name
        actor_rawname = self.skin_templates[actor_id_str].get('name', actor_id_str)

        # usually XXXXX0 is the ship real name, we can validate their ship_group
        # if the actor_group is the same as the actor_id_endwith0_group, then use the name of the actor_id_endwith0_str
        actor_id_endwith0_str = actor_id_str[:-1] + "0"
        if actor_id_endwith0_str in self.skin_templates:
            actor_group = self.skin_templates[actor_id_str]['ship_group']        
            actor_id_endwith0_group = self.skin_templates[actor_id_endwith0_str]['ship_group']
            if actor_group == actor_id_endwith0_group:
                actor_id_endwith0_rawname = self.skin_templates[actor_id_endwith0_str]['name']
                actor_name = self.resolve_actor_name(actor_id_endwith0_rawname)
                actor_skin_name = self.resolve_actor_name(actor_rawname)
                # "NAME [SKIN_NAME]"
                return f'{actor_name} [{actor_skin_name}]' if actor_name != actor_skin_name else actor_name
        # otherwise return the name of the actor_id_str
        return self.resolve_actor_name(actor_rawname)

    def replace_namecodes(self, text: str) -> str:
        """Replaces {namecode:XX(:XXXX)} with the actual character name from name_code.json"""
        if not text or not isinstance(text, str):
            return text
            
        def replacer(match):
            code_id = match.group(1)
            if code_id in self.name_codes:
                return self.name_codes[code_id].get('name', match.group(0))
            return match.group(0)
            
        return re.sub(r'\{namecode:(\d+)(:.+)*\}', replacer, text)



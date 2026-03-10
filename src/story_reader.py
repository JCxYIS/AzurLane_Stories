import json
import re
import os

class StoryReader:
    def __init__(self, data_dir="f:/AZL_ScriptSite/AzurLaneData", region="JP"):
        self.data_dir = data_dir
        self.region = region
        story_filename = "storyjp.json" if region == "JP" else "story.json"
        self.story_filepath = os.path.join(data_dir, region, "GameCfg", story_filename)
        self.ship_skin_filepath = os.path.join(data_dir, region, "ShareCfg", "ship_skin_template.json")
        self.stories = {}
        self.skin_templates = {}
        self._load_data()

    def _load_data(self):
        try:
            with open(self.story_filepath, 'r', encoding='utf-8') as f:
                self.stories = json.load(f)
            
            with open(self.ship_skin_filepath, 'r', encoding='utf-8') as f:
                self.skin_templates = json.load(f)
        except Exception as e:
            print(f"Error loading JSON data: {e}")

    def get_parsed_stories(self):
        """
        Parses keys into (story_group, chapter).
        Returns a dict: { story_group: { chapter: [scripts...] } }
        """
        parsed = {}
        
        # Regex to split key into words and trailing numbers.
        pattern = re.compile(r'^([a-zA-Z_]+)(\d*)$')

        for key, val in self.stories.items():
            # Skip keys with no scripts or purely numerical IDs
            if not isinstance(val, dict) or 'scripts' not in val:
                continue
            
            if key.isdigit():
                continue # Skip pure numbers as requested

            match = pattern.match(key)
            if match:
                group = match.group(1)
                chapter = match.group(2)
                
                # If chapter is empty string, just default to '1' or the name itself?
                if not chapter:
                    chapter = "1"
                    
                if group not in parsed:
                    parsed[group] = {}
                
                parsed[group][chapter] = val['scripts']
            else:
                # Fallback if no match (should be rare)
                group = key
                chapter = "1"
                if group not in parsed:
                    parsed[group] = {}
                parsed[group][chapter] = val['scripts']

        return parsed

    def resolve_actor_name(self, actor_id):
        """Resolves a numeric actor ID using ship_skin_template.json"""
        actor_str = str(actor_id)
        
        # Direct match in the skin templates
        if actor_str in self.skin_templates:
            return self.skin_templates[actor_str].get('name', actor_str)
            
        return actor_str


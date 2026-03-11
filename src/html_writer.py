import os
import json
import shutil
import re

class HtmlWriter:
    def __init__(self, output_dir=None):
        # default output path: `../output/stories/`
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "stories")
        self.output_dir = output_dir
        self.template_dir = os.path.join(os.path.dirname(__file__), "template")
        self.root_output_dir = os.path.dirname(self.output_dir)

    def generate_stories(self, aggregated_stories, story_readers_by_region, overwrite=False):
        """
        aggregated_stories: { group_id: { "titles": {region: title}, "regions": { region: { chapter: [scripts...] } } } }
        story_readers_by_region: { "EN": StoryReaderObject, "JP": StoryReaderObject, ... }
        """
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 1. Copy the template directory to the root output dir
        self._copy_template(overwrite)
        
        # 2. Write global groups.json
        self._write_groups_json(aggregated_stories)
        
        # 3. Write individual story data.json
        for group_id, group_data in aggregated_stories.items():
            group_dir = os.path.join(self.output_dir, str(group_id))
            os.makedirs(group_dir, exist_ok=True)
            data_filepath = os.path.join(group_dir, "data.json")
            
            if os.path.exists(data_filepath) and not overwrite:
                print(f"Skipping JSON generation for {data_filepath} (already exists)")
                continue
                
            self._write_group_data(data_filepath, str(group_id), group_data, story_readers_by_region)

    def _copy_template(self, overwrite):
        """Copies the static HTML/CSS/JS template files to the output root."""
        # Ensure root output directory exists
        os.makedirs(self.root_output_dir, exist_ok=True)

        # Copy index.html
        shutil.copy2(os.path.join(self.template_dir, "index.html"), os.path.join(self.root_output_dir, "index.html"))
        
        # Copy story.html into stories/
        shutil.copy2(os.path.join(self.template_dir, "story.html"), os.path.join(self.root_output_dir, "story.html"))
        
        # Copy css and js folders
        for folder in ["css", "js"]:
            src_folder = os.path.join(self.template_dir, folder)
            dst_folder = os.path.join(self.root_output_dir, folder)
            if os.path.exists(dst_folder):
                if overwrite:
                    shutil.rmtree(dst_folder)
                    shutil.copytree(src_folder, dst_folder)
            else:
                shutil.copytree(src_folder, dst_folder)
                
        print("Copied static SPA templates.")

    def _write_groups_json(self, aggregated_stories):
        """Writes the lightweight groups.json for the global index logic."""
        groups_data = {}
        for g_id, data in aggregated_stories.items():
            groups_data[str(g_id)] = {
                "titles": data.get("titles", {}),
                "type": data.get("type", "Unknown")
            }
            
        data_dir = os.path.join(self.root_output_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        filepath = os.path.join(data_dir, "groups.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(groups_data, f, ensure_ascii=False)
        print(f"Generated global groups.json: {filepath}")

    def _write_group_data(self, filepath, group_id, group_data, story_readers_by_region):
        """Writes the specific data.json for an individual story viewer."""
        regions_data = group_data.get("regions", {})
        titles_data = group_data.get("titles", {})
        
        processed_data = {}
        for region, chapters in regions_data.items():
            processed_data[region] = {}
            for chapter, scripts in chapters.items():
                processed_scripts = []
                for s in scripts:
                    ps = {}
                    
                    if not isinstance(s, dict):
                        continue
                    
                    if s.get('bgm'): ps['bgm'] = s['bgm']
                    if s.get('stopbgm'): ps['stopbgm'] = True
                    if s.get('bgName'): ps['bgName'] = s['bgName']
                    
                    reader = story_readers_by_region.get(region)
                    
                    if s.get('sequence'):
                        seq_text = []
                        for seq in s['sequence']:
                            if isinstance(seq, list) and len(seq) > 0:
                                stxt = seq[0]
                                if reader:
                                    stxt = reader.replace_namecodes(stxt)
                                stxt = re.sub(
                                    r'<size=(\d+)>(.*?)</size>',
                                    lambda m: f'<span style="font-size: {int(m.group(1))/60.0:.3f}em;">{m.group(2)}</span>',
                                    stxt,
                                    flags=re.IGNORECASE|re.DOTALL
                                )
                                seq_text.append(stxt)
                        if seq_text:
                            ps['sequence'] = seq_text
                    
                    # Say
                    if 'say' in s:
                        ps['say'] = str(s['say']).replace('\\n', '<br>')
                        
                        if reader:
                            ps['say'] = reader.replace_namecodes(ps['say'])
                            
                        # Parse <size=XX> tags
                        ps['say'] = re.sub(
                            r'<size=(\d+)>(.*?)</size>',
                            lambda m: f'<span style="font-size: {int(m.group(1))/60.0:.3f}em;">{m.group(2)}</span>',
                            ps['say'],
                            flags=re.IGNORECASE|re.DOTALL
                        )
                            
                        if 'actor' in s or 'actorName' in s:
                            actor_name = ""
                            if 'actorName' in s:
                                actor_name = str(s['actorName'])
                            elif 'actor' in s:
                                actor_id = s['actor']
                                if reader and (isinstance(actor_id, int) or (isinstance(actor_id, str) and actor_id.isdigit())):
                                    actor_name = reader.resolve_actor_name(actor_id)
                                else:
                                    actor_name = str(actor_id)
                            
                            if reader:
                                actor_name = reader.replace_namecodes(actor_name)
                                
                            actor_name = re.sub(
                                r'<size=(\d+)>(.*?)</size>',
                                lambda m: f'<span style="font-size: {int(m.group(1))/60.0:.3f}em;">{m.group(2)}</span>',
                                actor_name,
                                flags=re.IGNORECASE|re.DOTALL
                            )
                                
                            ps['actorName'] = actor_name
                            
                            if 'nameColor' in s:
                                ps['nameColor'] = s['nameColor']
                        else:
                            ps['narration'] = True
                            
                    processed_scripts.append(ps)
                
                chap_key = chapter if chapter else "1"
                processed_data[region][chap_key] = processed_scripts

        # Combine titles and regions into a single JSON object
        final_payload = {
            "titles": titles_data,
            "regions": processed_data
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(final_payload, f, ensure_ascii=False)
        print(f"Generated story data: {filepath}")

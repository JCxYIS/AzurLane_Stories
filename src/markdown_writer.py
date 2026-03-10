import os

class MarkdownWriter:
    def __init__(self, output_dir="f:/AZL_ScriptSite/output/stories"):
        self.output_dir = output_dir

    def sanitize_filename(self, filename):
        # Keep things simple for now, remove invalid chars if needed
        return "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).rstrip()

    def generate_stories(self, parsed_stories, story_reader, overwrite=False):
        """
        parsed_stories: { story_group: { chapter: [scripts...] } }
        story_reader: instance of StoryReader needed to resolve actors
        """
        region = getattr(story_reader, "region", "JP").lower()
        region_upper = region.upper()
        
        index_lines = [f"# Azur Lane {region_upper} Stories\n"]
        
        for group, chapters in parsed_stories.items():
            group_dir = os.path.join(self.output_dir, group, region)
            os.makedirs(group_dir, exist_ok=True)
            
            index_lines.append(f"- [{group}](./stories/{group}/{region}/)\n")
            
            for chapter, scripts in chapters.items():
                
                # Check chapter name sanity
                chapter_filename = f"{chapter}.md"
                # Some chapter string might be empty if regex fails
                if not chapter:
                    chapter_filename = "1.md"
                    
                filepath = os.path.join(group_dir, chapter_filename)
                
                if os.path.exists(filepath) and not overwrite:
                    print(f"Skipping {filepath} (already exists and overwrite is False)")
                    continue
                    
                self._write_chapter(filepath, scripts, story_reader)

        # Write global index
        os.makedirs(self.output_dir, exist_ok=True)
        index_filepath = os.path.join(os.path.dirname(self.output_dir), f"index_{region}.md")
        with open(index_filepath, 'w', encoding='utf-8') as f:
            f.writelines(index_lines)
            
    def _write_chapter(self, filepath, scripts, story_reader):
        with open(filepath, 'w', encoding='utf-8') as f:
            for s in scripts:
                # 1. BGM
                if 'bgm' in s and s['bgm']:
                    f.write(f"> BGM: {s['bgm']}\n\n")
                
                if 'stopbgm' in s and s['stopbgm']:
                    f.write(f"> BGM Stopped\n\n")
                    
                # 2. Background
                if 'bgName' in s and s['bgName']:
                    f.write(f"> Background: {s['bgName']}\n\n")
                    
                # 3. Sequence (intro text)
                if 'sequence' in s and isinstance(s['sequence'], list):
                    f.write("...\n")
                    for seq in s['sequence']:
                        if isinstance(seq, list) and len(seq) > 0:
                            f.write(f"_{seq[0]}_\n")
                    f.write("...\n\n")

                # 4. Dialogue / Narration
                if 'say' in s:
                    text = s['say'].replace('\n', '<br>')
                    
                    if 'actor' in s or 'actorName' in s:
                        # Character speaking
                        actor_name = ""
                        
                        if 'actorName' in s:
                            actor_name = str(s['actorName'])
                        elif 'actor' in s:
                            actor_id = s['actor']
                            if isinstance(actor_id, int) or (isinstance(actor_id, str) and actor_id.isdigit()):
                                actor_name = story_reader.resolve_actor_name(actor_id)
                            else:
                                actor_name = str(actor_id)
                                
                        # Handle color
                        if 'nameColor' in s:
                            color = s['nameColor']
                            f.write(f"**<span style='color:{color}'>{actor_name}</span>**: {text}\n\n")
                        else:
                            f.write(f"**{actor_name}**: {text}\n\n")
                    else:
                        # Narration
                        f.write(f"_{text}_\n\n")
        print(f"Generated {filepath}")


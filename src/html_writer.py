import os
import json
import html

class HtmlWriter:
    def __init__(self, output_dir="f:/AZL_ScriptSite/output/stories"):
        self.output_dir = output_dir

    def generate_stories(self, aggregated_stories, story_readers_by_region, overwrite=False):
        """
        aggregated_stories: { group_id: { "titles": {region: title}, "regions": { region: { chapter: [scripts...] } } } }
        story_readers_by_region: { "EN": StoryReaderObject, "JP": StoryReaderObject, ... }
        """
        # Global index
        os.makedirs(self.output_dir, exist_ok=True)
        index_filepath = os.path.join(os.path.dirname(self.output_dir), "index.html")
        
        self._write_global_index(index_filepath, aggregated_stories)
        
        # Write individual group pages
        for group_id, group_data in aggregated_stories.items():
            group_dir = os.path.join(self.output_dir, str(group_id))
            os.makedirs(group_dir, exist_ok=True)
            page_filepath = os.path.join(group_dir, "index.html")
            
            if os.path.exists(page_filepath) and not overwrite:
                print(f"Skipping HTML generation for {page_filepath} (already exists)")
                continue
                
            self._write_group_page(page_filepath, str(group_id), group_data, story_readers_by_region)

    def _write_global_index(self, filepath, aggregated_stories):
        # Extract titles for JS
        groups_data = {}
        for g_id, data in aggregated_stories.items():
            groups_data[str(g_id)] = {
                "titles": data.get("titles", {}),
                "type": data.get("type", "Unknown")
            }
            
        json_groups = json.dumps(groups_data, ensure_ascii=False)
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Azur Lane Stories</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f9;
            color: #333;
        }}
        h1 {{
            text-align: left;
            margin-bottom: 10px;
        }}
        .header-controls {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 2px solid #ccc;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}
        .tabs {{
            display: flex;
            gap: 15px;
        }}
        .tab-btn {{
            background: none;
            border: none;
            font-size: 1.1em;
            font-weight: bold;
            color: #777;
            cursor: pointer;
            padding: 5px 10px;
            transition: color 0.2s;
        }}
        .tab-btn.active {{
            color: #000;
            border-bottom: 3px solid #000;
        }}
        .tab-btn:hover {{ color: #000; }}
        
        .sections-container {{
            display: flex;
            flex-direction: column;
        }}
        .type-section {{
            margin-bottom: 40px;
        }}
        .type-header {{
            border-bottom: 2px solid #ddd;
            padding-bottom: 8px;
            margin-bottom: 20px;
            color: #444;
            font-size: 1.5em;
            font-weight: bold;
        }}
        .grid-container {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
        }}
        .card {{
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
            text-decoration: none;
            color: inherit;
            transition: transform 0.2s, box-shadow 0.2s;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-bottom: 15px;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.15);
        }}
        .card-img-placeholder {{
            width: 100%;
            height: 120px;
            background-color: #e0e0e0;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #888;
            font-size: 0.9em;
            margin-bottom: 15px;
        }}
        .card-title {{
            font-weight: bold;
            text-align: center;
            font-size: 1.1em;
            padding: 0 10px;
            word-wrap: break-word;
            width: 100%;
            box-sizing: border-box;
        }}
    </style>
</head>
<body>
    <div class="header-controls">
        <h1>Azur Lane Stories</h1>
        <div class="tabs" id="region-tabs"></div>
    </div>
    
    <div class="sections-container" id="sections-container">
    </div>

    <script id="groups-data" type="application/json">
        {json_groups}
    </script>

    <script>
        const groupsData = JSON.parse(document.getElementById('groups-data').textContent);
        const regionTabsContainer = document.getElementById('region-tabs');
        const sectionsContainer = document.getElementById('sections-container');
        
        const regionOrder = ["EN", "CN", "JP", "KR", "TW"];
        let currentRegion = "JP"; // Default
        
        // Define human readable form for types
        const typeNames = {{
            "1": "Main Story",
            "2": "Event",
            "Orphan": "Orphans"
        }};
        
        // Find all available regions across all titles
        let allRegionsSet = new Set();
        Object.values(groupsData).forEach(data => {{
            Object.keys(data.titles).forEach(r => allRegionsSet.add(r));
        }});
        
        let availableRegions = Array.from(allRegionsSet).sort((a,b) => {{
            let ia = regionOrder.indexOf(a), ib = regionOrder.indexOf(b);
            if(ia === -1) ia = 99; if(ib === -1) ib = 99;
            return ia - ib;
        }});

        function init() {{
            if(availableRegions.length > 0) {{
                // Prefer JP or EN if available
                if(availableRegions.includes("EN")) currentRegion = "EN";
                if(availableRegions.includes("JP")) currentRegion = "JP";
            }}
            renderRegionTabs();
            selectRegion(currentRegion);
        }}

        function renderRegionTabs() {{
            regionTabsContainer.innerHTML = '';
            availableRegions.forEach(region => {{
                const btn = document.createElement('button');
                btn.className = 'tab-btn';
                btn.textContent = region;
                btn.onclick = () => selectRegion(region);
                if (region === currentRegion) btn.classList.add('active');
                regionTabsContainer.appendChild(btn);
            }});
        }}

        function selectRegion(region) {{
            currentRegion = region;
            
            Array.from(regionTabsContainer.children).forEach(btn => {{
                btn.classList.toggle('active', btn.textContent === region);
            }});
            
            renderGrid();
        }}

        function renderGrid() {{
            sectionsContainer.innerHTML = '';
            
            // Group by type
            let typeMap = {{}};
            Object.keys(groupsData).forEach(g_id => {{
                const data = groupsData[g_id];
                const t = data.type;
                if(!typeMap[t]) typeMap[t] = [];
                typeMap[t].push(g_id);
            }});
            
            let sortedTypes = Object.keys(typeMap).sort((a,b) => {{
                if (a === "Orphan") return 1;
                if (b === "Orphan") return -1;
                return parseInt(a) - parseInt(b);
            }});
            
            sortedTypes.forEach(type => {{
                const section = document.createElement("div");
                section.className = "type-section";
                
                const header = document.createElement("div");
                header.className = "type-header";
                header.textContent = typeNames[type] || `Type ${{type}}`;
                section.appendChild(header);
                
                const grid = document.createElement("div");
                grid.className = "grid-container";
                
                let sortedKeys = typeMap[type].sort((a,b) => parseInt(a) - parseInt(b));
                sortedKeys.forEach(g_id => {{
                    const titles = groupsData[g_id].titles;
                    let displayTitle = titles[currentRegion] || titles["JP"] || titles["EN"] || Object.values(titles)[0] || g_id;
                    
                    const card = document.createElement("a");
                    card.href = `./stories/${{g_id}}/index.html`;
                    card.className = "card";
                    card.innerHTML = `
                        <div class="card-img-placeholder">Image Placeholder</div>
                        <div class="card-title">${{displayTitle}}</div>
                    `;
                    grid.appendChild(card);
                }});
                
                section.appendChild(grid);
                sectionsContainer.appendChild(section);
            }});
        }}

        init();
    </script>
</body>
</html>
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Generated global index HTML: {filepath}")

    def _write_group_page(self, filepath, group_id, group_data, story_readers_by_region):
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
                    
                    if s.get('sequence'):
                        seq_text = []
                        for seq in s['sequence']:
                            if isinstance(seq, list) and len(seq) > 0:
                                seq_text.append(seq[0])
                        if seq_text:
                            ps['sequence'] = seq_text
                    
                    # Say
                    if 'say' in s:
                        ps['say'] = str(s['say']).replace('\\n', '<br>')
                        
                        reader = story_readers_by_region.get(region)
                        if reader:
                            ps['say'] = reader.replace_namecodes(ps['say'])
                            
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
                                
                            ps['actorName'] = actor_name
                            
                            if 'nameColor' in s:
                                ps['nameColor'] = s['nameColor']
                        else:
                            ps['narration'] = True
                            
                    processed_scripts.append(ps)
                
                chap_key = chapter if chapter else "1"
                processed_data[region][chap_key] = processed_scripts

        json_data = json.dumps(processed_data, ensure_ascii=False)
        json_titles = json.dumps(titles_data, ensure_ascii=False)
        
        # Initial title (fallback to JP/EN/whatever is there)
        display_title = titles_data.get("JP") or titles_data.get("EN") or (list(titles_data.values())[0] if titles_data else group_id)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Story: {display_title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0; padding: 20px;
            background-color: #fafafa;
            color: #333;
        }}
        .header {{
            margin-bottom: 20px;
        }}
        h1 {{ margin: 0 0 10px 0; }}
        
        .tabs {{
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            border-bottom: 2px solid #ddd;
            padding-bottom: 5px;
            flex-wrap: wrap;
        }}
        .tab-btn {{
            background: none;
            border: none;
            font-size: 1.2em;
            font-weight: bold;
            color: #777;
            cursor: pointer;
            padding: 5px 10px;
            transition: color 0.2s;
        }}
        .tab-btn.active {{
            color: #000;
            border-bottom: 3px solid #000;
        }}
        .tab-btn:hover {{ color: #000; }}
        
        .chapter-tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 1px solid #ccc;
            padding-bottom: 10px;
            flex-wrap: wrap;
        }}
        .chapter-btn {{
            background: none;
            border: none;
            font-size: 1em;
            color: #0066cc;
            cursor: pointer;
            padding: 5px;
        }}
        .chapter-btn.active {{
            font-weight: bold;
            color: #004499;
            text-decoration: underline;
        }}
        .chapter-btn:hover {{ text-decoration: underline; }}
        
        .story-content {{
            max-width: 800px;
            line-height: 1.6;
            font-size: 1.1em;
        }}
        
        .bgm-change, .bg-change {{
            color: #888;
            font-size: 0.9em;
            margin: 10px 0;
            font-style: italic;
            background-color: #f0f0f0;
            padding: 5px 10px;
            border-radius: 5px;
            display: inline-block;
        }}
        
        .sequence {{
            margin: 20px 0;
            font-style: italic;
            color: #555;
            text-align: center;
        }}
        
        .dialogue-box {{
            margin-bottom: 15px;
        }}
        
        .actor-name {{
            font-weight: bold;
            margin-bottom: 2px;
        }}
        
        .narration {{
            font-style: italic;
            margin-bottom: 15px;
            color: #444;
        }}
        
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            text-decoration: none;
            color: #0066cc;
        }}
        .back-link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <a href="../../index.html" class="back-link">← Back to Index</a>
    <div class="header">
        <h1><span id="story-title">{display_title}</span></h1>
        <div class="tabs" id="region-tabs"></div>
        <div class="chapter-tabs" id="chapter-tabs"></div>
    </div>
    
    <div class="story-content" id="story-content">
        <!-- Story content injected here -->
    </div>

    <script id="story-data" type="application/json">
        {json_data}
    </script>
    <script id="titles-data" type="application/json">
        {json_titles}
    </script>

    <script>
        const storyData = JSON.parse(document.getElementById('story-data').textContent);
        const titlesData = JSON.parse(document.getElementById('titles-data').textContent);
        const regionTabsContainer = document.getElementById('region-tabs');
        const chapterTabsContainer = document.getElementById('chapter-tabs');
        const contentContainer = document.getElementById('story-content');
        
        let currentRegion = null;
        let currentChapter = null;
        
        // Define region order visually
        const regionOrder = ["EN", "CN", "JP", "KR", "TW"];
        let availableRegions = Object.keys(storyData).sort((a,b) => {{
            let ia = regionOrder.indexOf(a), ib = regionOrder.indexOf(b);
            if(ia === -1) ia = 99; if(ib === -1) ib = 99;
            return ia - ib;
        }});

        function init() {{
            if (availableRegions.length === 0) return;
            currentRegion = availableRegions[0];
            
            renderRegionTabs();
            selectRegion(currentRegion);
        }}
        
        function renderRegionTabs() {{
            regionTabsContainer.innerHTML = '';
            availableRegions.forEach(region => {{
                const btn = document.createElement('button');
                btn.className = 'tab-btn';
                btn.textContent = region;
                btn.onclick = () => selectRegion(region);
                if (region === currentRegion) btn.classList.add('active');
                regionTabsContainer.appendChild(btn);
            }});
        }}
        
        function selectRegion(region) {{
            currentRegion = region;
            
            // Update title
            const titleElem = document.getElementById('story-title');
            if(titleElem && titlesData[region]) {{
                titleElem.textContent = titlesData[region];
                document.title = "Story: " + titlesData[region];
            }}
            
            // Update active state on RegionTabs
            Array.from(regionTabsContainer.children).forEach(btn => {{
                btn.classList.toggle('active', btn.textContent === region);
            }});
            
            // Re-render chapters for this region
            renderChapterTabs();
            
            const chapters = Object.keys(storyData[region]);
            // Attempt to keep same chapter index if possible, else default to first chapter
            if (!chapters.includes(currentChapter)) {{
                currentChapter = chapters[0];
            }}
            selectChapter(currentChapter);
        }}
        
        function renderChapterTabs() {{
            chapterTabsContainer.innerHTML = '';
            if(!storyData[currentRegion]) return;
            
            // Use the JSON keys exactly in the order they were inserted by Python dict
            const chapters = Object.keys(storyData[currentRegion]);
            
            chapters.forEach(chapter => {{
                const btn = document.createElement('button');
                btn.className = 'chapter-btn';
                btn.textContent = chapter;
                btn.onclick = () => selectChapter(chapter);
                if (chapter === currentChapter) btn.classList.add('active');
                chapterTabsContainer.appendChild(btn);
            }});
        }}
        
        function selectChapter(chapter) {{
            currentChapter = chapter;
            
            Array.from(chapterTabsContainer.children).forEach(btn => {{
                btn.classList.toggle('active', btn.textContent === chapter);
            }});
            
            renderContent();
        }}
        
        function renderContent() {{
            contentContainer.innerHTML = '';
            const scripts = storyData[currentRegion][currentChapter];
            if (!scripts) return;
            
            scripts.forEach(s => {{
                if (s.bgm) {{
                    const div = document.createElement('div');
                    div.className = 'bgm-change';
                    div.textContent = '▶ BGM: ' + s.bgm;
                    contentContainer.appendChild(div);
                }}
                if (s.stopbgm) {{
                    const div = document.createElement('div');
                    div.className = 'bgm-change';
                    div.textContent = '⏸ BGM Stopped';
                    contentContainer.appendChild(div);
                }}
                if (s.bgName) {{
                    const div = document.createElement('div');
                    div.className = 'bg-change';
                    div.textContent = '🖼 Background: ' + s.bgName;
                    contentContainer.appendChild(div);
                }}
                if (s.sequence) {{
                    const div = document.createElement('div');
                    div.className = 'sequence';
                    s.sequence.forEach(line => {{
                        const p = document.createElement('div');
                        p.textContent = line;
                        div.appendChild(p);
                    }});
                    contentContainer.appendChild(div);
                }}
                
                if (s.say) {{
                    if (s.narration) {{
                        const div = document.createElement('div');
                        div.className = 'narration';
                        div.innerHTML = s.say;
                        contentContainer.appendChild(div);
                    }} else {{
                        const box = document.createElement('div');
                        box.className = 'dialogue-box';
                        
                        const nameDiv = document.createElement('div');
                        nameDiv.className = 'actor-name';
                        if (s.nameColor) {{
                            nameDiv.style.color = s.nameColor;
                        }}
                        nameDiv.textContent = s.actorName;
                        
                        const textDiv = document.createElement('div');
                        textDiv.innerHTML = s.say;
                        
                        box.appendChild(nameDiv);
                        box.appendChild(textDiv);
                        contentContainer.appendChild(box);
                    }}
                }}
            }});
        }}
        
        init();
    </script>
</body>
</html>
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Generated HTML story page: {filepath}")


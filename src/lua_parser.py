import os
import re
import luadata
import luadata.io.read

def _patched_read_string(self):
    buffer = ""
    self.read_trim()
    left_ch = self.read_char()
    while True:
        self.p += 1
        if self.p >= len(self.data):
            raise IndexError("Unterminated string in Lua data")
        ch = self.data[self.p]
        if ch == left_ch:
            self.p += 1
            break
        elif ch == '\\':
            self.p += 1
            if self.p >= len(self.data):
                raise IndexError("Unterminated string escape in Lua data")
            esc = self.data[self.p]
            if esc == 'n':
                buffer += '\n'
            elif esc == 'r':
                buffer += '\r'
            elif esc == 't':
                buffer += '\t'
            elif esc == '\\':
                buffer += '\\'
            elif esc == left_ch:
                buffer += left_ch
            else:
                buffer += '\\' + esc
        else:
            buffer += ch
            
    self.read_trim()
    return buffer

luadata.io.read.StreamData.read_string = _patched_read_string

def extract_lua_table(s, start_idx):
    """
    Given a string `s` and starting index `start_idx` which is the start of a Lua table (should be '{'),
    scans forward balancing '{' and '}' (ignoring brackets inside strings/comments) and returns the full table string.
    """
    n = len(s)
    # Find the first '{'
    i = start_idx
    while i < n and s[i] != '{':
        i += 1
        
    if i >= n:
        return None
        
    brace_start = i
    brace_count = 0
    in_string = False
    string_char = None
    in_long_string = False
    in_comment = False
    
    while i < n:
        c = s[i]
        
        # Handle comments
        if in_comment:
            if c == '\n':
                in_comment = False
            i += 1
            continue
            
        # Handle long strings [[...]]
        if in_long_string:
            if c == ']' and i + 1 < n and s[i+1] == ']':
                in_long_string = False
                i += 2
            else:
                i += 1
            continue
            
        # Handle normal strings "..." and '...'
        if in_string:
            if c == '\\':
                i += 2 # Skip escape char
            elif c == string_char:
                in_string = False
                i += 1
            else:
                i += 1
            continue
            
        # Check start of comment
        if c == '-' and i + 1 < n and s[i+1] == '-':
            in_comment = True
            i += 2
            continue
            
        # Check start of long string
        if c == '[' and i + 1 < n and s[i+1] == '[':
            in_long_string = True
            i += 2
            continue
            
        # Check start of normal string
        if c == '"' or c == "'":
            in_string = True
            string_char = c
            i += 1
            continue
            
        # Check braces
        if c == '{':
            brace_count += 1
        elif c == '}':
            brace_count -= 1
            if brace_count == 0:
                # We found the matching closing brace!
                return s[brace_start:i+1]
        i += 1
        
    return None

def parse_lua_config_file(filepath):
    """
    Parses a sharecfg Lua file (e.g. name_code.lua) and returns a python dict.
    We support:
    - Recursive loading and merging of ship_skin_template sublist files.
    - Multiple index assignments pattern (pg.base.name[1] = { ... }) transformed and parsed in one go.
    - Single table assignments pattern (pg.base.name = { ... }) parsed directly.
    """
    filename = os.path.basename(filepath)
    if filename == "ship_skin_template.lua":
        dirpath = os.path.dirname(filepath)
        sublist_dir = os.path.join(dirpath, "ship_skin_template_sublist")
        data = {}
        if os.path.exists(sublist_dir):
            for f_name in os.listdir(sublist_dir):
                if f_name.endswith('.lua'):
                    sub_path = os.path.join(sublist_dir, f_name)
                    sub_data = parse_lua_config_file(sub_path)
                    if isinstance(sub_data, dict):
                        data.update(sub_data)
            return data
            
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Config file not found: {filepath}")
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    cfg_name = os.path.splitext(filename)[0]
    
    # Try finding multiple assignments pattern first: pg.base.<cfg_name>[
    prefix_bracket = f"pg.base.{cfg_name}["
    start_idx = content.find(prefix_bracket)
    if start_idx != -1:
        end_idx = content.rfind("end)()")
        if end_idx == -1:
            end_idx = len(content)
        body = content[start_idx:end_idx].strip()
        pattern = re.compile(r'end\s*\)\s*\(\s*\)\s*\n?\s*\(function\s*\(\s*\)')
        body_cleaned = pattern.sub('', body)
        body_transformed = body_cleaned.replace(prefix_bracket, "[")
        lua_table_str = f"return {{\n{body_transformed}\n}}"
        data = luadata.unserialize(lua_table_str)
        if isinstance(data, (list, tuple)) and len(data) > 0:
            data = data[0]
    else:
        # Single assignment pattern: pg.base.<cfg_name> = {
        prefix_assign = f"pg.base.{cfg_name}"
        assign_idx = content.find(prefix_assign)
        if assign_idx == -1:
            return {}
        brace_idx = content.find("{", assign_idx)
        if brace_idx == -1:
            return {}
        table_str = extract_lua_table(content, brace_idx)
        if not table_str:
            return {}
        data = luadata.unserialize(table_str)
        if isinstance(data, (list, tuple)) and len(data) > 0:
            data = data[0]
            
    if isinstance(data, dict):
        return {str(k): v for k, v in data.items()}
    return data

def parse_lua_story_file(filepath):
    """
    Parses a story file (e.g. actruyue01.lua) which returns a single Lua table,
    and returns a Python dict/list.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Story file not found: {filepath}")
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # The returned table starts at the first '{' in the file
    table_str = extract_lua_table(content, 0)
    if not table_str:
        raise ValueError(f"Could not extract Lua table from story file: {filepath}")
        
    parsed_val = luadata.unserialize(table_str)
    if isinstance(parsed_val, (list, tuple)) and len(parsed_val) > 0:
        parsed_val = parsed_val[0]
    return parsed_val

class LazyStoryDict(dict):
    def __init__(self, story_dir):
        super().__init__()
        self.story_dir = story_dir
        self.loaded = {}
        # Scan files in the directory
        if os.path.exists(story_dir):
            for filename in os.listdir(story_dir):
                if filename.endswith('.lua'):
                    key = os.path.splitext(filename)[0].lower()
                    self.loaded[key] = filename
                    
    def __contains__(self, key):
        return key.lower() in self.loaded
        
    def __getitem__(self, key):
        key_lower = key.lower()
        if key_lower not in self.loaded:
            raise KeyError(key)
        val = self.loaded[key_lower]
        if isinstance(val, str):
            filepath = os.path.join(self.story_dir, val)
            try:
                parsed_val = parse_lua_story_file(filepath)
                self.loaded[key_lower] = parsed_val
                return parsed_val
            except Exception as e:
                print(f"Error loading and parsing story file {filepath}: {e}")
                self.loaded[key_lower] = None
                return None
        return val
        
    def get(self, key, default=None):
        if key in self:
            val = self[key]
            return val if val is not None else default
        return default
        
    def items(self):
        for key in list(self.loaded.keys()):
            yield key, self[key]
            
    def keys(self):
        return self.loaded.keys()
        
    def values(self):
        for key in self.loaded.keys():
            yield self[key]

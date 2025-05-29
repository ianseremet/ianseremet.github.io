import os
import re
from pathlib import Path

APP_HTML = "app.html"
TOOLS_DIR = "tools"

TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{tool_title}</title>
  <link href="https://fonts.googleapis.com/css2?family=Space+Mono&display=swap" rel="stylesheet">
  <style>
    body {{
      font-family: 'Space Mono', monospace;
      background-color: #2a2a2a;
      color: #ffffff;
      padding: 40px;
    }}
    h1 {{
      color: #9CBA7F;
    }}
    a {{
      color: #8dc2a9;
    }}
  </style>
</head>
<body>
  <h1>{tool_title}</h1>
  <p>This tool is available as a Python file. Download and run it locally with Python 3.</p>
  <p><strong>Download:</strong> <a href="{script_name}" download>{script_name}</a></p>
</body>
</html>
'''

def parse_app_html(app_path):
    with open(app_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Match lines like: <a class="tool-link" href="tools/boltselector.html">Bolt Selector</a>
    pattern = r'href="tools/([a-zA-Z0-9_-]+)\.html">([^<]+)</a>'
    matches = re.findall(pattern, html)

    tool_map = {}
    for base_name, display_name in matches:
        script_name = base_name + ".py"
        tool_map[base_name] = {"title": display_name.strip(), "script": script_name}

    return tool_map

def generate_tool_pages(tool_map, tools_dir):
    for base_name, info in tool_map.items():
        html_path = os.path.join(tools_dir, f"{base_name}.html")
        content = TEMPLATE.format(tool_title=info["title"], script_name=info["script"])
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Created {html_path}")

if __name__ == "__main__":
    Path(TOOLS_DIR).mkdir(exist_ok=True)
    tools = parse_app_html(APP_HTML)
    generate_tool_pages(tools, TOOLS_DIR)

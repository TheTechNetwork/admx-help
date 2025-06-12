import os
import xml.etree.ElementTree as ET
import json

def parse_admx(admx_dir):
    results = []
    for file in os.listdir(admx_dir):
        if file.endswith(".admx"):
            filepath = os.path.join(admx_dir, file)
            try:
                tree = ET.parse(filepath)
                root = tree.getroot()
                policies = root.findall(".//policy")
                for policy in policies:
                    name = policy.attrib.get("name")
                    class_type = policy.attrib.get("class")
                    display_name = policy.attrib.get("displayName", "")
                    explain_text = policy.attrib.get("explainText", "")
                    regkey_el = policy.find(".//registryKey")
                    regvalue_el = policy.find(".//valueName")
                    results.append({
                        "name": name,
                        "display_name": display_name,
                        "explanation": explain_text,
                        "class": class_type,
                        "registry_key": regkey_el.text if regkey_el is not None else "",
                        "value_name": regvalue_el.text if regvalue_el is not None else ""
                    })
            except Exception as e:
                print(f"Error parsing {filepath}: {e}")
    return results

def generate_html(output_dir):
    html = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>ADMX Policy Viewer</title>
  <script src="https://cdn.jsdelivr.net/npm/fuse.js"></script>
</head>
<body>
  <h1>ADMX Policy Viewer</h1>
  <input type="text" id="search" placeholder="Search policies...">
  <ul id="results"></ul>
  <script>
    fetch('policies.json').then(r => r.json()).then(data => {
      const fuse = new Fuse(data, { keys: ['name', 'display_name', 'registry_key', 'value_name'], threshold: 0.3 });
      document.getElementById('search').addEventListener('input', (e) => {
        const result = fuse.search(e.target.value);
        document.getElementById('results').innerHTML =
          result.map(r => `<li><b>${r.item.name}</b>: ${r.item.registry_key} / ${r.item.value_name}</li>`).join('');
      });
    });
  </script>
</body>
</html>
"""
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

def main():
    import sys
    if len(sys.argv) < 3:
        print("Usage: parse_admx.py <admx_dir> <output_dir>")
        return

    admx_dir = sys.argv[1]
    output_dir = sys.argv[2]

    # Avoid clobbering any system file if accidentally given an invalid output path
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    print(f"Parsing ADMX files from: {admx_dir}")
    policies = parse_admx(admx_dir)

    print(f"Writing {len(policies)} policies to: {output_dir}/policies.json")
    with open(os.path.join(output_dir, "policies.json"), "w", encoding="utf-8") as f:
        json.dump(policies, f, indent=2)

    print("Generating HTML viewer...")
    generate_html(output_dir)

    print("Done.")

if __name__ == "__main__":
    main()

import os
import sys
import json
import xml.etree.ElementTree as ET
from collections import defaultdict

def load_adml_strings(adml_path):
    strings = {}
    tree = ET.parse(adml_path)
    root = tree.getroot()
    ns = {'w': 'http://schemas.microsoft.com/GroupPolicy/2006/07/PolicyDefinitions'}

    for string in root.findall('.//w:string', ns):
        id_attr = string.attrib.get('id')
        if id_attr:
            strings[id_attr] = string.text or ''
    return strings

def load_categories(admx_root, strings):
    categories = {}
    for cat in admx_root.findall(".//category"):
        cat_id = cat.attrib.get('name')
        parent = cat.attrib.get('parentCategory')
        cat_path = [strings.get(cat_id, cat_id)]
        while parent:
            parent_cat = admx_root.find(f".//category[@name='{parent}']")
            if parent_cat is not None:
                cat_path.insert(0, strings.get(parent, parent))
                parent = parent_cat.attrib.get('parentCategory')
            else:
                break
        categories[cat_id] = " > ".join(cat_path)
    return categories

def parse_admx(admx_path, adml_path):
    policies = []
    strings = load_adml_strings(adml_path)
    tree = ET.parse(admx_path)
    root = tree.getroot()
    categories = load_categories(root, strings)

    for policy in root.findall(".//policy"):
        policy_id = policy.attrib['name']
        display_name = strings.get(policy.attrib.get('displayName', ''), policy_id)
        class_type = policy.attrib.get('class', 'Machine').lower()
        scope = 'machine' if class_type == 'machine' else 'user'

        reg_key = ""
        value_names = []
        value_types = []

        reg_key_node = policy.find('registryKey')
        if reg_key_node is not None:
            reg_key = reg_key_node.attrib.get('key', '')
        else:
            # Try registrySettings path
            reg_settings = policy.find('registrySettings')
            if reg_settings is not None:
                reg_key = reg_settings.attrib.get('key', '')
                val_name = reg_settings.attrib.get('valueName')
                val_type = reg_settings.attrib.get('valueType', 'REG_SZ')
                if val_name:
                    value_names.append(val_name)
                    value_types.append(val_type)

        for elem in policy.findall(".//value"):
            val_name = elem.attrib.get('valueName')
            val_type = elem.attrib.get('valueType', 'REG_SZ')
            if val_name:
                value_names.append(val_name)
                value_types.append(val_type)

        for elem in policy.findall(".//elements/*"):
            val_name = elem.attrib.get('id')
            val_type = elem.attrib.get('valueType', 'REG_SZ')
            if val_name:
                value_names.append(val_name)
                value_types.append(val_type)

        desc_id = policy.attrib.get('explainText')
        description = strings.get(desc_id, '') if desc_id else ''

        cat = policy.attrib.get('parentCategory')
        gpo_path = categories.get(cat, '') if cat else ''

        policies.append({
            'name': policy_id,
            'display_name': display_name,
            'description': description,
            'gpo_path': gpo_path,
            'registry_key': reg_key,
            'value_names': value_names,
            'value_types': value_types,
            'scope': scope,
        })

    return policies

def main():
    admx_dir = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)
    all_policies = []

    for root, _, files in os.walk(admx_dir):
        for file in files:
            if file.endswith(".admx"):
                admx_path = os.path.join(root, file)
                lang_dir = os.path.join(os.path.dirname(admx_path), "en-US")
                adml_file = os.path.splitext(file)[0] + ".adml"
                adml_path = os.path.join(lang_dir, adml_file)
                if os.path.exists(adml_path):
                    all_policies.extend(parse_admx(admx_path, adml_path))

    with open(os.path.join(output_dir, "policies.json"), "w", encoding="utf-8") as f:
        json.dump(all_policies, f, indent=2)

    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(INDEX_HTML)

INDEX_HTML = """<!DOCTYPE html>
<html>
<head>
  <meta charset=\"UTF-8\">
  <title>ADMX Policy Viewer</title>
  <script src=\"https://cdn.jsdelivr.net/npm/fuse.js\"></script>
  <style>
    body { font-family: sans-serif; padding: 1em; }
    input { width: 100%; padding: 0.5em; font-size: 16px; }
    .result { margin-top: 1em; }
    .policy { border: 1px solid #ccc; padding: 1em; margin-bottom: 1em; border-radius: 5px; }
    .path { font-style: italic; color: #666; }
    .reg { font-family: monospace; color: #444; }
  </style>
</head>
<body>
  <h1>ADMX Policy Viewer</h1>
  <input type=\"text\" id=\"search\" placeholder=\"Search policies...\">
  <div class=\"result\" id=\"results\"></div>
  <script>
    fetch('policies.json').then(r => r.json()).then(data => {
      const fuse = new Fuse(data, {
        keys: ['name', 'display_name', 'registry_key', 'value_names', 'description', 'gpo_path'],
        threshold: 0.3
      });
      const render = items => {
        const el = document.getElementById('results');
        el.innerHTML = items.map(p => `
          <div class=\"policy\">
            <b>${p.display_name}</b><br>
            <div class=\"path\">${p.gpo_path} [${p.scope}]</div>
            <div class=\"reg\">${p.registry_key}\\${p.value_names.join(', ')}</div>
            <p>${p.description}</p>
          </div>`
        ).join('');
      };
      document.getElementById('search').addEventListener('input', e => {
        const results = fuse.search(e.target.value).map(r => r.item);
        render(results);
      });
      render(data);
    });
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    main()

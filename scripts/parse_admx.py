import os
import sys
import json
import xml.etree.ElementTree as ET
from collections import defaultdict

def load_strings(admx_dir):
    strings = {}
    for file in os.listdir(admx_dir):
        if file.endswith(".adml"):
            tree = ET.parse(os.path.join(admx_dir, file))
            root = tree.getroot()
            ns = {"aml": "http://schemas.microsoft.com/GroupPolicy/2006/07/AdministrativeTemplates"}
            for string in root.findall(".//aml:string", ns):
                strings[string.attrib["id"]] = string.text
    return strings

def parse_admx_file(filepath, strings):
    tree = ET.parse(filepath)
    root = tree.getroot()
    ns = {"admx": "http://schemas.microsoft.com/GroupPolicy/2006/07/AdministrativeTemplates"}

    policies = []

    for policy in root.findall(".//admx:policy", ns):
        name = policy.attrib["name"]
        display_name_id = policy.attrib.get("displayName", "")
        display_name = strings.get(display_name_id, display_name_id)

        explain_id = policy.attrib.get("explainText", "")
        description = strings.get(explain_id, "")

        class_type = policy.attrib.get("class", "Machine")
        scope = "Machine" if class_type.lower() == "machine" else "User"

        supported_on = policy.attrib.get("supportedOn", "")

        # Registry
        reg_key = None
        value_name = None
        for reg_elem in policy.findall(".//admx:registrySetting", ns):
            reg_key = reg_elem.attrib.get("key", reg_key)
            value_name = reg_elem.attrib.get("valueName", value_name)

        policies.append({
            "name": name,
            "display_name": display_name,
            "description": description,
            "gpo_path": "TODO",  # Will add later if you want categories
            "registry_key": reg_key or "",
            "value_name": value_name or "",
            "scope": scope,
            "supported_on": supported_on,
        })
    return policies

def main():
    if len(sys.argv) < 3:
        print("Usage: parse_admx.py <input_admx_dir> <output_dir>")
        sys.exit(1)

    admx_dir = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)

    strings = load_strings(admx_dir)
    all_policies = []

    for file in os.listdir(admx_dir):
        if file.endswith(".admx"):
            filepath = os.path.join(admx_dir, file)
            all_policies.extend(parse_admx_file(filepath, strings))

    with open(os.path.join(output_dir, "policies.json"), "w", encoding="utf-8") as f:
        json.dump(all_policies, f, indent=2, ensure_ascii=False)

    print(f"✅ Parsed {len(all_policies)} policies.")

if __name__ == "__main__":
    main()

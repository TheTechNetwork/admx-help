import os
import xml.etree.ElementTree as ET
import json

def parse_admx(admx_dir, adml_dir):
    results = []
    for file in os.listdir(admx_dir):
        if file.endswith(".admx"):
            try:
                tree = ET.parse(os.path.join(admx_dir, file))
                root = tree.getroot()
                policies = root.findall(".//policy")
                for p in policies:
                    name = p.attrib.get("name")
                    class_type = p.attrib.get("class")
                    regkey = p.find(".//registryKey")
                    regvalue = p.find(".//valueName")
                    results.append({
                        "name": name,
                        "class": class_type,
                        "registry_key": regkey.text if regkey is not None else "",
                        "value_name": regvalue.text if regvalue is not None else ""
                    })
            except Exception as e:
                print(f"Error parsing {file}: {e}")
    return results

if __name__ == "__main__":
    import sys
    admx_dir = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)
    policies = parse_admx(admx_dir, os.path.join(admx_dir, "en-US"))
    with open(os.path.join(output_dir, "policies.json"), "w") as f:
        json.dump(policies, f, indent=2)

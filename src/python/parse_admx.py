import os
import json
import xml.etree.ElementTree as ET
import sys

# --- Configuration ---
# Get ADMX source directory from command line argument
# sys.argv[1] would be the first argument passed to the script
ADMX_SOURCE_DIR = sys.argv[1] if len(sys.argv) > 1 else 'default/path/if/not/provided'
OUTPUT_DIR = 'src/frontend/data' # Where JSON files will be written
LANG = 'en-US' # Target language for ADML

# --- Main Parsing Logic (Simplified Example) ---
# This needs to be significantly more robust for production!

def parse_admx_adml(admx_dir, lang):
    policies_data = []
    admx_files = [f for f in os.listdir(admx_dir) if f.endswith('.admx')]
    print(f"Found {len(admx_files)} ADMX files in {admx_dir}")

    # Build a dictionary of ADML files for quicker lookup
    adml_files_map = {}
    adml_lang_dir = os.path.join(admx_dir, lang)
    if os.path.exists(adml_lang_dir):
        for f in os.listdir(adml_lang_dir):
            if f.endswith('.adml'):
                adml_files_map[os.path.splitext(f)[0]] = os.path.join(adml_lang_dir, f)
    else:
        print(f"Warning: ADML language directory '{adml_lang_dir}' not found.")


    for admx_filename in admx_files:
        admx_path = os.path.join(admx_dir, admx_filename)
        adml_base_name = os.path.splitext(admx_filename)[0]
        adml_path = adml_files_map.get(adml_base_name)

        if not adml_path or not os.path.exists(adml_path):
            print(f"Warning: ADML file not found or mapped for {admx_filename}. Skipping descriptions for this file.")
            adml_root = None # Process without ADML strings
        else:
            try:
                adml_tree = ET.parse(adml_path)
                adml_root = adml_tree.getroot()
            except ET.ParseError as e:
                print(f"Error parsing ADML file {adml_path}: {e}. Will proceed without ADML strings.")
                adml_root = None

        try:
            admx_tree = ET.parse(admx_path)
            admx_root = admx_tree.getroot()

            # Namespaces are crucial for ADMX/ADML parsing
            admx_ns = {'policy': 'http://schemas.microsoft.com/GroupPolicy/2006/07/PolicyDefinitions'}
            adml_ns = {'adml': 'http://schemas.microsoft.com/GroupPolicy/2006/07/PolicyDefinitions/ADML'}

            strings = {}
            if adml_root:
                for string_elem in adml_root.findall('.//adml:string', adml_ns):
                    strings[string_elem.get('id')] = string_elem.text

            # Parse policies from ADMX
            for policy_elem in admx_root.findall('.//policy:policy', admx_ns):
                policy_id = policy_elem.get('name')
                
                # Get display name and description, falling back to ID if not found
                display_name = strings.get(policy_elem.get('displayName'), policy_id)
                explain_text = strings.get(policy_elem.get('explainText'), '')

                # Attempt to get 'supportedOn' text
                supported_on_id = policy_elem.get('supported')
                supported_on_text = strings.get(supported_on_id, supported_on_id) if supported_on_id else ''

                policy_data = {
                    "id": policy_id,
                    "name": display_name,
                    "description": explain_text,
                    "category_path": get_category_path(policy_elem, admx_root, admx_ns, strings),
                    "supported_on": supported_on_text,
                    "admx_file": admx_filename
                }

                # Extract registry keys (this is very basic and needs extensive work)
                registry_elem = policy_elem.find('.//policy:registry', admx_ns)
                if registry_elem is not None:
                    key_elem = registry_elem.find('policy:key', admx_ns)
                    if key_elem is not None:
                        policy_data["registry_key"] = key_elem.text

                    value_name_elem = registry_elem.find('policy:valueName', admx_ns)
                    if value_name_elem is not None:
                        policy_data["registry_value_name"] = value_name_elem.text

                    # Basic handling for 'value' element if it's a fixed value
                    value_elem = registry_elem.find('policy:value', admx_ns)
                    if value_elem is not None and value_elem.text:
                        policy_data["registry_value"] = value_elem.text
                    elif value_elem is not None and value_elem.get('value'): # Sometimes value is an attribute
                        policy_data["registry_value"] = value_elem.get('value')
                    
                    # You'll need much more sophisticated parsing for 'elements' (e.g., text, enum, decimal)
                    # and how they map to registry values based on user input.

                policies_data.append(policy_data)

        except ET.ParseError as e:
            print(f"Error parsing XML file {admx_path}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while processing {admx_path}: {e}")

    return policies_data

def get_category_path(policy_elem, admx_root, admx_ns, strings):
    # This is a simplified category path resolver.
    # ADMX categories have parent categories, you need to traverse up.
    category_name_in_admx = policy_elem.get('category')
    
    path_segments = []

    # Determine Computer or User configuration base
    config_class = policy_elem.get('class')
    if config_class == 'Machine':
        path_segments.append("Computer Configuration")
    elif config_class == 'User':
        path_segments.append("User Configuration")
    else:
        path_segments.append("Unknown Configuration") # Fallback for unexpected class

    # Append "Administrative Templates"
    path_segments.append("Administrative Templates")

    # Build the category path by traversing up the parent categories
    current_category_name = category_name_in_admx
    category_stack = []

    # Iterate to find the current category element and its parents
    while current_category_name:
        current_category_elem = admx_root.find(f".//policy:category[@name='{current_category_name}']", admx_ns)
        if not current_category_elem:
            break # Category not found, stop traversal

        display_name_id = current_category_elem.get('displayName')
        display_name = strings.get(display_name_id, current_category_name)
        category_stack.append(display_name)

        parent_ref = current_category_elem.find('.//policy:parentCategory', admx_ns)
        if parent_ref is None:
            break # No more parents
        
        parent_id_full = parent_ref.get('ref')
        # Parent ref can be "Class:CategoryName" or just "CategoryName"
        if ':' in parent_id_full:
            current_category_name = parent_id_full.split(':')[1]
        else:
            current_category_name = parent_id_full

    # Insert categories after "Administrative Templates" in reverse order
    for segment in reversed(category_stack):
        path_segments.append(segment) # Append them in correct order (top-level category first)


    return "/".join(path_segments)

# --- Main execution ---
if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Perform parsing
    print(f"Parsing ADMX/ADML files from: {ADMX_SOURCE_DIR}")
    all_policies = parse_admx_adml(ADMX_SOURCE_DIR, LANG)

    # Save to JSON
    output_json_path = os.path.join(OUTPUT_DIR, 'policies.json')
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(all_policies, f, indent=2, ensure_ascii=False)
    print(f"Successfully generated {len(all_policies)} policies to {output_json_path}")

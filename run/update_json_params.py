import os
import json

def update_nested_keys(data, updates):
    """
    Recursively update specified keys in a nested dictionary.
    
    Parameters:
    - data (dict): The dictionary to update.
    - updates (dict): A dictionary where keys are the target keys to update,
                      and values are the new values to set.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key in updates:
                data[key] = updates[key]
            else:
                update_nested_keys(value, updates)
    elif isinstance(data, list):
        for item in data:
            update_nested_keys(item, updates)

def process_json_file(file_path, updates):
    """
    Load a JSON file, update specified keys, and save the changes.
    
    Parameters:
    - file_path (str): Path to the JSON file.
    - updates (dict): A dictionary where keys are the target keys to update,
                      and values are the new values to set.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        update_nested_keys(data, updates)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Updated: {file_path}")
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def update_json_files_in_directory(base_directory, updates):
    """
    Recursively find and process all JSON files in the directory.
    
    Parameters:
    - base_directory (str): The directory to search for JSON files.
    - updates (dict): A dictionary where keys are the target keys to update,
                      and values are the new values to set.
    """
    for root, _, files in os.walk(base_directory):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                process_json_file(file_path, updates)

if __name__ == "__main__":
    # Define the updates you want to make
    updates = {
        "protocol_repeats": 1,
        "n_replicas": 11,
        "production_length": {
            "magnitude": 2.0,
            "unit": "nanosecond",
            ":is_custom:": True,
            "pint_unit_registry": "openff_units"
        }
    }
    
    # Specify the directory containing the JSON files
    base_directory = os.getcwd()  # Current working directory
    update_json_files_in_directory(base_directory, updates)


import json
import yaml  # Provided by the PyYAML package

# Let's define a typical production configuration as a Python dictionary
app_config = {
    "server": {
        "host": "127.0.0.1",
        "port": 8080,
        "debug_mode": True
    },
    "database": {
        "db_name": "production_db",
        "pool_size": 10
    },
    "allowed_origins": [
        "http://localhost:3000",
        "https://myapp.com"
    ]
}

# =====================================================================
# PART 1: Writing Configurations to Files
# =====================================================================

# 1. Writing to JSON
# 'indent=4' makes the output file pretty-printed and easy to read
with open("config.json", "w") as json_file:
    json.dump(app_config, json_file, indent=4)
print("Successfully wrote configuration to config.json")

# 2. Writing to YAML
# 'default_flow_style=False' ensures clean block indentation rather than inline braces
with open("config.yaml", "w") as yaml_file:
    yaml.dump(app_config, yaml_file, default_flow_style=False)
print("Successfully wrote configuration to config.yaml\n")


# =====================================================================
# PART 2: Reading Configurations from Files
# =====================================================================

# 1. Reading from JSON
with open("config.json", "r") as json_file:
    loaded_json_config = json.load(json_file)

# 2. Reading from YAML
with open("config.yaml", "r") as yaml_file:
    # Security Note: Always use safe_load to prevent execution of arbitrary Python code
    loaded_yaml_config = yaml.safe_load(yaml_file)


# =====================================================================
# Verification: Print the loaded settings
# =====================================================================
print("--- Loaded JSON Config ---")
print(f"Host: {loaded_json_config['server']['host']}")
print(f"DB Name: {loaded_json_config['database']['db_name']}")
print(f"Origins: {loaded_json_config['allowed_origins']}\n")

print("--- Loaded YAML Config ---")
print(f"Host: {loaded_yaml_config['server']['host']}")
print(f"DB Name: {loaded_yaml_config['database']['db_name']}")
print(f"Origins: {loaded_yaml_config['allowed_origins']}")
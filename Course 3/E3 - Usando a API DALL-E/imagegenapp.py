import json
import os
import random
import time
import urllib.parse
import requests

# 1. Load our advanced configuration file
CONFIG_FILE = "config.json"
try:
    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)
except FileNotFoundError:
    raise FileNotFoundError(f"Missing configuration file: {CONFIG_FILE}")

def generate_multiple_images(user_prompt):
    # Retrieve top-level configurations
    base_url = config["api_base_url"]
    output_dir = config["output_directory"]
    output_base_name = config["default_output_file"]
    
    # Retrieve system and image settings
    net_settings = config["network_settings"]
    img_settings = config["image_settings"]
    
    n = img_settings.get("num_images", 1)

    # 2. Directory Safety: Create the output folder if it doesn't exist yet
    os.makedirs(output_dir, exist_ok=True)

    # 3. Prompt Engineering: Enhance user prompt if configured
    final_prompt = user_prompt
    if img_settings["enhance_prompt"]:
        final_prompt += img_settings["quality_suffix"]
    
    # URL-encode only the prompt because it forms part of the main path
    encoded_prompt = urllib.parse.quote(final_prompt)
    target_url = f"{base_url}/{encoded_prompt}"

    print(f"Beginning generation of {n} images inside directory: '{output_dir}/'...")

    # Loop 'n' times to generate the variations
    for i in range(1, n + 1):
        # Determine the seed (use fixed seed if specified, otherwise generate random)
        seed = img_settings["fixed_seed"]
        if seed is None:
            seed = random.randint(1, 999999)
        
        # 4. Clean Query Building: We let 'requests' build the URL query string safely
        query_params = {
            "width": img_settings["width"],
            "height": img_settings["height"],
            "seed": seed,
            "model": img_settings["model"],
            "nologo": "true" if img_settings["remove_watermark"] else "false",
            "negative": img_settings["negative_prompt"]
        }
        
        filename = os.path.join(output_dir, f"{output_base_name}_{i}.png")
        print(f"Generating image {i}/{n} (seed: {seed}) as '{filename}'...")

        # 5. Robust Network Loop: Handle retries if the server is overloaded
        success = False
        attempts = 0
        max_attempts = net_settings.get("max_retries", 3)
        timeout = net_settings.get("timeout_seconds", 15)

        while not success and attempts < max_attempts:
            try:
                attempts += 1
                # Send the request with explicit timeout and automated query-parameters mapping
                response = requests.get(target_url, params=query_params, timeout=timeout)
                
                if response.status_code == 200:
                    # Write the binary image data to the custom output directory
                    with open(filename, "wb") as file:
                        file.write(response.content)
                    success = True
                else:
                    print(f"  Attempt {attempts} failed with HTTP Status: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"  Attempt {attempts} timed out (limit: {timeout}s)...")
            except requests.exceptions.RequestException as e:
                print(f"  Attempt {attempts} network error: {e}")

            # If failed, pause briefly before retrying to respect server limits
            if not success and attempts < max_attempts:
                time.sleep(2)

        if not success:
            print(f"  [ERROR] Failed to generate image {i} after {max_attempts} attempts.")

    print("\nAll image generations complete!")

# --- Execution ---
if __name__ == "__main__":
    test_prompt = "A majestic dragon guarding a treasure chest in a cavern"
    generate_multiple_images(test_prompt)
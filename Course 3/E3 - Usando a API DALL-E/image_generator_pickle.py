import json
import os
import random
import time
import urllib.parse
import requests
import pickle # New: For object serialization

# 1. Load the Configuration File
CONFIG_FILE = "C:\\Users\\reich\\Downloads\\Generative AI For Software Development\\Course 3\\E3 - Usando a API DALL-E\\config.json"
try:
    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)
except FileNotFoundError:
    raise FileNotFoundError(f"Missing configuration file: {CONFIG_FILE}")


def generate_and_pickle_images(user_prompt):
    """
    Generates multiple unique images sequentially, saves them as PNGs,
    and then pickles all image data along with the config to a .pkl file.
    """
    # Extract directory and file settings
    base_url = config["api_base_url"]
    output_dir = config["output_directory"]
    output_base_name = config["default_output_file"]
    
    # Extract network and image parameters
    net_settings = config["network_settings"]
    img_settings = config["image_settings"]
    
    n = img_settings.get("num_images", 1)

    # 2. Directory Safety: Create output folder if it is missing
    os.makedirs(output_dir, exist_ok=True)

    # 3. Prompt Enhancement: Append quality tags if enabled
    final_prompt = user_prompt
    if img_settings["enhance_prompt"]:
        final_prompt += img_settings["quality_suffix"]
    
    # URL-encode only the prompt since it forms part of the main URL path
    encoded_prompt = urllib.parse.quote(final_prompt)
    target_url = f"{base_url}/{encoded_prompt}"

    print(f"Beginning sequential generation of {n} images inside: '{output_dir}/'...")

    # New: Initialize dictionary to hold config and all image data for pickling
    # The 'config' is stored for reproducibility, and 'images' will store raw bytes.
    pickle_data = {
        "config": config,
        "images": {}
    }

    # Loop 'n' times sequentially (the robust tractor approach)
    for i in range(1, n + 1):
        # Determine the seed (use fixed seed if specified, otherwise generate random)
        seed = img_settings["fixed_seed"]
        if seed is None:
            seed = random.randint(1, 999999)
        
        # 4. Clean Query Building: We let 'requests' handle query parameter formatting
        query_params = {
            "width": img_settings["width"],
            "height": img_settings["height"],
            "seed": seed,
            "model": img_settings["model"],
            "nologo": "true" if img_settings["remove_watermark"] else "false",
            "negative": img_settings["negative_prompt"]
        }
        
        # Generate the filename for both .png and for use as a key in pickle_data
        filename_without_path = f"{output_base_name}_{i}.png"
        full_filename_path = os.path.join(output_dir, filename_without_path)
        
        print(f"Generating image {i}/{n} (seed: {seed}) as '{full_filename_path}'...")

        # 5. Robust Network Loop: Handle retries and timeouts for each sequential request
        success = False
        attempts = 0
        max_attempts = net_settings.get("max_retries", 3)
        timeout = net_settings.get("timeout_seconds", 15)

        while not success and attempts < max_attempts:
            try:
                attempts += 1
                response = requests.get(target_url, params=query_params, timeout=timeout)
                
                if response.status_code == 200:
                    # Save image as PNG
                    with open(full_filename_path, "wb") as file:
                        file.write(response.content)
                    
                    # New: Store raw image content in our pickle_data dictionary
                    pickle_data["images"][filename_without_path] = response.content
                    
                    success = True
                else:
                    print(f"  Attempt {attempts}/{max_attempts} failed with HTTP Status: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"  Attempt {attempts}/{max_attempts} timed out (limit: {timeout}s)...")
            except requests.exceptions.RequestException as e:
                print(f"  Attempt {attempts}/{max_attempts} network error: {e}")

            if not success and attempts < max_attempts:
                time.sleep(2)

        if not success:
            print(f"  [ERROR] Failed to generate image {i} after {max_attempts} attempts.")

    print("\nAll image generations complete!")

    # 6. New: Pickle the entire data dictionary (config + all images)
    # The .pkl file will be saved in the main output_dir.
    pickle_output_filename = os.path.join(output_dir, f"{output_base_name}_data.pkl")
    try:
        with open(pickle_output_filename, "wb") as pickle_file:
            pickle.dump(pickle_data, pickle_file)
        print(f"Successfully pickled configuration and image data to '{pickle_output_filename}'")
    except Exception as e:
        print(f"  [ERROR] Failed to pickle data: {e}")


# --- Execution ---
if __name__ == "__main__":
    test_prompt = "An astronaut riding a unicorn on the moon, pixel art style"
    generate_and_pickle_images(test_prompt)

    # --- Verification of Pickled Data ---
    # After running the script, you can load and inspect the pickled data:
    # try:
    #     pickle_file_path = os.path.join(config["output_directory"], f"{config['default_output_file']}_data.pkl")
    #     with open(pickle_file_path, "rb") as file:
    #         loaded_data = pickle.load(file)
    #     print("\n--- Loaded Pickled Data Verification ---")
    #     print(f"Loaded config: {loaded_data['config']['image_settings']['width']}x{loaded_data['config']['image_settings']['height']}")
    #     print(f"Number of images in pickled data: {len(loaded_data['images'])}")
    #     # To further verify, you could save one of the pickled images to a new file:
    #     # with open("restored_image_from_pickle.png", "wb") as f:
    #     #    f.write(loaded_data['images'][f"{config['default_output_file']}_1.png"])
    # except FileNotFoundError:
    #     print(f"\n[Verification] Pickled file not found at {pickle_file_path}")
    # except Exception as e:
    #     print(f"\n[Verification Error] Failed to load pickled data: {e}")
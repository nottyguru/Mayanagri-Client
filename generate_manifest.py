import os
import hashlib
import json
import urllib.parse

# Policies
POLICY_STRICT = 0  # Hashes must match (Mods)
POLICY_IGNORE = 1  # Skip if exists (Player configs)
POLICY_REPLACE = 2  # Force overwrite

# --- CONFIGURATION ---
BASE_URL = "https://raw.githubusercontent.com/nottyguru/Mayanagri-Client/main/files/"
MODPACK_FOLDER = "files"
OUTPUT_FILE = "modpack_manifest.json"

SERVER_IP = "10.128.12.210:2556" # Change this for production deployment
SERVER_PORT = 25565
# ---------------------

def calculate_sha1(filepath):
    sha1 = hashlib.sha1()
    with open(filepath, "rb") as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()

def get_policy_for_file(filename, relative_path):
    ignore_files = [
        "options.txt",
        "servers.dat",
        "in-game-account-switcher.properties",
        "launcher_profiles.json",
        "usercache.json",
        "usernamecache.json",
        "hotbar.nbt"
    ]

    # FIX: Return POLICY_IGNORE so player settings don't get overwritten!
    if filename.lower() in ignore_files or relative_path.replace("\\", "/").startswith("resourcepacks/"):
        return POLICY_IGNORE

    # Default to Strict for mods and mandatory configs
    return POLICY_STRICT

def generate_manifest():
    manifest = {
        "manifest_version": 1,
        "minecraft_version": "1.21.11",
        "fabric_version": "0.18.4",
        "java_version": 21,
        "server_ip": SERVER_IP,
        "server_port": SERVER_PORT,
        "jvm_flags": [
            "-XX:+UseG1GC",
            "-XX:MaxGCPauseMillis=50",
            "-Xmn128M"
        ],
        "files": [],
    }

    print("Bhai, files scan ho rahi hain...")

    if not os.path.exists(MODPACK_FOLDER) or not os.path.isdir(MODPACK_FOLDER) or not os.listdir(MODPACK_FOLDER):
        print(f"Error: '{MODPACK_FOLDER}' folder nahi mila ya khali hai. Please check the directory.")
        return

    unsorted_files = []

    for root, _, files in os.walk(MODPACK_FOLDER):
        for file in files:
            filepath = os.path.join(root, file)
            relative_path = os.path.relpath(filepath, MODPACK_FOLDER)
            forward_slash_path = relative_path.replace("\\", "/")

            encoded_path = urllib.parse.quote(forward_slash_path)
            download_url = BASE_URL + encoded_path

            policy = get_policy_for_file(file, forward_slash_path)
            file_hash = calculate_sha1(filepath)

            unsorted_files.append(
                {
                    "path": forward_slash_path,
                    "url": download_url,
                    "sha1": file_hash,
                    "policy": policy,
                }
            )

    manifest["files"] = sorted(unsorted_files, key=lambda x: x["path"])

    with open(OUTPUT_FILE, "w") as f:
        json.dump(manifest, f, indent=4)

    print(f"Set hai boss! {len(manifest['files'])} files ka '{OUTPUT_FILE}' ready hai.")

if __name__ == "__main__":
    generate_manifest()
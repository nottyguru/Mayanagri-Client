import os
import hashlib
import json
import urllib.parse

# Policies
POLICY_STRICT = 0  # Hashes must match (mods, critical configs)
POLICY_IGNORE = 1  # Skip if exists (player settings, local data)
POLICY_REPLACE = 2  # Force overwrite (rare)

# --- CONFIGURATION ---
BASE_URL = "https://raw.githubusercontent.com/nottyguru/Mayanagri-Client/main/files/"
MODPACK_FOLDER = "files"
OUTPUT_FILE = "modpack_manifest.json"
POLICY_FILE = "policies.json"          # optional custom policy overrides

SERVER_IP = "10.128.12.210:25556"       # Change for production
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

def get_policy_for_file(filename, relative_path, custom_policies):
    """
    Returns the sync policy for a file.
    - If custom_policies dict contains an entry for the relative path, use that.
    - Otherwise, treat files in the 'ignore_files' list as POLICY_IGNORE.
    - Default: POLICY_STRICT.
    """
    # First check custom policies from the external JSON file
    if relative_path in custom_policies:
        pol = custom_policies[relative_path]
        if pol == "ignore":
            return POLICY_IGNORE
        if pol == "replace":
            return POLICY_REPLACE
        # "strict" or any other value falls through to default

    # Default ignore list (files that should not be overwritten)
    ignore_files = [
        "options.txt",
        "servers.dat",
        "in-game-account-switcher.properties",
        "launcher_profiles.json",
        "usercache.json",
        "usernamecache.json",
        "hotbar.nbt"
    ]

    # If the file matches one of these names, ignore it
    if filename.lower() in ignore_files:
        return POLICY_IGNORE

    # Also ignore any file inside resourcepacks/ (they are big and user-provided)
    if relative_path.replace("\\", "/").startswith("resourcepacks/"):
        return POLICY_IGNORE

    # All others are strict
    return POLICY_STRICT

def generate_manifest():
    # Load custom policies if the file exists
    custom_policies = {}
    if os.path.exists(POLICY_FILE):
        try:
            with open(POLICY_FILE, "r") as f:
                custom_policies = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load {POLICY_FILE}: {e}")

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

            policy = get_policy_for_file(file, forward_slash_path, custom_policies)
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
    print("Policies used:")
    for entry in manifest["files"]:
        pol_name = ["strict", "ignore", "replace"][entry["policy"]]
        print(f"  {entry['path']} -> {pol_name}")

if __name__ == "__main__":
    generate_manifest()
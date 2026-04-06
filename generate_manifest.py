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

SERVER_IP = "127.0.0.1"       # Changed to IPv4 loopback for local testing
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
    Returns the sync policy for a file using a Priority System.
    """
    # Ensure consistent forward slashes for matching
    safe_path = relative_path.replace("\\", "/")

    # PRIORITY 1: Exact file match (e.g., "config/custom_menu.json")
    if safe_path in custom_policies:
        pol = custom_policies[safe_path].lower()
        if pol == "ignore": return POLICY_IGNORE
        if pol == "replace": return POLICY_REPLACE
        if pol == "strict": return POLICY_STRICT

    # PRIORITY 2: Folder match (e.g., "config/")
    # Sort keys by length descending so deeper folders get checked before parent folders
    for key in sorted(custom_policies.keys(), key=len, reverse=True):
        if key.endswith("/") and safe_path.startswith(key):
            pol = custom_policies[key].lower()
            if pol == "ignore": return POLICY_IGNORE
            if pol == "replace": return POLICY_REPLACE
            if pol == "strict": return POLICY_STRICT

    # PRIORITY 3: Default hardcoded ignore list
    ignore_files = [
        "options.txt",
        "servers.dat",
        "in-game-account-switcher.properties",
        "launcher_profiles.json",
        "usercache.json",
        "usernamecache.json",
        "hotbar.nbt"
    ]

    if filename.lower() in ignore_files:
        return POLICY_IGNORE

    if safe_path.startswith("resourcepacks/"):
        return POLICY_IGNORE

    # PRIORITY 4: Default to Strict
    return POLICY_STRICT

def generate_manifest():
    # Load custom policies if the file exists
    custom_policies = {}
    if os.path.exists(POLICY_FILE):
        try:
            with open(POLICY_FILE, "r") as f:
                custom_policies = json.load(f)
            print(f"Loaded {len(custom_policies)} rules from {POLICY_FILE}")
        except Exception as e:
            print(f"Warning: Could not load {POLICY_FILE}: {e}")

    manifest = {
        "manifest_version": 1,
        "minecraft_version": "1.21.11",
        "fabric_version": "0.18.5",
        "java_version": 21,
        "server_ip": SERVER_IP,
        "server_port": SERVER_PORT,
        "jvm_flags": [
            "-XX:+UseG1GC",
            "-XX:MaxGCPauseMillis=50",
            "-Xmn128M"
        ],
        "files": [],
        "managed_directories": [
            "mods",
            "resourcepacks",
            "config",     # Now you can add config!
            "shaderpacks" # And shaders!
        ],
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

            # FIX: Ensure forward slashes inside paths aren't converted to %2F
            encoded_path = urllib.parse.quote(forward_slash_path, safe='/')
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

    # Sort files alphabetically to ensure consistent manifest generation
    manifest["files"] = sorted(unsorted_files, key=lambda x: x["path"])

    with open(OUTPUT_FILE, "w") as f:
        json.dump(manifest, f, indent=4)

    print(f"Set hai boss! {len(manifest['files'])} files ka '{OUTPUT_FILE}' ready hai.")
    
    # Optional: Print out a quick summary of what policies were applied
    strict_count = sum(1 for f in manifest["files"] if f["policy"] == POLICY_STRICT)
    ignore_count = sum(1 for f in manifest["files"] if f["policy"] == POLICY_IGNORE)
    replace_count = sum(1 for f in manifest["files"] if f["policy"] == POLICY_REPLACE)
    
    print(f"Summary: {strict_count} Strict | {ignore_count} Ignore | {replace_count} Replace")

if __name__ == "__main__":
    generate_manifest()
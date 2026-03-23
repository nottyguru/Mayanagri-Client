import os
import hashlib
import json

BASE_URL = "https://raw.githubusercontent.com/nottyguru/Mayanagri-Client/main/files/"
FILES_DIR = "files"


def calculate_sha1(file_path):
    sha1 = hashlib.sha1()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha1.update(chunk)
    return sha1.hexdigest()


def build_manifest():
    file_entries = []

    for root, _, files in os.walk(FILES_DIR):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, FILES_DIR).replace("\\", "/")
            download_url = BASE_URL + relative_path
            file_hash = calculate_sha1(local_path)

            file_entries.append(
                {"path": relative_path, "url": download_url, "sha1": file_hash}
            )

    # ADDED: java_version is now dynamically set here
    manifest_data = {
        "minecraft_version": "1.20.4",
        "fabric_version": "0.15.7",
        "java_version": 17,
        "server_ip": "play.mayanagri.net",
        "server_port": 25565,
        "jvm_flags": ["-XX:+UseG1GC", "-XX:MaxGCPauseMillis=50", "-Xmn128M"],
        "files": file_entries,
    }

    with open("modpack_manifest.json", "w") as f:
        json.dump(manifest_data, f, indent=4)

    print(f"Successfully mapped {len(file_entries)} files to modpack_manifest.json!")


if __name__ == "__main__":
    if not os.path.exists(FILES_DIR):
        print(f"Error: Could not find the '{FILES_DIR}' directory.")
    else:
        build_manifest()

import hashlib
import sys
import os


def calculate_sha256(filepath):
    """Calculates the SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            # Read the file in chunks to handle memory efficiently
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return None


if __name__ == "__main__":
    # Default to the standard compiled executable name
    target_file = "MayanagriLauncher.exe"

    # Allow passing a specific file path via command line arguments
    if len(sys.argv) > 1:
        target_file = sys.argv[1]

    print(f"Scanning: {target_file}...\n")

    if not os.path.exists(target_file):
        print(
            f"Error: Could not find '{target_file}'. Please ensure the file exists in this directory."
        )
        sys.exit(1)

    file_hash = calculate_sha256(target_file)

    if file_hash:
        print("Success! Here is your SHA256 hash:")
        print("-" * 64)
        print(file_hash)
        print("-" * 64)
        print("\nUpdate your bootstrap.json to include this line:")
        print(f'  "launcher_sha256": "{file_hash}"')

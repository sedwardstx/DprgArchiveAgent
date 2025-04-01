import os
import sys
from pathlib import Path

def check_file_for_null_bytes(file_path):
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            if b'\x00' in content:
                null_positions = [i for i, byte in enumerate(content) if byte == 0]
                return f"Found {len(null_positions)} null bytes in {file_path} at positions: {null_positions[:10]}..."
            return None
    except Exception as e:
        return f"Error checking {file_path}: {str(e)}"

def scan_directory(directory):
    results = []
    print(f"Starting scan of {directory}...")
    try:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    print(f"Checking {full_path}")
                    result = check_file_for_null_bytes(full_path)
                    if result:
                        results.append(result)
                        print(result)
    except Exception as e:
        print(f"Error scanning directory {directory}: {str(e)}")
    return results

if __name__ == "__main__":
    directories = ['src', 'tests']
    for directory in directories:
        print(f"\nScanning {directory}...")
        results = scan_directory(directory)
        if results:
            print(f"Found {len(results)} files with null bytes in {directory}:")
            for result in results:
                print(f"  {result}")
        else:
            print(f"No null bytes found in {directory}")
    print("\nScan complete.") 
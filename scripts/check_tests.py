import os

def check_file_for_null_bytes(file_path):
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            if b'\x00' in content:
                null_positions = [i for i, byte in enumerate(content) if byte == 0]
                print(f'Found {len(null_positions)} null bytes in {file_path} at positions: {null_positions[:10]}...')
                return True
            return False
    except Exception as e:
        print(f'Error checking {file_path}: {str(e)}')
        return False

# Check tests directory
print('Checking tests directory...')
for root, _, files in os.walk('tests'):
    for file in files:
        if file.endswith('.py'):
            full_path = os.path.join(root, file)
            print(f'Checking {full_path}')
            check_file_for_null_bytes(full_path) 
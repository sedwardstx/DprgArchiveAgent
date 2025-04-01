def convert_utf16_to_utf8(file_path):
    """Convert a UTF-16 encoded file to UTF-8 encoding."""
    # Read the content with UTF-16 encoding
    with open(file_path, 'r', encoding='utf-16') as file:
        content = file.read()
    
    # Write the content with UTF-8 encoding
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"Successfully converted {file_path} from UTF-16 to UTF-8 encoding.")

if __name__ == "__main__":
    file_path = "src/schema/models.py"
    convert_utf16_to_utf8(file_path) 
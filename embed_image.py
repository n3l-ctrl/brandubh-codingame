import base64
import re

# Read the image and encode to base64
with open('config/cover.png', 'rb') as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

bg_url = f"data:image/png;base64,{encoded_string}"

def replace_in_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace the background-image url(...) with the base64 string
    content = re.sub(
        r'background-image:\s*url\([^)]+\)',
        f'background-image: url({bg_url})',
        content
    )
    
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

replace_in_file('config/statement_en.html')
replace_in_file('config/statement_fr.html')

print("Successfully embedded base64 image into statements.")

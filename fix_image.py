import re

def replace_in_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace the background-image url(...) with the relative URL
    content = re.sub(
        r'background-image:\s*url\([^)]+\)',
        f'background-image: url(/assets/cover.png)',
        content
    )
    
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

replace_in_file('config/statement_en.html')
replace_in_file('config/statement_fr.html')

print("Successfully replaced base64 image with /assets/cover.png in statements.")

import urllib.request
import os

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import sys
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image, ImageDraw, ImageFont

url = 'https://github.com/google/fonts/raw/main/ofl/uncialantiqua/UncialAntiqua-Regular.ttf'
font_path = 'UncialAntiqua-Regular.ttf'
if not os.path.exists(font_path):
    urllib.request.urlretrieve(url, font_path)

font_title = ImageFont.truetype(font_path, 180)
font_sub = ImageFont.truetype(font_path, 80)

def create_text_image(text, font, fill_color, shadow_offset, filename):
    tb = font.getbbox(text)
    w = tb[2] - tb[0] + 40
    h = tb[3] - tb[1] + 40
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    tx = 20
    ty = 20
    
    # Shadow
    draw.text((tx + shadow_offset, ty + shadow_offset), text, font=font, fill=(0, 0, 0, 180))
    
    # Stroke
    stroke_w = shadow_offset // 2
    if stroke_w < 2: stroke_w = 2
    for dx in [-stroke_w, 0, stroke_w]:
        for dy in [-stroke_w, 0, stroke_w]:
            draw.text((tx + dx, ty + dy), text, font=font, fill=(20, 20, 20, 255))
            
    # Text
    draw.text((tx, ty), text, font=font, fill=fill_color)
    
    out_path = os.path.join(r'c:\AGrav\Brandubh\brandubh-game\src\main\resources\view\assets', filename)
    img.save(out_path)
    print('Saved', out_path)

create_text_image('BRANDUBH', font_title, (255, 215, 0, 255), 6, 'title.png')
create_text_image('Game of the Irish Kings', font_sub, (255, 230, 100, 255), 4, 'subtitle.png')

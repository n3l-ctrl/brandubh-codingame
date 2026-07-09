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

W, H = 1200, 400
img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

font_title = ImageFont.truetype(font_path, 180)
font_sub = ImageFont.truetype(font_path, 80)

title = 'BRANDUBH'
sub = 'Game of the Irish Kings'

# Bounding boxes
tb = font_title.getbbox(title)
sb = font_sub.getbbox(sub)

tw = tb[2] - tb[0]
th = tb[3] - tb[1]
sw = sb[2] - sb[0]
sh = sb[3] - sb[1]

tx = (W - tw) // 2
ty = 20

shadow_offset = 6
draw.text((tx + shadow_offset, ty + shadow_offset), title, font=font_title, fill=(0, 0, 0, 180))

stroke_w = 4
for dx in [-stroke_w, 0, stroke_w]:
    for dy in [-stroke_w, 0, stroke_w]:
        draw.text((tx + dx, ty + dy), title, font=font_title, fill=(20, 20, 20, 255))

draw.text((tx, ty), title, font=font_title, fill=(255, 215, 0, 255))

sx = (W - sw) // 2
sy = ty + th + 60

draw.text((sx + shadow_offset//2, sy + shadow_offset//2), sub, font=font_sub, fill=(0, 0, 0, 180))

stroke_w = 2
for dx in [-stroke_w, 0, stroke_w]:
    for dy in [-stroke_w, 0, stroke_w]:
        draw.text((sx + dx, sy + dy), sub, font=font_sub, fill=(20, 20, 20, 255))

draw.text((sx, sy), sub, font=font_sub, fill=(255, 230, 100, 255))

out_path = r'c:\AGrav\Brandubh\brandubh-game\src\main\resources\view\assets\title.png'
img.save(out_path)
print('Saved', out_path)

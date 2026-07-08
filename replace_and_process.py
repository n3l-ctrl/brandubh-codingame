import os
import shutil
from PIL import Image, ImageDraw

brain_dir = r"C:\Users\EmDev\.gemini\antigravity\brain\c0e4e2a3-9767-4499-b595-daf7710cfd03"
assets_dir = r"c:\AGrav\Brandubh\brandubh-game\src\main\resources\view\assets"

files = {
    "king_piece_1783291448990.png": "king.png",
    "defender_piece_1783291455970.png": "defender.png",
    "attacker_piece_1783291463050.png": "attacker.png"
}

def make_circle_transparent(img_path):
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    
    # We want a circle in the center. We use a mask.
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    
    # AI tokens usually have a shadow. We'll crop slightly inside to ensure pure token.
    # Radius is w/2 * 0.95
    center_x, center_y = w / 2, h / 2
    r = (min(w, h) / 2) * 0.95
    
    left, top, right, bottom = center_x - r, center_y - r, center_x + r, center_y + r
    draw.ellipse((left, top, right, bottom), fill=255)
    
    result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    result.paste(img, (0, 0), mask=mask)
    
    # Crop to the bounding box of the non-transparent area
    bbox = result.getbbox()
    if bbox:
        result = result.crop(bbox)
        
    result.save(img_path)

for src_name, dst_name in files.items():
    src = os.path.join(brain_dir, src_name)
    dst = os.path.join(assets_dir, dst_name)
    shutil.copy2(src, dst)
    make_circle_transparent(dst)
    print(f"Processed {dst_name}")

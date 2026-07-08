from PIL import Image, ImageDraw
import os

assets_dir = r"c:\AGrav\Brandubh\brandubh-game\src\main\resources\view\assets"

def apply_tighter_mask(img_name, scale_factor=0.85):
    img_path = os.path.join(assets_dir, img_name)
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    
    # Create a new transparent image
    result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    
    # Calculate circle bounds
    center_x, center_y = w / 2, h / 2
    # Radius based on the smallest dimension
    r = (min(w, h) / 2) * scale_factor
    
    # Create mask
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((center_x - r, center_y - r, center_x + r, center_y + r), fill=255)
    
    # Apply mask
    result.paste(img, (0, 0), mask)
    
    # Crop to the actual circle to remove the empty space
    # This prevents the piece from looking smaller than the attacker if we just mask it
    left, top, right, bottom = center_x - r, center_y - r, center_x + r, center_y + r
    result = result.crop((left, top, right, bottom))
    
    result.save(img_path)
    print(f"Applied tighter mask to {img_name}")

apply_tighter_mask("defender.png", 0.75)
apply_tighter_mask("king.png", 0.75)

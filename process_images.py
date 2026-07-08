from PIL import Image, ImageDraw
import glob
import os

assets_dir = r"c:\AGrav\Brandubh\brandubh-game\src\main\resources\view\assets"

def make_circle_transparent(img_path):
    img = Image.open(img_path).convert("RGBA")
    width, height = img.size
    
    # Create a circular mask
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)
    # The piece might have a slight border, let's mask out the corners
    # Draw a circle that fits exactly in the bounding box
    draw.ellipse((0, 0, width, height), fill=255)
    
    # Apply mask
    result = img.copy()
    result.putalpha(mask)
    
    # Save back
    result.save(img_path)
    print(f"Processed {os.path.basename(img_path)}")

# Apply to pieces
make_circle_transparent(os.path.join(assets_dir, "attacker.png"))
make_circle_transparent(os.path.join(assets_dir, "defender.png"))
make_circle_transparent(os.path.join(assets_dir, "king.png"))

# Crop board
board_path = os.path.join(assets_dir, "board.png")
board_img = Image.open(board_path).convert("RGBA")
w, h = board_img.size
# Let's crop the central 70% of the image to remove the table and keep just the carved board
crop_margin = int(w * 0.15)
cropped_board = board_img.crop((crop_margin, crop_margin, w - crop_margin, h - crop_margin))
cropped_board.save(board_path)
print("Cropped board.png")

from PIL import Image
import os

assets_dir = r"c:\AGrav\Brandubh\brandubh-game\src\main\resources\view\assets"

def remove_white_bg(img_path):
    img = Image.open(img_path).convert("RGBA")
    datas = img.getdata()
    
    newData = []
    # DALL-E white background is usually pure white or very close
    for item in datas:
        # Check if pixel is near white
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
            
    img.putdata(newData)
    
    # Now find the bounding box of non-transparent pixels
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        
    img.save(img_path)
    print(f"Removed white bg and cropped {os.path.basename(img_path)}")

remove_white_bg(os.path.join(assets_dir, "attacker.png"))
remove_white_bg(os.path.join(assets_dir, "defender.png"))
remove_white_bg(os.path.join(assets_dir, "king.png"))

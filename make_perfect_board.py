from PIL import Image, ImageDraw, ImageFilter

# Load the plain wood texture
bg_path = r"C:\Users\EmDev\.gemini\antigravity\brain\c0e4e2a3-9767-4499-b595-daf7710cfd03\plain_wood_board_1783291154481.png"
output_path = r"c:\AGrav\Brandubh\brandubh-game\src\main\resources\view\assets\board.png"

try:
    img = Image.open(bg_path).convert("RGBA")
    img = img.resize((1000, 1000))
except Exception as e:
    print(f"Error loading image: {e}")
    # Create a brown fallback image
    img = Image.new("RGBA", (1000, 1000), (139, 69, 19, 255))

draw = ImageDraw.Draw(img)

# The board is 1000x1000. We want the grid to be centered.
# The grid has 7 cells. We set CELL_SIZE in Referee to 126.
# 7 * 126 = 882.
# So grid starts at (1000 - 882) / 2 = 59
# and ends at 59 + 882 = 941

start = 59
end = 941
cell_size = 126

# Draw carved lines
for i in range(8):
    pos = start + i * cell_size
    
    # Highlight (bottom/right edge for depth)
    draw.line([(pos+2, start), (pos+2, end)], fill=(200, 160, 100, 150), width=2)
    draw.line([(start, pos+2), (end, pos+2)], fill=(200, 160, 100, 150), width=2)
    
    # Shadow (top/left edge for depth)
    draw.line([(pos-2, start), (pos-2, end)], fill=(30, 15, 0, 200), width=2)
    draw.line([(start, pos-2), (end, pos-2)], fill=(30, 15, 0, 200), width=2)
    
    # Center dark line
    draw.line([(pos, start), (pos, end)], fill=(0, 0, 0, 255), width=4)
    draw.line([(start, pos), (end, pos)], fill=(0, 0, 0, 255), width=4)

# Highlight Throne (center) and Corners
corners = [(0,0), (6,0), (0,6), (6,6)]
throne = (3,3)

def draw_special_cell(cell_x, cell_y, color):
    x1 = start + cell_x * cell_size
    y1 = start + cell_y * cell_size
    x2 = x1 + cell_size
    y2 = y1 + cell_size
    # Draw a semi-transparent overlay
    overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
    d = ImageDraw.Draw(overlay)
    d.rectangle([x1, y1, x2, y2], fill=color)
    return Image.alpha_composite(img, overlay)

for cx, cy in corners:
    img = draw_special_cell(cx, cy, (150, 0, 0, 60))

img = draw_special_cell(throne[0], throne[1], (255, 215, 0, 60))

img.save(output_path)
print("Perfect mathematical board generated and saved.")

import sys, os, json
from PIL import Image
base = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(base)
out = sys.argv[1]
slugs = json.load(open(os.path.join(base, "slugs.json")))
W, H = 360, 450
sheet = Image.new("RGB", (W * 7 + 16 * 8, (H + 16) * len(slugs) + 16), (40, 40, 40))
for r, s in enumerate(slugs):
    for c in range(7):
        im = Image.open(os.path.join(root, s, f"slide-{c+1:02d}.png")).resize((W, H))
        sheet.paste(im, (16 + c * (W + 16), 16 + r * (H + 16)))
sheet.save(out)

"""하린 원본 그림(흰 배경)에서 배경을 지우고 가벼운 webp로 저장한다.
사용: python3 tools/cutout.py 원본.png 저장이름 [--keep-bg] [--protect 변:시작-끝 ...]
  --protect left:0.45-0.8  왼쪽 변의 45~80% 구간에 닿은 흰 부분(예: 종이)은 배경으로 보지 않는다.
  변 이름: top, bottom, left, right
"""
import sys, numpy as np
from PIL import Image
from scipy import ndimage

src, name = sys.argv[1], sys.argv[2]
keep_bg = '--keep-bg' in sys.argv
im = Image.open(src).convert('RGB')
H = 900
im = im.resize((round(im.width * H / im.height), H), Image.LANCZOS)
out = f'/home/claude/teachme/assets/harin/{name}.webp'
if keep_bg:
    im.save(out, 'WEBP', quality=80)
    sys.exit()
a = np.asarray(im).astype(np.float32)
mn = a.min(axis=2)
white = mn > 236
lab, _ = ndimage.label(white)
h, w = mn.shape
edges = {'top': lab[0, :], 'bottom': lab[-1, :], 'left': lab[:, 0], 'right': lab[:, -1]}
protect = {}
args = sys.argv[3:]
for i, x in enumerate(args):
    if x == '--protect':
        side, rng = args[i + 1].split(':')
        lo, hi = map(float, rng.split('-'))
        protect.setdefault(side, []).append((lo, hi))
seeds = set()
for side, line in edges.items():
    n = len(line)
    for k, v in enumerate(line):
        if v and not any(lo <= k / n <= hi for lo, hi in protect.get(side, [])):
            seeds.add(int(v))
bg = np.isin(lab, list(seeds))
near = ndimage.binary_dilation(bg, iterations=2) & ~bg
alpha = np.ones(mn.shape, np.float32)
alpha[bg] = 0
soft = np.clip((255 - mn) / (255 - 200), 0, 1)
alpha[near] = soft[near]
aa = np.maximum(alpha, 1e-3)[..., None]
rgb = np.clip((a - 255 * (1 - aa)) / aa, 0, 255)
rgba = np.dstack([rgb, alpha * 255]).astype(np.uint8)
img = Image.fromarray(rgba, 'RGBA')
img = img.crop(img.getbbox())
img.save(out, 'WEBP', quality=82)

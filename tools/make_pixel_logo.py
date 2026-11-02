"""타이틀 화면의 픽셀 로고(Teach me!)를 그린다.

글자를 한 칸씩 찍은 도트 그림이라 작게 저장해도 화면에서 깨지지 않게 확대된다.
실행: python3 tools/make_pixel_logo.py        -> assets/title/logo.png (게임용)
      python3 tools/make_pixel_logo.py 24     -> assets/title/logo-x24.png (썸네일·발표용 큰 PNG)
그 뒤 python3 tools/embed_sprites.py 로 HTML에 다시 넣는다.
"""
import numpy as np
from PIL import Image
from scipy import ndimage
H=12
G={
'T':["##########"]*2+["....##...."]*10,
'e':[""]*4+[".######.","##....##","##....##","########","##......","##......","##....##",".######."],
'a':[""]*4+[".######.","......##","......##",".#######","##....##","##....##","##...###",".#######"],
'c':[""]*4+[".######.","##....##","##......","##......","##......","##......","##....##",".######."],
'h':["##......"]*4+["##.####.","###...##"]+["##....##"]*6,
'm':[""]*4+["#########.","##..##..##"]+["##..##..##"]*6,
'!':["##"]*9+[".."]+["##"]*2,
}
HEART=[".##.##.","#######","#######",".#####.","..###..","...#..."]
def glyph(c):
    rows=G[c]; w=max(len(r) for r in rows)
    a=np.zeros((H,w),bool)
    for y,r in enumerate(rows):
        for x,ch in enumerate(r):
            if ch=='#': a[y,x]=True
    return a
def word(s,gap=3):
    parts=[]
    for i,c in enumerate(s):
        parts.append(glyph(c))
        if i<len(s)-1: parts.append(np.zeros((H,gap),bool))
    return np.hstack(parts)
l1=word("Teach"); l2=word("me!")
hb=np.zeros((H,7),bool); hb[3:9]=np.array([[ch=='#' for ch in r] for r in HEART])
l2full=np.hstack([hb,np.zeros((H,4),bool),l2])
W=max(l1.shape[1],l2full.shape[1]); lg=4
pad=5
canvas_h=pad*2+H*2+lg; canvas_w=W+pad*2+2
M=np.zeros((canvas_h,canvas_w),bool); HM=np.zeros_like(M)
M[pad:pad+H,pad:pad+l1.shape[1]]=l1
x2=pad+W-l2full.shape[1]; y2=pad+H+lg
M[y2:y2+H,x2+11:x2+l2full.shape[1]]=l2
HM[y2:y2+H,x2:x2+7]=hb[:, :7]
ALL=M|HM
sq=np.ones((3,3),bool)
d1=ndimage.binary_fill_holes(ndimage.binary_dilation(ALL,sq)); d2=ndimage.binary_fill_holes(ndimage.binary_dilation(d1,sq)); d3=ndimage.binary_fill_holes(ndimage.binary_dilation(d2,sq))
img=np.zeros((canvas_h,canvas_w,4),np.uint8)
def put(mask,col):
    img[mask]=col
navy=(30,42,92,255); yel=(255,226,122,255); white=(255,255,255,255)
sh=np.zeros_like(d3); sh[2:,2:]=d3[:-2,:-2]
put(sh,yel); put(d3,navy); put(d2,white); put(d1,navy)
bands=[(0,5,(240,108,155,255)),(5,8,(255,152,188,255)),(8,9,(255,215,166,255)),(9,12,(255,226,122,255))]
for top in (pad,y2):
    for a,b,col in bands:
        m=np.zeros_like(M); m[top+a:top+b]=True
        put(M&m,col)
put(HM,(240,108,155,255))
hx,hy=x2,y2+3
img[hy+1,hx+1]=white; img[hy+3,hx+2:hx+5]=yel; img[hy+4,hx+3]=yel
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
S = int(sys.argv[1]) if len(sys.argv) > 1 else 1  # 1 = 게임용 원본(화면에서 픽셀 그대로 확대), 24 = 큰 PNG
out = Image.fromarray(img, 'RGBA').resize((canvas_w * S, canvas_h * S), Image.NEAREST)
name = 'logo.png' if S == 1 else 'logo-x%d.png' % S
out.save(ROOT / 'assets' / 'title' / name)
print('저장:', name, out.size)

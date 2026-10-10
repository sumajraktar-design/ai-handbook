"""第 1 课线稿风格样片：逐帧绘制，通过管道交给 ffmpeg 编码成 MP4。

风格：浅色纸面、黑色手绘线条（带轻微抖动）、逐笔"画出来"的动画，蓝色标重点，红色标错误。
运行：python3 lesson01_sample.py out.mp4
"""
import math
import random
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

W, H, S, FPS = 1280, 720, 2, 30          # S：超采样倍数，画完缩小以得到平滑线条
BG = (248, 247, 243)
INK = (32, 34, 40)
SOFT = (150, 152, 158)
BLUE = (44, 89, 224)
RED = (205, 58, 48)
GREEN = (30, 132, 86)
MARK = (255, 220, 90)
FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
FONT_B = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
_fonts = {}


def font(size, bold=False):
    k = (size, bold)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(FONT_B if bold else FONT, int(size * S))
    return _fonts[k]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def seg(t, a, b):
    """t 在 [a, b] 区间内的进度 0..1"""
    return clamp((t - a) / (b - a)) if b > a else float(t >= a)


def mix(c1, c2, k):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * k) for i in range(3))


# ── 手绘线条 ─────────────────────────────────────────────
def rough_line(p0, p1, seed, amp=1.4, n=None):
    rnd = random.Random(seed)
    L = math.dist(p0, p1)
    n = n or max(2, int(L / 18))
    nx, ny = (-(p1[1] - p0[1]) / (L or 1), (p1[0] - p0[0]) / (L or 1))
    pts = []
    for i in range(n + 1):
        t = i / n
        off = (rnd.random() - 0.5) * 2 * amp * math.sin(math.pi * t)
        pts.append((p0[0] + (p1[0] - p0[0]) * t + nx * off, p0[1] + (p1[1] - p0[1]) * t + ny * off))
    return pts


def rough_poly(points, seed, closed=False, amp=1.4):
    pts = list(points) + ([points[0]] if closed else [])
    out = []
    for i in range(len(pts) - 1):
        part = rough_line(pts[i], pts[i + 1], seed + i, amp)
        out += part if i == 0 else part[1:]
    return out


def rough_circle(cx, cy, rx, ry=None, seed=0, turns=1.06, amp=1.6):
    ry = ry or rx
    rnd = random.Random(seed)
    start = rnd.random() * math.tau
    n = 64
    return [(cx + (rx + (rnd.random() - .5) * amp * 2) * math.cos(start + turns * math.tau * i / n),
             cy + (ry + (rnd.random() - .5) * amp * 2) * math.sin(start + turns * math.tau * i / n)) for i in range(n + 1)]


def draw_path(d, pts, prog=1.0, color=INK, width=3):
    """只画出路径的前 prog 部分，形成"正在画"的效果"""
    if prog <= 0 or len(pts) < 2:
        return
    lens = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total, acc, out = sum(lens) * clamp(prog), 0.0, [pts[0]]
    for i, l in enumerate(lens):
        if acc + l >= total:
            k = (total - acc) / l if l else 0
            out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * k, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * k))
            break
        out.append(pts[i + 1])
        acc += l
    d.line([(x * S, y * S) for x, y in out], fill=color, width=int(width * S), joint='curve')
    r = width * S / 2
    for x, y in (out[0], out[-1]):
        d.ellipse((x * S - r, y * S - r, x * S + r, y * S + r), fill=color)


def dashed(d, p0, p1, color, width=2, dash=8, gap=6, prog=1.0):
    L = math.dist(p0, p1) * clamp(prog)
    if L <= 0:
        return
    ux, uy = (p1[0] - p0[0]) / math.dist(p0, p1), (p1[1] - p0[1]) / math.dist(p0, p1)
    s = 0
    while s < L:
        e = min(s + dash, L)
        d.line([((p0[0] + ux * s) * S, (p0[1] + uy * s) * S), ((p0[0] + ux * e) * S, (p0[1] + uy * e) * S)], fill=color, width=int(width * S))
        s += dash + gap


def text(d, xy, s, size, color=INK, prog=1.0, bold=False, anchor='la'):
    n = math.ceil(len(s) * clamp(prog))
    if n <= 0:
        return
    d.text((xy[0] * S, xy[1] * S), s[:n], font=font(size, bold), fill=color, anchor=anchor)


def text_w(s, size, bold=False):
    return font(size, bold).getlength(s) / S


def tick(d, x, y, prog, color=GREEN, seed=0, sz=14):
    draw_path(d, rough_poly([(x, y), (x + sz * .4, y + sz * .45), (x + sz, y - sz * .55)], seed, amp=.6), prog, color, 3)


def cross(d, x, y, r, prog, color=RED, seed=0, width=5):
    draw_path(d, rough_line((x - r, y - r), (x + r, y + r), seed, 2), seg(prog, 0, .5), color, width)
    draw_path(d, rough_line((x + r, y - r), (x - r, y + r), seed + 9, 2), seg(prog, .5, 1), color, width)


# ── 场景 1：标题 ─────────────────────────────────────────
def scene_title(d, t):
    text(d, (640, 250), '第 1 课', 30, SOFT, seg(t, 0, .6), anchor='mm')
    text(d, (640, 330), '机器怎么学会一件事', 64, INK, seg(t, .4, 2.0), bold=True, anchor='mm')
    w = text_w('机器怎么学会一件事', 64, True)
    draw_path(d, rough_line((640 - w / 2, 380), (640 + w / 2, 386), 7, 2.5), ease(seg(t, 2.0, 3.0)), BLUE, 5)
    text(d, (640, 440), '一台不会思考的机器，是怎么学会"猜"的？', 28, SOFT, seg(t, 3.0, 4.6), anchor='mm')


# ── 场景 2：猜下一个字 ──────────────────────────────────
CANDS1 = [('好', 52), ('热', 17), ('冷', 12), ('不错', 9), ('糟糕', 6)]
CANDS2 = [('，', 41), ('！', 29), ('。', 18), ('啊', 12)]


def bars(d, cands, t0, t, y0=300, hl_first=False, fade=1.0):
    for i, (w, p) in enumerate(cands):
        k = seg(t, t0 + i * .35, t0 + i * .35 + .9)
        if k <= 0:
            continue
        y = y0 + i * 62
        col = mix(BG, INK, fade)
        text(d, (300, y + 20), w, 32, col, 1, anchor='rm')
        bw = p * 11 * ease(k)
        box = [(330, y), (330 + bw, y), (330 + bw, y + 38), (330, y + 38)]
        lc = mix(BG, BLUE if (hl_first and i == 0) else INK, fade)
        draw_path(d, rough_poly(box, 100 + i, closed=True, amp=.8), 1, lc, 2.5)
        # 斜线填充
        for x in range(338, int(330 + bw) - 2, 12):
            d.line([(x * S, (y + 36) * S), ((x + 10) * S, (y + 2) * S)], fill=mix(BG, lc, .55), width=int(1.6 * S))
        text(d, (330 + bw + 14, y + 20), f'{p}%', 24, mix(BG, SOFT, fade), seg(t, t0 + i * .35 + .6, t0 + i * .35 + 1.0), anchor='lm')


def scene_next(d, t):
    base = '今天天气真'
    x0, y0 = 200, 170
    text(d, (x0, y0), base, 56, INK, seg(t, 0, 1.6), bold=True, anchor='lm')
    bw = text_w(base, 56, True)
    added = ''
    if t > 9.6:
        added = '好'
    if t > 15.2:
        added = '好，'
    if t > 16.4:
        tail = '适合出去走走。'
        added = '好，' + tail[:math.ceil(len(tail) * seg(t, 16.4, 19.0))]
    text(d, (x0 + bw, y0), added, 56, BLUE, 1, bold=True, anchor='lm')
    cw = text_w(added, 56, True) if added else 0
    if int(t * 2.4) % 2 == 0 and t > 1.6:   # 光标闪烁
        d.line([((x0 + bw + cw + 6) * S, (y0 - 30) * S), ((x0 + bw + cw + 6) * S, (y0 + 30) * S)], fill=BLUE, width=3 * S)
    if t < 12.2:
        fade = 1 - seg(t, 11.6, 12.2)
        bars(d, CANDS1, 2.2, t, hl_first=True, fade=fade)
        if 7.6 < t < 12.2:   # 圈出概率最高的"好"
            draw_path(d, rough_circle(287, 320, 40, 32, seed=3), ease(seg(t, 7.6, 8.6)), mix(BG, BLUE, fade), 3.5)
            draw_path(d, rough_poly([(287, 280), (300, 230), (x0 + bw + 10, 205)], 21, amp=1.2), ease(seg(t, 8.6, 9.5)), mix(BG, BLUE, fade), 3)
    elif t < 15.4:
        bars(d, CANDS2, 12.3, t, hl_first=True, fade=1 - seg(t, 14.8, 15.4))
    if t > 19.2:
        text(d, (640, 470), '根据前面的字，猜下一个字', 40, INK, seg(t, 19.2, 20.6), bold=True, anchor='mm')
        w = text_w('根据前面的字，猜下一个字', 40, True)
        draw_path(d, rough_line((640 - w / 2, 500), (640 + w / 2, 503), 41, 2), ease(seg(t, 20.6, 21.4)), MARK, 9)


# ── 场景 3：写规则认猫 ──────────────────────────────────
def draw_cat(d, cx, cy, p, seed=0, color=INK):
    strokes = [
        rough_circle(cx, cy, 78, 70, seed),
        rough_poly([(cx - 66, cy - 30), (cx - 58, cy - 108), (cx - 18, cy - 66)], seed + 1),
        rough_poly([(cx + 66, cy - 30), (cx + 58, cy - 108), (cx + 18, cy - 66)], seed + 2),
        rough_circle(cx - 28, cy - 10, 7, seed=seed + 3, amp=.5), rough_circle(cx + 28, cy - 10, 7, seed=seed + 4, amp=.5),
        rough_poly([(cx - 7, cy + 12), (cx + 7, cy + 12), (cx, cy + 20), (cx - 7, cy + 12)], seed + 5, amp=.4),
        rough_poly([(cx - 18, cy + 34), (cx, cy + 22), (cx + 18, cy + 34)], seed + 6, amp=.5),
    ] + [rough_line((cx + sgn * 26, cy + 18 + k * 9), (cx + sgn * 104, cy + 6 + k * 16), seed + 10 + k + (sgn > 0) * 5, .8)
         for sgn in (-1, 1) for k in range(3)]
    for i, st in enumerate(strokes):
        draw_path(d, st, seg(p, i / len(strokes), (i + 1) / len(strokes)), color, 3)


def draw_fox(d, cx, cy, p, seed=50, color=INK):
    strokes = [
        rough_poly([(cx - 86, cy - 28), (cx - 40, cy + 46), (cx, cy + 92), (cx + 40, cy + 46), (cx + 86, cy - 28), (cx + 30, cy - 52), (cx - 30, cy - 52)], seed, closed=True),
        rough_poly([(cx - 74, cy - 34), (cx - 70, cy - 132), (cx - 26, cy - 52)], seed + 1),
        rough_poly([(cx + 74, cy - 34), (cx + 70, cy - 132), (cx + 26, cy - 52)], seed + 2),
        rough_circle(cx - 30, cy - 8, 7, seed=seed + 3, amp=.5), rough_circle(cx + 30, cy - 8, 7, seed=seed + 4, amp=.5),
        rough_circle(cx, cy + 84, 8, seed=seed + 5, amp=.4),
    ] + [rough_line((cx + sgn * 20, cy + 62 + k * 7), (cx + sgn * 100, cy + 44 + k * 14), seed + 10 + k + (sgn > 0) * 5, .8)
         for sgn in (-1, 1) for k in range(3)]
    for i, st in enumerate(strokes):
        draw_path(d, st, seg(p, i / len(strokes), (i + 1) / len(strokes)), color, 3)


RULES = ['尖耳朵', '有胡须', '毛茸茸', '有尾巴']


def scene_rules(d, t):
    text(d, (640, 92), '能不能写规则，教电脑认猫？', 38, INK, seg(t, 0, 1.4), bold=True, anchor='mm')
    draw_cat(d, 250, 360, seg(t, 1.0, 4.6))
    text(d, (250, 500), '家猫', 26, SOFT, seg(t, 4.2, 4.8), anchor='mm')
    draw_fox(d, 520, 360, seg(t, 9.6, 13.4))
    text(d, (520, 500), '狐狸', 26, SOFT, seg(t, 13.0, 13.6), anchor='mm')
    # 规则清单
    text(d, (760, 190), '规则：全部满足就是猫', 26, SOFT, seg(t, 4.4, 5.4))
    for i, r in enumerate(RULES):
        a = 5.2 + i * .7
        text(d, (820, 250 + i * 54), r, 30, INK, seg(t, a, a + .5))
        tick(d, 770, 262 + i * 54, seg(t, a + .2, a + .6), seed=i)
        tick(d, 1000, 262 + i * 54, seg(t, 14.0 + i * .5, 14.5 + i * .5), color=RED, seed=i + 7)
    text(d, (770, 230 - 8), '猫', 18, SOFT, seg(t, 5.0, 5.4))
    text(d, (995, 230 - 8), '狐狸', 18, SOFT, seg(t, 13.8, 14.2))
    text(d, (760, 490), '→ 是猫', 32, GREEN, seg(t, 8.2, 8.8), bold=True)
    text(d, (990, 490), '→ 也是猫？', 32, RED, seg(t, 16.2, 16.8), bold=True)
    if t > 17:
        cross(d, 520, 360, 110, ease(seg(t, 17.0, 18.0)), seed=4, width=7)


# ── 场景 4：给例子，拟合直线 ────────────────────────────
AREA = [42, 50, 55, 61, 68, 74, 80, 86, 93, 99, 105, 112, 118, 125, 131, 138]
NOISE = [18, -22, 9, -14, 25, -6, -28, 12, 30, -17, 4, -25, 16, -9, 21, -12]
PRICE = [3 * a + 20 + NOISE[i] for i, a in enumerate(AREA)]
LX, RX = 40, 140


def gd_path():
    """在两个把手高度（a, b）上做梯度下降，记录每一步，用来驱动动画"""
    a, b, out = 150.0, 180.0, []
    for _ in range(40):
        out.append((a, b))
        ga = gb = 0.0
        for x, y in zip(AREA, PRICE):
            f = a + (b - a) * (x - LX) / (RX - LX)
            tt = (x - LX) / (RX - LX)
            ga += (f - y) * (1 - tt)
            gb += (f - y) * tt
        a -= 0.3 * ga / len(AREA) * 2      # 学习率取小一点，让收敛过程在画面上看得清
        b -= 0.3 * gb / len(AREA) * 2
    return out


PATH = gd_path()


def rmse(a, b):
    return math.sqrt(sum((a + (b - a) * (x - LX) / (RX - LX) - y) ** 2 for x, y in zip(AREA, PRICE)) / len(AREA))


def scene_fit(d, t):
    text(d, (640, 76), '换个思路：不写规则，给它看例子', 36, INK, seg(t, 0, 1.4), bold=True, anchor='mm')
    X0, X1, Y0, Y1 = 150, 900, 610, 150
    X = lambda v: X0 + (v - 30) / 120 * (X1 - X0)
    Y = lambda v: Y0 - v / 500 * (Y0 - Y1)
    draw_path(d, rough_line((X0, Y0), (X1 + 20, Y0), 1, 1), ease(seg(t, 1, 2)), INK, 3)
    draw_path(d, rough_line((X0, Y0), (X0, Y1 - 20), 2, 1), ease(seg(t, 1, 2)), INK, 3)
    text(d, (X1 + 30, Y0 - 22), '面积', 22, SOFT, seg(t, 1.8, 2.2), anchor='mm')
    text(d, (X0 - 10, Y1 - 36), '价格', 22, SOFT, seg(t, 1.8, 2.2), anchor='mm')
    for i, (x, y) in enumerate(zip(AREA, PRICE)):
        k = seg(t, 2.4 + i * .1, 2.7 + i * .1)
        if k > 0:
            r = 7 * ease(k)
            d.ellipse(((X(x) - r) * S, (Y(y) - r) * S, (X(x) + r) * S, (Y(y) + r) * S), outline=BLUE, width=int(2.5 * S))
    # 当前参数：t<9 停在初始；9~20 沿梯度下降轨迹移动
    steps = 16
    u = seg(t, 9, 20) * steps
    i = min(int(u), steps - 1)
    f = u - int(u) if u < steps else 1
    a = PATH[i][0] + (PATH[i + 1][0] - PATH[i][0]) * ease(f)
    b = PATH[i][1] + (PATH[i + 1][1] - PATH[i][1]) * ease(f)
    line = lambda x: a + (b - a) * (x - LX) / (RX - LX)
    if t > 5:
        draw_path(d, rough_line((X(32), Y(line(32))), (X(148), Y(line(148))), 77, .6), ease(seg(t, 5, 6.4)), INK, 4)
    if t > 7:
        for j, (x, y) in enumerate(zip(AREA, PRICE)):
            dashed(d, (X(x), Y(y)), (X(x), Y(line(x))), RED, 2, prog=seg(t, 7 + j * .05, 7.6 + j * .05))
        text(d, (960, 470), '平均猜错', 24, SOFT, seg(t, 7.4, 7.8))
        text(d, (960, 500), f'{rmse(a, b):.0f} 万元', 40, RED, seg(t, 7.6, 8.0), bold=True)
    # 两个旋钮：倾斜程度、整体高度
    if t > 3:
        for k, (label, val, lo, hi) in enumerate([('倾斜程度', (b - a) / 100, 0, 4), ('整体高度', a, 0, 300)]):
            cx, cy = 1010 + k * 140, 260
            p = seg(t, 3 + k * .3, 4 + k * .3)
            draw_path(d, rough_circle(cx, cy, 44, seed=60 + k), ease(p), INK, 3)
            ang = math.radians(-225 + 270 * clamp((val - lo) / (hi - lo)))
            if p >= 1:
                draw_path(d, [(cx, cy), (cx + 32 * math.cos(ang), cy + 32 * math.sin(ang))], 1, BLUE, 4)
            text(d, (cx, cy + 74), label, 20, SOFT, p, anchor='mm')
        text(d, (1080, 180), '模型的参数 = 旋钮', 22, INK, seg(t, 4.2, 5.2), bold=True, anchor='mm')
    if t > 9 and t < 20:
        text(d, (960, 560), f'第 {min(int(u) + 1, steps)} 步', 24, BLUE, 1)


# ── 场景 5：结尾 ─────────────────────────────────────────
def scene_end(d, t):
    text(d, (640, 300), '学会 = 把旋钮拧到合适的位置', 46, INK, seg(t, 0, 1.6), bold=True, anchor='mm')
    w = text_w('学会 = 把旋钮拧到合适的位置', 46, True)
    draw_path(d, rough_line((640 - w / 2, 340), (640 + w / 2, 344), 91, 2), ease(seg(t, 1.6, 2.4)), MARK, 10)
    text(d, (640, 420), '下一段：错了多少怎么算？机器怎么"下山"？', 28, SOFT, seg(t, 2.6, 4.0), anchor='mm')
    text(d, (640, 640), '线稿风格样片 · 第 1 课前半段', 18, SOFT, seg(t, 3.6, 4.2), anchor='mm')


SCENES = [(5.5, scene_title), (23, scene_next), (21, scene_rules), (24, scene_fit), (6.5, scene_end)]
CAPTIONS = [
    (5.8, 11.5, '给大模型半句话'), (11.5, 17.6, '它给每一个可能的下一个字打分，变成概率'), (17.6, 24.3, '挑一个接上去，再猜下一个……'),
    (24.3, 28.5, '大模型做的事情，说穿了只有这一件'),
    (28.8, 37.5, '早期的 AI：人把规则一条条写下来'), (38.3, 45.5, '可是狐狸也满足所有规则'), (45.5, 49.5, '例外永远写不完，人自己也说不清"猫"的完整规则'),
    (50, 56.8, '给它一堆例子：每个点是一套房子的面积和成交价'), (56.8, 62, '先随便画一条线，看看错了多少'),
    (62, 70, '往错得少一点的方向挪一点，再看，再挪'), (70, 73.8, '错误越来越小，两个旋钮停在了合适的位置'),
]


def caption(d, t):
    for a, b, s in CAPTIONS:
        if a <= t < b:
            k = min(seg(t, a, a + .3), 1 - seg(t, b - .3, b))
            w = text_w(s, 26)
            box = (640 - w / 2 - 20, 652, 640 + w / 2 + 20, 698)
            d.rounded_rectangle([v * S for v in box], radius=10 * S, fill=mix(BG, (255, 255, 255), k), outline=mix(BG, (210, 210, 205), k), width=S)
            text(d, (640, 675), s, 26, mix(BG, INK, k), anchor='mm')


def render(out):
    total = sum(d for d, _ in SCENES)
    n = int(total * FPS)
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'medium', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    snaps = {int(x * FPS) for x in (3, 14, 20, 40, 46, 55, 66, 78)}
    for f in range(n):
        t = f / FPS
        img = Image.new('RGB', (W * S, H * S), BG)
        d = ImageDraw.Draw(img)
        acc = 0
        for dur, fn in SCENES:
            if t < acc + dur:
                fn(d, t - acc)
                break
            acc += dur
        caption(d, t)
        small = img.resize((W, H), Image.LANCZOS)
        if f in snaps and len(sys.argv) > 2:
            small.save(f'{sys.argv[2]}/frame_{int(t):02d}.png')
        ff.stdin.write(small.tobytes())
    ff.stdin.close()
    ff.wait()
    print(f'{out}: {total:.1f}s, {n} frames')


if __name__ == '__main__':
    render(sys.argv[1] if len(sys.argv) > 1 else 'lesson01_sample.mp4')

"""track.py - point tracks for the tracking-overlay look (python3 stdlib only).

Frames come from ffmpeg as raw 8-bit gray (width TW). Start points: face landmarks when the shot has a face,
else Shi-Tomasi corners inside the shown region. Tracking: 3-level pyramid block matching (SAD) frame to frame;
a point whose match gets bad freezes instead of jumping.
"""
TW = 320


def pyr_down(img, w, h):
    w2, h2 = w // 2, h // 2
    out = bytearray(w2 * h2)
    for y in range(h2):
        r0, r1, o = 2 * y * w, (2 * y + 1) * w, y * w2
        for x in range(w2):
            a = 2 * x
            out[o + x] = (img[r0 + a] + img[r0 + a + 1] + img[r1 + a] + img[r1 + a + 1] + 2) >> 2
    return bytes(out), w2, h2


def pyramid(img, w, h, levels=3):
    out = [(img, w, h)]
    for _ in range(levels - 1):
        out.append(pyr_down(*out[-1]))
    return out


def sad(a, b, w, h, ax, ay, bx, by, r, cap):
    """sum of abs differences of (2r+1)^2 patches; None if a patch leaves the image; stops early above cap"""
    if ax - r < 0 or ay - r < 0 or ax + r >= w or ay + r >= h or bx - r < 0 or by - r < 0 or bx + r >= w or by + r >= h:
        return None
    s = 0
    for dy in range(-r, r + 1):
        oa, ob = (ay + dy) * w + ax, (by + dy) * w + bx
        for dx in range(-r, r + 1):
            d = a[oa + dx] - b[ob + dx]
            s += d if d >= 0 else -d
        if s > cap:
            return s
    return s


def match(P0, P1, x, y, radii=(5, 2, 2), r=3):
    """best position in frame 1 of the patch at (x, y) of frame 0; pyramids P0/P1 from pyramid(); returns (x, y, cost/px)"""
    nl = len(P0)
    dx = dy = 0
    cost = 0
    for lv in range(nl - 1, -1, -1):
        a, w, h = P0[lv]
        b = P1[lv][0]
        sc = 1 << lv
        ax, ay = int(round(x / sc)), int(round(y / sc))
        cx, cy = ax + dx, ay + dy
        best, bxy, R = None, (cx, cy), radii[min(lv, len(radii) - 1)]
        for oy in range(-R, R + 1):
            for ox in range(-R, R + 1):
                c = sad(a, b, w, h, ax, ay, cx + ox, cy + oy, r, best if best is not None else 1 << 30)
                if c is not None and (best is None or c < best):
                    best, bxy = c, (cx + ox, cy + oy)
        if best is None:
            return x, y, 255.0
        dx, dy = bxy[0] - ax, bxy[1] - ay
        cost = best / float((2 * r + 1) ** 2)
        if lv:
            dx, dy = dx * 2, dy * 2
    return x + dx, y + dy, cost


def track(frames, w, h, pts, bad=38.0):
    """frames: list of gray bytes (w*h); pts: [(x, y)] in frame-0 px -> [[(x, y), ..] per frame]"""
    out = [[(float(x), float(y)) for x, y in pts]]
    prev = pyramid(frames[0], w, h)
    for fr in frames[1:]:
        cur = pyramid(fr, w, h)
        nxt = []
        for x, y in out[-1]:
            nx, ny, c = match(prev, cur, int(round(x)), int(round(y)))
            nxt.append((float(nx), float(ny)) if c < bad else (x, y))
        out.append(nxt)
        prev = cur
    return out


def corners(img, w, h, region, n, mind, taken=()):
    """Shi-Tomasi corners (min eigenvalue of the structure tensor, 5x5 window, 2-px grid) inside region
    (x0, y0, x1, y1), strongest first, at least `mind` px apart from each other and from `taken`"""
    x0, y0, x1, y1 = [int(v) for v in region]
    x0, y0, x1, y1 = max(3, x0), max(3, y0), min(w - 4, x1), min(h - 4, y1)
    cand = []
    for y in range(y0, y1, 2):
        for x in range(x0, x1, 2):
            sxx = syy = sxy = 0
            for yy in range(y - 2, y + 3):
                o = yy * w
                for xx in range(x - 2, x + 3):
                    gx = img[o + xx + 1] - img[o + xx - 1]
                    gy = img[o + w + xx] - img[o - w + xx]
                    sxx += gx * gx
                    syy += gy * gy
                    sxy += gx * gy
            tr, det = sxx + syy, sxx * syy - sxy * sxy
            disc = max(0.0, tr * tr / 4.0 - det)
            lam = tr / 2.0 - disc ** 0.5
            if lam > 0:
                cand.append((lam, x, y))
    cand.sort(reverse=True)
    got = list(taken)
    out = []
    for lam, x, y in cand:
        if all((x - a) ** 2 + (y - b) ** 2 >= mind * mind for a, b in got):
            out.append((x, y))
            got.append((x, y))
            if len(out) == n:
                break
    return out


def snap(img, w, h, x, y, rad):
    """move a landmark to the strongest corner within rad px (stable to track); keeps it when nothing is there"""
    c = corners(img, w, h, (x - rad, y - rad, x + rad + 1, y + rad + 1), 1, 1)
    return c[0] if c else (x, y)

from PIL import Image, ImageDraw
from random import randint
import math
import sys


sys.setrecursionlimit(100000)

MIN_DIST = 50
MAX_CONNECTED = 10
SENSITIVITY = 5
DOT_SPACE = 7
DOT_SENSITIVITY = 30
IMG_NUMBER = 3
SCALAR = 1
CONTRAST = 0.5
MAX_DISTANCE = 100

def distance(dx, dy):
    return math.sqrt(dx * dx + dy * dy)


def generate_diffs():
    ans = []
    for d1 in range(1, MAX_CONNECTED + 1):
        for d2 in range(1, MAX_CONNECTED + 1):
            if distance(d1, d2) <= MAX_CONNECTED:
                ans.append((d1, d2))
                ans.append((-d1, d2))
                ans.append((d1, -d2))
                ans.append((-d1, -d2))
    return ans


def coords(*args):
    return tuple(i * SCALAR for i in args)


points = []


def dfs(at, last, visited, adj, allPoints):
    if visited[at]:
        return
    visited[at] = True
    for nxt in adj[at]:
        p1 = allPoints[nxt]
        p2 = allPoints[last]
        #print(type(arr[p1[0], p1[1]]))
        if distance(abs(p1[0] - p2[0]), abs(p1[1] - p2[1])) >= MIN_DIST * ((arr[p1[0], p1[1]] + SENSITIVITY) / 255) * SENSITIVITY:
            points.append(allPoints[nxt])
            dfs(nxt, nxt, visited, adj, allPoints)
        else:
            dfs(nxt, last, visited, adj, allPoints)


# def dfs2(at1, at2, last, visited, points, where):
#     if visited[at]:
#         return
#     visited[at] = True
#     i, j = points[at]
#     mn = MAX_DISTANCE
#     mnidx = -1
#     for ni in range(max(0, i - MAX_DISTANCE), min(rows, i + MAX_DISTANCE + 1)):
#         for nj in range(max(0, j - MAX_DISTANCE), min(cols, i + MAX_DISTANCE + 1)):
#             if where[ni][nj] != -1:
#                 d = distance(points[at], points[where[ni][nj]])
#                 if d < mn:
#                     mn = d
#                     mnidx =


with Image.open(f"imgs/{IMG_NUMBER}.edges.jpg") as im:
    rows, cols = im.size
    allPoints = []
    arr = im.load()
    for row in range(rows):
        for col in range(cols):
            if arr[row, col] == 1:
                allPoints.append((row, col))

    vis = [[-1 for _ in range(cols)] for _ in range(rows)]
    for idx, (i, j) in enumerate(allPoints):
        vis[i][j] = idx

    diffs = generate_diffs()

    adj = [[] for _ in allPoints]
    root = allPoints[0]
    for idx, (row, col) in enumerate(allPoints):
        for diff in diffs:
            newRow = row + diff[0]
            newCol = col + diff[1]
            if newRow < 0 or newCol < 0 or newRow >= rows or newCol >= cols:
                continue
            newIdx = vis[newRow][newCol]
            if newIdx != -1:
                adj[idx].append(newIdx)
    visited = [False for _ in allPoints]
    for i in range(len(allPoints)):
        if not visited[i]:
            points.append(allPoints[i])
            dfs(i, i, visited, adj, allPoints)

with Image.open(f"imgs/{IMG_NUMBER}.grayscale.jpg") as im:

    rows, cols = im.size
    rows *= SCALAR
    cols *= SCALAR
    # for row in range(rows):
    #    for col in range(cols):
    #        if arr[row, col] < 240:
    #            im.putpixel((row, col), 0)

    # búa til punktana á edgunum

    # generatea (semi)random punkta
    # teikna þríhyrninga
    im = im.convert("RGB")

    im = im.resize((rows, cols), Image.ANTIALIAS)

    arr = im.load()
    print(im.size, rows, cols)

    new = Image.new("RGBA", (rows, cols), (0, 0, 0, 0))

    print(len(points))
    draw = ImageDraw.Draw(new)
    for (x, y) in points:
        r = 2
        leftUpPoint = coords(x - r, y - r)
        rightDownPoint = coords(x + r, y + r)
        twoPointList = [leftUpPoint, rightDownPoint]
        draw.ellipse(twoPointList, fill=(0, 0, 255, 255))
        # im.putpixel(point, (255, 0, 0))
    for (x, y) in allPoints:
        r = 1
        leftUpPoint = coords(x - r, y - r)
        rightDownPoint = coords(x + r, y + r)
        twoPointList = [leftUpPoint, rightDownPoint]
        draw.ellipse(twoPointList, fill=(255, 0, 0, 255))
        # im.putpixel(point, (255, 0, 0))

    for idx, points in enumerate(adj):
        for point in points:
            # print(allPoints[idx], allPoints[point])
            draw.line(coords(allPoints[idx][0], allPoints[idx][1], allPoints[point][0], allPoints[point][1]),
                      fill=(64, 64, 0, 255))

    contrast = Image.new("RGB", (rows, cols), (0, 0, 0, 0))
    #drawDots = ImageDraw.Draw(dots)

    sm = 0
    for i in range(rows):
        for j in range(cols):
            sm += arr[i, j][0]
    avg = (sm / (rows * cols)) / 255

    otherPoints = []
    for i in range(0, rows):
        for j in range(0, cols):
            #print(i, j, rows, cols)
            #print(arr[i, j])
            #if randint(1, 1000) / 1000 >= math.pow((arr[i, j][0] / 255), 1 / 10):
            #    otherPoints.append((i, j))
            val = (arr[i, j][0] / 255)
            offset = val - avg
            diff = abs(offset) ** CONTRAST
            if offset < 0:
                color = int(255 * (avg - diff))
            else:
                color = int(255 * (avg + diff))
            contrast.putpixel((i, j), (color, color, color))

    contrastArr = contrast.load()
    #contrast.show()

    dots = Image.new("RGBA", (rows, cols), (0,0,0,0))
    dotsDraw = ImageDraw.Draw(dots)
    points = []
    where = [[-1 for _ in range(cols)] for _ in range(rows)]
    for x in range(0, rows, DOT_SPACE):
        for y in range(0, cols, DOT_SPACE):
            #print(randint(1, 100) / 100, contrastArr[row, col][0] / 255)
            if randint(1, 100) / 100 >= (contrastArr[x, y][0] - DOT_SENSITIVITY) / 255:
                r = 1
                xn = x + randint(-1, 1)
                yn = y + randint(-1, 1)
                points.append((xn, yn))
                where[xn][yn] = len(points) - 1
                leftUpPoint = coords(xn - r, yn - r)
                rightDownPoint = coords(xn + r, yn + r)

                twoPointList = [leftUpPoint, rightDownPoint]
                dotsDraw.ellipse(twoPointList, fill=(0, 255, 0))


    contrast.paste(dots, (0, 0), dots)
    contrast.show()
    # dots.show()
    # # for (x, y) in otherPoints:
    #     r = 2
    #     leftUpPoint = coords(x - r, y - r)
    #     rightDownPoint = coords(x + r, y + r)
    #     twoPointList = [leftUpPoint, rightDownPoint]
    #     draw.ellipse(twoPointList, fill=(0, 255, 0, 255))


    # draw.ellipse()
    im.paste(new, (0, 0), new)

    #im.show()
    # draw.line((0, 0) + im.size, fill=64)
    # draw.line((0, im.size[1], im.size[0], 0), fill=64)
    # im.save("test.png", "PNG")

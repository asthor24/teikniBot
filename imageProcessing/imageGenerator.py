from PIL import Image, ImageDraw, ImageEnhance
from random import randint
import math
import sys
import cv2
import numpy
import ctypes
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt

if __name__ == '__main__':
    from imageParser import parseSource
else:
    from .imageParser import parseSource

sys.setrecursionlimit(100000)

MIN_DIST = 50
MAX_CONNECTED = 10
SENSITIVITY = 5
DOT_SPACE = 15
DOT_SENSITIVITY = 5
IMG_NUMBER = 4
SCALAR = 1
CONTRAST = 1.5
# CONTRAST = 1 - CONTRAST
MAX_DISTANCE = 100

# get Screen Size
user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


def showImage(title, oriimg):
    W, H = screensize
    W -= 100
    H -= 100
    height, width, depth = oriimg.shape

    scaleWidth = float(W) / float(width)
    scaleHeight = float(H) / float(height)
    if scaleHeight > scaleWidth:
        imgScale = scaleWidth
    else:
        imgScale = scaleHeight

    newX, newY = oriimg.shape[1] * imgScale, oriimg.shape[0] * imgScale
    newimg = cv2.resize(oriimg, (int(newX), int(newY)))
    cv2.imshow(title, newimg)


def drawPILImg(title, img, delay=0):
    opencvnew = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR)
    showImage(title, opencvnew)
    cv2.waitKey(delay)


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
        # print(type(arr[p1[0], p1[1]]))
        if distance(abs(p1[0] - p2[0]), abs(p1[1] - p2[1])) >= MIN_DIST * (
                (arr[p1[0], p1[1]] + SENSITIVITY) / 255) * SENSITIVITY:
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

parses = parseSource(f'{IMG_NUMBER}.source.jpg')
edgeImg = Image.fromarray(parses['edges'])
grayscaleImg = Image.fromarray(parses['img'])

rows, cols = edgeImg.size
allPoints = []
arr = edgeImg.load()
for row in range(rows):
    for col in range(cols):
        if arr[row, col] == 0:
            allPoints.append((row, col))

vis = [[-1 for _ in range(cols)] for _ in range(rows)]
for idx, (i, j) in enumerate(allPoints):
    vis[i][j] = idx

diffs = generate_diffs()

adj = [[] for _ in allPoints]
if len(allPoints) == 0:
    raise Exception('No edges detected')
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

rows, cols = grayscaleImg.size
rows *= SCALAR
cols *= SCALAR
# for row in range(rows):
#    for col in range(cols):
#        if arr[row, col] < 240:
#            im.putpixel((row, col), 0)

# búa til punktana á edgunum

# generatea (semi)random punkta
# teikna þríhyrninga
grayscaleImg = grayscaleImg.convert("RGB")
grayscaleImg = grayscaleImg.resize((rows, cols), Image.ANTIALIAS)

arr = grayscaleImg.load()
print(grayscaleImg.size, rows, cols)

new = Image.new("RGBA", (rows, cols), (0, 0, 0, 0))

# print(len(points))
# draw = ImageDraw.Draw(new)
# print('Drawing selected points')
# for (x, y) in points:
#     r = 2
#     leftUpPoint = coords(x - r, y - r)
#     rightDownPoint = coords(x + r, y + r)
#     twoPointList = [leftUpPoint, rightDownPoint]
#     draw.ellipse(twoPointList, fill=(0, 0, 255, 255))
#     # im.putpixel(point, (255, 0, 0))
# print('Drawing all points')
# for (x, y) in allPoints:
#     r = 1
#     leftUpPoint = coords(x - r, y - r)
#     rightDownPoint = coords(x + r, y + r)
#     twoPointList = [leftUpPoint, rightDownPoint]
#     draw.ellipse(twoPointList, fill=(255, 0, 0, 255))
#     # im.putpixel(point, (255, 0, 0))
#     # im.paste(new, (0, 0), new)
#     # drawPILImg('d', im, 1)
#
# print('Drawing edges')
# for idx, points in enumerate(adj):
#     for point in points:
#         # print(allPoints[idx], allPoints[point])
#         draw.line(coords(allPoints[idx][0], allPoints[idx][1], allPoints[point][0], allPoints[point][1]),
#                   fill=(64, 64, 0, 255))

print('Drawing contrasted image')
contrastEnhancer = ImageEnhance.Contrast(grayscaleImg)

contrast = contrastEnhancer.enhance(CONTRAST)

contrastArr = contrast.load()

print('Drawing dots')
dots = Image.new("RGBA", (rows, cols), (0, 0, 0, 0))
dotsDraw = ImageDraw.Draw(dots)
points = []
where = [[-1 for _ in range(cols)] for _ in range(rows)]
for x in range(0, rows, DOT_SPACE):
    for y in range(0, cols, DOT_SPACE):
        # print(randint(1, 100) / 100, contrastArr[row, col][0] / 255)
        if randint(1, 100) / 100 >= (contrastArr[x, y][0] - DOT_SENSITIVITY) / 255:
            r = 1
            xn = x + randint(-1, 1)
            yn = y + randint(-1, 1)
            if xn < 0 or yn < 0 or xn >= rows or yn >= cols:
                continue
            points.append([xn, -yn])
            where[xn][yn] = len(points) - 1
            leftUpPoint = coords(xn - r, yn - r)
            rightDownPoint = coords(xn + r, yn + r)

            twoPointList = [leftUpPoint, rightDownPoint]
            dotsDraw.ellipse(twoPointList, fill=(0, 255, 0, 80))
points = numpy.array(points)

print('Triangulating points')
tri = Delaunay(points)
triSimplices = tri.simplices
print(f'Point count: {len(points)}, triangle count: {len(triSimplices)}')

plt.rcParams["figure.figsize"] = (12, 20)

plt.axis('off')
plt.triplot(points[:, 0], points[:, 1], triSimplices)
# plt.plot(points[:, 0], points[:, 1], 'o')
plt.show(bbox_inches='tight', pad_inches=0, transparent="True")

contrast.paste(dots, (0, 0), dots)
drawPILImg('contrast', contrast)

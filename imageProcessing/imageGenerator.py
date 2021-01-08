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
    from imageParser import parseSource, displayImageGroup
else:
    from .imageParser import parseSource, displayImageGroup

sys.setrecursionlimit(100000)

MIN_DIST = 50
MAX_CONNECTED = 10
SENSITIVITY = 5
DOT_SENSITIVITY = 10
IMG_NUMBER = 2
SCALAR = 2
DOT_SPACE = 10 * SCALAR
CONTRAST = 2
# CONTRAST = 1 - CONTRAST
MAX_DISTANCE = 100

points = []

print('getting screen size')
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
    newimg = cv2.resize(oriimg, (int(newX), int(newY)), interpolation=cv2.INTER_AREA)
    cv2.imshow(title, newimg)


def convertPilToCv2(img):
    return cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR)


def drawPILImg(title, img, delay=0):
    showImage(title, convertPilToCv2(img))
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


def printCircuit(adj):
    # adj represents the adjacency list of
    # the directed graph
    # edge_count represents the number of edges
    # emerging from a vertex
    edge_count = dict()

    for i in range(len(adj)):
        # find the count of edges to keep track
        # of unused edges
        edge_count[i] = len(adj[i])

    if len(adj) == 0:
        return  # empty graph

    # Maintain a stack to keep vertices
    curr_path = []

    # vector to store final circuit
    circuit = []

    # start from any vertex
    curr_path.append(0)
    curr_v = 0  # Current vertex

    while len(curr_path):

        # If there's remaining edge
        if edge_count[curr_v]:

            # Push the vertex
            curr_path.append(curr_v)

            # Find the next vertex using an edge
            next_v = adj[curr_v][-1]

            # and remove that edge
            edge_count[curr_v] -= 1
            adj[curr_v].pop()

            # Move to next vertex
            curr_v = next_v

            # back-track to find remaining circuit
        else:
            circuit.append(curr_v)

            # Back-tracking
            curr_v = curr_path[-1]
            curr_path.pop()

            # we've got the circuit, now print it in reverse
    ans = []
    for i in range(len(circuit) - 1, -1, -1):
        ans.append(circuit[i])
    return ans


print('parsing images')
parses = parseSource(f'{IMG_NUMBER}.source.jpg')
edgeImg = Image.fromarray(parses['edges'])
grayscaleImg = Image.fromarray(parses['img'])

rows, cols = grayscaleImg.size
rows *= SCALAR
cols *= SCALAR

print('resizing')
grayscaleImg = grayscaleImg.convert("RGB")
grayscaleImg = grayscaleImg.resize((rows, cols), Image.ANTIALIAS)

arr = grayscaleImg.load()
print(grayscaleImg.size, rows, cols)

new = Image.new("RGBA", (rows, cols), (0, 0, 0, 0))

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
            points.append([xn, yn])
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


adj = [[] for _ in points]
for triangle in triSimplices:
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            adj[triangle[i]].append(triangle[j])

for idx, edg in enumerate(adj):
    s = set()
    nw = []
    for v in edg:
        if not v in s:
            nw.append(v)
        else:
            s.add(v)
    adj[idx] = nw

edges = printCircuit(adj)

contrast.paste(dots, (0, 0), dots)
edgeImg = Image.new("RGB", (rows, cols), (0, 0, 0))
contrastDraw = ImageDraw.Draw(edgeImg)

color = 255
# edges = map(lambda x: tuple(points[x]), edges)
# contrastDraw.line(tuple(edges), fill=(color if color < 255 else 255, color - 255 if color > 255 else 255, 255, 255),
#                   width=SCALAR, joint='curve')

lastPoint = None
for index, edgeIndex in enumerate(edges):
    edge = points[edgeIndex]
    if index != 0:
        contrastDraw.line((edge[0], edge[1], lastPoint[0], lastPoint[1]),
                          fill=(color if color < 255 else 255, color - 255 if color > 255 else 255, 0, 255), width=SCALAR)
        if index % 100 == 0:
            drawPILImg('contrast', edgeImg, 1)
    lastPoint = edge
    color = (color + 5) % 510
drawPILImg('contrast', edgeImg)

# displayImageGroup('d', [convertPilToCv2(contrast), convertPilToCv2(edgeImg)], 2)
# cv2.waitKey()

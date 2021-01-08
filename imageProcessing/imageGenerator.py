from PIL import Image, ImageDraw, ImageEnhance
from random import randint
import math
import numpy
from scipy.spatial import Delaunay
import ctypes
# get Screen Size
user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
print(screensize)

if __name__ == '__main__':
    from utils import parseSource, displayImageGroup, drawPILImg, convertPilToCv2
else:
    from .utils import parseSource, displayImageGroup, drawPILImg, convertPilToCv2

IMG_NUMBER = 2
DOT_SENSITIVITY = 10
SCALAR = 2
DOT_SPACE = 10 * SCALAR
CONTRAST = 2
EDGE_COLOR_DIFF = 5


def distance(dx, dy):
    """return pythagorean distance"""
    return math.sqrt(dx * dx + dy * dy)


def coords(*args):
    """multiplies every parameter by the scalar constant"""
    return tuple(i * SCALAR for i in args)


def printCircuit(adj):
    """
    Hierholzer’s Algorithm for finding the eulerian path through all the edges
    copy from here: https://www.geeksforgeeks.org/hierholzers-algorithm-directed-graph/
    """
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
print("Image size:", grayscaleImg.size)

new = Image.new("RGBA", (rows, cols), (0, 0, 0, 0))

print('Drawing contrasted image')
contrastEnhancer = ImageEnhance.Contrast(grayscaleImg)
contrast = contrastEnhancer.enhance(CONTRAST)
contrastArr = contrast.load()

print('Drawing dots')
dots = Image.new("RGBA", (rows, cols), (0, 0, 0, 0))
dotsDraw = ImageDraw.Draw(dots)
points = []
for x in range(0, rows, DOT_SPACE):
    for y in range(0, cols, DOT_SPACE):
        # randomize whether a point gets selected, so that lower pixels are more likely
        if randint(1, 100) / 100 >= (contrastArr[x, y][0] - DOT_SENSITIVITY) / 255:
            r = 1
            xn = x + randint(-1, 1)
            yn = y + randint(-1, 1)
            if xn < 0 or yn < 0 or xn >= rows or yn >= cols:
                continue
            points.append((xn, yn))
            # draw ellipse on dots image
            leftUpPoint = coords(xn - r, yn - r)
            rightDownPoint = coords(xn + r, yn + r)
            twoPointList = [leftUpPoint, rightDownPoint]
            dotsDraw.ellipse(twoPointList, fill=(0, 255, 0, 80))
points = numpy.array(points)

print('Triangulating points')
tri = Delaunay(points)
triSimplices = tri.simplices
print(f'Point count: {len(points)}, triangle count: {len(triSimplices)}')

# create adjacency list
adj = [[] for _ in points]
for triangle in triSimplices:
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            adj[triangle[i]].append(triangle[j])

# remove multiple edges
for idx, edg in enumerate(adj):
    s = set()
    nw = []
    for v in edg:
        if v not in s:
            nw.append(v)
        else:
            s.add(v)
    adj[idx] = nw

# distance of path is 2 times the sum of lengths of edges, since we visit each edge twice (it is undirected)
edges = printCircuit(adj)

# draw dots on contrast image
contrast.paste(dots, (0, 0), dots)
edgeImg = Image.new("RGB", (rows, cols), (0, 0, 0))
edgeDraw = ImageDraw.Draw(edgeImg)

color = 255
lastPoint = None
for index, edgeIndex in enumerate(edges):
    edge = points[edgeIndex]
    if index != 0:
        # draw edge
        edgeDraw.line((edge[0], edge[1], lastPoint[0], lastPoint[1]),
                      fill=(color if color < 255 else 255, color - 255 if color > 255 else 255, 0, 255),
                      width=SCALAR)
        # display image
        if index % 100 == 0:
            drawPILImg('contrast', edgeImg, 1)
    # set the last point
    lastPoint = edge
    color = (color + EDGE_COLOR_DIFF) % 510
# finally show image
drawPILImg('contrast', edgeImg)

# Show side by side
# displayImageGroup('d', [convertPilToCv2(contrast), convertPilToCv2(edgeImg)], 2)
# cv2.waitKey()

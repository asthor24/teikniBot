from PIL import Image, ImageDraw
import math
import sys
sys.setrecursionlimit(100000)

MIN_DIST = 50
MAX_CONNECTED = 10
IMG_NUMBER = 3

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

points = []
def dfs(at, last, visited, adj, allPoints):
    if visited[at]:
        return
    visited[at] = True
    for nxt in adj[at]:
        p1 = allPoints[nxt]
        p2 = allPoints[last]
        if distance(abs(p1[0] - p2[0]), abs(p1[1] - p2[1])) >= MIN_DIST:
            points.append(allPoints[nxt])
            dfs(nxt, nxt, visited, adj, allPoints)
        else:
            dfs(nxt, last, visited, adj, allPoints)


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
    arr = im.load()
    rows, cols = im.size
    #for row in range(rows):
    #    for col in range(cols):
    #        if arr[row, col] < 240:
    #            im.putpixel((row, col), 0)

    # búa til punktana á edgunum

    # generatea (semi)random punkta
    # teikna þríhyrninga


    print(len(points))
    draw = ImageDraw.Draw(im)
    for (x, y) in points:
        r = 5
        leftUpPoint = (x - r, y - r)
        rightDownPoint = (x + r, y + r)
        twoPointList = [leftUpPoint, rightDownPoint]
        draw.ellipse(twoPointList, fill=0)
        # im.putpixel(point, (255, 0, 0))
    for (x, y) in allPoints:
        r = 3
        leftUpPoint = (x - r, y - r)
        rightDownPoint = (x + r, y + r)
        twoPointList = [leftUpPoint, rightDownPoint]
        draw.ellipse(twoPointList, fill=255)
        # im.putpixel(point, (255, 0, 0))

    for idx, points in enumerate(adj):
        for point in points:
            # print(allPoints[idx], allPoints[point])
            draw.line((allPoints[idx][0], allPoints[idx][1], allPoints[point][0], allPoints[point][1]), fill=64)

    # draw.ellipse()


    im.show()
    # draw.line((0, 0) + im.size, fill=64)
    # draw.line((0, im.size[1], im.size[0], 0), fill=64)
    im.save("test.png", "PNG")

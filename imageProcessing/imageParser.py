import os
import cv2
import numpy as np

from constants import IMG_DIR
# if __name__ == '__main__':
#     pass
# else:
#     from .constants import IMG_DIR

import ctypes

# get Screen Size
user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


def showImage(title, oriimg):
    W, H = screensize
    height, width = oriimg.shape

    scaleWidth = float(W) / float(width)
    scaleHeight = float(H) / float(height)
    if scaleHeight > scaleWidth:
        imgScale = scaleWidth
    else:
        imgScale = scaleHeight

    newX, newY = oriimg.shape[1] * imgScale, oriimg.shape[0] * imgScale
    newimg = cv2.resize(oriimg, (int(newX), int(newY)))
    cv2.imshow(title, newimg)


def displayImageGroup(title, images, numRows=4):
    images = list(images)

    if len(images) > numRows:
        tiled_images = [[images[j] for j in range(i, min(i + numRows, len(images)))] for i in range(0, len(images), numRows)]
        print(tiled_images)
        concattedImg = cv2.vconcat([cv2.hconcat(im_list_h) for im_list_h in tiled_images])
    else:
        concattedImg = cv2.hconcat(images)
    print(concattedImg.shape)
    showImage(title, concattedImg)


def parseSource(filename):
    img = cv2.imread(IMG_DIR + filename, 0)
    # getting edges from the pure image
    raw_img_edges = cv2.Canny(img, 200, 250)

    # getting contours from the edge image
    # kernel = np.ones((3, 3), dtype=np.uint8)
    # closing = cv2.morphologyEx(raw_img_edges, cv2.MORPH_CLOSE, kernel)
    # contours, hierarchy = cv2.findContours(closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # actualContour = max(contours, key=cv2.contourArea)

    # blur = cv2.blur(img, (8, 8))
    thresh = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    # ret, thresh = cv2.threshold(img, 100, 255, cv2.TRUNC)
    # thresh = cv2.bitwise_not(thresh, thresh)

    thresh_edges = cv2.Canny(thresh, 300, 400)

    img = cv2.GaussianBlur(img,(15,15),0)

    # display_images = [img, raw_img_edges, thresh, thresh_edges]
    return {
        "img": img,
        "edges": cv2.bitwise_not(raw_img_edges),
        # "blur": blur,
        "thresh": thresh,
        "thesh_edges": thresh_edges
    }

    # deciding where to cut the image
    hull = cv2.convexHull(actualContour, returnPoints=False)
    conDef = cv2.convexityDefects(actualContour, hull)

    convexHullImg = img.copy()
    for i in range(conDef.shape[0]):
        s, e, f, d = conDef[i, 0]
        start = tuple(actualContour[s][0])
        end = tuple(actualContour[e][0])
        far = tuple(actualContour[f][0])
        cv2.line(convexHullImg, start, end, [0, 255, 0], 2)
        cv2.circle(convexHullImg, far, 5, [0, 0, 255], -1)

    rect = cv2.minAreaRect(actualContour)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    asdf = cv2.drawContours(img.copy(), [box], 0, (0, 0, 255), 2)
    # countored_img = cv2.drawContours(img, contours, -1, (0,255,255), 3)
    ret, thresh = cv2.threshold(img, 105, 255, 0)
    thresh_edges = cv2.Canny(thresh, 100, 250)
    display_images = [img, raw_img_edges, thresh, thresh_edges, asdf, convexHullImg]
    cv2.imshow(filename + 'a', cv2.hconcat([scale_img(b, 40) for b in display_images]))


def getSources():
    files = os.listdir(IMG_DIR)
    parsedSources = {}
    for filename in files:
        if 'source' in filename:
            number = filename.split('.')[0]
            parsedSources[number] = parseSource(filename)
    return parsedSources


def writeSources():
    sources = getSources()
    writtenFiles = {
        'grayscale': 'img',
        'edges': 'edges'
    }
    for number, parsedSource in sources.items():
        for filename, objectType in writtenFiles.items():
            cv2.imwrite(f'{IMG_DIR}{number}.{filename}.jpg', parsedSource[objectType])


def showSources():
    sources = getSources()
    for number, parsedSource in sources.items():
        displayImageGroup(number, parsedSource.values(), 4)
    cv2.waitKey(0)


if __name__ == "__main__":
    showSources()

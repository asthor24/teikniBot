import os
from constants import IMG_DIR
import ctypes
import cv2
import numpy as np

# get Screen Size
user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


def showImage(title, oriimg):
    """Scales an image to the display size and displays it"""
    W, H = screensize
    W -= 100
    H -= 100
    shape = tuple(oriimg.shape[1::-1])

    scaleWidth = float(W) / float(shape[1])
    scaleHeight = float(H) / float(shape[0])
    if scaleHeight > scaleWidth:
        imgScale = scaleWidth
    else:
        imgScale = scaleHeight

    newX, newY = shape[1] * imgScale, shape[0] * imgScale
    newimg = cv2.resize(oriimg, (int(newX), int(newY)), interpolation=cv2.INTER_AREA)
    cv2.imshow(title, newimg)


def convertPilToCv2(img):
    """Converts an PIL image to a cv2 image"""
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def drawPILImg(title, img, delay=0):
    """Draws a PIL image with cv2, in the window size"""
    showImage(title, convertPilToCv2(img))
    cv2.waitKey(delay)


def displayImageGroup(title, images, numRows=4):
    """Display images in a tiled fashion, note: the images need to all have the same dimensions"""
    images = list(images)

    if len(images) > numRows:
        tiled_images = [[images[j] for j in range(i, min(i + numRows, len(images)))] for i in
                        range(0, len(images), numRows)]
        print(tiled_images)
        concattedImg = cv2.vconcat([cv2.hconcat(im_list_h) for im_list_h in tiled_images])
    else:
        concattedImg = cv2.hconcat(images)
    print(concattedImg.shape)
    showImage(title, concattedImg)


def parseSource(filename):
    """Parses an image, giving edges, thresh and a grayscale parse"""
    img = cv2.imread(IMG_DIR + filename, 0)
    # getting edges from the pure image
    raw_img_edges = cv2.Canny(img, 200, 250)

    thresh = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    thresh_edges = cv2.Canny(thresh, 300, 400)

    # Blurring the image sometimes helps the triangles
    # img = cv2.GaussianBlur(img,(15,15),0)

    return {
        "img": img,
        "edges": cv2.bitwise_not(raw_img_edges),
        "thresh": thresh,
        # "thesh_edges": thresh_edges
    }


def getSources():
    """Gets all the sources in the img directory, parses them and returns the list"""
    files = os.listdir(IMG_DIR)
    parsedSources = {}
    for filename in files:
        if 'source' in filename:
            number = filename.split('.')[0]
            parsedSources[number] = parseSource(filename)
    return parsedSources


def showSources():
    """Shows all the sources, side by side"""
    sources = getSources()
    for number, parsedSource in sources.items():
        displayImageGroup(number, parsedSource.values(), 4)
    cv2.waitKey(0)


if __name__ == "__main__":
    showSources()

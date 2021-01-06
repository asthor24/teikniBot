import os
import cv2
import numpy as np
import math

files = os.listdir()


def scale_img(img, scale_percent=50):
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    return cv2.resize(img, dim, interpolation = cv2.INTER_AREA)


for filename in files:
    if '.jpg' in filename:
        img = cv2.imread(filename, 0)
        # getting edges from the pure image
        raw_img_edges = cv2.Canny(img, 100, 250)

        # getting contours from the edge image
        kernel = np.ones((3, 3), dtype=np.uint8)
        closing = cv2.morphologyEx(raw_img_edges, cv2.MORPH_CLOSE, kernel)
        contours, hierarchy = cv2.findContours(closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        actualContour = max(contours, key=cv2.contourArea)

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

cv2.waitKey(0)

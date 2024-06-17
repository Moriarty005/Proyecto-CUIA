import cv2
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
import time


def popup(titulo, imagen):
    cv2.imshow(titulo, imagen)
    while True:
        if cv2.waitKey(10) > 0:
            cv2.destroyWindow(titulo)
            break
        elif cv2.getWindowProperty(titulo, cv2.WND_PROP_VISIBLE) < 1:
            break


def plot(image, titulo=None, axis=False):
    dpi = mpl.rcParams['figure.dpi']
    if len(image.shape) == 2:
        h, w = image.shape
        c = 1
    else:
        h, w, c = image.shape

    # What size does the figure need to be in inches to fit the image?
    figsize = w / float(dpi), h / float(dpi)

    # Create a figure of the right size with one axes that takes up the full figure
    fig = plt.figure(figsize=figsize)
    ax = fig.add_axes([0, 0, 1, 1])

    # Hide spines, ticks, etc.
    if not axis:
        ax.axis('off')
    if isinstance(titulo, str):
        plt.title(titulo)

    # Display the image.
    if c == 4:
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA))
    elif c == 1:
        plt.imshow(image, cmap='gray')
    else:
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), aspect='equal')


def bestBackend(camid):
    backends = cv2.videoio_registry.getCameraBackends()
    bestCap = 0
    bestTime = 999
    for b in backends:
        start = time.time()
        cam = cv2.VideoCapture(camid, b)
        end = time.time()
        if cam.isOpened():
            if end - start < bestTime:
                bestTime = end - start
                bestCap = b
            cam.release()
    return bestCap


def alphaBlending(fg, bg, x=0, y=0):
    sfg = fg.shape
    fgh = sfg[0]
    fgw = sfg[1]

    sbg = bg.shape
    bgh = sbg[0]
    bgw = sbg[1]

    h = max(bgh, y + fgh) - min(0, y)
    w = max(bgw, x + fgw) - min(0, x)

    CA = np.zeros(shape=(h, w, 3))
    aA = np.zeros(shape=(h, w))
    CB = np.zeros(shape=(h, w, 3))
    aB = np.zeros(shape=(h, w))

    bgx = max(0, -x)
    bgy = max(0, -y)

    if len(sbg) == 2 or sbg[2] == 1:
        aB[bgy:bgy + bgh, bgx:bgx + bgw] = np.ones(shape=sbg)
        CB[bgy:bgy + bgh, bgx:bgx + bgw, :] = cv2.cvtColor(bg, cv2.COLOR_GRAY2BGR)
    elif sbg[2] == 3:
        aB[bgy:bgy + bgh, bgx:bgx + bgw] = np.ones(shape=sbg[0:2])
        CB[bgy:bgy + bgh, bgx:bgx + bgw, :] = bg
    else:
        aB[bgy:bgy + bgh, bgx:bgx + bgw] = bg[:, :, 3] / 255.0
        CB[bgy:bgy + bgh, bgx:bgx + bgw, :] = bg[:, :, 0:3]

    fgx = max(0, x)
    fgy = max(0, y)

    if len(sfg) == 2 or sfg[2] == 1:
        aA[fgy:fgy + fgh, fgx:fgx + fgw] = np.ones(shape=sfg)
        CA[fgy:fgy + fgh, fgx:fgx + fgw, :] = cv2.cvtColor(fg, cv2.COLOR_GRAY2BGR)
    elif sfg[2] == 3:
        aA[fgy:fgy + fgh, fgx:fgx + fgw] = np.ones(shape=sfg[0:2])
        CA[fgy:fgy + fgh, fgx:fgx + fgw, :] = fg
    else:
        aA[fgy:fgy + fgh, fgx:fgx + fgw] = fg[:, :, 3] / 255.0
        CA[fgy:fgy + fgh, fgx:fgx + fgw, :] = fg[:, :, 0:3]

    aA = cv2.merge((aA, aA, aA))
    aB = cv2.merge((aB, aB, aB))
    a0 = aA + aB * (1 - aA)
    C0 = np.divide(((CA * aA) + (CB * aB) * (1.0 - aA)), a0, out=np.zeros_like(CA), where=(a0 != 0))

    res = cv2.cvtColor(np.uint8(C0), cv2.COLOR_BGR2BGRA)
    res[:, :, 3] = np.uint8(a0[:, :, 0] * 255.0)

    return res


def proyeccion(puntos, rvec, tvec, cameraMatrix, distCoeffs):
    if isinstance(puntos, list):
        return (proyeccion(np.array(puntos, dtype=np.float32), rvec, tvec, cameraMatrix, distCoeffs))
    if isinstance(puntos, np.ndarray):
        if puntos.ndim == 1 and puntos.size == 3:
            res, _ = cv2.projectPoints(puntos.astype(np.float32), rvec, tvec, cameraMatrix, distCoeffs)
            return (res[0][0].astype(int))
        if puntos.ndim > 1:
            aux = proyeccion(puntos[0], rvec, tvec, cameraMatrix, distCoeffs)
            aux = np.expand_dims(aux, axis=0)
            for p in puntos[1:]:
                aux = np.append(aux, [proyeccion(p, rvec, tvec, cameraMatrix, distCoeffs)], axis=0)
            return (np.array(aux))


def histogramahsv(imagen, solotono=True):
    if solotono:
        hist, (ax1) = plt.subplots(1)
    else:
        hist, (ax1, ax2, ax3) = plt.subplots(1, 3)
    framehsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(framehsv)
    histoh = cv2.calcHist([framehsv], [0], None, [180], [0, 180])
    ax1.set_title("Hue")
    ax1.get_yaxis().set_visible(False)
    ax1.plot(histoh)
    if not solotono:
        histos = cv2.calcHist([framehsv], [1], None, [256], [0, 256])
        ax2.set_title("Sat")
        ax2.get_yaxis().set_visible(False)
        ax2.plot(histos)
        histov = cv2.calcHist([framehsv], [2], None, [256], [0, 256])
        ax3.set_title("Val")
        ax3.get_yaxis().set_visible(False)
        ax3.plot(histov)
    plt.show()
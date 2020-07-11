import numpy
from PIL import Image


def color_diff(color1, color2):
    return numpy.sum((color1 - color2) ** 2) ** 1 / 2


def hsv(rgb: tuple) -> tuple:
    hue = numpy.array(rgb) / 255
    value_index = numpy.argmax(hue)
    value = hue[value_index]
    delta = value - numpy.min(hue)
    if delta == 0:
        hue = 0
    elif value_index == 0:
        hue = 60 * ((hue[1] - hue[2]) / delta)
    elif value_index == 1:
        hue = 60 * (((hue[2] - hue[0]) / delta) + 2)
    else:
        hue = 60 * (((hue[0] - hue[1]) / delta) + 4)
    saturation = 0 if value == 0 else delta / value
    return hue, saturation, value


def rgb(hue: float, saturation: float, value: float) -> tuple:
    """
    Converts HSV to RGB.

    :param hue: the dominant color in degrees (0 -> 360)
    :param saturation: the intensity of the color as a ratio (0 -> 1)
    :param value: the quantity of light reflected as a ratio (0 -> 1)
    :return: am RBG tuple
    """
    c = value * saturation
    x = c * (1 - abs(((hue / 60) % 2) - 1))
    m = value - c
    if 0 <= hue < 60:
        prime = (c, x, 0)
    elif 60 <= hue < 120:
        prime = (x, c, 0)
    elif 120 <= hue < 180:
        prime = (0, c, x)
    elif 180 <= hue < 240:
        prime = (0, x, c)
    elif 240 <= hue < 300:
        prime = (x, 0, c)
    else:
        prime = (c, 0, x)
    prime = numpy.array(prime)
    return tuple((prime + m) * 255)


def search(path, rgb):
    im: Image.Image = Image.open(path)
    pix = im.load()
    minimum = (0, 0)
    for x in range(im.width):
        for y in range(im.height):
            dist = color_diff(numpy.array(rgb), numpy.array(pix[x, y]))
            if dist < color_diff(numpy.array(rgb), numpy.array(pix[minimum[0], minimum[1]])):
                minimum = (x, y)
    reticle = Image.open('pso2/reticle.png')
    im.paste(reticle, (minimum[0] - 13, minimum[1] - 13), reticle)
    im.show()
    im.save('pso2/dump2.png')


nagatoro_skin = (233, 183, 146)  # nagatoro
search('pso2/human-newman.png', nagatoro_skin)

nagatoro_iris = (123, 123, 123)
h, s, v = hsv(nagatoro_iris)
print(h, s, v)
nagatoro_iris = rgb(h, 1, v)
print(nagatoro_iris)
search('pso2/cast.png', nagatoro_iris)

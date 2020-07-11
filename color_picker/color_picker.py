import numpy as np
from PIL import Image


def color_diff(rgb_x: np.array, rgb_y: np.array) -> float:
    """
    Computes the distance between two colors using Euclidean distance.

    :param rgb_x: a vector of one rbg color
    :param rgb_y: a vector of another rgb color
    :return: the distance between two vectors
    """
    return np.sum((rgb_x - rgb_y) ** 2) ** 1 / 2


def hsv(red: int, green: int, blue: int) -> tuple:
    """
    Converts RBG to HSV.

    :param red: the red value of the color (0 - 255)
    :param green: the green value of the color (0 - 255)
    :param blue: the blue value of the color (0 - 255)
    :return: HSV as a tuple
    """
    hue = np.array((red, green, blue)) / 255
    value_index = np.argmax(hue)
    value = hue[value_index]
    delta = value - np.min(hue)
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
    prime = np.array(prime)
    return tuple((prime + m) * 255)


def search(path: str, color: tuple) -> tuple:
    """
    Finds the pixel which contains the closest possible color to the one provided.

    :param path: the path of an image to search
    :param color: the color of the pixel to find in RGB
    :return: the location of the pixel that best matches the provided color as a tuple (x, y)
    """
    im: Image.Image = Image.open(path)
    pix = im.load()
    minimum = (0, 0)
    for x in range(im.width):
        for y in range(im.height):
            dist = color_diff(np.array(color), np.array(pix[x, y]))
            if dist < color_diff(np.array(color), np.array(pix[minimum[0], minimum[1]])):
                minimum = (x, y)
    return minimum


def render_reticle(path: str, pixel: tuple) -> Image.Image:
    """
    Renders the reticle at the position of a pixel.

    :param path: the image to draw on
    :param pixel: the location of the reticle
    :return: the updated image
    """
    im: Image.Image = Image.open(path)
    reticle = Image.open('../assets/reticle.png')
    im.paste(reticle, (pixel[0] - 13, pixel[1] - 13), reticle)
    return im


if __name__ == '__main__':
    # Nagatoro skin color lookup
    nagatoro_skin_color = (233, 183, 146)
    pixel = search('../assets/human-newman.png', nagatoro_skin_color)
    nagatoro_skin_sample = render_reticle('../assets/human-newman.png', pixel)
    nagatoro_skin_sample.show()
    nagatoro_skin_sample.save('../samples/nagatoro_skin.png')

    # Nagatoro iris color lookup
    nagatoro_iris_color = (123, 123, 123)
    h, s, v = hsv(*nagatoro_iris_color)
    print(f"Hue: {h}\nSaturation: {s}\nValue: {v}")
    nagatoro_iris_color = rgb(h, 1, v)
    pixel = search('../assets/cast.png', nagatoro_iris_color)
    nagatoro_iris_sample = render_reticle("../assets/cast.png", pixel)
    nagatoro_iris_sample.show()
    nagatoro_iris_sample.save('../samples/nagatoro_iris.png')
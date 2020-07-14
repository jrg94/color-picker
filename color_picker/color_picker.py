from typing import Sequence

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


def gradient(color_x: np.array, color_y: np.array, percent: float) -> tuple:
    """
    Computes the gradient between two colors.

    :param color_x: the first color as RBG
    :param color_y: the second color as RGB
    :param percent: the ratio between two colors
    :return: the gradient between two colors as RGB
    """
    return tuple((((color_y - color_x) * percent) + color_x).astype(int))


def generate_gradient(color_x: tuple, color_y: tuple, size: tuple) -> tuple:
    """
    Creates a list of pixels that represent a rectangle gradient.

    :param color_x: the first color as RGB
    :param color_y: the second color as RGB
    :param size: the size of the rectangle (width, height)
    :return: the gradient as a tuple
    """
    img = list()
    for x in range(size[0]):
        for y in range(size[1]):
            img.append(gradient(np.array(color_x), np.array(color_y), x / (size[0] - 1)))
    return tuple(img)


def render_gradient(color_x: tuple, color_y: tuple, size: tuple):
    """
    Renders a vertical rectangular gradient given two colors and a size.

    :param color_x: the first color in RGB
    :param color_y: the second color in RGB
    :param size: the size of the rectangle (width, height)
    :return: None
    """
    img = generate_gradient(color_x, color_y, size)
    grad = Image.new("RGB", (23, 197))
    grad.putdata(img)
    grad.show()
    grad.save('gradient.png')


def get_closest_color(colors: Sequence, target_color: tuple):
    min_index = 0
    for i, color in enumerate(colors):
        distance = color_diff(np.array(color), np.array(target_color))
        if distance < color_diff(np.array(color), np.array(colors[min_index])):
            min_index = i
    return min_index


def get_color(color: tuple):
    if color[0] == color[1] == color[2]:
        return search("../assets/cast.png", color), 100
    else:
        h, s, v = hsv(*color)
        if s > .995 or v > .995:
            return search("../assets/cast.png", color), 100
        else:
            gray = int(np.sum(color) / 3)
            gray = (gray, gray, gray)
            x = int((h / 360) * 268)
            im: Image.Image = Image.open('../assets/cast-grayscale.png')
            pix = im.load()
            minimum = (x, 0)
            for y in range(im.height):
                dist = color_diff(np.array(gray), np.array(pix[x, y]))
                if dist < color_diff(np.array(gray), np.array(pix[minimum[0], minimum[1]])):
                    minimum = (x, y)
            im: Image.Image = Image.open('../assets/cast.png')
            pix = im.load()
            rgb = pix[minimum[0], minimum[1]]
            grad = generate_gradient(rgb, gray, (23, 197))
            index = get_closest_color(grad, color)
            ratio = 1 - (index / len(grad))
            return minimum, ratio


if __name__ == '__main__':
    # WOOOO RISKY
    pixel, ratio = get_color((195, 188, 169))
    render_reticle("../assets/cast.png", pixel).show()
    print(ratio)


    """
    # Nagatoro skin color lookup
    nagatoro_skin_color = (233, 183, 146)
    pixel = search('../assets/human-newman.png', nagatoro_skin_color)
    nagatoro_skin_sample = render_reticle('../assets/human-newman.png', pixel)
    nagatoro_skin_sample.show()
    nagatoro_skin_sample.save('../samples/nagatoro_skin.png')

    # Nagatoro iris color lookup
    nagatoro_iris_color = (152, 90, 70)
    h, s, v = hsv(*nagatoro_iris_color)
    print(f"Hue: {h}\nSaturation: {s}\nValue: {v}")
    nagatoro_iris_color = rgb(h, 1, v)
    pixel = search('../assets/cast.png', nagatoro_iris_color)
    nagatoro_iris_sample = render_reticle("../assets/cast.png", pixel)
    nagatoro_iris_sample.show()
    nagatoro_iris_sample.save('../samples/nagatoro_iris.png')
    """

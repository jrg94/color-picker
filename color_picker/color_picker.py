from typing import Sequence

import numpy as np
from PIL import Image, ImageDraw

THRESHOLD = .995

GRADIENT_SIZE = (23, 197)

CAST_COLOR_IMAGE = "../assets/cast.png"
CAST_GRAY_IMAGE = '../assets/cast-grayscale.png'
SLIDER_IMAGE = '../assets/slider.png'
RETICLE_IMAGE = '../assets/reticle.png'
WINDOW_UI = '../assets/window_ui.png'


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
        hue = 60 * (((hue[1] - hue[2]) / delta) % 6)
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
    reticle = Image.open(RETICLE_IMAGE)
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
    for y in range(size[1]):
        for x in range(size[0]):
            img.append(gradient(np.array(color_x), np.array(color_y), y / (size[1] - 1)))
    return tuple(img)


def _render_gradient(gradient_pixels: tuple, size: tuple) -> Image.Image:
    """
    Renders a vertical rectangular gradient given two colors and a size.

    :param gradient_pixels: the gradient pixels as a sequence
    :param size: the size of the rectangle (width, height)
    :return: None
    """
    gradient_bar = Image.new("RGB", size)
    gradient_bar.putdata(gradient_pixels)
    return gradient_bar


def _render_slider(gradient_bar: Image.Image, ratio: float) -> Image.Image:
    """
    Draws a slider on a gradient bar.

    :param gradient_bar: the gradient bar image
    :param ratio: the vertical position of the slider (0 -> 1)
    :return: the new image with the slider over the gradient bar
    """
    slider: Image.Image = Image.open(SLIDER_IMAGE)
    img = Image.new("RGB", (gradient_bar.width + slider.width // 2, gradient_bar.height))
    img.paste(gradient_bar)
    img.paste(slider, (slider.width // 2, int(img.height * (1 - ratio)) - 9), slider)
    return img


def _render_color(color: tuple, slider: Image.Image, size: int) -> Image.Image:
    """
    Draws a color square above a slider.

    :param color: the color to be rendered
    :param slider: the slider image
    :param size: the size of the color square
    :return: the new image with the color square above the gradient bar
    """
    space = int(1.5 * size)
    img = Image.new("RGB", (slider.width, slider.height + space))
    img.paste(slider, (0, space))
    ImageDraw.Draw(img).rectangle(((0, 0), (size, size)), fill=color)
    return img


def _render_preview(reticle_preview: Image.Image, color_preview: Image.Image) -> Image.Image:
    """
    Draws the complete preview given a reticle preview and a color preview.

    :param reticle_preview: the color image including a reticle
    :param color_preview: the gradient bar, slider, and color preview square image
    :return: the combined image
    """
    size = (reticle_preview.width + color_preview.width + 10, reticle_preview.height)
    preview = Image.new("RGB", size)
    preview.paste(reticle_preview)
    preview.paste(color_preview, (reticle_preview.width + 10, reticle_preview.height - color_preview.height))
    return preview


def _render_window_ui(preview: Image.Image) -> Image.Image:
    window = Image.open(WINDOW_UI)
    window.paste(preview, (31, 69))
    return window


def render_color_palette(color: tuple) -> Image.Image:
    """
    Assembles the entire color palette preview from all the render pieces.

    :param color: the color to lookup
    :return: the preview image
    """
    pixel, ratio = get_cast_color_info(color)
    reticle_preview = render_reticle(CAST_COLOR_IMAGE, pixel)
    gradient = generate_gradient(lookup_pixel(CAST_COLOR_IMAGE, pixel), get_average_gray(color), GRADIENT_SIZE)
    gradient_bar = _render_gradient(gradient, GRADIENT_SIZE)
    slider = _render_slider(gradient_bar, ratio)
    color_location = int((1 - ratio) * len(gradient))
    color_preview = _render_color(gradient[color_location], slider, 23)
    preview = _render_preview(reticle_preview, color_preview)
    window_ui = _render_window_ui(preview)
    return window_ui


def get_closest_color(colors: Sequence, target_color: tuple) -> int:
    """
    Gets the index of closest color from a sequence.

    :param colors: a sequence of RGB colors
    :param target_color: an RGB color to find
    :return: the index of the closest color
    """
    min_index = 0
    for i, color in enumerate(colors):
        distance = color_diff(np.array(color), np.array(target_color))
        if distance < color_diff(np.array(color), np.array(colors[min_index])):
            min_index = i
    return min_index


def get_average_gray(color: tuple) -> tuple:
    """
    Generates a gray color given a color.

    :param color: an RGB color
    :return: an average RGB gray
    """
    average_gray = int(np.sum(color) / 3)
    return average_gray, average_gray, average_gray


def get_cast_color(color: tuple):
    """
    Computes a cast color given a target color in RGB.

    :param color: an RGB color
    :return: the location of the color pixel (x, y)
    """
    hue, _, _ = hsv(*color)
    average_gray = get_average_gray(color)
    column_index = int((hue / 360) * 268)
    im: Image.Image = Image.open(CAST_GRAY_IMAGE)
    column = list(im.getdata())[column_index::im.width]
    minimum = (column_index, get_closest_color(column, average_gray))
    return minimum


def lookup_pixel(path: str, pixel: tuple) -> tuple:
    """
    Looks up the color of a pixel given an image path and a pixel location.

    :param path: the path to an image
    :param pixel: the location of a pixel (x, y)
    :return: color as an RGB tuple (0 -> 255, 0 -> 255, 0 -> 255)
    """
    im: Image.Image = Image.open(path)
    pix = im.load()
    color = pix[pixel[0], pixel[1]]
    return color


def get_cast_scaling_factor(color: tuple, minimum: tuple) -> float:
    """
    Computes a scaling factor given a target color and
    the location of the cast color.

    :param color: a target RGB color
    :param minimum: the location of the closest cast color
    :return: a scaling factor (0 -> 1)
    """
    average_gray = get_average_gray(color)
    closest_color = lookup_pixel(CAST_COLOR_IMAGE, minimum)
    grad = generate_gradient(closest_color, average_gray, GRADIENT_SIZE)
    index = get_closest_color(grad, color)
    percent = 1 - (index / len(grad))
    return percent


def get_cast_color_info(color: tuple) -> tuple:
    """
    Returns the location of the closest color and its scaling factor.

    :param color: an RGB color to find
    :return: closest color pixel (x, y) and scaling factor (0 -> 1)
    """
    h, s, v = hsv(*color)
    if color[0] == color[1] == color[2] or s > THRESHOLD or v > THRESHOLD:
        return search(CAST_COLOR_IMAGE, color), 1
    else:
        minimum = get_cast_color(color)
        percent = get_cast_scaling_factor(color, minimum)
        return minimum, percent


def main() -> None:
    """
    The drop-in function.

    :return: None
    """
    file_name = input("Please provide file name (include .png): ")
    rgb_input = input("Please enter a color as comma-separated RGB: ")
    color = tuple(int(x.strip()) for x in rgb_input.split(','))
    preview = render_color_palette(color)
    preview.show()
    preview.save(file_name)


if __name__ == '__main__':
    main()

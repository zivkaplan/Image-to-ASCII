import os
import argparse

from PIL import Image


TEST_IMAGE = "test_image.jpg"
ASCII_CHARS = '`^",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$'


def average_colors_filter(r, g, b):
    return (r + g + b) / 3


def average_brightness_filter(r, g, b):
    return (max(r, g, b) + min(r, g, b)) / 2


def luminosity_filter(r, g, b):
    return 0.21 * r + 0.72 * g + 0.07 * b


ALL_FILTERS = (average_colors_filter, average_brightness_filter, luminosity_filter)


def resize_image(image):
    tty_width, tty_height = os.get_terminal_size()
    original_width, original_height = image.size
    ratio = original_height / original_width

    new_size = min(tty_width, tty_height)
    new_height = new_size
    new_width = int(new_size * ratio)

    multiplier = 1
    while new_width * multiplier <= tty_width:
        multiplier += 1

    resized_image = image.resize((new_width, new_height))
    return resized_image, multiplier - 1


def calculate_char(current_brightness, invert=False):
    brightness_percent = (current_brightness / 255) * 100
    index = int(round(len(ASCII_CHARS) * (brightness_percent / 100))) - 1
    return ASCII_CHARS[:: -1 if invert else 1][index]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path", type=str)
    parser.add_argument(
        "-i", "--invert", action="store_true", required=False, default=False
    )
    parser.add_argument(
        "-f",
        "--filter",
        type=int,
        choices=(range(1, len(ALL_FILTERS) + 1)),
        default=0,
    )

    args = parser.parse_args()

    # override the filter to the actual function pointer
    args.filter = ALL_FILTERS[args.filter - 1]

    return args


def convert_to_ascii(img, filter, invert, multiplier):
    tty_width, tty_height = os.get_terminal_size()

    final_img_str = ""
    for idx, current_pixel in enumerate(img.getdata(), 1):
        char = calculate_char(filter(*current_pixel), invert=invert)
        final_img_str += char * multiplier
        if idx % img.width == 0:
            final_img_str += "\n"

    return final_img_str[:-1]


def handle_img(path):
    if not os.path.exists(path):
        raise "Image not found"

    img = Image.open(path)
    return resize_image(img)


def main():
    args = parse_args()
    img, multiplier = handle_img(args.image_path)
    final_img_str = convert_to_ascii(img, args.filter, args.invert, multiplier)
    print(final_img_str)


if __name__ == "__main__":
    main()

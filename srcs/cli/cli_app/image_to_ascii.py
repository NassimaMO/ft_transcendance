from PIL import Image
import numpy as np

# Define ASCII characters from dark to light
ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

# Resize image to fit ASCII art proportions
def resize_image(image, new_width=35):
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width * 0.55)  # Adjust height to match terminal font aspect ratio
    return image.resize((new_width, new_height))

# Convert the image to grayscale
def grayscale_image(image):
    return image.convert("L")

# Map pixels to ASCII characters
def map_pixels_to_ascii(image, range_width=25):
    pixels = np.array(image)
    ascii_str = ""
    for pixel_row in pixels:
        for pixel in pixel_row:
            ascii_str += ASCII_CHARS[pixel // range_width]
        ascii_str += "\n"
    return ascii_str

# Convert image to ASCII art
def image_to_ascii(image_path, new_width=50):
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"Unable to open image file {image_path}: {e}")
        return
    
    image = resize_image(image, new_width)
    image = grayscale_image(image)
    
    ascii_str = map_pixels_to_ascii(image)
    return ascii_str
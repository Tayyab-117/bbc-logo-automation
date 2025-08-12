import os
from PIL import Image

def add_logo_to_image(image_path, logo_path,language, output_folder='output', logo_scale=0.45):
    """
    Adds a logo to the bottom-left of an image and saves it in the output folder.
    Automatically resizes the logo to a percentage of the image width.    
    Parameters:
        image_path (str): Path to main image.
        logo_path (str): Path to logo (PNG preferred).
        output_folder (str): Folder to save final image.
        logo_scale (float): Fraction of image width to scale logo (e.g., 0.12 = 12% of image width).
    """
    print("++++++++++-*---------------++++++++++++",image_path)
    os.makedirs(output_folder, exist_ok=True)
    main_image = Image.open(image_path)
    logo = Image.open(logo_path)
    # Resize logo dynamically
    main_width, main_height = main_image.size
    logo_ratio = logo.height / logo.width
    logo_new_width = int(main_width * logo_scale)
    logo_new_height = int(logo_new_width * logo_ratio)
    logo = logo.resize((logo_new_width, logo_new_height))
    # Ensure alpha channel
    if logo.mode != 'RGBA':
        logo = logo.convert('RGBA')

    # Bottom-left position
    position = (10, main_height - logo_new_height - 10)  # add padding from edges

    combined = main_image.copy()
    combined.paste(logo, position, logo)

    base_name = os.path.basename(image_path)
    name, ext = os.path.splitext(base_name)
    output_path = os.path.join(output_folder, f"{name}_{language}{ext}")
    combined.save(output_path, quality=100)

    print(f"✅ Logo added and saved to: {output_path}")
    return output_path

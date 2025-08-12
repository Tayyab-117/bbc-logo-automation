from PIL import Image
from io import BytesIO

def paste_logo(main_img: Image.Image, logo_img: Image.Image, language: str, logo_scale: float = 0.40):
    """
    Paste `logo_img` onto `main_img` at bottom-left with padding.
    - logo_scale is a fraction of main image width.
    Returns a new PIL Image.
    """
    if main_img.mode != "RGBA":
        main = main_img.convert("RGBA")
    else:
        main = main_img.copy()

    # Ensure logo has alpha
    if logo_img.mode != "RGBA":
        logo = logo_img.convert("RGBA")
    else:
        logo = logo_img.copy()

    mw, mh = main.size
    # Scale logo width relative to main image width
    target_w = max(1, int(mw * logo_scale))
    ratio = target_w / logo.width
    target_h = max(1, int(logo.height * ratio))
    logo = logo.resize((target_w, target_h), Image.LANCZOS)

    # Position: bottom-left with padding
    pad_left = 25
    pad_bottom = 30
    x = pad_left
    y = max(0, mh - target_h - pad_bottom)

    composed = Image.new("RGBA", (mw, mh))
    composed.paste(main, (0, 0))
    composed.paste(logo, (x, y), logo)
    return composed

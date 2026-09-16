from pathlib import Path
from PIL import Image


def _get_aspect_ratio(width, height):
    """Return simplified image aspect ratio."""

    if not width or not height:
        return "Unknown"

    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    divisor = gcd(width, height)

    return f"{width // divisor}:{height // divisor}"


def _get_bit_depth(image):
    """
    Return a human-readable bit-depth description
    based on the image mode and available metadata.
    """

    bits = image.info.get("bits")

    if bits:
        try:
            bits = int(bits)
            channels = len(image.getbands())

            if channels > 1:
                return f"{bits}-bit/channel"

            return f"{bits}-bit"

        except (TypeError, ValueError):
            pass

    mode_depth = {
        "1": "1-bit",
        "L": "8-bit",
        "P": "8-bit",
        "RGB": "8-bit/channel",
        "RGBA": "8-bit/channel",
        "CMYK": "8-bit/channel",
        "I": "32-bit",
        "F": "32-bit",
        "I;16": "16-bit",
        "I;16L": "16-bit",
        "I;16B": "16-bit",
    }

    return mode_depth.get(image.mode, "Unknown")


def _get_compression(image):
    """Return a human-readable compression description."""

    image_format = (image.format or "").upper()

    if image_format == "JPEG":
        return "JPEG (lossy)"

    if image_format == "PNG":
        return "PNG (lossless)"

    if image_format == "WEBP":
        if image.info.get("lossless") is True:
            return "WEBP (lossless)"

        return "WEBP"

    if image_format == "TIFF":
        compression = image.info.get("compression")

        if compression:
            return f"TIFF ({compression})"

        return "TIFF"

    return image_format or "Unknown"


def extract_metadata(image_path, original_filename=None):
    """
    Extract technical and forensic metadata from an image.

    Metadata is informational evidence only.
    It does NOT determine whether an image is real,
    AI-generated, or manipulated.
    """

    path = Path(image_path)

    metadata = {
        "filename": original_filename or path.name,

        "file_format": "Unknown",

        "file_size": round(
            path.stat().st_size / (1024 * 1024),
            2
        ),

        "width": None,
        "height": None,

        "aspect_ratio": "Unknown",

        "color_mode": "Unknown",

        "channels": None,

        "compression": "Unknown",

        "bit_depth": "Unknown",

        "exif_present": False,

        "metadata_status": "No EXIF metadata found",
    }

    try:

        with Image.open(image_path) as image:

            # -------------------------------------------------
            # Basic file information
            # -------------------------------------------------

            metadata["file_format"] = image.format or "Unknown"

            metadata["width"] = image.width
            metadata["height"] = image.height

            # -------------------------------------------------
            # Aspect ratio
            # -------------------------------------------------

            metadata["aspect_ratio"] = _get_aspect_ratio(
                image.width,
                image.height
            )

            # -------------------------------------------------
            # Color information
            # -------------------------------------------------

            metadata["color_mode"] = image.mode

            metadata["channels"] = len(image.getbands())

            # -------------------------------------------------
            # Compression
            # -------------------------------------------------

            metadata["compression"] = _get_compression(image)

            # -------------------------------------------------
            # Bit depth
            # -------------------------------------------------

            metadata["bit_depth"] = _get_bit_depth(image)

            # -------------------------------------------------
            # EXIF information
            # -------------------------------------------------

            exif = image.getexif()

            if exif:

                metadata["exif_present"] = True
                metadata["metadata_status"] = "EXIF metadata detected"

            else:

                metadata["exif_present"] = False
                metadata["metadata_status"] = "No EXIF metadata found"

    except Exception as e:

        metadata["metadata_status"] = "Metadata extraction failed"
        metadata["error"] = str(e)

    return metadata
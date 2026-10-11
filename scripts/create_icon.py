"""Creates a macOS .icns file from the temporary SVG logo."""

import os
import subprocess

from PySide6.QtCore import QRectF, QSize
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer


SVG_PATH = "assets/neatify-logo.svg"
ICONSET_PATH = "assets/Neatify.iconset"
ICNS_PATH = "assets/Neatify.icns"


def render_png(renderer, output_path, size):
    image = QImage(QSize(size, size), QImage.Format.Format_ARGB32)
    image.fill(0)

    painter = QPainter(image)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()

    image.save(output_path)


def main():
    os.makedirs(ICONSET_PATH, exist_ok=True)

    renderer = QSvgRenderer(SVG_PATH)

    icon_sizes = [
        ("icon_16x16.png", 16),
        ("icon_16x16@2x.png", 32),
        ("icon_32x32.png", 32),
        ("icon_32x32@2x.png", 64),
        ("icon_128x128.png", 128),
        ("icon_128x128@2x.png", 256),
        ("icon_256x256.png", 256),
        ("icon_256x256@2x.png", 512),
        ("icon_512x512.png", 512),
        ("icon_512x512@2x.png", 1024),
    ]

    for file_name, size in icon_sizes:
        output_path = os.path.join(ICONSET_PATH, file_name)
        render_png(renderer, output_path, size)

    subprocess.run(["iconutil", "-c", "icns", ICONSET_PATH, "-o", ICNS_PATH], check=True)


if __name__ == "__main__":
    main()

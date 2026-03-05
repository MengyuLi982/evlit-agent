#!/usr/bin/env python3
"""Convert beautiful SVG to high-quality PNG."""

import cairosvg

svg_path = '/home2/mengyu/evlit-agent/output/diagrams/evagent_promo_v2.svg'
png_path = '/home2/mengyu/evlit-agent/output/diagrams/evagent_promo_v2.png'

# Convert SVG to PNG with high DPI (1920x1080 @ 300 DPI)
cairosvg.svg2png(
    url=svg_path,
    write_to=png_path,
    dpi=300,
    output_width=5760,   # 1920 * 3 for ultra-high quality
    output_height=3240   # 1080 * 3 for ultra-high quality
)

print(f"✓ High-quality PNG rendered: {png_path}")
print(f"  Resolution: 5760x3240 pixels (300 DPI)")
print(f"  Aspect ratio: 16:9 (perfect for presentations)")

# Also create a web-optimized version
png_web_path = '/home2/mengyu/evlit-agent/output/diagrams/evagent_promo_v2_web.png'
cairosvg.svg2png(
    url=svg_path,
    write_to=png_web_path,
    dpi=96,
    output_width=1920,
    output_height=1080
)

print(f"✓ Web-optimized PNG rendered: {png_web_path}")
print(f"  Resolution: 1920x1080 pixels (96 DPI)")

#!/usr/bin/env python3
"""Convert SVG to PNG with high quality."""

import cairosvg

svg_path = '/home2/mengyu/evlit-agent/output/diagrams/evagent_promo.svg'
png_path = '/home2/mengyu/evlit-agent/output/diagrams/evagent_promo_final.png'

# Convert SVG to PNG with high DPI
cairosvg.svg2png(
    url=svg_path,
    write_to=png_path,
    dpi=300,
    output_width=4800,  # 1600 * 3 for high quality
    output_height=3000  # 1000 * 3 for high quality
)

print(f"✓ PNG rendered from SVG: {png_path}")
print(f"  Resolution: 4800x3000 pixels (300 DPI)")

#!/usr/bin/env python3
"""Generate promotional diagram as SVG, then render to PNG."""

import svgwrite
from svgwrite import cm, mm

def create_promo_svg():
    # Create SVG with good dimensions
    dwg = svgwrite.Drawing(
        '/home2/mengyu/evlit-agent/output/diagrams/evagent_promo.svg',
        size=('1600px', '1000px'),
        viewBox='0 0 1600 1000'
    )

    # Add background
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='#F0F2F5'))

    # Define colors
    COLOR_INPUT = '#4A90E2'
    COLOR_PROCESS = '#7ED321'
    COLOR_API = '#F5A623'
    COLOR_OUTPUT = '#BD10E0'
    COLOR_ACCENT = '#50E3C2'

    # Title
    title_group = dwg.g(id='title')
    title_group.add(dwg.text(
        'EventVision Literature Agent',
        insert=(800, 60),
        text_anchor='middle',
        font_size='42px',
        font_weight='bold',
        fill='#2C3E50',
        font_family='Arial, sans-serif'
    ))
    title_group.add(dwg.text(
        'Multi-Agent RAG System for Academic Research',
        insert=(800, 95),
        text_anchor='middle',
        font_size='20px',
        font_style='italic',
        fill='#7F8C8D',
        font_family='Arial, sans-serif'
    ))
    dwg.add(title_group)

    # Helper function to draw rounded rect
    def draw_box(x, y, width, height, text_lines, color, text_size='18px'):
        group = dwg.g()
        # Box
        group.add(dwg.rect(
            insert=(x, y),
            size=(width, height),
            rx=15, ry=15,
            fill=color,
            stroke='white',
            stroke_width=3,
            opacity=0.9
        ))
        # Text
        y_offset = y + height/2 - (len(text_lines)-1) * 12
        for i, line in enumerate(text_lines):
            group.add(dwg.text(
                line,
                insert=(x + width/2, y_offset + i * 24),
                text_anchor='middle',
                font_size=text_size,
                font_weight='bold',
                fill='white',
                font_family='Arial, sans-serif'
            ))
        return group

    # Helper function to draw circle
    def draw_circle(cx, cy, r, text_lines, color, text_size='14px'):
        group = dwg.g()
        group.add(dwg.circle(
            center=(cx, cy),
            r=r,
            fill=color,
            stroke='white',
            stroke_width=3,
            opacity=0.9
        ))
        y_offset = cy - (len(text_lines)-1) * 8
        for i, line in enumerate(text_lines):
            group.add(dwg.text(
                line,
                insert=(cx, y_offset + i * 16),
                text_anchor='middle',
                font_size=text_size,
                font_weight='bold',
                fill='white',
                font_family='Arial, sans-serif',
                dominant_baseline='middle'
            ))
        return group

    # Helper function to draw arrow
    def draw_arrow(x1, y1, x2, y2, color='#333333', width=4):
        group = dwg.g()
        # Line
        group.add(dwg.line(
            start=(x1, y1),
            end=(x2, y2),
            stroke=color,
            stroke_width=width,
            opacity=0.8
        ))
        # Arrowhead
        angle = 0
        import math
        if x2 != x1:
            angle = math.atan2(y2 - y1, x2 - x1)
        arrow_size = 12
        p1 = (x2, y2)
        p2 = (x2 - arrow_size * math.cos(angle - math.pi/6),
              y2 - arrow_size * math.sin(angle - math.pi/6))
        p3 = (x2 - arrow_size * math.cos(angle + math.pi/6),
              y2 - arrow_size * math.sin(angle + math.pi/6))
        group.add(dwg.polygon(
            points=[p1, p2, p3],
            fill=color,
            opacity=0.8
        ))
        return group

    # 1. INPUT - User Query
    dwg.add(draw_box(50, 450, 200, 100, ['User Query', '"What datasets', 'are used?"'], COLOR_INPUT, '16px'))

    # Arrow to pipeline
    dwg.add(draw_arrow(260, 500, 320, 500, COLOR_INPUT))

    # 2. PIPELINE - 5 Stages
    pipeline_y = 420
    stage_width = 150
    stage_height = 140
    gap = 20

    stages = [
        (['PLAN', '', 'Generate', 'Subqueries'], COLOR_PROCESS),
        (['SEARCH', '', 'Multi-Source', 'Retrieval'], COLOR_PROCESS),
        (['EXTRACT', '', 'Evidence', 'Extraction'], COLOR_PROCESS),
        (['VERIFY', '', 'Quality', 'Check'], COLOR_PROCESS),
        (['DRAFT', '', 'LLM', 'Synthesis'], COLOR_OUTPUT)
    ]

    for i, (text_lines, color) in enumerate(stages):
        x = 330 + i * (stage_width + gap)
        dwg.add(draw_box(x, pipeline_y, stage_width, stage_height, text_lines, color, '15px'))

        # Arrow to next stage
        if i < len(stages) - 1:
            dwg.add(draw_arrow(x + stage_width + 5, pipeline_y + stage_height/2,
                              x + stage_width + gap - 5, pipeline_y + stage_height/2,
                              '#555555', 3))

    # 3. ACADEMIC SOURCES - Below SEARCH stage
    sources_y = 650
    source_x_start = 480
    source_spacing = 110

    sources = [
        ['arXiv'],
        ['OpenAlex'],
        ['Semantic', 'Scholar'],
        ['Crossref']
    ]

    for i, source_lines in enumerate(sources):
        x = source_x_start + i * source_spacing
        dwg.add(draw_circle(x, sources_y, 40, source_lines, COLOR_API, '12px'))
        # Arrow from SEARCH to source
        dwg.add(draw_arrow(480, pipeline_y + stage_height + 5, x, sources_y - 40, COLOR_API, 2))

    # Label for sources
    label_group = dwg.g()
    label_group.add(dwg.rect(
        insert=(600, 720),
        size=(120, 35),
        rx=8, ry=8,
        fill='white',
        stroke=COLOR_API,
        stroke_width=2
    ))
    label_group.add(dwg.text(
        '20 API Calls',
        insert=(660, 742),
        text_anchor='middle',
        font_size='14px',
        font_weight='bold',
        fill=COLOR_API,
        font_family='Arial, sans-serif'
    ))
    dwg.add(label_group)

    # 4. LLM API - Below DRAFT stage
    llm_x = 1180
    llm_y = 630
    dwg.add(draw_circle(llm_x, llm_y, 50, ['LLM', 'API', '(1x)'], COLOR_OUTPUT, '14px'))
    # Arrow from DRAFT to LLM
    dwg.add(draw_arrow(1180, pipeline_y + stage_height + 5, llm_x, llm_y - 50, COLOR_OUTPUT, 2))

    # 5. OUTPUT - Grounded Answer
    dwg.add(draw_box(1000, 780, 350, 120,
                     ['Grounded Answer', '+ Evidence + Citations', '+ Provenance Tracking'],
                     COLOR_OUTPUT, '16px'))

    # Arrow from pipeline to output
    dwg.add(draw_arrow(1180, pipeline_y + stage_height + 5, 1175, 780, COLOR_OUTPUT, 4))

    # 6. KEY FEATURES - Left side
    feature_y_start = 650
    feature_height = 60
    feature_width = 280

    features = [
        ('Multi-Source Retrieval', '4 academic databases'),
        ('Profile-Based Filtering', 'Domain-specific ranking'),
        ('Smart Deduplication', 'DOI > arXiv > Title+Author'),
        ('Evidence Grounding', 'Citation-backed answers')
    ]

    for i, (title, desc) in enumerate(features):
        y = feature_y_start + i * (feature_height + 15)

        feature_group = dwg.g()
        feature_group.add(dwg.rect(
            insert=(30, y),
            size=(feature_width, feature_height),
            rx=10, ry=10,
            fill='white',
            stroke=COLOR_ACCENT,
            stroke_width=2.5,
            opacity=0.95
        ))
        feature_group.add(dwg.text(
            title,
            insert=(40, y + 22),
            font_size='14px',
            font_weight='bold',
            fill='#2C3E50',
            font_family='Arial, sans-serif'
        ))
        feature_group.add(dwg.text(
            desc,
            insert=(40, y + 42),
            font_size='12px',
            font_style='italic',
            fill='#7F8C8D',
            font_family='Arial, sans-serif'
        ))
        dwg.add(feature_group)

    # 7. STATS BOX - Bottom right
    stats_group = dwg.g()
    stats_group.add(dwg.rect(
        insert=(1000, 920),
        size=(350, 70),
        rx=10, ry=10,
        fill='#F8F9FA',
        stroke='#DEE2E6',
        stroke_width=2
    ))

    stats_lines = [
        'Performance: 21 API calls per query',
        '25-70 sec end-to-end • 5 subqueries',
        '10-30 papers retrieved per query'
    ]

    for i, line in enumerate(stats_lines):
        stats_group.add(dwg.text(
            line,
            insert=(1010, 945 + i * 18),
            font_size='11px',
            fill='#495057',
            font_family='Courier New, monospace'
        ))
    dwg.add(stats_group)

    # 8. ARCHITECTURE BADGE - Bottom left
    arch_group = dwg.g()
    arch_group.add(dwg.rect(
        insert=(30, 920),
        size=(280, 70),
        rx=10, ry=10,
        fill='#FFF8DC',
        stroke='#F5A623',
        stroke_width=2
    ))

    arch_lines = [
        'Built With: LangGraph orchestration',
        'LiteLLM • PaperQA2 patterns',
        'Multi-agent workflow'
    ]

    for i, line in enumerate(arch_lines):
        arch_group.add(dwg.text(
            line,
            insert=(40, 945 + i * 18),
            font_size='11px',
            fill='#856404',
            font_family='Courier New, monospace'
        ))
    dwg.add(arch_group)

    # Watermark
    dwg.add(dwg.text(
        'evagent - Academic Literature Multi-Agent System',
        insert=(800, 985),
        text_anchor='middle',
        font_size='12px',
        font_style='italic',
        fill='#ADB5BD',
        font_family='Arial, sans-serif'
    ))

    dwg.save()
    print("✓ SVG diagram generated: output/diagrams/evagent_promo.svg")

if __name__ == '__main__':
    create_promo_svg()

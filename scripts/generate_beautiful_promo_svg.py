#!/usr/bin/env python3
"""Generate a beautiful, high-level promotional diagram as SVG."""

import svgwrite
from svgwrite.gradients import LinearGradient

def create_beautiful_promo_svg():
    # Create SVG with professional dimensions
    dwg = svgwrite.Drawing(
        '/home2/mengyu/evlit-agent/output/diagrams/evagent_promo_v2.svg',
        size=('1920px', '1080px'),
        viewBox='0 0 1920 1080'
    )

    # Add gradient background
    gradient = LinearGradient(id='bg_gradient', start=(0, 0), end=(0, 1))
    gradient.add_stop_color(offset='0%', color='#F7F9FC')
    gradient.add_stop_color(offset='100%', color='#E8EDF5')
    dwg.defs.add(gradient)
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='url(#bg_gradient)'))

    # Define modern color palette
    COLORS = {
        'primary': '#2563EB',      # Blue
        'secondary': '#10B981',    # Green
        'accent': '#F59E0B',       # Amber
        'purple': '#8B5CF6',       # Purple
        'pink': '#EC4899',         # Pink
        'teal': '#14B8A6',         # Teal
        'gray': '#6B7280',         # Gray
        'dark': '#1F2937',         # Dark gray
    }

    # Helper: Draw card with shadow
    def draw_card(x, y, width, height, color, opacity=0.95):
        group = dwg.g()
        # Shadow
        group.add(dwg.rect(
            insert=(x + 5, y + 5),
            size=(width, height),
            rx=20, ry=20,
            fill='#000000',
            opacity=0.1
        ))
        # Card
        group.add(dwg.rect(
            insert=(x, y),
            size=(width, height),
            rx=20, ry=20,
            fill=color,
            opacity=opacity,
            stroke='white',
            stroke_width=2
        ))
        return group

    # Helper: Draw icon circle
    def draw_icon_circle(cx, cy, r, color, icon_text):
        group = dwg.g()
        # Outer glow
        group.add(dwg.circle(
            center=(cx, cy),
            r=r + 5,
            fill=color,
            opacity=0.2
        ))
        # Main circle
        group.add(dwg.circle(
            center=(cx, cy),
            r=r,
            fill=color,
            stroke='white',
            stroke_width=3
        ))
        # Icon text
        group.add(dwg.text(
            icon_text,
            insert=(cx, cy + 8),
            text_anchor='middle',
            font_size='32px',
            font_weight='bold',
            fill='white',
            font_family='Arial, sans-serif'
        ))
        return group

    # Helper: Curved arrow
    def draw_curved_arrow(x1, y1, x2, y2, color, curve=50):
        group = dwg.g()
        # Calculate control point for curve
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2 - curve

        path = dwg.path(
            d=f'M {x1},{y1} Q {mx},{my} {x2},{y2}',
            stroke=color,
            stroke_width=4,
            fill='none',
            opacity=0.7,
            stroke_dasharray='10,5'
        )
        group.add(path)

        # Arrowhead
        group.add(dwg.polygon(
            points=[(x2, y2), (x2-12, y2-8), (x2-12, y2+8)],
            fill=color,
            opacity=0.7
        ))
        return group

    # ============ TITLE SECTION ============
    title_y = 80

    # Main title with gradient effect
    title_group = dwg.g()
    title_group.add(dwg.text(
        'EventVision Literature Agent',
        insert=(960, title_y),
        text_anchor='middle',
        font_size='56px',
        font_weight='bold',
        fill=COLORS['primary'],
        font_family='Arial, sans-serif',
        letter_spacing='2'
    ))

    # Subtitle
    title_group.add(dwg.text(
        'Intelligent Multi-Agent System for Academic Research',
        insert=(960, title_y + 50),
        text_anchor='middle',
        font_size='24px',
        fill=COLORS['gray'],
        font_family='Arial, sans-serif',
        font_style='italic'
    ))
    dwg.add(title_group)

    # ============ MAIN WORKFLOW ============
    workflow_y = 250

    # 1. INPUT STAGE
    input_x = 150
    dwg.add(draw_card(input_x - 80, workflow_y, 160, 180, COLORS['primary']))
    dwg.add(draw_icon_circle(input_x, workflow_y + 60, 40, COLORS['primary'], '?'))
    dwg.add(dwg.text(
        'User Query',
        insert=(input_x, workflow_y + 130),
        text_anchor='middle',
        font_size='20px',
        font_weight='bold',
        fill='white',
        font_family='Arial, sans-serif'
    ))
    dwg.add(dwg.text(
        'Research Question',
        insert=(input_x, workflow_y + 155),
        text_anchor='middle',
        font_size='14px',
        fill='white',
        font_family='Arial, sans-serif',
        opacity=0.9
    ))

    # Arrow to processing
    dwg.add(draw_curved_arrow(input_x + 80, workflow_y + 90, 450, workflow_y + 90, COLORS['primary'], 30))

    # 2. MULTI-AGENT PROCESSING (Center piece)
    center_x = 960
    center_y = workflow_y - 50

    # Main processing card
    dwg.add(draw_card(center_x - 300, center_y, 600, 400, 'white', 0.98))

    # Title
    dwg.add(dwg.text(
        'Multi-Agent Pipeline',
        insert=(center_x, center_y + 40),
        text_anchor='middle',
        font_size='28px',
        font_weight='bold',
        fill=COLORS['dark'],
        font_family='Arial, sans-serif'
    ))

    # 5 Agent nodes in a flow
    agent_y = center_y + 100
    agent_spacing = 110
    agents = [
        ('PLAN', COLORS['secondary'], '📋'),
        ('SEARCH', COLORS['accent'], '🔍'),
        ('EXTRACT', COLORS['teal'], '📄'),
        ('VERIFY', COLORS['purple'], '✓'),
        ('DRAFT', COLORS['pink'], '✍')
    ]

    for i, (name, color, icon) in enumerate(agents):
        x = center_x - 250 + i * agent_spacing

        # Agent circle
        dwg.add(draw_icon_circle(x, agent_y, 35, color, icon))

        # Agent name
        dwg.add(dwg.text(
            name,
            insert=(x, agent_y + 60),
            text_anchor='middle',
            font_size='14px',
            font_weight='bold',
            fill=COLORS['dark'],
            font_family='Arial, sans-serif'
        ))

        # Arrow to next agent
        if i < len(agents) - 1:
            dwg.add(dwg.line(
                start=(x + 40, agent_y),
                end=(x + agent_spacing - 40, agent_y),
                stroke=COLORS['gray'],
                stroke_width=3,
                opacity=0.4,
                stroke_dasharray='5,5'
            ))

    # Data sources below agents
    sources_y = agent_y + 120
    dwg.add(dwg.text(
        'Data Sources',
        insert=(center_x, sources_y),
        text_anchor='middle',
        font_size='16px',
        font_weight='bold',
        fill=COLORS['gray'],
        font_family='Arial, sans-serif'
    ))

    # Source badges
    sources = ['arXiv', 'OpenAlex', 'Semantic Scholar', 'Crossref']
    source_start_x = center_x - 220
    for i, source in enumerate(sources):
        x = source_start_x + i * 120
        badge_group = dwg.g()
        badge_group.add(dwg.rect(
            insert=(x, sources_y + 15),
            size=(100, 30),
            rx=15, ry=15,
            fill=COLORS['accent'],
            opacity=0.2,
            stroke=COLORS['accent'],
            stroke_width=2
        ))
        badge_group.add(dwg.text(
            source,
            insert=(x + 50, sources_y + 35),
            text_anchor='middle',
            font_size='11px',
            font_weight='bold',
            fill=COLORS['accent'],
            font_family='Arial, sans-serif'
        ))
        dwg.add(badge_group)

    # LLM indicator
    llm_y = agent_y + 200
    llm_badge = dwg.g()
    llm_badge.add(dwg.rect(
        insert=(center_x - 60, llm_y),
        size=(120, 35),
        rx=18, ry=18,
        fill=COLORS['pink'],
        stroke='white',
        stroke_width=2
    ))
    llm_badge.add(dwg.text(
        '🤖 LLM (1x)',
        insert=(center_x, llm_y + 23),
        text_anchor='middle',
        font_size='14px',
        font_weight='bold',
        fill='white',
        font_family='Arial, sans-serif'
    ))
    dwg.add(llm_badge)

    # Arrow to output
    dwg.add(draw_curved_arrow(center_x + 300, workflow_y + 90, 1470, workflow_y + 90, COLORS['pink'], 30))

    # 3. OUTPUT STAGE
    output_x = 1770
    dwg.add(draw_card(output_x - 80, workflow_y, 160, 180, COLORS['pink']))
    dwg.add(draw_icon_circle(output_x, workflow_y + 60, 40, COLORS['pink'], '📊'))
    dwg.add(dwg.text(
        'Answer',
        insert=(output_x, workflow_y + 130),
        text_anchor='middle',
        font_size='20px',
        font_weight='bold',
        fill='white',
        font_family='Arial, sans-serif'
    ))
    dwg.add(dwg.text(
        'With Evidence',
        insert=(output_x, workflow_y + 155),
        text_anchor='middle',
        font_size='14px',
        fill='white',
        font_family='Arial, sans-serif',
        opacity=0.9
    ))

    # ============ KEY FEATURES (Bottom) ============
    features_y = 720
    feature_width = 350
    feature_height = 120
    feature_spacing = 50

    features = [
        {
            'icon': '🎯',
            'title': 'Multi-Source Intelligence',
            'desc': 'Aggregates from 4 academic databases',
            'color': COLORS['secondary']
        },
        {
            'icon': '⚡',
            'title': 'Smart Filtering',
            'desc': 'Profile-based ranking & deduplication',
            'color': COLORS['accent']
        },
        {
            'icon': '🔗',
            'title': 'Evidence Grounding',
            'desc': 'Citation-backed answers with provenance',
            'color': COLORS['purple']
        },
        {
            'icon': '🚀',
            'title': 'Fast & Reliable',
            'desc': '25-70s end-to-end with retry logic',
            'color': COLORS['teal']
        }
    ]

    start_x = (1920 - (feature_width * 4 + feature_spacing * 3)) / 2

    for i, feature in enumerate(features):
        x = start_x + i * (feature_width + feature_spacing)

        # Feature card
        card = draw_card(x, features_y, feature_width, feature_height, 'white', 0.95)
        dwg.add(card)

        # Icon
        dwg.add(dwg.text(
            feature['icon'],
            insert=(x + 40, features_y + 50),
            font_size='40px',
            font_family='Arial, sans-serif'
        ))

        # Title
        dwg.add(dwg.text(
            feature['title'],
            insert=(x + 90, features_y + 40),
            font_size='18px',
            font_weight='bold',
            fill=feature['color'],
            font_family='Arial, sans-serif'
        ))

        # Description
        dwg.add(dwg.text(
            feature['desc'],
            insert=(x + 90, features_y + 65),
            font_size='13px',
            fill=COLORS['gray'],
            font_family='Arial, sans-serif'
        ))

    # ============ STATS BADGES (Top right) ============
    stats_x = 1650
    stats_y = 180

    stats = [
        ('21', 'API Calls', COLORS['accent']),
        ('5', 'Subqueries', COLORS['secondary']),
        ('10-30', 'Papers', COLORS['purple'])
    ]

    for i, (number, label, color) in enumerate(stats):
        y = stats_y + i * 70

        stat_group = dwg.g()
        stat_group.add(dwg.rect(
            insert=(stats_x, y),
            size=(200, 55),
            rx=12, ry=12,
            fill='white',
            stroke=color,
            stroke_width=2,
            opacity=0.95
        ))
        stat_group.add(dwg.text(
            number,
            insert=(stats_x + 30, y + 35),
            font_size='28px',
            font_weight='bold',
            fill=color,
            font_family='Arial, sans-serif'
        ))
        stat_group.add(dwg.text(
            label,
            insert=(stats_x + 100, y + 32),
            font_size='14px',
            fill=COLORS['gray'],
            font_family='Arial, sans-serif'
        ))
        dwg.add(stat_group)

    # ============ TECH STACK BADGE (Top left) ============
    tech_x = 70
    tech_y = 180

    tech_group = dwg.g()
    tech_group.add(dwg.rect(
        insert=(tech_x, tech_y),
        size=(200, 140),
        rx=12, ry=12,
        fill='white',
        stroke=COLORS['primary'],
        stroke_width=2,
        opacity=0.95
    ))
    tech_group.add(dwg.text(
        'Built With',
        insert=(tech_x + 100, tech_y + 30),
        text_anchor='middle',
        font_size='14px',
        font_weight='bold',
        fill=COLORS['dark'],
        font_family='Arial, sans-serif'
    ))

    tech_items = ['LangGraph', 'LiteLLM', 'PaperQA2', 'Qdrant']
    for i, item in enumerate(tech_items):
        tech_group.add(dwg.text(
            f'• {item}',
            insert=(tech_x + 20, tech_y + 60 + i * 20),
            font_size='12px',
            fill=COLORS['gray'],
            font_family='Arial, sans-serif'
        ))
    dwg.add(tech_group)

    # ============ FOOTER ============
    footer_y = 1040
    dwg.add(dwg.text(
        'evagent - Academic Literature Multi-Agent System',
        insert=(960, footer_y),
        text_anchor='middle',
        font_size='14px',
        fill=COLORS['gray'],
        font_family='Arial, sans-serif',
        opacity=0.7
    ))

    dwg.save()
    print("✓ Beautiful SVG diagram generated: output/diagrams/evagent_promo_v2.svg")

if __name__ == '__main__':
    create_beautiful_promo_svg()

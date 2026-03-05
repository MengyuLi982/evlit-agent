#!/usr/bin/env python3
"""Generate a simple, clear promotional diagram for evagent."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import matplotlib.patheffects as path_effects

# Set up the figure with better proportions
fig, ax = plt.subplots(figsize=(16, 10))
ax.set_xlim(0, 16)
ax.set_ylim(0, 10)
ax.axis('off')

# Modern color scheme
COLOR_INPUT = '#4A90E2'      # Blue
COLOR_PROCESS = '#7ED321'    # Green
COLOR_API = '#F5A623'        # Orange
COLOR_OUTPUT = '#BD10E0'     # Purple
COLOR_ACCENT = '#50E3C2'     # Teal

def draw_rounded_box(ax, x, y, width, height, text, color, fontsize=14, alpha=0.9):
    """Draw a modern rounded box."""
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.15",
        facecolor=color,
        edgecolor='white',
        linewidth=3,
        alpha=alpha
    )
    ax.add_patch(box)

    txt = ax.text(x + width/2, y + height/2, text,
                  ha='center', va='center',
                  fontsize=fontsize, fontweight='bold',
                  color='white')
    txt.set_path_effects([path_effects.withStroke(linewidth=2, foreground='black', alpha=0.3)])

def draw_thick_arrow(ax, x1, y1, x2, y2, color='#333333', width=4):
    """Draw a thick arrow."""
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle='->,head_width=0.6,head_length=0.4',
        mutation_scale=30,
        linewidth=width,
        color=color,
        alpha=0.8
    )
    ax.add_patch(arrow)

def draw_circle_node(ax, x, y, radius, text, color, fontsize=12):
    """Draw a circular node."""
    circle = Circle((x, y), radius, facecolor=color, edgecolor='white', linewidth=3, alpha=0.9)
    ax.add_patch(circle)
    txt = ax.text(x, y, text, ha='center', va='center',
                  fontsize=fontsize, fontweight='bold', color='white')
    txt.set_path_effects([path_effects.withStroke(linewidth=2, foreground='black', alpha=0.3)])

# Title
title = ax.text(8, 9.5, 'EventVision Literature Agent',
                ha='center', va='top', fontsize=28, fontweight='bold', color='#2C3E50')
title.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])

subtitle = ax.text(8, 9, 'Multi-Agent RAG System for Academic Research',
                   ha='center', va='top', fontsize=16, color='#7F8C8D', style='italic')

# 1. INPUT - User Query
draw_rounded_box(ax, 0.5, 7, 2.5, 1.2, 'User Query\n"What datasets\nare used?"', COLOR_INPUT, 13)

# Arrow to pipeline
draw_thick_arrow(ax, 3.2, 7.6, 4.3, 7.6, '#4A90E2')

# 2. PIPELINE - 5 Stages in a row
pipeline_y = 6.8
pipeline_height = 1.6
stage_width = 1.8
gap = 0.15

stages = [
    ('PLAN', 'Generate\nSubqueries'),
    ('SEARCH', 'Multi-Source\nRetrieval'),
    ('EXTRACT', 'Evidence\nExtraction'),
    ('VERIFY', 'Quality\nCheck'),
    ('DRAFT', 'LLM\nSynthesis')
]

stage_colors = ['#7ED321', '#7ED321', '#7ED321', '#7ED321', '#BD10E0']

for i, (title, desc) in enumerate(stages):
    x = 4.5 + i * (stage_width + gap)

    # Main box
    draw_rounded_box(ax, x, pipeline_y, stage_width, pipeline_height,
                     f'{title}\n\n{desc}', stage_colors[i], 11)

    # Arrow to next stage
    if i < len(stages) - 1:
        draw_thick_arrow(ax, x + stage_width + 0.05, pipeline_y + pipeline_height/2,
                        x + stage_width + gap - 0.05, pipeline_y + pipeline_height/2,
                        '#555555', 3)

# 3. ACADEMIC SOURCES - Below SEARCH stage
sources_y = 4.8
source_x_start = 5.8
source_spacing = 1.3

sources = ['arXiv', 'OpenAlex', 'Semantic\nScholar', 'Crossref']
for i, source in enumerate(sources):
    x = source_x_start + i * source_spacing
    draw_circle_node(ax, x, sources_y, 0.45, source, COLOR_API, 9)
    # Arrow from SEARCH to source
    draw_thick_arrow(ax, 6.4, pipeline_y - 0.1, x, sources_y + 0.45, COLOR_API, 2)

# Label for sources
ax.text(7.5, 4.1, '20 API Calls', ha='center', fontsize=11,
        fontweight='bold', color=COLOR_API,
        bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                 edgecolor=COLOR_API, linewidth=2))

# 4. LLM API - Below DRAFT stage
llm_y = 5.2
llm_x = 13.5
draw_circle_node(ax, llm_x, llm_y, 0.55, 'LLM\nAPI\n(1x)', COLOR_OUTPUT, 10)
# Arrow from DRAFT to LLM
draw_thick_arrow(ax, 13.5, pipeline_y - 0.1, llm_x, llm_y + 0.55, COLOR_OUTPUT, 2)

# 5. OUTPUT - Grounded Answer
draw_rounded_box(ax, 11, 2.5, 4, 1.5,
                 'Grounded Answer\n+ Evidence + Citations\n+ Provenance Tracking',
                 COLOR_OUTPUT, 13)

# Arrow from pipeline to output
draw_thick_arrow(ax, 13.5, pipeline_y - 0.1, 13, 4.0, COLOR_OUTPUT, 4)

# 6. KEY FEATURES - Left side boxes
feature_y_start = 4.5
feature_height = 0.7
feature_width = 3.5

features = [
    ('Multi-Source Retrieval', '4 academic databases'),
    ('Profile-Based Filtering', 'Domain-specific ranking'),
    ('Smart Deduplication', 'DOI > arXiv > Title+Author'),
    ('Evidence Grounding', 'Citation-backed answers')
]

for i, (title, desc) in enumerate(features):
    y = feature_y_start - i * (feature_height + 0.2)

    # Feature box
    box = FancyBboxPatch(
        (0.3, y), feature_width, feature_height,
        boxstyle="round,pad=0.1",
        facecolor='white',
        edgecolor=COLOR_ACCENT,
        linewidth=2.5,
        alpha=0.95
    )
    ax.add_patch(box)

    ax.text(0.5, y + feature_height/2 + 0.15, title,
            ha='left', va='center', fontsize=11, fontweight='bold', color='#2C3E50')
    ax.text(0.5, y + feature_height/2 - 0.15, desc,
            ha='left', va='center', fontsize=9, color='#7F8C8D', style='italic')

# 7. STATS BOX - Bottom right
stats_box = FancyBboxPatch(
    (11, 0.5), 4, 1.5,
    boxstyle="round,pad=0.15",
    facecolor='#F8F9FA',
    edgecolor='#DEE2E6',
    linewidth=2
)
ax.add_patch(stats_box)

stats_text = """Performance:
• 21 API calls per query
• 25-70 sec end-to-end
• 5 subqueries generated
• 10-30 papers retrieved"""

ax.text(11.2, 1.7, stats_text, ha='left', va='top', fontsize=9,
        family='monospace', color='#495057')

# 8. ARCHITECTURE BADGE - Bottom left
arch_box = FancyBboxPatch(
    (0.3, 0.5), 3.5, 1.5,
    boxstyle="round,pad=0.15",
    facecolor='#FFF8DC',
    edgecolor='#F5A623',
    linewidth=2
)
ax.add_patch(arch_box)

arch_text = """Built With:
✓ LangGraph orchestration
✓ LiteLLM integration
✓ PaperQA2 patterns
✓ Multi-agent workflow"""

ax.text(0.5, 1.7, arch_text, ha='left', va='top', fontsize=9,
        family='monospace', color='#856404')

# Watermark
ax.text(8, 0.2, 'evagent - Academic Literature Multi-Agent System',
        ha='center', fontsize=10, color='#ADB5BD', style='italic')

plt.tight_layout()
plt.savefig('/home2/mengyu/evlit-agent/output/diagrams/evagent_promo.png',
            dpi=300, bbox_inches='tight', facecolor='#F0F2F5')
print("✓ Promotional diagram generated: output/diagrams/evagent_promo.png")

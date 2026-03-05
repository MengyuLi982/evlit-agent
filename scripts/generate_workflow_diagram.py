#!/usr/bin/env python3
"""Generate high-level workflow diagram for evagent ask command."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.lines as mlines

# Set up the figure
fig, ax = plt.subplots(figsize=(14, 16))
ax.set_xlim(0, 10)
ax.set_ylim(0, 20)
ax.axis('off')

# Color scheme
COLOR_USER = '#E8F4F8'
COLOR_CLI = '#B8E6F0'
COLOR_GRAPH = '#FFE5B4'
COLOR_NODE = '#D4E8D4'
COLOR_API = '#FFD4D4'
COLOR_LLM = '#E8D4FF'
COLOR_OUTPUT = '#F0E8D4'

def draw_box(ax, x, y, width, height, text, color, fontsize=10, fontweight='normal'):
    """Draw a rounded rectangle box with text."""
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.1",
        facecolor=color,
        edgecolor='black',
        linewidth=2
    )
    ax.add_patch(box)
    ax.text(x + width/2, y + height/2, text,
            ha='center', va='center',
            fontsize=fontsize, fontweight=fontweight,
            wrap=True)

def draw_arrow(ax, x1, y1, x2, y2, label='', style='->'):
    """Draw an arrow between two points."""
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle=style,
        mutation_scale=20,
        linewidth=2,
        color='black'
    )
    ax.add_patch(arrow)
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x + 0.3, mid_y, label,
                fontsize=8, style='italic',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

# Title
ax.text(5, 19.5, 'EventVision Literature Agent - evagent ask 工作流程',
        ha='center', va='top', fontsize=16, fontweight='bold')

# 1. User Input
draw_box(ax, 3, 18, 4, 0.8, '用户命令\nevagent ask "query" --profile sps', COLOR_USER, 10, 'bold')
draw_arrow(ax, 5, 18, 5, 17.2)

# 2. CLI Entry
draw_box(ax, 2.5, 16.2, 5, 0.8, 'CLI入口: app.py::ask()', COLOR_CLI, 10, 'bold')
ax.text(5, 15.8, '初始化: Settings, MultiSourceRetriever, LLMClient, Graph',
        ha='center', fontsize=8, style='italic')
draw_arrow(ax, 5, 16.2, 5, 15.4)

# 3. LangGraph Orchestration
draw_box(ax, 1.5, 14.4, 7, 0.8, 'LangGraph 图编排器', COLOR_GRAPH, 11, 'bold')
draw_arrow(ax, 5, 14.4, 5, 13.6)

# 4. Node 1: Plan
y_node = 12.8
draw_box(ax, 2, y_node, 6, 0.7, '节点1: plan_subquestions', COLOR_NODE, 10, 'bold')
ax.text(5, y_node - 0.3, '生成5个子查询（硬编码规则 + 领域术语扩展）',
        ha='center', fontsize=8)
draw_arrow(ax, 5, y_node, 5, y_node - 0.8)

# 5. Node 2: Retrieve
y_node = 11.2
draw_box(ax, 2, y_node, 6, 0.7, '节点2: retrieve_candidates', COLOR_NODE, 10, 'bold')
ax.text(5, y_node - 0.3, '遍历5个子查询，每个调用4个学术API',
        ha='center', fontsize=8)
draw_arrow(ax, 5, y_node, 5, y_node - 0.8)

# Academic APIs (side box)
draw_box(ax, 0.2, 9.8, 1.5, 1.2, 'arXiv\nOpenAlex\nSemantic\nScholar\nCrossref',
         COLOR_API, 8)
draw_arrow(ax, 2, y_node - 0.3, 1.7, 10.4, '20次\nHTTP', '<->')

# 6. Filtering & Ranking
y_node = 9.5
draw_box(ax, 2, y_node, 6, 0.7, 'profile_filter_and_rank', COLOR_NODE, 10, 'bold')
ax.text(5, y_node - 0.3, '评分 → 过滤 → 去重 → 排序',
        ha='center', fontsize=8)
ax.text(5, y_node - 0.6, '评分公式: 0.55×领域 + 0.25×来源 + 0.20×时效 - 负面惩罚',
        ha='center', fontsize=7, style='italic', color='#666')
draw_arrow(ax, 5, y_node, 5, y_node - 1.0)

# 7. Node 3: Evidence
y_node = 7.8
draw_box(ax, 2, y_node, 6, 0.7, '节点3: extract_evidence', COLOR_NODE, 10, 'bold')
ax.text(5, y_node - 0.3, '从��12篇候选论文提取摘要作为证据',
        ha='center', fontsize=8)
draw_arrow(ax, 5, y_node, 5, y_node - 0.8)

# 8. Node 4: Critic
y_node = 6.3
draw_box(ax, 2, y_node, 6, 0.7, '节点4: critic_and_fix', COLOR_NODE, 10, 'bold')
ax.text(5, y_node - 0.3, '检查证据数量是否满足 min_evidence',
        ha='center', fontsize=8)
draw_arrow(ax, 5, y_node, 5, y_node - 0.8)

# Decision diamond
y_decision = 4.8
diamond = mpatches.FancyBboxPatch(
    (4.3, y_decision), 1.4, 0.6,
    boxstyle="round,pad=0.05",
    facecolor='#FFFFCC',
    edgecolor='black',
    linewidth=2
)
ax.add_patch(diamond)
ax.text(5, y_decision + 0.3, '证据充足?',
        ha='center', va='center', fontsize=9, fontweight='bold')

# Retry path
draw_arrow(ax, 4.3, y_decision + 0.3, 2, y_node - 0.3, 'No\n(重试1次)', '->')
ax.text(3, y_decision + 0.8, 'needs_more=True', fontsize=7, style='italic')

# Continue path
draw_arrow(ax, 5, y_decision, 5, y_decision - 0.8, 'Yes')

# 9. Node 5: Draft (LLM Call)
y_node = 3.2
draw_box(ax, 2, y_node, 6, 0.7, '节点5: draft_answer', COLOR_NODE, 10, 'bold')
ax.text(5, y_node - 0.3, '★ 唯一的LLM调用点 ★',
        ha='center', fontsize=9, fontweight='bold', color='red')
draw_arrow(ax, 5, y_node, 5, y_node - 0.8)

# LLM API (side box)
draw_box(ax, 8.3, 2.5, 1.5, 1.2, 'LiteLLM\nAPI\n\nqwen3-max\ntemp=0.1\nmax=700',
         COLOR_LLM, 8)
draw_arrow(ax, 8, y_node - 0.3, 8.3, 3.1, '1次\nAPI调用', '<->')

# 10. Output
y_node = 1.6
draw_box(ax, 2.5, y_node, 5, 0.7, '返回 final_state', COLOR_OUTPUT, 10, 'bold')
ax.text(5, y_node - 0.3, 'answer + evidence + candidates + filter_stats',
        ha='center', fontsize=8)
draw_arrow(ax, 5, y_node, 5, y_node - 0.8)

# 11. Persistence
y_node = 0.5
draw_box(ax, 2.5, y_node, 5, 0.6, '持久化到 runs/ask_runs.jsonl', COLOR_OUTPUT, 9)

# Legend
legend_y = 0.2
legend_elements = [
    mpatches.Patch(facecolor=COLOR_USER, edgecolor='black', label='用户输入'),
    mpatches.Patch(facecolor=COLOR_CLI, edgecolor='black', label='CLI层'),
    mpatches.Patch(facecolor=COLOR_GRAPH, edgecolor='black', label='图编排'),
    mpatches.Patch(facecolor=COLOR_NODE, edgecolor='black', label='Agent节点'),
    mpatches.Patch(facecolor=COLOR_API, edgecolor='black', label='学术API'),
    mpatches.Patch(facecolor=COLOR_LLM, edgecolor='black', label='LLM API'),
    mpatches.Patch(facecolor=COLOR_OUTPUT, edgecolor='black', label='输出/存储'),
]
ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, legend_y),
          ncol=4, fontsize=8, framealpha=0.9)

# Statistics box
stats_text = """关键统计:
• 总API调用: 21次 (20次学术 + 1次LLM)
• 子查询数: 5个
• 学术源: 4个 (arXiv, OpenAlex, S2, Crossref)
• 去重策略: DOI > arXiv_id > title+author+year
• 预估耗时: 25-70秒"""

ax.text(9.8, 19, stats_text,
        ha='right', va='top', fontsize=7,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#F5F5F5', alpha=0.9),
        family='monospace')

# Borrowed components box
borrowed_text = """架构借鉴:
✓ PaperQA2: 多源检索 + 证据提取
✓ GPT-Researcher: 子问题分解
✓ STORM: 分阶段合成
✓ LangGraph: 图编排框架"""

ax.text(0.2, 19, borrowed_text,
        ha='left', va='top', fontsize=7,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF8DC', alpha=0.9),
        family='monospace')

plt.tight_layout()
plt.savefig('/home2/mengyu/evlit-agent/output/diagrams/evagent_ask_workflow.png',
            dpi=300, bbox_inches='tight', facecolor='white')
print("✓ 流程图已生成: output/diagrams/evagent_ask_workflow.png")

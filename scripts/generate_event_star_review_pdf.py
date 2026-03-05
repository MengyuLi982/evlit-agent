from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


@dataclass
class PaperItem:
    bucket: str
    title: str
    year: str
    venue: str
    link: str
    summary: str
    model_type: str


def register_fonts() -> None:
    body_font_path = "/usr/share/fonts/truetype/arphic/uming.ttc"
    heading_font_path = "/usr/share/fonts/truetype/arphic/ukai.ttc"
    pdfmetrics.registerFont(TTFont("NotoSansCJK", body_font_path))
    pdfmetrics.registerFont(TTFont("NotoSansCJK-Bold", heading_font_path))


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ZhTitle",
            parent=styles["Title"],
            fontName="NotoSansCJK-Bold",
            fontSize=18,
            leading=24,
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ZhHeading",
            parent=styles["Heading2"],
            fontName="NotoSansCJK-Bold",
            fontSize=13,
            leading=18,
            spaceBefore=8,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ZhBody",
            parent=styles["BodyText"],
            fontName="NotoSansCJK",
            fontSize=10.5,
            leading=15,
            wordWrap="CJK",
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ZhSmall",
            parent=styles["BodyText"],
            fontName="NotoSansCJK",
            fontSize=9.2,
            leading=13,
            wordWrap="CJK",
            spaceAfter=3,
        )
    )
    return styles


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("NotoSansCJK", 9)
    canvas.drawRightString(200 * mm, 10 * mm, f"第 {doc.page} 页")
    canvas.restoreState()


def build_items() -> list[PaperItem]:
    return [
        PaperItem(
            bucket="A-严格匹配",
            title="Asynchronous Kalman Filter for Event-Based Star Tracking",
            year="2022/2023",
            venue="ECCV Workshops / LNCS",
            link="https://doi.org/10.1007/978-3-031-25056-9_5",
            summary="提出异步卡尔曼滤波框架处理事件流，实现星点异步更新与稳健跟踪。",
            model_type="Kalman Filter family（异步KF）",
        ),
        PaperItem(
            bucket="A-严格匹配",
            title="The Adaptive Threshold Adjustment Method Based on Event-Based Star Tracker",
            year="2024",
            venue="IAECST",
            link="https://doi.org/10.1109/IAECST64597.2024.11118029",
            summary="针对背光导致的星点检测困难，使用SVR预测与ROC阈值优化进行自适应门限调整。",
            model_type="传统机器学习（SVR）+ 规则优化（ROC）",
        ),
        PaperItem(
            bucket="A-严格匹配",
            title="Event-based detectors for laser guide star tip-tilt sensing",
            year="2024/2025",
            venue="arXiv / Optical Engineering",
            link="https://doi.org/10.1117/1.OE.64.4.043102",
            summary="验证事件传感器在导星tip-tilt感知中的高时域分辨率优势，面向自适应光学场景。",
            model_type="事件信号处理方法（非Transformer）",
        ),
        PaperItem(
            bucket="A-严格匹配",
            title="EBS-EKF: Accurate and High Frequency Event-Based Star Tracking",
            year="2025",
            venue="CVPR 2025",
            link="https://doi.org/10.1109/CVPR52734.2025.00610",
            summary="结合事件相机电路机理建模与EKF估计，在真实夜空数据上实现高频高精度星跟踪。",
            model_type="Kalman Filter family（EKF）",
        ),
        PaperItem(
            bucket="A-严格匹配",
            title="Event-based Star Tracking under Spacecraft Jitter: the e-STURT Dataset",
            year="2025/2026",
            venue="arXiv / IEEE TAES",
            link="https://doi.org/10.1109/TAES.2026.3653351",
            summary="提出事件相机星跟踪抖动数据集与硬件仿真采集方案，支撑抖动场景算法评测。",
            model_type="数据集/Benchmark（非单一网络）",
        ),
        PaperItem(
            bucket="A-严格匹配",
            title="Fully Neuromorphic Star Tracking for Spacecraft Jitter Mitigation",
            year="2025",
            venue="IAF Space Communications and Navigation Symposium",
            link="https://doi.org/10.52202/083082-0075",
            summary="强调神经形态端到端星跟踪以降低航天器抖动影响，提高鲁棒与实时性。",
            model_type="神经形态方法（SNN-style pipeline）",
        ),
        PaperItem(
            bucket="A-严格匹配",
            title="Quantifying Accuracy of an Event-Based Star Tracker via Earth's Rotation",
            year="2025",
            venue="ICCVW 2025",
            link="https://doi.org/10.1109/ICCVW69036.2025.00487",
            summary="以地球自转作为高精度真值来源，量化事件星跟踪系统在真实观测条件下的精度。",
            model_type="基于物理先验的评测与跟踪管线",
        ),
        PaperItem(
            bucket="A-严格匹配",
            title="Dual-modality event-frame fusion for blind star image motion deblurring via sparse residual learning",
            year="2025",
            venue="Optics and Lasers in Engineering",
            link="https://doi.org/10.1016/j.optlaseng.2025.109368",
            summary="融合事件流与帧图像进行星图运动去模糊，改善后续星点检测与定位质量。",
            model_type="CNN family（稀疏残差融合网络）",
        ),
        PaperItem(
            bucket="A-严格匹配",
            title="Neuromorphic Cameras in Astronomy: Unveiling the Future of Celestial Imaging Beyond Conventional Limits",
            year="2025",
            venue="arXiv",
            link="https://arxiv.org/abs/2503.15883",
            summary="综述神经形态相机在天文成像中的优势与潜在路线，包含望远镜观测示例。",
            model_type="综述/展望（神经形态传感方向）",
        ),
        PaperItem(
            bucket="B-强相关扩展",
            title="Backlight and dim space object detection based on a novel event camera",
            year="2024",
            venue="PeerJ Computer Science",
            link="https://doi.org/10.7717/peerj-cs.2192",
            summary="面向背光与低照空间目标，提出异步卷积记忆网络（ACMNet）进行事件目标检测。",
            model_type="CNN family（ACMNet）",
        ),
        PaperItem(
            bucket="B-强相关扩展",
            title="End-to-end space object detection method based on event camera",
            year="2023",
            venue="SPIE PIOE 2023",
            link="https://doi.org/10.1117/12.3011053",
            summary="将异步事件流编码为EST表示并构建端到端检测网络，用于空间目标检测。",
            model_type="深度网络（EST表示 + 前馈检测头）",
        ),
        PaperItem(
            bucket="B-强相关扩展",
            title="Towards Bridging the Space Domain Gap for Satellite Pose Estimation using Event Sensing",
            year="2023",
            venue="ICRA 2023",
            link="https://doi.org/10.1109/ICRA48891.2023.10160531",
            summary="利用事件感知缓解仿真到空间环境的域差异，提升卫星位姿估计泛化能力。",
            model_type="深度学习 + 域适配（非Transformer主导）",
        ),
        PaperItem(
            bucket="B-强相关扩展",
            title="Leveraging Event-Based Cameras for Enhanced Space Situational Awareness: A Nanosatellite Mission Architecture Study",
            year="2024",
            venue="22nd IAA Symposium on Space Debris",
            link="https://doi.org/10.52202/078360-0131",
            summary="从任务体系结构角度讨论事件相机在空间态势感知中的部署方案与工程价值。",
            model_type="任务架构研究（非特定模型）",
        ),
    ]


def build_group_table(styles):
    header = [
        Paragraph("分组", styles["ZhSmall"]),
        Paragraph("代表文献", styles["ZhSmall"]),
        Paragraph("主流技术特征", styles["ZhSmall"]),
        Paragraph("研究空白点", styles["ZhSmall"]),
    ]
    rows = [
        [
            Paragraph("滤波法", styles["ZhSmall"]),
            Paragraph(
                "Asynchronous KF (2022/2023); EBS-EKF (2025); Earth-Rotation Accuracy (2025)",
                styles["ZhSmall"],
            ),
            Paragraph(
                "依赖状态空间建模与物理先验，实时性强、可解释性好。",
                styles["ZhSmall"],
            ),
            Paragraph(
                "缺少跨星等/跨传感器统一误差模型；对极端抖动与弱星点场景的鲁棒性仍需系统验证。",
                styles["ZhSmall"],
            ),
        ],
        [
            Paragraph("CNN", styles["ZhSmall"]),
            Paragraph(
                "Dual-modality Deblurring (2025); ACMNet Space Object Detection (2024); End-to-end EST Detection (2023)",
                styles["ZhSmall"],
            ),
            Paragraph(
                "事件-帧融合与时空特征提取能力强，适合复杂噪声与弱纹理场景。",
                styles["ZhSmall"],
            ),
            Paragraph(
                "公开星点级标注数据不足；跨轨道、跨光学系统的域泛化能力仍弱；缺乏统一算力-精度基准。",
                styles["ZhSmall"],
            ),
        ],
        [
            Paragraph("神经形态", styles["ZhSmall"]),
            Paragraph(
                "Fully Neuromorphic Star Tracking (2025); Neuromorphic Cameras in Astronomy (2025)",
                styles["ZhSmall"],
            ),
            Paragraph(
                "强调异步脉冲处理与低功耗潜力，适配星载实时处理需求。",
                styles["ZhSmall"],
            ),
            Paragraph(
                "可复现实验基线和开源工具链不足；与传统KF/CNN方法的公平对比和任务闭环评测不充分。",
                styles["ZhSmall"],
            ),
        ],
        [
            Paragraph("数据集", styles["ZhSmall"]),
            Paragraph("e-STURT Dataset (2025/2026)", styles["ZhSmall"]),
            Paragraph(
                "首次系统覆盖抖动条件下事件星观测，为算法训练和评测提供基础。",
                styles["ZhSmall"],
            ),
            Paragraph(
                "真实轨道数据稀缺；标注标准尚未统一；缺少与传统星敏感器数据的配对多模态基准。",
                styles["ZhSmall"],
            ),
        ],
    ]
    data = [header] + rows
    table = Table(data, colWidths=[22 * mm, 55 * mm, 48 * mm, 55 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "NotoSansCJK-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "NotoSansCJK"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF7")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1A1A1A")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B5B5B5")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def build_pdf(output_path: Path) -> None:
    register_fonts()
    styles = build_styles()
    items = build_items()

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Event Camera 星跟踪与星检测文献汇总（近5年）",
        author="Codex",
    )

    now_text = datetime.now().strftime("%Y-%m-%d %H:%M")
    story = [
        Paragraph("Event Camera 星跟踪与星检测文献汇总（近5年）", styles["ZhTitle"]),
        Paragraph(f"检索范围：2021-03-04 至 2026-03-04；生成时间：{now_text}", styles["ZhBody"]),
        Paragraph("说明：A为严格匹配（event camera + star tracking/detection）；B为强相关扩展。", styles["ZhBody"]),
        Spacer(1, 4),
    ]

    story.append(Paragraph("A/B文献清单（共13篇）", styles["ZhHeading"]))
    for idx, item in enumerate(items, start=1):
        story.append(
            Paragraph(
                f"{idx}. [{item.bucket}] <b>{item.title}</b> ({item.year})",
                styles["ZhBody"],
            )
        )
        story.append(Paragraph(f"来源：{item.venue}", styles["ZhSmall"]))
        story.append(Paragraph(f"链接：{item.link}", styles["ZhSmall"]))
        story.append(Paragraph(f"内容介绍：{item.summary}", styles["ZhSmall"]))
        story.append(Paragraph(f"模型类型：{item.model_type}", styles["ZhSmall"]))
        story.append(Spacer(1, 3))

    story.append(PageBreak())
    story.append(Paragraph("分组总结与研究空白点", styles["ZhHeading"]))
    story.append(
        Paragraph(
            "按“滤波法/CNN/神经形态/数据集”分组，给出当前研究重点与待解决问题。",
            styles["ZhBody"],
        )
    )
    story.append(build_group_table(styles))

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)


def main() -> None:
    out = Path("/home2/mengyu/evlit-agent/output/pdf/event_camera_star_tracking_detection_review_2021_2026.pdf")
    out.parent.mkdir(parents=True, exist_ok=True)
    build_pdf(out)
    print(out)


if __name__ == "__main__":
    main()

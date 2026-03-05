from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
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


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="EnTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=24,
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="EnHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=18,
            spaceBefore=8,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="EnBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=15,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="EnSmall",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=13,
            spaceAfter=3,
        )
    )
    return styles


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(200 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_items() -> list[PaperItem]:
    return [
        PaperItem(
            bucket="A-Strict Match",
            title="Asynchronous Kalman Filter for Event-Based Star Tracking",
            year="2022/2023",
            venue="ECCV Workshops / LNCS",
            link="https://doi.org/10.1007/978-3-031-25056-9_5",
            summary="Proposes an asynchronous Kalman filtering framework for event streams, enabling robust star tracking with asynchronous updates.",
            model_type="Kalman Filter family (Asynchronous KF)",
        ),
        PaperItem(
            bucket="A-Strict Match",
            title="The Adaptive Threshold Adjustment Method Based on Event-Based Star Tracker",
            year="2024",
            venue="IAECST",
            link="https://doi.org/10.1109/IAECST64597.2024.11118029",
            summary="Targets backlight-induced detection failure using SVR-based prediction and ROC-based threshold optimization.",
            model_type="Classical ML (SVR) + Rule-based Optimization (ROC)",
        ),
        PaperItem(
            bucket="A-Strict Match",
            title="Event-based detectors for laser guide star tip-tilt sensing",
            year="2024/2025",
            venue="arXiv / Optical Engineering",
            link="https://doi.org/10.1117/1.OE.64.4.043102",
            summary="Evaluates event-based sensing for guide-star tip-tilt measurement and highlights temporal-resolution benefits for adaptive optics.",
            model_type="Event Signal Processing (Non-Transformer)",
        ),
        PaperItem(
            bucket="A-Strict Match",
            title="EBS-EKF: Accurate and High Frequency Event-Based Star Tracking",
            year="2025",
            venue="CVPR 2025",
            link="https://doi.org/10.1109/CVPR52734.2025.00610",
            summary="Combines event-camera circuit modeling with EKF state estimation for high-frequency, high-accuracy star tracking on real night-sky data.",
            model_type="Kalman Filter family (EKF)",
        ),
        PaperItem(
            bucket="A-Strict Match",
            title="Event-based Star Tracking under Spacecraft Jitter: the e-STURT Dataset",
            year="2025/2026",
            venue="arXiv / IEEE TAES",
            link="https://doi.org/10.1109/TAES.2026.3653351",
            summary="Introduces a dedicated event-based star-tracking dataset under controlled spacecraft jitter with hardware-in-the-loop acquisition.",
            model_type="Dataset / Benchmark (Not a single model)",
        ),
        PaperItem(
            bucket="A-Strict Match",
            title="Fully Neuromorphic Star Tracking for Spacecraft Jitter Mitigation",
            year="2025",
            venue="IAF Space Communications and Navigation Symposium",
            link="https://doi.org/10.52202/083082-0075",
            summary="Emphasizes a fully neuromorphic star-tracking pipeline to mitigate spacecraft jitter with low-latency asynchronous processing.",
            model_type="Neuromorphic Method (SNN-style pipeline)",
        ),
        PaperItem(
            bucket="A-Strict Match",
            title="Quantifying Accuracy of an Event-Based Star Tracker via Earth's Rotation",
            year="2025",
            venue="ICCVW 2025",
            link="https://doi.org/10.1109/ICCVW69036.2025.00487",
            summary="Uses Earth's rotation as a precise physical reference to quantify event-based star tracker accuracy in real observations.",
            model_type="Physics-grounded Evaluation + Tracking Pipeline",
        ),
        PaperItem(
            bucket="A-Strict Match",
            title="Dual-modality event-frame fusion for blind star image motion deblurring via sparse residual learning",
            year="2025",
            venue="Optics and Lasers in Engineering",
            link="https://doi.org/10.1016/j.optlaseng.2025.109368",
            summary="Fuses event streams and frame images for star-image motion deblurring to improve downstream detection and localization quality.",
            model_type="CNN family (Sparse Residual Fusion Network)",
        ),
        PaperItem(
            bucket="A-Strict Match",
            title="Neuromorphic Cameras in Astronomy: Unveiling the Future of Celestial Imaging Beyond Conventional Limits",
            year="2025",
            venue="arXiv",
            link="https://arxiv.org/abs/2503.15883",
            summary="A perspective/review discussing neuromorphic imaging advantages for astronomy and demonstrating telescope-based observations.",
            model_type="Review / Perspective (Neuromorphic sensing direction)",
        ),
        PaperItem(
            bucket="B-Strongly Related Extension",
            title="Backlight and dim space object detection based on a novel event camera",
            year="2024",
            venue="PeerJ Computer Science",
            link="https://doi.org/10.7717/peerj-cs.2192",
            summary="Addresses backlit and low-illumination space-object detection with an asynchronous convolutional memory network (ACMNet).",
            model_type="CNN family (ACMNet)",
        ),
        PaperItem(
            bucket="B-Strongly Related Extension",
            title="End-to-end space object detection method based on event camera",
            year="2023",
            venue="SPIE PIOE 2023",
            link="https://doi.org/10.1117/12.3011053",
            summary="Encodes asynchronous event streams into event spike tensors (EST) and performs end-to-end space-object detection.",
            model_type="Deep Network (EST representation + feed-forward detection head)",
        ),
        PaperItem(
            bucket="B-Strongly Related Extension",
            title="Towards Bridging the Space Domain Gap for Satellite Pose Estimation using Event Sensing",
            year="2023",
            venue="ICRA 2023",
            link="https://doi.org/10.1109/ICRA48891.2023.10160531",
            summary="Uses event sensing to reduce simulation-to-space domain gap and improve satellite pose estimation generalization.",
            model_type="Deep Learning + Domain Adaptation (Not Transformer-centric)",
        ),
        PaperItem(
            bucket="B-Strongly Related Extension",
            title="Leveraging Event-Based Cameras for Enhanced Space Situational Awareness: A Nanosatellite Mission Architecture Study",
            year="2024",
            venue="22nd IAA Symposium on Space Debris",
            link="https://doi.org/10.52202/078360-0131",
            summary="Analyzes mission-level architecture and engineering value of event cameras for space situational awareness.",
            model_type="Mission Architecture Study (No specific model)",
        ),
    ]


def build_group_table(styles):
    header = [
        Paragraph("Group", styles["EnSmall"]),
        Paragraph("Representative Papers", styles["EnSmall"]),
        Paragraph("Main Technical Characteristics", styles["EnSmall"]),
        Paragraph("Research Gaps", styles["EnSmall"]),
    ]
    rows = [
        [
            Paragraph("Filtering Methods", styles["EnSmall"]),
            Paragraph(
                "Asynchronous KF (2022/2023); EBS-EKF (2025); Earth-Rotation Accuracy (2025)",
                styles["EnSmall"],
            ),
            Paragraph(
                "Relies on state-space estimation and physical priors, with strong real-time capability and interpretability.",
                styles["EnSmall"],
            ),
            Paragraph(
                "Still lacks unified error models across star magnitude ranges and sensors; robustness under extreme jitter and faint-star scenes needs broader validation.",
                styles["EnSmall"],
            ),
        ],
        [
            Paragraph("CNN", styles["EnSmall"]),
            Paragraph(
                "Dual-modality Deblurring (2025); ACMNet Space Object Detection (2024); End-to-end EST Detection (2023)",
                styles["EnSmall"],
            ),
            Paragraph(
                "Strong at event-frame fusion and spatiotemporal feature extraction in noisy, low-texture conditions.",
                styles["EnSmall"],
            ),
            Paragraph(
                "Public star-level annotations are limited; cross-orbit and cross-optics generalization remains weak; unified compute-accuracy benchmarks are missing.",
                styles["EnSmall"],
            ),
        ],
        [
            Paragraph("Neuromorphic", styles["EnSmall"]),
            Paragraph(
                "Fully Neuromorphic Star Tracking (2025); Neuromorphic Cameras in Astronomy (2025)",
                styles["EnSmall"],
            ),
            Paragraph(
                "Highlights asynchronous spike-based processing and low-power potential for onboard real-time deployment.",
                styles["EnSmall"],
            ),
            Paragraph(
                "Reproducible baselines and open tooling are still limited; fair comparisons against KF/CNN pipelines and closed-loop mission tests are insufficient.",
                styles["EnSmall"],
            ),
        ],
        [
            Paragraph("Dataset", styles["EnSmall"]),
            Paragraph("e-STURT Dataset (2025/2026)", styles["EnSmall"]),
            Paragraph(
                "Provides the first systematic event-star observations under controlled jitter for training and benchmarking.",
                styles["EnSmall"],
            ),
            Paragraph(
                "Real in-orbit data is scarce, annotation standards are not unified, and paired multimodal benchmarks with conventional star sensors are still lacking.",
                styles["EnSmall"],
            ),
        ],
    ]
    data = [header] + rows
    table = Table(data, colWidths=[20 * mm, 52 * mm, 50 * mm, 52 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
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
    styles = build_styles()
    items = build_items()

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Event Camera Star Tracking and Star Detection Literature Review (Last 5 Years)",
        author="Codex",
    )

    now_text = datetime.now().strftime("%Y-%m-%d %H:%M")
    story = [
        Paragraph("Event Camera Star Tracking and Star Detection Literature Review (Last 5 Years)", styles["EnTitle"]),
        Paragraph(f"Search window: 2021-03-04 to 2026-03-04; Generated at: {now_text}", styles["EnBody"]),
        Paragraph(
            "Note: A = strict match (event camera + star tracking/detection); B = strongly related extension.",
            styles["EnBody"],
        ),
        Spacer(1, 4),
    ]

    story.append(Paragraph("A/B Paper List (Total: 13)", styles["EnHeading"]))
    for idx, item in enumerate(items, start=1):
        story.append(
            Paragraph(
                f"{idx}. [{item.bucket}] <b>{item.title}</b> ({item.year})",
                styles["EnBody"],
            )
        )
        story.append(Paragraph(f"Venue: {item.venue}", styles["EnSmall"]))
        story.append(Paragraph(f"Link: {item.link}", styles["EnSmall"]))
        story.append(Paragraph(f"Summary: {item.summary}", styles["EnSmall"]))
        story.append(Paragraph(f"Model Type: {item.model_type}", styles["EnSmall"]))
        story.append(Spacer(1, 3))

    story.append(PageBreak())
    story.append(Paragraph("Grouped Summary and Research Gaps", styles["EnHeading"]))
    story.append(
        Paragraph(
            'Grouped by "Filtering Methods / CNN / Neuromorphic / Dataset", with technical focus and open gaps.',
            styles["EnBody"],
        )
    )
    story.append(build_group_table(styles))

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)


def main() -> None:
    out = Path("/home2/mengyu/evlit-agent/output/pdf/event_camera_star_tracking_detection_review_english_2021_2026.pdf")
    out.parent.mkdir(parents=True, exist_ok=True)
    build_pdf(out)
    print(out)


if __name__ == "__main__":
    main()

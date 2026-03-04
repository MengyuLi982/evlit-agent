# Event Camera Object Detection/Tracking Literature Summary (2021-present, v3)

- Generated at: 2026-03-04T15:21:39.671615+00:00
- Candidate raw: 345
- Candidate dedup(title): 185
- Content-filtered: 30
- Selected: 20

## Content-Based Selection Criteria

- year >= 2021
- content-level relevance (abstract/fulltext), not title-only
- must include explicit object detection/tracking semantics + evaluation evidence
- exclude non-target tasks (SLAM, pose estimation, super-resolution, optical flow, eye/star tracking, astronomy, device reviews)

Ranking factors:
- citation impact (OpenAlex + metadata)
- dataset/benchmark evidence in content
- method clarity in content
- multi-query & multi-source support
- venue quality + classic age
- fulltext verification bonus

## Top 20

### 1. [2023] Recurrent Vision Transformers for Object Detection with Event Cameras
- paper_id: `openalex:W4386075690`
- citation_count: 144
- task_type: detection
- content_level: abstract_only
- final_score: 0.80567
- selection_reason: 内容含数据集/benchmark证据；内容含方法范式与实现线索；内容含评估指标/实验结果语句；引用量高，经典性强；摘要级验证
- main_content_excerpt: We present Recurrent Vision Transformers (RVTs), a novel backbone for object detection with event cameras. Event cameras provide visual information with submillisecond latency at a high-dynamic range and with strong robustness against motion blur. These unique properties offer great potential for low-latency object detection and tracking in time-critical scenarios. Prior work in event-based vision has achieved outsta

### 2. [2021] Object Tracking by Jointly Exploiting Frame and Event Domain
- paper_id: `openalex:W3202534481`
- citation_count: 109
- task_type: tracking
- content_level: abstract_only
- final_score: 0.78702
- selection_reason: 内容含方法范式与实现线索；内容含评估指标/实验结果语句；引用量高，经典性强；摘要级验证
- main_content_excerpt: Inspired by the complementarity between conventional frame-based and bio-inspired event-based cameras, we propose a multi-modal based approach to fuse visual cues from the frame- and event-domain to enhance the single object tracking performance, especially in degraded conditions (e.g., scenes with high dynamic range, low light, and fast-motion objects). The proposed approach can effectively and adaptively combine me

### 3. [2022] Spike-Based Motion Estimation for Object Tracking Through Bio-Inspired Unsupervised Learning
- paper_id: `openalex:W4313482706`
- citation_count: 41
- task_type: detection
- content_level: abstract_only
- final_score: 0.66116
- selection_reason: 内容含方法范式与实现线索；内容含评估指标/实验结果语句；引用量较高，常用度高；摘要级验证
- main_content_excerpt: Neuromorphic vision sensors, whose pixels output events/spikes asynchronously with a high temporal resolution according to the scene radiance change, are naturally appropriate for capturing high-speed motion in the scenes. However, how to utilize the events/spikes to smoothly track high-speed moving objects is still a challenging problem. Existing approaches either employ time-consuming iterative optimization, or req

### 4. [2021] FAST-Dynamic-Vision: Detection and Tracking Dynamic Objects with Event and Depth Sensing
- paper_id: `openalex:W3134027214`
- citation_count: 37
- task_type: detection
- content_level: abstract_only
- final_score: 0.65751
- selection_reason: 内容含评估指标/实验结果语句；引用量较高，常用度高；摘要级验证
- main_content_excerpt: The development of aerial autonomy has enabled aerial robots to fly agilely in complex environments. However, dodging fast-moving objects in flight remains a challenge, limiting the further application of unmanned aerial vehicles (UAVs). The bottleneck of solving this problem is the accurate perception of rapid dynamic objects. Recently, event cameras have shown great potential in solving this problem. This paper pre

### 5. [2023] SODFormer: Streaming Object Detection With Transformer Using Events and Frames
- paper_id: `openalex:W4385285879`
- citation_count: 36
- task_type: detection
- content_level: abstract_only
- final_score: 0.63894
- selection_reason: 内容含方法范式与实现线索；内容含评估指标/实验结果语句；引用量较高，常用度高；摘要级验证
- main_content_excerpt: DAVIS camera, streaming two complementary sensing modalities of asynchronous events and frames, has gradually been used to address major object detection challenges (e.g., fast motion blur and low-light). However, how to effectively leverage rich temporal cues and fuse two heterogeneous visual streams remains a challenging endeavor. To address this challenge, we propose a novel streaming object detector with Transfor

### 6. [2023] A 73.53TOPS/W 14.74TOPS Heterogeneous RRAM In-Memory and SRAM Near-Memory SoC for Hybrid Frame and Event-Based Target Tracking
- paper_id: `openalex:W4360606223`
- citation_count: 45
- task_type: detection
- content_level: abstract_only
- final_score: 0.61093
- selection_reason: 内容含方法范式与实现线索；内容含评估指标/实验结果语句；引用量较高，常用度高；摘要级验证
- main_content_excerpt: Vision-based high-speed target-identification and tracking is a critical application in unmanned aerial vehicles (UAV) with wide military and commercial usage. Traditional frame cameras processed through convolutional neural networks (CNN) exhibit high target-identification accuracy but with low throughput (hence low tracking speed) and high power. On the other hand, event cameras or dynamic vision sensors (DVS) gene

### 7. [2022] Moving Object Detection and Tracking by Event Frame from Neuromorphic Vision Sensors
- paper_id: `crossref:10.3390/biomimetics7010031`
- citation_count: 26
- task_type: both
- content_level: abstract_only
- final_score: 0.60621
- selection_reason: 内容含评估指标/实验结果语句；多源交叉命中；摘要级验证
- main_content_excerpt: <jats:p>Fast movement of objects and illumination changes may lead to a negative effect on camera images for object detection and tracking. Event cameras are neuromorphic vision sensors that capture the vitality of a scene, mitigating data redundancy and latency. This paper proposes a new solution to moving object detection and tracking using an event frame from bio-inspired event cameras. First, an object detection 

### 8. [2023] Spike-Event Object Detection for Neuromorphic Vision
- paper_id: `openalex:W4316022139`
- citation_count: 12
- task_type: both
- content_level: abstract_only
- final_score: 0.59172
- selection_reason: 内容含方法范式与实现线索；内容含评估指标/实验结果语句；多源交叉命中；摘要级验证
- main_content_excerpt: Neuromorphic vision is one of the novel research fields that study neuromorphic cameras and spiking neural networks (SNNs) for computer vision. Instead of computing on frame-based images, spike events are streamed from neuromorphic cameras, and novel object detection algorithms have to deal with spike events to achieve detection tasks. In this paper, we propose a solution to the novel object detection method with spi

### 9. [2024] SpikingViT: A Multiscale Spiking Vision Transformer Model for Event-Based Object Detection
- paper_id: `openalex:W4400315083`
- citation_count: 17
- task_type: detection
- content_level: abstract_only
- final_score: 0.58344
- selection_reason: 内容含方法范式与实现线索；内容含评估指标/实验结果语句；摘要级验证
- main_content_excerpt: Event cameras have unique advantages in object detection, capturing asynchronous events without continuous frames. They excel in dynamic range, low latency, and high-speed motion scenarios, with lower power consumption. However, aggregating event data into image frames leads to information loss and reduced detection performance. Applying traditional neural networks to event camera outputs is challenging due to event 

### 10. [2024] Scene Adaptive Sparse Transformer for Event-based Object Detection
- paper_id: `openalex:W4402727829`
- citation_count: 22
- task_type: detection
- content_level: abstract_only
- final_score: 0.57808
- selection_reason: 内容含方法范式与实现线索；内容含评估指标/实验结果语句；摘要级验证
- main_content_excerpt: While recent Transformer-based approaches have shown impressive performances on event-based object detection tasks, their high computational costs still diminish the low power consumption advantage of event cameras. Image-based works attempt to reduce these costs by introducing sparse Transformers. However, they display inade-quate sparsity and adaptability when applied to event-based object detection, since these ap

### 11. [2022] Pushing the Limits of Asynchronous Graph-based Object Detection with Event Cameras
- paper_id: `openalex:W4309875759`
- citation_count: 22
- task_type: detection
- content_level: abstract_only
- final_score: 0.56408
- selection_reason: 内容含评估指标/实验结果语句；摘要级验证
- main_content_excerpt: State-of-the-art machine-learning methods for event cameras treat events as dense representations and process them with conventional deep neural networks. Thus, they fail to maintain the sparsity and asynchronous nature of event data, thereby imposing significant computation and latency constraints on downstream systems. A recent line of work tackles this issue by modeling events as spatiotemporally evolving graphs t

### 12. [2024] Spatiotemporal Aggregation Transformer for Object Detection With Neuromorphic Vision Sensors
- paper_id: `openalex:W4396505821`
- citation_count: 7
- task_type: detection
- content_level: abstract_only
- final_score: 0.52923
- selection_reason: 内容含数据集/benchmark证据；内容含方法范式与实现线索；内容含评估指标/实验结果语句；摘要级验证
- main_content_excerpt: To enhance the accuracy of object detection with event-based neuromorphic vision sensors, a novel event-based detector named Spatio-Temporal Aggregation Transformer (STAT) is proposed. Firstly, in order to collect sufficient event information to estimate the problem considered, STAT uses a density-based adaptive sampling (DAS) module to sample continuous event stream into multiple groups adaptively. This module can d

### 13. [2024] LEOD: Label-Efficient Object Detection for Event Cameras
- paper_id: `openalex:W4402753639`
- citation_count: 9
- task_type: detection
- content_level: abstract_only
- final_score: 0.51875
- selection_reason: 内容含数据集/benchmark证据；内容含评估指标/实验结果语句；摘要级验证
- main_content_excerpt: Object detection with event cameras benefits from the sensor's low latency and high dynamic range. However, it is costly to fully label event streams for supervised training due to their high temporal resolution. To reduce this cost, we present LEOD, the first method for label-efficient event-based detection. Our approach unifies weakly- and semi-supervised object detection with a self-training mech-anism. We first u

### 14. [2023] A Reconfigurable Architecture for Real-time Event-based Multi-Object Tracking
- paper_id: `openalex:W4366774363`
- citation_count: 10
- task_type: tracking
- content_level: abstract_only
- final_score: 0.50994
- selection_reason: 内容含方法范式与实现线索；内容含评估指标/实验结果语句；摘要级验证
- main_content_excerpt: Although advances in event-based machine vision algorithms have demonstrated unparalleled capabilities in performing some of the most demanding tasks, their implementations under stringent real-time and power constraints in edge systems remain a major challenge. In this work, a reconfigurable hardware-software architecture called REMOT, which performs real-time event-based multi-object tracking on FPGAs, is presented

### 15. [2024] SpikeMOT: Event-based Multi-Object Tracking with Sparse Motion Features
- paper_id: `arxiv:2309.16987v1`
- citation_count: 4
- task_type: both
- content_level: abstract_only
- final_score: 0.50556
- selection_reason: 内容含数据集/benchmark证据；内容含方法范式与实现线索；内容含评估指标/实验结果语句；多源交叉命中；摘要级验证
- main_content_excerpt: In comparison to conventional RGB cameras, the superior temporal resolution of event cameras allows them to capture rich information between frames, making them prime candidates for object tracking. Yet in practice, despite their theoretical advantages, the body of work on event-based multi-object tracking (MOT) remains in its infancy, especially in real-world settings where events from complex background and camera 

### 16. [2025] Object Detection using Event Camera: A MoE Heat Conduction based Detector and A New Benchmark Dataset
- paper_id: `openalex:W4413156100`
- citation_count: 4
- task_type: detection
- content_level: abstract_only
- final_score: 0.4609
- selection_reason: 内容含数据集/benchmark证据；内容含方法范式与实现线索；内容含评估指标/实验结果语句；摘要级验证
- main_content_excerpt: Object detection in event streams has emerged as a cutting-edge research area, demonstrating superior performance in low-light conditions, scenarios with motion blur, and rapid movements. Current detectors leverage spiking neural networks, Transformers, or convolutional neural networks as their core architectures, each with its own set of limitations including restricted performance, high computational overhead, or l

### 17. [2024] Direct 3D model-based object tracking with event camera by motion interpolation
- paper_id: `openalex:W4393172807`
- citation_count: 6
- task_type: tracking
- content_level: abstract_only
- final_score: 0.45101
- selection_reason: 内容含评估指标/实验结果语句；多源交叉命中；摘要级验证
- main_content_excerpt: Event cameras are recent sensors that measure intensity changes in each pixel asynchronously. It is being used due to lower latency and higher temporal resolution compared to traditional frame-based camera. We propose a method of 3D model-based object tracking directly from events captured by event camera. To enable reliable and accurate tracking of objects, we use a new event representation and predict brightness in

### 18. [2021] A Multi-target Tracking Algorithm for Fast-moving Workpieces Based on Event Camera
- paper_id: `openalex:W3214545583`
- citation_count: 3
- task_type: both
- content_level: abstract_only
- final_score: 0.42737
- selection_reason: 内容含方法范式与实现线索；内容含评估指标/实验结果语句；摘要级验证
- main_content_excerpt: Multi-target tracking application for fast-moving workpieces has drawn increasing attention in the industrial field. For the dense, fast moving workpieces with few texture features, traditional cameras get poor quality images with dynamic blur and object adhesion, which makes the detection and tracking of workpieces unreliable. However, the event camera outputs events asynchronously at a microsecond speed when the pi

### 19. [2025] CRSOT: Cross-Resolution Object Tracking Using Unaligned Frame and Event Cameras
- paper_id: `openalex:W4413010666`
- citation_count: 6
- task_type: tracking
- content_level: abstract_only
- final_score: 0.41935
- selection_reason: 内容含评估指标/实验结果语句；摘要级验证
- main_content_excerpt: Existing datasets for RGB-DVS tracking are collected with DVS346 camera and their resolution (<inline-formula xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink"><tex-math notation="LaTeX">$346 \times 260$</tex-math></inline-formula>) is low for practical applications. Actually, only visible cameras are deployed in many practical systems, and the newly designed neuromorphic camer

### 20. [2021] 3D Object Tracking with Neuromorphic Event Cameras via Image Reconstruction
- paper_id: `openalex:W4200312002`
- citation_count: 7
- task_type: tracking
- content_level: abstract_only
- final_score: 0.41623
- selection_reason: 内容含评估指标/实验结果语句；摘要级验证
- main_content_excerpt: One of the first and most remarkable successes in neuromorphic (brain-inspired) engineering was the development of bio-inspired event cameras, which communicate transients in luminance as events. Here we evaluate the combination of the Channel and Spatial Reliability Tracking (CSRT) algorithm and the LapDepth neural network for the implementation of 3D object tracking with event cameras. We show that following image 

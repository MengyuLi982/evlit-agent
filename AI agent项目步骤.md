# AI agent项目步骤

**User:** Anonymous (raymond.tanner05@gmail.com)  
**Created:** 3/3/2026 14:59:15  
**Updated:** 3/3/2026 16:04:27  
**Exported:** 3/3/2026 16:07:34  
**Link:** [https://chatgpt.com/c/69a6e932-5dbc-8331-ae24-add997b5ebac](https://chatgpt.com/c/69a6e932-5dbc-8331-ae24-add997b5ebac)  

## Prompt:
我现在要申请这个岗位： https://portal.mytum.de/jobs/wissenschaftler/NewsArticle_20260301_120103
因此我要开始着手做相关的准备，关于evetcamera的部分以及硬件部分以及ai imaging的部分我都已经有相关的很成熟的经验了，我唯一缺乏的就是ai agents的经验，为此我要从现在开始准备着手做一个开源的ai agent的项目用来证明我具备这项能力用于ai agents的在实战中的开发
我的想法是做一个“eventcamera和ai imaging这个领域用RAG来给我做文献retrievals的ai agents,其中api我考虑使用qwen的或者更适合这个的LLM的api）因为这个能够很好的证明我的能力
请给我这个制作过程中所遇必备的步骤以及我需要考虑到的细节（尤其是一些参考原和可以直接fork过来使用的代表性的已经开源的code我可以直接用来参考的）并且告诉我：如果我已经有了host machine以及api,我接下来应该执行的详细步骤是怎样的，并且我还要保留一些我自己的原创新的思考（或者是加速搜索或者是retrieving的全面性）能够证明我在将来工作中能够用到的agentic ai的能力

## Response:
下面给你一个**能直接对齐这个岗位要求**、并且能在 GitHub 上形成“看得见的 agentic AI 能力证据”的开源项目方案：做一个面向 **Event Camera / Event-based Vision / AI Imaging** 的 **文献检索 + 证据归纳 + 可追溯引用** 的多智能体（multi-agent）RAG 系统，并且在检索策略上加入一个**可量化优化回路**（最轻量也可以做成 contextual bandit / RL 风格），从而覆盖岗位里明确写到的 **multi-agent systems、AI agents 的生产环境、性能与可信度评估** 等要求。[TUM](https://portal.mytum.de/jobs/wissenschaftler/NewsArticle_20260301_120103)

* * *

1) 先对齐岗位：你的开源项目要证明哪些“AI agents 能力”
----------------------------------

岗位里和 “AI agents” 直接相关的点非常清楚：

*   **独立研究 multi-agent systems 与 reinforcement learning**（建立个人研究画像）[TUM](https://portal.mytum.de/jobs/wissenschaftler/NewsArticle_20260301_120103)
*   **搭建 production environment**，用于 AI agents 的 fine-tuning / testing / validation[TUM](https://portal.mytum.de/jobs/wissenschaftler/NewsArticle_20260301_120103)
*   **设计、验证、评估 agents 的能力与可信度**（trustworthiness）[TUM](https://portal.mytum.de/jobs/wissenschaftler/NewsArticle_20260301_120103)

所以你的项目不应只是“一个 RAG demo”，而应该体现：

### 你需要在仓库里“可见”的证据

1.  **Agent orchestration（编排）**：明确的工作流图/状态机（不是一个脚本顺序执行）
    *   推荐用图结构框架（例如 LangGraph 的 workflow/agent 模式），展示可调试、可持久化、多步骤的 agent 流程。[LangChain Docs+1](https://docs.langchain.com/oss/python/langgraph/workflows-agents)
2.  **Multi-agent 分工**：至少 3 个角色（Planner / Retriever / Critic 或 CitationChecker）
3.  **工具调用（tool-use）**：对外部文献 API（arXiv / Semantic Scholar / OpenAlex / Crossref）做结构化调用，而不是只“让 LLM 自己编”[www.crossref.org+3arXiv+3Semantic Scholar+3](https://info.arxiv.org/help/api/user-manual.html)
4.  **可复现实验与评估**：
    *   RAG 评估（例如 Ragas / TruLens / DeepEval 任意一个做主评估）[Ragas+2GitHub+2](https://docs.ragas.io/en/latest/howtos/applications/evaluate-and-improve-rag/)
    *   记录每次 agent run 的输入/检索结果/引用证据/最终输出（可用 OpenTelemetry 做 tracing）[OpenTelemetry](https://opentelemetry.io/docs/languages/python/)
5.  **最少一个“优化回路”**：证明你不只是调用 API，而是在做 agent 系统工程
    *   例如：检索策略选择用 contextual bandit（属于 RL 家族的工程化形态），根据评估 reward 自动调整策略（见后文“原创点”）。

* * *

2) 项目定位建议：做成 “EventVision Literature Agent” 更贴合岗位
-------------------------------------------------

岗位就是 EventVision（event camera）+ space observation（star tracking / satellite detection 等）方向。你做一个“泛化学术搜索”会显得不够贴合；建议你把项目的**第一个 domain**直接锚到：

*   Event-based vision 总体（event camera / neuromorphic vision / DVS / DAVIS）
*   **space 相关子域**（star tracking / satellite detection / spacecraft jitter 等）

这样你能在 README 里直接用岗位同款用例做 demo，例如：

*   “基于 event camera 的 star tracking 有哪些数据集、方法、误差来源、基线？”  
    这里可以直接把公开论文作为示例语料：比如 CVPR Workshop 的 _Star Tracking Using an Event Camera_（文中提到也发布了数据集）。[CVF Open Access](https://openaccess.thecvf.com/content_CVPRW_2019/papers/EventVision/Chin_Star_Tracking_Using_an_Event_Camera_CVPRW_2019_paper.pdf)  
    以及 e-STURT（event-based star tracking under jitter）数据集论文。[arXiv](https://arxiv.org/abs/2505.12588)

同时，你还可以用社区整理的资源库作为“冷启动语料种子”：

*   uzh-rpg 的 event-based vision resources（论文、数据集、代码、space applications 也有分类）[GitHub+1](https://github.com/uzh-rpg/event-based_vision_resources)
*   Awesome-Event-Imaging 这类 curated list 也可作为种子源[GitHub](https://github.com/yunfanLu/Awesome-Event-Imaging)

* * *

3) 推荐的总体架构（你可以把它画成 repo 里的图）
----------------------------

### 3.1 数据流（Data plane）

1.  **Seed**：从 curated list / 关键词检索得到候选论文集合
2.  **Metadata enrichment**：补全 DOI、venue、引用/被引、open access 链接等
3.  **PDF 获取**：优先 arXiv / CVF OpenAccess 等；付费墙只存 metadata（合规）
4.  **解析与切分**：PDF → 结构化文本 chunks（含 section / figure caption / references）
5.  **索引**：向量索引 + 关键词索引（hybrid） + 引文图（可选）
6.  **RAG**：检索 → rerank → 证据抽取 → 生成回答（带引用）

### 3.2 控制流（Agent plane：multi-agent）

建议最少 4 个 agent（可更多）：

*   **PlannerAgent**：把用户问题拆成子问题（datasets / methods / evaluation / limitations / implementation pointers）
*   **RetrieverAgent**：对每个子问题做 multi-source 检索（OpenAlex/S2/arXiv/Crossref + 本地索引）
*   **EvidenceAgent**：从检索到的段落里抽取“可引用证据”（句子级别/段落级别）并做结构化对齐（claim ↔ evidence）
*   **Critic/CitationCheckerAgent**：检查引用是否支持结论、是否存在冲突、是否需要补检索

用图结构框架（LangGraph）能把这些节点连成可调试的执行图，并支持持久化、streaming、debug。[LangChain Docs+1](https://docs.langchain.com/oss/python/langgraph/workflows-agents)

* * *

4) 你可以直接 fork/参考的代表性开源代码（按用途分组）
-------------------------------

### 4.1 “科学文献 RAG” 基座（最推荐）

**PaperQA2（Future-House/paper-qa）**

*   就是为科学论文做 grounded answers + citations 的；并强调 agentic RAG、元数据增强、多来源冗余抓取等。[GitHub+1](https://github.com/future-house/paper-qa)
*   默认支持 LiteLLM（意味着你可无痛切换到 Qwen/DashScope 等 provider）。[GitHub+1](https://github.com/future-house/paper-qa)

> 使用策略：
> 
> *   不一定要“fork 直接改核心库”。更工程化的做法是：**你的项目 repo 作为上层 agent 编排与检索策略层**，PaperQA 作为依赖库/可选 engine。这样你的原创贡献更清晰。
>     

### 4.2 “Research agent / 报告生成”参考

*   **GPT-Researcher（assafelovic/gpt-researcher）**：主打 deep research、并行化、报告带引用，可做你多 agent 并行检索/整合的参考。[GitHub+1](https://github.com/assafelovic/gpt-researcher)
*   **STORM（stanford-oval/storm）**：知识策展 + 长文报告生成 + citations；非常适合你参考其“多视角问题驱动检索”的策略。[GitHub+2GitHub+2](https://github.com/stanford-oval/storm)

### 4.3 Agent 编排框架（你需要一个“可展示”的 orchestrator）

*   **LangGraph**：把 agents 做成 graph/workflow，有 persistence/debug/deployment 叙事，非常适合写在简历里。[LangChain Docs+1](https://docs.langchain.com/oss/python/langgraph/workflows-agents)
*   可选：**AutoGen**（多 agent 框架）[GitHub+1](https://github.com/microsoft/autogen) 或 **CrewAI**（角色扮演式多 agent）[GitHub+1](https://github.com/crewAIInc/crewAI)
    *   但从“科研岗位 + 可控性”角度，LangGraph 的显式图结构更容易解释。

### 4.4 文献数据源 API（必须工具化）

*   **arXiv API**：官方用户手册（注意 terms of use）。[arXiv+1](https://info.arxiv.org/help/api/user-manual.html)
*   **Semantic Scholar Academic Graph API**：提供 paper search / references / citations 等接口。[Semantic Scholar+1](https://www.semanticscholar.org/product/api/tutorial)
*   **OpenAlex API**：开放学术图谱；works 有 referenced\_works / cited\_by 等字段，适合做引文图扩展检索。[OpenAlex+2OpenAlex+2](https://docs.openalex.org/)
*   **Crossref REST API**：用于 DOI / metadata；注意官方 “Etiquette / rate limit” 约束。[www.crossref.org+2GitHub+2](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)

### 4.5 PDF 解析（这是学术 RAG 的“地基”）

*   **GROBID**：专注学术 PDF 的结构化抽取（header、references、fulltext 结构等），Apache-2.0 许可。[GitHub](https://github.com/grobidOrg/grobid)
*   **Unstructured**：通用文档预处理组件，适合做 fallback。[GitHub](https://github.com/Unstructured-IO/unstructured)
*   注意：**PyMuPDF 是 AGPL**，如果你希望你的项目用 MIT/Apache 发布，需要特别小心依赖链的 license 兼容性。[GitHub](https://github.com/pymupdf/PyMuPDF)

### 4.6 向量库与检索底座

*   **Qdrant**（Rust 写的开源向量数据库，带 payload filter，很适合学术检索的 metadata filtering）。[GitHub+1](https://github.com/qdrant/qdrant)
*   可选：Milvus[GitHub](https://github.com/milvus-io/milvus)、Faiss（本地 ANN）[GitHub+1](https://github.com/facebookresearch/faiss)

### 4.7 评估与可信度（岗位明确要求“trustworthiness”）

*   **Ragas**：RAG 评估框架（context relevance/groundedness 等方向常用）。[Ragas+1](https://docs.ragas.io/en/latest/howtos/applications/evaluate-and-improve-rag/)
*   **TruLens**：对 RAG/agents 做 tracing + eval（强调“从 vibe 到 metrics”）。[GitHub+1](https://github.com/truera/trulens)
*   **DeepEval**：LLM 系统评估框架（可接 pytest/CI）。[GitHub+1](https://github.com/confident-ai/deepeval)
*   **Guardrails**：输入输出 schema/validator（你可用来约束“必须带引用/必须返回证据表”）。[GitHub+1](https://github.com/guardrails-ai/guardrails)
*   **OpenTelemetry（Python）**：工程化可观测性（traces/logs/metrics）。[OpenTelemetry+1](https://opentelemetry.io/docs/languages/python/)

* * *

5) 如果你已经有 host machine + LLM API：下一步的“详细执行步骤”
---------------------------------------------

下面我按**从零到可跑 MVP** → **做成可展示的 agent 系统** → **加入原创优化回路** 的顺序给你写成 checklist（你可以直接照做）。

### Step 0：确定你项目的最小可交付（MVP）接口

建议你至少提供两种入口：

*   **CLI**：`evagent ask "..."`、`evagent search "..."`、`evagent ingest ...`
*   **Web UI（可选）**：Streamlit/Gradio 用于展示（面试时很加分，但不是必须）

输出必须包含：

*   答案（自然语言）
*   关键论文列表（title/authors/year/venue/arxiv/doi）
*   每个结论的**证据引用**（至少到 paper + section/chunk）

### Step 1：项目初始化与工程骨架

1.  建一个新 repo（建议 Apache-2.0 或 MIT；和大多数依赖兼容）
2.  目录结构建议：

```
eventvision-literature-agent/
  README.md
  LICENSE
  pyproject.toml
  .env.example
  docker-compose.yml
  src/
    evagent/
      app.py               # CLI 入口
      config.py
      llm/                 # LLM & embedding wrapper (LiteLLM)
      sources/             # arXiv / OpenAlex / S2 / Crossref connectors
      ingest/              # pdf download + parse + chunk
      index/               # vector db + keyword index + metadata store
      agents/              # planner/retriever/critic graph
      eval/                # ragas/trulens/deepeval runners
      observability/       # opentelemetry tracing/logging
  notebooks/
  tests/
```

3.  `.env.example` 至少包含：
    *   `DASHSCOPE_API_KEY=...`
*   `DASHSCOPE_API_BASE=...`（如果用国际站/兼容模式）  
    LiteLLM 对 DashScope(Qwen) 的调用方式和环境变量约定可直接参考其文档。[LiteLLM+1](https://docs.litellm.ai/docs/providers/dashscope)

### Step 2：LLM 接入层（建议用 LiteLLM 做统一抽象）

原因：你未来可能想从 qwen 换到别的模型，但不想改一堆代码。PaperQA2 也默认支持 LiteLLM 模型，生态相对顺。[GitHub+1](https://github.com/future-house/paper-qa)

*   用 LiteLLM 调 DashScope/Qwen：文档里明确支持 `dashscope/` 前缀、`DASHSCOPE_API_KEY` 等。[LiteLLM](https://docs.litellm.ai/docs/providers/dashscope)
*   DashScope 官方 API 参考也可作为你实现的依据（参数、示例）。[Alibaba Cloud](https://www.alibabacloud.com/help/en/model-studio/qwen-api-via-dashscope)

你在代码里做两层 wrapper：

*   `chat(model, messages, tools=...)`
*   `embed(model, texts)`（embedding 也可以先用本地模型，后续再替换）

### Step 3：文献检索工具链（先做“metadata + PDF 链接”）

实现 4 个工具函数（agent 可以调用）：

1.  `search_arxiv(query, max_results, sort_by, time_filter)`
    *   arXiv 官方 API 文档说明了 query、分页和排序。[arXiv](https://info.arxiv.org/help/api/user-manual.html)
2.  `search_semanticscholar(query, limit)`
    *   S2 API 提到 keyword search endpoint；并且 Graph API 还有 references/citations 等。[Semantic Scholar+1](https://www.semanticscholar.org/product/api/tutorial)
3.  `search_openalex(query, filters)`
    *   OpenAlex works 实体提供 referenced\_works/cited\_by 等，后续可做引文图扩展。[OpenAlex+1](https://docs.openalex.org/api-entities/works)
    *   注意 OpenAlex API key 机制（免费 key + budget）。[OpenAlex](https://docs.openalex.org/how-to-use-the-api/api-overview)
4.  `lookup_crossref(doi_or_title)`
    *   Crossref REST API 提供检索与 metadata；注意 etiquette/rate limit。[www.crossref.org+2GitHub+2](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)

**实现细节要点（别跳过）**

*   **去重**：同一论文可能同时出现在 arXiv / OpenAlex / S2；用 DOI > arXiv\_id > title+first\_author+year 作为 dedup key
*   **合规**：只自动下载明确 open access 的 PDF；其余存 metadata（避免法律风险）
*   **缓存**：对外部 API 调用结果做本地缓存（SQLite/JSONL），否则迭代很慢、也容易打爆 rate limit

### Step 4：PDF 获取与解析（建议先用 GROBID，fallback 用 Unstructured）

**为什么学术 RAG 更推荐 GROBID**：它是为 scientific publications 做结构化抽取（header、references、citation contexts、fulltext segmentation 等），并且是 Apache-2.0。[GitHub](https://github.com/grobidOrg/grobid)

执行建议：

1.  用 `docker-compose` 拉起：
    *   `grobid` service（HTTP API）
    *   `qdrant` service（向量库）
2.  解析输出保留：
    *   section 标题层级
    *   figure/table caption
    *   references（后续做 citation-graph/多跳检索有用）

fallback：

*   Unstructured 做通用解析，作为“GROBID 解析失败/质量差”时的兜底。[GitHub](https://github.com/Unstructured-IO/unstructured)

⚠️ 依赖许可注意：

*   PyMuPDF 是 AGPL；如果你希望你的 repo 用 Apache/MIT，并且未来可能被单位/公司复用，尽量避免把 AGPL 变成硬依赖。[GitHub](https://github.com/pymupdf/PyMuPDF)

### Step 5：索引与检索（一定要做 Hybrid + Rerank）

最低配置建议：

*   **向量检索**：Qdrant（带 metadata filter）[GitHub+1](https://github.com/qdrant/qdrant)
*   **关键词检索**：BM25（可用 Elasticsearch/OpenSearch/Whoosh/tantivy 等；实现可从 PaperQA 的 full-text search 设计里借鉴）[GitHub](https://github.com/future-house/paper-qa)
*   **融合策略**：先 union topK（vector + BM25），再 rerank（cross-encoder 或 LLM rerank）

你要考虑的关键细节：

*   **chunk 粒度**：学术文献建议按 section/paragraph chunk，而不是固定长度盲切；引用定位更准确
*   **metadata-aware embedding**：把标题/年份/venue/关键词作为 embedding 输入的一部分（PaperQA2 也强调 metadata-awareness）。[GitHub](https://github.com/future-house/paper-qa)
*   **MMR / 多样性**：避免 topK 全是同一小方向的近重复论文，提升 coverage（这也是你后面“原创点”的一个抓手）

### Step 6：做成真正的“Agent 系统”（用 LangGraph 把多步流程显式化）

用 LangGraph 把流程做成图：

*   Node A: `plan_subquestions`
*   Node B: `retrieve_candidates`
*   Node C: `expand_citation_graph`（可选）
*   Node D: `extract_evidence`
*   Node E: `draft_answer`
*   Node F: `critic_and_fix`（若引用不足则回到 B/C）

LangGraph 的文档对 workflow vs agents、以及持久化/调试等优势有明确描述，你可以直接引用到 README 作为设计依据。[LangChain Docs+1](https://docs.langchain.com/oss/python/langgraph/workflows-agents)

### Step 7：加“可信度/可追溯性”机制（这部分很能打动面试官）

你要做到：**每个结论都能追溯到证据 chunk**。建议输出一个结构化 “Evidence Table”：

```
{
  "claim": "...",
  "evidence": [
    {
      "paper_id": "arxiv:1812.02895",
      "title": "...",
      "section": "Abstract/Method/Experiments",
      "snippet": "...",
      "confidence": 0.78
    }
  ],
  "notes": "..."
}
```

实现方式：

*   让 EvidenceAgent 只负责抽取 evidence，并把 snippet 原文带回来（长度控制）
*   CriticAgent 检查 claim 是否被 snippet 支持（否则强制补检索）

你也可以引入 Guardrails 来约束输出 schema（例如必须包含 citations/evidence）。[GitHub+1](https://github.com/guardrails-ai/guardrails)

### Step 8：评估与可观测（把它做成 CI 里的可重复实验）

至少做 2 类评估：

1.  **Retrieval 评估**（最重要）：Recall@K、MRR、nDCG（你自己实现即可）
2.  **RAG/Agent 评估**：用 Ragas 或 TruLens 跑 groundedness/context relevance 等指标（二选一也行）[Ragas+1](https://docs.ragas.io/en/latest/howtos/applications/evaluate-and-improve-rag/)

把每次 run 的：

*   检索结果
*   rerank 后列表
*   evidence table
*   final answer  
    全部保存到 `runs/` 目录（JSONL），并用 OpenTelemetry 打点（trace\_id 对齐一次完整 run）。[OpenTelemetry+1](https://opentelemetry.io/docs/languages/python/)

* * *

6) 你必须保留的“原创点”建议（可直接写成论文式贡献点）
-----------------------------

你提到希望“加速搜索 / 提升 retrieving 全面性”，下面给你 3 个既工程化、又能和岗位的 multi-agent/RL 对齐的原创方向——我建议你至少做其中 2 个，并在 README 里用 ablation 表展示收益。

### 原创点 A：引文图多跳检索（Coverage 明显提升）

做法：

*   初检索得到 seed papers（topN）
*   用 OpenAlex 的 `referenced_works` / `cited_by` 扩展 1 hop / 2 hop 候选集合[OpenAlex](https://docs.openalex.org/api-entities/works)
*   再做 rerank + 多样性约束（MMR）

价值：

*   学术检索常见问题是“只抓到最近/最热门”，多跳能补齐经典工作和相关分支
*   对 space/event vision 这种跨域方向，引用链扩展很有用

### 原创点 B：面向 event camera 领域的 Query Expansion（可解释、可控）

你可以做一个轻量的 domain lexicon（人工 + LLM 辅助）：

*   event camera / event-based vision / neuromorphic vision / DVS / DAVIS
*   star tracker / attitude estimation / centroiding / jitter compensation 等（对齐岗位子域）[TUM+1](https://portal.mytum.de/jobs/wissenschaftler/NewsArticle_20260301_120103)

用 PlannerAgent 先把 query 改写成 3–5 个检索子 query：

*   dataset 方向
*   method 方向
*   evaluation 方向
*   implementation/code 方向

然后 RetrieverAgent 并行跑，最后合并去重。  
这部分你可以参考 GPT-Researcher “拆分子问题 + 并行检索”叙事，但把数据源从普通网页改成学术图谱 API + 本地索引。[GitHub+1](https://github.com/assafelovic/gpt-researcher)

### 原创点 C：把“检索策略选择”做成 contextual bandit（RL 风格的优化回路）

这是你证明 “RL/agent systems” 的最便宜路线之一：

*   **动作（actions）**：选择检索策略组合
    *   例如：{BM25-only, Vector-only, Hybrid, Hybrid+CitationHop, Hybrid+QueryExpansion}
*   **状态（context）**：query 的特征（长度、是否包含 dataset/method 关键词、embedding）
*   **奖励（reward）**：你评估得到的指标（例如 Ragas context relevance / groundedness，或检索 Recall@K）[Ragas](https://docs.ragas.io/en/latest/howtos/applications/evaluate-and-improve-rag/)

实现：

*   初期用 Thompson Sampling / LinUCB 这种经典 contextual bandit 即可
*   每次用户 query 或 benchmark query 都产生一次 reward，在线更新策略
*   README 里展示：随着交互次数增加，平均 reward 上升（这是非常直观的“agentic + RL”证据）

* * *

7) 如何把项目写成“投简历/面试可用”的呈现材料
-------------------------

你的 repo 最终最好包含这些“面试官可快速消费”的内容：

1.  **README 第一屏**：
    *   1 张架构图（Data plane + Agent plane）
    *   3 条 demo 命令 + demo 输出截图（含 citations）
2.  **Benchmarks**：
    *   `benchmarks/eventvision_queries.jsonl`（50~100 条查询）
    *   `scripts/eval_retrieval.py`、`scripts/eval_rag.py`
    *   报告：baseline vs +QueryExpansion vs +CitationHop vs +BanditPolicy 的对比表
3.  **Reproducibility**：Docker compose 一键起服务（grobid/qdrant）、固定依赖锁文件、种子固定
4.  **Trustworthiness**：
    *   证据表（claim↔evidence）
    *   引用不足时自动补检索/拒答策略
5.  **对齐岗位的用例**：
    *   用 star tracking / jitter dataset（e-STURT）之类作为 showcase（和岗位描述高度一致）。[arXiv+1](https://arxiv.org/abs/2505.12588)

* * *

8) 你可以直接从哪条路线开始（避免走弯路）
----------------------

如果你的目标是“最快形成可展示成果 + 还能保留原创空间”，我建议顺序是：

1.  **先用 PaperQA2 跑通：本地 PDF → 带引用回答**（当作 baseline engine）[GitHub+1](https://github.com/future-house/paper-qa)
2.  外围加上 **LangGraph 多 agent 编排**（把 baseline 变成 agentic system）[LangChain Docs+1](https://docs.langchain.com/oss/python/langgraph/workflows-agents)
3.  再实现你的 **原创检索增强（A/B）**
4.  最后加 **contextual bandit 策略选择（C）** + 评估闭环（Ragas/TruLens/DeepEval 任一）[Ragas+2GitHub+2](https://docs.ragas.io/en/latest/howtos/applications/evaluate-and-improve-rag/)

* * *

如果你愿意，我也可以在你选定技术栈后，给你一份更“落到具体文件/函数”的实现拆解清单（例如每个模块需要哪些类、接口怎么定义、graph 节点的输入输出 schema 怎么写、benchmark 的数据格式怎么定），保证你按这个清单写出来就是一个完整的可运行仓库。



---
Powered by [ChatGPT Exporter](https://www.chatgptexporter.com)
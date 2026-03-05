# EventVision Literature Agent 工作流程深度分析

## 一、架构借鉴与套用情况

### 1.1 核心架构来源

根据 `references/borrowed_components.md` 的明确记录，本项目采用"先借鉴、后扩展"策略：

#### **PaperQA2** (future-house/paper-qa)
- **借鉴内容**：
  - 科学文献RAG的grounded citation模式
  - 多源检索与元数据感知的重排序思路
- **应用位置**：
  - `src/evagent/sources/` - 多源学术API连接器
  - `src/evagent/agents/nodes.py` - 证据优先提取模式（`extract_evidence`函数）
  - `src/evagent/models.py` - `PaperRecord`数据模型和去重策略

#### **GPT-Researcher** (assafelovic/gpt-researcher)
- **借鉴内容**：
  - Planner/Executor分离架构
  - 子问题分解与报告式组装
- **应用位置**：
  - `src/evagent/agents/nodes.py::plan_subquestions` - 查询分解逻辑
  - `src/evagent/app.py::ask` - 运行记录持久化到JSONL

#### **STORM** (stanford-oval/storm)
- **借鉴内容**：
  - 分阶段合成与引用
  - 视角驱动的问题扩展
- **应用位置**：
  - `src/evagent/agents/graph.py` - 五阶段图结构（plan → retrieve → evidence → critic → draft）
  - `src/evagent/analysis/paper_summary.py` - 结构化综合模板

#### **LangGraph** (langchain-ai/langgraph)
- **借鉴内容**：
  - 显式多智能体图编排框架
  - 状态管理与条件路由
- **应用位置**：
  - `src/evagent/agents/graph.py::build_graph` - 完整采用LangGraph的StateGraph API
  - `src/evagent/agents/state.py::AgentState` - TypedDict状态定义

#### **基础设施组件**
- **Qdrant** (qdrant/qdrant): 向量数据库（docker-compose.yml，预留集成点）
- **GROBID** (grobidOrg/grobid): PDF解析服务（`src/evagent/ingest/grobid.py`）

### 1.2 原创贡献部分

- **领域特定查询扩展**：`src/evagent/domain/profiles.py` 中的事件相机术语库
- **Profile驱动的检索策略**：`src/evagent/retrieval/ranking.py` 的加权评分机制
- **多源去重策略**：`DOI > arXiv_id > normalized(title+author+year)` 三级fallback

---

## 二、`evagent ask` 端到端调用流程

### 2.1 入口层（CLI）

**文件**: `src/evagent/app.py`

```
用户命令:
evagent ask "What datasets are used for event-camera star tracking?" \
  --profile sps_space_event_startracking \
  --year-from 2021 \
  --min-score 0.55 \
  --min-evidence 3 \
  --limit 6
```

**函数**: `app.py::ask(query, limit, profile, year_from, min_score, min_evidence)`

**执行步骤**:
1. 加载配置：`get_settings()` → 读取 `.env` 文件
2. 初始化日志：`configure_logging(settings.log_level)`
3. 创建检索器：`MultiSourceRetriever(settings)`
4. 创建LLM客户端：`LLMClient(settings)`
5. 构建图：`build_graph(retriever, llm)`
6. 准备初始状态：
   ```python
   state = {
       "query": query,
       "profile_name": profile_obj.name,
       "year_from": year_from,
       "min_score": min_score,
       "min_evidence": min_evidence,
       "per_source_limit": limit,
       "retry_count": 0,
   }
   ```
7. 执行图：`final_state = graph.invoke(state)`
8. 输出结果并持久化到 `runs/ask_runs.jsonl`

### 2.2 图编排层（LangGraph）

**文件**: `src/evagent/agents/graph.py`

**图结构**:
```
START → plan → retrieve → evidence → critic → [条件路由] → draft → END
                              ↑                    |
                              └────── retrieve ────┘
                                   (if needs_more)
```

**节点定义**:
- `plan`: `plan_subquestions`
- `retrieve`: `lambda s: retrieve_candidates(s, retriever)`
- `evidence`: `extract_evidence`
- `critic`: `critic_and_fix`
- `draft`: `lambda s: draft_answer(s, llm)`

**条件路由逻辑** (`route_after_critic`):
```python
if state.get("needs_more"):
    return "retrieve"  # 重新检索
return "draft"  # 生成答案
```

### 2.3 节点执行层（Agents）

**文件**: `src/evagent/agents/nodes.py`

#### **节点1: plan_subquestions**
- **输入**: `AgentState` (包含 `query`, `profile_name`)
- **逻辑**:
  - 获取profile配置
  - 根据profile生成4-5个子查询（硬编码规则）
  - 示例：
    ```python
    subqueries = [
        query,
        f"{query} event camera star tracking spacecraft jitter dataset benchmark",
        f"{query} attitude determination event-based vision method limitations",
        ...
    ]
    ```
- **输出**: `{"subqueries": [...]}`
- **LLM调用**: ❌ 无

#### **节点2: retrieve_candidates**
- **输入**: `AgentState` (包含 `subqueries`, `per_source_limit`, `profile_name`, `year_from`, `min_score`, `retry_count`)
- **逻辑**:
  1. 如果是重试（`retry_count > 0`），增加limit并使用聚焦查询
  2. 遍历每个子查询：
     - 调用 `retriever.search(query, per_source_limit, profile_name, year_from, min_score)`
     - 收集返回的论文和过滤统计
  3. 跨查询去重（保留最高分）
  4. 按 `(retrieval_score, year)` 降序排序
- **输出**: `{"candidates": [...], "query_filter_stats": [...], "filter_stats": {...}}`
- **LLM调用**: ❌ 无

#### **节点3: extract_evidence**
- **输入**: `AgentState` (包含 `candidates`, `query`)
- **逻辑**:
  - 从前12篇候选论文中提取摘要作为证据
  - 每条证据包含：`paper_id`, `title`, `snippet`（摘要前480字符）, `confidence`（检索分数）
- **输出**: `{"evidence": [...]}`
- **LLM调用**: ❌ 无

#### **节点4: critic_and_fix**
- **输入**: `AgentState` (包含 `evidence`, `retry_count`, `min_evidence`)
- **逻辑**:
  - 检查证据数量是否满足最小要求
  - 如果不足且未重试过，设置 `needs_more=True`
- **输出**: `{"needs_more": bool, "retry_count": int}`
- **LLM调用**: ❌ 无

#### **节点5: draft_answer**
- **输入**: `AgentState` (包含 `query`, `evidence`, `min_evidence`, `profile_name`)
- **逻辑**:
  1. 如果证据不足，返回错误消息
  2. 否则调用 `llm.summarize_evidence(query, evidence)`
- **输出**: `{"answer": str}`
- **LLM调用**: ✅ **唯一的LLM调用点**

### 2.4 检索层（Multi-Source Retrieval）

**文件**: `src/evagent/sources/__init__.py::MultiSourceRetriever`

**方法**: `search(query, per_source_limit, profile_name, year_from, min_score)`

**执行流程**:
1. 获取profile配置：`get_profile(profile_name)`
2. 计算各源的limit：
   ```python
   {
       "arxiv": ceil(1.5 * base),
       "openalex": ceil(1.3 * base),
       "semanticscholar": base,
       "crossref": max(1, int(0.7 * base)),
   }
   ```
3. 并行调用4个学术API：
   - `ArxivSource.search(query, limit)`
   - `OpenAlexSource.search(query, limit)`
   - `SemanticScholarSource.search(query, limit)`
   - `CrossrefSource.search(query, limit)`
4. 容错处理：单个API失败不影响整体流程
5. 调用 `profile_filter_and_rank(records, profile, year_from, min_score)`
6. 返回排序后的论文列表和统计信息

### 2.5 学术API层（Sources）

**文件**: `src/evagent/sources/*.py`

#### **ArxivSource** (`arxiv.py`)
- **API**: `http://export.arxiv.org/api/query`
- **请求**: `GET ?search_query=all:{query}&start=0&max_results={limit}`
- **解析**: XML (Atom feed)
- **返回**: `List[PaperRecord]`

#### **SemanticScholarSource** (`semanticscholar.py`)
- **API**: `https://api.semanticscholar.org/graph/v1/paper/search`
- **认证**: `x-api-key: {S2_API_KEY}`
- **请求**: `GET ?query={query}&limit={limit}&fields=...`
- **解析**: JSON
- **返回**: `List[PaperRecord]`

#### **OpenAlexSource** (`openalex.py`)
- **API**: `https://api.openalex.org/works`
- **认证**: 可选 `mailto` 参数
- **请求**: `GET ?search={query}&per_page={limit}`
- **解析**: JSON
- **返回**: `List[PaperRecord]`

#### **CrossrefSource** (`crossref.py`)
- **API**: `https://api.crossref.org/works`
- **认证**: `mailto` 参数（必需）
- **请求**: `GET ?query={query}&rows={limit}`
- **解析**: JSON
- **返回**: `List[PaperRecord]`

**重试机制**: 所有API客户端使用 `tenacity` 库的指数退避重试（最多3次）

### 2.6 排序与过滤层（Retrieval Ranking）

**文件**: `src/evagent/retrieval/ranking.py`

**函数**: `profile_filter_and_rank(records, profile, year_from, min_score)`

**评分公式**:
```python
domain_score = min(1.0, len(positive_term_hits) / 6.0)
source_score = profile.source_weights.get(source, 0.5)
recency_score = 1.0 if year >= year_from else 0.0
neg_penalty = min(0.5, 0.15 * len(negative_term_hits))

final_score = clamp(
    0.55 * domain_score +
    0.25 * source_score +
    0.20 * recency_score -
    neg_penalty
)
```

**过滤流程**:
1. 移除Crossref的component类型记录
2. 年份过滤（`year >= year_from`）
3. 评分过滤（`score >= min_score`）
4. 去重（`DOI > arXiv_id > title+author+year`）
5. 按 `(score, year)` 降序排序

### 2.7 LLM调用层（LiteLLM）

**文件**: `src/evagent/llm/client.py`

**类**: `LLMClient`

**方法**: `summarize_evidence(query, evidence)`

**执行流程**:
1. 构建prompt：
   ```python
   messages = [
       {
           "role": "system",
           "content": "You are a careful research assistant. Only answer with grounded claims."
       },
       {
           "role": "user",
           "content": f"Question: {query}\n"
                      "Use the evidence below and produce a concise answer with caveats.\n"
                      "Evidence:\n" + "\n".join(bullets)
       }
   ]
   ```
2. 调用LiteLLM：
   ```python
   resp = completion(
       model=model,  # 默认: "openai/qwen3-max"
       messages=messages,
       temperature=0.1,
       max_tokens=700,
       api_key=settings.effective_api_key,
       api_base=settings.effective_api_base,
   )
   ```
3. 提取响应：`resp.choices[0].message.content`

**API配置**:
- **模型**: `EVAGENT_CHAT_MODEL` (默认: qwen3-max)
- **API Key**: `EVAGENT_API_KEY` 或 `DASHSCOPE_API_KEY`
- **API Base**: `EVAGENT_API_BASE` 或 `DASHSCOPE_API_BASE`
- **温度**: 0.1（低随机性，确保一致性）
- **最大token**: 700

**Fallback机制**: 如果LiteLLM未安装或API Key缺失，返回本地fallback消息

---

## 三、LLM API调用详情

### 3.1 调用时机
- **唯一调用点**: `draft_answer` 节点
- **调用频率**: 每次 `evagent ask` 命令执行1次
- **前置条件**: 证据数量 >= `min_evidence`

### 3.2 调用参数
```python
{
    "model": "openai/qwen3-max",  # 可配置
    "messages": [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "Question: ... Evidence: ..."}
    ],
    "temperature": 0.1,
    "max_tokens": 700,
    "api_key": "<from .env>",
    "api_base": "<from .env>"
}
```

### 3.3 输入格式
- **系统提示**: "You are a careful research assistant. Only answer with grounded claims."
- **用户提示**: 包含原始查询和前6条证据的bullet列表
- **证据格式**: `- {title}: {snippet[:220]}`

### 3.4 输出处理
- 直接返回LLM生成的文本
- 无后处理或格式化
- 结果存储在 `AgentState["answer"]`

---

## 四、数据流转与状态管理

### 4.1 AgentState演化

```
初始状态:
{
    "query": str,
    "profile_name": str,
    "year_from": int,
    "min_score": float,
    "min_evidence": int,
    "per_source_limit": int,
    "retry_count": 0
}

↓ plan_subquestions

{
    ...,
    "subqueries": List[str]  # 新增
}

↓ retrieve_candidates

{
    ...,
    "candidates": List[dict],  # 新增
    "query_filter_stats": List[dict],  # 新增
    "filter_stats": dict  # 新增
}

↓ extract_evidence

{
    ...,
    "evidence": List[dict]  # 新增
}

↓ critic_and_fix

{
    ...,
    "needs_more": bool,  # 新增
    "retry_count": int  # 更新
}

↓ [条件路由: 如果needs_more=True，回到retrieve_candidates]

↓ draft_answer

{
    ...,
    "answer": str  # 新增
}
```

### 4.2 去重策略

**位置1**: `retrieval/ranking.py::profile_filter_and_rank`
- 在单次检索的多源结果中去重

**位置2**: `agents/nodes.py::retrieve_candidates`
- 在多个子查询的结果中去重（跨查询）

**去重键生成** (`models.py::dedup_key`):
```python
if p.doi:
    return f"doi:{p.doi.lower()}"
if p.paper_id.startswith("arxiv:"):
    return p.paper_id.lower()
# Fallback
title = " ".join((p.title or "").lower().split())
first_author = (p.authors[0].lower() if p.authors else "unknown")
year = str(p.year or "na")
return f"fallback:{title}|{first_author}|{year}"
```

---

## 五、关键设计模式

### 5.1 容错设计
- **API失败隔离**: 单个学术API失败不影响其他源
- **LLM Fallback**: 无API Key时返回本地消息
- **证据不足处理**: 自动触发重试或返回友好错误

### 5.2 可观测性
- **结构化日志**: 使用 `structlog`
- **运行记录**: 每次ask命令的完整trace存储到 `runs/ask_runs.jsonl`
- **过滤统计**: 每个阶段的数据量变化（raw → component_filter → year_filter → score_filter → dedup）

### 5.3 配置驱动
- **Profile系统**: 领域特定的检索策略
- **环境变量**: 所有API密钥和服务URL通过 `.env` 配置
- **可扩展性**: 新增profile或source只需添加配置，无需修改核心逻辑

---

## 六、性能特征

### 6.1 并发模型
- **学术API**: 串行调用（for循环），但有容错
- **子查询**: 串行处理
- **无异步**: 未使用 `asyncio`

### 6.2 网络请求统计（单次ask命令）
- **学术API**: 4个源 × N个子查询 = 最多20次HTTP请求（默认5个子查询）
- **LLM API**: 1次
- **总计**: 约21次外部API调用

### 6.3 重试机制
- **学术API**: 指数退避，最多3次（tenacity）
- **图层面**: critic节点触发的重检索（最多1次）

---

## 七、潜在改进点

### 7.1 性能优化
- 使用 `asyncio` 并发调用学术API
- 缓存学术API结果（基于query hash）
- 批量LLM调用（如果需要多轮对话）

### 7.2 功能增强
- 实现citation-hop检索（引用链追踪）
- 添加向量检索（Qdrant集成）
- 使用LLM生成子查询（替代硬编码规则）

### 7.3 可靠性
- 添加API rate limiting保护
- 实现更细粒度的错误分类和重试策略
- 增加单元测试覆盖率（当前仅有基础测试）

# `evagent ask` 端到端调用序列图

## 完整调用层级图（按实际函数执行顺序）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 用户命令行                                                                    │
│ $ evagent ask "What datasets are used?" --profile sps --year-from 2021      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. CLI入口层                                                                  │
│ src/evagent/app.py::ask()                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1.1 get_settings()                                                           │
│     └─> config.py::Settings.__init__()                                      │
│         └─> 读取 .env 文件                                                   │
│                                                                              │
│ 1.2 configure_logging(settings.log_level)                                   │
│     └─> observability/tracing.py::configure_logging()                       │
│                                                                              │
│ 1.3 retriever = MultiSourceRetriever(settings)                              │
│     └─> sources/__init__.py::MultiSourceRetriever.__init__()                │
│         ├─> ArxivSource()                                                   │
│         ├─> OpenAlexSource(api_key)                                         │
│         ├─> SemanticScholarSource(api_key)                                  │
│         └─> CrossrefSource(mailto)                                          │
│                                                                              │
│ 1.4 llm = LLMClient(settings)                                               │
│     └─> llm/client.py::LLMClient.__init__()                                 │
│                                                                              │
│ 1.5 graph = build_graph(retriever, llm)                                     │
│     └─> agents/graph.py::build_graph()                                      │
│         └─> StateGraph(AgentState)                                          │
│             ├─> add_node("plan", plan_subquestions)                         │
│             ├─> add_node("retrieve", lambda s: retrieve_candidates(...))    │
│             ├─> add_node("evidence", extract_evidence)                      │
│             ├─> add_node("critic", critic_and_fix)                          │
│             ├─> add_node("draft", lambda s: draft_answer(...))              │
│             ├─> add_edge(START, "plan")                                     │
│             ��─> add_edge("plan", "retrieve")                                │
│             ├─> add_edge("retrieve", "evidence")                            │
│             ├─> add_edge("evidence", "critic")                              │
│             ├─> add_conditional_edges("critic", route_after_critic, {...})  │
│             ├─> add_edge("draft", END)                                      │
│             └─> compile()                                                   │
│                                                                              │
│ 1.6 profile_obj = get_profile(profile)                                      │
│     └─> domain/profiles.py::get_profile()                                   │
│                                                                              │
│ 1.7 state = {初始状态字典}                                                    │
│                                                                              │
│ 1.8 final_state = graph.invoke(state)  ◄─── 进入LangGraph执行              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. LangGraph编排层                                                           │
│ [LangGraph内部调度器]                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2.1 执行节点: "plan"                                                         │
│     └─> agents/nodes.py::plan_subquestions(state)                           │
│         ├─> get_profile(state["profile_name"])                              │
│         │   └─> domain/profiles.py::get_profile()                           │
│         │       └─> 返回 SPS_SPACE_EVENT_STARTRACKING                       │
│         │                                                                    │
│         └─> 生成子查询列表（硬编码规则）:                                     │
│             [                                                                │
│               "What datasets are used?",                                    │
│               "What datasets... event camera star tracking...",             │
│               "What datasets... attitude determination...",                 │
│               "What datasets... satellite detection...",                    │
│               "What datasets... open-source code..."                        │
│             ]                                                                │
│         └─> 返回: {"subqueries": [...]}                                     │
│                                                                              │
│ 2.2 执行节点: "retrieve"                                                     │
│     └─> agents/nodes.py::retrieve_candidates(state, retriever)              │
│         │                                                                    │
│         ├─> 遍历每个子查询 (5次循环):                                        │
│         │   │                                                                │
│         │   └─> retriever.search(query, per_source_limit, ...)              │
│         │       └─> sources/__init__.py::MultiSourceRetriever.search()      │
│         │           │                                                        │
│         │           ├─> profile = get_profile(profile_name)                 │
│         │           │                                                        │
│         │           ├─> limits = _source_limits(per_source_limit)           │
│         │           │   └─> {"arxiv": 3, "openalex": 2, "s2": 2, ...}       │
│         │           │                                                        │
│         │           ├─> 调用学术API (4个源):                                 │
│         │           │   │                                                    │
│         │           │   ├─> self.arxiv.search(query, limit=3)               │
│         │           │   │   └─> sources/arxiv.py::ArxivSource.search()      │
│         │           │   │       └─> client.get_text(params={...})           │
│         │           │   │           └─> sources/base.py::APIClient.get_text()│
│         │           │   │               └─> requests.get(                    │
│         │           │   │                     "http://export.arxiv.org/...", │
│         │           │   │                     params={"search_query": ...}   │
│         │           │   │                   )                                │
│         │           │   │               └─> 解析XML (ElementTree)            │
│         │           │   │               └─> 返回 List[PaperRecord]           │
│         │           │   │                                                    │
│         │           │   ├─> self.openalex.search(query, limit=2)            │
│         │           │   │   └─> sources/openalex.py::OpenAlexSource.search()│
│         │           │   │       └─> client.get_json(params={...})           │
│         │           │   │           └─> requests.get(                        │
│         │           │   │                 "https://api.openalex.org/works",  │
│         │           │   │                 params={"search": query, ...}      │
│         │           │   │               )                                    │
│         │           │   │           └─> 解析JSON                             │
│         │           │   │           └─> 返回 List[PaperRecord]               │
│         │           │   │                                                    │
│         │           │   ├─> self.s2.search(query, limit=2)                  │
│         │           │   │   └─> sources/semanticscholar.py::...search()     │
│         │           │   │       └─> client.get_json(                        │
│         │           │   │             params={...},                          │
│         │           │   │             headers={"x-api-key": S2_API_KEY}      │
│         │           │   │           )                                        │
│         │           │   │           └─> requests.get(                        │
│         │           │   │                 "https://api.semanticscholar.org/...",│
│         │           │   │                 ...                                │
│         │           │   │               )                                    │
│         │           │   │           └─> 返回 List[PaperRecord]               │
│         │           │   │                                                    │
│         │           │   └─> self.crossref.search(query, limit=1)            │
│         │           │       └─> sources/crossref.py::CrossrefSource.search()│
│         │           │           └─> client.get_json(params={...})           │
│         │           │               └─> requests.get(                        │
│         │           │                     "https://api.crossref.org/works",  │
│         │           │                     params={"query": query, ...}       │
│         │           │                   )                                    │
│         │           │               └─> 返回 List[PaperRecord]               │
│         │           │                                                        │
│         │           │   [注: 每个API调用都有tenacity重试机制，最多3次]        │
│         │           │                                                        │
│         │           └─> profile_filter_and_rank(all_items, profile, ...)    │
│         │               └─> retrieval/ranking.py::profile_filter_and_rank() │
│         │                   │                                                │
│         │                   ├─> 过滤Crossref component记录                  │
│         │                   ├─> 年份过滤 (year >= year_from)                │
│         │                   ├─> 评分计算 (每条记录):                         │
│         │                   │   └─> _score_record(record, profile, ...)     │
│         │                   │       ├─> _normalized_text(record)            │
│         │                   │       ├─> _count_term_hits(text, positive)    │
│         │                   │       ├─> _count_term_hits(text, negative)    │
│         │                   │       └─> 计算加权分数:                        │
│         │                   │           0.55*domain + 0.25*source +         │
│         │                   │           0.20*recency - neg_penalty           │
│         │                   │                                                │
│         │                   ├─> 分数过滤 (score >= min_score)               │
│         │                   ├─> 去重 (dedup_key):                           │
│         │                   │   └─> models.py::dedup_key()                  │
│         │                   │       └─> DOI > arXiv_id > title+author+year  │
│         │                   │                                                │
│         │                   └─> 排序 (score desc, year desc)                │
│         │                   └─> 返回 (ranked, stats)                        │
│         │                                                                    │
│         ├─> 跨子查询去重 (seen字典，保留最高分)                              │
│         ├─> 最终排序                                                         │
│         └─> 返回: {                                                          │
│               "candidates": [...],                                           │
│               "query_filter_stats": [...],                                   │
│               "filter_stats": {...}                                          │
│             }                                                                │
│                                                                              │
│ 2.3 执行节点: "evidence"                                                     │
│     └─> agents/nodes.py::extract_evidence(state)                            │
│         ├─> 遍历前12个候选论文                                               │
│         ├─> 提取摘要作为snippet (前480字符)                                  │
│         └─> 返回: {"evidence": [                                             │
│               {                                                              │
│                 "claim": query,                                              │
│                 "paper_id": "...",                                           │
│                 "title": "...",                                              │
│                 "section": "abstract",                                       │
│                 "snippet": "...",                                            │
│                 "confidence": 0.75,                                          │
│                 "matched_terms": [...]                                       │
│               },                                                             │
│               ...                                                            │
│             ]}                                                               │
│                                                                              │
│ 2.4 执行节点: "critic"                                                       │
│     └─> agents/nodes.py::critic_and_fix(state)                              │
│         ├─> 检查: len(evidence) < min_evidence?                             │
│         ├─> 检查: retry_count < 1?                                          │
│         └─> 返回: {                                                          │
│               "needs_more": bool,                                            │
│               "retry_count": retry_count + 1                                 │
│             }                                                                │
│                                                                              │
│ 2.5 条件路由: route_after_critic(state)                                     │
│     └─> agents/graph.py::route_after_critic()                               │
│         ├─> if state["needs_more"]: return "retrieve"  ◄─┐                  │
│         └─> else: return "draft"                         │                  │
│                                                           │                  │
│     [如果needs_more=True，回到步骤2.2，使用focused_retry_subqueries]         │
│                                                                              │
│ 2.6 执行节点: "draft"                                                        │
│     └─> agents/nodes.py::draft_answer(state, llm)                           │
│         │                                                                    │
│         ├─> 检查: len(evidence) < min_evidence?                             │
│         │   └─> 如果是，返回错误消息                                         │
│         │                                                                    │
│         └─> llm.summarize_evidence(query, evidence)                         │
│             └─> llm/client.py::LLMClient.summarize_evidence()               │
│                 │                                                            │
│                 ├─> 构建prompt:                                              │
│                 │   messages = [                                             │
│                 │     {                                                      │
│                 │       "role": "system",                                    │
│                 │       "content": "You are a careful research assistant..." │
│                 │     },                                                     │
│                 │     {                                                      │
│                 │       "role": "user",                                      │
│                 │       "content": "Question: ...\nEvidence:\n- ..."         │
│                 │     }                                                      │
│                 │   ]                                                        │
│                 │                                                            │
│                 └─> self.chat(messages, temperature=0.1, max_tokens=700)    │
│                     └─> llm/client.py::LLMClient.chat()                     │
│                         │                                                    │
│                         ├─> 获取API配置:                                     │
│                         │   api_key = settings.effective_api_key            │
│                         │   api_base = settings.effective_api_base          │
│                         │   model = settings.chat_model                     │
│                         │                                                    │
│                         ├─> 模型名称处理:                                    │
│                         │   if api_base and "/" not in model:               │
│                         │       model = f"openai/{model}"                   │
│                         │                                                    │
│                         └─> ★★★ LLM API调用 ★★★                             │
│                             └─> litellm.completion(                         │
│                                   model="openai/qwen3-max",                 │
│                                   messages=[...],                            │
│                                   temperature=0.1,                           │
│                                   max_tokens=700,                            │
│                                   api_key="<DASHSCOPE_API_KEY>",            │
│                                   api_base="<DASHSCOPE_API_BASE>"           │
│                                 )                                            │
│                                 │                                            │
│                                 └─> [LiteLLM内部路由]                        │
│                                     └─> HTTP POST 到配置的API Base           │
│                                         (例: DashScope/OpenAI兼容端点)       │
│                                         {                                    │
│                                           "model": "qwen3-max",              │
│                                           "messages": [...],                 │
│                                           "temperature": 0.1,                │
│                                           "max_tokens": 700                  │
│                                         }                                    │
│                                     └─> 返回: ChatCompletion对象             │
│                                                                              │
│                             └─> 提取: resp.choices[0].message.content       │
│                             └─> 返回生成的答案文本                           │
│                                                                              │
│                 └─> 返回: {"answer": "生成的答案..."}                        │
│                                                                              │
│ 2.7 到达END节点                                                              │
│     └─> LangGraph返回final_state                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. 结果处理层                                                                 │
│ src/evagent/app.py::ask() [继续]                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3.1 提取结果:                                                                 │
│     answer = final_state["answer"]                                           │
│     evidence = final_state["evidence"]                                       │
│     candidates = final_state["candidates"]                                   │
│                                                                              │
│ 3.2 控制台输出:                                                               │
│     console.print(answer)                                                    │
│     console.print(evidence_table)                                            │
│                                                                              │
│ 3.3 持久化运行记录:                                                           │
│     record = {                                                               │
│       "ts": datetime.now().isoformat(),                                      │
│       "query": query,                                                        │
│       "profile": profile_obj.name,                                           │
│       "answer": answer,                                                      │
│       "evidence_count": len(evidence),                                       │
│       "candidate_count": len(candidates),                                    │
│       "filter_stats": {...},                                                 │
│       "query_trace": [...],                                                  │
│       "main_papers": [...],                                                  │
│       "evidence": [...]                                                      │
│     }                                                                        │
│                                                                              │
│     append_jsonl(settings.runs_dir / "ask_runs.jsonl", record)              │
│     └─> index/store.py::append_jsonl()                                      │
│         └─> 追加JSON行到文件                                                 │
│                                                                              │
│ 3.4 记录日志:                                                                 │
│     logger.info("run_saved path=%s query=%s", ...)                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │  命令执行完成  │
                            └───────────────┘
```

---

## 关键调用统计

### 外部API调用次数（单次ask命令）

| API类型 | 调用次数 | 说明 |
|---------|---------|------|
| arXiv API | 5次 | 每个子查询1次 |
| OpenAlex API | 5次 | 每个子查询1次 |
| Semantic Scholar API | 5次 | 每个子查询1次 |
| Crossref API | 5次 | 每个子查询1次 |
| **学术API小计** | **20次** | 4源 × 5子查询 |
| LLM API (LiteLLM) | 1次 | draft_answer节点 |
| **总计** | **21次** | |

### 重试机制

| 层级 | 重试策略 | 最大次数 |
|------|---------|---------|
| 学术API (tenacity) | 指数退避 (1s, 2s, 4s, 8s) | 3次 |
| 图层面 (critic) | 聚焦查询重检索 | 1次 |

### LLM调用详情

```python
# 唯一调用点
文件: src/evagent/llm/client.py
函数: LLMClient.chat()
触发节点: draft_answer

# 调用参数
{
    "model": "openai/qwen3-max",  # 可通过EVAGENT_CHAT_MODEL配置
    "messages": [
        {
            "role": "system",
            "content": "You are a careful research assistant. Only answer with grounded claims."
        },
        {
            "role": "user",
            "content": "Question: {query}\nUse the evidence below...\nEvidence:\n- {paper1}\n- {paper2}..."
        }
    ],
    "temperature": 0.1,      # 低随机性
    "max_tokens": 700,       # 限制输出长度
    "api_key": "<from .env>",
    "api_base": "<from .env>"
}

# 输入规模
- 系统提示: ~70 tokens
- 用户提示: ~200 tokens (query + 前6条evidence的title+snippet[:220])
- 总输入: ~270 tokens

# 输出规模
- 最大: 700 tokens
- 实际: 通常200-500 tokens (取决于证据复杂度)
```

---

## 数据流转示意

```
用户查询
    ↓
[plan] 生成5个子查询
    ↓
[retrieve] 每个子查询 → 4个学术API → 20次HTTP请求
    ↓
    合并 → 过滤 → 评分 → 去重 → 排序
    ↓
    候选论文列表 (通常10-30篇)
    ↓
[evidence] 提取前12篇的摘要
    ↓
    证据列表 (通常5-12条)
    ↓
[critic] 检查证据数量
    ↓
    如果不足 → 回到[retrieve] (最多1次)
    如果充足 → 继续
    ↓
[draft] 构建prompt → LLM API调用 (1次)
    ↓
    生成的答案文本
    ↓
输出到控制台 + 持久化到JSONL
```

---

## 时间复杂度分析

假设:
- N = 子查询数量 (默认5)
- M = 每源返回论文数 (默认2-3)
- K = 总候选论文数 (通常10-30)

| 操作 | 时间复杂度 | 说明 |
|------|-----------|------|
| plan_subquestions | O(1) | 硬编码规则 |
| retrieve_candidates | O(N × 4 × T_api) | N个查询 × 4个API × 网络延迟 |
| profile_filter_and_rank | O(K × P) | K篇论文 × P个术语匹配 |
| extract_evidence | O(K) | 遍历候选论文 |
| critic_and_fix | O(1) | 简单计数 |
| draft_answer | O(T_llm) | LLM推理时间 |

**总耗时估算** (无缓存):
- 学术API: 20次 × 1-3秒 = 20-60秒
- LLM API: 1次 × 2-5秒 = 2-5秒
- 本地处理: <1秒
- **总计**: 约25-70秒

---

## 状态转换图

```
AgentState演化:

初始 → [plan] → [retrieve] → [evidence] → [critic] → [draft] → 最终
  ↓        ↓          ↓            ↓           ↓          ↓        ↓
query  subqueries candidates   evidence   needs_more  answer   完整状态
       (5个)      (10-30篇)    (5-12条)   (bool)     (��本)
                                              │
                                              └─→ [retrieve] (如果True)
                                                      ↓
                                                  [evidence]
                                                      ↓
                                                  [draft]
```

---

## 错误处理路径

```
学术API失败
    ↓
    捕获异常 → 记录到source_errors → 继续其他源
    ↓
    如果所有源都失败 → candidates=[] → evidence=[] → 返回"证据不足"消息

LLM API失败
    ↓
    如果无API Key → 返回fallback消息 "[fallback-no-llm] ..."
    ↓
    如果API调用失败 → 异常向上传播 → 命令失败

证据不足
    ↓
    critic检测 → needs_more=True → 重试1次
    ↓
    如果仍不足 → draft返回友好错误消息
```

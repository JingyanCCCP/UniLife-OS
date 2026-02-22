# UniLife OS — 项目上下文

## 项目简介
2026 AI Agent 创新大赛参赛作品，校园生活 AI 助手。基于 Streamlit + DeepSeek-V3。

## 已完成

### Phase 1: Bug 修复 + 代码补全
- 修复 f-string 语法错误、plotly 依赖、饼图切换等
- 应用可正常运行

### Phase 2: Agent 能力 + 数据持久化 + UI 优化（2026-02-22 完成）
- **持久化层** `modules/persistence.py` — JSON 文件存储到 `data/user_data.json`，增量覆盖设计
- **Agent 工具** `modules/tools.py` — 8 个工具（query_schedule/finance/health/todos/exams/travel, record_expense, toggle_todo）
- **Agent 循环** `modules/chat_engine.py` 新增 `chat_agent()` — 自动 tool calling 最多 5 轮
- **mock_data.py** — get_todos/get_finance/get_health 集成持久化覆盖
- **app.py** — 接入 Agent 对话、持久化保存、工具调用可视化（st.status）、清除对话按钮、API 缺失引导、toast 反馈
- **system_prompt.py** — 新增工具使用指引
- 所有语法检查 + 运行时集成测试通过

## 文件结构
```
app.py                  — 主入口（Streamlit UI）
config.py               — 全局配置（API Key、模型名）
modules/
  mock_data.py          — Mock 数据 + 持久化合并
  chat_engine.py        — DeepSeek 对话引擎（流式 + Agent 循环）
  persistence.py        — JSON 持久化层
  tools.py              — Agent 工具 Schema + 执行路由
prompts/
  system_prompt.py      — Agent 人设 + 工具使用指引
data/
  user_data.json        — 用户数据（gitignore）
```

## 技术栈
- Python 3 + Streamlit 1.30+ + OpenAI SDK（连 DeepSeek API）
- Plotly（图表）、Pandas（数据处理）
- DeepSeek-V3（deepseek-chat）, function calling

## 待做（Phase 3 方向参考）
- 真实运行测试（streamlit run app.py）验证完整流程
- 更多 Agent 工具（如添加待办、修改旅行计划）
- 多轮对话记忆优化（context window 管理）
- 部署方案（Docker / Streamlit Cloud）
- 比赛演示 PPT / 录屏准备

# UniLife OS — 项目上下文

## 项目简介

2026 AI Agent 创新大赛参赛作品。UniLife OS 是一个专为大学生打造的 AI 校园生活助手，涵盖课程管理、财务记账、健康打卡、待办事项、旅行规划五大模块。用户可通过自然语言对话完成所有操作，AI Agent 自动调用 24 个工具处理请求。

基于 Streamlit + DeepSeek-V3（function calling），支持 PWA 添加到手机主屏幕。

## 技术架构

```
用户 ──→ Streamlit UI (app.py)
              │
              ├── 侧边栏：课程/财务/健康/待办/考试 实时面板
              ├── Tab 1：AI 对话（Agent 模式）
              └── Tab 2：数据看板（图表 + 旅行计划）
              │
         chat_agent() ← chat_engine.py
              │
              ├── DeepSeek API（function calling，最多 5 轮）
              ├── tools.py（24 个工具 schema + 执行路由）
              └── system_prompt.py（动态注入用户上下文）
              │
         数据层
              ├── mock_data.py（基础数据 + 持久化合并）
              └── persistence.py（增量覆盖 → data/user_data.json）
```

### 核心设计模式

- **增量覆盖**：mock_data 提供基础数据，persistence 只保存用户修改（覆盖/新增/删除标记），二者在 `get_*()` 函数中合并
- **Agent 循环**：`chat_agent()` 自动执行 tool calling → 工具结果反馈 → 模型生成回复，最多 5 轮
- **Toast 延迟**：`_toast_and_rerun()` 暂存消息到 session_state，rerun 后在 `main()` 顶部显示，解决 toast 被 rerun 清除的问题
- **主题自适应 CSS**：使用 `background-image` 半透明叠加（非 `background` 覆盖），保留 Streamlit 原生底色，单套 CSS 同时适配 Light/Dark

## Agent 工具总览（24 个）

| 类别 | 工具 | 功能 |
|------|------|------|
| 课程 | `query_schedule` | 查询整周/某天课表 |
|       | `add_course` | 添加课程 |
|       | `delete_course` | 删除课程（ID 或名称匹配） |
|       | `update_course` | 修改课程信息 |
| 财务 | `query_finance` | 查询月度财务概况 |
|       | `record_expense` | 记录消费 |
|       | `set_budget` | 设置月预算 |
| 健康 | `query_health` | 查询今日健康数据 |
|       | `record_water` | 喝水 +1 |
|       | `record_exercise` | 运动打卡（防重复，周计数累计） |
|       | `record_mood` | 记录心情 |
|       | `record_steps` | 记录步数 |
|       | `record_sleep` | 记录睡眠 |
|       | `set_exercise_goal` | 设置每周运动目标（3-7次） |
| 待办 | `query_todos` | 查询待办列表 |
|       | `toggle_todo` | 切换完成状态 |
|       | `add_todo` | 新增待办 |
| 考试 | `query_exams` | 查询考试倒计时 |
| 旅行 | `query_travel` | 查询旅行计划 |
|       | `update_travel` | 创建/修改/删除旅行计划 |
|       | `add_itinerary_stop` | 新增行程站点 |
|       | `delete_itinerary_stop` | 删除行程站点 |
|       | `update_itinerary_stop` | 修改行程站点 |
|       | `update_packing` | 勾选旅行必带清单 |

## 文件结构

```
app.py                  — 主入口（Streamlit UI + CSS + 侧边栏 + Tab 路由）
config.py               — 全局配置（API Key、模型名、应用名）
requirements.txt        — Python 依赖
modules/
  mock_data.py          — 基础数据 + 持久化合并（get_schedule/finance/health/todos/exams/travel/alerts）
  chat_engine.py        — DeepSeek 对话引擎（Agent 循环 + 上下文裁剪）
  persistence.py        — JSON 持久化层（原子写入，增量覆盖设计）
  tools.py              — 24 个 Agent 工具 Schema + 执行路由
prompts/
  system_prompt.py      — 动态 System Prompt（注入用户实时上下文 + 工具指引）
data/
  user_data.json        — 用户数据（gitignore，运行时自动生成）
.streamlit/
  static/
    manifest.json       — PWA 清单（standalone 模式）
    sw.js               — Service Worker（network-first + 离线回退）
    icon.svg            — 应用图标（学士帽 SVG）
    offline.html        — 离线回退页
```

## 技术栈

- **前端**：Streamlit 1.30+、Plotly（图表）、Pandas（数据处理）、PWA（Service Worker）
- **AI**：DeepSeek-V3（deepseek-chat），OpenAI SDK 兼容接口，function calling
- **持久化**：JSON 文件（原子写入，tempfile + os.replace）
- **部署**：Cloudflare Tunnel（cloudflared Quick Tunnel）演示部署

## 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key（项目根目录创建 .env）
echo "DEEPSEEK_API_KEY=你的密钥" > .env

# 3. 启动
streamlit run app.py

# 4. 公网演示（可选）
cloudflared tunnel --url http://localhost:8501
```

## 开发迭代记录

### Phase 1: Bug 修复 + 代码补全
- 修复 f-string 语法错误、plotly 依赖、饼图切换等
- 应用可正常运行

### Phase 2: Agent 能力 + 数据持久化 + UI 优化（2026-02-22）
- 持久化层 `persistence.py` — JSON 增量覆盖设计
- Agent 工具 8 个 + `chat_agent()` 自动 tool calling
- `app.py` — 工具调用可视化、清除对话、API 缺失引导

### Phase 3: 功能完善（2026-02-23）
- 新增 5 个工具（record_water / record_exercise / record_mood / update_packing / add_todo），总计 13 个
- `trim_messages()` 对话上下文裁剪（保留 system + 最近 20 条）

### Phase 4: PWA 支持（2026-02-23）
- manifest.json + Service Worker + 离线回退 + 学士帽图标
- 手机端"添加到主屏幕"体验

### Phase 5: 课表增删改 + Bug 修复（2026-02-23）
- 课表 CRUD 工具（add/delete/update_course），总计 18 个
- 图表禁用缩放，修复手机端误触

### Phase 5.1: 全面质量加固（2026-02-23）
修复 24 项缺陷：
- 健康数据跨天重置、动态日期计算、课表工具健壮性
- 待办状态同步、欢迎消息动态生成、对话历史限制 50 条
- OpenAI 客户端单例复用、原子写入防数据损坏

### Phase 5.2: 二次质量审查（2026-02-23）
修复 20 项问题：
- BUG（4 项）：类型强转、喝水计数修正、PWA 路径修复
- DEFECT（7 项）：整周课表、HTML 标签剥离、输入范围校验、Python 3.9+ 兼容
- IMPROVEMENT（8 项）：原子写入、重复打卡防护、心情选择、XSS 防护、考试倒计时

### Phase 6: UI/UX 修复 + 预算设置 + 旅行编辑（2026-02-24）
工具 18 → 23 个：
- Toast 持久化（`_toast_and_rerun()` 延迟机制）
- 月预算可设置（侧边栏 + Agent 工具 `set_budget`）
- 旅行计划 CRUD（4 个 Agent 工具 + 持久化合并）
- 课表自适应高度

### Phase 6.1: UI 视觉体系重构（2026-02-24）
多轮 Light/Dark 双模式真机调优：
- 侧边栏半透明紫渐变（`background-image` 自适应主题底色）
- 提醒卡片 85%~92% 半透明（自适应明暗）
- 毛玻璃指标卡片 + 胶囊式 Tab 导航

### Phase 6.2: 旅行计划创建修复（2026-02-24）
修复 AI 创建旅行计划无法显示的 bug：
- `update_travel` 新增 `create` 模式（清空旧行程 + 重建）
- 修复 deleted 标记未清除导致重建失败
- 新增 `packing_list` 可覆盖 + `companions` 类型守卫

### Phase 6.3: Header 卡片收窄（2026-02-24）
- `.main-header` 改为 `display: flex` 水平布局，padding 缩小为 `0.7rem 1.5rem`
- 标题 `font-size: 1.3rem`，描述 `font-size: 0.85rem`，减少纵向空间占用
- 保留原始完整描述文案

### Phase 7 尝试与回退记录（2026-02-24）
**目标**：将 AI 输入框悬浮到页面底部（类似 ChatGPT/Gemini），在任意视图都能输入。

**尝试方案**：
- 将 `st.chat_input()` 移到 `main()` 根作用域（Streamlit 自动 sticky 底部）
- 用 `session_state.active_view` + `st.button` 替代 `st.tabs`（因为 Streamlit 无法编程式切换 tab）
- 拆分 `render_chat_tab()` 为 `render_chat_messages()` + `process_chat_input()`
- 用 `_pending_prompt` 机制处理跨视图输入

**遇到的问题**：
1. `st.chat_input()` 在根作用域时页面自动滚动到底部，JS `scrollTo(0,0)` 注入无效
2. 用 `st.container(height=500)` 限制聊天区域后，与 `st.button` 导航 + `_pending_prompt` rerun 逻辑产生冲突
3. 页面出现异常颤动（rerun 循环），用户体验严重受损

**结论**：已回退到 `st.tabs` 布局，保留 Header 卡片收窄改动。悬浮输入框需要探索其他方案（如 Streamlit components 自定义组件、CSS-only fixed positioning 等）。

### Phase 8: 运动打卡修复 + 运动目标设置（2026-02-25）
工具 23 → 24 个：
- **Bug 修复**：运动打卡周次数不累计（`exercise_this_week` 每天重置回 mock 基础值）
  - 根因：`health_overrides.exercise_today` 跨天重置，导致昨天打卡记录丢失
  - 修复：新增 `exercise_weekly` 持久化字段（`week_start` + `count`），跨天累计、跨周自动重置
  - `get_health()` 从 `_past_base` mock 历史动态计算当前周运动次数 + 持久化计数
  - `log_exercise()` 防止同日重复打卡（返回 `bool`），Agent 工具给出对应提示
- **新功能**：每周运动目标可修改（3-7 次）
  - 持久化 `exercise_goal` 字段，侧边栏新增「运动目标设置」expander
  - Agent 工具 `set_exercise_goal`（第 24 个），支持自然语言设置

## 当前状态（2026-02-25）

- **布局**：`st.tabs(["💬 AI 对话", "📊 数据看板"])` 标准 tab 切换
- **输入框**：在"AI 对话" tab 内部，`st.chat_input()` 位于 `render_chat_tab()` 中
- **Header**：紧凑型 flex 水平布局（Phase 6.3 改动已保留）
- **Agent 工具**：24 个，覆盖课程/财务/健康/待办/考试/旅行全模块
- **持久化**：JSON 增量覆盖，原子写入
- **PWA**：manifest + Service Worker + 离线回退

## 待做（Phase 7 方向参考）

- 悬浮输入框（需要新方案，避免 Streamlit rerun 循环问题）
- 更多 Agent 工具（添加/修改考试安排）
- 数据导出（消费报表、健康周报）
- 多用户支持（当前单用户）
- Docker 容器化部署
- 比赛演示 PPT / 录屏准备

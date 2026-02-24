# UniLife OS — 项目上下文

## 项目简介
2026 AI Agent 创新大赛参赛作品，校园生活 AI 助手。基于 Streamlit + DeepSeek-V3。

## 已完成

### Phase 1: Bug 修复 + 代码补全
- 修复 f-string 语法错误、plotly 依赖、饼图切换等
- 应用可正常运行

### Phase 2: Agent 能力 + 数据持久化 + UI 优化（2026-02-22 完成）
- **持久化层** `modules/persistence.py` — JSON 文件存储到 `data/user_data.json`，增量覆盖设计
- **Agent 工具** `modules/tools.py` — 8 个工具（Phase 3/4/5 后续扩展至 18 个）
- **Agent 循环** `modules/chat_engine.py` 新增 `chat_agent()` — 自动 tool calling 最多 5 轮，含上下文裁剪
- **mock_data.py** — get_todos/get_finance/get_health 集成持久化覆盖
- **app.py** — 接入 Agent 对话、持久化保存、工具调用可视化（st.status）、清除对话按钮、API 缺失引导、toast 反馈
- **system_prompt.py** — 新增工具使用指引
- 所有语法检查 + 运行时集成测试通过

### Phase 3: 功能完善 — 新增 5 个 Agent 工具 + 对话上下文管理（2026-02-23 完成）
- **persistence.py** — 新增 `extra_todos` 持久化、`add_todo()` / `get_extra_todos()` 函数
- **mock_data.py** — `get_todos()` 合并用户新增的 extra_todos
- **tools.py** — 新增 5 个工具（record_water / record_exercise / record_mood / update_packing / add_todo），工具总数达 13 个
- **chat_engine.py** — 新增 `trim_messages()` 对话上下文裁剪（保留 system + 最近 20 条消息）
- **system_prompt.py** — 更新工具使用指引，覆盖全部 13 个工具
- **app.py** — 接入 `trim_messages()` 裁剪

### Phase 4: PWA 支持 — 手机端"添加到主屏幕"体验（2026-02-23 完成）
- **`.streamlit/static/manifest.json`** — PWA 清单（standalone 模式，紫色主题）
- **`.streamlit/static/sw.js`** — 轻量 Service Worker（network-first + 离线回退）
- **`.streamlit/static/icon.svg`** — 学士帽 SVG 图标（渐变紫色背景）
- **`.streamlit/static/offline.html`** — 离线回退页面
- **`app.py`** — 注入 PWA meta 标签 + Service Worker 注册脚本

### Phase 5: Bug 修复 + 课表增删改（2026-02-23 完成）
- **图表禁用缩放** — 3 处 `st.plotly_chart()` 添加 `config` + `dragmode=False`，修复手机端误触缩放
- **课表增删改** — 通过 AI 对话操作课表（add/delete/update_course 工具），工具总数达 18 个
- **快速记一笔修复** — 金额 0 时显示 `st.warning()` 提示；成功后 `st.toast()` + `st.rerun()`

### Phase 5.1: 全面质量加固（2026-02-23 完成）
修复真机测试发现的 24 项缺陷：
- **健康数据跨天失效** — `persistence.py` 新增 `_ensure_today_overrides()` 统一日期校验，水/步数/睡眠/运动/心情全部跨天自动重置
- **动态日期计算** — `get_finance()` 的 `days_left`/`daily_avg` 改为基于 `datetime.now()` 动态计算；`get_upcoming_exams()` 的 `days_left` 同理，并自动过滤已过期考试
- **提醒卡片 HTML** — `get_alerts()` 消息中的 `**markdown**` 替换为 `<strong>` HTML 标签
- **课表工具健壮性** — 模糊匹配改为单向子串 + 歧义提示；delete/update_course 验证课程存在；update 支持改课程名
- **待办状态同步** — `todo_done` session_state 每次渲染刷新而非仅初始化
- **旅行清单防幽灵保存** — checkbox 变化检测改为与持久化对比 + rerun
- **欢迎消息** — 不再持久化，每次新会话动态生成避免隔天陈旧
- **对话引擎** — OpenAI 客户端改为模块级单例复用；模型输出截断时追加提示；清理 `chat_once` 死代码和未使用 import
- **持久化层** — 对话历史限制最多 50 条防文件膨胀
- **PWA** — manifest.json SVG 图标去除误导性像素尺寸；SW 注册添加 scope 参数
- **代码清理** — 移除 `chat_stream` 未使用导入、`APP_DESCRIPTION` 未使用常量、内联 `datetime` 导入统一到模块级
- 全量语法检查 + 8 项运行时集成测试通过

### Phase 5.2: 二次质量审查修复（2026-02-23 完成）
针对二次审查发现的 20 项问题全部修复：
- **BUG 修复 (4 项)**
  - `tools.py` — delete/update_course 对 `course_id` 增加 `int()` 强转，防止 LLM 传入字符串类型
  - `persistence.py` + `tools.py` + `app.py` — `increment_water()` 返回值是覆盖计数而非总量，修改调用方改用 `get_health()["water_cups"]` 获取真实总量
  - `manifest.json` — icon `src` 从 `app/static/icon.svg` 改为 `icon.svg`（同目录相对路径），`start_url` 从 `.` 改为 `/`
  - `sw.js` — `OFFLINE_URL` 从 `app/static/offline.html` 改为 `offline.html`
- **DEFECT 修复 (7 项)**
  - `tools.py` — `query_schedule` 不传 day 时返回整周课表而非仅今日（与 schema 描述一致）
  - `mock_data.py` — `build_context_summary()` 使用 `re.sub` 剥离 alert message 中的 HTML `<strong>` 标签，避免泄漏到 LLM 上下文
  - `tools.py` — `update_course` 当 LLM 仅传 `course` 字段（未传 `course_id`/`course_name`）时 fallback 用 `course` 作为标识符
  - `tools.py` — `record_expense`/`record_steps`/`record_sleep` 增加输入范围校验
  - `tools.py` — `delete_course`/`update_course` 重构为统一流程：先解析 → int 转换 → 按 ID 验证 → 获取规范名称，杜绝使用 LLM 传入的未验证 `course_name`
  - 所有 modules 加 `from __future__ import annotations` 兼容 Python 3.9+
  - `sw.js` — 添加 scope 限制注释说明
- **IMPROVEMENT 优化 (8 项)**
  - `persistence.py` — `save_user_data()` 改为原子写入（tempfile + os.replace），防止写入中断导致 JSON 损坏
  - `persistence.py` — 添加 `OSError` 异常兜底，写入权限/磁盘空间不足时打印 stderr 而非崩溃
  - `chat_engine.py` — 彻底删除未使用的 `chat_stream()` 函数体
  - `app.py` — 运动打卡按钮：已打卡时显示 "✅ 已打卡" 并 disabled，防止重复点击
  - `app.py` — 心情记录改为 selectbox 下拉选择 5 种心情，取代硬编码 "😊 开心"
  - `app.py` — 消费流水用 `html.escape()` 转义用户输入的 item/category，防止 Self-XSS
  - `app.py` + `tools.py` + `mock_data.py` — 考试倒计时 "0 天后" 改为 "今天！"
  - `mock_data.py` — `get_upcoming_exams()` 返回数据新增 `is_today` 字段
- 全量 py_compile 语法检查通过

### Phase 6: UI/UX 修复 + 预算设置 + 旅行计划编辑（2026-02-24 完成）
真机测试发现的 5 个体验问题全部修复，工具总数 18 → 23 个：
- **Toast 提示持久化** — `st.toast()` 后 `st.rerun()` 导致提示一闪而过；改为 `_toast_and_rerun()` 延迟机制，暂存到 `session_state`，rerun 后在 `main()` 顶部统一显示。涉及 9 处替换
- **月预算可设置** — `persistence.py` 新增 `set_budget()`/`get_budget()`；`mock_data.py` 的 `get_finance()` 读取持久化预算；侧边栏新增预算设置 expander；新增 `set_budget` Agent 工具
- **旅行计划可删改** — `persistence.py` 新增旅行覆盖/行程增删改持久化函数；`mock_data.py` 的 `get_travel_plan()` 合并持久化数据（支持删除整个计划返回 None）；新增 4 个 Agent 工具（update_travel / add_itinerary_stop / delete_itinerary_stop / update_itinerary_stop）
- **课表自适应展开** — `st.dataframe(height=350)` 去掉固定高度，自适应行数
- 全量 py_compile 语法检查 + 集成测试通过

### Phase 6.1: UI 视觉体系重构（2026-02-24 完成）
多轮 Light/Dark 双模式真机调优：
- **侧边栏渐变** — 使用 `background-image`（非 `background`）叠加半透明亮紫渐变（indigo-400 / violet-500 / violet-300），保留主题原生底色。Light 模式呈清新薰衣草色，Dark 模式呈深沉紫调，单套 CSS 自动适配
- **提醒卡片自适应明度** — 三档卡片（high/medium/low）改为 85%~92% 半透明背景，叠在白底上自动变亮（珊瑚红/金琥珀/翠绿），叠在深色底上自动变沉（酒红/古铜/森林绿），无需 media query
- **指标卡片 & 折叠面板** — `backdrop-filter: blur()` 毛玻璃效果 + 紫调描边 + 阴影，两种模式下都有卡片层次感
- **侧边栏按钮统一风格** — 所有按钮加紫色半透明底色 + 描边 + 圆角 + hover 效果，与卡片/面板视觉语言一致
- **Tab 导航重构** — 智能提醒提升到 Tab 上方全局展示；Tab 按钮改为胶囊式，选中态紫色渐变 + 投影，视觉权重与 header 对齐
- **部署方案确认** — 使用 Cloudflare Tunnel（cloudflared）Quick Tunnel 模式进行演示部署

### Phase 6.2: 旅行计划创建/显示修复（2026-02-24 完成）
修复 AI 交互创建旅行计划无法正常显示的 bug：
- **根因 1：deleted 标记未清除** — `_exec_update_travel()` 修改计划时未清除 `deleted` 标记，导致删除后重新创建的计划始终被 `get_travel_plan()` 过滤为 None。修复：更新字段时统一写入 `deleted=False`
- **根因 2：无法创建全新计划** — 新增 `create` 模式：`update_travel(create=true, ...)` 会清空全部旧行程（`reset_travel_itinerary()`），之后通过 `add_itinerary_stop` 逐个添加新行程站点
- **根因 3：自定义数据未生效** — `get_travel_plan()` 的可覆盖字段新增 `packing_list`，支持 AI 设置自定义必带清单
- **健壮性加固** — `companions` 类型守卫（string → list 自动转换）；空行程占位提示；`add_itinerary_stop` 增加计划存在性检查；`packing_list` 为空时隐藏清单区域
- **persistence.py** — 新增 `reset_travel_itinerary()` 清空全部行程数据
- **tools.py** — `update_travel` schema 新增 `create`/`packing_list` 参数；`_exec_update_travel()` 重写支持创建模式
- **system_prompt.py** — 更新 `update_travel` 工具指引，说明创建用法
- 全量 py_compile 语法检查 + 集成测试通过

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
.streamlit/
  static/
    manifest.json       — PWA 清单
    sw.js               — Service Worker
    icon.svg            — 应用图标
    offline.html        — 离线回退页
```

## 技术栈
- Python 3 + Streamlit 1.30+ + OpenAI SDK（连 DeepSeek API）
- Plotly（图表）、Pandas（数据处理）
- DeepSeek-V3（deepseek-chat）, function calling

## 待做（Phase 7 方向参考）
- 更多 Agent 工具（如添加考试安排、修改旅行打包清单）
- 部署方案（Docker / Streamlit Cloud）
- 比赛演示 PPT / 录屏准备

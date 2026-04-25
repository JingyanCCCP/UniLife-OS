"""
UniLife OS — CSS 样式层（R4 起；R8 系列接入设计系统令牌 + 多版本拟态深化）

调用方只需在 `st.set_page_config` 之后一次调用 `inject_css()`。
设计系统令牌见 docs/设计系统.md。

版本演进（V2 → V3.4 全部累积；最新 V3.4 详见底部）：

- V2 Claude.ai 暖色 + 微拟态融合：米白 #FAF7F1 / 暖棕黑 #2C1F14 / Anthropic coral #D97757
- V3 editorial hero：横条改大衬线 hero + 4-up 数字面板，alert 卡走 severity 顶线
- V3.1 拟态深化：侧栏 / 输入控件凹陷皮肤；rest / hover / active 三态触感
- V3.2 磨砂 + 沙底：沙底 #E2DCCD 暖陶土；alert 卡换磨砂半透色 + 同色 hairline
- V3.3 边缘细化：所有 raised surface 补 inset 顶部 1px 内白光；Streamlit 原生 alert / checkbox / form / plotly 接入拟态系统

V3.4 仿 jj66-ui-refactor 分支扩层（2026-04-25 22:50+）：仿照参考分支的"双卡 hero + section heading + AI 状态胶囊 + 纸纹背景"扩展拟态层次：
- 多级 surface tokens：新增 `--color-bg-deep` 用作 hero 外卡 / 看板分隔区；`--color-accent-soft` 用作 alert 圆形 icon badge 底色
- `.stApp::before` 纸纹叠加：极弱的等距横线（1px / 5px gap，alpha 0.018）模拟便签纸质感；`.stApp` 本身追加两个 radial-gradient 暖光锚点
- Hero 三层结构：外卡 `--color-bg-deep` 微浮 → 内 `.hero-copy`（带顶部 inset 0.72 内白光）+ `.hero-metrics`（同样的内白光）；右上角加 5rem 装饰性 conic-gradient 圆斑（opacity 0.18）
- Hero 数字面板改 3-line tile：label / value（tabular-nums）/ note，让数字旁有 caption 解释
- 新增 `.hero-status` AI 在线/离线胶囊（dot + 文本）；离线/在线分别给 sand / low-severity 色调
- 新增 `.section-heading`（eyebrow small-caps + h2 大字）—— "Proactive care / 主动关怀" 类二级区块标题统一走这套
- Alert 卡恢复圆形 icon badge（`.alert-card-icon`），避免单纯磨砂色块缺一个视觉锚点；icon 用 accent-soft 底色 + grid 布局 24px 大小
- 侧栏内嵌 alert（考试倒计时）拿到自己的 wash 色 `--color-sidebar-alert`，跟主区 alert 拉开（避免主区磨砂色叠在沙底上"撞色"）
- 侧栏 metric / expander 加 24px 模糊 / 0 偏移的额外软阴影，制造"贴在沙底上的浮卡"感
- 旅行 item 加 `clip-path` 右上缺角，呼应构成主义几何骨架
- 全局 `font-variant-numeric: tabular-nums` 注入到所有数字 metric value，避免数字宽度跳动

V3.4.1 真机回归三修（2026-04-25 23:25 后）：用户在浏览器预览 V3.4 后报 3 个问题，按"surgical patch"补：
- 进度条满进度问题：删 V3.4 给侧栏 progress 加的 `[data-baseweb="progress-bar"] div:last-child` 渐变，因为这条选择器在 BaseWeb 嵌套结构里命中过宽，会把 track 也染上渐变看起来像 100% 满。回退到 V3.1 的"track bg-muted + inset / fill brand 实色"4 级嵌套规则
- 数据看板 metric 没拟态：补 `[data-testid="stMain"] [data-testid="stMetric"]` 拟态卡（warm bg + hairline + shadow-card），消费指标 / 旅行预算 metric 跟侧栏 metric 视觉对齐；同时把主区 h4 章节标题（`#### 消费构成` 等）改 display 字体 + 700 字重，4 个 panel 视觉拉开
- chat 第二层背景：Streamlit `[data-testid="stChatMessage"]` 外层已套 surface card，但内部 `[data-testid="stChatMessageContent"]` / `[data-testid="stMarkdownContainer"]` / `[data-testid="stChatMessageAvatarContainer"]` 自带 BaseWeb 默认 bg，叠在外卡上形成双层。把这些内层容器全部强制 `background: transparent`，让外层 surface 独立发挥

V3.4.2 chat 内外背景对齐重做（2026-04-25 23:35 后）：V3.4.1 的 chat 修只点了 3 个 testid 内层容器，但 Streamlit 实际嵌套常常 >3 层（emotion-cache 包了 stMarkdownContainer 外面再多一层 div 带 BaseWeb 默认 surface-2 浅灰底），导致用户在 V3.4.1 之后仍然看到「白外框 + 内浅灰文字框」双层。V3.4.2 改用「全部 descendant `*` transparent + 例外列表」策略：
- 外层 `.stChatMessage` 重申 surface card 全部 `!important`（防被 emotion-cache 覆盖）
- 内部 `[data-testid="stChatMessage"] *` 全部 background-color: transparent
- 例外保留 1：`code` / `pre` / `pre code` 保留 rgba(44,31,20,0.06) 暖底 + radius-sm + 内边距，让 inline code 在文字里有视觉边界
- 例外保留 2：`[data-testid="stChatMessageAvatarContainer"]` > * 保留 `--color-bg-warm` 底 + hairline，让头像 emoji 有圆形视觉边界
- 同时删除中段 V3.1 的 chat 卡 rule（与 V3.4.2 重复，统一用 V3.4.2）

V3.4.3 步数显示退化（2026-04-25 23:45 后）：用户报"步数显示又出问题了"。V3.1.1 修过的 ellipsis 在新版 BaseWeb 嵌套（value/delta 外又包一层 inner div）下又被裁。V3.4.3 surgical patch：
- delta 字号从 fs-caption 降到 0.72rem，svg 缩到 10x10，给"目标 8,000"留余地
- 新增 `[data-testid="stSidebar"] [data-testid="stMetric"] *` 全员兜底（min-width:0 / overflow:visible / nowrap / clip）→ 不再依赖只点外层 testid

V3.4.4 字体规范化（2026-04-25 后）：用户报"现在字体有些乱，统一规划一下"。按 DesignPrompt 工作流第 3 条"先口头化系统再动手"，把散落的字号 / 字重 / letter-spacing / line-height 统一收到一套 token：
- 字体家族：移除 `--font-body` 里第一档的 Inter（DesignPrompt 红线"Inter / Roboto / Arial 已审美疲劳"），改 PingFang SC 优先；display 仍 Source Serif 4 衬线（用户决策保留）
- 字号阶 5 → 6 + 1 特例：新增 `--fs-hero`（hero h1 唯一 clamp 动态字号）/ `--fs-display 1.75rem`（dashboard h4 / 主区大标题）/ `--fs-micro 0.7rem`（metric delta / note）/ `--fs-metric 1.2rem`（sidebar metric value 窄列特例，承接 V3.1.1 的紧凑值）；fs-h2 从 1.5rem 降到 1.34rem 与 section h2 / alert h4 对齐
- 行高 4 档 token：`--lh-tight 1.0` / `--lh-snug 1.2` / `--lh-normal 1.5` / `--lh-relaxed 1.62`；原本散落的 1.15 / 1.35 / 1.4 / 1.45 / 1.55 全部归到这 4 档
- letter-spacing 3 档 token：`--ls-eyebrow 0.14em`（uppercase 大写小字 eyebrow / 按钮）/ `--ls-display -0.02em`（display 大字微负 tracking）/ `--ls-caps 0.06em`（metric label uppercase）；原本散落的 0.05/0.18/-0.005/-0.018/-0.025/-0.035 全部归并
- 字重收敛：500 全部并入 600（标题）或 400（正文）；保留 400/600/800 三档 + 数字强调用 800
- 关键映射：hero h1 → fs-hero/800/display/tight；section h2 → fs-h2/800/display/tight；dashboard h4 → fs-display/800/display/snug；alert h4 → fs-h2/600/display/snug；sidebar metric value → fs-metric/800/display/snug；sidebar / main metric label → caption/600/caps/uppercase；hero-metric-note → micro/400/0/snug

- 不引入 12px+ 大圆角 / 紫粉糖果色 / 双向高光等 AI-slop 拟态特征
- 阴影透明度上限 0.10，inset 高光透明度上限 0.72
- 暖米 + Anthropic coral + 暖陶土 sidebar 三色基调不变
"""
from __future__ import annotations

import streamlit as st


_CSS = """
<style>
    /* ============================================================
     * 字体引入（V2：Claude.ai 风格的衬线 display + 现代 sans body）
     * ============================================================ */
    @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700;8..60,800&family=Inter:wght@400;500;600;700&family=Noto+Serif+SC:wght@400;600;700&display=swap');

    /* ============================================================
     * 设计系统令牌（R8-T1 定稿，V2 调暖：Claude.ai 配色 + 微拟态 + 构成主义骨架）
     * 详见 docs/设计系统.md
     * ============================================================ */
    :root {
        /* 中性（V2：暖米白底 + 暖棕黑文字；V3.1 加 recessed；V3.2 沙底加深 + overlay） */
        --color-bg-primary:  #FAF7F1;
        --color-bg-surface:  #FFFFFF;
        --color-bg-emphasis: #2C1F14;
        --color-bg-muted:    #F0EBE0;
        --color-bg-recessed: #E2DCCD;  /* V3.2.1：暖陶土 taupe，比 Claude 沙底再偏褐一点；纸本 / 咖啡馆质感 */
        --color-bg-deep:     #ECE3D2;  /* V3.4：hero 外卡 / 看板分隔 panel 底；介于 primary 与 recessed 之间 */
        --color-bg-warm:     #FFFCF7;  /* V3.4：略带暖意的纯白 surface，避免冷白 #FFF 撞米色背景 */
        --color-sidebar-alert:    #F1E8DC;  /* V3.4：侧栏内嵌 alert wash，跟主区磨砂色避免撞色 */
        --color-sidebar-alert-2:  #E7DECF;  /* 偶数序 alert 的对比色，让多个 alert 排在一起有节奏 */
        --color-accent-soft:      rgba(217, 119, 87, 0.16);  /* V3.4：alert 圆形 icon badge 底色 */
        --overlay-recess:    rgba(44, 31, 20, 0.05);  /* V3.2：universal 凹陷叠加，自适应任何 surface */
        --color-text-primary: #2C1F14;
        --color-text-muted:   #7A6859;
        --color-text-inverse: #FAF7F1;

        /* 品牌（V2：Anthropic coral + 暖深 hover） */
        --color-brand:      #D97757;
        --color-brand-soft: #E8967A;
        --color-brand-deep: #B05F44;

        /* 语义（V2：暖系 severity，避免冷硬；V3.2：补 RGB 分量便于 rgba() 调用） */
        --color-severity-high:   #C5483F;
        --color-severity-medium: #D9893F;
        --color-severity-low:    #4F8A6E;
        --color-severity-high-rgb:   197, 72, 63;
        --color-severity-medium-rgb: 217, 137, 63;
        --color-severity-low-rgb:    79, 138, 110;

        /* 数据可视化 */
        --color-data-1: #2C1F14;
        --color-data-2: #D97757;
        --color-data-3: #B89476;

        /* 边框（V2：暖棕透明，强分隔降到 0.40 而非 0.85） */
        --color-border-hairline: rgba(44, 31, 20, 0.10);
        --color-border-strong:   rgba(44, 31, 20, 0.40);

        /* 字体（V3.4.4：移除 Inter — DesignPrompt 红线"Inter/Roboto/Arial 已审美疲劳"；
         *                中文项目优先 PingFang SC，display 仍用 Source Serif 4 衬线） */
        --font-display: "Source Serif 4", "Noto Serif SC", "Songti SC", Georgia, serif;
        --font-body:    "PingFang SC", "Hiragino Sans GB", "Helvetica Neue", "Microsoft YaHei", system-ui, -apple-system, sans-serif;

        /* 字号阶（V3.4.4：6 档收敛 + 一个 hero clamp + 一个 metric 特例）
         *   --fs-hero    : hero h1 唯一动态字号
         *   --fs-display : dashboard 章节 h4 / 主区大标题
         *   --fs-h2      : section-heading h2 / alert-card h4
         *   --fs-h3      : sidebar 模块标题（### 课程 / 财务 / 健康）
         *   --fs-body    : 正文 / 按钮 / metric label
         *   --fs-caption : caption / eyebrow / 小字标签
         *   --fs-micro   : metric delta / metric note 等极小辅助文
         *   --fs-metric  : sidebar metric value 窄列特例（V3.1.1 防截断的 1.2rem，单独命名）
         */
        --fs-hero:     clamp(2.4rem, 4.6vw, 3.6rem);
        --fs-display:  1.75rem;
        --fs-h2:       1.34rem;
        --fs-h3:       1.05rem;
        --fs-body:     0.95rem;
        --fs-caption:  0.78rem;
        --fs-micro:    0.68rem;
        --fs-metric:   1.46rem;

        /* 行高 4 档（V3.4.4） */
        --lh-tight:    1.0;
        --lh-snug:     1.2;
        --lh-normal:   1.5;
        --lh-relaxed:  1.62;

        /* Letter-spacing 3 档（body 走 0 不需要 token；V3.4.4） */
        --ls-eyebrow:  0.14em;
        --ls-display:  -0.02em;
        --ls-caps:     0.06em;

        /* 间距（8px 网格） */
        --space-1: 4px;
        --space-2: 8px;
        --space-3: 16px;
        --space-4: 24px;
        --space-5: 32px;
        --space-6: 48px;

        /* 圆角（V2：微拟态略温和，但克制不到 12px+ 那种 GPT 默认） */
        --radius-sm: 4px;
        --radius-md: 6px;
        --radius-lg: 10px;

        /* 阴影（V2 注入；V3.1 加 inset/button-rest；V3.3 raised surface 补顶部 1px 内白光；
         * V3.4.6：alpha 抬一档（0.04 → 0.08 / 0.04 → 0.07）— 沙底 #E2DCCD 和米底 #F5F2EC
         * 比纯白暗一档，0.04 在这两个底上几乎不可见；上限仍 0.10 不破红线 */
        --shadow-card:
            inset 0 1px 0 rgba(255, 255, 255, 0.62),
            0 1px 2px rgba(44, 31, 20, 0.07),
            0 6px 16px rgba(44, 31, 20, 0.08);
        --shadow-hover:
            inset 0 1px 0 rgba(255, 255, 255, 0.68),
            0 3px 8px rgba(44, 31, 20, 0.09),
            0 12px 24px rgba(44, 31, 20, 0.09);
        --shadow-emphasis:
            inset 0 1px 0 rgba(255, 255, 255, 0.58),
            0 6px 20px rgba(44, 31, 20, 0.10);
        --shadow-inset:    inset 0 1px 2px rgba(44, 31, 20, 0.06), inset 0 0 0 1px rgba(44, 31, 20, 0.04);
        --shadow-button-rest:
            inset 0 1px 0 rgba(255, 255, 255, 0.45),
            0 1px 1px rgba(44, 31, 20, 0.03),
            0 0 0 1px rgba(44, 31, 20, 0.05);
    }

    /* ============================================================
     * 全局：底色 + 字体 + V3.4 纸纹 / 暖光底层
     *
     * `.stApp` 主底走米色 #FAF7F1，叠加 2 个极弱的 radial-gradient（左下 coral 暖光 + 右上 sand 暖光）
     * `.stApp::before` 全屏覆盖一层 1px 横线纸纹（alpha 0.018，5px 间距），点缀但不抢戏
     * ============================================================ */
    .stApp,
    [data-testid="stAppViewContainer"] {
        background-color: var(--color-bg-primary) !important;
        color: var(--color-text-primary);
        font-family: var(--font-body);
        font-variant-numeric: tabular-nums;
        background-image:
            radial-gradient(circle at 92% -8%, rgba(184, 148, 118, 0.10), transparent 34rem),
            radial-gradient(circle at 9% 12%, rgba(217, 119, 87, 0.07), transparent 30rem) !important;
    }
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;
        background-image: repeating-linear-gradient(
            0deg,
            rgba(44, 31, 20, 0.018) 0,
            rgba(44, 31, 20, 0.018) 1px,
            transparent 1px,
            transparent 5px
        );
        opacity: 0.30;
    }
    /* 内容层位于 ::before 之上，避免纸纹遮住交互 */
    [data-testid="stAppViewContainer"] > * {
        position: relative;
        z-index: 1;
    }

    /* ============================================================
     * Header（V3.4 双卡 hero — 外卡 bg-deep panel 包住两张内卡：hero-copy + hero-metrics）
     *
     * 旧 V3 的 hero 直接贴在主区背景上，缺少"作品装在画框里"的层次。
     * V3.4 用一层 `--color-bg-deep` 微浮外卡把 hero 整体框起来，再在内层各自给两张白底卡片，
     * 形成 deep panel → warm surface 两段层级关系，呼应整页的"main → recessed → surface"三段调色。
     *
     * 内卡顶部都补了 inset 0 1px 0 rgba(255,255,255,0.72)（比通用 shadow-card 的 0.60 更亮一点），
     * 因为 hero 是首屏视觉锚点，多吃一点高光更扎眼。
     * 装饰圆斑：`.hero-copy::after` 5rem conic-gradient，opacity 0.18，作为右上角的几何 anchor。
     * ============================================================ */
    .main-header {
        display: grid;
        grid-template-columns: minmax(320px, 1.04fr) minmax(320px, 0.96fr);
        gap: var(--space-2);
        align-items: stretch;
        margin: 0 0 var(--space-4) 0;
        padding: var(--space-2);
        color: var(--color-text-primary);
        background: var(--color-bg-deep);
        border: 1px solid var(--color-border-hairline);
        border-radius: var(--radius-lg);
        box-shadow:
            inset 0 1px 0 rgba(255, 255, 255, 0.50),
            0 1px 2px rgba(44, 31, 20, 0.04),
            0 12px 32px rgba(44, 31, 20, 0.06);
    }
    .main-header .hero-copy {
        position: relative;
        min-height: 232px;
        padding: var(--space-4) var(--space-4);
        border-radius: var(--radius-md);
        background: var(--color-bg-warm);
        border: 1px solid var(--color-border-hairline);
        box-shadow:
            inset 0 1px 0 rgba(255, 255, 255, 0.72),
            0 1px 2px rgba(44, 31, 20, 0.03);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        overflow: hidden;
    }
    /* 装饰性几何圆斑：克制的 0.18 opacity 不抢主视觉，但呼应构成主义骨架 */
    .main-header .hero-copy::after {
        content: "";
        position: absolute;
        right: 1rem;
        top: 1rem;
        width: 5rem;
        height: 5rem;
        border-radius: 50%;
        background: conic-gradient(
            from 90deg,
            #D97757,
            #B89476,
            #7A6859,
            #4F8A6E,
            #B05F44,
            #D97757
        );
        opacity: 0.18;
        filter: blur(0.5px);
        pointer-events: none;
    }
    .main-header .hero-eyebrow {
        display: block;
        position: relative;
        z-index: 1;
        font-family: var(--font-body);
        font-size: var(--fs-caption);
        font-weight: 700;
        letter-spacing: var(--ls-eyebrow);
        text-transform: uppercase;
        color: var(--color-brand-deep);
        margin-bottom: var(--space-2);
    }
    .main-header h1 {
        position: relative;
        z-index: 1;
        margin: 0 0 var(--space-2) 0;
        font-family: var(--font-display);
        font-size: var(--fs-hero);
        font-weight: 800;
        letter-spacing: var(--ls-display);
        line-height: var(--lh-tight);
        color: var(--color-text-primary);
    }
    .main-header .hero-desc {
        position: relative;
        z-index: 1;
        margin: 0 0 var(--space-3) 0;
        font-size: var(--fs-body);
        color: var(--color-text-muted);
        max-width: 38ch;
        line-height: var(--lh-relaxed);
    }

    /* AI 在线 / 离线胶囊（V3.4 新增） */
    .main-header .hero-status {
        position: relative;
        z-index: 1;
        align-self: flex-start;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0.75rem;
        font-size: var(--fs-caption);
        font-weight: 600;
        color: var(--color-text-primary);
        background: var(--color-bg-surface);
        border: 1px solid var(--color-border-hairline);
        border-radius: 999px;
        box-shadow: var(--shadow-card);
    }
    .main-header .hero-status .hero-status-dot {
        width: 0.5rem;
        height: 0.5rem;
        border-radius: 50%;
        background: var(--color-text-muted);
    }
    .main-header .hero-status.is-online .hero-status-dot {
        background: var(--color-severity-low);
        box-shadow: 0 0 0 3px rgba(var(--color-severity-low-rgb), 0.20);
    }
    .main-header .hero-status.is-offline .hero-status-dot {
        background: var(--color-severity-medium);
        box-shadow: 0 0 0 3px rgba(var(--color-severity-medium-rgb), 0.18);
    }

    /* Metrics 卡：2x2 网格内嵌在外卡里；每个 cell 透明，靠 grid border 分隔 */
    .main-header .hero-metrics {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0;
        overflow: hidden;
        background: var(--color-bg-warm);
        border: 1px solid var(--color-border-hairline);
        border-radius: var(--radius-md);
        box-shadow:
            inset 0 1px 0 rgba(255, 255, 255, 0.72),
            0 1px 2px rgba(44, 31, 20, 0.03);
    }
    .main-header .hero-metric {
        position: relative;
        min-height: 92px;
        padding: var(--space-2) var(--space-3);
        background: transparent;
        border: 0;
        border-radius: 0;
        box-shadow: none;
        transition: background 0.2s ease, transform 0.2s ease;
    }
    .main-header .hero-metric:nth-child(odd) {
        border-right: 1px solid var(--color-border-hairline);
    }
    .main-header .hero-metric:nth-child(n + 3) {
        border-top: 1px solid var(--color-border-hairline);
    }
    .main-header .hero-metric:hover {
        background: rgba(255, 252, 247, 0.62);
        transform: translateY(-1px);
    }
    .main-header .hero-metric-label {
        display: block;
        margin: 0 0 var(--space-1) 0;
        font-size: var(--fs-body);
        font-weight: 600;
        color: var(--color-text-muted);
        letter-spacing: var(--ls-caps);
    }
    .main-header .hero-metric-value {
        display: block;
        font-family: var(--font-display);
        font-size: clamp(1.85rem, 3.2vw, 2.4rem);
        font-weight: 800;
        color: var(--color-text-primary);
        line-height: var(--lh-tight);
        letter-spacing: var(--ls-display);
        font-variant-numeric: tabular-nums;
    }
    .main-header .hero-metric-note {
        display: block;
        margin-top: var(--space-1);
        font-size: var(--fs-caption);
        font-weight: 400;
        color: var(--color-text-muted);
        line-height: var(--lh-snug);
    }
    @media (max-width: 880px) {
        .main-header { grid-template-columns: 1fr; }
        .main-header .hero-copy { min-height: 188px; }
    }
    @media (max-width: 720px) {
        .main-header .hero-metrics { grid-template-columns: 1fr; }
        .main-header .hero-metric:nth-child(odd) { border-right: 0; }
        .main-header .hero-metric:nth-child(n + 2) { border-top: 1px solid var(--color-border-hairline); }
    }

    /* ============================================================
     * Section heading（V3.4 新增）—— eyebrow + h2 二级区块标题
     *
     * 用于"主动关怀"等主区二级 section header，替换原来的 ### 单行 markdown
     * eyebrow 走小型大写字（Anthropic 范式），h2 走 display 字体 + 760 字重
     * ============================================================ */
    .section-heading {
        display: flex;
        align-items: end;
        justify-content: space-between;
        gap: var(--space-3);
        margin: var(--space-5) 0 var(--space-3) 0;
    }
    .section-heading .section-eyebrow {
        display: block;
        margin-bottom: var(--space-1);
        font-family: var(--font-body);
        font-size: var(--fs-caption);
        font-weight: 700;
        letter-spacing: var(--ls-eyebrow);
        text-transform: uppercase;
        color: var(--color-brand-deep);
    }
    .section-heading h2 {
        margin: 0;
        font-family: var(--font-display);
        font-size: var(--fs-h2);
        font-weight: 800;
        letter-spacing: var(--ls-display);
        color: var(--color-text-primary);
    }

    /* ============================================================
     * 以下规则将在 R8-T3 / T4 / T5 阶段逐步重构。
     * 暂保留旧紫色样式以避免视觉断层；T3 起按卡片替换。
     * ============================================================ */

    /* ============================================================
     * Alert 卡片（V3.2 磨砂半透色 + 同色 hairline；V3.4 复活圆形 icon badge）
     *
     * V3 取消了 icon emoji，结果磨砂色块缺少视觉锚点，3 张卡片排在一起像 3 块同形色块。
     * V3.4 在标题左侧补一个 2.1rem 圆形 badge 装 icon —— icon 是功能性 marker（不在 h1~h4 里），
     * 不违反"标题去 emoji"规则；圆形 badge 底色用 accent-soft（coral 透明 16%），跟磨砂色块共享同一套暖色阶。
     * Layout 改 grid auto 1fr 让 badge 跟标题/正文垂直对齐。
     * ============================================================ */
    .alert-card-high,
    .alert-card-medium,
    .alert-card-low {
        display: grid;
        grid-template-columns: auto 1fr;
        gap: var(--space-3);
        align-items: start;
        padding: var(--space-3) var(--space-4);
        border-radius: var(--radius-md);
        margin-bottom: var(--space-2);
        color: var(--color-text-primary);
        border: 1px solid var(--color-border-hairline);
        box-shadow: var(--shadow-card);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        transition: box-shadow 0.2s ease, transform 0.2s ease, border-color 0.2s ease;
    }
    .alert-card-high:hover,
    .alert-card-medium:hover,
    .alert-card-low:hover {
        box-shadow: var(--shadow-hover);
        transform: translateY(-1px);
    }
    .alert-card-high {
        background: rgba(var(--color-severity-high-rgb), 0.10);
        border-color: rgba(var(--color-severity-high-rgb), 0.22);
    }
    .alert-card-medium {
        background: rgba(var(--color-severity-medium-rgb), 0.10);
        border-color: rgba(var(--color-severity-medium-rgb), 0.22);
    }
    .alert-card-low {
        background: rgba(var(--color-severity-low-rgb), 0.10);
        border-color: rgba(var(--color-severity-low-rgb), 0.22);
    }
    /* 圆形 icon badge（V3.4 新增）—— alert 卡左侧 2.1rem 圆，icon emoji 居中 */
    .alert-card-icon {
        width: 2.1rem;
        height: 2.1rem;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        line-height: 1;
        border-radius: 50%;
        background: var(--color-bg-warm);
        border: 1px solid var(--color-border-hairline);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.65);
    }
    .alert-card-high .alert-card-icon {
        background: rgba(var(--color-severity-high-rgb), 0.16);
        border-color: rgba(var(--color-severity-high-rgb), 0.26);
    }
    .alert-card-medium .alert-card-icon {
        background: rgba(var(--color-severity-medium-rgb), 0.16);
        border-color: rgba(var(--color-severity-medium-rgb), 0.26);
    }
    .alert-card-low .alert-card-icon {
        background: rgba(var(--color-severity-low-rgb), 0.16);
        border-color: rgba(var(--color-severity-low-rgb), 0.26);
    }
    .alert-card-high h4,
    .alert-card-medium h4,
    .alert-card-low h4 {
        margin: 0 0 var(--space-1) 0;
        font-family: var(--font-display);
        font-size: var(--fs-h2);
        font-weight: 600;
        letter-spacing: var(--ls-display);
        line-height: var(--lh-snug);
        color: var(--color-text-primary);
    }
    .alert-card-high p,
    .alert-card-medium p,
    .alert-card-low p {
        margin: 0;
        font-size: var(--fs-body);
        color: var(--color-text-primary);
        opacity: 0.85;
        line-height: var(--lh-normal);
    }

    /* 旅行行程条目 V3.4：在 V3.3 卡片基础上加 clip-path 右上缺角，呼应构成主义几何骨架 */
    .travel-item {
        position: relative;
        background: var(--color-bg-warm);
        border: 1px solid var(--color-border-hairline);
        border-left: 3px solid var(--color-brand);
        border-radius: 0 var(--radius-md) var(--radius-md) 0;
        box-shadow: var(--shadow-card);
        padding: var(--space-3) var(--space-3);
        margin-bottom: var(--space-2);
        clip-path: polygon(0 0, calc(100% - 0.7rem) 0, 100% 0.7rem, 100% 100%, 0 100%);
    }
    .travel-item strong {
        font-family: var(--font-body);
        font-weight: 700;
        color: var(--color-text-primary);
    }
    .travel-item small {
        color: var(--color-text-muted);
    }

    /* ============================================================
     * 侧边栏（V3.2 沙底；V3.3 重启右边缘 hairline，沙底加深后这条线现在能看见了）
     * ============================================================ */
    [data-testid="stSidebar"] {
        background-image: none;
        background-color: var(--color-bg-recessed);
        box-shadow: inset -1px 0 0 rgba(44, 31, 20, 0.10);
    }
    [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        background-color: transparent;
    }

    /* 侧边栏顶部 brand 区（V2：display 字体 + 暖棕黑） */
    [data-testid="stSidebar"] h2 {
        font-family: var(--font-display);
        font-size: var(--fs-h2);
        font-weight: 800;
        letter-spacing: var(--ls-display);
        color: var(--color-text-primary);
        margin-bottom: var(--space-1);
    }

    /* 模块标题（"今日课程""财务快览"等 ### 标题） */
    [data-testid="stSidebar"] h3 {
        font-size: var(--fs-h3);
        font-weight: 600;
        letter-spacing: var(--ls-caps);
        text-transform: uppercase;
        color: var(--color-text-primary);
        margin-top: var(--space-3);
        margin-bottom: var(--space-2);
    }

    /* 正文段落（stMarkdown 渲染的普通文字） */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        font-size: var(--fs-body);
        color: var(--color-text-primary);
        line-height: var(--lh-normal);
    }

    /* caption 与小字 */
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    [data-testid="stSidebar"] small {
        font-size: var(--fs-caption);
        color: var(--color-text-muted);
    }

    /* 分隔线（V3.1：从 2px 实黑改 1px hairline，让卡片自身的微阴影承担分隔） */
    [data-testid="stSidebar"] hr {
        border: none;
        border-top: 1px solid var(--color-border-hairline);
        margin: var(--space-3) 0;
    }

    /* 进度条（V3.1：轨道凹陷 + 品牌色填充） */
    [data-testid="stSidebar"] [data-testid="stProgress"] > div > div {
        background: var(--color-bg-muted) !important;
        box-shadow: var(--shadow-inset);
        border-radius: var(--radius-sm);
        overflow: hidden;
    }
    [data-testid="stSidebar"] [data-testid="stProgress"] > div > div > div > div {
        background-color: var(--color-brand) !important;
    }
    /* ============================================================
     * Metric 指标卡（V2：白底 + 微拟态阴影；V3.1.1：紧凑 padding + 关 ellipsis）
     *
     * 侧边栏 2-column metric 在 245px 默认宽下每列仅约 80px 内容区，
     * 4-5 位带千位分隔的步数（"8,000"）在 1.5rem 粗体下会被 Streamlit 默认 ellipsis 截掉。
     * 这里收紧 padding（16→8px）+ 降字号（1.5→1.2rem）+ 显式关 ellipsis 防止内容被剪。
     * ============================================================ */
    [data-testid="stSidebar"] [data-testid="stMetric"],
    [data-testid="stSidebar"] .stMetric,
    .stSidebar [data-testid="stMetric"],
    .stSidebar .stMetric {
        background: rgba(255, 255, 255, 0.94) !important;
        backdrop-filter: none;
        -webkit-backdrop-filter: none;
        border: 1px solid rgba(33, 27, 23, 0.18) !important;
        border-radius: var(--radius-md) !important;
        padding: var(--space-2) !important;
        box-shadow:
            inset 0 1px 0 rgba(255, 255, 255, 0.85),
            0 2px 4px rgba(44, 31, 20, 0.09),
            0 10px 22px rgba(44, 31, 20, 0.10) !important;
        overflow: visible;
    }
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        font-size: var(--fs-caption);
        font-weight: 600;
        color: var(--color-text-muted);
        letter-spacing: var(--ls-caps);
        text-transform: uppercase;
    }
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        font-family: var(--font-display);
        font-size: var(--fs-metric) !important;
        font-weight: 800;
        letter-spacing: var(--ls-display);
        color: var(--color-text-primary);
        line-height: var(--lh-snug);
        white-space: nowrap;
        overflow: visible;
        text-overflow: clip;
        font-variant-numeric: tabular-nums;
    }
    [data-testid="stSidebar"] [data-testid="stMetricValue"] p {
        font-size: var(--fs-metric) !important;
        line-height: var(--lh-snug) !important;
    }
    [data-testid="stSidebar"] [data-testid="stMetricDelta"] {
        font-size: var(--fs-micro) !important;
        color: var(--color-text-muted);
        white-space: nowrap;
        overflow: visible;
        text-overflow: clip;
    }
    [data-testid="stSidebar"] [data-testid="stMetricDelta"] p {
        font-size: var(--fs-micro) !important;
        line-height: var(--lh-snug) !important;
    }
    [data-testid="stSidebar"] [data-testid="stMetricDelta"] svg {
        width: 10px;
        height: 10px;
        margin-right: 2px;
    }
    /* V3.4.3：BaseWeb 在 metric value/delta 外又包一层 inner <div>，那层默认带
     * overflow:hidden + ellipsis。V3.1.1 只命中 outer testid，inner 仍会裁。
     * 这里全员兜底：让侧栏 metric 内任何后代都不再裁掉数字 / "目标 X,XXX" 文本。
     * 限定在 stSidebar stMetric 内，不影响主区或其它组件。
     */
    [data-testid="stSidebar"] [data-testid="stMetric"] * {
        min-width: 0;
        max-width: none;
        white-space: nowrap;
        overflow: visible;
        text-overflow: clip;
    }

    /* ============================================================
     * Expander 折叠面板（V2：白底 + 微拟态阴影 + 圆角 6px）
     * ============================================================ */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background: var(--color-bg-warm);
        backdrop-filter: none;
        -webkit-backdrop-filter: none;
        border: 1px solid var(--color-border-hairline);
        border-radius: var(--radius-md);
        box-shadow:
            inset 0 1px 0 rgba(255, 255, 255, 0.65),
            0 2px 4px rgba(44, 31, 20, 0.07),
            0 8px 18px rgba(44, 31, 20, 0.08);
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary {
        font-size: var(--fs-body);
        font-weight: 500;
        color: var(--color-text-primary);
    }

    /* 主区域 expander（图片上传等） */
    [data-testid="stMain"] [data-testid="stExpander"] {
        background: var(--color-bg-surface);
        border: 1px solid var(--color-border-hairline);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-card);
    }
    /* ============================================================
     * 侧边栏二级按钮（V3.1 拟态化）：rest 浅浮 + hover 抬升 + active 凹陷
     * ============================================================ */
    [data-testid="stSidebar"] .stButton > button {
        border: 1px solid var(--color-border-hairline);
        border-radius: var(--radius-md);
        background: var(--color-bg-surface);
        color: var(--color-text-primary);
        font-weight: 500;
        transition: all 0.15s ease;
        padding: var(--space-2) var(--space-3);
        box-shadow: var(--shadow-button-rest);
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: var(--color-bg-surface);
        border-color: var(--color-border-hairline);
        box-shadow: var(--shadow-card);
        transform: translateY(-1px);
    }
    [data-testid="stSidebar"] .stButton > button:active {
        box-shadow: var(--shadow-inset);
        transform: translateY(0);
    }

    /* form 内部主按钮（"📝 记录"等表单提交按钮）—— 主按钮样式（V3.1：rest 也带阴影） */
    [data-testid="stSidebar"] [data-testid="stForm"] .stButton > button,
    [data-testid="stSidebar"] [data-testid="stFormSubmitButton"] > button {
        background: var(--color-bg-emphasis);
        color: var(--color-text-inverse);
        border: 1px solid var(--color-bg-emphasis);
        border-radius: var(--radius-md);
        font-weight: 600;
        transition: all 0.15s ease;
        box-shadow: var(--shadow-card);
    }
    [data-testid="stSidebar"] [data-testid="stForm"] .stButton > button:hover,
    [data-testid="stSidebar"] [data-testid="stFormSubmitButton"] > button:hover {
        background: var(--color-brand);
        border-color: var(--color-brand);
        color: var(--color-text-inverse);
        box-shadow: 0 6px 16px rgba(217, 119, 87, 0.30);
        transform: translateY(-1px);
    }
    [data-testid="stSidebar"] [data-testid="stForm"] .stButton > button:active,
    [data-testid="stSidebar"] [data-testid="stFormSubmitButton"] > button:active {
        transform: translateY(0);
        box-shadow: var(--shadow-card);
    }

    /* 主区按钮（V3.1：标为已读 / 跑起来等）：与侧边栏按钮一致的拟态触感 */
    [data-testid="stMain"] .stButton > button {
        border: 1px solid var(--color-border-hairline);
        border-radius: var(--radius-md);
        background: var(--color-bg-surface);
        color: var(--color-text-primary);
        font-weight: 500;
        transition: all 0.15s ease;
        padding: var(--space-2) var(--space-3);
        box-shadow: var(--shadow-button-rest);
    }
    [data-testid="stMain"] .stButton > button:hover {
        box-shadow: var(--shadow-card);
        transform: translateY(-1px);
    }
    [data-testid="stMain"] .stButton > button:active {
        box-shadow: var(--shadow-inset);
        transform: translateY(0);
    }

    /* ============================================================
     * Tab 导航（R8-T4）：底部 3px 品牌色条 + 字重区分
     * ============================================================ */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: var(--space-4);
        border-bottom: 1px solid var(--color-border-hairline) !important;
    }
    [data-testid="stTabs"] button[data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
        border-bottom: 3px solid transparent !important;
        border-radius: 0 !important;
        padding: var(--space-2) var(--space-3) calc(var(--space-2) + 1px) var(--space-3);
        font-size: var(--fs-body);
        font-weight: 500;
        color: var(--color-text-muted) !important;
        box-shadow: none !important;
        margin-bottom: -1px;  /* 让底部线和 tab-list border-bottom 对齐 */
        transition: color 0.15s ease, border-color 0.15s ease;
    }
    [data-testid="stTabs"] button[data-baseweb="tab"]:hover {
        color: var(--color-text-primary) !important;
        background: transparent !important;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        background: transparent !important;
        color: var(--color-text-primary) !important;
        font-weight: 700 !important;
        border-bottom: 3px solid var(--color-brand) !important;
        box-shadow: none !important;
    }

    /* ============================================================
     * 输入控件（V3.1：rest 凹陷皮肤；V3.2：bg 改 overlay 自适应任何 surface）
     * 控件由"扁平方块"升级到"凹槽 + 内阴影"，跟周围 surface 形成层次
     * 使用 var(--overlay-recess) 而非固定色，让控件在主区 / 侧边栏（已加深）都比所在底色暗一档
     * ============================================================ */
    .stTextInput > div > div,
    .stNumberInput > div > div,
    .stTextArea > div > div,
    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stDateInput > div > div {
        background: var(--overlay-recess) !important;
        border: 1px solid var(--color-border-hairline) !important;
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-inset);
        transition: box-shadow 0.15s ease, border-color 0.15s ease, background 0.15s ease;
    }
    .stTextInput > div > div:hover,
    .stNumberInput > div > div:hover,
    .stTextArea > div > div:hover,
    .stSelectbox > div > div:hover {
        background: rgba(44, 31, 20, 0.07) !important;
    }
    .stTextInput > div > div:focus-within,
    .stNumberInput > div > div:focus-within,
    .stTextArea > div > div:focus-within,
    .stSelectbox > div > div:focus-within {
        border-color: var(--color-brand) !important;
        box-shadow: var(--shadow-inset), 0 0 0 1px var(--color-brand) !important;
        background: var(--color-bg-surface) !important;
    }
    /* 输入框内的 input/textarea/select 元素自身透明，让外层凹槽显出 */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    .stSelectbox [data-baseweb="select"] > div {
        background: transparent !important;
    }

    /* Chat input：底部输入框也走 overlay 凹陷皮肤 */
    [data-testid="stChatInput"] {
        background: transparent;
    }
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] textarea {
        background: var(--overlay-recess) !important;
        border: 1px solid var(--color-border-hairline) !important;
        border-radius: var(--radius-md) !important;
        box-shadow: var(--shadow-inset) !important;
    }
    [data-testid="stChatInput"] textarea {
        box-shadow: none !important;  /* 内层 textarea 不重复内阴影，由外层承担 */
        border: none !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        outline: none !important;
    }
    [data-testid="stChatInput"]:focus-within > div {
        border-color: var(--color-brand) !important;
        box-shadow: var(--shadow-inset), 0 0 0 1px var(--color-brand) !important;
    }

    /* ============================================================
     * Chat message 滚动容器（V3.1：去默认边框，自适应高度）
     * 卡片样式见底部 V3.4.2 段；这里只管滚动容器
     * ============================================================ */
    [data-testid="stTabs"] [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stChatMessage"]) {
        border: none !important;
        height: calc(100vh - 280px) !important;
        min-height: 350px;
    }
    [data-testid="stTabs"] [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stChatMessage"]) > div {
        height: 100% !important;
    }

    /* ============================================================
     * Hero metric hover lift（V3.1：让首屏数字面板可点感更强）
     * ============================================================ */
    .main-header .hero-metric {
        transition: box-shadow 0.2s ease, transform 0.2s ease;
    }
    .main-header .hero-metric:hover {
        box-shadow: var(--shadow-hover);
        transform: translateY(-1px);
    }

    /* ============================================================
     * V3.3 拟态扩展：Streamlit 原生 alert / checkbox / form 接入拟态系统
     * ============================================================ */

    /* 原生 alert（考试倒计时用 st.error/warning/info）→ 拟态卡 */
    [data-testid="stAlert"] {
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--color-border-hairline) !important;
        box-shadow: var(--shadow-card) !important;
        padding: var(--space-2) var(--space-3) !important;
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        margin-bottom: var(--space-2);
    }
    /* 不同 kind 的色调走 severity-rgb，跟主动关怀卡保持一致语言 */
    [data-testid="stAlert"][kind="error"],
    [data-testid="stAlertContentError"] {
        background: rgba(var(--color-severity-high-rgb), 0.10) !important;
        border-color: rgba(var(--color-severity-high-rgb), 0.22) !important;
    }
    [data-testid="stAlert"][kind="warning"],
    [data-testid="stAlertContentWarning"] {
        background: rgba(var(--color-severity-medium-rgb), 0.10) !important;
        border-color: rgba(var(--color-severity-medium-rgb), 0.22) !important;
    }
    [data-testid="stAlert"][kind="info"],
    [data-testid="stAlertContentInfo"] {
        background: rgba(176, 95, 68, 0.06) !important;
        border-color: rgba(176, 95, 68, 0.18) !important;
    }
    [data-testid="stAlert"][kind="success"],
    [data-testid="stAlertContentSuccess"] {
        background: rgba(var(--color-severity-low-rgb), 0.10) !important;
        border-color: rgba(var(--color-severity-low-rgb), 0.22) !important;
    }

    /* Checkbox（待办勾选）→ 加 hover bg + 微抬升触感 */
    [data-testid="stSidebar"] [data-testid="stCheckbox"] {
        padding: var(--space-1) var(--space-2);
        border-radius: var(--radius-sm);
        transition: background 0.15s ease;
    }
    [data-testid="stSidebar"] [data-testid="stCheckbox"]:hover {
        background: rgba(44, 31, 20, 0.04);
    }
    [data-testid="stSidebar"] [data-testid="stCheckbox"] label {
        font-size: var(--fs-body);
        line-height: var(--lh-normal);
    }

    /* Form 容器（"快速记一笔" / "预算设置" 等）→ hairline + 圆角 + 微浮，把表单分成可识别的子区 */
    [data-testid="stSidebar"] [data-testid="stForm"],
    [data-testid="stMain"] [data-testid="stForm"] {
        background: var(--color-bg-surface);
        border: 1px solid var(--color-border-hairline);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-card);
        padding: var(--space-3);
    }

    /* 旅行 / 看板里的 stContainer with border → 同步拟态卡 */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: var(--radius-md);
    }

    /* Plotly chart 容器边缘细化（V3.4.9：加 .class 兜底；testid 在 emotion-cache 下不一定保留） */
    [data-testid="stPlotlyChart"],
    .stPlotlyChart {
        border-radius: var(--radius-md);
        overflow: hidden;
        box-shadow: var(--shadow-card) !important;
        border: 1px solid var(--color-border-hairline) !important;
        background: var(--color-bg-warm) !important;
    }

    /* 旅行 item 行（.travel-item）V3.3 → 升级到 V3.4 见上方 clip-path 缺角版 */
    /* 此处保留空注释以提醒该规则已合并到上方 V3.2 区域；实际样式见上一段 .travel-item */

    /* ============================================================
     * V3.4：侧栏内嵌 alert（考试倒计时）— wash 色 + 软阴影；不复用 V3.3 的磨砂规则
     *
     * V3.3 给主区 stAlert 加了磨砂半透色（rgba severity 0.10）。
     * 但这套色叠在沙底 #E2DCCD 上会被沙色推得"偏暖发糊"，对比度不足。
     * 侧栏走独立 wash：奇数序 #F1E8DC（暖白偏黄），偶数序 #E7DECF（沙底再深一点），
     * 形成"沙底 → 暖白 wash → 暖陶白" 三档梯度，让 4-5 个 alert 排在一起也有节奏。
     * ============================================================ */
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        position: relative;
        background: var(--color-sidebar-alert) !important;
        border: 1px solid rgba(93, 70, 59, 0.22) !important;
        border-radius: var(--radius-md) !important;
        backdrop-filter: none;
        -webkit-backdrop-filter: none;
        box-shadow:
            inset 0 1px 0 rgba(255, 252, 247, 0.70),
            0 2px 4px rgba(44, 31, 20, 0.07),
            0 10px 20px rgba(44, 31, 20, 0.08) !important;
        padding: var(--space-2) var(--space-3) !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"]:nth-of-type(even) {
        background: var(--color-sidebar-alert-2) !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"] [class*="stAlertContainer"] {
        background: transparent !important;
        border: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"],
    [data-testid="stSidebar"] [data-testid="stAlert"] p,
    [data-testid="stSidebar"] [data-testid="stAlert"] span,
    [data-testid="stSidebar"] [data-testid="stAlert"] div {
        color: var(--color-text-primary) !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"] svg {
        color: var(--color-brand-deep) !important;
        fill: var(--color-brand-deep) !important;
    }

    /* V3.4.1：删除 V3.4 误加的 sidebar progress 渐变填充
     * 问题：`[data-baseweb="progress-bar"] div:last-child` 在 BaseWeb 嵌套结构里命中过宽，
     *      会把 track 也一起染上渐变，看起来像 100% 满进度。
     * 回退：依赖 V3.1 的 `> div > div > div > div` 4 级嵌套规则给 fill 上 brand 实色，
     *      track 维持 bg-muted + inset shadow。
     */

    /* V3.4：dataframe / table 接入拟态卡风格（V3.4.7：去 stMain 前缀；V3.4.8：!important；V3.4.9：加 .class 兜底） */
    [data-testid="stDataFrame"],
    [data-testid="stTable"],
    .stDataFrame,
    .stTable {
        overflow: hidden;
        background: var(--color-bg-warm) !important;
        border: 1px solid var(--color-border-hairline) !important;
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-card) !important;
    }

    /* ============================================================
     * V3.4.1：主区 stMetric 拟态卡 — 数据看板的 3 个消费指标 / 旅行预算 metric 都套这层
     * 此前主区 metric 是光秃秃的"label + 大字 + delta"裸文本，跟侧栏 metric 已有的拟态卡视觉断层。
     * V3.4.7 修复：去掉 `[data-testid="stMain"]` 前缀。Streamlit 1.30+ 的主区可能不是 stMain 而是
     *           stMainBlockContainer / 别的 testid，导致这条 selector 完全没命中（截图显示 3 个消费指标
     *           完全无卡边）。改成默认所有 metric 都套这套拟态；侧栏 metric 因 selector specificity 更高
     *           （`stSidebar stMetric` > `stMetric`），自动覆盖回紧凑版（fs-metric value + 更深阴影）。
     * V3.4.8 拟态加固：参照 jj66-ui-refactor 分支范式，给 background / border / box-shadow 三条加
     *           `!important` 防止被 streamlit emotion-cache / BaseWeb 默认样式覆盖；同时给关键三条
     *           复制一份到文件末尾的"拟态兜底块"，确保最晚定义优先级。
     * ============================================================ */
    [data-testid="stMetric"],
    .stMetric {
        background: #FFFFFF !important;
        border: 1px solid var(--color-border-hairline) !important;
        border-radius: var(--radius-md) !important;
        padding: var(--space-3) !important;
        box-shadow:
            inset 0 1px 0 rgba(255, 255, 255, 0.85),
            0 1px 2px rgba(44, 31, 20, 0.08),
            0 8px 18px rgba(44, 31, 20, 0.09) !important;
    }
    [data-testid="stMetricLabel"],
    .stMetricLabel {
        font-size: var(--fs-caption);
        font-weight: 600;
        color: var(--color-text-muted);
        letter-spacing: var(--ls-caps);
        text-transform: uppercase;
    }
    [data-testid="stMetricLabel"] p,
    .stMetricLabel p {
        font-size: var(--fs-caption) !important;
        color: var(--color-text-muted) !important;
        letter-spacing: var(--ls-caps);
        text-transform: uppercase;
    }
    [data-testid="stMetricValue"],
    .stMetricValue {
        font-family: var(--font-display);
        font-variant-numeric: tabular-nums;
        color: var(--color-text-primary);
        letter-spacing: var(--ls-display);
        font-size: 1.72rem !important;
        font-weight: 800;
        line-height: var(--lh-snug);
    }
    [data-testid="stMetricValue"] p,
    .stMetricValue p {
        font-size: 1.72rem !important;
        line-height: var(--lh-snug) !important;
    }
    [data-testid="stMetricDelta"],
    .stMetricDelta {
        font-size: var(--fs-micro) !important;
        color: var(--color-text-muted);
    }
    [data-testid="stMetricDelta"] p,
    .stMetricDelta p {
        font-size: var(--fs-micro) !important;
        line-height: var(--lh-snug) !important;
    }

    /* V3.4.1：数据看板的 #### 消费构成 / 📅 本周课表 / 🏥 7 天健康趋势 / 🗺️ 旅行计划 章节标题
     * 增加 hairline + 微下边距，把 4 个 panel 视觉拉开
     */
    h4 {
        margin-top: var(--space-3);
        margin-bottom: var(--space-2);
        font-family: var(--font-display);
        font-size: var(--fs-display);
        font-weight: 800;
        letter-spacing: var(--ls-display);
        line-height: var(--lh-snug);
        color: var(--color-text-primary);
    }

    /* ============================================================
     * V3.4.2：Chat message 文字背景 / 外围拟态框对齐重做
     *
     * V3.4.1 只对 3 个 testid 内层容器加 transparent，但 Streamlit chat 的实际嵌套
     * 经常多于 3 层（emotion-cache 包了 stMarkdownContainer 外面再多一层 div），
     * 那些中间层带 BaseWeb 默认 surface-2 浅灰底，肉眼上会形成"白外框 + 内浅灰文字框"双层。
     *
     * V3.4.2 改用「全部 descendant transparent + 例外列表」策略，确保只剩外层那一层 surface：
     * - 外层 .stChatMessage 重申 surface card（防止被 emotion-cache 覆盖）
     * - 内部所有 descendant `*` background-color: transparent
     * - 例外保留：code / pre 块（保持代码视觉边界）+ avatar 圆圈（让头像不变成纯透明）
     * ============================================================ */
    .stChatMessage,
    [data-testid="stChatMessage"] {
        border-radius: var(--radius-lg) !important;
        background: var(--color-bg-surface) !important;
        background-color: var(--color-bg-surface) !important;
        border: 1px solid var(--color-border-hairline) !important;
        box-shadow: var(--shadow-card) !important;
        padding: var(--space-3) var(--space-4) !important;
    }
    [data-testid="stChatMessage"] * {
        background: transparent !important;
        background-color: transparent !important;
    }
    /* 例外 1：inline code / 代码块保留浅暖底，避免嵌在文字里看不出来 */
    [data-testid="stChatMessage"] code,
    [data-testid="stChatMessage"] pre,
    [data-testid="stChatMessage"] pre code {
        background: rgba(44, 31, 20, 0.06) !important;
        background-color: rgba(44, 31, 20, 0.06) !important;
        border-radius: var(--radius-sm);
        padding: 0.1rem 0.35rem;
    }
    [data-testid="stChatMessage"] pre {
        padding: var(--space-2) var(--space-3);
    }
    /* 例外 2：avatar 圆圈保留 surface-warm 底，让头像 emoji 有圆形视觉边界 */
    [data-testid="stChatMessage"] [data-testid="stChatMessageAvatarContainer"] > *,
    [data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] {
        background: var(--color-bg-warm) !important;
        background-color: var(--color-bg-warm) !important;
        border: 1px solid var(--color-border-hairline);
    }
</style>
"""


_PWA_META = """
<link rel="manifest" href="/app/static/manifest.json">
<meta name="theme-color" content="#2C1F14">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="apple-touch-icon" href="/app/static/icon.svg">
<script>
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/app/static/sw.js')
        .then(function(reg) { console.log('SW registered:', reg.scope); })
        .catch(function(err) { console.log('SW registration failed:', err); });
}
</script>
"""


def inject_css() -> None:
    """注入主题 CSS。调用时机：st.set_page_config 之后、任何其它渲染之前。"""
    st.markdown(_CSS, unsafe_allow_html=True)


def inject_pwa_meta() -> None:
    """注入 PWA manifest / Service Worker 注册脚本。与 inject_css 同阶段调用。"""
    st.markdown(_PWA_META, unsafe_allow_html=True)

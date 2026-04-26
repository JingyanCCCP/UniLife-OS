from __future__ import annotations

import streamlit as st

_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@500;700;800&family=Source+Serif+4:opsz,wght@8..60,600;8..60,700;8..60,800&display=swap');

:root {
  --bg: #f3efe7;
  --bg-quiet: #ebe3d6;
  --surface: #fffaf4;
  --surface-2: #f8f1e8;
  --surface-3: #e5dccf;
  --sidebar-bg: #d7d0c2;
  --sidebar-surface: #fbf5eb;
  --sidebar-surface-2: #efe6da;
  --text: #251e19;
  --muted: #62584f;
  --faint: #81756a;
  --line: rgba(37, 30, 25, 0.14);
  --line-strong: rgba(37, 30, 25, 0.26);
  --accent: #9a735f;
  --accent-2: #6a5146;
  --accent-soft: rgba(154, 115, 95, 0.14);
  --sage: #7d897c;
  --sage-soft: rgba(125, 137, 124, 0.15);
  --slate: #77838a;
  --clay: #b27c70;
  --clay-soft: rgba(178, 124, 112, 0.14);
  --sand: #b4a07b;
  --sand-soft: rgba(180, 160, 123, 0.16);
  --rose: #b88b82;
  --ink: #2c241f;
  --radius-sm: 5px;
  --radius: 7px;
  --radius-lg: 8px;
  --shadow-card:
    inset 0 1px 0 rgba(255, 252, 247, 0.72),
    0 1px 2px rgba(61, 45, 35, 0.06),
    0 12px 24px rgba(61, 45, 35, 0.08);
  --shadow-soft:
    inset 0 1px 0 rgba(255, 252, 247, 0.62),
    0 8px 18px rgba(61, 45, 35, 0.06);
  --shadow-pressed:
    inset 0 1px 3px rgba(61, 45, 35, 0.10),
    inset 0 -1px 0 rgba(255, 252, 247, 0.40);
  --ease: cubic-bezier(0.16, 1, 0.3, 1);
  --font-body: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei UI", "Segoe UI", system-ui, sans-serif;
  --font-brand: "Microsoft YaHei UI", "Microsoft YaHei", "PingFang SC", "Segoe UI", system-ui, sans-serif;
  --font-display: "Source Serif 4", Georgia, "Times New Roman", "Noto Serif SC", "Songti SC", serif;
  --font-ui: "PingFang SC", "Microsoft YaHei UI", "Segoe UI", system-ui, sans-serif;
  --font-mono: "SF Mono", "Cascadia Mono", ui-monospace, monospace;
}

html,
body,
[class*="css"] {
  font-family: var(--font-body);
}

.stApp,
[data-testid="stAppViewContainer"] {
  color: var(--text);
  background-color: var(--bg) !important;
  background-image:
    linear-gradient(180deg, rgba(255, 250, 244, 0.82), rgba(255, 250, 244, 0) 22rem),
    repeating-linear-gradient(0deg, rgba(37, 30, 25, 0.018) 0, rgba(37, 30, 25, 0.018) 1px, transparent 1px, transparent 6px) !important;
  font-variant-numeric: tabular-nums;
}

.block-container {
  max-width: 1320px;
  padding: 1.35rem 2.25rem 3.5rem;
}

[data-testid="stHeader"] {
  background: rgba(243, 239, 231, 0.94) !important;
  border-bottom: 1px solid var(--line);
}

[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stMainMenu"] button,
[data-testid="stToolbar"] button {
  color: var(--muted) !important;
}

h1,
h2,
h3,
h4,
h5,
h6 {
  color: var(--text);
  font-family: var(--font-ui);
  letter-spacing: 0;
}

p,
li,
small,
label,
span {
  color: inherit;
  font-family: var(--font-body);
  letter-spacing: 0;
}

a {
  color: var(--accent-2);
}

[data-testid="stMarkdownContainer"] a[href^="#"] {
  display: none !important;
}

hr,
[data-testid="stDivider"] {
  border-color: var(--line) !important;
}

.workspace-tabs-shell {
  margin-top: 1rem;
}

.main-header {
  display: grid;
  grid-template-columns: minmax(320px, 1.04fr) minmax(360px, 0.96fr);
  gap: 0.75rem;
  align-items: stretch;
  margin: 0 0 1.25rem;
  padding: 0.68rem;
  background: var(--surface-3);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft);
}

.hero-copy {
  position: relative;
  min-height: 224px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
  padding: 1.38rem 1.45rem;
  background: var(--surface);
  border: 1px solid rgba(37, 30, 25, 0.12);
  border-radius: var(--radius);
  box-shadow: inset 0 1px 0 rgba(255, 252, 247, 0.82);
}

.hero-copy::after {
  content: "";
  position: absolute;
  right: 1.05rem;
  top: 1.05rem;
  width: 4.65rem;
  height: 4.65rem;
  border: 1.05rem solid transparent;
  border-radius: 50%;
  background:
    linear-gradient(var(--surface), var(--surface)) padding-box,
    conic-gradient(from 45deg, var(--clay), var(--sand), var(--sage), var(--slate), var(--rose), var(--clay)) border-box;
  opacity: 0.34;
}

.hero-eyebrow,
.section-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  color: var(--accent-2);
  font-family: var(--font-ui);
  font-size: 0.76rem;
  font-weight: 700;
  text-transform: uppercase;
}

.hero-icon,
.section-icon {
  width: 1.35rem;
  height: 1.35rem;
  display: inline-grid;
  place-items: center;
  color: var(--accent-2);
  background: var(--accent-soft);
  border: 1px solid rgba(106, 81, 70, 0.14);
  border-radius: 999px;
}

.hero-icon svg,
.section-icon svg {
  width: 0.86rem;
  height: 0.86rem;
}

.hero-title {
  margin: 0.58rem 0 0.72rem;
  color: var(--text);
  font-family: var(--font-brand);
  font-size: 3.28rem;
  font-weight: 800;
  line-height: 1.02;
  letter-spacing: 0;
}

.hero-desc {
  max-width: 52ch;
  margin: 0;
  color: var(--muted);
  font-size: 0.98rem;
  line-height: 1.68;
}

.hero-status {
  width: fit-content;
  display: inline-flex;
  align-items: center;
  gap: 0.48rem;
  margin-top: 1rem;
  padding: 0.42rem 0.68rem;
  color: var(--text);
  font-family: var(--font-ui);
  font-size: 0.82rem;
  font-weight: 700;
  background: var(--surface-2);
  border: 1px solid var(--line);
  border-radius: 999px;
  box-shadow: var(--shadow-pressed);
}

.hero-status-dot {
  width: 0.48rem;
  height: 0.48rem;
  border-radius: 50%;
  background: var(--sand);
}

.hero-status.is-online .hero-status-dot {
  background: var(--sage);
}

.hero-metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0;
  overflow: hidden;
  background: var(--surface);
  border: 1px solid rgba(37, 30, 25, 0.12);
  border-radius: var(--radius);
  box-shadow: inset 0 1px 0 rgba(255, 252, 247, 0.76);
}

.hero-metric {
  min-height: 112px;
  padding: 1.05rem 1.08rem;
  background: rgba(255, 250, 244, 0.52);
  transition: transform 180ms var(--ease), background-color 180ms var(--ease);
}

.hero-metric:nth-child(odd) {
  border-right: 1px solid var(--line);
}

.hero-metric:nth-child(n + 3) {
  border-top: 1px solid var(--line);
}

.hero-metric:hover {
  transform: translateY(-1px);
  background: rgba(248, 241, 232, 0.78);
}

.hero-metric-label,
.hero-metric-note {
  display: block;
  color: var(--muted);
  font-family: var(--font-ui);
  font-size: 0.78rem;
  line-height: 1.42;
}

.hero-metric-value {
  display: block;
  margin: 0.42rem 0 0.24rem;
  color: var(--text);
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 800;
  line-height: 1;
  letter-spacing: 0;
}

.section-heading {
  display: block;
  margin: 1.72rem 0 0.9rem;
}

.section-title {
  margin: 0.32rem 0 0;
  color: var(--text);
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 800;
  line-height: 1.12;
  letter-spacing: 0;
}

.proactive-heading {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: 1rem;
  margin: 1.72rem 0 1rem;
  padding-bottom: 0.58rem;
  border-bottom: 1px solid rgba(154, 115, 95, 0.28);
}

.proactive-heading-left {
  display: inline-flex;
  align-items: center;
  gap: 0.48rem;
  color: var(--accent-2);
  font-family: var(--font-ui);
  font-size: 0.76rem;
  font-weight: 800;
  text-transform: uppercase;
}

.proactive-heading-title {
  color: var(--accent-2);
  font-family: var(--font-ui);
  font-size: 0.82rem;
  font-weight: 800;
}

.alert-card {
  height: 116px;
  display: flex;
  flex-direction: column;
  gap: 0.34rem;
  padding: 0.64rem 1rem 0.82rem;
  color: var(--text);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow-card);
  transition: transform 180ms var(--ease), border-color 180ms var(--ease);
}

.alert-card:hover {
  transform: translateY(-1px);
  border-color: var(--line-strong);
}

.alert-card-head {
  height: 1.05rem;
  display: flex;
  align-items: center;
}

.alert-severity-badge {
  display: inline-flex;
  align-items: center;
  min-height: 1.14rem;
  padding: 0 0.36rem;
  color: var(--text);
  background: rgba(37, 30, 25, 0.08);
  border: 1px solid rgba(37, 30, 25, 0.10);
  border-radius: var(--radius-sm);
  font-size: 0.66rem;
  font-weight: 800;
  line-height: 1;
}

.alert-card-high .alert-severity-badge {
  color: #fffaf4;
  background: #bf675e;
  border-color: rgba(116, 55, 49, 0.18);
}

.alert-card-medium .alert-severity-badge {
  color: var(--text);
  background: #d9c69b;
  border-color: rgba(126, 97, 54, 0.18);
}

.alert-card-low .alert-severity-badge {
  color: var(--text);
  background: #cbd5c6;
  border-color: rgba(82, 99, 79, 0.18);
}

.alert-card-content {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.86rem;
  align-items: start;
  transform: translateY(-0.04rem);
}

.alert-card-high {
  background: #f6e8e3;
  border-color: rgba(178, 124, 112, 0.32);
}

.alert-card-medium {
  background: #f2eadc;
  border-color: rgba(180, 160, 123, 0.34);
}

.alert-card-low {
  background: #f6f3ec;
  border-color: rgba(125, 137, 124, 0.32);
}

.alert-card-icon {
  width: 2.1rem;
  height: 2.1rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--accent-soft);
  border: 1px solid rgba(106, 81, 70, 0.12);
  box-shadow: inset 0 1px 0 rgba(255, 252, 247, 0.70);
}

.alert-card-high .alert-card-icon {
  background: var(--clay-soft);
}

.alert-card-medium .alert-card-icon {
  background: var(--sand-soft);
}

.alert-card-low .alert-card-icon {
  background: var(--sage-soft);
}

.alert-card h4 {
  margin: 0 0 0.38rem;
  color: var(--text);
  font-family: var(--font-display);
  font-size: 1.03rem;
  font-weight: 700;
  line-height: 1.18;
  letter-spacing: 0;
}

.alert-card p {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 0;
  color: var(--muted);
  font-size: 0.88rem;
  line-height: 1.45;
}

.alert-suggestion {
  min-height: 2.7rem;
  margin: 0.56rem 0 0.46rem;
  color: var(--faint);
  font-size: 0.82rem;
  line-height: 1.55;
}

.alert-suggestion.is-empty {
  opacity: 0;
}

.travel-item {
  position: relative;
  margin-bottom: 0.58rem;
  padding: 0.78rem 0.88rem;
  color: var(--text);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: inset 0 1px 0 rgba(255, 252, 247, 0.64);
  clip-path: polygon(0 0, calc(100% - 0.72rem) 0, 100% 0.72rem, 100% 100%, 0 100%);
}

.travel-time {
  color: var(--accent-2);
  font-family: var(--font-mono);
  font-size: 0.76rem;
  font-weight: 700;
}

.travel-main {
  margin-top: 0.22rem;
  color: var(--text);
  font-family: var(--font-ui);
  font-weight: 700;
}

.travel-meta {
  margin-top: 0.24rem;
  color: var(--muted);
  font-size: 0.8rem;
}

[data-testid="stSidebar"] {
  background: var(--sidebar-bg) !important;
  background-image:
    linear-gradient(180deg, rgba(255, 250, 244, 0.24), rgba(255, 250, 244, 0)),
    repeating-linear-gradient(0deg, rgba(37, 30, 25, 0.025) 0, rgba(37, 30, 25, 0.025) 1px, transparent 1px, transparent 7px) !important;
  border-right: 1px solid rgba(37, 30, 25, 0.20);
  box-shadow: inset -1px 0 0 rgba(255, 250, 244, 0.52), 14px 0 34px rgba(61, 49, 41, 0.07);
}

[data-testid="stSidebar"] > div:first-child {
  padding: 1.2rem 0.85rem 1.8rem;
}

[data-testid="stSidebar"] .sidebar-brand {
  display: flex;
  align-items: center;
  gap: 0.72rem;
  margin: 0.15rem 0 0.9rem;
}

[data-testid="stSidebar"] .sidebar-brand-icon {
  width: 1.6rem;
  height: 1.6rem;
  display: inline-grid;
  place-items: center;
  color: var(--accent-2);
  background: rgba(255, 250, 244, 0.52);
  border: 1px solid rgba(37, 30, 25, 0.12);
  border-radius: 999px;
  box-shadow: inset 0 1px 0 rgba(255, 252, 247, 0.64);
}

[data-testid="stSidebar"] .sidebar-brand-icon svg {
  width: 0.95rem;
  height: 0.95rem;
}

[data-testid="stSidebar"] .sidebar-brand-title {
  color: var(--text);
  font-family: var(--font-brand);
  font-size: 1.24rem;
  font-weight: 800;
  line-height: 1.08;
  letter-spacing: 0;
}

[data-testid="stSidebar"] .sidebar-brand-subtitle {
  margin-top: 0.32rem;
  color: var(--faint);
  font-size: 0.78rem;
  line-height: 1.35;
}

[data-testid="stSidebar"] h2 {
  color: var(--text);
  font-family: var(--font-display);
  font-size: 1.4rem;
  font-weight: 800;
  line-height: 1.05;
  margin-bottom: 0.22rem;
  letter-spacing: 0;
}

[data-testid="stSidebar"] h3 {
  margin: 0.7rem 0 0.52rem;
  color: var(--text);
  font-family: var(--font-ui);
  font-size: 0.92rem;
  font-weight: 800;
  letter-spacing: 0;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
  color: var(--muted);
}

[data-testid="stSidebar"] strong {
  color: var(--text);
}

[data-testid="stSidebar"] hr {
  margin: 1.08rem 0;
  border-color: rgba(37, 30, 25, 0.15) !important;
  opacity: 1;
}

[data-testid="stSidebar"] [data-testid="stAlert"] {
  color: var(--text) !important;
  background: var(--sidebar-surface-2) !important;
  border: 1px solid rgba(106, 81, 70, 0.20) !important;
  border-radius: var(--radius) !important;
  box-shadow: var(--shadow-soft) !important;
}

[data-testid="stSidebar"] [data-testid="stAlert"] [class*="stAlertContainer"] {
  background: transparent !important;
  border: 0 !important;
}

[data-testid="stSidebar"] [data-testid="stAlert"] *,
[data-testid="stSidebar"] [data-testid="stAlert"] p,
[data-testid="stSidebar"] [data-testid="stAlert"] span,
[data-testid="stSidebar"] [data-testid="stAlert"] div {
  color: var(--text) !important;
}

[data-testid="stSidebar"] [data-testid="stMetric"],
[data-testid="stSidebar"] [data-testid="stExpander"] {
  position: relative;
  background: rgba(255, 250, 244, 0.58) !important;
  border: 1px solid rgba(37, 30, 25, 0.16) !important;
  border-radius: var(--radius) !important;
  box-shadow: var(--shadow-soft) !important;
}

[data-testid="stSidebar"] [data-testid="stMetric"] {
  padding: 0.78rem 0.78rem !important;
}

[data-testid="stSidebar"] [data-testid="stMetric"] * {
  min-width: 0 !important;
  overflow: visible !important;
  white-space: nowrap !important;
  text-overflow: clip !important;
}

[data-testid="stMetric"] {
  padding: 0.86rem 0.92rem !important;
  color: var(--text) !important;
  background: var(--surface) !important;
  border: 1px solid var(--line) !important;
  border-radius: var(--radius) !important;
  box-shadow: var(--shadow-card) !important;
  font-variant-numeric: tabular-nums;
}

[data-testid="stMetricLabel"] p {
  color: var(--muted) !important;
  font-family: var(--font-ui) !important;
  font-size: 0.78rem !important;
  font-weight: 700 !important;
  letter-spacing: 0 !important;
}

[data-testid="stMetricValue"],
[data-testid="stMetricValue"] p {
  color: var(--text) !important;
  font-family: var(--font-display) !important;
  font-size: 1.72rem !important;
  font-weight: 800 !important;
  line-height: 1.12 !important;
  letter-spacing: 0 !important;
}

[data-testid="stSidebar"] [data-testid="stMetricValue"],
[data-testid="stSidebar"] [data-testid="stMetricValue"] p {
  font-size: 1.34rem !important;
}

[data-testid="stMetricDelta"],
[data-testid="stMetricDelta"] p {
  color: var(--faint) !important;
  font-size: 0.68rem !important;
  line-height: 1.25 !important;
}

[data-testid="stExpander"] {
  overflow: hidden;
  background: rgba(255, 250, 244, 0.72) !important;
  border: 1px solid var(--line) !important;
  border-radius: var(--radius) !important;
  box-shadow: var(--shadow-soft) !important;
}

[data-testid="stExpander"] summary {
  font-family: var(--font-ui);
  font-weight: 700;
}

.stButton > button,
[data-testid="stFormSubmitButton"] button {
  min-height: 2.42rem;
  color: var(--text);
  background: var(--surface);
  border: 1px solid var(--line-strong);
  border-radius: var(--radius-sm);
  box-shadow: inset 0 1px 0 rgba(255, 252, 247, 0.72), 0 1px 2px rgba(61, 45, 35, 0.05);
  font-family: var(--font-ui);
  font-weight: 700;
  transition: transform 160ms var(--ease), background-color 160ms var(--ease), border-color 160ms var(--ease);
}

.stButton > button:hover,
[data-testid="stFormSubmitButton"] button:hover {
  color: var(--text);
  background: var(--surface-2);
  border-color: rgba(106, 81, 70, 0.42);
}

.stButton > button:active,
[data-testid="stFormSubmitButton"] button:active {
  transform: scale(0.985);
  box-shadow: var(--shadow-pressed);
}

.stButton > button:focus,
[data-testid="stFormSubmitButton"] button:focus,
textarea:focus,
input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 2px var(--accent-soft) !important;
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
  gap: 0.82rem;
  width: fit-content;
  padding: 0;
  margin: 1.08rem 0 1rem;
  background: transparent;
  border-bottom: 1px solid var(--line);
}

[data-testid="stTabs"] button[data-baseweb="tab"],
[data-testid="stTabs"] [role="tab"] {
  min-height: 2.35rem;
  padding: 0.46rem 0.32rem 0.58rem;
  color: var(--muted);
  background: transparent !important;
  border: 0 !important;
  border-bottom: 2px solid transparent !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  font-family: var(--font-ui);
  font-weight: 700;
  transition: color 160ms var(--ease), border-color 160ms var(--ease);
}

[data-testid="stTabs"] button[data-baseweb="tab"] *,
[data-testid="stTabs"] [role="tab"] * {
  background: transparent !important;
  box-shadow: none !important;
}

[data-testid="stTabs"] button[data-baseweb="tab"]:hover,
[data-testid="stTabs"] [role="tab"]:hover {
  color: var(--text);
}

[data-testid="stTabs"] button[aria-selected="true"],
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  color: var(--text) !important;
  border-bottom-color: var(--accent) !important;
}

[data-testid="stTabs"] button[aria-selected="true"] *,
[data-testid="stTabs"] [role="tab"][aria-selected="true"] * {
  color: var(--text) !important;
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
  display: none;
}

.stChatMessage,
[data-testid="stChatMessage"] {
  background: var(--surface) !important;
  border: 1px solid var(--line) !important;
  border-radius: var(--radius-lg) !important;
  box-shadow: var(--shadow-card) !important;
  padding: 0.85rem 1rem !important;
}

[data-testid="stChatMessage"] * {
  background-color: transparent !important;
}

[data-testid="stChatMessage"] code,
[data-testid="stChatMessage"] pre,
[data-testid="stChatMessage"] pre code {
  background: rgba(37, 30, 25, 0.06) !important;
  border-radius: var(--radius-sm) !important;
  font-family: var(--font-mono) !important;
}

[data-testid="stChatMessageContent"] p {
  color: var(--text);
  line-height: 1.72;
}

[data-testid="stChatInput"] textarea {
  min-height: 3rem !important;
  color: var(--text) !important;
  background: var(--surface) !important;
  border: 1px solid var(--line-strong) !important;
  border-radius: var(--radius) !important;
  font-family: var(--font-body) !important;
}

[data-testid="stChatInput"] textarea::placeholder {
  color: var(--faint) !important;
}

[data-testid="stDataFrame"],
[data-testid="stTable"],
[data-testid="stPlotlyChart"] {
  overflow: hidden;
  background: rgba(255, 250, 244, 0.88) !important;
  border: 1px solid var(--line) !important;
  border-radius: var(--radius) !important;
  box-shadow: var(--shadow-card) !important;
}

[data-testid="stDataFrame"] * {
  color: var(--text);
  font-family: var(--font-ui);
}

[data-testid="stPlotlyChart"] {
  padding: 0.35rem;
}

[data-testid="stAlert"] {
  color: var(--text) !important;
  background: var(--surface-2) !important;
  border: 1px solid var(--line) !important;
  border-radius: var(--radius) !important;
}

[data-testid="stProgress"] > div {
  background: rgba(255, 250, 244, 0.58) !important;
  border: 1px solid rgba(37, 30, 25, 0.12);
  border-radius: 999px;
  box-shadow: var(--shadow-pressed);
}

[data-testid="stProgress"] > div > div,
[data-testid="stProgress"] [role="progressbar"] {
  background: var(--accent) !important;
  border-radius: 999px;
}

[data-testid="stProgress"] * {
  color: transparent !important;
  font-weight: 700 !important;
}

.sidebar-progress-note {
  margin: 0.24rem 0 0.72rem;
  color: var(--muted);
  font-family: var(--font-ui);
  font-size: 0.78rem;
  font-weight: 700;
  line-height: 1.25;
}

[data-testid="stCheckbox"] label,
[data-testid="stSelectbox"] label,
[data-testid="stNumberInput"] label,
[data-testid="stTextInput"] label,
[data-testid="stFileUploader"] label {
  color: var(--muted) !important;
  font-family: var(--font-ui) !important;
  font-weight: 700;
}

[data-baseweb="input"],
[data-baseweb="select"] > div,
textarea {
  color: var(--text) !important;
  background: var(--surface) !important;
  border-color: var(--line-strong) !important;
  border-radius: var(--radius-sm) !important;
  font-family: var(--font-body) !important;
}

[data-baseweb="popover"],
[data-baseweb="menu"] {
  color: var(--text) !important;
  background: var(--surface) !important;
}

[role="option"] {
  color: var(--text) !important;
  font-family: var(--font-ui) !important;
}

[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] * {
  color: var(--faint) !important;
  font-family: var(--font-ui) !important;
}

code,
pre {
  color: var(--text) !important;
  background: #efe5d8 !important;
  border-radius: var(--radius-sm) !important;
  font-family: var(--font-mono) !important;
}

h4 {
  margin: 1rem 0 0.58rem;
  color: var(--text);
  font-family: var(--font-display);
  font-size: 1.45rem;
  font-weight: 800;
  line-height: 1.16;
  letter-spacing: 0;
}

[data-testid="stTabs"] [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stChatMessage"]) {
  height: calc(100vh - 330px) !important;
  min-height: 390px;
  padding: 0.15rem;
  border: 1px solid var(--line) !important;
  border-radius: var(--radius-lg);
  background: rgba(255, 250, 244, 0.36);
}

[data-testid="stTabs"] [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stChatMessage"]) > div {
  height: 100% !important;
}

@media (max-width: 900px) {
  .block-container {
    padding: 1rem 1rem 2.4rem;
  }

  .main-header {
    grid-template-columns: 1fr;
  }

  .hero-copy {
    min-height: 188px;
  }

  .hero-title {
    font-size: 2.35rem;
  }

  .hero-metrics {
    grid-template-columns: 1fr;
  }

  .hero-metric:nth-child(odd) {
    border-right: 0;
  }

  .hero-metric:nth-child(n + 2) {
    border-top: 1px solid var(--line);
  }

  .alert-card {
    height: auto;
    min-height: 132px;
  }
}
</style>"""

_PWA_META = """
<link rel="manifest" href="/app/static/manifest.json">
<meta name="theme-color" content="#f3efe7">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
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
    st.markdown(_CSS, unsafe_allow_html=True)


def inject_pwa_meta() -> None:
    st.markdown(_PWA_META, unsafe_allow_html=True)

from __future__ import annotations

import streamlit as st

_CSS = """<style>
:root {
  --bg: #F5F0E6;
  --bg-deep: #EDE5D8;
  --surface: #FAF7F0;
  --surface-2: #F3EBDD;
  --surface-3: #EDE5D8;
  --sidebar-bg: #EDE5D8;
  --sidebar-surface: #FAF7F0;
  --sidebar-surface-2: #F3EBDD;
  --sidebar-muted: #887A6B;
  --sidebar-line: rgba(139, 90, 43, 0.16);
  --sidebar-alert: #FAF7F0;
  --sidebar-alert-2: #F3EBDD;
  --title: #332A1F;
  --text: #554A3F;
  --muted: #887A6B;
  --disabled: #BBB0A3;
  --faint: #BBB0A3;
  --line: rgba(139, 90, 43, 0.13);
  --line-strong: rgba(139, 90, 43, 0.24);
  --accent: #8B5A2B;
  --accent-2: #70451F;
  --accent-soft: rgba(139, 90, 43, 0.12);
  --danger: #C4554B;
  --danger-soft: rgba(196, 85, 75, 0.12);
  --success: #5B8C5A;
  --success-soft: rgba(91, 140, 90, 0.14);
  --warn: #C49A4B;
  --warn-soft: rgba(196, 154, 75, 0.16);
  --ink: #332A1F;
  --radius-sm: 8px;
  --radius: 8px;
  --radius-lg: 8px;
  --shadow: 0 2px 8px rgba(0, 0, 0, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.8);
  --shadow-pressed: inset 2px 2px 6px rgba(139, 90, 43, 0.12), inset -2px -2px 6px rgba(255, 255, 255, 0.72);
  --ease: cubic-bezier(0.16, 1, 0.3, 1);
  --font-body: "SF Pro Text", "PingFang SC", "Microsoft YaHei UI", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-display: "Didot", "Bodoni 72", "Playfair Display", "Avenir Next", "Georgia", "PingFang SC", "Microsoft YaHei UI", serif;
  --font-heading: "Avenir Next", "Geist Sans", "SF Pro Display", "PingFang SC", "Microsoft YaHei UI", sans-serif;
  --font-ui: "SF Pro Display", "Geist Sans", "PingFang SC", "Microsoft YaHei UI", sans-serif;
  --font-mono: "Geist Mono", "SF Mono", "JetBrains Mono", "Cascadia Mono", ui-monospace, monospace;
}

html,
body,
[class*="css"] {
  font-family: var(--font-body);
}

.stApp {
  color: var(--text);
  background: var(--bg);
}

.stApp::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background-image:
    radial-gradient(circle at 20% 20%, rgba(139, 90, 43, 0.05) 0 1px, transparent 1px),
    repeating-linear-gradient(0deg, rgba(51,42,31,0.018) 0, rgba(51,42,31,0.018) 1px, transparent 1px, transparent 5px);
  background-size: 7px 7px, auto;
  opacity: 0.05;
  z-index: 0;
}

.block-container {
  max-width: 1320px;
  padding: 2rem 2rem 3.6rem;
}

.workspace-tabs-shell {
  margin-top: 1rem;
}

[data-testid="stHeader"] {
  background: rgba(245, 240, 230, 0.94) !important;
  border-bottom: 0;
}

[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stMainMenu"] button,
[data-testid="stToolbar"] button {
  color: var(--muted) !important;
}

h1, h2, h3, h4, h5, h6 {
  color: var(--title);
  font-family: var(--font-heading);
  letter-spacing: 0;
}

p, li, small, label, span {
  color: inherit;
  font-family: var(--font-body);
}

a {
  color: var(--accent-2);
}

hr {
  margin: 1.45rem 0;
  border-color: rgba(139, 90, 43, 0.18) !important;
}

.main-header {
  display: grid;
  grid-template-columns: minmax(320px, 1.04fr) minmax(360px, 0.96fr);
  gap: 1rem;
  align-items: stretch;
  margin: 0 0 2rem;
  padding: 0;
  color: var(--text);
  background: transparent;
  border: 0;
  border-radius: var(--radius-lg);
  box-shadow: none;
}

.hero-copy {
  position: relative;
  min-height: 232px;
  padding: 2rem;
  border-radius: var(--radius);
  background: var(--surface);
  border: 0;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.hero-copy::after {
  content: "";
  position: absolute;
  right: 1.05rem;
  top: 1.05rem;
  width: 4.75rem;
  height: 4.75rem;
  border-radius: 50%;
  background:
    conic-gradient(from 90deg, #8e6a5a, #b09a76, #73847e, #6f7d73, #827983, #8e6a5a);
  opacity: 0.3;
}

.hero-kicker,
.section-heading span {
  color: var(--accent);
  font-family: var(--font-display);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.26em;
  text-transform: uppercase;
}

.hero-copy h1 {
  margin: 0.68rem 0 0.74rem;
  color: var(--title);
  font-size: clamp(3.2rem, 5.2vw, 5.6rem);
  font-family: var(--font-display);
  font-weight: 800;
  line-height: 0.92;
  letter-spacing: -0.055em;
}

.hero-copy p {
  max-width: 54ch;
  margin: 0;
  color: var(--text);
  font-size: 0.95rem;
  font-family: var(--font-body);
  line-height: 1.72;
}

.hero-status {
  width: fit-content;
  display: inline-flex;
  align-items: center;
  gap: 0.48rem;
  margin-top: 1rem;
  padding: 0.42rem 0.68rem;
  color: var(--surface);
  font-size: 0.82rem;
  font-family: var(--font-ui);
  font-weight: 700;
  background: var(--accent);
  border: 0;
  border-radius: var(--radius);
  box-shadow: 0 2px 8px rgba(139, 90, 43, 0.22), inset 0 1px 0 rgba(255,255,255,0.24);
}

.hero-status span {
  width: 0.48rem;
  height: 0.48rem;
  border-radius: 50%;
  background: var(--faint);
}

.hero-status.is-online span {
  background: var(--success);
}

.hero-status.is-offline span {
  background: var(--warn);
}

.hero-metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0;
  overflow: hidden;
  background: var(--surface);
  border: 0;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

.hero-metric {
  position: relative;
  min-height: 112px;
  padding: 1.24rem 1.42rem;
  border-radius: 0;
  background: transparent;
  border: 0;
  box-shadow: none;
  transition: transform 220ms var(--ease), background-color 220ms var(--ease), border-color 220ms var(--ease);
}

.hero-metric:nth-child(odd) {
  border-right: 1px solid rgba(139, 90, 43, 0.12);
}

.hero-metric:nth-child(n + 3) {
  border-top: 1px solid rgba(139, 90, 43, 0.12);
}

.hero-metric:hover {
  transform: translateY(-2px);
  background: rgba(139, 90, 43, 0.035);
}

.hero-metric:nth-child(1) {
  background: transparent;
}

.hero-metric:nth-child(2) {
  background: transparent;
}

.hero-metric:nth-child(3) {
  background: transparent;
}

.hero-metric:nth-child(4) {
  background: transparent;
}

.hero-metric span,
.hero-metric small {
  display: block;
  color: var(--muted);
  font-family: var(--font-ui);
  font-size: 0.75rem;
  line-height: 1.45;
}

.hero-metric strong {
  display: block;
  margin: 0.35rem 0 0.26rem;
  color: var(--title);
  font-family: var(--font-display);
  font-size: clamp(3rem, 3.7vw, 3.5rem);
  font-weight: 800;
  line-height: 0.96;
  letter-spacing: -0.045em;
  font-variant-numeric: tabular-nums;
}

.section-heading {
  position: relative;
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 1rem;
  margin: 2rem 0 1.1rem;
  padding-bottom: 0.42rem;
}

.section-heading::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: 0;
  width: 80%;
  height: 1px;
  background: rgba(139, 90, 43, 0.24);
}

.section-heading h2 {
  margin: 0;
  color: var(--title);
  font-family: var(--font-heading);
  font-size: 1rem;
  font-weight: 600;
  letter-spacing: -0.015em;
}

.alert-card-high,
.alert-card-medium,
.alert-card-low {
  position: relative;
  min-height: 124px;
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.78rem;
  padding: 1.05rem;
  padding-top: 2rem;
  margin-bottom: 0.62rem;
  color: var(--text);
  background: var(--surface);
  border: 0;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  transition: transform 220ms var(--ease), border-color 220ms var(--ease), background-color 220ms var(--ease);
}

.alert-card-high::before,
.alert-card-medium::before,
.alert-card-low::before {
  position: absolute;
  left: 1rem;
  top: 0.78rem;
  padding: 0.14rem 0.42rem;
  border-radius: 4px;
  font-family: var(--font-ui);
  font-size: 0.68rem;
  font-weight: 700;
  line-height: 1.3;
}

.alert-card-high:hover,
.alert-card-medium:hover,
.alert-card-low:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.07), inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.alert-card-high {
  background: #FFF0ED;
}

.alert-card-high::before {
  content: "紧急";
  color: var(--surface);
  background: var(--danger);
}

.alert-card-medium {
  background: var(--surface);
}

.alert-card-medium::before {
  content: "警告";
  color: var(--title);
  background: var(--warn-soft);
}

.alert-card-low {
  background: var(--surface);
}

.alert-card-low::before {
  content: "普通";
  color: var(--success);
  background: var(--success-soft);
}

.alert-card-icon {
  width: 2.15rem;
  height: 2.15rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--warn-soft);
  color: var(--accent);
  box-shadow: var(--shadow-pressed);
}

.alert-card-high .alert-card-icon {
  background: var(--danger-soft);
}

.alert-card-medium .alert-card-icon {
  background: var(--warn-soft);
}

.alert-card-low .alert-card-icon {
  background: var(--success-soft);
}

.alert-card-high h4,
.alert-card-medium h4,
.alert-card-low h4 {
  margin: 0 0 0.35rem;
  color: var(--title);
  font-family: var(--font-ui);
  font-size: 0.98rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  line-height: 1.35;
}

.alert-card-high p,
.alert-card-medium p,
.alert-card-low p {
  margin: 0;
  color: var(--text);
  font-family: var(--font-body);
  font-size: 0.88rem;
  line-height: 1.62;
}

.travel-item {
  position: relative;
  margin-bottom: 0.58rem;
  padding: 0.82rem 0.9rem;
  color: var(--text);
  background: var(--surface);
  border: 0;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  clip-path: polygon(0 0, calc(100% - 0.72rem) 0, 100% 0.72rem, 100% 100%, 0 100%);
}

.travel-time {
  color: var(--accent);
  font-family: var(--font-mono);
  font-size: 0.76rem;
  font-weight: 760;
}

.travel-main {
  margin-top: 0.22rem;
  color: var(--text);
  font-family: var(--font-ui);
  font-weight: 760;
  letter-spacing: -0.01em;
}

.travel-meta {
  margin-top: 0.24rem;
  color: var(--muted);
  font-family: var(--font-body);
  font-size: 0.8rem;
}

[data-testid="stSidebar"] {
  background: var(--sidebar-bg) !important;
  width: 270px !important;
  min-width: 270px !important;
  border-right: 0;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.06), inset -1px 0 0 rgba(255, 255, 255, 0.62);
}

[data-testid="stSidebar"] > div:first-child {
  padding: 2rem 1rem 1.8rem;
}

[data-testid="stSidebar"] [data-baseweb="select"] {
  min-width: 100%;
}

[data-testid="stSidebar"] h2 {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.55rem;
  min-height: 1.9rem;
  padding-left: 0;
  color: transparent;
  font-family: var(--font-display);
  font-size: 0;
  font-weight: 760;
  letter-spacing: -0.035em;
  line-height: 0.98;
  margin-bottom: 0.22rem;
}

[data-testid="stSidebar"] h2::before {
  content: "";
  position: static;
  flex: 0 0 auto;
  width: 1.1rem;
  height: 0.78rem;
  background: var(--accent);
  clip-path: polygon(50% 0, 100% 34%, 50% 68%, 0 34%);
  box-shadow: 0 1px 3px rgba(139, 90, 43, 0.24);
}

[data-testid="stSidebar"] h2::after {
  content: "UniLife OS";
  color: var(--title);
  font-family: var(--font-display);
  font-size: 1.42rem;
  font-weight: 760;
  letter-spacing: -0.035em;
}

[data-testid="stSidebar"] h3 {
  margin: 0.7rem 0 0.52rem;
  color: var(--title);
  font-family: var(--font-ui);
  font-size: 0.86rem;
  font-weight: 780;
  letter-spacing: 0.015em;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
  color: var(--sidebar-muted);
  font-family: var(--font-body);
}

[data-testid="stSidebar"] strong {
  color: var(--text);
}

[data-testid="stSidebar"] hr {
  margin: 1.35rem 0;
  border-color: rgba(139, 90, 43, 0.22) !important;
  opacity: 1;
}

[data-testid="stSidebar"] [data-testid="stAlert"] {
  position: relative;
  color: var(--text) !important;
  background: var(--sidebar-alert) !important;
  border: 0 !important;
  border-radius: var(--radius-sm) !important;
  box-shadow: var(--shadow) !important;
}

[data-testid="stSidebar"] [data-testid="stAlert"] [class*="stAlertContainer"] {
  background: transparent !important;
  border: 0 !important;
}

[data-testid="stSidebar"] [data-testid="stAlert"]:nth-of-type(even) {
  background: var(--sidebar-alert-2) !important;
}

[data-testid="stSidebar"] [data-testid="stAlert"] *,
[data-testid="stSidebar"] [data-testid="stAlert"] p,
[data-testid="stSidebar"] [data-testid="stAlert"] span,
[data-testid="stSidebar"] [data-testid="stAlert"] div {
  color: var(--text) !important;
}

[data-testid="stSidebar"] [data-testid="stAlert"] svg {
  color: var(--accent) !important;
  fill: var(--accent) !important;
}

[data-testid="stSidebar"] [data-testid="stAlert"] code {
  color: var(--ink) !important;
  background: rgba(139, 90, 43, 0.08) !important;
  border: 0;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p:has(strong) {
  padding: 0.74rem 0.82rem;
  color: var(--text);
  background: rgba(255, 252, 247, 0.46);
  border: 0;
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow);
}

[data-testid="stSidebar"] [data-testid="stMetric"],
[data-testid="stSidebar"] [data-testid="stExpander"] {
  position: relative;
  background: rgba(255, 252, 247, 0.52);
  border: 0;
  box-shadow: var(--shadow);
}

[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] [data-testid="stFormSubmitButton"] button {
  background: rgba(255, 252, 247, 0.66);
  border: 0;
}

[data-testid="stSidebar"] .stButton > button:hover,
[data-testid="stSidebar"] [data-testid="stFormSubmitButton"] button:hover {
  background: var(--sidebar-surface);
  color: var(--accent);
}

[data-testid="stSidebar"] [data-testid="stProgress"] > div {
  background: rgba(255, 252, 247, 0.62) !important;
  border: 0;
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-pressed);
}

[data-testid="stSidebar"] [data-testid="stProgress"] > div > div,
[data-testid="stSidebar"] [data-testid="stProgress"] [role="progressbar"] {
  background: linear-gradient(90deg, var(--accent), var(--warn)) !important;
  border-radius: var(--radius-sm);
}

[data-testid="stSidebar"] [data-testid="stProgress"] [role="progressbar"] > div:first-child {
  background: rgba(255, 252, 247, 0.72) !important;
}

[data-testid="stSidebar"] [data-testid="stProgress"] [role="progressbar"] > div:last-child {
  background: linear-gradient(90deg, var(--accent), var(--warn)) !important;
}

[data-testid="stSidebar"] [data-baseweb="progress-bar"] div {
  background-color: transparent !important;
}

[data-testid="stSidebar"] [data-baseweb="progress-bar"] div:last-child {
  background-color: var(--accent) !important;
  background-image: linear-gradient(90deg, var(--accent), var(--warn)) !important;
}

[data-testid="stSidebar"] [data-testid="stProgress"] * {
  color: var(--text) !important;
}

[data-testid="stMetric"] {
  padding: 1rem;
  background: var(--surface);
  border: 0;
  border-radius: var(--radius);
  font-variant-numeric: tabular-nums;
  box-shadow: var(--shadow);
}

[data-testid="stMetricLabel"] p {
  color: var(--muted) !important;
  font-family: var(--font-ui) !important;
  font-size: 0.75rem !important;
}

[data-testid="stMetricValue"] {
  color: var(--title);
  font-family: var(--font-display);
  letter-spacing: -0.04em;
}

[data-testid="stSidebar"] [data-testid="stMetricValue"] {
  font-size: 1.5rem !important;
  font-weight: 800 !important;
}

[data-testid="stMetricDelta"] {
  color: var(--faint) !important;
}

[data-testid="stExpander"] {
  overflow: hidden;
  background: var(--surface);
  border: 0;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

[data-testid="stExpander"] summary {
  font-family: var(--font-ui);
  font-weight: 720;
}

.stButton > button,
[data-testid="stFormSubmitButton"] button {
  min-height: 2.42rem;
  color: var(--accent);
  background: var(--surface);
  border: 0;
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow);
  font-family: var(--font-ui);
  font-weight: 700;
  transition: transform 180ms var(--ease), background-color 180ms var(--ease), border-color 180ms var(--ease), opacity 180ms var(--ease);
}

.stButton > button:hover,
[data-testid="stFormSubmitButton"] button:hover {
  color: var(--accent);
  background: var(--surface-2);
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
  gap: 0.34rem;
  width: fit-content;
  padding: 0.28rem;
  margin: 1.1rem 0 1rem;
  background: var(--surface);
  border: 0;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

[data-testid="stTabs"] button[data-baseweb="tab"] {
  min-height: 2.55rem;
  padding: 0.54rem 1.35rem;
  color: var(--muted);
  background: transparent;
  border: 0;
  border-radius: var(--radius-sm);
  font-family: var(--font-ui);
  font-weight: 760;
  transition: background-color 180ms var(--ease), color 180ms var(--ease);
}

[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
  color: var(--accent);
  background: var(--surface-2);
}

[data-testid="stTabs"] button[aria-selected="true"] {
  color: var(--surface) !important;
  background: var(--accent) !important;
  box-shadow: 0 2px 8px rgba(139, 90, 43, 0.24), inset 0 1px 0 rgba(255,255,255,0.22) !important;
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
  display: none;
}

.stChatMessage {
  border: 0;
  border-radius: var(--radius) !important;
  background: var(--surface) !important;
  box-shadow: var(--shadow);
}

[data-testid="stChatMessageContent"] p {
  color: var(--text);
  font-family: var(--font-body);
  line-height: 1.72;
}

[data-testid="stChatInput"] textarea {
  min-height: 3rem !important;
  color: var(--text) !important;
  background: var(--surface) !important;
  border: 0 !important;
  border-radius: var(--radius) !important;
  font-family: var(--font-body) !important;
  box-shadow: var(--shadow-pressed) !important;
}

[data-testid="stChatInput"] textarea::placeholder {
  color: var(--faint) !important;
}

[data-testid="stDataFrame"],
[data-testid="stTable"],
[data-testid="stPlotlyChart"] {
  overflow: hidden;
  background: var(--surface);
  border: 0;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

[data-testid="stDataFrame"] * {
  color: var(--text);
  font-family: var(--font-ui);
}

[data-testid="stPlotlyChart"] {
  padding: 0.35rem;
}

[data-testid="stAlert"] {
  color: var(--text);
  background: var(--surface);
  border: 0;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

[data-testid="stProgress"] > div {
  background: var(--surface-2) !important;
  box-shadow: var(--shadow-pressed);
}

[data-testid="stProgress"] > div > div {
  background: var(--accent) !important;
}

[data-testid="stProgress"] * {
  color: var(--surface) !important;
  font-weight: 720 !important;
}

[data-testid="stCheckbox"] label,
[data-testid="stSelectbox"] label,
[data-testid="stNumberInput"] label,
[data-testid="stTextInput"] label {
  color: var(--muted) !important;
  font-family: var(--font-ui) !important;
  font-weight: 680;
}

[data-baseweb="input"],
[data-baseweb="select"] > div,
textarea {
  color: var(--text) !important;
  background: var(--surface) !important;
  border-color: transparent !important;
  border-radius: var(--radius-sm) !important;
  font-family: var(--font-body) !important;
  box-shadow: var(--shadow-pressed);
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
  font-family: var(--font-ui) !important;
}

code,
pre {
  color: var(--title) !important;
  background: rgba(139, 90, 43, 0.08) !important;
  border-radius: var(--radius-sm) !important;
  font-family: var(--font-mono) !important;
}

[data-testid="stTabs"] [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stChatMessage"]) {
  height: calc(100vh - 330px) !important;
  min-height: 390px;
  padding: 0.15rem;
  border: 0 !important;
  border-radius: var(--radius);
  background: var(--surface);
  box-shadow: var(--shadow-pressed);
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

  .hero-metrics {
    grid-template-columns: 1fr;
  }
}
</style>"""

_PWA_META = """
<link rel="manifest" href="app/static/manifest.json">
<meta name="theme-color" content="#f4efe6">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<link rel="apple-touch-icon" href="app/static/icon.svg">
<script>
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('app/static/sw.js', {scope: '/'})
        .then(function(reg) { console.log('SW registered:', reg.scope); })
        .catch(function(err) { console.log('SW scope limited to static path:', err); });
}
</script>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def inject_pwa_meta() -> None:
    st.markdown(_PWA_META, unsafe_allow_html=True)

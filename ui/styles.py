from __future__ import annotations

import streamlit as st

_CSS = """<style>
:root {
  --bg: #f5f1e9;
  --bg-deep: #e7dfd4;
  --surface: #fffcf7;
  --surface-2: #f7f1e8;
  --surface-3: #ebe1d6;
  --sidebar-bg: #d8d0c3;
  --sidebar-bg-2: #cfc6b8;
  --sidebar-surface: #fbf6ed;
  --sidebar-surface-2: #f1eadf;
  --sidebar-muted: #6d6258;
  --sidebar-line: rgba(33, 27, 23, 0.2);
  --sidebar-alert: #f3e8de;
  --sidebar-alert-2: #e8e5dc;
  --text: #211b17;
  --muted: #62564e;
  --faint: #81746a;
  --line: rgba(33, 27, 23, 0.15);
  --line-strong: rgba(33, 27, 23, 0.27);
  --accent: #8e6a5a;
  --accent-2: #5d463b;
  --accent-soft: rgba(142, 106, 90, 0.13);
  --moss: #6f7d73;
  --moss-soft: rgba(111, 125, 115, 0.12);
  --clay: #a47d6b;
  --clay-soft: rgba(164, 125, 107, 0.12);
  --sand: #b09a76;
  --sand-soft: rgba(176, 154, 118, 0.13);
  --shape-soft: rgba(111, 125, 115, 0.16);
  --shape-warm: rgba(176, 154, 118, 0.18);
  --ink: #2a241f;
  --radius-sm: 6px;
  --radius: 10px;
  --radius-lg: 12px;
  --shadow: 0 18px 48px rgba(66, 45, 30, 0.10);
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
  background:
    radial-gradient(circle at 92% -8%, rgba(111,125,115,0.08), transparent 34rem),
    radial-gradient(circle at 9% 12%, rgba(142,106,90,0.07), transparent 30rem),
    linear-gradient(180deg, rgba(255,252,247,0.72), rgba(255,252,247,0) 18rem),
    var(--bg);
}

.stApp::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background-image:
    repeating-linear-gradient(0deg, rgba(36,24,18,0.018) 0, rgba(36,24,18,0.018) 1px, transparent 1px, transparent 5px);
  opacity: 0.28;
}

.block-container {
  max-width: 1320px;
  padding: 1.35rem 2.35rem 3.6rem;
}

.workspace-tabs-shell {
  margin-top: 1rem;
}

[data-testid="stHeader"] {
  background: rgba(245, 241, 232, 0.96) !important;
  border-bottom: 1px solid var(--line);
}

[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stMainMenu"] button,
[data-testid="stToolbar"] button {
  color: var(--muted) !important;
}

h1, h2, h3, h4, h5, h6 {
  color: var(--text);
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
  margin: 1.4rem 0;
  border-color: var(--line) !important;
}

.main-header {
  display: grid;
  grid-template-columns: minmax(320px, 1.04fr) minmax(360px, 0.96fr);
  gap: 0.85rem;
  align-items: stretch;
  margin: 0 0 1.15rem;
  padding: 0.72rem;
  color: var(--text);
  background: var(--surface-3);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
}

.hero-copy {
  position: relative;
  min-height: 232px;
  padding: 1.35rem 1.45rem;
  border-radius: var(--radius);
  background: var(--surface);
  border: 1px solid var(--line);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.72);
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
  opacity: 0.26;
}

.hero-kicker,
.section-heading span {
  color: var(--accent-2);
  font-family: var(--font-display);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.hero-copy h1 {
  margin: 0.58rem 0 0.62rem;
  color: var(--text);
  font-size: clamp(2.7rem, 5.4vw, 5.55rem);
  font-family: var(--font-display);
  font-weight: 760;
  line-height: 0.9;
  letter-spacing: -0.055em;
}

.hero-copy p {
  max-width: 54ch;
  margin: 0;
  color: var(--muted);
  font-size: 1.02rem;
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
  color: var(--text);
  font-size: 0.82rem;
  font-family: var(--font-ui);
  font-weight: 700;
  background: var(--surface-2);
  border: 1px solid var(--line);
  border-radius: 999px;
}

.hero-status span {
  width: 0.48rem;
  height: 0.48rem;
  border-radius: 50%;
  background: var(--faint);
}

.hero-status.is-online span {
  background: var(--moss);
}

.hero-status.is-offline span {
  background: var(--sand);
}

.hero-metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0;
  overflow: hidden;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.56);
}

.hero-metric {
  position: relative;
  min-height: 112px;
  padding: 1.08rem 1.16rem;
  border-radius: 0;
  background: transparent;
  border: 0;
  box-shadow: none;
  transition: transform 220ms var(--ease), background-color 220ms var(--ease), border-color 220ms var(--ease);
}

.hero-metric:nth-child(odd) {
  border-right: 1px solid var(--line);
}

.hero-metric:nth-child(n + 3) {
  border-top: 1px solid var(--line);
}

.hero-metric:hover {
  transform: translateY(-2px);
  background: rgba(255, 252, 247, 0.62);
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
  font-size: 0.78rem;
  line-height: 1.45;
}

.hero-metric strong {
  display: block;
  margin: 0.48rem 0 0.22rem;
  color: var(--text);
  font-family: var(--font-display);
  font-size: clamp(1.45rem, 2.85vw, 2.22rem);
  font-weight: 700;
  line-height: 0.96;
  letter-spacing: -0.045em;
  font-variant-numeric: tabular-nums;
}

.section-heading {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 1rem;
  margin: 1.55rem 0 0.82rem;
}

.section-heading h2 {
  margin: 0;
  color: var(--text);
  font-family: var(--font-heading);
  font-size: 1.34rem;
  font-weight: 760;
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
  margin-bottom: 0.62rem;
  color: var(--text);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  transition: transform 220ms var(--ease), border-color 220ms var(--ease), background-color 220ms var(--ease);
}

.alert-card-high:hover,
.alert-card-medium:hover,
.alert-card-low:hover {
  transform: translateY(-2px);
  border-color: var(--line-strong);
}

.alert-card-high {
  background: var(--surface);
  border-color: var(--line);
}

.alert-card-medium {
  background: var(--surface);
  border-color: var(--line);
}

.alert-card-low {
  background: var(--surface);
  border-color: var(--line);
}

.alert-card-icon {
  width: 2.15rem;
  height: 2.15rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--accent-soft);
}

.alert-card-high .alert-card-icon {
  background: var(--accent-soft);
}

.alert-card-medium .alert-card-icon {
  background: var(--accent-soft);
}

.alert-card-low .alert-card-icon {
  background: var(--accent-soft);
}

.alert-card-high h4,
.alert-card-medium h4,
.alert-card-low h4 {
  margin: 0 0 0.35rem;
  color: var(--text);
  font-family: var(--font-ui);
  font-size: 0.98rem;
  font-weight: 760;
  letter-spacing: -0.01em;
  line-height: 1.35;
}

.alert-card-high p,
.alert-card-medium p,
.alert-card-low p {
  margin: 0;
  color: var(--muted);
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
  border: 1px solid var(--line);
  border-radius: var(--radius);
  clip-path: polygon(0 0, calc(100% - 0.72rem) 0, 100% 0.72rem, 100% 100%, 0 100%);
}

.travel-time {
  color: var(--accent-2);
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
  border-right: 1px solid var(--sidebar-line);
  box-shadow: inset -1px 0 0 rgba(255, 252, 247, 0.48), 16px 0 36px rgba(61, 49, 41, 0.075);
}

[data-testid="stSidebar"] > div:first-child {
  padding: 1.24rem 0.85rem 1.8rem;
}

[data-testid="stSidebar"] h2 {
  color: var(--text);
  font-family: var(--font-display);
  font-size: 1.42rem;
  font-weight: 760;
  letter-spacing: -0.035em;
  line-height: 0.98;
  margin-bottom: 0.22rem;
}

[data-testid="stSidebar"] h3 {
  margin: 0.7rem 0 0.52rem;
  color: var(--text);
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
  margin: 1.08rem 0;
  border-color: rgba(33, 27, 23, 0.15) !important;
  opacity: 1;
}

[data-testid="stSidebar"] [data-testid="stAlert"] {
  position: relative;
  color: var(--text) !important;
  background: var(--sidebar-alert) !important;
  border: 1px solid rgba(93, 70, 59, 0.22) !important;
  border-radius: var(--radius-sm) !important;
  box-shadow: inset 0 1px 0 rgba(255, 252, 247, 0.66), 0 10px 22px rgba(61, 49, 41, 0.055) !important;
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
  color: var(--accent-2) !important;
  fill: var(--accent-2) !important;
}

[data-testid="stSidebar"] [data-testid="stAlert"] code {
  color: var(--ink) !important;
  background: rgba(255, 252, 247, 0.68) !important;
  border: 1px solid rgba(93, 70, 59, 0.16);
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p:has(strong) {
  padding: 0.74rem 0.82rem;
  color: var(--text);
  background: rgba(255, 252, 247, 0.46);
  border: 1px solid rgba(33, 27, 23, 0.13);
  border-radius: var(--radius-sm);
}

[data-testid="stSidebar"] [data-testid="stMetric"],
[data-testid="stSidebar"] [data-testid="stExpander"] {
  position: relative;
  background: rgba(255, 252, 247, 0.52);
  border-color: rgba(33, 27, 23, 0.16);
  box-shadow: inset 0 1px 0 rgba(255, 252, 247, 0.62), 0 8px 20px rgba(61, 49, 41, 0.04);
}

[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] [data-testid="stFormSubmitButton"] button {
  background: rgba(255, 252, 247, 0.66);
  border-color: rgba(33, 27, 23, 0.18);
}

[data-testid="stSidebar"] .stButton > button:hover,
[data-testid="stSidebar"] [data-testid="stFormSubmitButton"] button:hover {
  background: var(--sidebar-surface);
  border-color: rgba(93, 70, 59, 0.42);
}

[data-testid="stSidebar"] [data-testid="stProgress"] > div {
  background: rgba(255, 252, 247, 0.62) !important;
  border: 1px solid rgba(33, 27, 23, 0.14);
  border-radius: var(--radius-sm);
}

[data-testid="stSidebar"] [data-testid="stProgress"] > div > div,
[data-testid="stSidebar"] [data-testid="stProgress"] [role="progressbar"] {
  background: linear-gradient(90deg, var(--accent), var(--sand)) !important;
  border-radius: var(--radius-sm);
}

[data-testid="stSidebar"] [data-testid="stProgress"] [role="progressbar"] > div:first-child {
  background: rgba(255, 252, 247, 0.72) !important;
}

[data-testid="stSidebar"] [data-testid="stProgress"] [role="progressbar"] > div:last-child {
  background: linear-gradient(90deg, var(--accent), var(--sand)) !important;
}

[data-testid="stSidebar"] [data-baseweb="progress-bar"] div {
  background-color: transparent !important;
}

[data-testid="stSidebar"] [data-baseweb="progress-bar"] div:last-child {
  background-color: var(--accent) !important;
  background-image: linear-gradient(90deg, var(--accent), var(--sand)) !important;
}

[data-testid="stSidebar"] [data-testid="stProgress"] * {
  color: var(--text) !important;
}

[data-testid="stMetric"] {
  padding: 0.86rem 0.92rem;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  font-variant-numeric: tabular-nums;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.62);
}

[data-testid="stMetricLabel"] p {
  color: var(--muted) !important;
  font-family: var(--font-ui) !important;
  font-size: 0.8rem !important;
}

[data-testid="stMetricValue"] {
  color: var(--text);
  font-family: var(--font-display);
  letter-spacing: -0.04em;
}

[data-testid="stMetricDelta"] {
  color: var(--faint) !important;
}

[data-testid="stExpander"] {
  overflow: hidden;
  background: rgba(255,253,248,0.72);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: none;
}

[data-testid="stExpander"] summary {
  font-family: var(--font-ui);
  font-weight: 720;
}

.stButton > button,
[data-testid="stFormSubmitButton"] button {
  min-height: 2.42rem;
  color: var(--text);
  background: var(--surface);
  border: 1px solid var(--line-strong);
  border-radius: var(--radius-sm);
  box-shadow: none;
  font-family: var(--font-ui);
  font-weight: 700;
  transition: transform 180ms var(--ease), background-color 180ms var(--ease), border-color 180ms var(--ease), opacity 180ms var(--ease);
}

.stButton > button:hover,
[data-testid="stFormSubmitButton"] button:hover {
  color: var(--text);
  background: var(--surface);
  border-color: rgba(142, 106, 90, 0.42);
}

.stButton > button:active,
[data-testid="stFormSubmitButton"] button:active {
  transform: scale(0.985);
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
  background: rgba(255, 253, 248, 0.88);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.62);
}

[data-testid="stTabs"] button[data-baseweb="tab"] {
  min-height: 2.55rem;
  padding: 0.54rem 1.35rem;
  color: var(--muted);
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  font-family: var(--font-ui);
  font-weight: 760;
  transition: background-color 180ms var(--ease), color 180ms var(--ease);
}

[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
  color: var(--text);
  background: var(--surface-2);
}

[data-testid="stTabs"] button[aria-selected="true"] {
  color: var(--surface) !important;
  background: var(--ink) !important;
  border-color: var(--ink) !important;
  box-shadow: none !important;
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
  display: none;
}

.stChatMessage {
  border: 1px solid var(--line);
  border-radius: var(--radius-lg) !important;
  background: rgba(255, 253, 248, 0.9) !important;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.56);
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
  background: rgba(255, 253, 248, 0.9);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.58);
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
  border: 1px solid var(--line);
  border-radius: var(--radius);
}

[data-testid="stProgress"] > div {
  background: #e4d8c7 !important;
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
  font-family: var(--font-ui) !important;
}

code,
pre {
  color: var(--text) !important;
  background: #f1e7d9 !important;
  border-radius: var(--radius-sm) !important;
  font-family: var(--font-mono) !important;
}

[data-testid="stTabs"] [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stChatMessage"]) {
  height: calc(100vh - 330px) !important;
  min-height: 390px;
  padding: 0.15rem;
  border: 1px solid var(--line) !important;
  border-radius: var(--radius-lg);
  background: rgba(255,255,255,0.34);
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

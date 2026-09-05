import os
import random
import streamlit as st
from google import genai
from typing import TypedDict, Generator

# ==================== TYPE DEFINITIONS ====================
ProductInfo = TypedDict("ProductInfo", {"scheme": str, "is": str})
CategoryInfo = TypedDict("CategoryInfo", {"icon": str, "items": dict[str, ProductInfo]})


st.set_page_config(
    page_title="Cognivolt AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==================== LUXURY PROFESSIONAL CSS ====================
st.markdown(
    """
<style>
/* ===== CSS CUSTOM PROPERTIES ===== */
:root {
  --ink: #0B0D12;
  --ink-soft: #1A1D26;
  --paper: #FAFAF8;
  --paper-elevated: #FFFFFF;
  --gold: #C8A84A;
  --gold-light: #E8D4A0;
  --gold-dim: #A68B3D;
  --slate: #3A3F4E;
  --slate-muted: #6B7280;
  --line: #E8E6E1;
  --shadow-ambient: rgba(11, 13, 18, 0.04);
  --shadow-key: rgba(11, 13, 18, 0.08);
  --shadow-elevated: rgba(11, 13, 18, 0.12);
  --radius: 16px;
  --radius-sm: 10px;
  --transition-fast: 150ms cubic-bezier(0.2, 0, 0, 1);
  --transition-base: 250ms cubic-bezier(0.2, 0, 0, 1);
  --transition-spring: 400ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

@media (prefers-color-scheme: dark) {
  :root {
    --ink: #F5F5F0;
    --ink-soft: #E8E4DC;
    --paper: #0E1014;
    --paper-elevated: #14181E;
    --gold: #D4B85C;
    --gold-light: #E8D4A0;
    --gold-dim: #B8964A;
    --slate: #A0A8B8;
    --slate-muted: #7A8290;
    --line: #2A2E36;
    --shadow-ambient: rgba(0, 0, 0, 0.3);
    --shadow-key: rgba(0, 0, 0, 0.4);
    --shadow-elevated: rgba(0, 0, 0, 0.5);
  }
}

/* ===== GLOBAL RESET ===== */
* { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
  background: var(--paper) !important;
  color: var(--ink) !important;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#MainMenu, header[data-testid="stHeader"], footer, .stDeployButton { display: none !important; }
[data-testid="stSidebar"] { background: var(--paper-elevated) !important; border-right: 1px solid var(--line) !important; }

/* ===== TYPOGRAPHY ===== */
h1 { font-size: clamp(1.75rem, 3vw, 2.25rem) !important; font-weight: 700 !important; letter-spacing: -0.02em !important; color: var(--ink) !important; margin: 0 0 0.5rem !important; }
h2 { font-size: clamp(1.25rem, 2vw, 1.5rem) !important; font-weight: 600 !important; letter-spacing: -0.01em !important; color: var(--ink) !important; margin: 0 0 0.5rem !important; }
h3 { font-size: 1rem !important; font-weight: 600 !important; color: var(--ink) !important; margin: 0 !important; }
p, .stMarkdown, .stCaption { color: var(--slate) !important; line-height: 1.6 !important; }
.caption { font-size: 0.8125rem !important; color: var(--slate-muted) !important; }

/* ===== NATIVE TABS STYLING ===== */
.stTabs [data-baseweb="tab-list"] {
  gap: 8px;
  background: rgba(250, 250, 248, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  padding: 8px;
  border-radius: 16px;
  border-bottom: none !important;
  margin-bottom: 1.5rem;
}
@media (prefers-color-scheme: dark) {
  .stTabs [data-baseweb="tab-list"] { background: rgba(14, 16, 20, 0.85); }
}

.stTabs [data-baseweb="tab"] {
  padding: 10px 20px;
  border-radius: 12px;
  background: transparent;
  color: var(--slate-muted);
  font-weight: 500;
  font-size: 0.875rem;
  transition: all var(--transition-base);
  white-space: nowrap;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--ink); background: var(--line); }
.stTabs [aria-selected="true"] {
  background: var(--gold) !important;
  color: var(--paper) !important;
}

/* ===== BENTO GRID ===== */
.bento-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  padding: 4px;
}
@media (max-width: 640px) { .bento-grid { grid-template-columns: 1fr; } }

.bento-card {
  background: var(--paper-elevated);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 24px;
  transition: transform var(--transition-spring), box-shadow var(--transition-spring), border-color var(--transition-base);
  box-shadow: var(--shadow-ambient);
  position: relative;
  overflow: hidden;
}
.bento-card::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--gold), var(--gold-light));
  opacity: 0;
  transition: opacity var(--transition-base);
}
.bento-card:hover {
  transform: translateY(-4px) scale(1.01);
  box-shadow: var(--shadow-elevated);
  border-color: var(--gold);
}
.bento-card:hover::before { opacity: 1; }

.bento-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 16px; }
.bento-icon {
  width: 44px; height: 44px;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, var(--gold), var(--gold-dim));
  border-radius: var(--radius-sm);
  color: var(--paper);
  font-size: 1.25rem;
  flex-shrink: 0;
  box-shadow: var(--shadow-key);
}
.bento-badge { font-size: 0.6875rem; font-weight: 600; padding: 4px 10px; background: var(--ink-soft); color: var(--ink); border-radius: 999px; text-transform: uppercase; letter-spacing: 0.05em; }
.bento-title { font-size: 1.0625rem; font-weight: 600; color: var(--ink); margin: 0 0 4px; letter-spacing: -0.01em; }
.bento-count { font-size: 0.8125rem; color: var(--slate-muted); margin: 0 0 16px; }

.bento-preview { display: flex; flex-direction: column; gap: 8px; margin-bottom: 20px; }
.bento-preview-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 12px;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}
.bento-preview-item:hover { border-color: var(--gold); background: var(--paper-elevated); }
.bento-preview-name { font-size: 0.8125rem; font-weight: 500; color: var(--ink); }
.bento-preview-scheme {
  font-size: 0.6875rem; font-weight: 600; padding: 3px 8px; border-radius: 6px;
  text-transform: uppercase; letter-spacing: 0.03em;
}
.scheme-isi { background: #E8F0FE; color: #1A4DB8; }
.scheme-crs { background: #E8F5E9; color: #2E7D32; }
.scheme-fmcs { background: #FFF3E0; color: #E65100; }
.scheme-hallmark { background: #FEF3C7; color: #B45309; }
.scheme-other { background: var(--line); color: var(--slate); }

.bento-cta {
  width: 100%;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  padding: 12px;
  background: transparent;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--slate);
  cursor: pointer;
  transition: all var(--transition-base);
}
.bento-cta:hover { background: var(--gold); border-color: var(--gold); color: var(--paper); }

.category-expanded { animation: expandDown 300ms cubic-bezier(0.2, 0, 0, 1); }
@keyframes expandDown { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: translateY(0); } }

.category-back { display: inline-flex; align-items: center; gap: 6px; padding: 8px 12px; margin-bottom: 16px; background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-sm); font-size: 0.8125rem; font-weight: 500; color: var(--slate); cursor: pointer; transition: all var(--transition-fast); }
.category-back:hover { background: var(--gold); border-color: var(--gold); color: var(--paper); }

.product-list { display: flex; flex-direction: column; gap: 10px; }
.product-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 16px;
  background: var(--paper-elevated);
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}
.product-row:hover { border-color: var(--gold); box-shadow: var(--shadow-key); }
.product-info { display: flex; flex-direction: column; gap: 4px; flex: 1; }
.product-name { font-size: 0.9375rem; font-weight: 500; color: var(--ink); }
.product-meta { display: flex; align-items: center; gap: 10px; font-size: 0.75rem; }
.product-scheme { font-weight: 600; padding: 2px 8px; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.03em; }
.product-is { color: var(--slate-muted); font-family: 'SF Mono', 'Monaco', monospace; }
.product-ask {
  padding: 8px 16px;
  background: var(--gold);
  border: none;
  border-radius: var(--radius-sm);
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--paper);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}
.product-ask:hover { background: var(--gold-dim); transform: translateX(2px); }

/* ===== CHAT INTERFACE ===== */
.chat-container { display: flex; flex-direction: column; height: calc(100vh - 220px); min-height: 500px; }
.chat-messages { flex: 1; overflow-y: auto; padding: 8px 4px 24px; display: flex; flex-direction: column; gap: 16px; }
.chat-message { display: flex; gap: 12px; animation: messageIn 300ms cubic-bezier(0.2, 0, 0, 1); }
@keyframes messageIn { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
.message-avatar { width: 36px; height: 36px; flex-shrink: 0; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1rem; }
.user .message-avatar { background: var(--ink); color: var(--paper); }
.assistant .message-avatar { background: linear-gradient(135deg, var(--gold), var(--gold-dim)); color: var(--paper); }
.message-content { flex: 1; min-width: 0; padding-top: 2px; }
.message-role { font-size: 0.6875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--slate-muted); margin-bottom: 6px; }
.message-text { font-size: 0.9375rem; line-height: 1.7; color: var(--ink); white-space: pre-wrap; word-wrap: break-word; }
.message-text code { background: var(--ink-soft); color: var(--gold); padding: 2px 6px; border-radius: 4px; font-size: 0.8125rem; font-family: 'SF Mono', 'Monaco', monospace; }
.message-text table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 0.8125rem; }
.message-text th, .message-text td { padding: 10px 12px; border: 1px solid var(--line); text-align: left; }
.message-text th { background: var(--ink-soft); font-weight: 600; color: var(--ink); }
.message-text tr:nth-child(even) td { background: var(--paper); }
.streaming-cursor { display: inline-block; width: 8px; height: 1.1em; background: var(--gold); margin-left: 2px; animation: cursorPulse 1s ease-in-out infinite; vertical-align: text-bottom; }
@keyframes cursorPulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
.chat-input-area { padding: 16px 0 0; border-top: 1px solid var(--line); margin-top: auto; }
.chat-input-wrapper { display: flex; gap: 10px; align-items: flex-end; }
.chat-input { flex: 1; min-height: 52px; max-height: 160px; padding: 14px 18px; background: var(--paper-elevated); border: 1px solid var(--line); border-radius: var(--radius); font-size: 0.9375rem; color: var(--ink); resize: none; transition: all var(--transition-fast); font-family: inherit; line-height: 1.5; }
.chat-input:focus { outline: none; border-color: var(--gold); box-shadow: 0 0 0 3px rgba(200, 168, 74, 0.15); }
.chat-input::placeholder { color: var(--slate-muted); }
.chat-send { width: 52px; height: 52px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; background: var(--ink); border: none; border-radius: var(--radius); color: var(--paper); cursor: pointer; transition: all var(--transition-base); }
.chat-send:hover { background: var(--gold); transform: scale(1.02); }
.chat-send:active { transform: scale(0.97); }
.chat-send svg { width: 20px; height: 20px; }

.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 40px 24px; text-align: center; }
.empty-icon { width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, var(--gold), var(--gold-dim)); display: flex; align-items: center; justify-content: center; font-size: 2rem; color: var(--paper); margin-bottom: 24px; box-shadow: var(--shadow-elevated); animation: float 3s ease-in-out infinite; }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
.empty-title { font-size: 1.5rem; font-weight: 600; color: var(--ink); margin-bottom: 8px; }
.empty-desc { font-size: 1rem; color: var(--slate-muted); max-width: 360px; margin-bottom: 32px; }
.prompt-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; width: 100%; max-width: 480px; }
.prompt-card { padding: 16px 20px; background: var(--paper-elevated); border: 1px solid var(--line); border-radius: var(--radius); text-align: left; cursor: pointer; transition: all var(--transition-base); }
.prompt-card:hover { border-color: var(--gold); box-shadow: var(--shadow-key); transform: translateY(-2px); }
.prompt-card-icon { width: 36px; height: 36px; border-radius: var(--radius-sm); background: var(--ink-soft); display: flex; align-items: center; justify-content: center; color: var(--ink); font-size: 1rem; margin-bottom: 10px; }
.prompt-card-title { font-size: 0.875rem; font-weight: 500; color: var(--ink); margin: 0; }

/* ===== CHECKLISTS ===== */
.checklist-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 20px; }
.checklist-card { background: var(--paper-elevated); border: 1px solid var(--line); border-radius: var(--radius); padding: 24px; transition: all var(--transition-base); }
.checklist-card:hover { border-color: var(--gold); box-shadow: var(--shadow-key); }
.checklist-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 20px; }
.checklist-title { font-size: 1.0625rem; font-weight: 600; color: var(--ink); margin: 0; }
.progress-ring { width: 48px; height: 48px; flex-shrink: 0; }
.checklist-progress { font-size: 0.75rem; font-weight: 600; color: var(--slate-muted); text-align: right; margin-top: 4px; }
.checklist-items { display: flex; flex-direction: column; gap: 10px; }
.checklist-item { display: flex; align-items: flex-start; gap: 12px; padding: 12px; background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-sm); transition: all var(--transition-fast); cursor: pointer; }
.checklist-item:hover { border-color: var(--gold); background: var(--paper-elevated); }
.checklist-item.completed .check-custom { background: var(--gold); border-color: var(--gold); }
.checklist-item.completed .check-label { color: var(--slate-muted); text-decoration: line-through; }
.check-custom { width: 22px; height: 22px; flex-shrink: 0; border: 2px solid var(--line); border-radius: 6px; display: flex; align-items: center; justify-content: center; transition: all var(--transition-spring); margin-top: 2px; }
.check-custom::after { content: "✓"; font-size: 0.75rem; font-weight: 700; color: var(--paper); opacity: 0; transform: scale(0.5); transition: all var(--transition-spring); }
.checklist-item.completed .check-custom::after { opacity: 1; transform: scale(1); }
.check-label { flex: 1; font-size: 0.875rem; line-height: 1.5; color: var(--ink); min-width: 0; }

/* ===== FEE CALCULATOR ===== */
.calculator-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; align-items: start; }
@media (max-width: 900px) { .calculator-grid { grid-template-columns: 1fr; } }
.calc-input-card { background: var(--paper-elevated); border: 1px solid var(--line); border-radius: var(--radius); padding: 24px; }
.calc-field { margin-bottom: 20px; }
.calc-label { display: block; font-size: 0.8125rem; font-weight: 500; color: var(--slate); margin-bottom: 8px; }
.calc-select, .calc-input { width: 100%; padding: 12px 14px; background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-sm); font-size: 0.9375rem; color: var(--ink); font-family: inherit; transition: all var(--transition-fast); }
.calc-select:focus, .calc-input:focus { outline: none; border-color: var(--gold); box-shadow: 0 0 0 3px rgba(200, 168, 74, 0.15); }
.calc-checkboxes { display: flex; flex-direction: column; gap: 10px; }
.calc-checkbox { display: flex; align-items: center; gap: 10px; padding: 10px 12px; background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-sm); cursor: pointer; transition: all var(--transition-fast); }
.calc-checkbox:hover { border-color: var(--gold); }
.calc-checkbox input { width: 20px; height: 20px; accent-color: var(--gold); cursor: pointer; }
.calc-checkbox label { font-size: 0.875rem; color: var(--ink); cursor: pointer; }
.calc-result-card { background: var(--paper-elevated); border: 1px solid var(--line); border-radius: var(--radius); padding: 24px; position: sticky; top: 100px; }
.calc-result-title { font-size: 1.0625rem; font-weight: 600; color: var(--ink); margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
.result-table { width: 100%; border-collapse: collapse; }
.result-table td { padding: 14px 16px; border-bottom: 1px solid var(--line); font-size: 0.9375rem; }
.result-table tr:last-child td { border-bottom: none; }
.result-label { color: var(--slate); }
.result-value { font-weight: 600; color: var(--ink); text-align: right; font-variant-numeric: tabular-nums; font-family: 'SF Mono', 'Monaco', monospace; }
.result-row-total { background: var(--ink-soft); }
.result-row-total .result-label { font-weight: 600; color: var(--ink); }
.result-row-total .result-value { color: var(--gold); font-size: 1.125rem; }
.calc-note { margin-top: 20px; padding: 14px; background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-sm); font-size: 0.8125rem; color: var(--slate-muted); line-height: 1.6; }

/* ===== SIDEBAR ===== */
.sidebar-section { padding: 16px 0; border-bottom: 1px solid var(--line); }
.sidebar-title { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--slate-muted); margin: 0 0 12px; padding: 0 4px; }
.sidebar-btn { width: 100%; display: flex; align-items: center; gap: 10px; padding: 12px 14px; background: transparent; border: 1px solid var(--line); border-radius: var(--radius-sm); font-size: 0.875rem; color: var(--slate); cursor: pointer; transition: all var(--transition-base); text-align: left; }
.sidebar-btn:hover { background: var(--gold); border-color: var(--gold); color: var(--paper); }
.sidebar-divider { height: 1px; background: var(--line); margin: 16px 0; }

/* ===== LUXURY CHECKBOX STYLING ===== */
.stCheckbox > label > div:first-child { display: none !important; }
.stCheckbox label {
  display: flex !important;
  align-items: flex-start !important;
  gap: 12px !important;
  padding: 12px !important;
  background: var(--paper) !important;
  border: 1px solid var(--line) !important;
  border-radius: var(--radius-sm) !important;
  transition: all var(--transition-fast) !important;
  cursor: pointer !important;
}
.stCheckbox label:hover { border-color: var(--gold) !important; background: var(--paper-elevated) !important; }
.stCheckbox label::before {
  content: "" !important;
  width: 22px !important; height: 22px !important;
  flex-shrink: 0 !important;
  border: 2px solid var(--line) !important;
  border-radius: 6px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  transition: all var(--transition-spring) !important;
  margin-top: 2px !important;
}
.stCheckbox input:checked + div + span::before {
  background: var(--gold) !important;
  border-color: var(--gold) !important;
}
.stCheckbox input:checked + div + span::after {
  content: "✓" !important;
  font-size: 0.75rem !important;
  font-weight: 700 !important;
  color: var(--paper) !important;
  opacity: 1 !important;
  transform: scale(1) !important;
}
.stCheckbox input:not(:checked) + div + span::after {
  content: "✓" !important;
  font-size: 0.75rem !important;
  font-weight: 700 !important;
  color: var(--paper) !important;
  opacity: 0 !important;
  transform: scale(0.5) !important;
}
.stCheckbox label > span { flex: 1 !important; font-size: 0.875rem !important; line-height: 1.5 !important; color: var(--ink) !important; min-width: 0 !important; }
.stCheckbox input:checked + div + span > span { color: var(--slate-muted) !important; text-decoration: line-through !important; }

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--line); border-radius: 4px; border: 2px solid var(--paper); }
::-webkit-scrollbar-thumb:hover { background: var(--slate-muted); }
@media (prefers-color-scheme: dark) { ::-webkit-scrollbar-thumb { border-color: var(--paper); } }

/* ===== SELECTBOX STYLING ===== */
.stSelectbox > div > div { background: var(--paper) !important; border: 1px solid var(--line) !important; border-radius: var(--radius-sm) !important; }
.stSelectbox > div > div:focus-within { border-color: var(--gold) !important; box-shadow: 0 0 0 3px rgba(200, 168, 74, 0.15) !important; }
.stSelectbox label { color: var(--slate) !important; font-size: 0.8125rem !important; font-weight: 500 !important; }

/* ===== NUMBER INPUT ===== */
.stNumberInput > div > div > input { background: var(--paper) !important; border: 1px solid var(--line) !important; border-radius: var(--radius-sm) !important; color: var(--ink) !important; }
.stNumberInput > div > div > input:focus { border-color: var(--gold) !important; box-shadow: 0 0 0 3px rgba(200, 168, 74, 0.15) !important; }
.stNumberInput label { color: var(--slate) !important; font-size: 0.8125rem !important; font-weight: 500 !important; }

/* ===== BUTTON OVERRIDES ===== */
.stButton > button {
  background: var(--ink) !important; color: var(--paper) !important;
  border: none !important; border-radius: var(--radius-sm) !important;
  padding: 10px 20px !important; font-size: 0.875rem !important; font-weight: 500 !important;
  transition: all var(--transition-base) !important;
}
.stButton > button:hover { background: var(--gold) !important; transform: translateY(-1px) !important; }
.stButton > button:active { transform: scale(0.98) !important; }
.stButton > button[kind="secondary"] { background: transparent !important; color: var(--slate) !important; border: 1px solid var(--line) !important; }
.stButton > button[kind="secondary"]:hover { background: var(--gold) !important; border-color: var(--gold) !important; color: var(--paper) !important; }

/* ===== EXPANDER ===== */
.streamlit-expanderHeader { background: var(--paper-elevated) !important; border: 1px solid var(--line) !important; border-radius: var(--radius-sm) !important; font-weight: 500 !important; color: var(--ink) !important; padding: 14px 16px !important; }
.streamlit-expanderContent { background: var(--paper) !important; border: 1px solid var(--line) !important; border-top: none !important; border-radius: 0 0 var(--radius-sm) var(--radius-sm) !important; padding: 16px !important; }

/* ===== ALERT/INFO BOXES ===== */
.stAlert { border-radius: var(--radius-sm) !important; border: 1px solid var(--line) !important; background: var(--paper-elevated) !important; }
.stInfo { border-left: 3px solid var(--gold) !important; }

/* ===== TABLE ===== */
.stTable { border-radius: var(--radius-sm) !important; overflow: hidden; border: 1px solid var(--line) !important; }
.stTable th { background: var(--ink-soft) !important; color: var(--ink) !important; font-weight: 600 !important; padding: 12px 16px !important; }
.stTable td { padding: 12px 16px !important; border: 1px solid var(--line) !important; color: var(--ink) !important; }
.stTable tr:nth-child(even) td { background: var(--paper) !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ==================== CONSTANTS ====================
BIS_CONTEXT = """You are Cognivolt AI, a specialized assistant ONLY for BIS (Bureau of Indian Standards) certification and Indian Standards topics. Provide thorough, well-explained answers — include context, practical steps, and examples where helpful, not just a one-line answer.

LANGUAGE: Detect the language the user is asking in, and respond in that same language (e.g. Hindi, Telugu, Tamil, or any other Indian language), even though the reference information below is written in English. Translate the relevant facts naturally rather than answering in English by default.

PRODUCT-TO-STANDARD RECOMMENDATIONS: If a user describes a product they make, sell, or import (e.g. "I manufacture LED bulbs" or "I import electric kettles"), identify which certification scheme applies (ISI Mark, CRS, or FMCS) and which specific IS standard from the reference information is relevant, if one is listed. If no specific standard in the reference information matches, say so honestly and suggest checking the BIS "Know Your Standard" tool on bis.gov.in rather than guessing a standard number.

Treat the reference information below as your source of truth for specific facts, standard numbers, and figures — don't contradict it. You may draw on general knowledge ONLY when it is directly about India's regulatory, certification, or standards landscape, to explain concepts more fully.

ABOUT-THE-APP QUESTIONS: Questions about Cognivolt AI itself — what it is, how it works, what technology/model it uses, its accuracy, its limitations, or its purpose — ARE in scope and should be answered directly and honestly using the information below, even though they're not about BIS standards specifically.

STRICT SCOPE RULE: If a question is not about BIS, Indian Standards, certification, or closely related regulatory/compliance topics — including general knowledge, other countries, unrelated technology, personal advice, entertainment, math, coding, or anything outside this domain — do NOT attempt to answer it, even partially. Respond only with: "I'm built specifically to help with BIS and Indian Standards questions, so I can't help with that — but feel free to ask me about certification, standards, or compliance." Do not add anything else when declining.

Reference information:

1. About BIS: The Bureau of Indian Standards (BIS) is India's National Standards Body, responsible for standardisation, marking, and quality certification of goods. Originally established as the Indian Standards Institution (ISI) on January 7, 1947, it was formally reconstituted as BIS under the BIS Act 1986 (effective April 1, 1987) and now operates under the BIS Act 2016. It functions under the Ministry of Consumer Affairs, Food & Public Distribution, headquartered in New Delhi with 5 regional offices.

2. BIS Certification: An official mark proving a product meets Indian Standards for quality, performance, and safety. Required before many goods can be legally sold, manufactured, or imported into India. Main schemes:
   - ISI Mark Scheme (Scheme-I): industrial/consumer goods (cement, steel, LPG cylinders, electrical appliances) — requires factory inspection.
   - Compulsory Registration Scheme (CRS): electronics and IT products (mobile phones, laptops, LED TVs, Bluetooth devices like speakers/headphones/smartwatches) — based on self-declaration and lab testing.
   - Foreign Manufacturers Certification Scheme (FMCS): for imported products, requires an Indian representative.
   Over 300 product categories require mandatory BIS certification under government Quality Control Orders (QCOs).

3. How to apply for an ISI mark: Identify the applicable Indian Standard (IS code) for your product, get preliminary testing done at a BIS-recognized lab, register and apply through the BIS Manak Online Portal (manakonline.in) with required documents (business proof, factory layout, quality control manual, test reports, raw material/supplier details) and fees, undergo a factory inspection, and receive the license upon approval.

4. License validity: As of a February 2026 BIS regulation update, a Standard Mark license is now valid for up to 5 years on first grant, renewable for further 5-year terms with annual fee payment — a significant increase from the earlier 1-2 year validity period.

5. Fee concessions for MSMEs: BIS offers concessions on marking fees — 80% for Micro Scale units and Startups, 50% for Small Scale, and 20% for Medium Scale enterprises. An additional 10% concession applies to Women Entrepreneurs and enterprises located in North-East India.

6. Hallmarking (gold/silver): BIS's certification confirming precious metal purity. Since the HUID (Hallmark Unique Identification) system was introduced on July 1, 2021, a valid hallmark consists of exactly 3 marks: the BIS logo, the purity/fineness grade (e.g. 916 for 22K gold, 750 for 18K, 585 for 14K), and a unique 6-digit alphanumeric HUID code. Older pre-2021 items may show additional separate assaying-centre and jeweller marks — that 5-mark format is no longer used for new hallmarks.

7. Helmet standards: Two-wheeler helmets must comply with IS 4151:2015, covering impact absorption, penetration resistance, and chin strap/retention strength. Related: IS 2925:1984 (industrial safety helmets), IS 2745:1983 (firefighter helmets).

8. LPG cylinder standards: IS 3196 (Part 1):2006 covers welded steel LPG cylinders above 5-litre capacity; IS 7142 covers smaller cylinders under 5 litres; IS 8737 covers valve fittings for cylinders above 5-litre capacity, requiring impact, pneumatic, torque, and hydrostatic testing.

9. Toy safety standards: Under the Toys (Quality Control) Order, IS 9873 covers mechanical/physical safety (Part 1), flammability (Part 2), and chemical safety restricting heavy metals like lead, mercury, and cadmium (Parts 3 & 9).

10. Food, water & infant product standards: IS 14543 (packaged drinking water), IS 13428 (packaged natural mineral water), IS 1165 (milk powder), IS 14433 (infant milk substitutes), IS 4984 (HDPE pipes for potable water).

11. PVC material standards: IS 10151 (PVC for food/pharma/drinking water contact, limiting residual vinyl chloride monomer), IS 4985 (UPVC pipes for water supply), IS 15778 (CPVC pipes for hot/cold water), IS 6719 (PVC soles and heels for footwear), IS 13592 (UPVC soil/waste pipes), IS 9537 (PVC electrical conduits).

12. Stainless steel standards: IS 6911 (plate/sheet/strip), IS 1570 (grade classification, e.g. 304, 316), IS 3444 (bars and flats), IS 7283 (tubes), IS 6529 (wire), IS 6603 (forgings).

13. Automotive component standards: IS 15633 (tubeless tyres for passenger cars), IS 15636 (tyres for trucks/commercial vehicles), IS 2573 (brake linings), IS 2553 Part 1 (safety glass for windscreens/windows).

14. Testing laboratories: Product testing for certification must be done at a BIS-recognized laboratory. Manufacturers can find the official, current list of recognized labs for their specific product/IS code using BIS's own "Testing Facilities" search tool at lims.bis.gov.in — this always reflects the latest recognized labs, so guide users there rather than naming specific labs, which can change over time.

15. Consumer verification & complaints: Consumers can verify a hallmark's authenticity, including registration date and testing centre, by entering the 6-digit HUID code into the official BIS CARE mobile app. The same app allows verification of ISI marks and CRS registration numbers, and lets consumers file a complaint directly with BIS if a product shows a fake, missing, or suspicious mark.

16. About Cognivolt AI: Cognivolt AI is a Q&A assistant built for Smart India Hackathon 2026, helping consumers and manufacturers understand BIS certification and Indian Standards. It's built using Google's Gemini AI model, combined with curated reference content on BIS schemes and standards that the team researched and verified, so answers stay grounded in accurate, specific facts rather than general AI guesses. On accuracy: as an AI-based system, it doesn't have a single official accuracy percentage like a classification model would. Its reliability comes from restricting answers to verified reference material for the topics it covers, and the team manually tested it across many question types during development. For high-stakes or complex compliance decisions, users should still confirm details against official BIS sources.

17. Pressure cookers: Aluminium (IS 2347), Stainless steel (IS 4251). Mandatory ISI mark under Scheme-I. Requires factory inspection, pressure/hydrostatic testing at BIS-recognized lab.

18. Domestic water heaters (electric): IS 302-2-35. Mandatory ISI mark. Covers storage and instant types. Safety tests: earthing, temperature control, pressure relief.

19. Electric fans (ceiling, table, pedestal): IS 374. Mandatory ISI mark. Tests: speed, power factor, temperature rise, insulation resistance, mechanical strength.

20. PVC insulated cables (up to 1100V): IS 694. Mandatory ISI mark. Covers copper/aluminium conductors for fixed wiring. Conductor resistance, insulation thickness, voltage test.

21. Switches for household use: IS 3854. Mandatory ISI mark. Covers switches up to 20A. Endurance, temperature rise, contact resistance tests.

22. LPG domestic gas stoves: IS 4246. Mandatory ISI mark. Covers 1-4 burner stoves. Thermal efficiency, flame stability, safety device tests.

23. Cement — Ordinary Portland (OPC 33/43/53): IS 269, IS 455, IS 1489. Mandatory ISI mark. Chemical composition, compressive strength, setting time tests.

24. Steel bars for concrete reinforcement: IS 1786 (Fe 415/500/550/600). Mandatory ISI mark. Yield strength, elongation, bend test, rib pattern.

25. Steel pipes for water/gas: IS 1239 (ERW), IS 3589 (submerged arc welded). Mandatory ISI mark. Hydrostatic test, flattening, bend test.

26. UPVC pipes for water supply: IS 4985. Mandatory ISI mark. Dimensions, vicat softening, impact, hydrostatic pressure test.

27. CPVC pipes for hot/cold water: IS 15778. Mandatory ISI mark. Higher temperature rating than UPVC. Chlorine content, impact, hydrostatic tests.

28. Toys safety: IS 9873 Parts 1-9. Mechanical/physical (Part 1), flammability (Part 2), migration of heavy metals (Parts 3, 9). Mandatory under Toys QCO. CRS scheme for electronic toys.

29. Two-wheeler helmets: IS 4151:2015. Mandatory ISI mark. Impact absorption, penetration, retention system, field of vision. BIS CARE app verification.

30. LED lamps (self-ballasted): IS 16102. Mandatory CRS registration. Safety, photometric, EMC tests. BIS-recognized lab test report + self-declaration.

31. LED luminaires (street, flood, downlight): IS 10322 Parts 5-1 to 5-6. Mandatory CRS. Photometric, thermal, IP rating, electrical safety.

32. Secondary lithium-ion batteries (portable): IS 16046 (IEC 62133). Mandatory CRS. Cell/battery level tests: crush, short circuit, overcharge, thermal abuse.

33. Inverters/UPS (up to 10 kVA): IS 16221. Mandatory CRS. Electrical safety, EMC, performance. Factory inspection not required (CRS = self-declaration).

34. Solar PV modules: IS 14286 (crystalline), IS 16170 (thin film). Mandatory CRS. Performance at STC, insulation, wet leakage, mechanical load.

35. Solar PV inverters: IS 16221 / IEC 62109. Mandatory CRS. Efficiency, grid synchronization, anti-islanding, protection functions.

36. Medical devices (notified): IS 16142 (risk classification), CDSCO registration + BIS certification. Varies by class (A/B/C/D). Some under CRS, some ISI.

37. Cosmetics: IS 4707 (toothpaste), IS 6356 (skin cream), IS 5383 (hair oil). BIS certification voluntary but QCOs expanding. Check latest Gazette notifications.

38. Packaged drinking water: IS 14543. Mandatory ISI mark. Microbiological, chemical, radiological limits. Source approval, plant hygiene critical.

39. Packaged natural mineral water: IS 13428. Mandatory ISI mark. Source protection, composition stability, treatment restrictions.

40. Milk powder / infant formula: IS 1165 (milk powder), IS 14433 (infant milk substitutes). Mandatory ISI mark. Protein, fat, moisture, microbiological limits.

41. Stainless steel sheets/plates: IS 6911. Grades 304, 316L, 430. Mandatory ISI mark for notified grades. Chemical composition, mechanical properties.

42. Stainless steel bars/wire: IS 1570 (grades), IS 6529 (wire), IS 3444 (bars/flats). Mandatory ISI for construction grades.

43. Aluminium conductors (AAC/AAAC/ACSR): IS 398. Mandatory ISI mark. Stranding, tensile strength, electrical resistance, wrapping test.

44. Distribution transformers: IS 1180. Mandatory ISI mark. Losses (no-load, load), impedance, temperature rise, short-circuit withstand.

45. Energy meters (static): IS 13779, IS 16444. Mandatory CRS. Accuracy class, tamper detection, communication protocol (DLMS/COSEM).

46. Electric irons: IS 366. Mandatory ISI mark. Temperature control, soleplate finish, steam function, electrical safety.

47. Mixer grinders: IS 4250. Mandatory ISI mark. Motor endurance, jar locking, overheating protection, noise level.

48. Room air conditioners: IS 1391. Mandatory CRS (split/window). Star labeling (BEE) + BIS safety. Cooling capacity, EER, refrigerant charge.

49. Refrigerators: IS 1391 Part 2. Mandatory CRS. Energy consumption, storage temperature, safety, refrigerant.

50. Washing machines: IS 1391 Part 3. Mandatory CRS. Wash performance, water consumption, spin speed, electrical safety.

51. Microwave ovens: IS 11676. Mandatory CRS. Microwave leakage, heating uniformity, door interlock, EMC.

52. Audio/video equipment (TVs, monitors): IS 616 / IEC 60065. Mandatory CRS. Electrical safety, radiation, mechanical stability.

53. Plugs and socket-outlets: IS 1293. Mandatory ISI mark. Up to 16A. Dimensional check, temperature rise, mechanical endurance.

54. Circuit breakers (MCB/RCCB): IS 8828, IS 12640. Mandatory ISI mark. Tripping characteristics, breaking capacity, endurance.

55. Wires and cables for automotive: IS 2465, IS 6380. Mandatory ISI for notified types. Conductor, insulation, abrasion, heat resistance.

56. Automotive lighting: IS 15588 (headlamps), IS 15589 (signalling). Mandatory ISI. Photometry, color, environmental tests.

57. Tyres (car/truck/bus): IS 15633 (passenger), IS 15636 (truck/bus). Mandatory ISI. Dimensions, load/speed rating, endurance, high-speed test.

58. Safety glass (windscreen/window): IS 2553 Part 1. Mandatory ISI. Laminated/toughened. Impact, fragmentation, optical distortion.

59. Brake linings: IS 2573. Mandatory ISI. Friction coefficient, wear, shear strength, fade resistance.

60. Hallmarking (gold/silver) — updated: Since June 2022, mandatory hallmarking in 288+ districts (phased expansion). HUID = 6-digit alphanumeric. 3 marks only: BIS logo + purity (916/750/585/375) + HUID. Verify on BIS CARE app. Jeweller registration mandatory on manakonline.in.

61. BIS CARE app features: Verify ISI mark (enter license no.), verify CRS (registration no.), verify HUID (6-digit code), file complaint (fake mark, missing mark, quality issue), check lab recognition status.

62. BIS Manak Online Portal (manakonline.in): Apply for ISI/FMCS/CRS, manage licenses, pay fees, submit test requests, track application status. Digital signatures (DSC) required for submission.

63. Testing labs — how to find: Go to lims.bis.gov.in → "Testing Facilities" → select IS code or product category → filter by state → get lab name, address, scope of recognition, contact. Always verify current recognition status before sending samples.

64. MSME fee concessions (2026): Micro/Startup: 80% off marking fee. Small: 50%. Medium: 20%. Women entrepreneurs + North-East units: additional 10% on top. Annual license fee concession also applies.

65. License validity (Feb 2026 update): First grant = up to 5 years. Renewal = 5-year terms. Annual fee payable each year. Surveillance visits: at least once per year for ISI, market surveillance for CRS.

66. Foreign Manufacturers Certification Scheme (FMCS): For imports. Indian representative (AIR) mandatory. Factory inspection in foreign country by BIS. License validity 1-2 years initially. Marking fee in USD.

67. Compulsory Registration Scheme (CRS) — Electronics/IT: Self-declaration based. No factory inspection. BIS-recognized lab test report (not older than 90 days) + declaration + fees → registration number. Products: mobile phones, laptops, tablets, LED TVs, Bluetooth devices, smart watches, power banks, adapters, keyboards, mice, routers, set-top boxes, CCTV cameras, etc.

68. Know Your Standard tool: bis.gov.in → "Know Your Standard" → enter product keyword → get applicable IS codes, scheme, status. Official source — use when unsure.

69. Quality Control Orders (QCOs): Issued by ministries under BIS Act 2016. Make BIS certification mandatory for notified products. Violation = punishable (fine, imprisonment). Check latest QCOs on bis.gov.in → "QCO Dashboard".

70. Consumer complaint process: BIS CARE app → "File Complaint" → enter product details, mark photos, purchase proof → BIS investigates. Alternatively: write to nearest BIS regional office (Delhi, Mumbai, Kolkata, Chennai, Chandigarh).

71. About Cognivolt AI (for self-questions): Built for SIH 2026 by Team Cognivolt. Google Gemini model + curated BIS reference data (150 entries). Not an official BIS tool. For compliance decisions, always verify on bis.gov.in or BIS CARE app.

72. Domestic gas appliances (beyond stoves): IS 15558 (gas water heaters), IS 15559 (gas room heaters). Mandatory ISI mark. Flame supervision device, combustion efficiency, CO emission tests.

73. Kerosene stoves: IS 13592. Mandatory ISI mark. Safety, efficiency, durability tests. Declining but still notified.

74. Bicycle reflectors: IS 6351. Mandatory ISI mark. Photometric performance, weathering, impact resistance.

75. Bicycle tyres/tubes: IS 15627 (tyres), IS 15628 (tubes). Mandatory ISI mark. Dimensions, load rating, endurance.

76. Cycle helmets: IS 10865. Mandatory ISI mark (recent QCO). Impact, retention, field of vision. Different from motorcycle helmets (IS 4151).

77. School bags: IS 15824. Mandatory ISI mark (2023 QCO). Weight limit (10% body weight), strap width, reflective strips, no sharp edges.

78. Footwear — safety/protective: IS 15298 (ISO 20345). Mandatory ISI for industrial safety boots. Toe cap impact (200J), compression, penetration, sole slip resistance.

79. Footwear — leather shoes: IS 5557 (men's), IS 6002 (women's). Voluntary ISI but QCO expanding. Upper-leather bond, sole attachment, water vapour permeability.

80. Leather gloves (industrial): IS 6994. Mandatory ISI for notified types. Abrasion, cut, tear, puncture resistance per EN 388.

81. Safety helmets (industrial): IS 2925:1984. Mandatory ISI mark. Shock absorption, penetration, chin strap, flammability. Construction, mining, factory use.

82. Firefighter helmets: IS 2745:1983. Mandatory ISI. High heat resistance, impact, visor optical quality, neck protection.

83. Respiratory protective devices: IS 9473 (filtering half masks), IS 15322 (powered air). Mandatory ISI for industrial use. Filter efficiency, breathing resistance, leakage.

84. Eye/face protection: IS 5983 (spectacles), IS 1179 (face shields). Mandatory ISI. Impact (high/low velocity), optical class, UV/IR protection.

85. Hearing protection: IS 6229 (ear muffs), IS 12079 (ear plugs). Mandatory ISI. Attenuation (SNR), comfort, durability.

86. Fall protection equipment: IS 3521 (body belts), IS 3522 (harnesses). Mandatory ISI. Static strength, dynamic test, corrosion resistance.

87. Conveyor belts (fire resistant): IS 1891 Part 2. Mandatory ISI for underground mining. Drum friction test, gallery test, electrical resistance.

88. Fire extinguishers: IS 15683 (portable), IS 16018 (wheeled). Mandatory ISI. Discharge duration, range, rating (A/B/C/D/K), rechargeability.

89. Fire hoses: IS 636 (rubber), IS 8423 (synthetic). Mandatory ISI. Burst pressure, abrasion, heat resistance, coupling compatibility.

90. Fire hydrants/landing valves: IS 5290. Mandatory ISI. Flow rate, pressure rating, operational torque, corrosion.

91. LPG rubber hoses: IS 9573. Mandatory ISI. Permeation, burst pressure, flame resistance, end fitting pull-out.

92. LPG regulators (domestic): IS 9798. Mandatory ISI. Lock-up pressure, relief valve, flow capacity, endurance.

93. LPG cylinder valves: IS 8737. Mandatory ISI. Hydrostatic test, torque, impact, pneumatic leak test. For cylinders >5L.

94. LPG cylinders (<5L): IS 7142. Mandatory ISI. Small portable cylinders. Design, manufacturing, testing per Part 1/2.

95. CNG cylinders (vehicular): IS 15490 (Type 1 steel), ISO 11439 (Type 2-4 composite). Mandatory ISI/third-party. Hydrostatic, burst, fatigue, bonfire test.

96. Medical oxygen cylinders: IS 3224 (steel), IS 15656 (composite). Mandatory ISI. Cleanliness (oxygen service), hydrostatic, volumetric capacity.

97. Valves for gas cylinders: IS 3224 (outlet connections), IS 8737 (LPG), IS 15490 (CNG). Mandatory ISI. Gas-specific outlet threads prevent cross-connection.

98. Pressure regulators (industrial): IS 13405. Mandatory ISI for notified gases. Lock-up, relief capacity, seat leakage, endurance.

99. Welding electrodes (mild steel): IS 814. Mandatory ISI. Chemical composition, mechanical properties, diffusible hydrogen, moisture.

100. Welding rods/wires (stainless): IS 5206. Mandatory ISI for notified grades. Alloy composition, ferrite number, corrosion test.

101. Flux-cored wires: IS 13955. Mandatory ISI. Slag system, mechanical properties, diffusible hydrogen.

102. Gas welding rods: IS 1278. Mandatory ISI. Composition, mechanical properties for oxy-fuel welding.

103. Solder alloys: IS 1921 (tin-lead), IS 16166 (lead-free). Mandatory ISI for electronics grades. Melting range, spread, corrosion flux residue.

104. Industrial explosives: IS 4967 (ANFO), IS 5513 (slurry), IS 5514 (emulsion). Mandatory ISI. Velocity of detonation, density, water resistance, gap test.

105. Detonators: IS 2572 (electric), IS 4067 (non-electric). Mandatory ISI. Firing current, no-fire current, delay accuracy, shock sensitivity.

106. Safety fuses: IS 2749. Mandatory ISI. Burning rate, tensile strength, water resistance.

107. Matchboxes (safety matches): IS 2769. Mandatory ISI. Head composition, splint quality, striking surface, moisture resistance.

108. Fireworks: IS 15558 (wire sparklers), IS 15559 (crackers). Mandatory ISI. Composition limits (no chlorates in crackers), noise level (125 dB), debris distance.

109. Cement — Portland Pozzolana (PPC): IS 1489 Part 1 (fly ash), Part 2 (calcined clay). Mandatory ISI. Pozzolanic activity, compressive strength, drying shrinkage.

110. Cement — Rapid Hardening: IS 8041. Mandatory ISI. High early strength (1 day ≥ 16 MPa), fineness, soundness.

111. ISI Mark Scheme (Scheme-I) — Step-by-step:
    1) Identify applicable IS standard via "Know Your Standard" tool
    2) Preliminary testing at BIS-recognized lab (test report ≤90 days old)
    3) Prepare documents: factory layout, machinery list, QC manual, org chart, raw material sources, test records
    4) Register on manakonline.in → fill Form-I/II → pay scrutiny fee (₹1,000) + marking fee advance
    5) BIS scrutiny → factory inspection (officer verifies QC, tests samples, checks records)
    6) Pay license fee + marking fee → license granted (valid up to 5 years)
    7) Ongoing: annual fee, surveillance visits (min 1/year), market samples tested.

112. CRS (Compulsory Registration Scheme) — Step-by-step:
    1) Confirm product in CRS notified list (bis.gov.in → CRS → Notified Products)
    2) Test at BIS-recognized lab (report ≤90 days, all applicable IS/IEC standards)
    3) Register on manakonline.in → fill Form-III → upload test report + declaration + fees
    4) No factory inspection. BIS verifies documents → grants registration number (R-xxxxxxx)
    5) Mark product with Standard Mark + R-number. Validity: 2 years, renewable.
    6) Surveillance: market samples picked by BIS, tested at recognized labs.

113. FMCS (Foreign Manufacturers Certification Scheme) — Step-by-step:
    1) Foreign manufacturer appoints Authorized Indian Representative (AIR) — Indian entity with DSC
    2) AIR applies on manakonline.in → Form-IV + manufacturer's QC docs + test reports
    3) BIS scrutiny → factory inspection in foreign country (BIS officer or empanelled agency)
    4) Manufacturer pays inspection charges (travel, daily allowance in USD) + marking fee in USD
    5) License granted (1-2 years initially) → product marked with ISI + license number
    6) Renewal: re-inspection or documentary review. Surveillance visits periodic.

114. Hallmarking (Gold/Silver) — Jeweller Registration:
    1) Jeweller registers on manakonline.in → Form-V + GSTIN + PAN + premises proof
    2) Pay registration fee (₹25,000 for 5 years) + security deposit
    3) BIS verifies → grants jeweller registration number (JRN)
    4) Jeweller sends articles to BIS-recognized AHC (Assaying & Hallmarking Centre)
    5) AHC tests purity (XRF/fire assay) → applies hallmark (3 marks: BIS logo + purity + HUID)
    6) HUID = 6-digit alphanumeric, unique per article. Trackable on BIS CARE app.

115. Hallmarking — AHC (Assaying & Hallmarking Centre) Recognition:
    1) Apply on manakonline.in → Form-VI + lab infrastructure (XRF, fire assay, cupellation)
    2) BIS audit → recognition granted (valid 3 years)
    3) AHC must maintain NABL accreditation (ISO 17025) for hallmarking scope
    4) Random audits, proficiency testing mandatory. HUID generation via BIS server.

116. Fee Structure (2026 approximate, verify latest):
    - Scrutiny fee: ₹1,000 (ISI), ₹1,000 (CRS), ₹5,000 (FMCS)
    - Marking fee: % of production value (varies by product, e.g., cement 0.2%, steel 0.1%, cables 0.5%)
    - Minimum annual marking fee: ₹50,000 (ISI), ₹25,000 (CRS)
    - License fee: ₹1,000/year (ISI), ₹1,000/2 years (CRS)
    - FMCS: marking fee in USD (e.g., $0.50-$2 per unit), inspection charges actuals
    - MSME concessions: Micro/Startup 80%, Small 50%, Medium 20% on marking fee. Women + NE: +10%.

117. License Validity & Renewal (Feb 2026 regulation):
    - First grant: up to 5 years (previously 1-2 years)
    - Renewal: 5-year terms
    - Annual fee payable each year regardless of term
    - Surveillance: at least 1 factory visit/year (ISI), market sampling (CRS)
    - Late renewal: penalty + possible suspension. Expired >6 months = fresh application.

118. Surveillance & Market Sampling:
    - ISI: Factory inspection (QC system, testing, records) + factory sample testing + market sample testing
    - CRS: Market samples purchased anonymously → tested at recognized lab → failure = suspension/cancellation
    - FMCS: Foreign factory inspection + market surveillance in India
    - Failure consequences: advisory → warning → suspension → cancellation → prosecution under BIS Act 2016.

119. Testing Requirements — Lab Recognition:
    - Labs must be BIS-recognized for specific IS codes (scope of recognition)
    - Recognition via BIS Lab Recognition Scheme (LRS) — audit per ISO 17025 + BIS criteria
    - Validity: 3 years, surveillance audits. Search at lims.bis.gov.in → "Testing Facilities"
    - Test report validity: 90 days from date of issue for certification applications
    - Manufacturer's own lab: can be recognized if meets criteria (separate LRS application)

120. Testing Requirements — Type Testing vs Routine Testing:
    - Type testing: Full standard coverage, done at recognized lab for initial license/registration
    - Routine testing: Subset of tests (critical parameters) done at factory on each batch/lot
    - Factory must have test equipment, calibrated, trained personnel, records maintained
    - BIS officer verifies routine test records during surveillance visits.

121. Documentation — QC Manual Minimum Contents:
    - Organization structure & responsibilities
    - Incoming material inspection (raw materials, components)
    - In-process inspection (stage-wise checks, frequency)
    - Final inspection (type test parameters, sampling plan)
    - Calibration schedule (equipment list, frequency, standards traceability)
    - Non-conformance handling (rework, rejection, corrective action)
    - Internal audit plan & records
    - Management review minutes.

122. Documentation — Factory Layout Requirements:
    - Scale drawing showing: raw material storage, production flow, testing lab, finished goods, rejected goods
    - Machinery layout with capacity, make, year
    - Utilities: power, water, compressed air, ventilation
    - Safety: fire extinguishers, exits, first aid
    - Separate areas for: QC hold, calibration, standards room.

123. Common Rejection Reasons (Applications):
    - Test report >90 days old or from non-recognized lab
    - QC manual generic (not product-specific), missing calibration plan
    - Factory layout incomplete, no separate rejected goods area
    - Machinery list missing key equipment for the product
    - Raw material sources not declared, no incoming inspection records
    - DSC not registered on manakonline.in, authorization letter missing.

124. BIS CARE App — Full Features:
    - Verify ISI: enter license number → shows licensee, product, validity, factory address
    - Verify CRS: enter registration number → shows registrant, product, validity
    - Verify Hallmark: enter 6-digit HUID → shows jeweller, AHC, purity, date
    - File Complaint: photo of mark + product + bill → BIS investigates
    - Check Lab: search by IS code/state → recognized labs list
    - Know Your Standard: product keyword → applicable IS codes
    - Available: Android, iOS, web (care.bis.gov.in).

125. Consumer Rights Under BIS Act 2016:
    - Right to buy only certified products for notified categories
    - Right to verify mark authenticity via BIS CARE app
    - Right to file complaint for fake/missing/substandard marks
    - Right to compensation if certified product causes injury (product liability)
    - Right to information: BIS must publish license/registration details publicly.

126. Offences & Penalties (BIS Act 2016):
    - Using fake Standard Mark: up to 2 years imprisonment + fine ≥ ₹2 lakh
    - Manufacturing/selling non-certified notified product: up to 1 year + fine
    - Misusing license/registration: suspension/cancellation + fine
    - Obstructing BIS officer: up to 6 months + fine
    - Repeat offence: enhanced penalty. Compounding possible for first offence.

127. Appeals & Adjudication:
    - License suspension/cancellation → appeal to DG, BIS within 30 days
    - Further appeal → Central Government (Ministry of Consumer Affairs)
    - Penalty orders → adjudicating officer → appeal to Appellate Authority
    - Prosecution cases → judicial magistrate. Legal counsel recommended.

128. International Alignment:
    - Many IS standards harmonized with IEC/ISO (dual numbering: IS 16102 = IEC 62384)
    - BIS is member of ISO, IEC, Codex Alimentarius
    - Mutual Recognition Agreements (MRAs) with select countries for test reports
    - FMCS aligns with WTO TBT Agreement — non-discriminatory treatment.

129. Recent Key Updates (2024-2026):
    - License validity extended to 5 years (Feb 2026)
    - Hallmarking mandatory in 288+ districts (phased, check current list)
    - CRS expanded: smart watches, CCTV cameras, routers, set-top boxes added
    - QCOs issued for: toys, helmets, pressure cookers, cables, fans, water heaters
    - Manak Online portal upgraded: single sign-on, digital payments, auto-renewal alerts
    - BIS CARE app: vernacular languages added, complaint tracking.

130. Useful Links for Users:
    - bis.gov.in — main portal
    - manakonline.in — licensing portal
    - lims.bis.gov.in — lab search
    - care.bis.gov.in — BIS CARE web version
    - bis.gov.in/qco-dashboard — latest QCOs
    - bis.gov.in/know-your-standard — standard finder tool
    - bis.gov.in/fee-structure — current fees
    - bis.gov.in/crs-notified-products — CRS list

131. BIS Lab Recognition Scheme (LRS) — Process:
    1) Lab applies online → Form-LR + quality manual (ISO 17025) + scope request
    2) BIS document review → adequacy audit (ISO 17025 + BIS-specific criteria)
    3) Technical assessment: witness testing, equipment calibration, personnel competence
    4) Recognition granted for specific IS codes (scope) — valid 3 years
    5) Surveillance: annual audit + proficiency testing (PT) participation mandatory
    6) Renewal: full reassessment. Scope extension: supplementary assessment.

132. Manufacturer's In-House Lab Recognition:
    - Separate LRS application for factory lab
    - Must be independent of production (separate QC department)
    - Equipment calibration traceable to NABL/national standards
    - Personnel trained, authorized, records maintained
    - BIS may restrict scope to routine tests only (not type tests)
    - Advantage: faster routine testing, but type tests still need external lab.

133. NABL Accreditation vs BIS Recognition:
    - NABL = ISO 17025 accreditation (general competence)
    - BIS Recognition = NABL + BIS-specific criteria (product standards, marking rules)
    - All BIS-recognized labs must have NABL accreditation for relevant scope
    - But not all NABL labs are BIS-recognized (must apply separately)
    - Check both: lims.bis.gov.in for BIS recognition, nabl.gov.in for accreditation.

134. Proficiency Testing (PT) for Recognized Labs:
    - Mandatory participation in PT schemes (BIS-organized or NABL/APLAC)
    - Frequency: at least once per year per test parameter
    - Unsatisfactory PT result → root cause analysis → corrective action → re-test
    - Repeated failure → scope suspension. Results shared with BIS.

135. Test Report Requirements for Certification:
    - Must be on lab letterhead with BIS recognition number
    - All applicable clauses of IS standard tested (or clearly stated exclusions)
    - Results with units, pass/fail per clause, measurement uncertainty where applicable
    - Sample identification: manufacturer, batch, quantity, date received/tested
    - Signed by authorized signatory. Digital signature accepted.
    - Validity: 90 days from issue date for license/registration application.

136. Common Test Parameters by Category:
    - Electrical: insulation resistance, high voltage, leakage current, temperature rise, earthing continuity
    - Mechanical: impact, compression, tensile, hardness, fatigue, wear
    - Chemical: composition analysis, migration limits (heavy metals), pH, residual monomers
    - Thermal: thermal stability, Vicat softening, heat deflection, flammability
    - Dimensional: critical dimensions per standard, tolerances, gauging
    - Performance: efficiency, capacity, output, endurance, cycling.

137. Sample Selection & Quantity:
    - Type test: per standard's sampling clause (typically 3-5 samples per variant)
    - Factory surveillance: officer selects randomly from production/lot
    - Market surveillance: purchased anonymously from retail/wholesale
    - Sample size must allow all tests + reserve for retest/dispute
    - Sealing & identification: BIS officer seals samples, unique ID, chain of custody.

138. Retest & Dispute Resolution:
    - Licensee/registrant can request retest within 14 days of failure intimation
    - Retest at same or different recognized lab (mutually agreed)
    - Cost borne by requester. If retest passes → original failure reviewed
    - Dispute on test method/interpretation → referred to BIS technical committee
    - Final appeal → DG, BIS. Legal action only after administrative remedies exhausted.

139. Calibration Requirements for Factory Labs:
    - All measuring/test equipment calibrated per schedule (max 1 year unless justified)
    - Traceable to national/international standards (NPL, NABL labs)
    - Calibration certificates retained ≥3 years
    - Out-of-calibration equipment → immediate withdrawal, impact assessment on past tests
    - Reference standards (master gauges, weights) calibrated externally annually.

140. Finding the Right Lab — Practical Guide:
    1) Go to lims.bis.gov.in → "Testing Facilities"
    2) Enter IS code (e.g., IS 16102) or product keyword (e.g., "LED lamp")
    3) Filter by state/region for logistics
    4) Check scope: ensure lab recognized for ALL required test clauses
    5) Contact lab: confirm availability, turnaround time (typically 7-21 days), cost
    6) Verify current recognition status (expiry date) before sending samples
    7) Ask for quote with break-up: test fees + sample prep + report + GST.

141. How to Identify Fake ISI Mark:
    - Check font: "ISI" in specific stylized font, not plain text
    - License number format: CM/L-xxxxxxx (7-8 digits after CM/L-)
    - Mandatory: IS number below mark (e.g., "IS 302-2-35")
    - Verify on BIS CARE app — fake marks won't appear in database
    - Poor print quality, smudging, wrong proportions = red flags
    - Report via BIS CARE app with photos.

142. How to Identify Fake CRS Mark:
    - Format: Standard Mark + "R-xxxxxxx" (7 digits after R-)
    - No IS number required on mark (but must be in documentation)
    - Verify registration number on BIS CARE app or manakonline.in
    - CRS mark only on notified electronics/IT products
    - If product not in CRS list but has CRS mark = fake.

143. How to Identify Fake Hallmark (Post-2021):
    - Must have EXACTLY 3 marks: (1) BIS logo (triangle), (2) Purity grade (916/750/585/375), (3) 6-digit HUID
    - NO separate jeweller mark, NO separate assaying centre mark (old 5-mark format discontinued)
    - HUID must verify on BIS CARE app showing matching jeweller + AHC + date
    - Laser-engraved, not stamped (for HUID). Stamped purity + logo acceptable.
    - Magnifying glass: HUID characters should be crisp, uniform depth.

144. Common Consumer Complaints & Resolution:
    - "Product has ISI mark but fails early" → File complaint on BIS CARE app with bill, photos, failure description. BIS tests market sample.
    - "Jeweller refuses to hallmark" → Mandatory in notified districts. Complaint → BIS issues notice to jeweller.
    - "Online product no mark" → Screenshot listing + delivered product photos → complaint. E-commerce platforms liable.
    - "Mark looks suspicious" → Verify on app. If fake → complaint → BIS raids, seizes, prosecutes.

145. MSME/Startup Specific Guidance:
    - Register on Udyam portal first (udyamregistration.gov.in) for MSME certificate
    - Apply for BIS license with MSME certificate → automatic fee concession
    - Startups (DPIIT recognized): 80% marking fee concession + priority processing
    - Women entrepreneurs: additional 10% on top of category concession
    - North-East states: additional 10% concession
    - Use BIS "Handholding" scheme: free technical guidance for first-time applicants.

146. Importer Specific Guidance (FMCS):
    - Must have Indian entity as Authorized Indian Representative (AIR)
    - AIR holds license, pays fees, liaises with BIS
    - Foreign factory inspection: BIS officer travels (manufacturer pays ~$5,000-10,000)
    - Alternative: empanelled foreign inspection agency (BIS-approved) — lower cost
    - License validity initially 1-2 years, then 5-year renewals
    - Marking fee in USD, payable quarterly/annually.

147. Student/Researcher Guidance:
    - Indian Standards available for purchase at bis.gov.in → "Standards" → "Buy Standards"
    - College libraries often have institutional access (check with librarian)
    - BIS Student Membership: discounted standards access, competition updates
    - Standards Clubs in colleges: BIS supports with resources, guest lectures
    - Internship opportunities: BIS offers summer internships (apply via bis.gov.in).

148. Export-Oriented Units (EOUs) & SEZ:
    - Products for export only: BIS certification not mandatory IF not sold in India
    - But if ANY quantity sold domestically → full certification required
    - EOU/SEZ units can apply for ISI/CRS same as domestic units
    - FMCS not needed (Indian manufacturer). AIR not required.
    - Customs may ask for BIS certificate at import clearance for notified products.

149. Digital/Tech Products — Emerging Categories:
    - Smart home devices (IoT): CRS likely applicable if "electronic" + "IT" notified
    - Wearables (health monitoring): May need CDSCO (medical) + BIS (safety/EMC)
    - EV charging equipment: IS 17017 series (AC/DC charging). Mandatory CRS/ISI per QCO
    - Drone components: Emerging standards. Check QCO dashboard.
    - 5G equipment: TEC (Telecom) + BIS (safety/EMC) dual compliance.

150. When in Doubt — Official Sources Hierarchy:
    1) BIS Act 2016 + Rules/Regulations (legally binding)
    2) Quality Control Orders (Gazette notifications — mandatory compliance)
    3) BIS Certification Schemes (ISI, CRS, FMCS guidelines on bis.gov.in)
    4) Indian Standards (IS codes — technical requirements)
    5) BIS Circulars/Office Memoranda (procedural clarifications)
    6) BIS CARE app / manakonline.in / lims.bis.gov.in (operational tools)
    7) This assistant (Cognivolt AI) — curated guidance, NOT legal advice.
    ALWAYS verify for compliance decisions. Use "Know Your Standard" tool first."""

CITATION_INDEX = {
    "gold": [6, 60, 114, 115, 143],
    "hallmark": [6, 60, 114, 115, 143],
    "huid": [6, 60, 114, 115, 143],
    "jeweller": [60, 114, 115],
    "assaying": [115],
    "purity": [6, 60, 143],
    "916": [6, 60, 143],
    "750": [6, 60, 143],
    "585": [6, 60, 143],
    "375": [6, 60, 143],
    "bis care": [15, 61, 124],
    "isi": [2, 3, 111, 141],
    "crs": [2, 30, 31, 32, 33, 34, 35, 67, 112, 142],
    "fmcs": [2, 66, 113, 146],
    "scheme": [2, 111, 112, 113],
    "helmet": [7, 29, 76, 81, 82],
    "pressure cooker": [17],
    "water heater": [18, 72],
    "fan": [19],
    "cable": [20, 55],
    "switch": [21, 53],
    "gas stove": [22, 73],
    "cement": [23, 109, 110],
    "steel bar": [24, 42],
    "pipe": [25, 26, 27, 11],
    "toy": [9, 28],
    "led": [30, 31],
    "battery": [32],
    "inverter": [33],
    "solar": [34, 35],
    "medical device": [36],
    "cosmetic": [37],
    "water": [38, 39, 10],
    "milk": [40],
    "stainless": [12, 41, 42, 100],
    "conductor": [43],
    "transformer": [44],
    "energy meter": [45],
    "iron": [46],
    "mixer": [47],
    "ac": [48],
    "refrigerator": [49],
    "washing machine": [50],
    "microwave": [51],
    "tv": [52],
    "plug": [53],
    "circuit breaker": [54],
    "automotive": [13, 55, 56, 57, 58, 59],
    "tyre": [57],
    "glass": [58],
    "brake": [59],
    "apply": [3, 111, 112, 113, 114],
    "license": [4, 65, 111, 117],
    "renewal": [4, 65, 111, 117],
    "fee": [5, 64, 116],
    "msme": [5, 64, 145],
    "startup": [5, 64, 145],
    "woman": [5, 64, 145],
    "north east": [5, 64, 145],
    "surveillance": [118],
    "testing lab": [14, 63, 119, 131, 132, 133, 140],
    "lab recognition": [131, 132, 133, 134],
    "nab": [133],
    "test report": [119, 135],
    "type test": [120],
    "routine test": [120],
    "qc manual": [121],
    "factory layout": [122],
    "rejection": [123],
    "consumer": [15, 124, 125, 144],
    "complaint": [15, 61, 70, 124, 144],
    "penalty": [126],
    "appeal": [127],
    "importer": [66, 113, 146],
    "export": [148],
    "student": [147],
    "2026": [4, 65, 116, 117, 129],
    "2024": [129],
    "qco": [2, 69, 129],
    "know your standard": [68, 130],
    "fake": [141, 142, 143],
    "verify": [15, 61, 124, 141, 142, 143],
}

CATEGORIES: dict[str, CategoryInfo] = {
    "Electrical & Electronics": {
        "icon": "⬡",
        "items": {
            "LED Lamps (self-ballasted)": {"scheme": "CRS", "is": "IS 16102"},
            "LED Luminaires (street, flood, downlight)": {
                "scheme": "CRS",
                "is": "IS 10322 Parts 5-1 to 5-6",
            },
            "Electric Fans (ceiling, table, pedestal)": {
                "scheme": "ISI",
                "is": "IS 374",
            },
            "PVC Insulated Cables (up to 1100V)": {"scheme": "ISI", "is": "IS 694"},
            "Switches for Household Use": {"scheme": "ISI", "is": "IS 3854"},
            "Energy Meters (static)": {"scheme": "CRS", "is": "IS 13779, IS 16444"},
            "Electric Irons": {"scheme": "ISI", "is": "IS 366"},
            "Mixer Grinders": {"scheme": "ISI", "is": "IS 4250"},
            "Room Air Conditioners": {"scheme": "CRS", "is": "IS 1391"},
            "Refrigerators": {"scheme": "CRS", "is": "IS 1391 Part 2"},
            "Washing Machines": {"scheme": "CRS", "is": "IS 1391 Part 3"},
            "Microwave Ovens": {"scheme": "CRS", "is": "IS 11676"},
            "Audio/Video Equipment (TVs, monitors)": {
                "scheme": "CRS",
                "is": "IS 616 / IEC 60065",
            },
            "Plugs and Socket-Outlets": {"scheme": "ISI", "is": "IS 1293"},
            "Circuit Breakers (MCB/RCCB)": {"scheme": "ISI", "is": "IS 8828, IS 12640"},
        },
    },
    "Construction Materials": {
        "icon": "⬛",
        "items": {
            "Cement — Ordinary Portland (OPC 33/43/53)": {
                "scheme": "ISI",
                "is": "IS 269, IS 455, IS 1489",
            },
            "Cement — Portland Pozzolana (PPC)": {
                "scheme": "ISI",
                "is": "IS 1489 Part 1 & 2",
            },
            "Cement — Rapid Hardening": {"scheme": "ISI", "is": "IS 8041"},
            "Steel Bars for Concrete Reinforcement": {"scheme": "ISI", "is": "IS 1786"},
            "Steel Pipes for Water/Gas": {"scheme": "ISI", "is": "IS 1239, IS 3589"},
            "UPVC Pipes for Water Supply": {"scheme": "ISI", "is": "IS 4985"},
            "CPVC Pipes for Hot/Cold Water": {"scheme": "ISI", "is": "IS 15778"},
            "Stainless Steel Sheets/Plates": {"scheme": "ISI", "is": "IS 6911"},
            "Stainless Steel Bars/Wire": {
                "scheme": "ISI",
                "is": "IS 1570, IS 6529, IS 3444",
            },
            "Aluminium Conductors (AAC/AAAC/ACSR)": {"scheme": "ISI", "is": "IS 398"},
        },
    },
    "Automotive": {
        "icon": "⬟",
        "items": {
            "Two-Wheeler Helmets": {"scheme": "ISI", "is": "IS 4151:2015"},
            "Cycle Helmets": {"scheme": "ISI", "is": "IS 10865"},
            "Tyres (Car/Truck/Bus)": {"scheme": "ISI", "is": "IS 15633, IS 15636"},
            "Safety Glass (Windscreen/Window)": {
                "scheme": "ISI",
                "is": "IS 2553 Part 1",
            },
            "Brake Linings": {"scheme": "ISI", "is": "IS 2573"},
            "Automotive Lighting": {"scheme": "ISI", "is": "IS 15588, IS 15589"},
            "Wires and Cables for Automotive": {
                "scheme": "ISI",
                "is": "IS 2465, IS 6380",
            },
        },
    },
    "LPG & Gas Appliances": {
        "icon": "⬡",
        "items": {
            "LPG Cylinders (>5L)": {"scheme": "ISI", "is": "IS 3196 Part 1"},
            "LPG Cylinders (<5L)": {"scheme": "ISI", "is": "IS 7142"},
            "LPG Cylinder Valves": {"scheme": "ISI", "is": "IS 8737"},
            "LPG Domestic Gas Stoves": {"scheme": "ISI", "is": "IS 4246"},
            "LPG Rubber Hoses": {"scheme": "ISI", "is": "IS 9573"},
            "LPG Regulators (Domestic)": {"scheme": "ISI", "is": "IS 9798"},
            "Domestic Gas Water Heaters": {"scheme": "ISI", "is": "IS 15558"},
            "Domestic Gas Room Heaters": {"scheme": "ISI", "is": "IS 15559"},
            "Kerosene Stoves": {"scheme": "ISI", "is": "IS 13592"},
            "CNG Cylinders (Vehicular)": {"scheme": "ISI", "is": "IS 15490"},
        },
    },
    "Food, Water & Infant Products": {
        "icon": "⬜",
        "items": {
            "Packaged Drinking Water": {"scheme": "ISI", "is": "IS 14543"},
            "Packaged Natural Mineral Water": {"scheme": "ISI", "is": "IS 13428"},
            "Milk Powder": {"scheme": "ISI", "is": "IS 1165"},
            "Infant Milk Substitutes": {"scheme": "ISI", "is": "IS 14433"},
            "HDPE Pipes for Potable Water": {"scheme": "ISI", "is": "IS 4984"},
        },
    },
    "Toys & Safety Equipment": {
        "icon": "⬟",
        "items": {
            "Toys (Mechanical/Physical Safety)": {
                "scheme": "ISI/CRS",
                "is": "IS 9873 Part 1",
            },
            "Toys (Flammability)": {"scheme": "ISI/CRS", "is": "IS 9873 Part 2"},
            "Toys (Chemical Safety - Heavy Metals)": {
                "scheme": "ISI/CRS",
                "is": "IS 9873 Parts 3 & 9",
            },
            "Industrial Safety Helmets": {"scheme": "ISI", "is": "IS 2925:1984"},
            "Firefighter Helmets": {"scheme": "ISI", "is": "IS 2745:1983"},
            "Respiratory Protective Devices": {
                "scheme": "ISI",
                "is": "IS 9473, IS 15322",
            },
            "Eye/Face Protection": {"scheme": "ISI", "is": "IS 5983, IS 1179"},
            "Hearing Protection": {"scheme": "ISI", "is": "IS 6229, IS 12079"},
            "Fall Protection Equipment": {"scheme": "ISI", "is": "IS 3521, IS 3522"},
            "School Bags": {"scheme": "ISI", "is": "IS 15824"},
        },
    },
    "Hallmarking & Jewellery": {
        "icon": "⬡",
        "items": {
            "Gold Hallmarking (22K/18K/14K/9K)": {
                "scheme": "Hallmarking",
                "is": "IS 1417 (purity grades)",
            },
            "Silver Hallmarking": {
                "scheme": "Hallmarking",
                "is": "IS 2112 (purity grades)",
            },
            "Jeweller Registration": {
                "scheme": "Hallmarking",
                "is": "Form-V on manakonline.in",
            },
            "AHC Recognition": {
                "scheme": "Hallmarking",
                "is": "Form-VI on manakonline.in",
            },
        },
    },
    "Industrial & Specialized": {
        "icon": "⬛",
        "items": {
            "Pressure Cookers (Aluminium/Stainless Steel)": {
                "scheme": "ISI",
                "is": "IS 2347, IS 4251",
            },
            "Domestic Water Heaters (Electric)": {"scheme": "ISI", "is": "IS 302-2-35"},
            "Distribution Transformers": {"scheme": "ISI", "is": "IS 1180"},
            "Secondary Lithium-Ion Batteries": {"scheme": "CRS", "is": "IS 16046"},
            "Inverters/UPS (up to 10 kVA)": {"scheme": "CRS", "is": "IS 16221"},
            "Solar PV Modules": {"scheme": "CRS", "is": "IS 14286, IS 16170"},
            "Solar PV Inverters": {"scheme": "CRS", "is": "IS 16221 / IEC 62109"},
            "Medical Devices (Notified)": {"scheme": "ISI/CRS", "is": "IS 16142"},
            "Cosmetics": {"scheme": "Voluntary/ISI", "is": "IS 4707, IS 6356, IS 5383"},
            "Fire Extinguishers": {"scheme": "ISI", "is": "IS 15683, IS 16018"},
            "Fire Hoses": {"scheme": "ISI", "is": "IS 636, IS 8423"},
            "Industrial Explosives": {
                "scheme": "ISI",
                "is": "IS 4967, IS 5513, IS 5514",
            },
            "Detonators": {"scheme": "ISI", "is": "IS 2572, IS 4067"},
            "Welding Electrodes": {"scheme": "ISI", "is": "IS 814, IS 5206, IS 13955"},
            "Bicycle Tyres/Tubes": {"scheme": "ISI", "is": "IS 15627, IS 15628"},
            "Bicycle Reflectors": {"scheme": "ISI", "is": "IS 6351"},
            "PVC Materials": {
                "scheme": "ISI",
                "is": "IS 10151, IS 4985, IS 15778, IS 6719, IS 13592, IS 9537",
            },
        },
    },
    "Emerging Categories": {
        "icon": "✦",
        "items": {
            "Smart Home Devices (IoT)": {
                "scheme": "CRS (likely)",
                "is": "Check CRS notified list",
            },
            "Wearables (Health Monitoring)": {
                "scheme": "CDSCO + CRS",
                "is": "Medical + safety standards",
            },
            "EV Charging Equipment": {"scheme": "CRS/ISI", "is": "IS 17017 series"},
            "Drone Components": {
                "scheme": "Check QCO dashboard",
                "is": "Emerging standards",
            },
            "5G Equipment": {"scheme": "TEC + CRS", "is": "Telecom + safety/EMC"},
        },
    },
}

CHECKLISTS = {
    "ISI Mark (Scheme-I)": [
        "Identify applicable IS standard via 'Know Your Standard' tool (bis.gov.in)",
        "Preliminary testing at BIS-recognized lab (test report ≤90 days old)",
        "Prepare factory layout with QC areas marked",
        "Prepare quality control manual (product-specific)",
        "Prepare machinery list with capacity, make, year",
        "Document raw material sources + supplier details",
        "Maintain test records & calibration certificates",
        "Register on manakonline.in → fill Form-I/II",
        "Pay scrutiny fee (₹1,000) + marking fee advance",
        "Factory inspection by BIS officer (QC, testing, records)",
        "Pay license fee + marking fee → license granted (up to 5 years)",
        "Ongoing: annual fee, surveillance visits (min 1/year), market samples tested",
    ],
    "CRS (Compulsory Registration Scheme)": [
        "Confirm product in CRS notified list (bis.gov.in → CRS → Notified Products)",
        "Test at BIS-recognized lab (report ≤90 days, all applicable IS/IEC standards)",
        "Register on manakonline.in → fill Form-III",
        "Upload test report + declaration + fees",
        "No factory inspection required",
        "BIS verifies documents → grants registration number (R-xxxxxxx)",
        "Mark product with Standard Mark + R-number",
        "Validity: 2 years, renewable",
        "Surveillance: market samples picked by BIS, tested at recognized labs",
    ],
    "FMCS (Foreign Manufacturers Certification Scheme)": [
        "Foreign manufacturer appoints Authorized Indian Representative (AIR) — Indian entity with DSC",
        "AIR applies on manakonline.in → Form-IV + manufacturer's QC docs + test reports",
        "BIS scrutiny → factory inspection in foreign country (BIS officer or empanelled agency)",
        "Manufacturer pays inspection charges (travel, daily allowance in USD) + marking fee in USD",
        "License granted (1-2 years initially) → product marked with ISI + license number",
        "Renewal: re-inspection or documentary review",
        "Surveillance visits periodic",
    ],
    "Hallmarking (Jeweller Registration)": [
        "Register on manakonline.in → Form-V + GSTIN + PAN + premises proof",
        "Pay registration fee (₹25,000 for 5 years) + security deposit",
        "BIS verifies → grants jeweller registration number (JRN)",
        "Send articles to BIS-recognized AHC (Assaying & Hallmarking Centre)",
        "AHC tests purity (XRF/fire assay) → applies hallmark (3 marks: BIS logo + purity + HUID)",
        "HUID = 6-digit alphanumeric, unique per article, trackable on BIS CARE app",
    ],
}

SCHEME_STYLES = {
    "ISI": "scheme-isi",
    "CRS": "scheme-crs",
    "FMCS": "scheme-fmcs",
    "Hallmarking": "scheme-hallmark",
    "ISI/CRS": "scheme-isi",
    "Voluntary/ISI": "scheme-isi",
    "CRS (likely)": "scheme-crs",
    "CDSCO + CRS": "scheme-crs",
    "CRS/ISI": "scheme-crs",
    "Check QCO dashboard": "scheme-other",
    "TEC + CRS": "scheme-crs",
}


# ==================== HELPER FUNCTIONS ====================
def extract_citations(answer_text: str, citation_index: dict) -> list[int]:
    found: set[int] = set()
    answer_lower = answer_text.lower()
    for keyword, entries in citation_index.items():
        if keyword in answer_lower:
            found.update(entries)
    return sorted(found)


def get_answer_stream(messages: list) -> Generator[str, None, None]:
    keys = [
        os.getenv("GEMINI_API_KEY_1"),
        os.getenv("GEMINI_API_KEY_2"),
        os.getenv("GEMINI_API_KEY_3"),
        os.getenv("GEMINI_API_KEY_4"),
        os.getenv("GEMINI_API_KEY_5"),
        os.getenv("GEMINI_API_KEY_6"),
    ]
    keys = [k for k in keys if k]
    if not keys:
        raise RuntimeError(
            "No Gemini API keys configured. Add them in the app's Secrets panel."
        )
    api_key = random.choice(keys)
    client = genai.Client(api_key=api_key)
    recent = messages[-8:]
    convo = "\n".join(
        f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
        for m in recent
    )
    prompt = f"""{BIS_CONTEXT}

Conversation so far:
{convo}

Answer the latest User message above. If it refers back to something earlier in
the conversation (e.g. "what about X" or "and for Y"), use that earlier context
to understand what's being asked. When your answer references a specific fact
from the reference information, mention the relevant IS standard number or
scheme name."""
    import time

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content_stream(
                model="gemini-3.6-flash",
                contents=prompt,
            )
            break
        except Exception as e:
            if (
                "503" in str(e) or "UNAVAILABLE" in str(e)
            ) and attempt < max_retries - 1:
                time.sleep(2**attempt)
                continue
            raise
    for chunk in response:
        if chunk.text:
            yield chunk.text


# ==================== RENDER FUNCTIONS ====================
def render_tab_bar() -> None:
    """No-op: native st.tabs handles tab bar"""
    pass


def render_home() -> None:
    if not st.session_state.get("messages"):
        st.markdown(
            """
        <div class="empty-state">
            <div class="empty-icon">✦</div>
            <h2 class="empty-title">Ask me anything about BIS</h2>
            <p class="empty-desc">From certification schemes to IS standards, hallmarking to fee calculations — I'm here to help.</p>
            <div class="prompt-grid">
                <div class="prompt-card" onclick="document.querySelector('[data-testid=stChatInput] textarea').value='What is the ISI mark certification process?'; document.querySelector('[data-testid=stChatInput] textarea').dispatchEvent(new Event('input', {bubbles: true})); document.querySelector('[data-testid=stChatInput] button').click();">
                    <div class="prompt-card-icon">⬜</div>
                    <p class="prompt-card-title">ISI Mark Process</p>
                </div>
                <div class="prompt-card" onclick="document.querySelector('[data-testid=stChatInput] textarea').value='What are the 3 marks on hallmarked gold?'; document.querySelector('[data-testid=stChatInput] textarea').dispatchEvent(new Event('input', {bubbles: true})); document.querySelector('[data-testid=stChatInput] button').click();">
                    <div class="prompt-card-icon">⬡</div>
                    <p class="prompt-card-title">Gold Hallmarking</p>
                </div>
                <div class="prompt-card" onclick="document.querySelector('[data-testid=stChatInput] textarea').value='I manufacture LED bulbs. What certification do I need?'; document.querySelector('[data-testid=stChatInput] textarea').dispatchEvent(new Event('input', {bubbles: true})); document.querySelector('[data-testid=stChatInput] button').click();">
                    <div class="prompt-card-icon">⬡</div>
                    <p class="prompt-card-title">Product Certification</p>
                </div>
                <div class="prompt-card" onclick="document.querySelector('[data-testid=stChatInput] textarea').value='How to verify BIS hallmark on CARE app?'; document.querySelector('[data-testid=stChatInput] textarea').dispatchEvent(new Event('input', {bubbles: true})); document.querySelector('[data-testid=stChatInput] button').click();">
                    <div class="prompt-card-icon">⌕</div>
                    <p class="prompt-card-title">Verify Hallmark</p>
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Chat history
    for msg in st.session_state.get("messages", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle pending question from other tabs
    if "pending_question" in st.session_state:
        question = st.session_state.pending_question
        del st.session_state.pending_question
    else:
        question = None

    # Chat input (built-in send button)
    question = question or st.chat_input(
        "Ask about BIS certifications, standards, or compliance…", key="home_chat"
    )

    if question:
        st.session_state.messages = st.session_state.get("messages", []) + [
            {"role": "user", "content": question}
        ]
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            try:
                # Use write_stream for efficient streaming (Streamlit 1.36+)
                full = st.write_stream(get_answer_stream(st.session_state.messages))
            except Exception as e:
                full = f"Unable to get an answer: {e}"
                st.markdown(full)
        st.session_state.messages.append({"role": "assistant", "content": full})
        st.rerun()

    # Sidebar (Home only)
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-title">Try asking</p>', unsafe_allow_html=True)
        for q in [
            "What is an ISI mark?",
            "How do I apply for BIS certification?",
            "What standard applies to two-wheeler helmets?",
            "What does hallmarking mean for gold?",
        ]:
            if st.button(q, key=f"sidebar_{q}", use_container_width=True):
                st.session_state.pending_question = q
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-title">Actions</p>', unsafe_allow_html=True)
        if st.button("🗑️ Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-title">Theme</p>', unsafe_allow_html=True)
        dark = st.toggle("Dark mode", value=False, key="dark_mode")
        st.markdown("</div>", unsafe_allow_html=True)


def render_categories() -> None:
    st.markdown(
        '<h2 style="margin-bottom:0.5rem;">📂 IS Code Explorer</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="caption">Browse 10 categories, 60+ products with IS standards and certification schemes. Click a card to explore.</p>',
        unsafe_allow_html=True,
    )

    cat_names = list(CATEGORIES.keys())
    selected_cat = st.selectbox(
        "Jump to category",
        ["All Categories"] + cat_names,
        label_visibility="collapsed",
        key="cat_select",
    )

    # Bento grid using Streamlit components
    cols_per_row = 3
    cat_items = list(CATEGORIES.items())

    for i in range(0, len(cat_items), cols_per_row):
        row_cols = st.columns(cols_per_row, gap="medium")
        for j, (cat_name, cat_data) in enumerate(cat_items[i : i + cols_per_row]):
            with row_cols[j]:
                if selected_cat != "All Categories" and cat_name != selected_cat:
                    continue

                items = cat_data["items"]
                icon = cat_data["icon"]
                scheme_counts: dict[str, int] = {}
                for info in items.values():
                    s = info["scheme"].split("/")[0].split(" ")[0]
                    scheme_counts[s] = scheme_counts.get(s, 0) + 1

                with st.container(border=True):
                    st.markdown(
                        f"""
                    <div class="bento-card">
                        <div class="bento-header">
                            <div>
                                <div class="bento-icon">{icon}</div>
                                <h3 class="bento-title">{cat_name}</h3>
                                <p class="bento-count">{len(items)} products · {len(scheme_counts)} schemes</p>
                            </div>
                            <span class="bento-badge">{len(items)} items</span>
                        </div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    # Preview items
                    preview_items = list(items.items())[:3]
                    for name, info in preview_items:
                        scheme_key = info["scheme"].split("/")[0].split(" ")[0]
                        scheme_class = SCHEME_STYLES.get(scheme_key, "scheme-other")
                        st.markdown(
                            f"""
                        <div class="bento-preview-item">
                            <span class="bento-preview-name">{name}</span>
                            <span class="bento-preview-scheme {scheme_class}">{info["scheme"].split("/")[0]}</span>
                        </div>""",
                            unsafe_allow_html=True,
                        )

                    if st.button(
                        "Explore", key=f"explore_{cat_name}", use_container_width=True
                    ):
                        st.session_state.expanded_category = cat_name
                        st.rerun()

    # Expanded category detail
    if st.session_state.get("expanded_category"):
        cat = st.session_state.expanded_category
        items = CATEGORIES[cat]["items"]
        icon = CATEGORIES[cat]["icon"]

        st.markdown("---")
        if st.button(
            "← Back to all categories", key="back_cats", use_container_width=False
        ):
            st.session_state.expanded_category = None
            st.rerun()

        st.markdown(
            f"""
        <div class="category-expanded">
            <h2 style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
                <div class="bento-icon">{icon}</div>
                <span style="margin:0;">{cat}</span>
            </h2>
            <p class="caption">{len(items)} products across multiple certification schemes</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        for name, info in items.items():
            scheme_key = info["scheme"].split("/")[0].split(" ")[0]
            scheme_class = SCHEME_STYLES.get(scheme_key, "scheme-other")

            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{name}**")
                st.caption(f"Scheme: `{info['scheme']}` | Standard: `{info['is']}`")
            with col2:
                if st.button("Ask", key=f"ask_{cat}_{name}", use_container_width=True):
                    st.session_state.pending_question = (
                        f"What is the certification process for {name}?"
                    )
                    # Switch to Home tab by letting main app handle it
                    st.rerun()


def render_checklists() -> None:
    st.markdown(
        '<h2 style="margin-bottom:0.5rem;">✅ Certification Checklists</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="caption">Track your compliance progress for each BIS scheme. Progress persists during your session.</p>',
        unsafe_allow_html=True,
    )

    if "checklist_progress" not in st.session_state:
        st.session_state.checklist_progress = {scheme: set() for scheme in CHECKLISTS}

    for scheme, steps in CHECKLISTS.items():
        completed = st.session_state.checklist_progress.get(scheme, set())
        progress = len(completed) / len(steps) if steps else 0
        progress_pct = int(progress * 100)

        if "ISI" in scheme:
            ring_color = "#1A4DB8"
        elif "CRS" in scheme:
            ring_color = "#2E7D32"
        elif "FMCS" in scheme:
            ring_color = "#E65100"
        else:
            ring_color = "#B45309"

        st.markdown(
            f'''
        <div class="checklist-card">
            <div class="checklist-header">
                <h3 class="checklist-title">{scheme}</h3>
                <div>
                    <svg class="progress-ring" viewBox="0 0 48 48">
                        <circle cx="24" cy="24" r="20" fill="none" stroke="var(--line)" stroke-width="4"/>
                        <circle cx="24" cy="24" r="20" fill="none" stroke="{ring_color}" stroke-width="4"
                                stroke-dasharray="125.6" stroke-dashoffset="{125.6 * (1 - progress)}"
                                stroke-linecap="round" transform="rotate(-90 24 24)"
                                style="transition: stroke-dashoffset 600ms cubic-bezier(0.34, 1.56, 0.64, 1);"/>
                    </svg>
                    <div class="checklist-progress">{progress_pct}% complete</div>
                </div>
            </div>
        ''',
            unsafe_allow_html=True,
        )

        for i, step in enumerate(steps):
            is_done = i in completed
            st.markdown(
                f'<div class="checklist-item {"completed" if is_done else ""}">',
                unsafe_allow_html=True,
            )
            if st.checkbox(
                f"{i + 1}. {step}",
                value=is_done,
                key=f"check_{scheme}_{i}",
                label_visibility="collapsed",
            ):
                if i not in completed:
                    completed.add(i)
                else:
                    completed.discard(i)
            st.session_state.checklist_progress[scheme] = completed
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def render_fee_calculator() -> None:
    st.markdown(
        '<h2 style="margin-bottom:0.5rem;">💰 BIS Fee Calculator</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="caption">Estimate annual marking fees with MSME concessions. Real-time calculation — no button needed.</p>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        scheme = st.selectbox(
            "Certification Scheme",
            ["ISI Mark (Scheme-I)", "CRS", "FMCS"],
            key="fee_scheme",
        )
        category = st.selectbox(
            "Enterprise Category",
            ["Micro/Startup", "Small", "Medium", "Large (no concession)"],
            key="fee_category",
        )
    with col2:
        production_value = st.number_input(
            "Annual Production Value (₹)",
            min_value=0,
            value=10000000,
            step=100000,
            key="fee_prod",
        )
        is_woman = st.checkbox("Women Entrepreneur", key="fee_woman")
        is_ne = st.checkbox("North-East State Unit", key="fee_ne")

    base_rates = {"ISI Mark (Scheme-I)": 0.005, "CRS": 0.002, "FMCS": 0.01}
    concessions = {
        "Micro/Startup": 0.8,
        "Small": 0.5,
        "Medium": 0.2,
        "Large (no concession)": 0.0,
    }
    base_rate = base_rates.get(scheme, 0.005)
    concession = concessions.get(category, 0.0)
    extra = 0.1 if (is_woman or is_ne) else 0.0
    total_concession = min(concession + extra, 0.9)
    base_fee = production_value * base_rate
    min_fee = 50000 if "ISI" in scheme else (25000 if "CRS" in scheme else 0)
    base_fee = max(base_fee, min_fee)
    concession_amount = base_fee * total_concession
    net_fee = base_fee - concession_amount

    st.markdown(
        f"""
    <div class="calc-result-card">
        <h3 class="calc-result-title">Fee Breakdown <span style="font-size:0.75rem;color:var(--gold);">({int(total_concession * 100)}% concession)</span></h3>
        <table class="result-table">
            <tr><td class="result-label">Base Marking Fee</td><td class="result-value">₹{base_fee:,.0f}</td></tr>
            <tr><td class="result-label">Concession ({int(total_concession * 100)}%)</td><td class="result-value">-₹{concession_amount:,.0f}</td></tr>
            <tr class="result-row-total"><td class="result-label">Net Marking Fee (Annual)</td><td class="result-value">₹{net_fee:,.0f}</td></tr>
        </table>
    """,
        unsafe_allow_html=True,
    )

    if "FMCS" in scheme:
        st.info(
            "FMCS fees payable in USD. Marking fee typically $0.50–$2/unit. Inspection charges (travel, daily allowance) additional."
        )
    st.markdown(
        '<p class="calc-note">Scrutiny fee (₹1,000 ISI/CRS, ₹5,000 FMCS) and license fee (₹1,000/year) separate. Verify latest fees on <a href="https://bis.gov.in/fee-structure" target="_blank" style="color:var(--gold);">bis.gov.in/fee-structure</a> before payment.</p>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ==================== MAIN APP ====================
def main() -> None:
    # Initialize session state
    DEFAULTS = {
        "active_tab": "home",
        "messages": [],
        "checklist_progress": {scheme: set() for scheme in CHECKLISTS},
        "expanded_category": None,
        "pending_question": None,
    }
    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Handle pending question from Categories tab
    if "pending_question" in st.session_state and st.session_state.pending_question:
        # Let Home tab handle it naturally

        # Native tabs
        tabs = st.tabs(
            ["🏠 Home", "📂 Categories", "✅ Checklists", "💰 Fee Calculator"]
        )

    with tabs[0]:
        render_home()
    with tabs[1]:
        render_categories()
    with tabs[2]:
        render_checklists()
    with tabs[3]:
        render_fee_calculator()

    # Footer
    st.markdown(
        """
    <hr style="margin:3rem 0 1.5rem;border:none;border-top:1px solid var(--line);">
    <p style="text-align:center;color:var(--slate-muted);font-size:0.8125rem;">
        Built for Smart India Hackathon 2026 — Team Cognivolt ✦
    </p>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

"""
app.py  –  mSIMU Gradio Interface
Entry point: python app.py
"""

import gradio as gr
from ui.tab_config    import build_config_tab
from ui.tab_manip     import build_manip_tab
from ui.tab_run       import build_run_tab
from ui.tab_reader    import build_reader_tab
from ui.tab_logs      import build_logs_tab

# ── Dark theme: override every Gradio 4.x CSS token ────────────────────────
DARK_THEME = gr.themes.Base(
    primary_hue=gr.themes.colors.cyan,
    secondary_hue=gr.themes.colors.slate,
    neutral_hue=gr.themes.colors.slate,
    font=[gr.themes.GoogleFont("Barlow"), "sans-serif"],
    font_mono=[gr.themes.GoogleFont("Share Tech Mono"), "monospace"],
).set(
    # ── canvas / surfaces ────────────────────────────────────────────────────
    body_background_fill="#0a0d12",
    body_background_fill_dark="#0a0d12",
    background_fill_primary="#10151e",
    background_fill_primary_dark="#10151e",
    background_fill_secondary="#161d2b",
    background_fill_secondary_dark="#161d2b",
    block_background_fill="#161d2b",
    block_background_fill_dark="#161d2b",
    # ── borders ──────────────────────────────────────────────────────────────
    border_color_primary="#2a3650",
    border_color_primary_dark="#2a3650",
    block_border_color="#2a3650",
    block_border_color_dark="#2a3650",
    block_border_width="1px",
    # ── text ─────────────────────────────────────────────────────────────────
    body_text_color="#c8d8e8",
    body_text_color_dark="#c8d8e8",
    body_text_color_subdued="#5a7090",
    body_text_color_subdued_dark="#5a7090",
    block_label_text_color="#5a7090",
    block_label_text_color_dark="#5a7090",
    block_title_text_color="#c8d8e8",
    block_title_text_color_dark="#c8d8e8",
    # ── inputs ───────────────────────────────────────────────────────────────
    input_background_fill="#1e2738",
    input_background_fill_dark="#1e2738",
    input_background_fill_focus="#1e2738",
    input_background_fill_focus_dark="#1e2738",
    input_border_color="#2a3650",
    input_border_color_dark="#2a3650",
    input_border_color_focus="#00d4ff",
    input_border_color_focus_dark="#00d4ff",
    input_placeholder_color="#5a7090",
    input_placeholder_color_dark="#5a7090",
    # ── buttons ──────────────────────────────────────────────────────────────
    button_primary_background_fill="#003c55",
    button_primary_background_fill_dark="#003c55",
    button_primary_background_fill_hover="#00d4ff",
    button_primary_background_fill_hover_dark="#00d4ff",
    button_primary_text_color="#00d4ff",
    button_primary_text_color_dark="#00d4ff",
    button_primary_text_color_hover="#0a0d12",
    button_primary_text_color_hover_dark="#0a0d12",
    button_primary_border_color="#00d4ff",
    button_primary_border_color_dark="#00d4ff",
    button_secondary_background_fill="#161d2b",
    button_secondary_background_fill_dark="#161d2b",
    button_secondary_background_fill_hover="#1e2738",
    button_secondary_background_fill_hover_dark="#1e2738",
    button_secondary_text_color="#c8d8e8",
    button_secondary_text_color_dark="#c8d8e8",
    button_secondary_border_color="#2a3650",
    button_secondary_border_color_dark="#2a3650",
    # ── shadows / radius ─────────────────────────────────────────────────────
    block_shadow="none",
    block_shadow_dark="none",
    container_radius="6px",
    block_radius="6px",
    input_radius="4px",
    button_large_radius="4px",
    button_small_radius="4px",
    # ── table ─────────────────────────────────────────────────────────────────
    table_even_background_fill="#161d2b",
    table_even_background_fill_dark="#161d2b",
    table_odd_background_fill="#10151e",
    table_odd_background_fill_dark="#10151e",
    table_border_color="#2a3650",
    table_border_color_dark="#2a3650",
    # ── code block ───────────────────────────────────────────────────────────
    code_background_fill="#0d1117",
    code_background_fill_dark="#0d1117",
    # ── checkbox / slider ────────────────────────────────────────────────────
    checkbox_background_color="#1e2738",
    checkbox_background_color_dark="#1e2738",
    checkbox_background_color_focus="#1e2738",
    checkbox_background_color_focus_dark="#1e2738",
    checkbox_background_color_selected="#00d4ff",
    checkbox_background_color_selected_dark="#00d4ff",
    checkbox_border_color="#2a3650",
    checkbox_border_color_dark="#2a3650",
    checkbox_border_color_focus="#00d4ff",
    checkbox_border_color_focus_dark="#00d4ff",
    checkbox_border_color_selected="#00d4ff",
    checkbox_border_color_selected_dark="#00d4ff",
    checkbox_label_background_fill="#161d2b",
    checkbox_label_background_fill_dark="#161d2b",
    checkbox_label_background_fill_selected="#1e2738",
    checkbox_label_background_fill_selected_dark="#1e2738",
    slider_color="#00d4ff",
    slider_color_dark="#00d4ff",
    # ── stat cards ───────────────────────────────────────────────────────────
    stat_background_fill="#161d2b",
    stat_background_fill_dark="#161d2b",
)

# ── Supplemental CSS: plug every remaining gap ──────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Barlow:wght@300;400;600;700&display=swap');

:root {
    --bg0:      #0a0d12;
    --bg1:      #10151e;
    --bg2:      #161d2b;
    --bg3:      #1e2738;
    --border:   #2a3650;
    --accent:   #00d4ff;
    --accent2:  #ff6b35;
    --green:    #00ff88;
    --red:      #ff3860;
    --text:     #c8d8e8;
    --text-dim: #5a7090;
    --mono:     'Share Tech Mono', monospace;
    --sans:     'Barlow', sans-serif;
}

/* ── nuke any residual white surfaces ───────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body,
.gradio-container,
.gradio-container > div,
footer,
.wrap, .gap, .form,
.block, .block.padded,
.tabitem, .tab-content,
.prose,
.svelte-1ed2p3z      /* common Gradio wrapper hash */
{
    background-color: var(--bg0) !important;
    color: var(--text) !important;
}

/* ── top-level page chrome ──────────────────────────────────────────────── */
.gradio-container { max-width: 1600px !important; padding: 12px !important; }

/* ── all block containers ───────────────────────────────────────────────── */
.block, .block.padded, .form, .box {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    box-shadow: none !important;
}

/* ── tab bar ────────────────────────────────────────────────────────────── */
.tab-nav, .tab-nav > div {
    background: var(--bg1) !important;
    border-bottom: 1px solid var(--border) !important;
}
.tab-nav button {
    background: var(--bg1) !important;
    color: var(--text-dim) !important;
    border: 1px solid var(--border) !important;
    border-bottom: none !important;
    font-family: var(--mono) !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.08em !important;
    padding: 8px 18px !important;
    transition: all .15s;
}
.tab-nav button.selected {
    background: var(--bg2) !important;
    color: var(--accent) !important;
    border-top: 2px solid var(--accent) !important;
}
.tab-nav button:hover:not(.selected) { color: var(--text) !important; }

/* ── all input surfaces ─────────────────────────────────────────────────── */
input, input[type="text"], input[type="number"], input[type="search"],
textarea,
select,
.input-wrap, .wrap-inner,
[data-testid="textbox"] textarea,
[data-testid="dropdown"] input,
[data-testid="dropdown"] .wrap,
.dropdown-wrap,
.multiselect,
.token-label,
.svelte-input { 
    background: var(--bg3) !important;
    background-color: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: var(--mono) !important;
    font-size: 0.82rem !important;
    border-radius: 4px !important;
}
input:focus, textarea:focus {
    border-color: var(--accent) !important;
    outline: none !important;
    box-shadow: 0 0 0 2px rgba(0,212,255,0.15) !important;
}

/* ── dropdown popup list ────────────────────────────────────────────────── */
ul.options, .options, .option,
[data-testid="dropdown-options"],
.dropdown > .wrap > ul,
.listbox, .listbox li {
    background: var(--bg3) !important;
    background-color: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
}
.option:hover, .listbox li:hover, .option.selected {
    background: var(--border) !important;
    color: var(--accent) !important;
}

/* ── labels ─────────────────────────────────────────────────────────────── */
label, .block > label, span.svelte-1b6s6s, .label-wrap span {
    color: var(--text-dim) !important;
    font-size: 0.75rem !important;
    font-family: var(--mono) !important;
    background: transparent !important;
}

/* ── checkboxes ─────────────────────────────────────────────────────────── */
.checkbox-group label, .checkbox label {
    background: var(--bg2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
}
.checkbox input[type=checkbox], .checkbox-group input[type=checkbox] {
    accent-color: var(--accent);
}

/* ── code blocks (JSON viewer) ──────────────────────────────────────────── */
.code-wrap, code, pre,
[data-testid="code"] .wrap,
[data-testid="code"] textarea,
.cm-editor, .cm-content, .cm-gutters,
.codemirror-wrapper, .codemirror-wrapper .cm-editor {
    background: #0d1117 !important;
    background-color: #0d1117 !important;
    color: #7dcfff !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    font-family: var(--mono) !important;
    font-size: 0.8rem !important;
}
.cm-gutters { background: #0a0e15 !important; border-right: 1px solid var(--border) !important; }
.cm-activeLineGutter, .cm-activeLine { background: rgba(0,212,255,0.05) !important; }
.cm-lineNumbers .cm-gutterElement { color: var(--text-dim) !important; }

/* ── buttons ────────────────────────────────────────────────────────────── */
button { font-family: var(--mono) !important; letter-spacing: 0.08em !important; }

.btn-primary, .btn-primary button {
    background: linear-gradient(135deg, #003c55, #005f7f) !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
    border-radius: 4px !important;
    transition: all .15s !important;
}
.btn-primary:hover, .btn-primary button:hover {
    background: var(--accent) !important;
    color: var(--bg0) !important;
}
.btn-danger, .btn-danger button {
    background: linear-gradient(135deg, #3a0010, #5f0020) !important;
    border: 1px solid var(--red) !important;
    color: var(--red) !important;
    border-radius: 4px !important;
}
.btn-danger:hover, .btn-danger button:hover {
    background: var(--red) !important; color: var(--bg0) !important;
}
.btn-success, .btn-success button {
    background: linear-gradient(135deg, #003d20, #006633) !important;
    border: 1px solid var(--green) !important;
    color: var(--green) !important;
    border-radius: 4px !important;
}
.btn-success:hover, .btn-success button:hover {
    background: var(--green) !important; color: var(--bg0) !important;
}

/* ── console / log output textboxes ────────────────────────────────────── */
.console-out textarea,
.console-out input,
.console-out .wrap,
.console-out {
    background: #050810 !important;
    background-color: #050810 !important;
    border: 1px solid var(--border) !important;
    color: #7fff9a !important;
    font-family: var(--mono) !important;
    font-size: 0.78rem !important;
    border-radius: 4px !important;
}

/* ── plot container ─────────────────────────────────────────────────────── */
.plot-container, .plot-container > div, .matplotlib, canvas {
    background: var(--bg1) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
}

/* ── scrollbars ─────────────────────────────────────────────────────────── */
::-webkit-scrollbar       { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg1); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ── panel titles (our custom HTML) ─────────────────────────────────────── */
.panel-title {
    font-family: var(--mono);
    font-size: 0.68rem;
    letter-spacing: 0.15em;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border);
}

/* ── header banner ──────────────────────────────────────────────────────── */
#msim-header {
    background: linear-gradient(135deg, var(--bg2), var(--bg3)) !important;
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    padding: 18px 24px;
    margin-bottom: 16px;
    border-radius: 4px;
    font-family: var(--mono);
}
#msim-header h1 { font-size: 1.6rem; color: var(--accent); letter-spacing: 0.12em; margin: 0; }
#msim-header p  { font-size: 0.72rem; color: var(--text-dim); margin: 4px 0 0 0; letter-spacing: 0.08em; }

/* ── Gradio footer (version text) ───────────────────────────────────────── */
footer { display: none !important; }
"""

# ── Build UI ─────────────────────────────────────────────────────────────────
with gr.Blocks(css=CSS, title="mSIMU Interface", theme=DARK_THEME) as demo:

    gr.HTML("""
        <div id="msim-header">
            <h1>▸ mSIMU</h1>
            <p>MAGNETIC SIMULATOR · DRONE TRAJECTORY ENGINE · SENSOR ARRAY TOOLBOX</p>
        </div>
    """)

    with gr.Tabs():
        with gr.Tab("⬡  CONFIG VIEWER"):
            build_config_tab()
        with gr.Tab("⬡  NEW EXPERIMENT"):
            build_manip_tab()
        with gr.Tab("▶  RUN SIMULATION"):
            build_run_tab()
        with gr.Tab("⬡  READER / CSV"):
            build_reader_tab()
        with gr.Tab("⬡  LOGS VIEWER"):
            build_logs_tab()


if __name__ == "__main__":
    demo.launch(share=False, server_port=7860)
"""
ui/tab_reader.py  –  Reader / CSV Conversion Tab

Wraps run_reader.py:
  • Auto-discovers sensor names from the log's metadata.json → experiment JSON
  • Supports gradiometer mode (2 sensor names → difference)
  • Streams subprocess output into console
  • Shows a quick preview plot of the generated CSV
"""

from __future__ import annotations
import subprocess
import sys
import threading
import queue
import gradio as gr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

from ui.helpers import (
    list_log_dirs, read_log_metadata, get_log_sensor_names, ROOT,
)


_q: queue.Queue = queue.Queue()

BG0  = "#0a0d12"; BG1 = "#10151e"; BG2 = "#161d2b"
CYAN = "#00d4ff"; ORNG = "#ff6b35"; GREEN = "#00ff88"
RED  = "#ff3860"; GREY = "#3a4a60"; TEXT = "#c8d8e8"


# ── helpers ───────────────────────────────────────────────────────────────────
def _load_log_info(log_dir: str) -> tuple[str, list[str]]:
    """Returns (info_text, sensor_names)."""
    if not log_dir:
        return "— select a log folder —", []
    meta    = read_log_metadata(log_dir)
    sensors = get_log_sensor_names(log_dir)
    p       = Path(log_dir)
    csv_files = list(p.glob("manip*.csv"))

    lines = [
        f"Log folder : {log_dir}",
        f"Exp name   : {meta.get('experiment_name','?')}",
        f"Created    : {meta.get('created_at','?')}",
        f"Sensors    : {sensors}",
        "",
        "CSV files present:",
    ]
    if csv_files:
        for c in csv_files:
            lines.append(f"  ✓ {c.name}")
    else:
        lines.append("  (none yet — run reader to generate)")
    return "\n".join(lines), sensors


def _stream(proc: subprocess.Popen):
    for line in iter(proc.stdout.readline, b""):
        _q.put(line.decode("utf-8", errors="replace"))
    proc.wait()
    _q.put(f"\n[Process exited with code {proc.returncode}]\n")


def run_reader(log_dir: str, sensor_sel: list[str], gradiometer: bool):
    """Generator – yields console text while reader runs."""
    if not log_dir:
        yield "✗ No log folder selected.\n"; return
    if not sensor_sel:
        yield "✗ No sensors selected.\n"; return

    while not _q.empty():
        _q.get_nowait()

    cmd = [sys.executable, str(ROOT / "run_reader.py"), log_dir]
    cmd += ["--sensor_names"] + sensor_sel
    if gradiometer:
        cmd += ["--gradiometer"]

    yield f"▶ {' '.join(cmd)}\n"

    try:
        proc = subprocess.Popen(
            cmd, cwd=str(ROOT),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1,
        )
    except Exception as e:
        yield f"✗ {e}\n"; return

    t = threading.Thread(target=_stream, args=(proc,), daemon=True)
    t.start()

    buf = ""
    while t.is_alive() or not _q.empty():
        try:
            buf += _q.get(timeout=0.1)
            yield buf
        except queue.Empty:
            pass
    while not _q.empty():
        buf += _q.get_nowait()
    yield buf


def plot_csv_preview(log_dir: str, gradiometer: bool):
    """Plot manip(_gradio).csv from the selected log folder."""
    if not log_dir:
        return None
    suffix = "_gradio" if gradiometer else ""
    csv_path = Path(log_dir) / f"manip{suffix}.csv"
    if not csv_path.exists():
        # try the other variant
        alt = Path(log_dir) / ("manip.csv" if gradiometer else "manip_gradio.csv")
        if alt.exists():
            csv_path = alt
        else:
            return None

    try:
        df = pd.read_csv(csv_path)
    except Exception:
        return None

    mag_cols = [c for c in df.columns if c.startswith("mag") and not c.startswith("magx")
                and not c.startswith("magy") and not c.startswith("magz")]

    colours = [CYAN, ORNG, GREEN, "#b060ff", "#ffcc00"]
    n_plots = 1 + (1 if mag_cols else 0)   # trajectory + magnitude(s)
    fig, axes = plt.subplots(n_plots, 1, figsize=(11, 4 * n_plots),
                             facecolor=BG0, tight_layout=True)
    if n_plots == 1:
        axes = [axes]
    fig.patch.set_facecolor(BG0)

    def _style(ax, title, xlabel, ylabel):
        ax.set_facecolor(BG1)
        ax.spines[:].set_color(GREY)
        ax.tick_params(colors=TEXT, labelsize=7)
        for lab in [ax.xaxis.label, ax.yaxis.label]:
            lab.set_color(TEXT)
        ax.set_xlabel(xlabel, fontsize=8)
        ax.set_ylabel(ylabel, fontsize=8)
        ax.set_title(title, color=CYAN, fontsize=9, fontfamily="monospace")
        ax.grid(color=GREY, linewidth=0.4, alpha=0.5)

    # trajectory
    if "longitude" in df.columns and "latitude" in df.columns:
        ax0 = axes[0]
        _style(ax0, "DRONE TRAJECTORY  (from log)", "Longitude [°]", "Latitude [°]")
        ax0.plot(df["longitude"], df["latitude"], color=CYAN, lw=0.8)
        ax0.scatter(df["longitude"].iloc[0],  df["latitude"].iloc[0],
                    color=GREEN, s=40, zorder=5, label="start")
        ax0.scatter(df["longitude"].iloc[-1], df["latitude"].iloc[-1],
                    color=RED, marker="x", s=60, linewidths=2, zorder=5, label="end")
        ax0.legend(facecolor=BG2, edgecolor=GREY, labelcolor=TEXT, fontsize=7)

    # magnitudes
    if mag_cols and len(axes) > 1:
        ax1 = axes[1]
        _style(ax1, "MAGNETIC FIELD MAGNITUDE", "Sample index", "Magnitude [nT]")
        for i, col in enumerate(mag_cols):
            ax1.plot(df[col], color=colours[i % len(colours)],
                     lw=0.8, label=col)
        ax1.legend(facecolor=BG2, edgecolor=GREY, labelcolor=TEXT, fontsize=7)

    return fig


# ── TAB BUILDER ───────────────────────────────────────────────────────────────
def build_reader_tab():
    with gr.Row():
        # ── Left: controls ────────────────────────────────────────────────────
        with gr.Column(scale=1, min_width=300):
            gr.HTML('<div class="panel-title">SELECT LOG FOLDER</div>')

            log_dd = gr.Dropdown(
                choices=list_log_dirs(), label="Log directory", interactive=True,
            )
            refresh_btn = gr.Button("↺  Refresh", elem_classes=["btn-primary"])

            gr.HTML('<div class="panel-title" style="margin-top:10px">LOG INFO</div>')
            log_info = gr.Textbox(label="", lines=8, interactive=False,
                                  elem_classes=["console-out"])

            gr.HTML('<div class="panel-title" style="margin-top:10px">READER SETTINGS</div>')
            sensor_cb = gr.CheckboxGroup(
                choices=[], label="Sensor names (auto-detected)",
                interactive=True,
            )
            gradio_mode = gr.Checkbox(label="Gradiometer mode (2 sensors → difference)",
                                      value=False)

            with gr.Row():
                run_btn    = gr.Button("▶  Run reader",   elem_classes=["btn-success"])
                plot_btn   = gr.Button("📈  Preview CSV", elem_classes=["btn-primary"])

        # ── Right: console + plot ─────────────────────────────────────────────
        with gr.Column(scale=3):
            gr.HTML('<div class="panel-title">READER CONSOLE</div>')
            console = gr.Textbox(label="", lines=10, interactive=False,
                                 elem_classes=["console-out"], autoscroll=True)

            gr.HTML('<div class="panel-title" style="margin-top:10px">CSV PREVIEW</div>')
            csv_plot = gr.Plot(label="")

    # ── Event wiring ──────────────────────────────────────────────────────────
    def refresh():
        return gr.Dropdown(choices=list_log_dirs())

    def on_log_select(log_dir):
        info, sensors = _load_log_info(log_dir)
        return info, gr.CheckboxGroup(choices=sensors, value=sensors)

    refresh_btn.click(refresh, outputs=[log_dd])
    log_dd.change(on_log_select, inputs=[log_dd], outputs=[log_info, sensor_cb])

    run_btn.click(run_reader, inputs=[log_dd, sensor_cb, gradio_mode], outputs=[console])
    plot_btn.click(plot_csv_preview, inputs=[log_dd, gradio_mode], outputs=[csv_plot])
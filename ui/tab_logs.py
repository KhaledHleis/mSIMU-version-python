"""
ui/tab_logs.py  –  Logs Viewer Tab

Lets the user:
  • Browse all experiment log folders
  • View metadata + CSV status
  • Plot magnetic field components and trajectory from manip*.csv
  • If no CSV exists, show a one-click button that triggers the reader
"""

from __future__ import annotations
import subprocess
import sys
import gradio as gr
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
from pathlib import Path

from ui.helpers import (
    list_log_dirs, read_log_metadata, get_log_sensor_names, ROOT,
)


BG0  = "#0a0d12"; BG1 = "#10151e"; BG2 = "#161d2b"
CYAN = "#00d4ff"; ORNG = "#ff6b35"; GREEN = "#00ff88"
RED  = "#ff3860"; GREY = "#3a4a60"; TEXT = "#c8d8e8"
COLS = [CYAN, ORNG, GREEN, "#b060ff", "#ffcc00", "#ff80a0"]


def _style(ax, title="", xlabel="", ylabel=""):
    ax.set_facecolor(BG1)
    ax.spines[:].set_color(GREY)
    ax.tick_params(colors=TEXT, labelsize=7)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    if xlabel: ax.set_xlabel(xlabel, fontsize=8)
    if ylabel: ax.set_ylabel(ylabel, fontsize=8)
    if title:  ax.set_title(title, color=CYAN, fontsize=9, fontfamily="monospace")
    ax.grid(color=GREY, linewidth=0.4, alpha=0.5)


# ── Metadata summary ──────────────────────────────────────────────────────────
def log_summary(log_dir: str) -> str:
    if not log_dir:
        return "— select a log folder —"
    meta    = read_log_metadata(log_dir)
    sensors = get_log_sensor_names(log_dir)
    p       = Path(log_dir)
    drone_jsons = list(p.glob("drone/*.json"))
    world_jsons = list(p.glob("world/*.json"))
    csv_files   = sorted(p.glob("manip*.csv"))

    lines = [
        f"┌─ LOG FOLDER: {log_dir}",
        f"│  experiment_name : {meta.get('experiment_name','?')}",
        f"│  created_at      : {meta.get('created_at','?')}",
        f"│  description     : {meta.get('description','') or '—'}",
        f"│  sensors detected: {sensors}",
        f"│  drone JSON batch: {len(drone_jsons)} file(s)",
        f"│  world JSON batch: {len(world_jsons)} file(s)",
        "├─ CSV FILES:",
    ]
    if csv_files:
        for c in csv_files:
            size_kb = c.stat().st_size // 1024
            lines.append(f"│    ✓ {c.name}  ({size_kb} kB)")
    else:
        lines.append("│    ✗ none — run the reader first")
    lines.append("└─")
    return "\n".join(lines)


# ── Plot all channels from CSV ────────────────────────────────────────────────
def plot_log(log_dir: str, csv_choice: str) -> plt.Figure | None:
    if not log_dir or not csv_choice:
        return None
    csv_path = Path(log_dir) / csv_choice
    if not csv_path.exists():
        return None

    try:
        df = pd.read_csv(csv_path)
    except Exception:
        return None

    # detect component columns per sensor
    # naming: magx, magy, magz, mag   OR   magx_sname, magy_sname, magz_sname, mag_sname
    base_names = set()
    for c in df.columns:
        if c.startswith("magx_"):
            base_names.add(c[5:])
    if not base_names and "magx" in df.columns:
        base_names.add("")   # single-sensor, no suffix

    n_sensors = len(base_names) if base_names else 0
    n_rows = 2 + n_sensors   # trajectory, magnitude(s), then components per sensor

    fig = plt.figure(figsize=(12, 3.5 * n_rows), facecolor=BG0)
    fig.patch.set_facecolor(BG0)
    gs = GridSpec(n_rows, 1, figure=fig, hspace=0.45)

    t = df.get("timestamp", pd.RangeIndex(len(df)))

    # ── row 0: trajectory ─────────────────────────────────────────────────────
    ax0 = fig.add_subplot(gs[0])
    _style(ax0, "DRONE TRAJECTORY", "Longitude [°]", "Latitude [°]")
    if "longitude" in df.columns and "latitude" in df.columns:
        scatter = ax0.scatter(
            df["longitude"], df["latitude"],
            c=np.arange(len(df)), cmap="plasma", s=1.5, linewidths=0,
        )
        cb = fig.colorbar(scatter, ax=ax0, pad=0.02)
        cb.ax.tick_params(colors=TEXT, labelsize=6)
        ax0.scatter(df["longitude"].iloc[0],  df["latitude"].iloc[0],
                    color=GREEN, s=50, zorder=5, label="start")
        ax0.scatter(df["longitude"].iloc[-1], df["latitude"].iloc[-1],
                    color=RED, marker="x", s=70, lw=2, zorder=5, label="end")
        ax0.legend(facecolor=BG2, edgecolor=GREY, labelcolor=TEXT, fontsize=7)

    # ── row 1: magnetic magnitude ──────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[1])
    _style(ax1, "MAGNETIC MAGNITUDE", "sample", "‖B‖ [nT]")
    for i, name in enumerate(sorted(base_names)):
        suffix = f"_{name}" if name else ""
        col = f"mag{suffix}"
        if col in df.columns:
            ax1.plot(t, df[col], color=COLS[i % len(COLS)], lw=0.7,
                     label=col if name else "mag")
    ax1.legend(facecolor=BG2, edgecolor=GREY, labelcolor=TEXT, fontsize=7)

    # ── rows 2+: XYZ components per sensor ────────────────────────────────────
    comp_labels = [("magx", "Bx [nT]"), ("magy", "By [nT]"), ("magz", "Bz [nT]")]
    for row_i, name in enumerate(sorted(base_names), start=2):
        suffix = f"_{name}" if name else ""
        ax = fig.add_subplot(gs[row_i])
        _style(ax, f"COMPONENTS{(' · ' + name) if name else ''}", "sample", "B [nT]")
        for j, (comp, ylabel) in enumerate(comp_labels):
            col = f"{comp}{suffix}"
            if col in df.columns:
                ax.plot(t, df[col], color=COLS[j], lw=0.7, label=comp)
        ax.legend(facecolor=BG2, edgecolor=GREY, labelcolor=TEXT, fontsize=7)

    fig.suptitle(f"{csv_path.parent.name}  /  {csv_choice}",
                 color=TEXT, fontsize=10, fontfamily="monospace", y=1.005)
    return fig


def auto_generate_csv(log_dir: str) -> str:
    """Run reader with all auto-detected sensors; return short status."""
    if not log_dir:
        return "✗ No log folder selected."
    sensors = get_log_sensor_names(log_dir)
    if not sensors:
        return "✗ Could not detect sensor names."
    cmd = [sys.executable, str(ROOT / "run_reader.py"), log_dir,
           "--sensor_names"] + sensors
    try:
        res = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=300)
        out = (res.stdout + res.stderr).strip()
        if res.returncode == 0:
            return f"✓ Reader finished.\n{out}"
        return f"✗ Reader failed (code {res.returncode}).\n{out}"
    except subprocess.TimeoutExpired:
        return "✗ Timeout — simulation logs may be very large."
    except Exception as e:
        return f"✗ {e}"


def get_csv_choices(log_dir: str) -> list[str]:
    if not log_dir:
        return []
    return sorted(p.name for p in Path(log_dir).glob("manip*.csv"))


# ── TAB BUILDER ───────────────────────────────────────────────────────────────
def build_logs_tab():
    with gr.Row():
        # ── Left: selector + metadata ─────────────────────────────────────────
        with gr.Column(scale=1, min_width=300):
            gr.HTML('<div class="panel-title">SELECT LOG FOLDER</div>')
            log_dd = gr.Dropdown(
                choices=list_log_dirs(), label="Experiment log", interactive=True,
            )
            refresh_btn = gr.Button("↺  Refresh", elem_classes=["btn-primary"])

            gr.HTML('<div class="panel-title" style="margin-top:10px">LOG SUMMARY</div>')
            summary_out = gr.Textbox(label="", lines=14, interactive=False,
                                     elem_classes=["console-out"])

            gr.HTML('<div class="panel-title" style="margin-top:10px">CSV FILE</div>')
            csv_dd = gr.Dropdown(choices=[], label="Select CSV", interactive=True)

            with gr.Row():
                plot_btn = gr.Button("📈  Plot", elem_classes=["btn-success"])
                gen_btn  = gr.Button("⚙  Generate CSV", elem_classes=["btn-primary"])

            gen_status = gr.Textbox(label="", lines=3, interactive=False,
                                    elem_classes=["console-out"])

        # ── Right: plot ───────────────────────────────────────────────────────
        with gr.Column(scale=3):
            gr.HTML('<div class="panel-title">LOG VISUALISATION</div>')
            log_plot = gr.Plot(label="")

    # ── Event wiring ──────────────────────────────────────────────────────────
    def refresh():
        return gr.Dropdown(choices=list_log_dirs())

    def on_log_select(log_dir):
        summary = log_summary(log_dir)
        choices = get_csv_choices(log_dir)
        return summary, gr.Dropdown(choices=choices, value=choices[0] if choices else None)

    def on_generate(log_dir):
        status = auto_generate_csv(log_dir)
        choices = get_csv_choices(log_dir)
        return status, gr.Dropdown(choices=choices, value=choices[0] if choices else None)

    refresh_btn.click(refresh, outputs=[log_dd])
    log_dd.change(on_log_select, inputs=[log_dd], outputs=[summary_out, csv_dd])
    gen_btn.click(on_generate, inputs=[log_dd], outputs=[gen_status, csv_dd])
    plot_btn.click(plot_log, inputs=[log_dd, csv_dd], outputs=[log_plot])
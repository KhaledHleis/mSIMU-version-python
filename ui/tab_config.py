"""
ui/tab_config.py  –  Configuration Viewer Tab
Lets the user inspect:
  • Drone sensor layout (relative positions, names, types)
  • Trajectory on a 2-D lon/lat plot
  • World cables / dipoles on the same plot
"""

from __future__ import annotations
import json
import gradio as gr
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import MaxNLocator

from ui.helpers import (
    list_drones, list_worlds, list_trajectories,
    load_drone, load_world, read_trajectory_sample, pretty_json,
)


# ── colour palette for dark plots ────────────────────────────────────────────
BG0   = "#0a0d12"
BG1   = "#10151e"
BG2   = "#161d2b"
CYAN  = "#00d4ff"
ORNG  = "#ff6b35"
GREEN = "#00ff88"
RED   = "#ff3860"
GREY  = "#3a4a60"
TEXT  = "#c8d8e8"


def _style_axes(ax, title="", xlabel="", ylabel=""):
    ax.set_facecolor(BG1)
    ax.spines[:].set_color(GREY)
    ax.tick_params(colors=TEXT, labelsize=7)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    if xlabel: ax.set_xlabel(xlabel, fontsize=8)
    if ylabel: ax.set_ylabel(ylabel, fontsize=8)
    if title:  ax.set_title(title, color=CYAN, fontsize=9, fontfamily="monospace")
    ax.grid(color=GREY, linewidth=0.4, alpha=0.5)


# ── drone sensor visualisation ───────────────────────────────────────────────
def plot_drone_sensors(drone_path: str):
    """Return a matplotlib figure showing sensor positions relative to drone body."""
    data = load_drone(drone_path)
    if not data or "sensors" not in data:
        fig, ax = plt.subplots(facecolor=BG0)
        ax.text(0.5, 0.5, "No drone loaded", ha="center", va="center",
                color=RED, fontsize=12, transform=ax.transAxes)
        ax.set_facecolor(BG0)
        return fig

    sensors = data["sensors"]
    fig, (ax_top, ax_side) = plt.subplots(1, 2, figsize=(10, 4.5),
                                           facecolor=BG0, tight_layout=True)
    fig.patch.set_facecolor(BG0)

    colours = [CYAN, ORNG, GREEN, RED, "#b060ff", "#ffcc00"]
    pos_array = [s["relative_position"] for s in sensors]

    # relative_position = [North, East, Down]  →  index 0=N, 1=E, 2=D
    for view_idx, (ax, (xi, yi, lbl_x, lbl_y, title)) in enumerate(zip(
        [ax_top, ax_side],
        [(1, 0, "East offset [m]", "North offset [m]", "TOP VIEW  (N-E plane)"),
         (0, 2, "North offset [m]", "Down offset [m]",  "SIDE VIEW  (N-D plane)")]
    )):
        _style_axes(ax, title=title, xlabel=lbl_x, ylabel=lbl_y)
        # drone body reference
        ax.scatter([0], [0], marker="D", s=200, color=BG2, edgecolors=GREY,
                   linewidths=1.5, zorder=4, label="drone CoG")
        for i, s in enumerate(sensors):
            p = s["relative_position"]
            c = colours[i % len(colours)]
            ax.scatter(p[xi], p[yi], s=120, color=c, edgecolors="white",
                       linewidths=0.8, zorder=5)
            # offset arrow from CoG
            if abs(p[xi]) + abs(p[yi]) > 1e-6:
                ax.annotate("", xy=(p[xi], p[yi]), xytext=(0, 0),
                            arrowprops=dict(arrowstyle="->", color=c, lw=1.2))
            ax.annotate(f" {s['name']}\n [{s['type']}]",
                        xy=(p[xi], p[yi]),
                        color=c, fontsize=7, fontfamily="monospace",
                        xytext=(5, 5), textcoords="offset points")

        # axes decoration
        ax.axhline(0, color=GREY, lw=0.6, ls="--")
        ax.axvline(0, color=GREY, lw=0.6, ls="--")
        ax.xaxis.set_major_locator(MaxNLocator(5))
        ax.yaxis.set_major_locator(MaxNLocator(5))
        margin = 0.5
        all_x = [p[xi] for p in pos_array] + [0]
        all_y = [p[yi] for p in pos_array] + [0]
        ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
        ax.set_ylim(min(all_y) - margin, max(all_y) + margin)

    fig.suptitle(f"Drone: {data.get('name', '?')} · {len(sensors)} sensor(s)",
                 color=TEXT, fontsize=10, fontfamily="monospace")
    return fig


# ── trajectory + world visualisation ─────────────────────────────────────────
def plot_world_trajectory(world_path: str, traj_path: str):
    """Return a matplotlib figure with cables, dipoles, and trajectory overlaid."""
    fig, ax = plt.subplots(figsize=(10, 7), facecolor=BG0, tight_layout=True)
    fig.patch.set_facecolor(BG0)
    _style_axes(ax, title="WORLD  +  TRAJECTORY", xlabel="Longitude [°]", ylabel="Latitude [°]")
    legend_handles = []

    # ── trajectory ────────────────────────────────────────────────────────────
    if traj_path:
        df = read_trajectory_sample(traj_path, n=3000)
        if df is not None and "longitude" in df.columns:
            ax.plot(df["longitude"], df["latitude"], color=CYAN, lw=0.9,
                    alpha=0.7, label="Trajectory")
            ax.scatter(df["longitude"].iloc[0],  df["latitude"].iloc[0],
                       color=GREEN, s=60, zorder=6, label="Start")
            ax.scatter(df["longitude"].iloc[-1], df["latitude"].iloc[-1],
                       color=RED, marker="x", s=80, linewidths=2, zorder=6, label="End")
            legend_handles += [
                mpatches.Patch(color=CYAN,  label="Trajectory"),
                mpatches.Patch(color=GREEN, label="Start"),
                mpatches.Patch(color=RED,   label="End"),
            ]

    # ── world ─────────────────────────────────────────────────────────────────
    if world_path:
        world = load_world(world_path)
        if world:
            ref_lon = world.get("reference_longitude", 0)
            ref_lat = world.get("reference_latitude", 0)

            # reference point
            ax.scatter([ref_lon], [ref_lat], marker="+", s=150, color=TEXT,
                       linewidths=1.5, zorder=7, label="Reference point")
            legend_handles.append(mpatches.Patch(color=TEXT, label="Ref. point"))

            # cables
            for cab in world.get("cables", []):
                lons = [cab["starting_longitude"], cab["ending_longitude"]]
                lats = [cab["starting_latitude"],  cab["ending_latitude"]]
                ax.plot(lons, lats, color=ORNG, lw=2.5, zorder=5, solid_capstyle="round")
                mid_lon = (lons[0] + lons[1]) / 2
                mid_lat = (lats[0] + lats[1]) / 2
                ax.annotate(cab["name"], xy=(mid_lon, mid_lat),
                            color=ORNG, fontsize=7, fontfamily="monospace",
                            xytext=(4, 4), textcoords="offset points")
            if world.get("cables"):
                legend_handles.append(mpatches.Patch(color=ORNG, label="Cable"))

            # dipoles
            for dip in world.get("dipoles", []):
                ax.scatter([dip["center_longitude"]], [dip["center_latitude"]],
                           marker="*", s=200, color="#b060ff", zorder=6)
                ax.annotate(dip["name"],
                            xy=(dip["center_longitude"], dip["center_latitude"]),
                            color="#b060ff", fontsize=7, fontfamily="monospace",
                            xytext=(4, 4), textcoords="offset points")
            if world.get("dipoles"):
                legend_handles.append(mpatches.Patch(color="#b060ff", label="Dipole"))

    ax.legend(handles=legend_handles, facecolor=BG2, edgecolor=GREY,
              labelcolor=TEXT, fontsize=7, loc="upper right")
    return fig


# ── JSON preview helpers ──────────────────────────────────────────────────────
def show_drone_json(path):
    return pretty_json(load_drone(path)) if path else "— select a drone —"

def show_world_json(path):
    return pretty_json(load_world(path)) if path else "— select a world —"

def show_traj_info(path):
    if not path:
        return "— select a trajectory —"
    df = read_trajectory_sample(path, n=5)
    if df is None:
        return "Could not read trajectory file."
    rows = len(open(path).readlines()) - 1
    return (
        f"File:    {path}\n"
        f"Rows:    {rows:,}\n"
        f"Columns: {list(df.columns)}\n\n"
        f"First 5 rows:\n{df.head(5).to_string(index=False)}"
    )


# ── TAB BUILDER ───────────────────────────────────────────────────────────────
def build_config_tab():
    with gr.Row():
        # ── Left panel: selectors ─────────────────────────────────────────────
        with gr.Column(scale=1, min_width=260):
            gr.HTML('<div class="panel-title">SELECT FILES</div>')

            drone_dd = gr.Dropdown(
                choices=list_drones(), label="Drone JSON",
                elem_classes=[], interactive=True,
            )
            gr.HTML('<div style="margin:4px 0"></div>')
            world_dd = gr.Dropdown(
                choices=list_worlds(), label="World JSON", interactive=True,
            )
            gr.HTML('<div style="margin:4px 0"></div>')
            traj_dd = gr.Dropdown(
                choices=list_trajectories(), label="Trajectory CSV", interactive=True,
            )
            refresh_btn = gr.Button("↺  Refresh file lists", elem_classes=["btn-primary"])

            gr.HTML('<div class="panel-title" style="margin-top:16px">DRONE CONFIG JSON</div>')
            drone_json_out = gr.Code(language="json", label="", lines=12,
                                     interactive=False)

            gr.HTML('<div class="panel-title" style="margin-top:8px">WORLD CONFIG JSON</div>')
            world_json_out = gr.Code(language="json", label="", lines=12,
                                     interactive=False)

            gr.HTML('<div class="panel-title" style="margin-top:8px">TRAJECTORY INFO</div>')
            traj_info_out = gr.Textbox(label="", lines=8, interactive=False,
                                       elem_classes=["console-out"])

        # ── Right panel: plots ────────────────────────────────────────────────
        with gr.Column(scale=3):
            gr.HTML('<div class="panel-title">DRONE SENSOR LAYOUT</div>')
            drone_plot = gr.Plot(label="")

            gr.HTML('<div class="panel-title" style="margin-top:12px">WORLD + TRAJECTORY MAP</div>')
            world_plot = gr.Plot(label="")

    # ── Event wiring ──────────────────────────────────────────────────────────
    def refresh_lists():
        return (
            gr.Dropdown(choices=list_drones()),
            gr.Dropdown(choices=list_worlds()),
            gr.Dropdown(choices=list_trajectories()),
        )

    refresh_btn.click(refresh_lists, outputs=[drone_dd, world_dd, traj_dd])

    drone_dd.change(
        lambda p: (plot_drone_sensors(p), show_drone_json(p)),
        inputs=[drone_dd], outputs=[drone_plot, drone_json_out],
    )
    world_dd.change(
        lambda w, t: (plot_world_trajectory(w, t), show_world_json(w)),
        inputs=[world_dd, traj_dd], outputs=[world_plot, world_json_out],
    )
    traj_dd.change(
        lambda w, t: (plot_world_trajectory(w, t), show_traj_info(t)),
        inputs=[world_dd, traj_dd], outputs=[world_plot, traj_info_out],
    )
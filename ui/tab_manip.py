"""
ui/tab_manip.py  –  New Experiment (Manip) Creator Tab
Builds and saves an experiment JSON from available drones, worlds, trajectories.
"""

from __future__ import annotations
import json
import gradio as gr
from pathlib import Path

from ui.helpers import (
    list_drones, list_worlds, list_trajectories, manips_dir,
    load_drone, load_world, pretty_json, get_sensor_names,
)


def _default_experiment_name() -> str:
    from datetime import datetime
    return "bb_" + datetime.now().strftime("%Y%m%d_%H%M%S")


def _build_experiment_dict(
    exp_name: str,
    world_path: str,
    drone_path: str,
    traj_type: str,
    traj_csv: str,
    skip_logging: bool,
) -> dict | str:
    """Validate inputs and return experiment dict or error string."""
    if not exp_name.strip():
        return "ERROR: experiment_name is empty"
    if not world_path:
        return "ERROR: no world selected"
    if not drone_path:
        return "ERROR: no drone selected"
    if traj_type == "pp" and not traj_csv:
        return "ERROR: trajectory type 'pp' requires a CSV file"

    d = {
        "experiment_name": exp_name.strip(),
        "world_name":      world_path,
        "drone_name":      drone_path,
        "trajectory_type": traj_type,
        "skip_logging":    skip_logging,
    }
    if traj_type == "pp":
        d["pp_trajectory_filename"] = traj_csv
    return d


def preview_experiment(exp_name, world_path, drone_path, traj_type, traj_csv, skip_logging):
    result = _build_experiment_dict(
        exp_name, world_path, drone_path, traj_type, traj_csv, skip_logging
    )
    if isinstance(result, str):   # error message
        return result
    return json.dumps(result, indent=2)


def save_experiment(exp_name, world_path, drone_path, traj_type, traj_csv, skip_logging):
    result = _build_experiment_dict(
        exp_name, world_path, drone_path, traj_type, traj_csv, skip_logging
    )
    if isinstance(result, str):
        return f"✗ {result}"

    manips_dir().mkdir(parents=True, exist_ok=True)
    out_path = manips_dir() / f"{result['experiment_name']}.json"
    if out_path.exists():
        return f"✗ File already exists: {out_path}\n  Rename the experiment or delete the existing file."

    with open(out_path, "w") as f:
        json.dump(result, f, indent=4)
    return f"✓ Saved to: {out_path}"


def show_sensor_summary(drone_path: str) -> str:
    if not drone_path:
        return "— select a drone to see its sensors —"
    d = load_drone(drone_path)
    if not d:
        return "Could not load drone file."
    lines = [f"Drone: {d.get('name','?')}"]
    for s in d.get("sensors", []):
        pos = s.get("relative_position", [0, 0, 0])
        lines.append(
            f"  • {s['name']:20s}  type={s.get('type','?'):12s}  "
            f"pos=[{pos[0]:+.3f}, {pos[1]:+.3f}, {pos[2]:+.3f}]"
        )
    return "\n".join(lines)


def show_world_summary(world_path: str) -> str:
    if not world_path:
        return "— select a world to see its targets —"
    w = load_world(world_path)
    if not w:
        return "Could not load world file."
    lines = [
        f"World:  {w.get('name','?')}",
        f"Ref:    ({w.get('reference_longitude',0):.6f}, {w.get('reference_latitude',0):.6f})",
        f"Radius: {w.get('simulation_radius','?')} m",
        f"B_reg:  {w.get('regional_magnetic_field',[])} nT",
    ]
    for c in w.get("cables", []):
        lines.append(
            f"  ⬥ CABLE  {c['name']:20s}  I={c.get('current','?')} A  "
            f"depth {c.get('starting_depth','?')}→{c.get('ending_depth','?')} m"
        )
    for d in w.get("dipoles", []):
        lines.append(
            f"  ★ DIPOLE {d['name']:20s}  m={d.get('dipole_moment',[])} A·m²"
        )
    return "\n".join(lines)


# ── TAB BUILDER ───────────────────────────────────────────────────────────────
def build_manip_tab():
    with gr.Row():
        # ── Left: form ───────────────────────────────────────────────────────
        with gr.Column(scale=1, min_width=320):
            gr.HTML('<div class="panel-title">EXPERIMENT PARAMETERS</div>')

            exp_name_in = gr.Textbox(
                label="experiment_name",
                value=_default_experiment_name(),
                placeholder="bb_S60_gradio_snake",
            )

            with gr.Row():
                drone_dd = gr.Dropdown(
                    choices=list_drones(), label="Drone JSON", interactive=True,
                )
                refresh_btn = gr.Button("↺", elem_classes=["btn-primary"], scale=0, min_width=40)

            world_dd = gr.Dropdown(
                choices=list_worlds(), label="World JSON", interactive=True,
            )

            traj_type_dd = gr.Dropdown(
                choices=["pp"],
                value="pp",
                label="trajectory_type",
                interactive=True,
            )

            traj_csv_dd = gr.Dropdown(
                choices=list_trajectories(), label="Trajectory CSV (pp)", interactive=True,
            )

            skip_log_cb = gr.Checkbox(label="skip_logging", value=False)

            with gr.Row():
                preview_btn = gr.Button("👁  Preview JSON", elem_classes=["btn-primary"])
                save_btn    = gr.Button("💾  Save experiment", elem_classes=["btn-success"])

            save_status = gr.Textbox(label="", lines=2, interactive=False,
                                     elem_classes=["console-out"])

        # ── Right: info panels ────────────────────────────────────────────────
        with gr.Column(scale=2):
            gr.HTML('<div class="panel-title">JSON PREVIEW</div>')
            json_preview = gr.Code(language="json", label="", lines=18,
                                   interactive=False)

            gr.HTML('<div class="panel-title" style="margin-top:12px">DRONE SENSORS</div>')
            drone_summary = gr.Textbox(label="", lines=6, interactive=False,
                                       elem_classes=["console-out"])

            gr.HTML('<div class="panel-title" style="margin-top:12px">WORLD TARGETS</div>')
            world_summary = gr.Textbox(label="", lines=8, interactive=False,
                                       elem_classes=["console-out"])

    # ── Event wiring ──────────────────────────────────────────────────────────
    def refresh():
        return (
            gr.Dropdown(choices=list_drones()),
            gr.Dropdown(choices=list_worlds()),
            gr.Dropdown(choices=list_trajectories()),
        )
    refresh_btn.click(refresh, outputs=[drone_dd, world_dd, traj_csv_dd])

    drone_dd.change(show_sensor_summary, inputs=[drone_dd], outputs=[drone_summary])
    world_dd.change(show_world_summary,  inputs=[world_dd], outputs=[world_summary])

    _inputs = [exp_name_in, world_dd, drone_dd, traj_type_dd, traj_csv_dd, skip_log_cb]
    preview_btn.click(preview_experiment, inputs=_inputs, outputs=[json_preview])
    save_btn.click(save_experiment, inputs=_inputs, outputs=[save_status])
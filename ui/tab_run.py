"""
ui/tab_run.py  –  Run Simulation Tab
Launches `python run_program.py <experiment.json>` in a subprocess
and streams stdout/stderr back into the Gradio console in real-time.
"""

from __future__ import annotations
import subprocess
import sys
import threading
import queue
import time
import gradio as gr
from pathlib import Path

from ui.helpers import list_manips, load_experiment, manips_dir, ROOT


# ── subprocess runner ─────────────────────────────────────────────────────────
_run_queue: queue.Queue = queue.Queue()
_proc_ref: list[subprocess.Popen] = []   # single-item "ref" so threads can share it


def _stream_proc(proc):
    for line in iter(proc.stdout.readline, ""):
        _run_queue.put(line)
    proc.wait()
    _run_queue.put(f"\n[Process exited with code {proc.returncode}]\n")


def run_simulation(manip_path: str):
    """Generator: yield console lines as the simulation runs."""
    if not manip_path:
        yield "✗ No experiment selected.\n"
        return

    # clear previous queue
    while not _run_queue.empty():
        _run_queue.get_nowait()

    cmd = [sys.executable, str(ROOT / "run_program.py"), manip_path]
    yield f"▶ Starting: {' '.join(cmd)}\n"

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            bufsize=1,
        )
    except Exception as e:
        yield f"✗ Failed to start process: {e}\n"
        return

    _proc_ref.clear()
    _proc_ref.append(proc)

    t = threading.Thread(target=_stream_proc, args=(proc,), daemon=True)
    t.start()

    buffer = ""
    while t.is_alive() or not _run_queue.empty():
        try:
            line = _run_queue.get(timeout=0.1)
            buffer += line
            yield buffer
        except queue.Empty:
            pass

    # drain any leftovers
    while not _run_queue.empty():
        buffer += _run_queue.get_nowait()
    yield buffer


def stop_simulation():
    if _proc_ref:
        _proc_ref[0].terminate()
        return "⏹ Simulation terminated."
    return "No running simulation."


def load_experiment_info(manip_path: str) -> str:
    if not manip_path:
        return "— select an experiment —"
    d = load_experiment(manip_path)
    if not d:
        return "Could not load experiment file."

    from ui.helpers import load_drone, load_world, get_sensor_names
    lines = [
        f"Experiment : {d.get('experiment_name','?')}",
        f"World      : {d.get('world_name','?')}",
        f"Drone      : {d.get('drone_name','?')}",
        f"Traj type  : {d.get('trajectory_type','?')}",
        f"Traj file  : {d.get('pp_trajectory_filename','—')}",
        f"Log        : {'disabled' if d.get('skip_logging') else 'ENABLED'}",
        "",
        "Sensors:",
    ]
    drone_path = d.get("drone_name", "")
    for name in get_sensor_names(drone_path):
        lines.append(f"  • {name}")
    return "\n".join(lines)


# ── TAB BUILDER ───────────────────────────────────────────────────────────────
def build_run_tab():
    with gr.Row():
        # ── Left: controls ────────────────────────────────────────────────────
        with gr.Column(scale=1, min_width=300):
            gr.HTML('<div class="panel-title">SELECT EXPERIMENT</div>')

            manip_dd = gr.Dropdown(
                choices=list_manips(), label="Experiment JSON", interactive=True,
            )
            refresh_btn = gr.Button("↺  Refresh", elem_classes=["btn-primary"])

            gr.HTML('<div class="panel-title" style="margin-top:12px">EXPERIMENT SUMMARY</div>')
            exp_info = gr.Textbox(label="", lines=12, interactive=False,
                                  elem_classes=["console-out"])

            with gr.Row():
                run_btn  = gr.Button("▶  RUN",  elem_classes=["btn-success"])
                stop_btn = gr.Button("⏹  STOP", elem_classes=["btn-danger"])

            stop_msg = gr.Textbox(label="", lines=1, interactive=False,
                                  elem_classes=["console-out"])

        # ── Right: console output ─────────────────────────────────────────────
        with gr.Column(scale=3):
            gr.HTML('<div class="panel-title">SIMULATION CONSOLE</div>')
            console = gr.Textbox(
                label="",
                lines=35,
                max_lines=200,
                interactive=False,
                elem_classes=["console-out"],
                autoscroll=True,
            )

    # ── Event wiring ──────────────────────────────────────────────────────────
    def refresh():
        return gr.Dropdown(choices=list_manips())

    refresh_btn.click(refresh, outputs=[manip_dd])
    manip_dd.change(load_experiment_info, inputs=[manip_dd], outputs=[exp_info])

    run_btn.click(run_simulation, inputs=[manip_dd], outputs=[console])
    stop_btn.click(stop_simulation, outputs=[stop_msg])
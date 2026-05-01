#!/usr/bin/env python3
"""
run_nb.py — Persistent-kernel notebook runner.

Executes a Jupyter notebook cell-by-cell using a long-lived kernel.
On cell error: saves the kernel connection file + notebook state, then exits.
The kernel keeps running so you can fix the offending cell and resume.

Usage
-----
Fresh run:
    python run_nb.py notebooks/02_qc_cell_typing.ipynb

Resume from cell N using the still-live kernel:
    python run_nb.py notebooks/02_qc_cell_typing.ipynb --start-cell N --km-file .kernel.json

Resume from cell N with a brand-new kernel (if old kernel died):
    python run_nb.py notebooks/02_qc_cell_typing.ipynb --start-cell N
"""

import argparse
import queue
import shutil
import sys
import time
from pathlib import Path

import jupyter_client
import nbformat

CELL_TIMEOUT = 36000   # seconds — 10 h ceiling per cell


# ---------------------------------------------------------------------------
# Kernel helpers
# ---------------------------------------------------------------------------

def start_kernel(kernel_name: str, cwd: str = None) -> tuple:
    """Start a new kernel; return (km, kc).

    *cwd* sets the kernel's working directory (defaults to the notebook's
    parent so that relative paths in cells resolve correctly).
    """
    km = jupyter_client.KernelManager(kernel_name=kernel_name)
    km.start_kernel(cwd=cwd)
    kc = km.blocking_client()
    kc.start_channels()
    kc.wait_for_ready(timeout=60)
    return km, kc


def connect_kernel(conn_file: str) -> tuple:
    """Reconnect to a running kernel via its connection file; return (None, kc)."""
    kc = jupyter_client.BlockingKernelClient()
    kc.load_connection_file(conn_file)
    kc.start_channels()
    kc.wait_for_ready(timeout=30)
    return None, kc


# ---------------------------------------------------------------------------
# Cell execution
# ---------------------------------------------------------------------------

def execute_cell(kc, source: str) -> tuple:
    """
    Send *source* to the kernel and collect all reply messages.
    Returns (outputs, error_dict_or_None).
    """
    outputs = []
    error = None

    msg_id = kc.execute(source)

    while True:
        try:
            msg = kc.get_iopub_msg(timeout=CELL_TIMEOUT)
        except queue.Empty:
            print("  [warning] iopub timed out waiting for cell to finish", flush=True)
            break

        # Only process replies that belong to this execution
        if msg.get("parent_header", {}).get("msg_id") != msg_id:
            continue

        msg_type = msg["msg_type"]
        content  = msg["content"]

        if msg_type == "status":
            if content["execution_state"] == "idle":
                break

        elif msg_type == "stream":
            outputs.append(
                nbformat.v4.new_output("stream",
                                       name=content["name"],
                                       text=content["text"])
            )

        elif msg_type == "display_data":
            outputs.append(
                nbformat.v4.new_output("display_data",
                                       data=content.get("data", {}),
                                       metadata=content.get("metadata", {}))
            )

        elif msg_type == "execute_result":
            outputs.append(
                nbformat.v4.new_output("execute_result",
                                       data=content.get("data", {}),
                                       metadata=content.get("metadata", {}),
                                       execution_count=content.get("execution_count"))
            )

        elif msg_type == "error":
            outputs.append(
                nbformat.v4.new_output("error",
                                       ename=content["ename"],
                                       evalue=content["evalue"],
                                       traceback=content["traceback"])
            )
            error = {
                "ename":     content["ename"],
                "evalue":    content["evalue"],
                "traceback": content["traceback"],
            }

    return outputs, error


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("notebook",               help="Path to .ipynb file")
    parser.add_argument("--start-cell", type=int, default=0,
                        help="Cell index (0-based) to start/resume from")
    parser.add_argument("--km-file",              default=None,
                        help="Kernel connection file to reuse a live kernel")
    args = parser.parse_args()

    nb_path      = Path(args.notebook).resolve()
    conn_save    = nb_path.parent / ".kernel.json"

    # ------------------------------------------------------------------
    # Read notebook & pick kernel name from metadata
    # ------------------------------------------------------------------
    nb = nbformat.read(nb_path, as_version=4)
    kernel_name = (nb.metadata.get("kernelspec", {}).get("name") or "python3")

    # ------------------------------------------------------------------
    # Start or reconnect to kernel
    # ------------------------------------------------------------------
    if args.km_file:
        print(f"Reconnecting to kernel at {args.km_file} …", flush=True)
        km, kc = connect_kernel(args.km_file)
        print("Reconnected.\n", flush=True)
    else:
        print(f"Starting kernel '{kernel_name}' …", flush=True)
        km, kc = start_kernel(kernel_name, cwd=str(nb_path.parent))
        # Persist connection file immediately so we can always resume
        src = km.connection_file
        shutil.copy(src, conn_save)
        print(f"Kernel started.  Connection file saved → {conn_save}\n", flush=True)

    # ------------------------------------------------------------------
    # Execute cells
    # ------------------------------------------------------------------
    code_cells = [(i, c) for i, c in enumerate(nb.cells) if c.cell_type == "code"]
    total      = len(code_cells)

    for order, (idx, cell) in enumerate(code_cells):
        if idx < args.start_cell:
            continue

        preview = cell.source.strip().splitlines()[0][:72] if cell.source.strip() else "(empty)"
        print(f"[{order+1}/{total}] Cell {idx}  {preview!r} … ", end="", flush=True)

        if not cell.source.strip():
            print("(skipped — empty)")
            continue

        t0 = time.time()
        outputs, error = execute_cell(kc, cell.source)
        elapsed = time.time() - t0

        cell.outputs = outputs

        # Flush outputs to disk after every cell
        nbformat.write(nb, nb_path)

        if error:
            print(f"ERROR  ({elapsed:.1f}s)")
            print("\n" + "="*68)
            print(f"  Cell {idx} raised {error['ename']}: {error['evalue']}")
            print("="*68)
            # Print cleaned traceback (strip ANSI)
            import re
            ansi = re.compile(r"\x1b\[[0-9;]*m")
            for line in error["traceback"]:
                print("  " + ansi.sub("", line))
            print("="*68)
            print(f"\nKernel is still alive.  Connection file: {conn_save}")
            print(f"\nTo resume after fixing cell {idx}, run:")
            print(f"  python run_nb.py {nb_path} --start-cell {idx} --km-file {conn_save}")
            sys.exit(1)
        else:
            print(f"OK  ({elapsed:.1f}s)")

    # ------------------------------------------------------------------
    # Done
    # ------------------------------------------------------------------
    print("\nAll cells completed successfully!")
    if km:
        km.shutdown_kernel()
        conn_save.unlink(missing_ok=True)


if __name__ == "__main__":
    main()

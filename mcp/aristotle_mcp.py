#!/usr/bin/env python3
"""Zero-dep MCP stdio server wrapping the Aristotle CLI.

Exposes tools for the Aristotle Lean workflow:
  submit(prompt)              -> uploads the Lean project, returns project id
  list()                      -> lists recent Aristotle jobs
  result(project_id)          -> downloads tarball, extracts locally
  cancel(project_id)          -> cancels an in-progress job
  diff_result(project_id,...) -> diffs an extracted result file against the tree

Configuration (all optional, resolved at server startup):
  ARISTOTLE_API_KEY      Aristotle API key. If unset, the server looks for an
                         `aristotle-key.sh` file in the working dir containing
                         `export ARISTOTLE_API_KEY=...` and loads it.
  ARISTOTLE_LEAN_DIR     Lean project root passed as --project-dir to submit.
                         Default: ./lean if present, else the current dir.
  ARISTOTLE_STAGING_DIR  Where result tarballs are saved and extracted.
                         Default: ./aristotle-staging

Speaks JSON-RPC 2.0 over newline-delimited stdio (MCP default transport).
"""

import json
import os
import re
import subprocess
import sys
import tarfile
from pathlib import Path


def resolve_paths() -> tuple[Path, Path, Path]:
    cwd = Path.cwd()
    lean_env = os.environ.get("ARISTOTLE_LEAN_DIR")
    if lean_env:
        lean_dir = Path(lean_env).resolve()
    elif (cwd / "lean").is_dir():
        lean_dir = (cwd / "lean").resolve()
    else:
        lean_dir = cwd

    staging_env = os.environ.get("ARISTOTLE_STAGING_DIR")
    staging_dir = Path(staging_env).resolve() if staging_env else (cwd / "aristotle-staging").resolve()

    key_file = cwd / "aristotle-key.sh"
    return lean_dir, staging_dir, key_file


LEAN_DIR, STAGING_DIR, KEY_FILE = resolve_paths()


def load_key() -> None:
    if os.environ.get("ARISTOTLE_API_KEY"):
        return
    if not KEY_FILE.exists():
        return
    match = re.search(r"ARISTOTLE_API_KEY\s*=\s*(\S+)", KEY_FILE.read_text())
    if match:
        os.environ["ARISTOTLE_API_KEY"] = match.group(1)


load_key()

TOOLS = [
    {
        "name": "submit",
        "description": (
            "Submit an Aristotle Lean job. Uploads the configured Lean project "
            "directory as --project-dir. Returns the project id printed by the "
            "Aristotle CLI."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Instructions for Aristotle (passed as the submit prompt).",
                }
            },
            "required": ["prompt"],
        },
    },
    {
        "name": "list",
        "description": "List recent Aristotle jobs with status, progress, and creation time.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "result",
        "description": (
            "Download and extract the result tarball for a completed Aristotle job. "
            "Extracts to <staging>/<project_id>/ and returns the extraction path."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "UUID returned by `submit` or shown in `list`.",
                }
            },
            "required": ["project_id"],
        },
    },
    {
        "name": "cancel",
        "description": "Cancel an in-progress or queued Aristotle job.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "UUID of the job to cancel.",
                }
            },
            "required": ["project_id"],
        },
    },
    {
        "name": "diff_result",
        "description": (
            "Diff a file from an extracted Aristotle result against the current "
            "working tree. `path` is relative to the Lean project root. Requires "
            "`result` to have been called first on the project_id. Auto-detects "
            "tarball layout (project_aristotle/<path> or project_aristotle/lean/<path>)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "UUID of the Aristotle job whose result has been extracted.",
                },
                "path": {
                    "type": "string",
                    "description": "File path relative to the Lean project root.",
                },
            },
            "required": ["project_id", "path"],
        },
    },
]


def run_cli(args: list, cwd=None, timeout: int = 300) -> str:
    try:
        r = subprocess.run(
            ["aristotle", *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=cwd,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return f"ERROR: aristotle {' '.join(args[:2])} timed out after {timeout}s"
    except FileNotFoundError:
        return "ERROR: `aristotle` CLI not found on PATH"
    return (r.stdout or "") + (r.stderr or "")


def handle_submit(prompt: str) -> str:
    if not LEAN_DIR.exists():
        return f"ERROR: Lean project dir not found: {LEAN_DIR}"
    return run_cli(["submit", prompt, "--project-dir", "."], cwd=LEAN_DIR, timeout=180)


def handle_list() -> str:
    return run_cli(["list"], timeout=60)


def handle_result(project_id: str) -> str:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    dest = STAGING_DIR / f"{project_id}.tar.gz"
    out = run_cli(["result", project_id, "--destination", str(dest)], timeout=300)
    extract_dir = STAGING_DIR / project_id
    extract_dir.mkdir(exist_ok=True)
    try:
        with tarfile.open(dest, "r:gz") as tf:
            tf.extractall(extract_dir)
        out += f"\nExtracted to: {extract_dir}"
    except Exception as e:
        out += f"\nExtract failed: {e}"
    return out


def handle_cancel(project_id: str) -> str:
    return run_cli(["cancel", project_id], timeout=30)


def handle_diff_result(project_id: str, path: str) -> str:
    extract_dir = STAGING_DIR / project_id
    if not extract_dir.exists():
        return f"ERROR: extracted directory not found: {extract_dir}\n(Call `result` first.)"
    candidates = [
        extract_dir / "project_aristotle" / path,
        extract_dir / "project_aristotle" / "lean" / path,
    ]
    tarball_file = next((c for c in candidates if c.exists()), None)
    if tarball_file is None:
        return f"ERROR: {path} not found in tarball for {project_id}. Tried: {[str(c) for c in candidates]}"
    working_file = LEAN_DIR / path
    if not working_file.exists():
        return f"ERROR: {path} not present in working tree at {working_file}"
    try:
        r = subprocess.run(
            ["diff", "-u", str(working_file), str(tarball_file)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
    except FileNotFoundError:
        return "ERROR: `diff` not found on PATH"
    out = r.stdout or ""
    if r.returncode == 0:
        out = "(files are identical)"
    return out


def respond(msg_id, result=None, error=None) -> None:
    resp = {"jsonrpc": "2.0", "id": msg_id}
    if error is not None:
        resp["error"] = error
    else:
        resp["result"] = result
    sys.stdout.write(json.dumps(resp) + "\n")
    sys.stdout.flush()


def process(msg: dict) -> None:
    method = msg.get("method")
    msg_id = msg.get("id")
    params = msg.get("params", {}) or {}

    if method == "initialize":
        respond(
            msg_id,
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "aristotle", "version": "0.1.0"},
            },
        )
        return

    if method in ("initialized", "notifications/initialized"):
        return

    if method == "tools/list":
        respond(msg_id, {"tools": TOOLS})
        return

    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {}) or {}
        try:
            if name == "submit":
                text = handle_submit(args["prompt"])
            elif name == "list":
                text = handle_list()
            elif name == "result":
                text = handle_result(args["project_id"])
            elif name == "cancel":
                text = handle_cancel(args["project_id"])
            elif name == "diff_result":
                text = handle_diff_result(args["project_id"], args["path"])
            else:
                respond(msg_id, error={"code": -32601, "message": f"Unknown tool: {name}"})
                return
            respond(msg_id, {"content": [{"type": "text", "text": text}]})
        except Exception as e:
            respond(msg_id, error={"code": -32603, "message": f"{type(e).__name__}: {e}"})
        return

    if msg_id is not None:
        respond(msg_id, error={"code": -32601, "message": f"Method not found: {method}"})


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        try:
            process(msg)
        except Exception as e:
            sys.stderr.write(f"process error: {e}\n")
            sys.stderr.flush()


if __name__ == "__main__":
    main()

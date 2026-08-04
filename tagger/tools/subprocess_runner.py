"""Helpers for running model tools in tool-specific Python subprocesses."""

import json
import os
from pathlib import Path
import subprocess


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class SubprocessToolError(RuntimeError):
    """Raised when a subprocess-backed tool cannot return a valid result."""


class JsonSubprocessWorker:
    def __init__(self, python_executable, tool_name):
        self.python_executable = _resolve_python_executable(python_executable)
        self.tool_name = tool_name
        env = os.environ.copy()
        pythonpath = str(PROJECT_ROOT)
        if env.get("PYTHONPATH"):
            pythonpath = pythonpath + os.pathsep + env["PYTHONPATH"]
        env["PYTHONPATH"] = pythonpath
        self.process = subprocess.Popen(
            [
                self.python_executable,
                "-m",
                "tagger.tools.subprocess_worker",
                self.tool_name,
            ],
            cwd=str(PROJECT_ROOT),
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=None,
            universal_newlines=True,
            bufsize=1,
        )

    def call(self, request):
        if self.process.poll() is not None:
            raise SubprocessToolError(
                "subprocess worker exited before request: %s" % self.tool_name
            )
        self.process.stdin.write(json.dumps(request, ensure_ascii=False) + "\n")
        self.process.stdin.flush()
        response = self._read_response()
        if response.get("status") != "ok":
            message = response.get("message") or "subprocess tool failed"
            error_type = response.get("error_type")
            if error_type:
                message = "%s: %s" % (error_type, message)
            raise SubprocessToolError(message)
        return response.get("result")

    def close(self):
        if self.process.poll() is not None:
            return
        try:
            self.process.stdin.write(json.dumps({"_command": "close"}) + "\n")
            self.process.stdin.flush()
            self.process.stdin.close()
        except Exception:
            pass
        try:
            self.process.wait(timeout=5)
        except Exception:
            self.process.terminate()

    def _read_response(self):
        noise = []
        while True:
            line = self.process.stdout.readline()
            if not line:
                code = self.process.poll()
                raise SubprocessToolError(
                    "subprocess worker produced no JSON response for %s; "
                    "returncode=%s; stdout_noise=%s"
                    % (self.tool_name, code, " | ".join(noise[-5:]))
                )
            stripped = line.strip()
            try:
                response = json.loads(stripped)
            except ValueError:
                noise.append(stripped)
                continue
            if isinstance(response, dict) and "status" in response:
                return response
            noise.append(stripped)


def run_subprocess_tool(python_executable, tool_name, request, context=None):
    if not python_executable:
        raise SubprocessToolError("subprocess python is not configured")
    if context is None:
        worker = JsonSubprocessWorker(python_executable, tool_name)
        try:
            return worker.call(request)
        finally:
            worker.close()

    workers = context.setdefault("_subprocess_workers", {})
    key = (_resolve_python_executable(python_executable), tool_name)
    if key not in workers:
        workers[key] = JsonSubprocessWorker(python_executable, tool_name)
    return workers[key].call(request)


def close_subprocess_workers(context):
    if not context:
        return
    workers = context.pop("_subprocess_workers", {})
    for worker in workers.values():
        worker.close()


def _resolve_python_executable(python_executable):
    path = Path(str(python_executable)).expanduser()
    if path.is_absolute():
        return str(path)
    candidate = PROJECT_ROOT / path
    if candidate.exists():
        return str(candidate)
    return str(path)

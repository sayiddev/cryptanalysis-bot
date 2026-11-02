"""Bot-side client that runs one cryptanalysis job in an isolated subprocess.

See app/worker/run_job.py for what actually executes. This module only
spawns the subprocess, feeds it JSON, and enforces a wall-clock timeout as a
second line of defense on top of the subprocess's own resource.setrlimit.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from dataclasses import dataclass


@dataclass
class JobOutcome:
    ok: bool
    result: dict | None = None
    error: str | None = None
    timed_out: bool = False


async def run_job(
    job_type: str,
    input_text: str,
    params: dict | None = None,
    timeout_seconds: int = 20,
    memory_limit_mb: int = 256,
) -> JobOutcome:
    job_payload = json.dumps({"job_type": job_type, "input": input_text, "params": params or {}})

    env = os.environ.copy()
    env["JOB_TIMEOUT_SECONDS"] = str(timeout_seconds)
    env["JOB_MEMORY_LIMIT_MB"] = str(memory_limit_mb)

    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "app.worker.run_job",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )

    try:
        stdout, _stderr = await asyncio.wait_for(
            process.communicate(job_payload.encode("utf-8")),
            timeout=timeout_seconds + 5,  # grace period beyond the subprocess's own CPU limit
        )
    except TimeoutError:
        process.kill()
        await process.wait()
        return JobOutcome(ok=False, error="job timed out", timed_out=True)

    try:
        payload = json.loads(stdout.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JobOutcome(ok=False, error="worker produced invalid output")

    if payload.get("ok"):
        return JobOutcome(ok=True, result=payload.get("result"))
    return JobOutcome(ok=False, error=payload.get("error", "unknown worker error"))

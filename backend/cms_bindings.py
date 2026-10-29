# backend/cms_bindings.py
import os
import sys
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# =========================================================
# TYME CMS — Sovereign UCE/UFW bindings
# =========================================================

REPO_ROOT = Path(".").resolve()
DRY_RUN = os.environ.get("TYME_DRY_RUN") == "1"

# ----------------------------
# Shell + Git helpers
# ----------------------------

def sh(cmd: str, cwd: str = ".") -> str:
    print(f"$ {cmd}")
    if DRY_RUN:
        return ""
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(result.stdout)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")
    return result.stdout


def ensure_git_identity() -> None:
    def get_cfg(key: str) -> str:
        return subprocess.run(
            f"git config {key}",
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ).stdout.strip()

    if not get_cfg("user.name"):
        sh('git config user.name "TYME CMS"')
    if not get_cfg("user.email"):
        sh('git config user.email "tyme-cms@users.noreply.github.com"')


def safe_commit(summary: str, touched_files: List[str]) -> None:
    ensure_git_identity()

    summary = re.sub(r'["\n\r\t]', " ", (summary or "Tyme CMS update"))[:120]

    if DRY_RUN:
        print("[DRY-RUN] Commit skipped")
        return

    for f in touched_files:
        sh(f'git add "{f}"')

    status = subprocess.run(
        "git status --porcelain",
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()

    if not status:
        print("No changes detected; skipping commit.")
        return

    sh(f'git commit -m "{summary}"')


# ----------------------------
# Path safety
# ----------------------------

def normalize_rel_path(p: str) -> str:
    if not p:
        raise ValueError("Empty path")

    p = str(p).strip().strip('"').strip("'")
    p = p.lstrip("/").lstrip("./")

    candidate = (REPO_ROOT / p).resolve()
    if not str(candidate).startswith(str(REPO_ROOT)):
        raise ValueError(f"Unsafe path (escapes repo): {p}")

    return p.replace("\\", "/")


def ensure_parent_dirs(rel_path: str) -> None:
    parent = (REPO_ROOT / rel_path).parent
    if not DRY_RUN:
        parent.mkdir(parents=True, exist_ok=True)


# ----------------------------
# Content normalization
# ----------------------------

def normalize_content(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value if value.endswith("\n") else value + "\n"
    try:
        return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    except Exception:
        return str(value) + "\n"


# ----------------------------
# Robust JSON extraction
# ----------------------------

def extract_first_json_object(text: str) -> Dict[str, Any]:
    if not text:
        raise ValueError("Empty model output")

    cleaned = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE)

    depth = 0
    start = None
    for i, ch in enumerate(cleaned):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth:
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    obj = json.loads(cleaned[start : i + 1])
                    if isinstance(obj, dict):
                        return obj
                except Exception:
                    pass

    raise ValueError("Could not extract valid JSON object")


# ----------------------------
# Directive Layer
# ----------------------------

def now_utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:80] or "proposal"


def directive_plan(raw: str) -> Optional[Dict[str, Any]]:
    r = raw.strip().lower()

    if r in {"refresh system index", "refresh index"}:
        return {
            "summary": "System index refresh",
            "steps": [{
                "op": "replace",
                "file": "chronicle/system-index.json",
                "mode": "overwrite",
                "content": scan_repo_index(),
            }],
        }

    if r.startswith("proposal:"):
        body = raw.split(":", 1)[1].strip()
        ts = now_utc_stamp()
        title, _, content = body.partition("::")
        return {
            "summary": f"Proposal: {title.strip()}",
            "steps": [
                {"op": "mkdir", "file": "proposals"},
                {
                    "op": "create",
                    "file": f"proposals/{ts}_{slugify(title)}.md",
                    "mode": "overwrite",
                    "content": f"# {title.strip()}\n\nCreated: {ts}\n\n{content.strip()}",
                },
            ],
        }

    return None


# ----------------------------
# Executor
# ----------------------------

ALLOWED_OPS = {"create", "replace", "patch", "delete", "mkdir"}
OP_ALIASES = {
    "overwrite": "replace",
    "append": "patch",
    "write": "replace",
    "update": "patch",
    "add": "create",
    "remove": "delete",
}

def canonical_op(op: str) -> str:
    return OP_ALIASES.get((op or "").lower(), (op or "").lower())


def validate_step(step: Dict[str, Any]) -> None:
    if "op" not in step or "file" not in step:
        raise ValueError(f"Invalid step: {step}")
    if canonical_op(step["op"]) not in ALLOWED_OPS:
        raise ValueError(f"Unknown operation: {step['op']}")


def apply_step(step: Dict[str, Any], touched: List[str]) -> None:
    validate_step(step)

    op = canonical_op(step["op"])
    path = normalize_rel_path(step["file"])
    content = normalize_content(step.get("content"))

    print(f"STEP: {op} {path}")

    if op == "mkdir":
        if not DRY_RUN:
            (REPO_ROOT / path).mkdir(parents=True, exist_ok=True)
        return

    full = REPO_ROOT / path

    if op == "delete":
        if full.exists() and full.is_file():
            if not DRY_RUN:
                full.unlink()
            touched.append(path)
        return

    ensure_parent_dirs(path)

    mode = "a" if op == "patch" else "w"
    if not DRY_RUN:
        with full.open(mode, encoding="utf-8") as f:
            f.write(content)
    touched.append(path)


def run_plan(plan: Dict[str, Any]) -> None:
    steps = plan.get("steps") or []
    summary = plan.get("summary", "Tyme CMS update")

    touched: List[str] = []
    for step in steps:
        apply_step(step, touched)

    safe_commit(summary, touched)


# ----------------------------
# Fail-closed compatibility interpreter
# ----------------------------
# This module retains legacy plan/writer helpers for separately authorized
# pathways, but its public execute() endpoint MUST NOT invoke them.
# Until a governed interpreter is implemented, execution stays disabled.
from dataclasses import dataclass, field


@dataclass(frozen=True)
class CMSExecutionResult:
    mode: str
    canonical: Optional[str] = None
    parsed: Optional[Any] = None
    result: Any = None
    error: Optional[str] = None
    notes: Dict[str, Any] = field(default_factory=dict)


_CMS_SHORTHAND = re.compile(r"[A-Za-z_]\\w*(?:\\.[A-Za-z_]\\w*)+\\s*\\(.*\\)", re.DOTALL)
_CMS_DIRECTIVES = {"refresh index", "refresh system index"}


def execute(raw: str) -> CMSExecutionResult:
    """Classify commands without granting filesystem, shell or Git authority.

    Recognizable commands return BLOCKED until an independently governed
    interpreter exists. Ordinary chat remains UNKNOWN for AVOT narrative
    fallback. No legacy writer, LLM, or subprocess is called here.
    """
    notes = {
        "authority_effect": "none",
        "mutation": "not_performed",
        "executor": "unavailable",
    }
    if not isinstance(raw, str):
        return CMSExecutionResult(
            mode="blocked",
            result={
                "status": "blocked",
                "reason": "INVALID_CMS_INPUT",
                "authority_effect": "none",
            },
            error="CMS input must be text; no action performed.",
            notes=notes,
        )

    command = raw.strip()
    if not command:
        return CMSExecutionResult(mode="unknown", notes=notes)

    is_shorthand = _CMS_SHORTHAND.fullmatch(command) is not None
    is_directive = (
        command.lower() in _CMS_DIRECTIVES
        or command.lower().startswith("proposal:")
    )
    if is_shorthand or is_directive:
        return CMSExecutionResult(
            mode="blocked",
            canonical=command,
            result={
                "status": "blocked",
                "reason": "CMS_EXECUTOR_UNAVAILABLE",
                "authority_effect": "none",
            },
            error="CMS execution is not configured; no action performed.",
            notes=notes,
        )

    return CMSExecutionResult(mode="unknown", notes=notes)


# ----------------------------
# Main
# ----------------------------

def clean_user_input(raw: str) -> str:
    raw = raw.strip()
    m = re.match(r"^[a-zA-Z_]\w*$begin:math:text$(.*)$end:math:text$$", raw)
    return m.group(1).strip() if m else raw


def main() -> None:
    raw = " ".join(sys.argv[1:]).strip()
    if not raw:
        print("No command provided.")
        return

    dplan = directive_plan(raw)
    if dplan:
        run_plan(dplan)
        return

    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    resp = client.chat.completions.create(
        model=os.environ.get("TYME_MODEL", "gpt-4o-mini"),
        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                  {"role": "user", "content": clean_user_input(raw)}],
        temperature=0.2,
    )

    plan = extract_first_json_object(resp.choices[0].message.content or "")
    run_plan(plan)


if __name__ == "__main__":
    main()
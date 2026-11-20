#!/usr/bin/env python3
"""TYME Codex Bridge Controller 001.

Offline-first controller core for validating bounded session connection packets,
constructing a secret-free codex exec-server launch specification, and modeling
bounded reconnect behavior.

This module performs no network calls and never reads secret material.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CONTROLLER_ID = "tyme-codex-bridge-controller-001"
PACKET_VERSION = "tyme-codex-session-connection/0.1"
MAX_RECONNECT_ATTEMPTS = 3
BACKOFF_SECONDS = (2, 5, 15)


class PacketError(ValueError):
    """Raised when a session connection packet is invalid."""


@dataclass(frozen=True)
class SessionPacket:
    packet_version: str
    session_id: str
    environment_id: str
    remote_url: str
    workspace: str
    authority_id: str
    issued_at: str
    expires_at: str

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "SessionPacket":
        required = (
            "packet_version",
            "session_id",
            "environment_id",
            "remote_url",
            "workspace",
            "authority_id",
            "issued_at",
            "expires_at",
        )
        missing = [key for key in required if not data.get(key)]
        if missing:
            raise PacketError(f"missing required fields: {', '.join(missing)}")

        packet = cls(**{key: str(data[key]) for key in required})
        packet.validate()
        return packet

    def validate(self, now: datetime | None = None) -> None:
        if self.packet_version != PACKET_VERSION:
            raise PacketError(f"unsupported packet_version: {self.packet_version}")

        if self.workspace != "/workspace":
            raise PacketError("workspace must be exactly /workspace for proof 001")

        if not self.remote_url.startswith("https://api.openai.com/"):
            raise PacketError("remote_url must target api.openai.com")

        current = now or datetime.now(timezone.utc)
        issued = _parse_timestamp(self.issued_at)
        expires = _parse_timestamp(self.expires_at)

        if expires <= issued:
            raise PacketError("expires_at must be later than issued_at")
        if expires <= current:
            raise PacketError("packet is expired")


@dataclass(frozen=True)
class LaunchSpec:
    argv: tuple[str, ...]
    required_env: tuple[str, ...]
    workspace: str

    def shell_preview(self) -> str:
        args = " ".join(_quote(arg) for arg in self.argv)
        return f'CODEX_API_KEY="$OPENAI_ENVIRONMENT_KEY" {args}'


@dataclass
class BridgeState:
    controller_id: str
    session_id: str
    environment_id: str
    authority_id: str
    connection_state: str = "BRIDGE_CONNECTION_REQUIRED"
    reconnect_count: int = 0
    last_error: str | None = None

    def receipt(self, event: str) -> dict[str, Any]:
        return {
            "controller_id": self.controller_id,
            "session_id": self.session_id,
            "environment_id": self.environment_id,
            "authority_id": self.authority_id,
            "event": event,
            "connection_state": self.connection_state,
            "reconnect_count": self.reconnect_count,
            "error_class": self.last_error,
        }


def build_launch_spec(packet: SessionPacket) -> LaunchSpec:
    """Build a launch specification without embedding secret material."""
    argv = (
        "codex",
        "exec-server",
        "--remote",
        packet.remote_url,
        "--environment-id",
        packet.environment_id,
    )
    return LaunchSpec(
        argv=argv,
        required_env=("OPENAI_ENVIRONMENT_KEY",),
        workspace=packet.workspace,
    )


def simulate_reconnect_failures(packet: SessionPacket, failures: int) -> list[dict[str, Any]]:
    """Model bounded reconnect behavior without spawning a process."""
    state = BridgeState(
        controller_id=CONTROLLER_ID,
        session_id=packet.session_id,
        environment_id=packet.environment_id,
        authority_id=packet.authority_id,
    )
    receipts = [state.receipt("BRIDGE_CONNECTION_REQUIRED")]

    attempts = min(max(failures, 0), MAX_RECONNECT_ATTEMPTS)
    for index in range(attempts):
        state.reconnect_count += 1
        state.connection_state = "RECONNECTING"
        state.last_error = "synthetic_disconnect"
        receipt = state.receipt("RECONNECT_ATTEMPT")
        receipt["backoff_seconds"] = BACKOFF_SECONDS[index]
        receipts.append(receipt)

    if failures > MAX_RECONNECT_ATTEMPTS:
        state.connection_state = "ESCALATED"
        state.last_error = "reconnect_exhausted"
        receipts.append(state.receipt("RECONNECT_EXHAUSTED"))
    elif failures > 0:
        state.connection_state = "ENVIRONMENT_CONNECTED"
        state.last_error = None
        receipts.append(state.receipt("ENVIRONMENT_CONNECTED"))

    return receipts


def dry_run(packet_path: Path, failures: int) -> dict[str, Any]:
    data = json.loads(packet_path.read_text(encoding="utf-8"))
    packet = SessionPacket.from_mapping(data)
    spec = build_launch_spec(packet)
    receipts = simulate_reconnect_failures(packet, failures)

    return {
        "controller_id": CONTROLLER_ID,
        "mode": "synthetic_dry_run",
        "network_calls": 0,
        "host_mutations": 0,
        "packet": asdict(packet),
        "launch_spec": {
            "argv": list(spec.argv),
            "required_env": list(spec.required_env),
            "workspace": spec.workspace,
            "shell_preview": spec.shell_preview(),
        },
        "receipts": receipts,
    }


def _parse_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise PacketError(f"invalid timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise PacketError("timestamps must include timezone information")
    return parsed.astimezone(timezone.utc)


def _quote(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"


def main() -> int:
    parser = argparse.ArgumentParser(description="TYME Codex Bridge Controller 001")
    parser.add_argument("--dry-run", type=Path, required=True, help="Synthetic packet JSON")
    parser.add_argument(
        "--synthetic-failures",
        type=int,
        default=0,
        help="Number of synthetic disconnect failures to model",
    )
    args = parser.parse_args()

    try:
        result = dry_run(args.dry_run, args.synthetic_failures)
    except (PacketError, json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"status": "REFUSED", "error": str(exc)}, indent=2))
        return 2

    print(json.dumps({"status": "PASS", **result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

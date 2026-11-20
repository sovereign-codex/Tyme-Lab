#!/usr/bin/env python3
from datetime import datetime, timedelta, timezone
import unittest

from controller import (
    BACKOFF_SECONDS,
    MAX_RECONNECT_ATTEMPTS,
    PACKET_VERSION,
    PacketError,
    SessionPacket,
    build_launch_spec,
    simulate_reconnect_failures,
)


def packet(**overrides):
    now = datetime.now(timezone.utc)
    data = {
        "packet_version": PACKET_VERSION,
        "session_id": "sess_synthetic_001",
        "environment_id": "ccarenv_synthetic_001",
        "remote_url": "https://api.openai.com/v1/agents/api/connect/rt_synthetic",
        "workspace": "/workspace",
        "authority_id": "TYME-AUTH-CODEX-CONTROLLER-IMPL-001",
        "issued_at": now.isoformat(),
        "expires_at": (now + timedelta(minutes=10)).isoformat(),
    }
    data.update(overrides)
    return data


class ControllerTests(unittest.TestCase):
    def test_valid_packet(self):
        parsed = SessionPacket.from_mapping(packet())
        self.assertEqual(parsed.workspace, "/workspace")

    def test_missing_field_rejected(self):
        data = packet()
        data.pop("environment_id")
        with self.assertRaises(PacketError):
            SessionPacket.from_mapping(data)

    def test_expired_packet_rejected(self):
        now = datetime.now(timezone.utc)
        with self.assertRaises(PacketError):
            SessionPacket.from_mapping(
                packet(
                    issued_at=(now - timedelta(minutes=20)).isoformat(),
                    expires_at=(now - timedelta(minutes=10)).isoformat(),
                )
            )

    def test_wrong_workspace_rejected(self):
        with self.assertRaises(PacketError):
            SessionPacket.from_mapping(packet(workspace="/etc"))

    def test_launch_spec_has_no_secret(self):
        parsed = SessionPacket.from_mapping(packet())
        spec = build_launch_spec(parsed)
        preview = spec.shell_preview()
        self.assertIn('OPENAI_ENVIRONMENT_KEY', preview)
        self.assertNotIn("sk-", preview)
        self.assertEqual(spec.required_env, ("OPENAI_ENVIRONMENT_KEY",))

    def test_reconnect_is_bounded(self):
        parsed = SessionPacket.from_mapping(packet())
        receipts = simulate_reconnect_failures(parsed, MAX_RECONNECT_ATTEMPTS + 2)
        attempts = [r for r in receipts if r["event"] == "RECONNECT_ATTEMPT"]
        self.assertEqual(len(attempts), MAX_RECONNECT_ATTEMPTS)
        self.assertEqual(
            [r["backoff_seconds"] for r in attempts],
            list(BACKOFF_SECONDS),
        )
        self.assertEqual(receipts[-1]["event"], "RECONNECT_EXHAUSTED")
        self.assertEqual(receipts[-1]["connection_state"], "ESCALATED")


if __name__ == "__main__":
    unittest.main()

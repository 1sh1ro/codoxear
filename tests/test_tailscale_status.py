import json
import subprocess
import unittest
from unittest.mock import patch

from codoxear.server import _parse_tailscale_time
from codoxear.server import _tailscale_status_snapshot


class TestTailscaleStatus(unittest.TestCase):
    def test_parse_go_nanosecond_timestamp(self) -> None:
        ts = _parse_tailscale_time("2026-06-16T14:56:31.994590829+08:00")
        self.assertIsNotNone(ts)
        self.assertGreater(ts or 0, 0)
        self.assertIsNone(_parse_tailscale_time("0001-01-01T00:00:00Z"))

    def test_snapshot_summarizes_and_redacts_tailscale_json(self) -> None:
        payload = {
            "BackendState": "Running",
            "TailscaleIPs": ["100.64.0.1"],
            "CurrentTailnet": {"Name": "tailnet@example.com"},
            "Self": {
                "PublicKey": "nodekey:self",
                "HostName": "self-host",
                "DNSName": "self-host.example.ts.net.",
                "OS": "linux",
                "UserID": 123,
                "TailscaleIPs": ["100.64.0.1"],
                "Online": True,
                "Relay": "sfo",
                "RxBytes": 10,
                "TxBytes": 20,
            },
            "Peer": {
                "nodekey:peer": {
                    "PublicKey": "nodekey:peer",
                    "HostName": "peer-host",
                    "DNSName": "peer-host.example.ts.net.",
                    "OS": "linux",
                    "UserID": 456,
                    "TailscaleIPs": ["100.64.0.2"],
                    "Online": False,
                    "LastHandshake": "2026-06-16T14:56:31.994590829+08:00",
                }
            },
        }
        completed = subprocess.CompletedProcess(["tailscale"], 0, stdout=json.dumps(payload), stderr="")
        with patch("codoxear.server.shutil.which", return_value="/usr/bin/tailscale"), patch("codoxear.server.subprocess.run", return_value=completed):
            snapshot = _tailscale_status_snapshot()

        self.assertTrue(snapshot["ok"])
        self.assertEqual(snapshot["online_count"], 1)
        self.assertEqual(snapshot["machine_count"], 2)
        self.assertEqual(snapshot["machines"][0]["hostname"], "self-host")
        self.assertTrue(snapshot["machines"][0]["is_self"])
        self.assertEqual(snapshot["machines"][1]["hostname"], "peer-host")
        encoded = json.dumps(snapshot)
        self.assertNotIn("nodekey:", encoded)
        self.assertNotIn("UserID", encoded)
        self.assertNotIn("PublicKey", encoded)

    def test_missing_tailscale_command_returns_unavailable_payload(self) -> None:
        with patch("codoxear.server.shutil.which", return_value=None):
            snapshot = _tailscale_status_snapshot()
        self.assertFalse(snapshot["ok"])
        self.assertFalse(snapshot["available"])
        self.assertEqual(snapshot["machines"], [])


if __name__ == "__main__":
    unittest.main()

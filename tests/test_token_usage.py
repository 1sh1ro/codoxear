import datetime
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from codoxear.server import _today_token_usage_snapshot


class TestTokenUsage(unittest.TestCase):
    def test_today_snapshot_sums_last_token_usage_for_local_day(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            codoxear = root / "codoxear" / "sessions"
            codex = root / ".codex" / "sessions"
            pi = root / "pi" / "sessions"
            codoxear.mkdir(parents=True)
            codex.mkdir(parents=True)
            pi.mkdir(parents=True)
            (codoxear / "rollout-a.jsonl").write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-06-16T01:00:00+08:00",
                                "type": "event_msg",
                                "payload": {
                                    "type": "token_count",
                                    "info": {
                                        "last_token_usage": {
                                            "input_tokens": 100,
                                            "cached_input_tokens": 40,
                                            "output_tokens": 20,
                                            "reasoning_output_tokens": 5,
                                            "total_tokens": 120,
                                        }
                                    },
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-06-15T23:59:59+08:00",
                                "type": "event_msg",
                                "payload": {"type": "token_count", "info": {"last_token_usage": {"total_tokens": 999}}},
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (codex / "rollout-b.jsonl").write_text(
                json.dumps(
                    {
                        "timestamp": "2026-06-16T03:00:00+08:00",
                        "type": "event_msg",
                        "payload": {
                            "type": "token_count",
                            "info": {
                                "last_token_usage": {
                                    "input_tokens": 200,
                                    "cached_input_tokens": 80,
                                    "output_tokens": 30,
                                    "reasoning_output_tokens": 7,
                                    "total_tokens": 230,
                                }
                            },
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            (pi / "pi-a.jsonl").write_text(
                json.dumps(
                    {
                        "timestamp": "2026-06-16T04:00:00+08:00",
                        "type": "message",
                        "message": {"role": "assistant", "usage": {"totalTokens": 300}},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            now = datetime.datetime.fromisoformat("2026-06-16T12:00:00+08:00")
            with patch("codoxear.server.CODEX_SESSIONS_DIR", codoxear), patch("pathlib.Path.home", return_value=root), patch(
                "codoxear.server.PI_SESSIONS_DIR", pi
            ):
                snapshot = _today_token_usage_snapshot(now)

        self.assertTrue(snapshot["ok"])
        self.assertEqual(snapshot["date"], "2026-06-16")
        self.assertEqual(snapshot["token_events"], 3)
        self.assertEqual(snapshot["files"], 3)
        self.assertEqual(snapshot["input_tokens"], 300)
        self.assertEqual(snapshot["cached_input_tokens"], 120)
        self.assertEqual(snapshot["output_tokens"], 50)
        self.assertEqual(snapshot["reasoning_output_tokens"], 12)
        self.assertEqual(snapshot["total_tokens"], 650)
        self.assertEqual(snapshot["session_count"], 3)


if __name__ == "__main__":
    unittest.main()

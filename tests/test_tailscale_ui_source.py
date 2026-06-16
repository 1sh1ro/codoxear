import unittest
from pathlib import Path


APP_JS = Path(__file__).resolve().parents[1] / "codoxear" / "static" / "app.js"
APP_CSS = Path(__file__).resolve().parents[1] / "codoxear" / "static" / "app.css"


class TestTailscaleUiSource(unittest.TestCase):
    def test_split_shell_source_paths_exist(self) -> None:
        source = APP_JS.read_text(encoding="utf-8")
        self.assertIn("const splitShellMode =", source)
        self.assertIn("function renderSplitShell()", source)
        self.assertIn("function splitSessionIdsFromHash()", source)
        self.assertIn('id: "splitChoice"', source)
        self.assertIn("async function showSplitChoice()", source)
        self.assertIn("function startSessionSplitDrag", source)
        self.assertIn("function moveSessionSplitDrag", source)
        self.assertIn("leftSession, rightSession: s.session_id", source)
        self.assertIn("window.location.href = urlForMode({ split: true, leftSession, rightSession });", source)
        self.assertIn("window.top.location.href = urlForMode({ split: false });", source)
        self.assertIn("function paneStorageKey(base)", source)
        self.assertIn("paneStorageKey(\"codexweb.selected\")", source)

    def test_topbar_has_tailscale_status_widget(self) -> None:
        source = APP_JS.read_text(encoding="utf-8")
        self.assertIn('id: "tailscaleBtn"', source)
        self.assertIn('id: "tailscalePanel"', source)
        self.assertIn('async function loadTailscaleStatus', source)
        self.assertIn('await api("/api/tailscale/status")', source)
        self.assertIn("renderTailscaleStatus(data);", source)
        self.assertIn("setInterval(() => {\n              void loadTailscaleStatus();\n            }, 15000);", source)

    def test_topbar_has_today_token_usage_widget(self) -> None:
        source = APP_JS.read_text(encoding="utf-8")
        self.assertIn('id: "tokenUsageBtn"', source)
        self.assertIn('id: "tokenUsagePanel"', source)
        self.assertIn('async function loadTokenUsageToday', source)
        self.assertIn('await api("/api/token_usage/today")', source)
        self.assertIn("renderTokenUsageToday(data);", source)
        self.assertIn("setInterval(() => {\n              void loadTokenUsageToday();\n            }, 60000);", source)

    def test_tailscale_widget_styles_exist(self) -> None:
        source = APP_CSS.read_text(encoding="utf-8")
        self.assertIn(".tailscaleBtn", source)
        self.assertIn(".tailscalePanel", source)
        self.assertIn(".tailscaleMachine.online .tailscaleDot", source)
        self.assertIn(".tailscaleMachine.offline", source)

    def test_token_usage_widget_styles_exist(self) -> None:
        source = APP_CSS.read_text(encoding="utf-8")
        self.assertIn(".tokenUsageBtn", source)
        self.assertIn(".tokenUsagePanel", source)
        self.assertIn(".tokenUsageMetric", source)
        self.assertIn(".tokenUsageSession", source)

    def test_split_shell_styles_exist(self) -> None:
        source = APP_CSS.read_text(encoding="utf-8")
        self.assertIn(".splitShell", source)
        self.assertIn(".splitPanes", source)
        self.assertIn(".splitPaneFrame", source)
        self.assertIn(".splitChoice", source)
        self.assertIn(".splitChoiceRow", source)
        self.assertIn(".sessionSplitPreview", source)
        self.assertIn("body.session-split-armed .sidebar", source)


if __name__ == "__main__":
    unittest.main()

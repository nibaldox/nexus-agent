from pathlib import Path
from typing import List
import json
import time
from agno.tools import Toolkit


class FileTools(Toolkit):
    """Workspace-scoped file tools with UTF-8 support."""

    _ALLOWED_WRITE_PREFIXES = (
        "workspace/conversations/",
        "workspace/mission_plans/",
        "workspace/assets/",
        "workspace/knowledge/",
        "workspace/logs/",
        "artifacts/",
    )

    def __init__(self, base_dir: str | None = None):
        super().__init__(name="file_tools")
        root = Path(base_dir) if base_dir else Path(__file__).resolve().parents[1]
        self.base_dir = root.resolve()
        self._log_path = self.base_dir / "workspace" / "logs" / "file_ops.jsonl"
        self.register(self.read_file)
        self.register(self.write_file)
        self.register(self.append_to_file)
        self.register(self.list_dir)

    def _resolve_path(self, filepath: str) -> Path:
        if not filepath:
            raise ValueError("Invalid filepath")
        rel = filepath.lstrip("/").lstrip("\\")
        if rel.startswith("workspace/charts/"):
            rel = rel.replace("workspace/charts/", "workspace/assets/charts/", 1)
        full_path = (self.base_dir / rel).resolve()
        try:
            full_path.relative_to(self.base_dir)
        except ValueError:
            raise ValueError("Access denied: file outside workspace")
        return full_path

    def _validate_write_path(self, full_path: Path) -> None:
        rel = full_path.relative_to(self.base_dir).as_posix()
        if not any(rel.startswith(prefix) for prefix in self._ALLOWED_WRITE_PREFIXES):
            raise ValueError("Write denied: path must be under workspace/")

    def _log_file_op(self, action: str, filepath: str) -> None:
        try:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)
            record = {
                "timestamp": time.time(),
                "action": action,
                "path": filepath
            }
            with self._log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def read_file(self, filepath: str) -> str:
        full_path = self._resolve_path(filepath)
        if full_path.is_dir():
            entries = sorted(p.name for p in full_path.iterdir())
            return "\n".join(entries)
        return full_path.read_text(encoding="utf-8")

    def write_file(self, filepath: str, content: str) -> str:
        full_path = self._resolve_path(filepath)
        self._validate_write_path(full_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        self._log_file_op("write", filepath)
        return f"File written: {filepath}"

    def append_to_file(self, filepath: str, content: str) -> str:
        full_path = self._resolve_path(filepath)
        self._validate_write_path(full_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with full_path.open("a", encoding="utf-8") as f:
            f.write(content)
        self._log_file_op("append", filepath)
        return f"File appended: {filepath}"

    def list_dir(self, dirpath: str) -> List[str]:
        full_path = self._resolve_path(dirpath)
        if not full_path.is_dir():
            raise ValueError("Not a directory")
        return sorted(p.name for p in full_path.iterdir())

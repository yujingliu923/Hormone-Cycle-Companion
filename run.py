from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"


def _venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python3"


def _run(cmd: list[str], env: dict | None = None) -> None:
    subprocess.run(cmd, check=True, env=env)


def ensure_virtualenv() -> Path:
    if not VENV_DIR.exists():
        print("正在创建虚拟环境...")
        _run([sys.executable, "-m", "venv", str(VENV_DIR)])
    python_path = _venv_python()
    if not python_path.exists():
        raise RuntimeError("虚拟环境创建失败，请检查 Python 版本。")
    return python_path


def install_requirements(python_bin: Path) -> None:
    print("正在安装依赖包...")
    _run([str(python_bin), "-m", "pip", "install", "-r", "requirements.txt"])


def run_app(python_bin: Path) -> None:
    env = os.environ.copy()
    env.setdefault("FLASK_APP", "app.py")
    print("启动 Flask 应用...")
    _run([str(python_bin), "app.py"], env=env)


def main() -> None:
    python_bin = ensure_virtualenv()
    install_requirements(python_bin)
    run_app(python_bin)


if __name__ == "__main__":
    main()

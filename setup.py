#!/usr/bin/env python
"""Project setup script - installs dependencies and configures environment."""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Executes a command and returns True if successful."""
    print(f"🔧 {description}...")
    try:
        subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} - OK\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {description} failed\n")
        return False


def main():
    """Configures the project environment."""
    print("=" * 60)
    print("🚀 Temporal QnA Agent Project Setup")
    print("=" * 60)
    print()

    project_root = Path(__file__).parent

    # 1. Check Python version
    print(f"🐍 Python version: {sys.version}")
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ is required!")
        sys.exit(1)

    # 2. Create virtual environment if it doesn't exist
    venv_path = project_root / ".venv"
    if not venv_path.exists():
        if not run_command(
            [sys.executable, "-m", "venv", ".venv"],
            "Creating virtual environment"
        ):
            sys.exit(1)
    else:
        print("✅ Virtual environment already exists\n")

    # 3. Detect pip path in venv
    if os.name == "nt":  # Windows
        pip_path = venv_path / "Scripts" / "pip.exe"
        python_path = venv_path / "Scripts" / "python.exe"
    else:  # Unix/Linux/Mac
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"

    # 4. Update pip
    run_command(
        [str(python_path), "-m", "pip", "install", "--upgrade", "pip"],
        "Updating pip"
    )

    # 5. Install dependencies
    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists():
        if not run_command(
            [str(pip_path), "install", "-r", str(requirements_file)],
            "Installing dependencies"
        ):
            sys.exit(1)
    else:
        print("⚠️  requirements.txt not found\n")

    # 6. Check .env
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️  .env file not found!")
            print(f"📄 Copy .env.example to .env and configure your credentials:")
            print(f"   cp .env.example .env")
            print()
        else:
            print("⚠️  .env and .env.example not found!\n")
    else:
        print("✅ .env file found\n")

    # 7. Check search index
    search_index = project_root / "database" / "search_index.json"
    if not search_index.exists():
        print("⚠️  search_index.json not found!")
        print("💡 Run: python database/utils.py to generate embeddings\n")

    print("=" * 60)
    print("✅ Setup completed!")
    print("=" * 60)
    print()
    print("📝 Next steps:")
    print("   1. Configure .env file with your Azure credentials")
    print("   2. Generate embeddings: python database/utils.py")
    print("   3. Start Temporal Server (docker-compose up temporal)")
    print("   4. Run the worker: python worker.py")
    print("   5. Run the API: python api/main.py")
    print("   6. Run the frontend: streamlit run frontend/app.py")
    print()


if __name__ == "__main__":
    main()

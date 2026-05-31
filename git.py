#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 GitHub Publish CLI | v4.3 (Bug-Fixed Final)
Interactive tool to publish folders/files to GitHub with smart security.

╔══════════════════════════════════════════════════════════════╗
║  👨‍💻 Developed By: Ali Jahani                                 ║
║  🌐 Website: https://jahaniwww.com                           ║
║  🐦 Twitter: https://twitter.com/selfmrj                     ║
║  💼 LinkedIn: https://www.linkedin.com/in/ajahani/           ║
║  📺 YouTube: https://youtube.com/tarfandoonchannel           ║
║  ✈️ Telegram: https://t.me/tarfandoonchannel                  ║
║  🆔 Bale: http://ble.ir/tarfandoonchannel                    ║
╚══════════════════════════════════════════════════════════════╝

Usage:
    python github_publish.py          # Run interactive mode
    python github_publish.py --info   # Show developer info & links
    python github_publish.py --help   # Show help message

License: MIT | Use freely, give credit where due ❤️
"""
import os, sys, subprocess, requests, questionary as q
from pathlib import Path

# ── DEVELOPER INFO ───────────────────────────────────────────
DEV_INFO = {
    "name": "Ali Jahani",
    "website": "https://jahaniwww.com",
    "social": {
        "Twitter": "https://twitter.com/selfmrj",
        "LinkedIn": "https://www.linkedin.com/in/ajahani/",
        "YouTube": "https://youtube.com/tarfandoonchannel",
        "Telegram": "https://t.me/tarfandoonchannel",
        "Bale": "http://ble.ir/tarfandoonchannel"
    }
}

# Force UTF-8 for Windows
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ── CONFIG ───────────────────────────────────────────────────
SENSITIVE_PATTERNS = {
    ".env", ".env.local", ".env.production", "*.env",
    "*.key", "*.pem", "*.crt", "*.p12", "*.pfx",
    "config.json", "secrets.yaml", "credentials.json",
    ".aws/", ".azure/", ".gcp/", "firebase-config.json",
    "*.log", "*.sql", "dump.rdb", "*.sqlite",
    "__pycache__/", "*.pyc", ".DS_Store", "Thumbs.db",
    "node_modules/", ".venv/", "venv/", ".idea/", ".vscode/"
}
SECRET_EXTENSIONS = {".key", ".pem", ".crt", ".p12", ".pfx", ".env"}


# Symbols with fallback
def _sym(emoji, fallback):
    return emoji if sys.stdout.encoding == 'utf-8' else fallback


SYM = {
    "lock": _sym("🔐", "[SEC]"), "folder": _sym("📁", "[DIR]"),
    "file": _sym("📄", "[FILE]"), "up": _sym("🔙", "[UP]"),
    "select": _sym("✅", "[OK]"), "input": _sym("⌨️", "[TXT]"),
    "browse": _sym("🗂️", "[BRW]"), "check": _sym("✅", "[+]"),
    "cross": _sym("❌", "[X]"), "warn": _sym("⚠️", "[!]"),
    "rocket": _sym("🚀", "[>]"), "star": _sym("🌟", "[*]"),
    "party": _sym("🎉", "[!]"), "heart": _sym("❤️", "<3"),
    "code": _sym("👨‍💻", "[DEV]"), "link": _sym("🔗", "[URL]"),
}


# ── UTILS ────────────────────────────────────────────────────
def show_info():
    """Display developer information."""
    print(f"\n{SYM['star']} GitHub Publish CLI | v4.3")
    print(f"\n{SYM['code']} Developed By: {DEV_INFO['name']}")
    print(f"\n{SYM['link']} Official Links:")
    print(f"   🌐 Website  : {DEV_INFO['website']}")
    for platform, url in DEV_INFO['social'].items():
        print(f"   {platform:12}: {url}")
    print(f"\n{SYM['heart']} Thank you for using this tool! Share the love {SYM['heart']}\n")
    sys.exit(0)


def show_help():
    """Display help message."""
    print(f"""
{SYM['star']} GitHub Publish CLI | v4.3
Interactive tool to publish local folders/files to GitHub.

{SYM['folder']} USAGE:
   python github_publish.py          Run interactive mode
   python github_publish.py --info   Show developer info & links
   python github_publish.py --help   Show this help message

{SYM['folder']} FEATURES:
   • Interactive file/folder browser (cross-platform)
   • Auto-detect & protect sensitive files (.env, *.key, etc.)
   • Create GitHub repo (Public/Private) via API
   • Secure push without storing credentials
   • Step-by-step guided workflow

{SYM['code']} Developed by {DEV_INFO['name']}
{SYM['link']} {DEV_INFO['website']}

{SYM['heart']} MIT License | Free to use & modify
""")
    sys.exit(0)


def run_cmd(cmd, cwd=None, env=None, check=True, silent=False):
    """Run shell command with error handling."""
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True, cwd=cwd, env=env or os.environ)
        return result.stdout.strip() if not silent else None
    except subprocess.CalledProcessError as e:
        if not silent:
            print(f"\n{SYM['cross']} Command failed: {' '.join(cmd)}")
            if e.stderr: print(f"   {e.stderr.strip()}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{SYM['cross']} Error: {e}")
        sys.exit(1)


def step(n, total, title):
    """Print step header."""
    print(f"\n{'=' * 60}")
    print(f"  {SYM['folder']} STEP {n}/{total}: {title}")
    print(f"{'=' * 60}\n")


def is_sensitive(path: Path) -> bool:
    """Check if path matches sensitive patterns."""
    name = path.name
    suffix = path.suffix.lower()
    if name in SENSITIVE_PATTERNS or suffix in SECRET_EXTENSIONS:
        return True
    for pattern in SENSITIVE_PATTERNS:
        if pattern.startswith("*.") and name.endswith(pattern[2:]):
            return True
        if pattern.endswith("/") and path.is_dir() and name == pattern[:-1]:
            return True
    return False


def browse_path(start_path: Path = None) -> Path:
    """
    Interactive file/folder browser.
    - Click folder → navigate into it
    - Click file → return that file path
    - Use 'SELECT THIS FOLDER' → return current folder
    """
    current = start_path or Path.cwd()

    while True:
        items = []
        parent = current.parent if current != Path(current.root) else None

        # Parent navigation
        if parent:
            items.append(q.Choice(title=f"{SYM['up']} .. (Parent)", value="__UP__"))

        # List contents
        try:
            entries = sorted(current.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except (PermissionError, UnicodeEncodeError):
            print(f"   {SYM['warn']} Could not list: {current}")
            entries = []

        for entry in entries:
            try:
                if entry.is_dir():
                    # Folder: show with trailing slash, clicking navigates in
                    display = f"{SYM['folder']} {entry.name}/"
                    items.append(q.Choice(title=display, value=str(entry)))
                else:
                    # File: show with icon, clicking SELECTS the file
                    sensitive_tag = f" {SYM['lock']}" if is_sensitive(entry) else ""
                    display = f"{SYM['file']} {entry.name}{sensitive_tag}"
                    items.append(q.Choice(title=display, value=str(entry)))
            except UnicodeEncodeError:
                continue

        # Action separators
        items.append(q.Separator())
        items.append(q.Choice(title=f"{SYM['select']} SELECT THIS FOLDER: {current.name}/", value="__SELECT_FOLDER__"))
        items.append(q.Choice(title=f"{SYM['input']} Type path manually", value="__INPUT__"))
        items.append(q.Choice(title=f"{SYM['cross']} Cancel", value="__CANCEL__"))

        choice = q.select(f"{SYM['browse']} Browse: {current}", choices=items).ask()

        if choice in [None, "__CANCEL__"]:
            return None
        elif choice == "__UP__":
            current = parent
        elif choice == "__SELECT_FOLDER__":
            return current  # Return current folder as selected
        elif choice == "__INPUT__":
            path_input = q.text("Enter full path:", default=str(current)).ask()
            p = Path(path_input).resolve()
            if p.exists():
                return p
            print(f"   {SYM['cross']} Invalid path, try again.")
        elif choice and Path(choice).exists():
            selected = Path(choice)
            if selected.is_dir():
                # Clicking a folder navigates INTO it
                current = selected
            else:
                # ✅ Clicking a FILE returns that file directly!
                return selected
        else:
            return current


def select_files_to_stage(target_dir: Path) -> list:
    """Let user choose what to commit: all, specific files/folders, or quick."""
    mode = q.select(
        "What do you want to commit?",
        choices=[
            "All files in folder (auto-exclude sensitive)",
            "Select specific files/folders",
            "Quick: Stage everything (not recommended)"
        ]
    ).ask()

    if mode.startswith("Quick") or mode.startswith("All"):
        return ["."]

    # Specific selection mode
    print(f"   {SYM['browse']} Browsing from: {target_dir}")
    print(f"   💡 Click a {SYM['file']} file to select it, or {SYM['folder']} folder/ to navigate\n")

    selected = []
    while True:
        # Show current selection
        if selected:
            names = [Path(p).name for p in selected[:4]]
            extra = f" (+{len(selected) - 4} more)" if len(selected) > 4 else ""
            print(f"   {SYM['check']} Selected: {', '.join(names)}{extra}")

        action = q.select("Next action?",
                          choices=["➕ Add more files/folders", "✅ Finish & continue"]).ask()
        if action.startswith("✅"):
            break

        # Browse and pick
        chosen = browse_path(target_dir)
        if chosen is None:
            continue  # Cancelled

        # Convert to relative path if possible
        try:
            rel_path = chosen.relative_to(target_dir)
            selected.append(str(rel_path))
            item_type = "file" if chosen.is_file() else "folder"
            print(f"   {SYM['check']} Added {item_type}: {chosen.name}")
        except ValueError:
            # Outside target_dir, use absolute path
            selected.append(str(chosen))
            print(f"   {SYM['warn']} External path added: {chosen}")

    return selected if selected else ["."]


def update_gitignore(target_dir: Path, patterns: set):
    """Add patterns to .gitignore - UTF-8 encoded, NO EMOJIS in file content."""
    gitignore = target_dir / ".gitignore"
    existing = set()

    if gitignore.exists():
        try:
            with open(gitignore, 'r', encoding='utf-8', errors='ignore') as f:
                existing = set(line.strip() for line in f if line.strip() and not line.startswith("#"))
        except:
            pass

    new_patterns = patterns - existing
    if new_patterns:
        with open(gitignore, 'a', encoding='utf-8') as f:
            f.write("\n# Auto-protected by GitHub Publish CLI\n")
            for p in sorted(new_patterns):
                f.write(f"{p}\n")
        print(f"   {SYM['check']} Added {len(new_patterns)} patterns to .gitignore")


def filter_sensitive_from_staging(target_dir: Path):
    """Remove sensitive files from git staging (non-destructive)."""
    staged = run_cmd(["git", "ls-files", "--cached"], cwd=target_dir, silent=True)
    if not staged:
        return

    for line in staged.split("\n"):
        file_path = Path(line.strip())
        if file_path.name and is_sensitive(file_path):
            run_cmd(["git", "rm", "--cached", str(file_path)], cwd=target_dir, check=False, silent=True)
            print(f"   {SYM['lock']} Excluded: {file_path.name}")


def print_footer():
    """Print developer credit footer."""
    print(f"\n{'─' * 60}")
    print(f"  {SYM['code']} Developed By: {DEV_INFO['name']}")
    print(f"  {SYM['link']} {DEV_INFO['website']}")
    print(f"  {SYM['heart']} Share: Twitter @{SYM['link']}twitter.com/selfmrj")
    print(f"{'─' * 60}\n")


# ── MAIN ─────────────────────────────────────────────────────
def main():
    # Handle CLI arguments
    if "--info" in sys.argv or "-i" in sys.argv:
        show_info()
    if "--help" in sys.argv or "-h" in sys.argv:
        show_help()

    print(f"{SYM['star']} GitHub Publish CLI | v4.3")
    print(f"   {SYM['code']} By {DEV_INFO['name']} | {DEV_INFO['website']}\n")

    # ── STEP 1: Select Directory ───────────────────────────────
    step(1, 7, "Select Project Location")
    print("   Navigate drives or enter path manually.\n")

    method = q.select("How to select?", choices=["Interactive browser", "Type path manually"]).ask()

    if method.startswith("Interactive"):
        target_dir = browse_path()
    else:
        target_dir = Path(q.text("Enter full path:", default=str(Path.cwd())).ask()).resolve()

    if target_dir is None:
        sys.exit(f"{SYM['cross']} Selection cancelled")
    if not target_dir.exists():
        sys.exit(f"{SYM['cross']} Path not found: {target_dir}")
    if not target_dir.is_dir():
        print(f"   {SYM['file']} File selected: {target_dir.name}")
        target_dir = target_dir.parent

    print(f"   {SYM['check']} Working directory: {target_dir}")

    # ── STEP 2: Git Initialization ─────────────────────────────
    step(2, 7, "Initialize Git Repository")
    if not (target_dir / ".git").exists():
        if q.confirm("No .git folder. Run 'git init' now?", default=True).ask():
            run_cmd(["git", "init", "-b", "main"], cwd=target_dir)
            print("   Git initialized")
    else:
        print("   Existing Git repository")

    # ── STEP 3: Security Setup ─────────────────────────────────
    step(3, 7, "Security: Protect Sensitive Files")
    update_gitignore(target_dir, SENSITIVE_PATTERNS)
    print("   Sensitive file protection: ACTIVE")

    # ── STEP 4: Select Files to Stage ──────────────────────────
    step(4, 7, "Select Files to Commit")
    to_stage = select_files_to_stage(target_dir)

    print("   Staging files...")
    run_cmd(["git", "add"] + to_stage, cwd=target_dir)
    filter_sensitive_from_staging(target_dir)

    changes = run_cmd(["git", "status", "--short"], cwd=target_dir, silent=True)
    if changes:
        preview = changes[:500].replace('\n', '\n   ')
        print(f"   To be committed:\n   {preview}")

    # ── STEP 5: Commit ─────────────────────────────────────────
    step(5, 7, "Create Commit")
    commit_msg = q.text("Commit message:", default="Initial commit").ask().strip()
    if not commit_msg:
        sys.exit("Message required")

    run_cmd(["git", "commit", "-m", commit_msg], cwd=target_dir)
    print("   Committed successfully")

    # ── STEP 6: GitHub Setup ───────────────────────────────────
    step(6, 7, "GitHub Repository Details")
    repo_name = q.text("Repository name:", validate=lambda x: "Required" if not x.strip() else True).ask().strip()
    visibility = q.select("Visibility:", choices=["Public", "Private"]).ask()
    is_private = (visibility == "Private")

    print("\n   GitHub Personal Access Token (scope: repo)")
    print("   Create: https://github.com/settings/tokens/new")
    print("   Never stored on disk\n")
    token = q.password("   Token: ").ask()
    if not token:
        sys.exit("Token required")

    print("   Verifying token...")
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get("https://api.github.com/user", headers=headers)
    if r.status_code != 200:
        sys.exit("Invalid token or missing 'repo' scope")

    github_user = r.json()["login"]
    print(f"   Authenticated: @{github_user}")

    # ── STEP 7: Create & Push ──────────────────────────────────
    step(7, 7, "Create Repository & Push")
    print("   Creating on GitHub...")
    repo_data = {"name": repo_name, "private": is_private, "auto_init": False}
    r = requests.post("https://api.github.com/user/repos", json=repo_data, headers=headers)

    if r.status_code not in (200, 201):
        err = r.json().get("message", "Unknown error")
        if "already exists" in err.lower():
            sys.exit(f"'{repo_name}' exists. Choose another name.")
        sys.exit(f"Create failed: {err}")

    repo_url = r.json()["html_url"]
    remote_url = f"https://github.com/{github_user}/{repo_name}.git"

    print("   Configuring remote...")
    run_cmd(["git", "remote", "remove", "origin"], cwd=target_dir, check=False, silent=True)
    run_cmd(["git", "remote", "add", "origin", remote_url], cwd=target_dir)

    branch = run_cmd(["git", "branch", "--show-current"], cwd=target_dir) or "main"
    print(f"   {SYM['rocket']} Pushing to {branch}...")

    env = os.environ.copy()
    env.update({"GIT_TERMINAL_PROMPT": "0", "GIT_USERNAME": "x-access-token", "GIT_PASSWORD": token})
    run_cmd(["git", "push", "-u", "origin", branch], cwd=target_dir, env=env)

    # ── SUCCESS + FOOTER ───────────────────────────────────────
    print(f"\n{SYM['party'] * 8}")
    print(f"   {SYM['check']} Published! {repo_url}")
    print(f"   {SYM['folder']} Local: {target_dir}")
    print(f"   {SYM['lock']} Protected patterns: {len(SENSITIVE_PATTERNS)}")

    print_footer()
    print(f"   {SYM['heart']} Tip: Run with --info to see all developer links\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{SYM['warn']} Cancelled by user")
        print_footer()
        sys.exit(0)
    except UnicodeEncodeError as e:
        print(f"\n{SYM['cross']} Encoding error: {e}")
        print("   Tip: Run 'chcp 65001' in CMD for UTF-8 support")
        print_footer()
        sys.exit(1)
    except Exception as e:
        print(f"\n{SYM['cross']} Unexpected error: {e}")
        import traceback;

        traceback.print_exc()
        print_footer()
        sys.exit(1)
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from playwright.sync_api import Page, sync_playwright

DEFAULT_HOME = "https://www.google.com"
BOOKMARKS_FILE = Path("bookmarks.json")


@dataclass
class Bookmark:
    title: str
    url: str


class BrowserApp:
    def __init__(self) -> None:
        self.bookmarks: List[Bookmark] = []
        self.pages: List[Page] = []
        self.active_index: int = 0
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context()

    def start(self, initial_url: str = DEFAULT_HOME) -> None:
        self.new_tab(initial_url)
        self.run_command_loop()

    def run_command_loop(self) -> None:
        print("Borgor Browser (Playwright Edition)")
        print("Type 'help' for commands. 'quit' to exit.")
        while True:
            try:
                command = input("borgor> ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nExiting...")
                break

            if not command:
                continue

            if not self.handle_command(command):
                break

        self.shutdown()

    def handle_command(self, command: str) -> bool:
        parts = command.split()
        action = parts[0].lower()
        args = parts[1:]

        handlers = {
            "help": self.show_help,
            "open": self.open_url,
            "newtab": self.new_tab,
            "tabs": self.list_tabs,
            "switch": self.switch_tab,
            "back": self.go_back,
            "forward": self.go_forward,
            "reload": self.reload,
            "bookmark": self.handle_bookmark,
            "save": self.save_bookmarks,
            "load": self.load_bookmarks,
            "quit": self.quit,
            "exit": self.quit,
        }

        handler = handlers.get(action)
        if not handler:
            print(f"Unknown command: {action}. Type 'help' for a list of commands.")
            return True

        return handler(args)

    def show_help(self, _args: List[str]) -> bool:
        print(
            "\nCommands:\n"
            "  open <url>            Navigate the current tab to a URL\n"
            "  newtab [url]          Open a new tab (defaults to homepage)\n"
            "  tabs                  List open tabs\n"
            "  switch <index>        Switch to a tab by index\n"
            "  back                  Go back in history\n"
            "  forward               Go forward in history\n"
            "  reload                Reload the current tab\n"
            "  bookmark add          Bookmark the current page\n"
            "  bookmark list         List bookmarks\n"
            "  bookmark open <index> Open a bookmarked page in the current tab\n"
            "  save [file]           Save bookmarks to file (default bookmarks.json)\n"
            "  load [file]           Load bookmarks from file (default bookmarks.json)\n"
            "  quit                  Exit the browser\n"
        )
        return True

    def open_url(self, args: List[str]) -> bool:
        if not args:
            print("Usage: open <url>")
            return True
        url = self.normalize_url(args[0])
        page = self.current_page()
        page.goto(url)
        print(f"Navigated to {url}")
        return True

    def new_tab(self, args: Optional[List[str]] = None) -> bool:
        url = DEFAULT_HOME
        if args:
            url = self.normalize_url(args[0])
        page = self.context.new_page()
        page.goto(url)
        self.pages.append(page)
        self.active_index = len(self.pages) - 1
        print(f"Opened new tab ({self.active_index}) -> {url}")
        return True

    def list_tabs(self, _args: List[str]) -> bool:
        for index, page in enumerate(self.pages):
            title = page.title() or "(untitled)"
            active_marker = "*" if index == self.active_index else " "
            print(f"{active_marker} [{index}] {title} - {page.url}")
        return True

    def switch_tab(self, args: List[str]) -> bool:
        if not args:
            print("Usage: switch <index>")
            return True
        try:
            index = int(args[0])
        except ValueError:
            print("Tab index must be a number.")
            return True
        if not (0 <= index < len(self.pages)):
            print("Tab index out of range.")
            return True
        self.active_index = index
        page = self.current_page()
        page.bring_to_front()
        print(f"Switched to tab {index}: {page.url}")
        return True

    def go_back(self, _args: List[str]) -> bool:
        self.current_page().go_back()
        return True

    def go_forward(self, _args: List[str]) -> bool:
        self.current_page().go_forward()
        return True

    def reload(self, _args: List[str]) -> bool:
        self.current_page().reload()
        return True

    def handle_bookmark(self, args: List[str]) -> bool:
        if not args:
            print("Usage: bookmark <add|list|open>")
            return True

        action = args[0].lower()
        if action == "add":
            return self.add_bookmark()
        if action == "list":
            return self.list_bookmarks()
        if action == "open":
            return self.open_bookmark(args[1:])

        print("Unknown bookmark action. Use add, list, or open.")
        return True

    def add_bookmark(self) -> bool:
        page = self.current_page()
        title = page.title() or page.url
        bookmark = Bookmark(title=title, url=page.url)
        if bookmark in self.bookmarks:
            print("Bookmark already exists.")
            return True
        self.bookmarks.append(bookmark)
        print(f"Bookmarked {title}")
        return True

    def list_bookmarks(self) -> bool:
        if not self.bookmarks:
            print("No bookmarks saved.")
            return True
        for index, bookmark in enumerate(self.bookmarks):
            print(f"[{index}] {bookmark.title} - {bookmark.url}")
        return True

    def open_bookmark(self, args: List[str]) -> bool:
        if not args:
            print("Usage: bookmark open <index>")
            return True
        try:
            index = int(args[0])
        except ValueError:
            print("Bookmark index must be a number.")
            return True
        if not (0 <= index < len(self.bookmarks)):
            print("Bookmark index out of range.")
            return True
        url = self.bookmarks[index].url
        self.current_page().goto(url)
        print(f"Opened bookmark {index} -> {url}")
        return True

    def save_bookmarks(self, args: List[str]) -> bool:
        file_path = Path(args[0]) if args else BOOKMARKS_FILE
        data = [bookmark.__dict__ for bookmark in self.bookmarks]
        file_path.write_text(json.dumps(data, indent=2))
        print(f"Saved {len(self.bookmarks)} bookmarks to {file_path}")
        return True

    def load_bookmarks(self, args: List[str]) -> bool:
        file_path = Path(args[0]) if args else BOOKMARKS_FILE
        if not file_path.exists():
            print(f"Bookmark file not found: {file_path}")
            return True
        data = json.loads(file_path.read_text())
        self.bookmarks = [Bookmark(**entry) for entry in data]
        print(f"Loaded {len(self.bookmarks)} bookmarks from {file_path}")
        return True

    def quit(self, _args: List[str]) -> bool:
        return False

    def current_page(self) -> Page:
        if not self.pages:
            self.new_tab([DEFAULT_HOME])
        return self.pages[self.active_index]

    @staticmethod
    def normalize_url(url: str) -> str:
        if url.startswith("http://") or url.startswith("https://"):
            return url
        return f"https://{url}"

    def shutdown(self) -> None:
        for page in self.pages:
            if not page.is_closed():
                page.close()
        self.context.close()
        self.browser.close()
        self.playwright.stop()


def main() -> None:
    app = BrowserApp()
    app.start(DEFAULT_HOME)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Fatal error: {exc}", file=sys.stderr)
        sys.exit(1)

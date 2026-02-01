# BB Browser (Playwright Edition)

A lightweight command-line browser controller built on top of **Playwright Chromium**. It opens real Chromium windows and lets you manage tabs, navigation, and bookmarks from a simple terminal prompt.

## Features

- **Playwright Chromium**: Real browser windows (no PyQtWebEngine).
- **Multiple Tabs**: Open and switch between tabs.
- **Bookmarks**: Save, load, and open bookmarked pages.
- **Navigation Controls**: Back, forward, reload, open URL.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/BorgorNinja/Borgor-Browser.git
   cd Borgor-Browser
   ```

2. **Set Up a Virtual Environment** (recommended)

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   ```bash
   pip install playwright
   playwright install chromium
   ```

## Usage

Launch the browser controller:

```bash
python browser.py
```

You will see a prompt:

```
borgor>
```

### Command Reference

- `open <url>` – Navigate the current tab to a URL
- `newtab [url]` – Open a new tab (defaults to homepage)
- `tabs` – List open tabs
- `switch <index>` – Switch to a tab by index
- `back` – Go back in history
- `forward` – Go forward in history
- `reload` – Reload the current tab
- `bookmark add` – Bookmark the current page
- `bookmark list` – List bookmarks
- `bookmark open <index>` – Open a bookmark in the current tab
- `save [file]` – Save bookmarks (default `bookmarks.json`)
- `load [file]` – Load bookmarks (default `bookmarks.json`)
- `quit` – Exit the browser

## Notes

- Chromium opens in non-headless mode so you can interact with pages visually.
- Bookmarks are stored in JSON format for easy editing.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

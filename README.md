
# BB Browser

An enhanced web browser application built using PyQt5 and PyQtWebEngine. This browser supports multiple tabs, bookmarks, and has a progress bar to indicate page loading status.

## Features

- **Multiple Tabs**: Open and manage multiple web pages in separate tabs.
- **Bookmarks**: Add, view, and manage bookmarks.
- **Progress Bar**: See the progress of page loading.
- **Navigation Controls**: Back, forward, reload, and open new tabs.
- **Search Functionality**: Navigate to URLs directly from the address bar or search button.

## Installation

To get started with this project, you'll need to have Python 3.x installed on your system. Follow these steps to set up your environment:

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
   pip install PyQt5 PyQtWebEngine
   ```

## Usage

To run the browser, execute the following command in your terminal or command prompt:

```bash
python browser.py
```

### Features Usage

- **Open a New Tab**: Click the "New Tab" button in the navigation bar.
- **Navigate to a URL**: Enter a URL in the address bar and press Enter, or click the "Search" button.
- **Bookmark a Page**: Click the "Bookmark" button in the navigation bar to add the current page to your bookmarks.
- **Manage Bookmarks**: Use the "File" menu to load or save bookmarks.

## Contributing

Contributions are welcome! If you would like to contribute to this project, please follow these steps:

1. **Fork the Repository**
2. **Create a New Branch**

   ```bash
   git checkout -b feature/your-feature
   ```

3. **Make Your Changes**
4. **Commit Your Changes**

   ```bash
   git add .
   git commit -m "Add new feature"
   ```

5. **Push to Your Fork**

   ```bash
   git push origin feature/your-feature
   ```

6. **Create a Pull Request**

   Go to the original repository on GitHub and create a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- **PyQt5**: The Python bindings for the Qt application framework.
- **QtWebEngine**: A set of classes for web content in applications.

## Troubleshooting

If you encounter issues running the application, ensure that all dependencies are installed and up-to-date. If `Qt5Core.dll` is missing, make sure to install or update `PyQt5` and `PyQtWebEngine`, and verify that the DLL files are present in your Python environment's `site-packages` directory.

For further assistance, please check the [GitHub Issues](https://github.com/yourusername/qtwebengine-browser/issues) page or create a new issue with details about the problem you're facing.

---

Feel free to replace `yourusername` with your actual GitHub username and adjust the repository URL accordingly. This `README.md` provides a comprehensive guide to setting up, using, and contributing to your QtWebEngine browser project.

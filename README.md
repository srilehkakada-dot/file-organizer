# 🗂️ File Organizer

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Tests](https://img.shields.io/badge/tests-17%20passed-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

Automatically organizes files in a directory into category subfolders — Images, Documents, Videos, Audio, Archives, Code, Executables, Fonts, and Others.

## 🚀 Live Demos

| Demo | Link |
|---|---|
| 🌐 GitHub Pages | ` https://srilehkakada-dot.github.io/file-organizer/` |
| ⚡ Streamlit App | `https://file-organizer-ud2qqx9hjbbnkfkgvkrkbn.streamlit.app/` |

---

## 📦 Project Structure

```
file_organizer/
├── file_organizer.py      # Core logic
├── gui.py                 # Tkinter desktop GUI
├── streamlit_app.py       # Streamlit web app
├── test_file_organizer.py # Unit tests (17 tests)
├── requirements.txt       # Streamlit dependency
├── README.md
└── docs/
    └── index.html         # GitHub Pages demo
```

---

## 🖥️ Run Locally

### Desktop GUI
```bash
python gui.py
```

### Streamlit Web App
```bash
pip install streamlit
streamlit run streamlit_app.py
```

### CLI
```bash
python file_organizer.py C:\Users\you\Downloads --preview
python file_organizer.py C:\Users\you\Downloads
python file_organizer.py C:\Users\you\Downloads --categories Images Documents
```

---

## 📂 Categories

| Category | Extensions |
|---|---|
| Images | jpg, jpeg, png, gif, bmp, svg, webp, ico, tiff, heic |
| Documents | pdf, doc, docx, xls, xlsx, ppt, pptx, txt, rtf, csv, md |
| Videos | mp4, mkv, avi, mov, wmv, flv, webm |
| Audio | mp3, wav, aac, flac, ogg, wma, m4a |
| Archives | zip, tar, gz, rar, 7z, bz2 |
| Code | py, js, ts, html, css, java, cpp, go, rs |
| Executables | exe, msi, dmg, apk, deb, rpm |
| Fonts | ttf, otf, woff, woff2 |
| Others | everything else |

---

## ✅ Tests
```bash
python -m unittest test_file_organizer -v
```

## 📄 License
MIT

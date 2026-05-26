import streamlit as st
import tempfile
import os
import shutil
from pathlib import Path
from file_organizer import organize, CATEGORIES

st.set_page_config(
    page_title="File Organizer",
    page_icon="🗂️",
    layout="wide",
)

st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    .stButton > button { width: 100%; }
    .log-ok    { color: #1D9E75; font-family: monospace; font-size: 13px; }
    .log-skip  { color: #D85A30; font-family: monospace; font-size: 13px; }
    .log-info  { color: #888;    font-family: monospace; font-size: 13px; }
    .stat-box  { background: #f5f5f3; border-radius: 10px; padding: 1rem; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("🗂️ File Organizer")
st.caption("Upload files, pick categories, and organize them instantly.")

st.divider()

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📁 Upload Files")
    uploaded_files = st.file_uploader(
        "Drop files here to organize",
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    st.subheader("⚙️ Options")
    preview_mode   = st.toggle("Preview only (don't move)", value=True)
    skip_dups      = st.toggle("Skip duplicate files",       value=True)
    auto_rename    = st.toggle("Auto-rename conflicts",      value=False)

    st.subheader("📂 Categories to organize")
    cat_cols = st.columns(2)
    selected_cats = []
    for i, cat in enumerate(CATEGORIES.keys()):
        with cat_cols[i % 2]:
            if st.checkbox(cat, value=True):
                selected_cats.append(cat)

with col2:
    st.subheader("📊 Results")

    if not uploaded_files:
        st.info("Upload some files on the left to get started.")
    else:
        st.write(f"**{len(uploaded_files)} files** ready to organize.")

        if st.button("▶ Organize Files", type="primary"):
            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)

                for f in uploaded_files:
                    dest = tmp_path / f.name
                    dest.write_bytes(f.read())

                import io, contextlib
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    stats = organize(
                        directory=str(tmp_path),
                        preview=preview_mode,
                        skip_duplicates=skip_dups,
                        auto_rename=auto_rename,
                        recurse=False,
                        categories=selected_cats if selected_cats else None,
                    )

                m1, m2, m3 = st.columns(3)
                m1.metric("Files found",  len(uploaded_files))
                m2.metric("Moved",        stats.get("moved", 0))
                m3.metric("Skipped",      stats.get("skipped", 0) + stats.get("duplicates", 0))

                st.divider()
                st.markdown("**Activity log**")
                log_html = ""
                for line in buf.getvalue().splitlines():
                    if "MOVE" in line or "Done" in line:
                        log_html += f'<div class="log-ok">{line}</div>'
                    elif "SKIP" in line or "Error" in line:
                        log_html += f'<div class="log-skip">{line}</div>'
                    else:
                        log_html += f'<div class="log-info">{line}</div>'
                st.markdown(
                    f'<div style="background:#1e1e1e;padding:1rem;border-radius:8px;max-height:320px;overflow-y:auto">{log_html}</div>',
                    unsafe_allow_html=True,
                )

                if not preview_mode:
                    st.divider()
                    st.markdown("**Download organized files**")
                    zip_buf = io.BytesIO()
                    import zipfile
                    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                        for fpath in Path(tmp).rglob("*"):
                            if fpath.is_file():
                                zf.write(fpath, fpath.relative_to(tmp))
                    zip_buf.seek(0)
                    st.download_button(
                        "⬇️ Download organized ZIP",
                        data=zip_buf,
                        file_name="organized_files.zip",
                        mime="application/zip",
                    )

st.divider()
with st.expander("📖 How it works"):
    st.markdown("""
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
""")

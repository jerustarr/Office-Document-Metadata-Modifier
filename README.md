# DOCX Metadata Automation Script

## Overview
This project provides a Python script to **edit and manage Microsoft Word (DOCX) metadata**.  
It works by directly modifying the `core.xml` and `app.xml` files inside the Office Open XML structure of a `.docx` file.  

With this tool, you can update:
- **Created / Modified timestamps**
- **Last modified by (author)**
- **Document statistics** (total time, pages, words, characters)
- **Filesystem timestamps** (on macOS, using `SetFile`)

---

## Features
- **[Metadata editing](ca://s?q=GitHub_DOCX_metadata_editing)**: Change creation and modification dates, author, and other properties.  
- **[Document statistics](ca://s?q=GitHub_DOCX_document_statistics)**: Update fields like total time, pages, words, and characters.  
- **[Filesystem integration](ca://s?q=GitHub_DOCX_filesystem_integration)**: Optionally sync metadata with filesystem timestamps.  
- **[Cross‑platform Python script](ca://s?q=GitHub_DOCX_cross_platform_python)**: Works on Linux, macOS, and Windows (with minor adjustments).  

---

## Usage
```bash
python set_docx_metadata.py /path/to/file.docx \
  --created "2026-05-01T12:00:00" \
  --modified "2026-05-01T12:00:00" \
  --lastmodifiedby "Your Name" \
  --totaltime 42 \
  --setfs
```
## Xfiles usage common commands 
tbc 

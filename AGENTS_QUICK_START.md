# Quick Start: OCR Extraction Agents

## 🎯 30 Seconds Overview

**What:** 5 agents extract metadata from OCR → MARC21  
**Where:** `backend/services/agents/`  
**Test:** `python demo_agents.py --mode all`

---

## 📊 Agents Summary

| Agent | Input | Output | MARC |
|-------|-------|--------|------|
| **1. Title** | OCR text | "Clinical Medicine" | 245 |
| **2. Authors** | OCR text | ["Doe, John"] | 100, 700 |
| **3. ISBN/Year** | OCR text | "978-X-XX-X", 2024 | 020, 260 |
| **4. Keywords** | Keywords | MESH/LCSH terms | 050, 060, 650 |
| **5. Doc Type** | OCR text | "textbook" | Leader |

---

## 🚀 Quick Usage

### One-Line Integration

```python
from backend.services.agents import MARCIntegration

marc_record = MARCIntegration().agents_output_to_marc21(ocr_text)
```

### Individual Agents

```python
from backend.services.agents import (
    TitleExtractor, 
    AuthorExtractor,
    ISBNYearExtractor,
    DocumentTypeClassifier
)

# Extract components
title = TitleExtractor().extract_title(ocr_text)
authors = AuthorExtractor().extract_authors(ocr_text)
isbn, year = ISBNYearExtractor().extract_both(ocr_text)
doc_type = DocumentTypeClassifier().classify_document_type(ocr_text)
```

---

## 🧪 Test Commands

```bash
# Test all
python demo_agents.py --mode all

# Test individual
python demo_agents.py --mode individual

# Test integration only
python demo_agents.py --mode integration

# Test specific agent
python backend/services/agents/agent_1_title.py
```

---

## 💡 Example

### Input (OCR Text)

```
Introduction to Clinical Medicine
Third Edition
By Dr. John Smith, MD
ISBN: 978-0-123-45678-9
Copyright © 2024
```

### Output (MARC21)

```
100 1  $aDr. John Smith, MD
245 10 $aIntroduction to Clinical Medicine
260    $c2024
650  0 $aClinical Medicine
```

---

## 📁 Files

```
backend/services/agents/
├── agent_1_title.py         # Title
├── agent_2_author.py        # Authors
├── agent_3_isbn_year.py     # ISBN & Year
├── agent_5_doctype.py       # Doc Type
└── marc_integration.py      # Integration

backend/examples/
└── agent_4_integration.py   # Keywords
```

---

## ✨ Features

✅ 5 specialized agents  
✅ MARC21 compliant  
✅ Multilingual (EN + VI)  
✅ ISBN validation  
✅ Authority control  
✅ 64+ test cases

---

**For details:** See `AGENTS_IMPLEMENTATION_SUMMARY.md`  
**Status:** ✅ Production Ready

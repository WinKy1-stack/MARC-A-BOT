# Tool: get_classification_and_keywords

## 🎯 Mục Đích

Tool này được thiết kế đặc biệt để trả về **KHUNG PHÂN LOẠI** và **TỪ KHÓA CHUẨN** - hai output quan trọng nhất cho việc biên mục thư viện.

## 📊 Output Chính

### 1. KHUNG PHÂN LOẠI (Classification Framework)

Là các số phân loại để xếp sách trên kệ:

- **LCC** (Library of Congress Classification) - Cho tài liệu general/science
  - Example: `QA76.9.A25` (Machine Learning)
  - MARC Field: `050`

- **NLM** (National Library of Medicine Classification) - Cho tài liệu medical
  - Example: `WK 810` (Diabetes Mellitus)
  - MARC Field: `060`

### 2. TỪ KHÓA CHUẨN (Controlled Keywords)

Là thuật ngữ chuẩn để tìm kiếm và tra cứu:

- **MESH** (Medical Subject Headings) - Cho medical
  - Example: `Diabetes Mellitus` (D003920)
  - MARC Field: `650 _2`

- **LCSH** (Library of Congress Subject Headings) - Cho general/science
  - Example: `Machine learning`
  - MARC Field: `650 _0`

## 📥 Input

```json
{
  "keywords": ["diabetes", "insulin", "glucose"],
  "subject_type": "medical"
}
```

**Parameters:**
- `keywords` (array, required): Danh sách keywords raw từ OCR/Agent
- `subject_type` (string, optional): `"medical"` | `"general"` | `"science"`

## 📤 Output Structure

```json
{
  "success": true,
  "input_keywords": ["diabetes", "insulin", "glucose"],
  "subject_type": "medical",
  "output": {
    "classification_framework": [
      {
        "framework": "NLM",
        "classification_number": "WK 810",
        "description": "Diabetes Mellitus",
        "marc_field": "060"
      }
    ],
    "controlled_keywords": [
      {
        "keyword": "Diabetes Mellitus",
        "vocabulary": "MESH",
        "term_id": "D003920",
        "confidence": 95.5,
        "marc_field": "650"
      },
      {
        "keyword": "Insulin",
        "vocabulary": "MESH",
        "term_id": "D007334",
        "confidence": 98.0,
        "marc_field": "650"
      }
    ]
  },
  "marc_fields": {
    "classification": [
      "060 _4 $a WK 810"
    ],
    "subjects": [
      "650 _2 $a Diabetes Mellitus",
      "650 _2 $a Insulin"
    ]
  },
  "summary": {
    "total_keywords": 3,
    "classifications_found": 1,
    "controlled_terms_found": 2,
    "uncontrolled_terms": 1
  }
}
```

## 🔗 API Endpoint

```
POST /api/authority/classification-keywords
```

## 📝 Usage Examples

### Example 1: Medical Document

```python
import requests

keywords = ["diabetes mellitus", "insulin therapy", "glucose monitoring"]

response = requests.post(
    'http://localhost:5000/api/authority/classification-keywords',
    json={
        'keywords': keywords,
        'subject_type': 'medical'
    }
)

result = response.json()

# Get classification framework
classifications = result['output']['classification_framework']
for cls in classifications:
    print(f"Khung: {cls['framework']} {cls['classification_number']}")
    # Output: Khung: NLM WK 810

# Get controlled keywords
keywords = result['output']['controlled_keywords']
for kw in keywords:
    print(f"Từ khóa: {kw['keyword']} ({kw['vocabulary']})")
    # Output: Từ khóa: Diabetes Mellitus (MESH)
```

### Example 2: Computer Science Document

```python
keywords = ["machine learning", "neural networks"]

response = requests.post(
    'http://localhost:5000/api/authority/classification-keywords',
    json={
        'keywords': keywords,
        'subject_type': 'science'
    }
)

result = response.json()

# Output:
# Khung: LCC QA76.9.M35
# Từ khóa: Machine learning (LCSH)
```

### Example 3: Integration với Agent 4

```python
# Agent 4 workflow
def agent_4_process(ocr_text):
    # Step 1: Extract keywords (AI logic)
    keywords = extract_keywords(ocr_text)
    
    # Step 2: Get classification & keywords
    response = requests.post(
        'http://localhost:5000/api/authority/classification-keywords',
        json={'keywords': keywords, 'subject_type': 'medical'}
    )
    
    result = response.json()
    
    return {
        'classification_framework': result['output']['classification_framework'],
        'controlled_keywords': result['output']['controlled_keywords'],
        'marc_fields': result['marc_fields']
    }
```

## 🆚 So sánh với Tool Khác

### Tool: `map_keywords_to_authorities`

**Output:**
```json
{
  "authorities": [...],  // Mixed data
  "marc_fields": [...]   // Chỉ có 650 fields
}
```

**Use case:** General mapping

### Tool: `get_classification_and_keywords` ⭐ NEW

**Output:**
```json
{
  "classification_framework": [...],  // Tách riêng KHUNG
  "controlled_keywords": [...],       // Tách riêng TỪ KHÓA
  "marc_fields": {
    "classification": [...],          // 050/060 fields
    "subjects": [...]                 // 650 fields
  }
}
```

**Use case:** Output RÕ RÀNG cho agent, tách biệt khung và từ khóa

## 💡 Benefits

### 1. Output Rõ Ràng
- **Khung phân loại** và **từ khóa** tách biệt
- Dễ hiểu, dễ sử dụng cho agent

### 2. Structured Data
- Classification: Framework + Number + Description
- Keywords: Term + Vocabulary + Confidence + Term ID

### 3. MARC21 Ready
- Classification fields (050/060) sẵn sàng
- Subject fields (650) sẵn sàng
- Format chuẩn MARC21

### 4. Agent Friendly
- JSON structure rõ ràng
- Easy to parse và sử dụng
- Complete metadata included

## 🎯 Use Cases

### Use Case 1: Cataloging Workflow
```
OCR Text → Agent 4 Extract → Tool → Classification + Keywords → MARC Record
```

### Use Case 2: Auto Classification
```
Keywords → Tool → Classification Number → Shelf Location
```

### Use Case 3: Subject Indexing
```
Keywords → Tool → Controlled Terms → Search Index
```

## 📚 MARC21 Fields Generated

### Classification Fields

**Medical Documents:**
```
060 _4 $a WK 810        # NLM Classification
```

**General/Science Documents:**
```
050 _4 $a QA76.9.M35    # LCC Classification
```

### Subject Heading Fields

**Medical:**
```
650 _2 $a Diabetes Mellitus $0 (DNLM)D003920
650 _2 $a Insulin $0 (DNLM)D007334
```

**General/Science:**
```
650 _0 $a Machine learning
650 _0 $a Neural networks (Computer science)
```

## 🔧 Configuration

Tool sử dụng priority sources based on `subject_type`:

**Medical:**
1. MESH (keywords)
2. NLM (classification)
3. LCSH (fallback)

**Science/General:**
1. LCSH (keywords)
2. LCC (classification)

## 📈 Performance

- Cache-enabled: < 100ms
- API call: < 1s
- Batch processing: ~200ms per keyword

## 🧪 Testing

```powershell
# Test tool
python backend/examples/classification_keywords_tool.py

# Test API
curl -X POST http://localhost:5000/api/authority/classification-keywords `
  -H "Content-Type: application/json" `
  -d '{\"keywords\": [\"diabetes\"], \"subject_type\": \"medical\"}'
```

## 📞 Support

- **Example Code:** `backend/examples/classification_keywords_tool.py`
- **API Docs:** `/api/authority/tools`
- **Test:** `python backend/test_complete_workflow.py`

## ✅ Checklist

Khi sử dụng tool này, output sẽ bao gồm:

- [x] **Khung phân loại** (LCC/NLM numbers) để xếp sách
- [x] **Từ khóa chuẩn** (MESH/LCSH terms) để tìm kiếm
- [x] **MARC 050/060** fields cho classification
- [x] **MARC 650** fields cho subject headings
- [x] **Confidence scores** cho quality check
- [x] **Statistics** cho monitoring

---

**Perfect for Agent 4 Integration! 🚀**

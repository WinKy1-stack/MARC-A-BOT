"""
Agent 4: Keywords & Subject Headings Extractor
Trích xuất keywords và map sang authority (LCSH/MeSH/LCC/NLM) - MARC21 Field 650 + 050/090
"""
import re
import logging
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

try:
    from services.authority.tools import AuthorityTools
    from services.authority.authority_service import AuthorityService
except ImportError:
    AuthorityTools = None
    AuthorityService = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Stopwords (tiếng Anh và tiếng Việt)
STOPWORDS_EN = {
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
    'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
    'could', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
}

STOPWORDS_VN = {
    'và', 'của', 'cho', 'với', 'từ', 'trong', 'đến', 'là', 'có', 'được',
    'sẽ', 'đã', 'một', 'những', 'các', 'về', 'theo', 'vì', 'nếu', 'khi'
}


class KeywordExtractor:
    """
    Agent 4: Trích xuất keywords và map sang authority terms
    MARC21 Fields: 650 (Subject Headings), 050/090 (Classification)
    """
    
    def __init__(self):
        """Khởi tạo Agent 4 với Authority Tools"""
        self.authority_tools = AuthorityTools() if AuthorityTools else None
        if not self.authority_tools:
            logger.warning("AuthorityTools không khả dụng, Agent 4 sẽ hoạt động ở chế độ đơn giản")
    
    def extract_keywords(self, ocr_text: str, title: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Trích xuất keywords từ OCR text
        
        Args:
            ocr_text: Raw OCR text (đã được clean)
            title: Tiêu đề sách (nếu có, từ Agent 1)
            
        Returns:
            List of dict:
            [
                {"keyword": "giáo dục đại học Việt Nam", "score": 0.9},
                {"keyword": "giáo sư Trần Hồng Quân", "score": 0.85}
            ]
        
        Logic:
        - Lấy keyword từ title (nếu có)
        - Trích xuất từ toàn bộ ocr_text
        - Loại bỏ stopwords (EN + VN)
        - Tính score dựa trên tần suất và vị trí
        """
        if not ocr_text or not ocr_text.strip():
            logger.warning("Empty OCR text")
            return []
        
        keywords = []
        text_lower = ocr_text.lower()
        
        # Bước 1: Trích keywords từ title (nếu có)
        if title:
            title_keywords = self._extract_from_text(title, weight=1.0)
            keywords.extend(title_keywords)
        
        # Bước 2: Trích keywords từ toàn bộ text
        # Tách thành các câu/phrase quan trọng
        text_keywords = self._extract_from_text(ocr_text, weight=0.7)
        keywords.extend(text_keywords)
        
        # Bước 3: Loại bỏ stopwords và chuẩn hóa
        keywords = self._filter_stopwords(keywords)
        
        # Bước 4: Loại bỏ duplicate và merge scores
        keywords = self._deduplicate_keywords(keywords)
        
        # Bước 5: Sắp xếp theo score
        keywords = sorted(keywords, key=lambda x: x['score'], reverse=True)
        
        # Chỉ lấy top keywords (tối đa 10)
        keywords = keywords[:10]
        
        logger.info(f"Extracted {len(keywords)} keywords")
        return keywords
    
    def _extract_from_text(self, text: str, weight: float = 1.0) -> List[Dict[str, Any]]:
        """
        Trích xuất keywords từ một đoạn text
        
        Args:
            text: Text để trích xuất
            weight: Trọng số (1.0 = từ title, 0.7 = từ body)
            
        Returns:
            List of keyword dicts
        """
        keywords = []
        
        # Tách thành các câu
        sentences = re.split(r'[.!?。！？]\s+', text)
        
        for sentence in sentences:
            if not sentence or len(sentence) < 5:
                continue
            
            # Trích các cụm từ quan trọng (2-4 từ)
            words = re.findall(r'\b[A-Za-zÀ-ỹ]{2,}\b', sentence)
            
            # Tạo các cụm từ
            phrases = []
            for i in range(len(words)):
                # 2-word phrases
                if i < len(words) - 1:
                    phrase = f"{words[i]} {words[i+1]}"
                    phrases.append(phrase)
                # 3-word phrases
                if i < len(words) - 2:
                    phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
                    phrases.append(phrase)
                # 4-word phrases (ít quan trọng hơn)
                if i < len(words) - 3 and i < 5:  # Chỉ lấy 5 đầu tiên
                    phrase = f"{words[i]} {words[i+1]} {words[i+2]} {words[i+3]}"
                    phrases.append(phrase)
            
            # Thêm vào keywords với score
            for phrase in phrases:
                if len(phrase) > 5:  # Ít nhất 5 ký tự
                    keywords.append({
                        "keyword": phrase.strip(),
                        "score": 0.8 * weight  # Score mặc định
                    })
        
        return keywords
    
    def _filter_stopwords(self, keywords: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Loại bỏ keywords chứa stopwords
        
        Args:
            keywords: List of keyword dicts
            
        Returns:
            Filtered list
        """
        filtered = []
        
        for kw_dict in keywords:
            keyword = kw_dict['keyword'].lower()
            words = keyword.split()
            
            # Bỏ qua nếu tất cả từ đều là stopwords
            if all(word in STOPWORDS_EN or word in STOPWORDS_VN for word in words):
                continue
            
            # Bỏ qua nếu chỉ có 1 từ và là stopword
            if len(words) == 1 and (words[0] in STOPWORDS_EN or words[0] in STOPWORDS_VN):
                continue
            
            filtered.append(kw_dict)
        
        return filtered
    
    def _deduplicate_keywords(self, keywords: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Loại bỏ duplicate keywords và merge scores
        
        Args:
            keywords: List of keyword dicts
            
        Returns:
            Deduplicated list
        """
        seen = {}
        
        for kw_dict in keywords:
            keyword = kw_dict['keyword'].lower().strip()
            score = kw_dict['score']
            
            if keyword in seen:
                # Merge scores (lấy max)
                seen[keyword]['score'] = max(seen[keyword]['score'], score)
            else:
                # Lưu keyword gốc (với chữ hoa/thường đúng)
                seen[keyword] = {
                    "keyword": kw_dict['keyword'].strip(),
                    "score": score
                }
        
        return list(seen.values())
    
    def find_authority_terms(self, keyword: str, source: str = 'ALL') -> List[Dict[str, Any]]:
        """
        Tìm authority terms cho một keyword
        
        Args:
            keyword: Keyword cần tìm authority
            source: 'MESH' | 'LCSH' | 'LCC' | 'NLM' | 'ALL'
            
        Returns:
            List of dict:
            [
                {
                    "id": <mã authority>,
                    "term": <tên chuẩn>,
                    "score": <float 0-1>,
                    "source": <nguồn>
                },
                ...
            ]
        """
        if not self.authority_tools:
            logger.warning("AuthorityTools không khả dụng")
            return []
        
        try:
            result = self.authority_tools.search_authority_terms(keyword, source)
            
            if not result.get('success'):
                logger.warning(f"Không tìm thấy authority terms cho '{keyword}': {result.get('error')}")
                return []
            
            # Format kết quả
            authority_terms = []
            for item in result.get('results', []):
                authority_terms.append({
                    "id": item.get('authority_id', ''),
                    "term": item.get('term', item.get('descriptor_name', keyword)),
                    "score": item.get('score', 0.0) / 100.0 if item.get('score', 0) > 1 else item.get('score', 0.0),
                    "source": item.get('source', 'UNKNOWN')
                })
            
            return authority_terms
            
        except Exception as e:
            logger.error(f"Lỗi khi tìm authority terms cho '{keyword}': {e}")
            return []
    
    def map_keyword_to_authorities(
        self, 
        keywords: List[Dict[str, Any]], 
        subject_type: str = 'general'
    ) -> Dict[str, Any]:
        """
        Map danh sách keywords sang authority terms và classification
        
        Args:
            keywords: List of keyword dicts (từ extract_keywords)
            subject_type: 'medical' | 'general' | 'science'
            
        Returns:
            Dict:
            {
                "subjects": [...],      # Dữ liệu để build 650
                "classification": {...} # LCC / NLM / DDC nếu có
            }
        
        Rule:
        - Nếu tài liệu y khoa → ưu tiên MeSH + NLM
        - Nếu tài liệu chung → ưu tiên LCSH + LCC
        """
        if not self.authority_tools:
            logger.warning("AuthorityTools không khả dụng, trả về keywords thô")
            return {
                "subjects": [],
                "classification": {}
            }
        
        try:
            # Lấy danh sách keywords dạng string
            keyword_strings = [kw['keyword'] for kw in keywords]
            
            # Gọi authority service để map
            result = self.authority_tools.get_classification_and_keywords(
                keywords=keyword_strings,
                subject_type=subject_type
            )
            
            if not result.get('success'):
                logger.warning(f"Không thể map keywords: {result.get('error')}")
                return {
                    "subjects": [],
                    "classification": {}
                }
            
            # Format kết quả
            output = result.get('output', {})
            classification_framework = output.get('classification_framework', [])
            controlled_keywords = output.get('controlled_keywords', [])
            
            # Build subjects (cho MARC 650)
            subjects = []
            for ck in controlled_keywords:
                subject = {
                    "raw": ck.get('keyword', ''),
                    "heading": ck.get('keyword', ''),  # Có thể cải thiện sau
                    "source": ck.get('vocabulary', 'UNCONTROLLED'),
                    "confidence": ck.get('confidence', 0.0) / 100.0 if ck.get('confidence', 0) > 1 else ck.get('confidence', 0.0),
                    "marc_650": {
                        "ind1": " ",
                        "ind2": "0" if ck.get('vocabulary') == 'LCSH' else "2" if ck.get('vocabulary') == 'MESH' else "4",
                        "subfields": [
                            {"code": "a", "value": ck.get('keyword', '')}
                        ]
                    }
                }
                subjects.append(subject)
            
            # Build classification (cho MARC 050/060)
            classification = {}
            for cf in classification_framework:
                framework = cf.get('framework', '')
                if framework == 'LCC':
                    classification['lcc'] = cf.get('classification_number', '')
                elif framework == 'NLM':
                    classification['nlm'] = cf.get('classification_number', '')
            
            logger.info(f"Mapped {len(keywords)} keywords -> {len(subjects)} subjects, {len(classification)} classifications")
            
            return {
                "subjects": subjects,
                "classification": classification
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi map keywords sang authorities: {e}")
            return {
                "subjects": [],
                "classification": {}
            }


# Example usage
if __name__ == "__main__":
    extractor = KeywordExtractor()
    
    # Test case
    ocr_text = """
    GS. Trần Hồng Quân với sự nghiệp giáo dục đào tạo Việt Nam
    Trần Xuân Nhĩ biên soạn
    
    Cuốn sách này nói về lịch sử giáo dục đại học tại Việt Nam.
    Tác giả tập trung vào vai trò của giáo sư Trần Hồng Quân trong việc
    phát triển hệ thống giáo dục và đào tạo.
    """
    
    title = "GS. Trần Hồng Quân với sự nghiệp giáo dục đào tạo Việt Nam"
    
    print("="*80)
    print("AGENT 4: KEYWORDS EXTRACTOR - TEST RESULTS")
    print("="*80)
    
    # Extract keywords
    keywords = extractor.extract_keywords(ocr_text, title)
    print(f"\nExtracted {len(keywords)} keywords:")
    for kw in keywords[:5]:
        print(f"  - {kw['keyword']} (score: {kw['score']:.2f})")
    
    # Map to authorities (nếu có authority service)
    if extractor.authority_tools:
        print("\nMapping to authorities...")
        mapping_result = extractor.map_keyword_to_authorities(keywords, subject_type='general')
        print(f"Subjects: {len(mapping_result['subjects'])}")
        print(f"Classification: {mapping_result['classification']}")


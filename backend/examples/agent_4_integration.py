"""
Agent 4 Integration Example
Demonstrates how Agent 4 (Keywords Extractor) integrates with Authority Control Service
"""
import requests
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Agent4KeywordsProcessor:
    """
    Agent 4: Keywords Extractor and Authority Mapper
    
    Workflow:
    1. Extract keywords from OCR text (AI/NLP logic)
    2. Standardize keywords using Authority Control Service
    3. Generate MARC21 650 fields
    4. Return structured output for MARC record
    """
    
    def __init__(self, authority_service_url="http://localhost:5000"):
        self.authority_url = authority_service_url
        self.api_endpoint = f"{authority_service_url}/api/authority"
        
    def extract_keywords(self, ocr_text: str, document_type: str = "general") -> List[str]:
        """
        Step 1: Extract keywords from OCR text
        
        Note: Đây là placeholder. Trong thực tế, bạn sẽ dùng:
        - AI model (GPT, Claude, etc.) để extract keywords
        - NLP libraries (spaCy, NLTK) để extract key phrases
        - TF-IDF hoặc KeyBERT để extract important terms
        
        Args:
            ocr_text: Raw OCR text from document
            document_type: Type of document (medical, science, general)
            
        Returns:
            List of extracted keywords
        """
        # TODO: Replace với AI/NLP logic thật
        # Example: Use AI model prompt
        """
        prompt = f'''
        Extract key subject terms from this document text.
        Focus on main topics, concepts, and important terms.
        
        Document type: {document_type}
        
        Text:
        {ocr_text}
        
        Return as JSON array of keywords.
        '''
        keywords = call_ai_model(prompt)
        """
        
        # Placeholder: Extract simple keywords
        logger.info("Extracting keywords from OCR text...")
        
        # Simulated extraction (replace with real AI logic)
        if "diabetes" in ocr_text.lower():
            keywords = ["diabetes mellitus", "insulin", "glucose metabolism", "treatment"]
        elif "machine learning" in ocr_text.lower():
            keywords = ["machine learning", "artificial intelligence", "neural networks"]
        else:
            # Simple extraction (not production-ready)
            words = ocr_text.split()
            keywords = [w for w in words if len(w) > 5][:5]
        
        logger.info(f"Extracted {len(keywords)} keywords: {keywords}")
        return keywords
    
    def standardize_keywords(
        self, 
        keywords: List[str], 
        subject_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Step 2: Standardize keywords using Authority Control Service
        
        Maps extracted keywords to controlled vocabulary terms from:
        - MESH (Medical Subject Headings)
        - LCSH (Library of Congress Subject Headings)
        - LCC (Library of Congress Classification)
        - NLM (National Library of Medicine)
        
        Args:
            keywords: List of extracted keywords
            subject_type: Document subject type (medical, science, general)
            
        Returns:
            Standardization result with authority terms and MARC fields
        """
        logger.info(f"Standardizing {len(keywords)} keywords...")
        
        try:
            response = requests.post(
                f"{self.api_endpoint}/map",
                json={
                    "keywords": keywords,
                    "subject_type": subject_type
                },
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(f"Standardization complete:")
            logger.info(f"  - Valid terms: {result['statistics']['valid_terms']}")
            logger.info(f"  - Cache hits: {result['statistics']['cache_hits']}")
            logger.info(f"  - API calls: {result['statistics']['api_calls']}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Authority service error: {e}")
            # Fallback: Return original keywords
            return self._create_fallback_result(keywords)
    
    def _create_fallback_result(self, keywords: List[str]) -> Dict[str, Any]:
        """Create fallback result when authority service fails"""
        return {
            "mapping_results": [
                {
                    "original_keyword": kw,
                    "term": kw,
                    "source": "ORIGINAL",
                    "is_valid": False,
                    "confidence": 0.5
                }
                for kw in keywords
            ],
            "marc21_fields": [
                f"650 _4 $a {kw}"  # _4 = Source not specified
                for kw in keywords
            ],
            "statistics": {
                "valid_terms": 0,
                "cache_hits": 0,
                "api_calls": 0,
                "fallback": True
            }
        }
    
    def generate_marc21_output(self, authority_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 3: Generate MARC21 output structure
        
        Converts authority mapping results into MARC21 fields format
        
        Args:
            authority_result: Result from standardize_keywords()
            
        Returns:
            MARC21 fields structure ready for integration
        """
        logger.info("Generating MARC21 output...")
        
        # Extract validated authority terms
        authority_terms = [
            {
                "term": item["term"],
                "source": item["source"],
                "confidence": item["confidence"],
                "mesh_id": item.get("mesh_id"),
                "lccn": item.get("lccn")
            }
            for item in authority_result["mapping_results"]
            if item["is_valid"]
        ]
        
        # MARC21 650 fields
        marc_650_fields = authority_result["marc21_fields"]
        
        # Additional metadata
        metadata = {
            "total_keywords": len(authority_result["mapping_results"]),
            "validated_terms": len(authority_terms),
            "validation_rate": (
                len(authority_terms) / len(authority_result["mapping_results"]) * 100
                if authority_result["mapping_results"] else 0
            ),
            "cache_hit_rate": authority_result["statistics"].get("cache_hit_rate", 0),
            "processing_time": authority_result["statistics"].get("processing_time", 0)
        }
        
        return {
            "authority_terms": authority_terms,
            "marc21_650_fields": marc_650_fields,
            "metadata": metadata
        }
    
    def process_document(
        self, 
        ocr_text: str, 
        document_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Complete Agent 4 Workflow
        
        Full pipeline: OCR Text → Keywords → Authorities → MARC21
        
        Args:
            ocr_text: Raw OCR text from document
            document_type: Type of document (medical, science, general)
            
        Returns:
            Complete processing result with MARC21 fields
        """
        logger.info("="*80)
        logger.info("Agent 4: Keywords Processing Pipeline")
        logger.info("="*80)
        
        # Step 1: Extract keywords
        logger.info("\n[Step 1/3] Extracting keywords...")
        keywords = self.extract_keywords(ocr_text, document_type)
        
        # Step 2: Standardize with authority control
        logger.info("\n[Step 2/3] Standardizing with authority control...")
        authority_result = self.standardize_keywords(keywords, document_type)
        
        # Step 3: Generate MARC21 output
        logger.info("\n[Step 3/3] Generating MARC21 output...")
        marc_output = self.generate_marc21_output(authority_result)
        
        # Complete result
        result = {
            "original_keywords": keywords,
            "authority_terms": marc_output["authority_terms"],
            "marc21_650_fields": marc_output["marc21_650_fields"],
            "metadata": marc_output["metadata"]
        }
        
        logger.info("\n" + "="*80)
        logger.info("Pipeline Complete!")
        logger.info(f"  Keywords Extracted: {len(keywords)}")
        logger.info(f"  Authority Terms: {len(marc_output['authority_terms'])}")
        logger.info(f"  MARC Fields: {len(marc_output['marc21_650_fields'])}")
        logger.info(f"  Validation Rate: {marc_output['metadata']['validation_rate']:.1f}%")
        logger.info("="*80 + "\n")
        
        return result


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_medical_document():
    """Example 1: Process Medical Document"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Medical Document Processing")
    print("="*80)
    
    ocr_text = """
    Clinical Guidelines for Diabetes Mellitus Management
    
    Diabetes mellitus is a chronic metabolic disorder characterized by 
    hyperglycemia. Treatment involves insulin therapy, glucose monitoring,
    and lifestyle modifications. Complications include cardiovascular disease
    and nephropathy.
    
    Keywords: diabetes, insulin resistance, glucose metabolism, cardiovascular
    """
    
    agent = Agent4KeywordsProcessor()
    result = agent.process_document(ocr_text, document_type="medical")
    
    print("\n📊 RESULTS:")
    print(f"\n   Original Keywords: {result['original_keywords']}")
    print(f"\n   Authority Terms:")
    for term in result['authority_terms']:
        print(f"      - {term['term']} ({term['source']}) [confidence: {term['confidence']:.2f}]")
    
    print(f"\n   MARC21 650 Fields:")
    for field in result['marc21_650_fields']:
        print(f"      {field}")
    
    print(f"\n   Metadata:")
    print(f"      Validation Rate: {result['metadata']['validation_rate']:.1f}%")
    print(f"      Cache Hit Rate: {result['metadata']['cache_hit_rate']:.1f}%")


def example_computer_science_document():
    """Example 2: Process Computer Science Document"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Computer Science Document Processing")
    print("="*80)
    
    ocr_text = """
    Introduction to Machine Learning and Neural Networks
    
    Machine learning is a subset of artificial intelligence focused on
    algorithms that learn from data. Deep learning uses neural networks
    with multiple layers. Applications include computer vision and
    natural language processing.
    """
    
    agent = Agent4KeywordsProcessor()
    result = agent.process_document(ocr_text, document_type="science")
    
    print("\n📊 RESULTS:")
    print(f"\n   Original Keywords: {result['original_keywords']}")
    print(f"\n   MARC21 650 Fields:")
    for field in result['marc21_650_fields'][:3]:
        print(f"      {field}")


def example_batch_processing():
    """Example 3: Batch Process Multiple Documents"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Batch Processing Multiple Documents")
    print("="*80)
    
    documents = [
        ("Medical doc", "diabetes treatment guidelines", "medical"),
        ("CS doc", "machine learning algorithms", "science"),
        ("General doc", "history of ancient rome", "general")
    ]
    
    agent = Agent4KeywordsProcessor()
    
    for name, text, doc_type in documents:
        print(f"\n📄 Processing: {name}")
        result = agent.process_document(text, doc_type)
        print(f"   ✅ Generated {len(result['marc21_650_fields'])} MARC fields")


def example_integration_with_other_agents():
    """Example 4: Integration with Other Agents"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Multi-Agent Integration")
    print("="*80)
    
    # Simulated outputs from other agents
    agent_1_output = {
        "title": "Clinical Guidelines for Diabetes Management",
        "authors": ["John Smith", "Mary Johnson"]
    }
    
    agent_2_output = {
        "isbn": "978-0-123456-78-9",
        "year": 2023,
        "publisher": "Medical Press"
    }
    
    agent_3_output = {
        "document_type": "medical guideline",
        "language": "English"
    }
    
    # Agent 4: Keywords and subjects
    ocr_text = "diabetes mellitus insulin therapy glucose monitoring"
    agent_4 = Agent4KeywordsProcessor()
    agent_4_output = agent_4.process_document(ocr_text, "medical")
    
    # Combine all outputs into complete MARC record
    complete_marc = {
        "245": f"$a {agent_1_output['title']}",
        "100": f"$a {agent_1_output['authors'][0]}",
        "020": f"$a {agent_2_output['isbn']}",
        "260": f"$c {agent_2_output['year']}",
        "650": agent_4_output['marc21_650_fields']  # From Agent 4
    }
    
    print("\n📚 Complete MARC21 Record:")
    for tag, value in complete_marc.items():
        if isinstance(value, list):
            for field in value:
                print(f"   {field}")
        else:
            print(f"   {tag} {value}")


def main():
    """Main runner"""
    print("\n" + "="*80)
    print("🤖 AGENT 4 - KEYWORDS PROCESSOR EXAMPLES")
    print("="*80)
    
    print("\nNote: Đảm bảo Authority Service đang chạy tại http://localhost:5000")
    input("Press Enter để tiếp tục...")
    
    # Run examples
    example_medical_document()
    example_computer_science_document()
    example_batch_processing()
    example_integration_with_other_agents()
    
    print("\n" + "="*80)
    print("✅ All examples completed!")
    print("="*80)
    print("\n💡 Next Steps:")
    print("   1. Replace extract_keywords() với AI model thật")
    print("   2. Integrate với Agent 1, 2, 3, 5")
    print("   3. Add error handling và retry logic")
    print("   4. Implement caching ở agent level")
    print("   5. Add monitoring và logging")


if __name__ == "__main__":
    main()

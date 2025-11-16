"""
Comprehensive Demo: All 5 OCR Extraction Agents + MARC21 Integration
Test các agent với nhiều loại tài liệu khác nhau
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent / 'backend' / 'services' / 'agents'))

from marc_integration import MARCIntegration


def test_all_document_types():
    """
    Test integration with different document types
    """
    integration = MARCIntegration()
    
    # Test cases
    test_cases = [
        {
            'name': 'Medical Textbook',
            'ocr_text': """
            Introduction to Clinical Medicine
            Third Edition
            
            By Dr. John Smith, MD, PhD
            Co-author: Dr. Jane Doe, MD
            
            ISBN: 978-0-123-45678-9
            
            Published by Medical Press
            Copyright © 2024
            
            Chapter 1: Introduction to Medicine
            Chapter 2: Patient Assessment
            Chapter 3: Diagnostic Methods
            
            Exercises at the end of each chapter
            """,
            'keywords': ['Clinical Medicine', 'Medical Education', 'Patient Care'],
            'frameworks': [
                {'type': 'LCC', 'number': 'R729'},
                {'type': 'NLM', 'number': 'W 18'}
            ]
        },
        {
            'name': 'Journal Article',
            'ocr_text': """
            Advanced Machine Learning Techniques for Medical Diagnosis
            
            Authors: John Smith; Mary Johnson; Peter Brown
            
            Journal of Medical Informatics
            Vol. 45, No. 3, July 2024
            ISSN: 1234-5678
            
            Abstract: This paper presents...
            """,
            'keywords': ['Machine Learning', 'Medical Informatics', 'Artificial Intelligence'],
            'frameworks': [
                {'type': 'LCC', 'number': 'R858'},
                {'type': 'NLM', 'number': 'W 26.5'}
            ]
        },
        {
            'name': 'Conference Proceeding',
            'ocr_text': """
            Proceedings of the 15th International Conference on Machine Learning in Healthcare
            
            Edited by Prof. John Smith and Prof. Mary Johnson
            
            June 15-17, 2024
            San Francisco, USA
            
            ISBN: 978-1-234-56789-0
            © 2024 IEEE Computer Society
            """,
            'keywords': ['Machine Learning', 'Healthcare', 'Conference Proceedings'],
            'frameworks': [
                {'type': 'LCC', 'number': 'R858.A2'},
                {'type': 'NLM', 'number': 'W 26.5'}
            ]
        },
        {
            'name': 'Vietnamese Textbook',
            'ocr_text': """
            Hướng dẫn điều trị bệnh tiểu đường
            
            Tác giả: PGS.TS. Nguyễn Văn An
            Đồng tác giả: TS. Trần Thị Bình
            
            ISBN: 978-604-0-12345-6-7
            Nhà xuất bản Y học
            Năm xuất bản: 2024
            
            Chương 1: Tổng quan về bệnh tiểu đường
            Chương 2: Chẩn đoán
            Chương 3: Điều trị
            
            Bài tập cuối mỗi chương
            """,
            'keywords': ['Diabetes Mellitus', 'Treatment', 'Clinical Practice'],
            'frameworks': [
                {'type': 'LCC', 'number': 'RC660'},
                {'type': 'NLM', 'number': 'WK 810'}
            ]
        },
        {
            'name': 'PhD Thesis',
            'ocr_text': """
            Machine Learning Approaches for Early Detection of Diabetes
            
            A Dissertation Presented to the Faculty of Computer Science
            In Partial Fulfillment of the Requirements for the Degree of 
            Doctor of Philosophy
            
            By Jane Smith
            Supervisor: Prof. John Doe, Ph.D.
            
            University of Medicine
            © 2024
            """,
            'keywords': ['Machine Learning', 'Diabetes', 'Early Detection'],
            'frameworks': [
                {'type': 'LCC', 'number': 'QA76.9.M3'},
                {'type': 'NLM', 'number': 'WK 810'}
            ]
        }
    ]
    
    # Run tests
    print("="*100)
    print("COMPREHENSIVE DEMO: 5 OCR EXTRACTION AGENTS + MARC21 INTEGRATION")
    print("="*100)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\n{'='*100}")
        print(f"TEST CASE {i}: {test_case['name']}")
        print(f"{'='*100}")
        
        # Generate MARC21 record
        marc_record = integration.agents_output_to_marc21(
            ocr_text=test_case['ocr_text'],
            keywords=test_case['keywords'],
            classification_frameworks=test_case['frameworks']
        )
        
        # Display formatted result
        print(integration.format_marc_display(marc_record))
    
    print(f"\n\n{'='*100}")
    print("ALL TESTS COMPLETED")
    print("="*100)


def test_individual_agents():
    """
    Test each agent individually
    """
    from agent_1_title import TitleExtractor
    from agent_2_author import AuthorExtractor
    from agent_3_isbn_year import ISBNYearExtractor
    from agent_5_doctype import DocumentTypeClassifier
    
    ocr_text = """
    Introduction to Clinical Medicine
    Third Edition
    
    By Dr. John Smith, MD, PhD
    Co-author: Dr. Jane Doe, MD
    
    ISBN: 978-0-123-45678-9
    Published by Medical Press
    Copyright © 2024
    
    Chapter 1: Introduction
    Exercises included
    """
    
    print("="*100)
    print("INDIVIDUAL AGENT TESTS")
    print("="*100)
    
    # Agent 1: Title
    print("\n--- AGENT 1: TITLE EXTRACTOR ---")
    title_ext = TitleExtractor()
    title = title_ext.extract_title(ocr_text)
    title_with_sub = title_ext.extract_title_with_subtitle(ocr_text)
    print(f"Title: {title}")
    print(f"Title with subtitle: {title_with_sub}")
    
    # Agent 2: Authors
    print("\n--- AGENT 2: AUTHOR EXTRACTOR ---")
    author_ext = AuthorExtractor()
    authors = author_ext.extract_authors(ocr_text)
    print(f"Authors ({len(authors)}):")
    for i, author in enumerate(authors, 1):
        print(f"  {i}. {author}")
    
    # Agent 3: ISBN & Year
    print("\n--- AGENT 3: ISBN & YEAR EXTRACTOR ---")
    isbn_ext = ISBNYearExtractor()
    isbn, year = isbn_ext.extract_both(ocr_text)
    print(f"ISBN: {isbn}")
    print(f"Year: {year}")
    
    # Agent 5: Document Type
    print("\n--- AGENT 5: DOCUMENT TYPE CLASSIFIER ---")
    doctype_cls = DocumentTypeClassifier()
    metadata = {
        'has_isbn': isbn is not None,
        'has_chapters': 'chapter' in ocr_text.lower(),
        'has_exercises': 'exercise' in ocr_text.lower(),
    }
    doc_type = doctype_cls.classify_document_type(ocr_text, metadata)
    details = doctype_cls.classify_with_details(ocr_text, metadata)
    marc_code = doctype_cls.get_marc_leader_code(doc_type)
    print(f"Document Type: {doc_type}")
    print(f"Confidence: {details['confidence']:.2f}")
    print(f"MARC Leader Type: {marc_code}")
    print(f"All Scores: {details['scores']}")
    
    print("\n" + "="*100)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Demo OCR Extraction Agents')
    parser.add_argument('--mode', choices=['all', 'individual', 'integration'], 
                       default='all', help='Test mode')
    args = parser.parse_args()
    
    if args.mode == 'all' or args.mode == 'individual':
        test_individual_agents()
    
    if args.mode == 'all' or args.mode == 'integration':
        print("\n\n")
        test_all_document_types()

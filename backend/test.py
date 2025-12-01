import sys
import os
from pathlib import Path
from urllib.parse import urlparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.image_processor import ImageProcessor
from app.services.pdf_processor import PDFProcessor
import logging
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_file_from_url(url: str, base_name: str = "temp_downloaded"):
    """
    Tải file (ảnh hoặc PDF) từ URL và lưu tạm.
    Trả về đường dẫn file đã lưu hoặc None nếu lỗi.
    """
    try:
        parsed = urlparse(url)
        ext = Path(parsed.path).suffix.lower()

        # Nếu URL không có extension rõ ràng thì default là .jpg
        if not ext:
            ext = ".jpg"

        save_path = f"{base_name}{ext}"

        print(f"⬇️ Đang tải file từ URL: {url}")
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()

        with open(save_path, "wb") as f:
            f.write(resp.content)

        print(f"✅ Đã tải xong → lưu tại: {save_path}")
        return save_path
    except Exception as e:
        print(f"❌ Không tải được file từ URL: {url}")
        print(f"Lỗi: {e}")
        return None


def test_image_ocr(image_path: str):
    """Test OCR trên 1 ảnh"""
    print(f"\n{'='*60}")
    print(f"Testing OCR on: {image_path}")
    print(f"{'='*60}\n")
    
    if not os.path.exists(image_path):
        print(f"❌ File không tồn tại: {image_path}")
        return
    
    # Khởi tạo processor
    processor = ImageProcessor()
    
    try:
        # Process image
        print("⏳ Processing image...")
        result = processor.process_image(image_path)
        
        # Print results
        print(f"\n{'='*60}")
        print("📊 KẾT QUẢ OCR")
        print(f"{'='*60}")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Image ID: {result.get('image_id', 'N/A')}")
        print(f"Confidence: {result.get('confidence', 0):.2%}")
        print(f"Processing Time: {result.get('processing_time_ms', 0):.2f}ms")
        
        if result.get('error'):
            print(f"\n❌ Error: {result['error']}")
        
        if result.get('ocr_text'):
            print(f"\n{'='*60}")
            print("📝 EXTRACTED TEXT:")
            print(f"{'='*60}")
            print(result['ocr_text'])
            print(f"{'='*60}\n")
        else:
            print("\n⚠️ No text extracted\n")
            
    except Exception as e:
        print(f"\n❌ Error processing image: {e}")
        import traceback
        traceback.print_exc()


def test_pdf_ocr(pdf_path: str):
    """Test OCR trên PDF"""
    print(f"\n{'='*60}")
    print(f"Testing OCR on PDF: {pdf_path}")
    print(f"{'='*60}\n")
    
    if not os.path.exists(pdf_path):
        print(f"❌ File không tồn tại: {pdf_path}")
        return
    
    # Khởi tạo processor
    processor = PDFProcessor()
    
    try:
        # Process PDF
        print("⏳ Processing PDF...")
        result = processor.process_pdf(pdf_path)
        
        # Print results
        print(f"\n{'='*60}")
        print("📊 KẾT QUẢ OCR PDF")
        print(f"{'='*60}")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Total Pages: {result.get('total_pages', 0)}")
        print(f"Average Confidence: {result.get('avg_confidence', 0):.2%}")
        print(f"Processing Time: {result.get('processing_time_ms', 0):.2f}ms")
        
        if result.get('error'):
            print(f"\n❌ Error: {result['error']}")
        
        if result.get('pages'):
            for page in result['pages']:
                print(f"\n{'='*60}")
                print(f"📄 PAGE {page['page_number']}")
                print(f"{'='*60}")
                print(f"Confidence: {page.get('confidence', 0):.2%}")
                print(f"Lines: {page.get('lines_detected', 0)}")
                if page.get('text'):
                    print("\nText:")
                    text = page['text']
                    print(text[:500] + "..." if len(text) > 500 else text)
        else:
            print("\n⚠️ No pages extracted\n")
            
    except Exception as e:
        print(f"\n❌ Error processing PDF: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("\n❌ Usage: python test_ocr_direct.py <path_or_url_to_image_or_pdf>")
        print("\nExamples:")
        print("  python test_ocr_direct.py image.jpg")
        print("  python test_ocr_direct.py document.pdf")
        print("  python test_ocr_direct.py C:/path/to/file.png")
        print("  python test_ocr_direct.py https://example.com/image.png")
        print("  python test_ocr_direct.py https://example.com/file.pdf")
        sys.exit(1)
    
    arg = sys.argv[1]

    # Nếu là URL
    if arg.startswith("http://") or arg.startswith("https://"):
        downloaded_path = download_file_from_url(arg)
        if not downloaded_path:
            sys.exit(1)
        file_path = downloaded_path
    else:
        file_path = arg
    
    # Kiểm tra file extension
    ext = Path(file_path).suffix.lower()
    
    if ext == '.pdf':
        test_pdf_ocr(file_path)
    elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
        test_image_ocr(file_path)
    else:
        print(f"❌ Unsupported file type: {ext}")
        print("Supported: .jpg, .jpeg, .png, .bmp, .tiff, .tif, .pdf")
        sys.exit(1)


if __name__ == "__main__":
    main()

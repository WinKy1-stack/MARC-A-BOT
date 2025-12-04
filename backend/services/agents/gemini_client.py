"""
Gemini AI Client Helper
Helper để khởi tạo và sử dụng Gemini AI client
"""
import logging
from typing import Optional, Any
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from services.agents.config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

# Global Gemini client instance
_gemini_client = None
_gemini_model = None


def get_gemini_client() -> Optional[Any]:
    """
    Lấy Gemini client instance (lazy initialization)
    
    Returns:
        Gemini GenerativeModel instance hoặc None nếu không có API key
    """
    global _gemini_client, _gemini_model
    
    if not GEMINI_API_KEY or GEMINI_API_KEY == 'your-gemini-api-key-here':
        logger.warning("GEMINI_API_KEY không được cấu hình. Gemini AI sẽ không khả dụng.")
        return None
    
    if _gemini_client is None:
        try:
            import google.generativeai as genai
            
            # Cấu hình API key
            genai.configure(api_key=GEMINI_API_KEY)
            
            # Tạo model
            _gemini_model = genai.GenerativeModel(GEMINI_MODEL)
            _gemini_client = genai
            
            logger.info(f"Đã khởi tạo Gemini client với model: {GEMINI_MODEL}")
            
        except ImportError:
            logger.error(
                "Thư viện google-generativeai chưa được cài đặt. "
                "Cài đặt bằng: pip install google-generativeai"
            )
            return None
        except Exception as e:
            logger.error(f"Lỗi khi khởi tạo Gemini client: {e}")
            return None
    
    return _gemini_model


def is_gemini_available() -> bool:
    """
    Kiểm tra Gemini có khả dụng không
    
    Returns:
        True nếu Gemini có thể sử dụng
    """
    return get_gemini_client() is not None


def generate_with_gemini(prompt: str, tools: Optional[list] = None) -> Optional[Any]:
    """
    Gọi Gemini để generate content
    
    Args:
        prompt: Prompt text
        tools: Optional list of tools (function calling)
        
    Returns:
        Response từ Gemini hoặc None nếu lỗi
    """
    model = get_gemini_client()
    if not model:
        return None
    
    try:
        kwargs = {"contents": prompt}
        if tools:
            kwargs["tools"] = tools
        
        response = model.generate_content(**kwargs)
        return response
        
    except Exception as e:
        logger.error(f"Lỗi khi gọi Gemini: {e}")
        return None


# Example usage
if __name__ == "__main__":
    # Test Gemini connection
    print("Testing Gemini connection...")
    
    if is_gemini_available():
        print(f"✅ Gemini available with model: {GEMINI_MODEL}")
        
        # Test simple generation
        response = generate_with_gemini("Hello, say hi in Vietnamese")
        if response:
            print(f"Response: {response.text}")
    else:
        print("❌ Gemini not available. Check GEMINI_API_KEY in config.")


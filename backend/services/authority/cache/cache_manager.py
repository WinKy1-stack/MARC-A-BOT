"""
Cache Manager cho Authority Terms
Sử dụng SQLite để cache local và tối ưu tra cứu
"""
import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from rapidfuzz import fuzz, process

logger = logging.getLogger(__name__)


class AuthorityCacheManager:
    """Quản lý cache cho authority terms"""
    
    def __init__(self, db_path: str):
        """
        Initialize cache manager
        
        Args:
            db_path: Đường dẫn đến SQLite database
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
    def _init_database(self):
        """Khởi tạo database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Authority Terms Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authority_terms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL,
                authority_id TEXT NOT NULL,
                normalized_term TEXT NOT NULL,
                source TEXT NOT NULL,
                category TEXT,
                score REAL DEFAULT 100.0,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for fast lookup
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_keyword 
            ON authority_terms(keyword COLLATE NOCASE)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_authority_id 
            ON authority_terms(authority_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_source 
            ON authority_terms(source)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_keyword_source 
            ON authority_terms(keyword COLLATE NOCASE, source)
        ''')
        
        # Cache Statistics Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_keyword TEXT NOT NULL,
                source TEXT,
                cache_hit BOOLEAN,
                match_type TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
        
    def add_term(self, keyword: str, authority_id: str, normalized_term: str, 
                 source: str, category: str = None, score: float = 100.0, 
                 metadata: Dict = None) -> bool:
        """
        Thêm authority term vào cache
        
        Args:
            keyword: Từ khóa gốc
            authority_id: ID từ authority source
            normalized_term: Thuật ngữ chuẩn hóa
            source: Nguồn (MESH, LCSH, LCC, NLM)
            category: Phân loại (medical, general, science, etc.)
            score: Confidence score (0-100)
            metadata: Metadata bổ sung (JSON)
            
        Returns:
            True nếu thêm thành công
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute('''
                INSERT INTO authority_terms 
                (keyword, authority_id, normalized_term, source, category, score, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (keyword.lower(), authority_id, normalized_term, source, 
                  category, score, metadata_json))
            
            conn.commit()
            conn.close()
            logger.debug(f"Added term: {keyword} -> {authority_id} ({source})")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error adding term to cache: {e}")
            return False
            
    def exact_match(self, keyword: str, source: str = None) -> List[Dict]:
        """
        Tìm exact match trong cache
        
        Args:
            keyword: Từ khóa cần tìm
            source: Nguồn cụ thể (optional)
            
        Returns:
            List of matching authority terms
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if source:
                cursor.execute('''
                    SELECT * FROM authority_terms 
                    WHERE LOWER(keyword) = ? AND source = ?
                    ORDER BY score DESC
                ''', (keyword.lower(), source))
            else:
                cursor.execute('''
                    SELECT * FROM authority_terms 
                    WHERE LOWER(keyword) = ?
                    ORDER BY score DESC
                ''', (keyword.lower(),))
            
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                results.append({
                    'keyword': row['keyword'],
                    'authority_id': row['authority_id'],
                    'normalized_term': row['normalized_term'],
                    'source': row['source'],
                    'category': row['category'],
                    'score': row['score'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                    'match_type': 'exact'
                })
                
            if results:
                self._log_cache_stat(keyword, source, cache_hit=True, match_type='exact')
            
            return results
            
        except sqlite3.Error as e:
            logger.error(f"Error in exact_match: {e}")
            return []
            
    def fuzzy_match(self, keyword: str, source: str = None, 
                    threshold: int = 80, limit: int = 10) -> List[Dict]:
        """
        Tìm fuzzy match trong cache
        
        Args:
            keyword: Từ khóa cần tìm
            source: Nguồn cụ thể (optional)
            threshold: Ngưỡng điểm tối thiểu (0-100)
            limit: Số kết quả tối đa
            
        Returns:
            List of matching authority terms với fuzzy score
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all keywords from cache for fuzzy matching
            if source:
                cursor.execute('''
                    SELECT DISTINCT keyword FROM authority_terms 
                    WHERE source = ?
                ''', (source,))
            else:
                cursor.execute('SELECT DISTINCT keyword FROM authority_terms')
            
            cached_keywords = [row['keyword'] for row in cursor.fetchall()]
            
            # Perform fuzzy matching
            matches = process.extract(
                keyword.lower(), 
                cached_keywords, 
                scorer=fuzz.WRatio,
                limit=limit,
                score_cutoff=threshold
            )
            
            results = []
            for matched_keyword, score, _ in matches:
                # Get full details for matched keyword
                cursor.execute('''
                    SELECT * FROM authority_terms 
                    WHERE LOWER(keyword) = ?
                ''', (matched_keyword,))
                
                row = cursor.fetchone()
                if row:
                    results.append({
                        'keyword': row['keyword'],
                        'authority_id': row['authority_id'],
                        'normalized_term': row['normalized_term'],
                        'source': row['source'],
                        'category': row['category'],
                        'score': score,  # Use fuzzy match score
                        'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                        'match_type': 'fuzzy',
                        'original_score': row['score']
                    })
            
            conn.close()
            
            if results:
                self._log_cache_stat(keyword, source, cache_hit=True, match_type='fuzzy')
            
            return results
            
        except Exception as e:
            logger.error(f"Error in fuzzy_match: {e}")
            return []
            
    def search(self, keyword: str, source: str = None, 
               fuzzy_threshold: int = 80, limit: int = 10) -> List[Dict]:
        """
        Tìm kiếm authority terms (exact first, then fuzzy)
        
        Args:
            keyword: Từ khóa cần tìm
            source: Nguồn cụ thể (optional)
            fuzzy_threshold: Ngưỡng cho fuzzy match
            limit: Số kết quả tối đa
            
        Returns:
            List of matching authority terms
        """
        # Try exact match first
        results = self.exact_match(keyword, source)
        
        # If no exact match, try fuzzy match
        if not results:
            results = self.fuzzy_match(keyword, source, fuzzy_threshold, limit)
            
        return results
        
    def get_cache_stats(self, days: int = 7) -> Dict:
        """
        Lấy thống kê cache performance
        
        Args:
            days: Số ngày để thống kê
            
        Returns:
            Dictionary chứa cache statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total cache entries
            cursor.execute('SELECT COUNT(*) FROM authority_terms')
            total_entries = cursor.fetchone()[0]
            
            # Cache stats for last N days
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_queries,
                    SUM(CASE WHEN cache_hit = 1 THEN 1 ELSE 0 END) as cache_hits,
                    SUM(CASE WHEN match_type = 'exact' THEN 1 ELSE 0 END) as exact_matches,
                    SUM(CASE WHEN match_type = 'fuzzy' THEN 1 ELSE 0 END) as fuzzy_matches
                FROM cache_stats
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            row = cursor.fetchone()
            total_queries = row[0] or 0
            cache_hits = row[1] or 0
            exact_matches = row[2] or 0
            fuzzy_matches = row[3] or 0
            
            hit_rate = (cache_hits / total_queries * 100) if total_queries > 0 else 0
            
            conn.close()
            
            return {
                'total_cache_entries': total_entries,
                'total_queries': total_queries,
                'cache_hits': cache_hits,
                'cache_misses': total_queries - cache_hits,
                'hit_rate': round(hit_rate, 2),
                'exact_matches': exact_matches,
                'fuzzy_matches': fuzzy_matches,
                'period_days': days
            }
            
        except sqlite3.Error as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
            
    def _log_cache_stat(self, keyword: str, source: str, 
                       cache_hit: bool, match_type: str):
        """Log cache statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO cache_stats (query_keyword, source, cache_hit, match_type)
                VALUES (?, ?, ?, ?)
            ''', (keyword, source, cache_hit, match_type))
            
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            logger.error(f"Error logging cache stat: {e}")
            
    def clear_cache(self):
        """Xóa toàn bộ cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM authority_terms')
            cursor.execute('DELETE FROM cache_stats')
            conn.commit()
            conn.close()
            logger.info("Cache cleared successfully")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error clearing cache: {e}")
            return False

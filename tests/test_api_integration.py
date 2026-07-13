import pytest
from unittest.mock import Mock, patch

def test_api_call_integration():
    """Test integration with external APIs"""
    
    # Test DuckDuckGo search
    with patch('ddgs.ddg') as mock_ddg:
        mock_ddg.return_value = [{"title": "Test", "href": "http://test.com"}]
        
        from src.api_handlers import search_duckduckgo
        results = search_duckduckgo("test query")
        
        assert len(results) > 0

def test_wikipedia_api():
    """Test Wikipedia API integration"""
    
    with patch('wikipedia.search') as mock_search:
        mock_search.return_value = ["Test Page"]
        
        from src.api_handlers import get_wikipedia_content
        content = get_wikipedia_content("Test Page")
        
        assert content is not None
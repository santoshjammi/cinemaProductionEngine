"""Research module — gathers web references and Wikipedia context before story generation.

All sources are free and open-source (no API keys required):
  - duckduckgo-search: anonymous web search
  - wikipedia: Wikipedia API
  - requests + BeautifulSoup: page crawling
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("pipeline.research")

# Heavy / optional imports — lazy-loaded so tests can mock them
_ddgs = None
_wikipedia = None


def _get_ddgs():
    """Lazy-load DuckDuckGo search client. Supports both ddgs and duckduckgo-search."""
    global _ddgs
    if _ddgs is None:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS
        _ddgs = DDGS()
    return _ddgs


def _get_wikipedia():
    """Lazy-load wikipedia library."""
    global _wikipedia
    if _wikipedia is None:
        import wikipedia
        _wikipedia = wikipedia
    return _wikipedia


@dataclass
class SearchResult:
    """A single web search result."""
    title: str
    url: str
    snippet: str


@dataclass
class CrawledPage:
    """A crawled web page with extracted text."""
    url: str
    title: str
    text: str
    error: Optional[str] = None


@dataclass
class ResearchContext:
    """Aggregated research context for story generation."""
    topic: str
    search_results: List[SearchResult] = field(default_factory=list)
    wikipedia_summary: str = ""
    wikipedia_url: str = ""
    crawled_pages: List[CrawledPage] = field(default_factory=list)
    combined_context: str = ""

    def to_prompt_context(self, max_chars: int = 4000) -> str:
        """Format the research as a context string for LLM prompts."""
        if not self.combined_context:
            self._build_combined_context()
        return self.combined_context[:max_chars]

    def _build_combined_context(self):
        """Build a single context string from all research sources."""
        parts = []

        if self.wikipedia_summary:
            parts.append(f"[Wikipedia Summary]\n{self.wikipedia_summary}")

        for i, page in enumerate(self.crawled_pages[:3], 1):
            if page.text and not page.error:
                parts.append(f"[Reference {i}: {page.title}]\n{page.text[:800]}")

        if self.search_results:
            snippets = "\n".join(
                f"- {r.title}: {r.snippet}" for r in self.search_results[:5]
            )
            parts.append(f"[Related Search Results]\n{snippets}")

        self.combined_context = "\n\n".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for YAML output (truncated to avoid recursion/size issues)."""
        return {
            "topic": self.topic,
            "wikipedia_summary": self.wikipedia_summary[:500] if self.wikipedia_summary else "",
            "wikipedia_url": self.wikipedia_url,
            "search_results": [
                {"title": r.title, "url": r.url, "snippet": r.snippet[:200] if r.snippet else ""}
                for r in self.search_results[:5]
            ],
            "crawled_pages": [
                {"url": p.url, "title": p.title, "text_preview": p.text[:300] if p.text else ""}
                for p in self.crawled_pages[:3]
            ],
        }


class WebSearcher:
    """Search the web using DuckDuckGo (free, no API key)."""

    def __init__(self, max_results: int = 8):
        self.max_results = max_results

    def search(self, query: str) -> List[SearchResult]:
        """Search DuckDuckGo and return results."""
        logger.info(f"[Research] Searching web for: '{query}'")
        try:
            ddgs = _get_ddgs()
            results = []
            for r in ddgs.text(query, max_results=self.max_results):
                results.append(SearchResult(
                    title=r.get("title", ""),
                    url=r.get("href", r.get("url", "")),
                    snippet=r.get("body", r.get("snippet", "")),
                ))
            logger.info(f"[Research] Found {len(results)} search results")
            return results
        except Exception as e:
            logger.warning(f"[Research] Web search failed: {e}")
            return []


class WikipediaFetcher:
    """Fetch Wikipedia article summaries for factual grounding."""

    def __init__(self, sentences: int = 5):
        self.sentences = sentences

    def fetch(self, topic: str) -> tuple:
        """Fetch Wikipedia summary and URL for a topic.
        Returns (summary, url) or ("", "") if not found.
        """
        logger.info(f"[Research] Fetching Wikipedia for: '{topic}'")
        try:
            wiki = _get_wikipedia()
            page = wiki.page(topic, auto_suggest=True, redirect=True)
            summary = page.summary[:2000]
            url = page.url
            logger.info(f"[Research] Wikipedia article found: '{page.title}'")
            return summary, url
        except wiki.exceptions.DisambiguationError as e:
            # Try the first option
            try:
                page = wiki.page(e.options[0], auto_suggest=False)
                return page.summary[:2000], page.url
            except Exception:
                return "", ""
        except Exception as e:
            logger.warning(f"[Research] Wikipedia fetch failed: {e}")
            return "", ""


class PageCrawler:
    """Crawl web pages and extract readable text using requests + BeautifulSoup."""

    def __init__(self, timeout: int = 10, max_pages: int = 3, max_text_length: int = 1500):
        self.timeout = timeout
        self.max_pages = max_pages
        self.max_text_length = max_text_length
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; TextCinemaEngine/1.0; +https://github.com/video-gen)"
        })

    def crawl(self, url: str) -> CrawledPage:
        """Crawl a single URL and extract text."""
        logger.info(f"[Research] Crawling: {url}")
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")

            # Remove script/style tags
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            title = soup.get_title or url
            if soup.title:
                title = soup.title.string or url

            # Extract text from paragraphs
            paragraphs = soup.find_all("p")
            text = " ".join(p.get_text(strip=True) for p in paragraphs[:10])

            # Clean up whitespace
            text = re.sub(r"\s+", " ", text).strip()

            return CrawledPage(
                url=url,
                title=title,
                text=text[:self.max_text_length],
            )
        except Exception as e:
            logger.warning(f"[Research] Crawl failed for {url}: {e}")
            return CrawledPage(url=url, title="", text="", error=str(e))

    def crawl_multiple(self, urls: List[str]) -> List[CrawledPage]:
        """Crawl multiple URLs (up to max_pages)."""
        pages = []
        for url in urls[:self.max_pages]:
            pages.append(self.crawl(url))
        return pages


class ResearchStage:
    """Stage 0: Internet Research — gathers references before story generation.

    Combines web search, Wikipedia, and page crawling into a ResearchContext
    that gets passed to the story generator as grounding context.
    """

    def __init__(self, config: dict = None):
        self.config = config or {}
        research_cfg = self.config.get("research", {})
        self.searcher = WebSearcher(max_results=research_cfg.get("max_search_results", 8))
        self.wiki_fetcher = WikipediaFetcher(sentences=research_cfg.get("wiki_sentences", 5))
        self.crawler = PageCrawler(
            timeout=research_cfg.get("crawl_timeout", 10),
            max_pages=research_cfg.get("max_crawl_pages", 3),
            max_text_length=research_cfg.get("max_crawl_text_length", 1500),
        )

    def research(self, topic: str) -> ResearchContext:
        """Run the full research pipeline for a topic."""
        logger.info(f"\n=== Starting Research Phase for: '{topic}' ===")

        context = ResearchContext(topic=topic)

        # 1. Wikipedia (fast, reliable)
        wiki_summary, wiki_url = self.wiki_fetcher.fetch(topic)
        context.wikipedia_summary = wiki_summary
        context.wikipedia_url = wiki_url

        # 2. Web search
        search_query = self._build_search_query(topic)
        context.search_results = self.searcher.search(search_query)

        # 3. Crawl top search results
        urls_to_crawl = [r.url for r in context.search_results if r.url]
        context.crawled_pages = self.crawler.crawl_multiple(urls_to_crawl)

        # 4. Build combined context
        context.to_prompt_context()

        logger.info(
            f"=== Research Complete: "
            f"{len(context.search_results)} search results, "
            f"{'Wikipedia' if wiki_summary else 'no Wikipedia'}, "
            f"{len(context.crawled_pages)} pages crawled ===\n"
        )

        return context

    def _build_search_query(self, topic: str) -> str:
        """Build a search query from the topic."""
        # Add context terms to get better results for storytelling
        return f"{topic} facts setting description"
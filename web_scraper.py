#!/usr/bin/env python3
"""
web_scraper.py - 웹 스크래핑 유틸리티

웹 페이지에서 데이터를 추출하는 다양한 기능을 제공합니다.
BeautifulSoup와 requests를 사용합니다.

주의: 웹 스크래핑 시 해당 사이트의 robots.txt와 이용약관을 확인하세요.
"""

import re
import json
import csv
import time
import argparse
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin, urlparse
from pathlib import Path

# 외부 라이브러리 체크
try:
    import requests
    from bs4 import BeautifulSoup
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False


@dataclass
class ScrapedLink:
    """스크래핑된 링크 정보"""
    text: str
    url: str
    is_external: bool = False


@dataclass  
class ScrapedImage:
    """스크래핑된 이미지 정보"""
    src: str
    alt: str = ""
    width: Optional[int] = None
    height: Optional[int] = None


@dataclass
class PageMetadata:
    """페이지 메타데이터"""
    title: str = ""
    description: str = ""
    keywords: List[str] = field(default_factory=list)
    og_title: str = ""
    og_description: str = ""
    og_image: str = ""
    canonical_url: str = ""


@dataclass
class ScrapedPage:
    """스크래핑된 페이지 정보"""
    url: str
    status_code: int
    metadata: PageMetadata
    text_content: str
    links: List[ScrapedLink]
    images: List[ScrapedImage]
    headings: Dict[str, List[str]]
    tables: List[List[List[str]]]


class WebScraper:
    """
    웹 스크래핑 유틸리티 클래스
    
    웹 페이지에서 다양한 데이터를 추출합니다.
    """
    
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    
    def __init__(self, timeout: int = 10, delay: float = 1.0):
        """
        Args:
            timeout: 요청 타임아웃 (초)
            delay: 연속 요청 간 딜레이 (초)
        """
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError(
                "필요한 라이브러리가 설치되지 않았습니다.\n"
                "설치: pip install requests beautifulsoup4"
            )
        
        self.timeout = timeout
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)
        self.last_request_time = 0
    
    def _wait_for_delay(self) -> None:
        """연속 요청 간 딜레이를 적용합니다."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request_time = time.time()
    
    def fetch(self, url: str) -> requests.Response:
        """URL에서 HTML을 가져옵니다."""
        self._wait_for_delay()
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response
    
    def get_soup(self, url: str) -> BeautifulSoup:
        """URL에서 BeautifulSoup 객체를 반환합니다."""
        response = self.fetch(url)
        return BeautifulSoup(response.text, "html.parser")
    
    def extract_metadata(self, soup: BeautifulSoup) -> PageMetadata:
        """페이지 메타데이터를 추출합니다."""
        metadata = PageMetadata()
        
        # 제목
        title_tag = soup.find("title")
        if title_tag:
            metadata.title = title_tag.get_text(strip=True)
        
        # meta 태그들
        for meta in soup.find_all("meta"):
            name = meta.get("name", "").lower()
            property_attr = meta.get("property", "").lower()
            content = meta.get("content", "")
            
            if name == "description":
                metadata.description = content
            elif name == "keywords":
                metadata.keywords = [k.strip() for k in content.split(",")]
            elif property_attr == "og:title":
                metadata.og_title = content
            elif property_attr == "og:description":
                metadata.og_description = content
            elif property_attr == "og:image":
                metadata.og_image = content
        
        # canonical URL
        canonical = soup.find("link", rel="canonical")
        if canonical:
            metadata.canonical_url = canonical.get("href", "")
        
        return metadata
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[ScrapedLink]:
        """페이지의 모든 링크를 추출합니다."""
        links = []
        base_domain = urlparse(base_url).netloc
        
        for a in soup.find_all("a", href=True):
            href = a["href"]
            
            # 상대 URL을 절대 URL로 변환
            full_url = urljoin(base_url, href)
            
            # 링크 도메인 확인
            link_domain = urlparse(full_url).netloc
            is_external = link_domain != base_domain
            
            text = a.get_text(strip=True) or "[이미지/아이콘]"
            
            links.append(ScrapedLink(
                text=text[:100],  # 텍스트 길이 제한
                url=full_url,
                is_external=is_external
            ))
        
        return links
    
    def extract_images(self, soup: BeautifulSoup, base_url: str) -> List[ScrapedImage]:
        """페이지의 모든 이미지를 추출합니다."""
        images = []
        
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if not src:
                continue
            
            full_src = urljoin(base_url, src)
            
            # 크기 정보
            width = img.get("width")
            height = img.get("height")
            
            images.append(ScrapedImage(
                src=full_src,
                alt=img.get("alt", ""),
                width=int(width) if width and width.isdigit() else None,
                height=int(height) if height and height.isdigit() else None
            ))
        
        return images
    
    def extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """h1~h6 제목들을 추출합니다."""
        headings = {}
        
        for level in range(1, 7):
            tag_name = f"h{level}"
            found = soup.find_all(tag_name)
            if found:
                headings[tag_name] = [h.get_text(strip=True) for h in found]
        
        return headings
    
    def extract_tables(self, soup: BeautifulSoup) -> List[List[List[str]]]:
        """테이블 데이터를 추출합니다."""
        tables = []
        
        for table in soup.find_all("table"):
            table_data = []
            
            for row in table.find_all("tr"):
                cells = row.find_all(["th", "td"])
                row_data = [cell.get_text(strip=True) for cell in cells]
                if row_data:
                    table_data.append(row_data)
            
            if table_data:
                tables.append(table_data)
        
        return tables
    
    def extract_text(self, soup: BeautifulSoup) -> str:
        """페이지의 텍스트 콘텐츠를 추출합니다."""
        # 스크립트, 스타일 태그 제거
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        
        text = soup.get_text(separator="\n", strip=True)
        
        # 여러 줄바꿈을 하나로
        text = re.sub(r"\n{3,}", "\n\n", text)
        
        return text
    
    def scrape(self, url: str) -> ScrapedPage:
        """URL을 스크래핑하여 모든 정보를 추출합니다."""
        response = self.fetch(url)
        soup = BeautifulSoup(response.text, "html.parser")
        
        return ScrapedPage(
            url=url,
            status_code=response.status_code,
            metadata=self.extract_metadata(soup),
            text_content=self.extract_text(BeautifulSoup(response.text, "html.parser")),
            links=self.extract_links(soup, url),
            images=self.extract_images(soup, url),
            headings=self.extract_headings(soup),
            tables=self.extract_tables(soup)
        )
    
    def find_elements(self, url: str, selector: str) -> List[str]:
        """CSS 선택자로 요소를 찾습니다."""
        soup = self.get_soup(url)
        elements = soup.select(selector)
        return [el.get_text(strip=True) for el in elements]
    
    def download_image(self, url: str, save_path: str) -> bool:
        """이미지를 다운로드합니다."""
        try:
            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
        except Exception:
            return False


def print_scraped_page(page: ScrapedPage, verbose: bool = False) -> None:
    """스크래핑 결과를 출력합니다."""
    print("\n" + "=" * 60)
    print(f"🌐 스크래핑 결과: {page.url}")
    print("=" * 60)
    
    print(f"\n📋 상태 코드: {page.status_code}")
    
    print("\n📑 메타데이터:")
    print("-" * 40)
    print(f"  제목: {page.metadata.title}")
    if page.metadata.description:
        print(f"  설명: {page.metadata.description[:100]}...")
    if page.metadata.keywords:
        print(f"  키워드: {', '.join(page.metadata.keywords[:5])}")
    if page.metadata.og_image:
        print(f"  OG 이미지: {page.metadata.og_image}")
    
    print(f"\n📊 통계:")
    print("-" * 40)
    print(f"  링크 수: {len(page.links)} (외부: {sum(1 for l in page.links if l.is_external)})")
    print(f"  이미지 수: {len(page.images)}")
    print(f"  테이블 수: {len(page.tables)}")
    print(f"  텍스트 길이: {len(page.text_content)} 자")
    
    if page.headings:
        print("\n📌 제목 구조:")
        print("-" * 40)
        for tag, texts in page.headings.items():
            for text in texts[:3]:  # 각 레벨당 최대 3개
                indent = "  " * int(tag[1])
                print(f"{indent}{tag}: {text[:50]}")
    
    if verbose:
        if page.links:
            print("\n🔗 링크 (처음 10개):")
            print("-" * 40)
            for link in page.links[:10]:
                external_mark = " [외부]" if link.is_external else ""
                print(f"  • {link.text[:30]}: {link.url[:50]}{external_mark}")
        
        if page.images:
            print("\n🖼️ 이미지 (처음 5개):")
            print("-" * 40)
            for img in page.images[:5]:
                print(f"  • {img.alt[:30] or '(alt 없음)'}: {img.src[:50]}")
        
        if page.tables:
            print("\n📊 테이블:")
            print("-" * 40)
            for i, table in enumerate(page.tables[:2]):
                print(f"  테이블 {i + 1}: {len(table)} 행")
                for row in table[:3]:
                    print(f"    {' | '.join(str(cell)[:15] for cell in row[:4])}")


def export_to_json(page: ScrapedPage, filepath: str) -> None:
    """스크래핑 결과를 JSON으로 저장합니다."""
    data = {
        "url": page.url,
        "status_code": page.status_code,
        "metadata": {
            "title": page.metadata.title,
            "description": page.metadata.description,
            "keywords": page.metadata.keywords,
            "og_title": page.metadata.og_title,
            "og_description": page.metadata.og_description,
            "og_image": page.metadata.og_image,
            "canonical_url": page.metadata.canonical_url,
        },
        "links": [{"text": l.text, "url": l.url, "is_external": l.is_external} for l in page.links],
        "images": [{"src": i.src, "alt": i.alt} for i in page.images],
        "headings": page.headings,
        "tables": page.tables,
        "text_content": page.text_content,
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ JSON 저장 완료: {filepath}")


def export_links_to_csv(links: List[ScrapedLink], filepath: str) -> None:
    """링크를 CSV로 저장합니다."""
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["텍스트", "URL", "외부링크"])
        for link in links:
            writer.writerow([link.text, link.url, "예" if link.is_external else "아니오"])
    
    print(f"✅ CSV 저장 완료: {filepath}")


def main():
    """메인 CLI 함수"""
    if not DEPENDENCIES_AVAILABLE:
        print("❌ 필요한 라이브러리가 설치되지 않았습니다.")
        print("설치: pip install requests beautifulsoup4")
        return
    
    parser = argparse.ArgumentParser(
        description="🌐 웹 스크래핑 유틸리티",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python web_scraper.py https://example.com              # 기본 스크래핑
  python web_scraper.py https://example.com -v           # 상세 출력
  python web_scraper.py https://example.com --json out.json  # JSON 저장
  python web_scraper.py https://example.com --links      # 링크만 추출
  python web_scraper.py https://example.com -s "h1"      # CSS 선택자로 추출

주의: 웹 스크래핑 시 해당 사이트의 robots.txt와 이용약관을 확인하세요.
        """
    )
    
    parser.add_argument("url", help="스크래핑할 URL")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="상세 출력")
    parser.add_argument("--json", type=str, metavar="FILE",
                        help="결과를 JSON 파일로 저장")
    parser.add_argument("--links", action="store_true",
                        help="링크만 추출")
    parser.add_argument("--images", action="store_true",
                        help="이미지만 추출")
    parser.add_argument("--text", action="store_true",
                        help="텍스트만 추출")
    parser.add_argument("-s", "--selector", type=str,
                        help="CSS 선택자로 요소 추출")
    parser.add_argument("--csv", type=str, metavar="FILE",
                        help="링크를 CSV 파일로 저장")
    parser.add_argument("--timeout", type=int, default=10,
                        help="요청 타임아웃 (초, 기본값: 10)")
    
    args = parser.parse_args()
    
    try:
        scraper = WebScraper(timeout=args.timeout)
        
        # CSS 선택자 모드
        if args.selector:
            print(f"\n🔍 선택자 '{args.selector}'로 검색 중...")
            results = scraper.find_elements(args.url, args.selector)
            
            print(f"\n찾은 요소: {len(results)}개")
            print("-" * 40)
            for i, text in enumerate(results[:20], 1):
                print(f"  {i}. {text[:100]}")
            return
        
        # 스크래핑 실행
        print(f"\n🔄 스크래핑 중: {args.url}")
        page = scraper.scrape(args.url)
        
        # 특정 데이터만 출력
        if args.links:
            print(f"\n🔗 링크 ({len(page.links)}개):")
            print("-" * 40)
            for link in page.links:
                external = " [외부]" if link.is_external else ""
                print(f"  • {link.text}: {link.url}{external}")
            
            if args.csv:
                export_links_to_csv(page.links, args.csv)
            return
        
        if args.images:
            print(f"\n🖼️ 이미지 ({len(page.images)}개):")
            print("-" * 40)
            for img in page.images:
                print(f"  • {img.alt or '(alt 없음)'}: {img.src}")
            return
        
        if args.text:
            print("\n📄 텍스트 콘텐츠:")
            print("-" * 40)
            print(page.text_content[:5000])
            if len(page.text_content) > 5000:
                print(f"\n... (총 {len(page.text_content)} 자)")
            return
        
        # 전체 결과 출력
        print_scraped_page(page, verbose=args.verbose)
        
        # JSON 저장
        if args.json:
            export_to_json(page, args.json)
    
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 오류: {e}")
    except Exception as e:
        print(f"❌ 오류: {e}")


if __name__ == "__main__":
    main()


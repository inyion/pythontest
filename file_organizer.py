#!/usr/bin/env python3
"""
file_organizer.py - 파일 정리/분류 유틸리티

지정된 폴더의 파일들을 확장자별로 자동 분류하는 도구입니다.
다운로드 폴더 정리 등에 유용합니다.
"""

import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict


# 파일 카테고리 매핑
FILE_CATEGORIES: Dict[str, List[str]] = {
    "📷 Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff"],
    "📹 Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
    "🎵 Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
    "📄 Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx"],
    "📦 Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
    "💻 Code": [".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".go", ".rs", ".rb", ".php"],
    "📊 Data": [".json", ".xml", ".csv", ".yaml", ".yml", ".sql", ".db", ".sqlite"],
    "📱 Applications": [".exe", ".msi", ".dmg", ".app", ".deb", ".rpm"],
    "🔤 Fonts": [".ttf", ".otf", ".woff", ".woff2", ".eot"],
}


@dataclass
class FileInfo:
    """파일 정보를 담는 데이터 클래스"""
    name: str
    path: Path
    size: int
    extension: str
    modified_time: datetime
    category: str = "📁 Others"


@dataclass
class OrganizeResult:
    """정리 결과를 담는 데이터 클래스"""
    total_files: int = 0
    moved_files: int = 0
    skipped_files: int = 0
    errors: List[str] = field(default_factory=list)
    category_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))


class FileOrganizer:
    """파일 정리를 수행하는 메인 클래스"""
    
    def __init__(self, source_dir: str, dest_dir: Optional[str] = None):
        """
        Args:
            source_dir: 정리할 소스 디렉토리
            dest_dir: 정리된 파일을 넣을 목적지 디렉토리 (None이면 source_dir에 정리)
        """
        self.source_dir = Path(source_dir).resolve()
        self.dest_dir = Path(dest_dir).resolve() if dest_dir else self.source_dir
        
        if not self.source_dir.exists():
            raise ValueError(f"소스 디렉토리가 존재하지 않습니다: {self.source_dir}")
        
        # 확장자 -> 카테고리 매핑 생성
        self.ext_to_category: Dict[str, str] = {}
        for category, extensions in FILE_CATEGORIES.items():
            for ext in extensions:
                self.ext_to_category[ext.lower()] = category
    
    def get_file_category(self, extension: str) -> str:
        """파일 확장자에 해당하는 카테고리를 반환합니다."""
        return self.ext_to_category.get(extension.lower(), "📁 Others")
    
    def scan_files(self) -> List[FileInfo]:
        """소스 디렉토리의 파일들을 스캔합니다."""
        files = []
        
        for item in self.source_dir.iterdir():
            if item.is_file():
                stat = item.stat()
                extension = item.suffix.lower()
                
                file_info = FileInfo(
                    name=item.name,
                    path=item,
                    size=stat.st_size,
                    extension=extension,
                    modified_time=datetime.fromtimestamp(stat.st_mtime),
                    category=self.get_file_category(extension)
                )
                files.append(file_info)
        
        return files
    
    def preview(self) -> Dict[str, List[FileInfo]]:
        """
        정리 결과를 미리보기합니다 (실제 이동하지 않음).
        
        Returns:
            카테고리별 파일 목록
        """
        files = self.scan_files()
        categorized: Dict[str, List[FileInfo]] = defaultdict(list)
        
        for file_info in files:
            categorized[file_info.category].append(file_info)
        
        return dict(categorized)
    
    def organize(self, dry_run: bool = False) -> OrganizeResult:
        """
        파일들을 카테고리별 폴더로 정리합니다.
        
        Args:
            dry_run: True면 실제로 이동하지 않고 시뮬레이션만 수행
            
        Returns:
            정리 결과
        """
        result = OrganizeResult()
        files = self.scan_files()
        result.total_files = len(files)
        
        for file_info in files:
            category_dir = self.dest_dir / file_info.category
            dest_path = category_dir / file_info.name
            
            try:
                if not dry_run:
                    # 카테고리 디렉토리 생성
                    category_dir.mkdir(exist_ok=True)
                    
                    # 동일한 이름의 파일이 있으면 이름 변경
                    if dest_path.exists():
                        base = dest_path.stem
                        ext = dest_path.suffix
                        counter = 1
                        while dest_path.exists():
                            dest_path = category_dir / f"{base}_{counter}{ext}"
                            counter += 1
                    
                    # 파일 이동
                    shutil.move(str(file_info.path), str(dest_path))
                
                result.moved_files += 1
                result.category_counts[file_info.category] += 1
                
            except Exception as e:
                result.errors.append(f"{file_info.name}: {str(e)}")
                result.skipped_files += 1
        
        return result
    
    def get_statistics(self) -> Dict:
        """디렉토리 통계를 반환합니다."""
        files = self.scan_files()
        
        total_size = sum(f.size for f in files)
        category_sizes: Dict[str, int] = defaultdict(int)
        category_counts: Dict[str, int] = defaultdict(int)
        
        for f in files:
            category_sizes[f.category] += f.size
            category_counts[f.category] += 1
        
        # 가장 큰 파일 찾기
        largest_files = sorted(files, key=lambda x: x.size, reverse=True)[:5]
        
        # 가장 오래된 파일 찾기
        oldest_files = sorted(files, key=lambda x: x.modified_time)[:5]
        
        return {
            "total_files": len(files),
            "total_size": total_size,
            "total_size_readable": format_size(total_size),
            "category_counts": dict(category_counts),
            "category_sizes": {k: format_size(v) for k, v in category_sizes.items()},
            "largest_files": [(f.name, format_size(f.size)) for f in largest_files],
            "oldest_files": [(f.name, f.modified_time.strftime("%Y-%m-%d")) for f in oldest_files]
        }


def format_size(size_bytes: int) -> str:
    """바이트 크기를 읽기 쉬운 형식으로 변환합니다."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def print_preview(categorized: Dict[str, List[FileInfo]]) -> None:
    """미리보기 결과를 출력합니다."""
    print("\n" + "=" * 60)
    print("📂 파일 정리 미리보기")
    print("=" * 60)
    
    for category, files in sorted(categorized.items()):
        print(f"\n{category} ({len(files)}개)")
        print("-" * 40)
        for f in files[:10]:  # 최대 10개만 표시
            print(f"  • {f.name} ({format_size(f.size)})")
        if len(files) > 10:
            print(f"  ... 외 {len(files) - 10}개")


def print_statistics(stats: Dict) -> None:
    """통계를 출력합니다."""
    print("\n" + "=" * 60)
    print("📊 디렉토리 통계")
    print("=" * 60)
    
    print(f"\n총 파일 수: {stats['total_files']}개")
    print(f"총 용량: {stats['total_size_readable']}")
    
    print("\n📁 카테고리별 파일 수:")
    print("-" * 40)
    for category, count in sorted(stats['category_counts'].items()):
        size = stats['category_sizes'].get(category, "0 B")
        print(f"  {category}: {count}개 ({size})")
    
    if stats['largest_files']:
        print("\n📦 가장 큰 파일 TOP 5:")
        print("-" * 40)
        for name, size in stats['largest_files']:
            print(f"  • {name}: {size}")
    
    if stats['oldest_files']:
        print("\n📅 가장 오래된 파일 TOP 5:")
        print("-" * 40)
        for name, date in stats['oldest_files']:
            print(f"  • {name}: {date}")


def print_result(result: OrganizeResult, dry_run: bool = False) -> None:
    """정리 결과를 출력합니다."""
    print("\n" + "=" * 60)
    print("✅ 파일 정리 " + ("미리보기 결과" if dry_run else "완료"))
    print("=" * 60)
    
    print(f"\n총 파일: {result.total_files}개")
    print(f"{'이동 예정' if dry_run else '이동 완료'}: {result.moved_files}개")
    print(f"건너뜀: {result.skipped_files}개")
    
    print("\n📁 카테고리별 파일 수:")
    print("-" * 40)
    for category, count in sorted(result.category_counts.items()):
        print(f"  {category}: {count}개")
    
    if result.errors:
        print("\n⚠️ 오류:")
        for error in result.errors:
            print(f"  • {error}")


def main():
    """메인 CLI 함수"""
    parser = argparse.ArgumentParser(
        description="📂 파일 정리 유틸리티 - 파일을 확장자별로 자동 분류합니다",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python file_organizer.py ~/Downloads              # Downloads 폴더 정리
  python file_organizer.py ~/Downloads --preview    # 미리보기만
  python file_organizer.py ~/Downloads --stats      # 통계만 보기
  python file_organizer.py ~/Downloads -d ~/Sorted  # 다른 폴더로 정리
  python file_organizer.py ~/Downloads --dry-run    # 시뮬레이션 실행
        """
    )
    
    parser.add_argument("source", nargs="?", default=".",
                        help="정리할 디렉토리 경로 (기본값: 현재 디렉토리)")
    parser.add_argument("-d", "--dest", type=str,
                        help="정리된 파일을 넣을 디렉토리 (기본값: 소스와 동일)")
    parser.add_argument("--preview", action="store_true",
                        help="미리보기만 수행 (파일 이동 없음)")
    parser.add_argument("--stats", action="store_true",
                        help="디렉토리 통계 보기")
    parser.add_argument("--dry-run", action="store_true",
                        help="시뮬레이션 실행 (실제 이동 없음)")
    
    args = parser.parse_args()
    
    try:
        organizer = FileOrganizer(args.source, args.dest)
        
        if args.stats:
            stats = organizer.get_statistics()
            print_statistics(stats)
            return
        
        if args.preview:
            categorized = organizer.preview()
            print_preview(categorized)
            return
        
        # 실제 정리 수행
        if args.dry_run:
            result = organizer.organize(dry_run=True)
            print_result(result, dry_run=True)
        else:
            # 확인 메시지
            categorized = organizer.preview()
            print_preview(categorized)
            
            total = sum(len(files) for files in categorized.values())
            print(f"\n⚠️  {total}개의 파일을 정리하시겠습니까?")
            response = input("계속하려면 'yes'를 입력하세요: ")
            
            if response.lower() in ["yes", "y", "예"]:
                result = organizer.organize(dry_run=False)
                print_result(result, dry_run=False)
            else:
                print("❌ 작업이 취소되었습니다.")
    
    except ValueError as e:
        print(f"❌ 오류: {e}")
    except KeyboardInterrupt:
        print("\n❌ 작업이 중단되었습니다.")


if __name__ == "__main__":
    main()


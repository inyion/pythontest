#!/usr/bin/env python3
"""
data_analyzer.py - 데이터 분석 유틸리티

CSV 파일의 기본적인 데이터 분석 및 시각화 기능을 제공합니다.
pandas 없이 기본 라이브러리만으로 구현되었습니다.
"""

import csv
import math
import argparse
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from collections import Counter, defaultdict
from pathlib import Path


@dataclass
class ColumnStats:
    """열의 통계 정보"""
    name: str
    dtype: str  # 'numeric', 'string', 'mixed'
    count: int
    missing: int
    unique: int
    
    # 숫자형일 경우
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    mean: Optional[float] = None
    median: Optional[float] = None
    std_dev: Optional[float] = None
    sum_val: Optional[float] = None
    
    # 문자형일 경우
    top_values: List[Tuple[str, int]] = field(default_factory=list)


@dataclass
class DataSummary:
    """데이터셋 요약 정보"""
    filename: str
    rows: int
    columns: int
    column_names: List[str]
    column_stats: Dict[str, ColumnStats]
    sample_rows: List[Dict[str, Any]]


class DataAnalyzer:
    """
    CSV 데이터 분석 클래스
    
    pandas 없이 기본 라이브러리만으로 데이터 분석을 수행합니다.
    """
    
    def __init__(self, filepath: str, encoding: str = "utf-8"):
        """
        Args:
            filepath: CSV 파일 경로
            encoding: 파일 인코딩 (기본값: utf-8)
        """
        self.filepath = Path(filepath)
        self.encoding = encoding
        self.data: List[Dict[str, Any]] = []
        self.columns: List[str] = []
        
        self._load_data()
    
    def _load_data(self) -> None:
        """CSV 파일을 로드합니다."""
        encodings_to_try = [self.encoding, "utf-8", "cp949", "euc-kr", "latin-1"]
        
        for enc in encodings_to_try:
            try:
                with open(self.filepath, "r", encoding=enc, newline="") as f:
                    # 구분자 자동 감지
                    sample = f.read(4096)
                    f.seek(0)
                    
                    # 구분자 추측
                    delimiter = ","
                    for delim in [",", "\t", ";", "|"]:
                        if sample.count(delim) > sample.count(delimiter):
                            delimiter = delim
                    
                    reader = csv.DictReader(f, delimiter=delimiter)
                    self.columns = reader.fieldnames or []
                    self.data = list(reader)
                    self.encoding = enc
                    return
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        raise ValueError(f"파일을 읽을 수 없습니다: {self.filepath}")
    
    def _is_numeric(self, value: str) -> bool:
        """값이 숫자인지 확인합니다."""
        if not value or value.strip() == "":
            return False
        try:
            float(value.replace(",", ""))
            return True
        except (ValueError, AttributeError):
            return False
    
    def _to_numeric(self, value: str) -> Optional[float]:
        """값을 숫자로 변환합니다."""
        if not value or value.strip() == "":
            return None
        try:
            return float(value.replace(",", ""))
        except (ValueError, AttributeError):
            return None
    
    def _calculate_stats(self, values: List[float]) -> Dict[str, float]:
        """숫자 리스트의 통계를 계산합니다."""
        if not values:
            return {}
        
        n = len(values)
        sorted_vals = sorted(values)
        
        mean = sum(values) / n
        
        # 중앙값
        mid = n // 2
        if n % 2 == 0:
            median = (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
        else:
            median = sorted_vals[mid]
        
        # 표준편차
        if n > 1:
            variance = sum((x - mean) ** 2 for x in values) / (n - 1)
            std_dev = math.sqrt(variance)
        else:
            std_dev = 0
        
        return {
            "min": min(values),
            "max": max(values),
            "mean": mean,
            "median": median,
            "std_dev": std_dev,
            "sum": sum(values),
        }
    
    def get_column_stats(self, column: str) -> ColumnStats:
        """특정 열의 통계를 계산합니다."""
        if column not in self.columns:
            raise ValueError(f"열이 존재하지 않습니다: {column}")
        
        values = [row.get(column, "") for row in self.data]
        
        # 결측치 계산
        missing = sum(1 for v in values if not v or v.strip() == "")
        
        # 고유값 수
        unique = len(set(v for v in values if v and v.strip()))
        
        # 숫자형 여부 판단
        numeric_values = [self._to_numeric(v) for v in values]
        numeric_values = [v for v in numeric_values if v is not None]
        
        numeric_ratio = len(numeric_values) / len(values) if values else 0
        
        stats = ColumnStats(
            name=column,
            dtype="numeric" if numeric_ratio > 0.8 else "string",
            count=len(values),
            missing=missing,
            unique=unique
        )
        
        if stats.dtype == "numeric" and numeric_values:
            calc_stats = self._calculate_stats(numeric_values)
            stats.min_val = calc_stats.get("min")
            stats.max_val = calc_stats.get("max")
            stats.mean = calc_stats.get("mean")
            stats.median = calc_stats.get("median")
            stats.std_dev = calc_stats.get("std_dev")
            stats.sum_val = calc_stats.get("sum")
        else:
            # 문자형: 빈도 상위 값
            counter = Counter(v for v in values if v and v.strip())
            stats.top_values = counter.most_common(5)
        
        return stats
    
    def get_summary(self) -> DataSummary:
        """데이터셋 전체 요약을 반환합니다."""
        column_stats = {}
        for col in self.columns:
            column_stats[col] = self.get_column_stats(col)
        
        return DataSummary(
            filename=self.filepath.name,
            rows=len(self.data),
            columns=len(self.columns),
            column_names=self.columns,
            column_stats=column_stats,
            sample_rows=self.data[:5]
        )
    
    def describe(self) -> str:
        """pandas의 describe()와 유사한 출력을 생성합니다."""
        summary = self.get_summary()
        
        lines = []
        lines.append(f"파일: {summary.filename}")
        lines.append(f"행 수: {summary.rows:,}")
        lines.append(f"열 수: {summary.columns}")
        lines.append("")
        
        # 숫자형 열 통계
        numeric_cols = [s for s in summary.column_stats.values() if s.dtype == "numeric"]
        if numeric_cols:
            lines.append("📊 숫자형 열 통계:")
            lines.append("-" * 80)
            
            # 헤더
            headers = ["", "count", "mean", "std", "min", "median", "max"]
            lines.append(f"{headers[0]:15} {headers[1]:>10} {headers[2]:>12} {headers[3]:>12} {headers[4]:>12} {headers[5]:>12} {headers[6]:>12}")
            lines.append("-" * 80)
            
            for s in numeric_cols:
                lines.append(
                    f"{s.name[:15]:15} {s.count - s.missing:>10} "
                    f"{s.mean:>12.2f} {s.std_dev:>12.2f} "
                    f"{s.min_val:>12.2f} {s.median:>12.2f} {s.max_val:>12.2f}"
                )
        
        lines.append("")
        
        # 문자형 열 통계
        string_cols = [s for s in summary.column_stats.values() if s.dtype == "string"]
        if string_cols:
            lines.append("📝 문자형 열 통계:")
            lines.append("-" * 60)
            
            for s in string_cols:
                lines.append(f"\n{s.name}:")
                lines.append(f"  - 유효값: {s.count - s.missing:,} / 결측: {s.missing:,}")
                lines.append(f"  - 고유값: {s.unique:,}")
                if s.top_values:
                    top_str = ", ".join(f"{v}({c})" for v, c in s.top_values[:3])
                    lines.append(f"  - 상위값: {top_str}")
        
        return "\n".join(lines)
    
    def filter(self, column: str, condition: str, value: Any) -> List[Dict[str, Any]]:
        """
        조건에 맞는 행을 필터링합니다.
        
        Args:
            column: 필터링할 열
            condition: 조건 (eq, ne, gt, lt, ge, le, contains)
            value: 비교 값
            
        Returns:
            필터링된 행 목록
        """
        if column not in self.columns:
            raise ValueError(f"열이 존재하지 않습니다: {column}")
        
        results = []
        
        for row in self.data:
            cell_value = row.get(column, "")
            numeric_cell = self._to_numeric(cell_value)
            
            match = False
            
            if condition == "eq":
                match = cell_value == str(value) or (numeric_cell is not None and numeric_cell == float(value))
            elif condition == "ne":
                match = cell_value != str(value)
            elif condition == "gt" and numeric_cell is not None:
                match = numeric_cell > float(value)
            elif condition == "lt" and numeric_cell is not None:
                match = numeric_cell < float(value)
            elif condition == "ge" and numeric_cell is not None:
                match = numeric_cell >= float(value)
            elif condition == "le" and numeric_cell is not None:
                match = numeric_cell <= float(value)
            elif condition == "contains":
                match = str(value).lower() in cell_value.lower()
            
            if match:
                results.append(row)
        
        return results
    
    def group_by(self, column: str, agg_column: Optional[str] = None) -> Dict[str, Any]:
        """
        열 기준으로 그룹화합니다.
        
        Args:
            column: 그룹화 기준 열
            agg_column: 집계할 열 (선택적)
            
        Returns:
            그룹별 집계 결과
        """
        if column not in self.columns:
            raise ValueError(f"열이 존재하지 않습니다: {column}")
        
        groups: Dict[str, List[Dict]] = defaultdict(list)
        
        for row in self.data:
            key = row.get(column, "(빈값)")
            groups[key].append(row)
        
        if agg_column and agg_column in self.columns:
            # 숫자형 집계
            result = {}
            for key, rows in groups.items():
                values = [self._to_numeric(r.get(agg_column, "")) for r in rows]
                values = [v for v in values if v is not None]
                
                if values:
                    result[key] = {
                        "count": len(rows),
                        "sum": sum(values),
                        "mean": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                    }
                else:
                    result[key] = {"count": len(rows)}
            return result
        else:
            # 단순 카운트
            return {key: len(rows) for key, rows in groups.items()}
    
    def correlation(self, col1: str, col2: str) -> Optional[float]:
        """두 숫자형 열의 상관계수를 계산합니다."""
        if col1 not in self.columns or col2 not in self.columns:
            raise ValueError("열이 존재하지 않습니다")
        
        pairs = []
        for row in self.data:
            v1 = self._to_numeric(row.get(col1, ""))
            v2 = self._to_numeric(row.get(col2, ""))
            if v1 is not None and v2 is not None:
                pairs.append((v1, v2))
        
        if len(pairs) < 2:
            return None
        
        n = len(pairs)
        x_vals = [p[0] for p in pairs]
        y_vals = [p[1] for p in pairs]
        
        mean_x = sum(x_vals) / n
        mean_y = sum(y_vals) / n
        
        numerator = sum((x - mean_x) * (y - mean_y) for x, y in pairs)
        denom_x = math.sqrt(sum((x - mean_x) ** 2 for x in x_vals))
        denom_y = math.sqrt(sum((y - mean_y) ** 2 for y in y_vals))
        
        if denom_x == 0 or denom_y == 0:
            return None
        
        return numerator / (denom_x * denom_y)
    
    def to_csv(self, filepath: str, rows: Optional[List[Dict]] = None) -> None:
        """데이터를 CSV 파일로 저장합니다."""
        data_to_write = rows if rows is not None else self.data
        
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.columns)
            writer.writeheader()
            writer.writerows(data_to_write)
    
    def head(self, n: int = 5) -> List[Dict[str, Any]]:
        """처음 n개 행을 반환합니다."""
        return self.data[:n]
    
    def tail(self, n: int = 5) -> List[Dict[str, Any]]:
        """마지막 n개 행을 반환합니다."""
        return self.data[-n:]
    
    def value_counts(self, column: str) -> List[Tuple[str, int]]:
        """열의 값 빈도를 반환합니다."""
        if column not in self.columns:
            raise ValueError(f"열이 존재하지 않습니다: {column}")
        
        values = [row.get(column, "") for row in self.data]
        return Counter(values).most_common()


def create_histogram(values: List[float], bins: int = 10, width: int = 50) -> str:
    """간단한 텍스트 히스토그램을 생성합니다."""
    if not values:
        return "데이터가 없습니다."
    
    min_val = min(values)
    max_val = max(values)
    
    if min_val == max_val:
        return f"모든 값이 동일: {min_val}"
    
    bin_width = (max_val - min_val) / bins
    bin_counts = [0] * bins
    
    for v in values:
        idx = min(int((v - min_val) / bin_width), bins - 1)
        bin_counts[idx] += 1
    
    max_count = max(bin_counts) if bin_counts else 1
    
    lines = []
    for i, count in enumerate(bin_counts):
        start = min_val + i * bin_width
        end = start + bin_width
        bar_len = int(count / max_count * width)
        bar = "█" * bar_len
        lines.append(f"{start:10.2f} - {end:10.2f} | {bar} ({count})")
    
    return "\n".join(lines)


def print_table(rows: List[Dict[str, Any]], columns: List[str], max_col_width: int = 20) -> None:
    """데이터를 테이블 형식으로 출력합니다."""
    if not rows:
        print("데이터가 없습니다.")
        return
    
    # 열 너비 계산
    col_widths = {}
    for col in columns:
        max_width = len(col)
        for row in rows[:50]:  # 처음 50행만 확인
            val = str(row.get(col, ""))
            max_width = max(max_width, min(len(val), max_col_width))
        col_widths[col] = min(max_width, max_col_width)
    
    # 헤더
    header = " | ".join(col[:col_widths[col]].ljust(col_widths[col]) for col in columns)
    separator = "-+-".join("-" * col_widths[col] for col in columns)
    
    print(header)
    print(separator)
    
    # 데이터
    for row in rows:
        values = []
        for col in columns:
            val = str(row.get(col, ""))[:max_col_width]
            values.append(val.ljust(col_widths[col]))
        print(" | ".join(values))


def main():
    """메인 CLI 함수"""
    parser = argparse.ArgumentParser(
        description="📊 데이터 분석 유틸리티",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python data_analyzer.py data.csv                    # 데이터 요약
  python data_analyzer.py data.csv --describe         # 상세 통계
  python data_analyzer.py data.csv --head 10          # 처음 10행
  python data_analyzer.py data.csv --column age       # 특정 열 통계
  python data_analyzer.py data.csv --filter "age gt 30"  # 필터링
  python data_analyzer.py data.csv --group city       # 그룹화
  python data_analyzer.py data.csv --hist age         # 히스토그램
  python data_analyzer.py data.csv --corr age salary  # 상관계수
        """
    )
    
    parser.add_argument("file", help="CSV 파일 경로")
    parser.add_argument("--describe", "-d", action="store_true",
                        help="상세 통계 출력")
    parser.add_argument("--head", type=int, metavar="N",
                        help="처음 N개 행 출력")
    parser.add_argument("--tail", type=int, metavar="N",
                        help="마지막 N개 행 출력")
    parser.add_argument("--column", "-c", type=str,
                        help="특정 열의 통계")
    parser.add_argument("--filter", "-f", type=str,
                        help="필터링 (예: 'column gt 100')")
    parser.add_argument("--group", "-g", type=str,
                        help="그룹화 기준 열")
    parser.add_argument("--agg", type=str,
                        help="그룹화 시 집계할 열")
    parser.add_argument("--hist", type=str, metavar="COLUMN",
                        help="히스토그램 출력")
    parser.add_argument("--corr", nargs=2, metavar=("COL1", "COL2"),
                        help="두 열의 상관계수")
    parser.add_argument("--value-counts", "-v", type=str, metavar="COLUMN",
                        help="값 빈도 출력")
    parser.add_argument("--output", "-o", type=str,
                        help="결과 저장 파일")
    parser.add_argument("--encoding", "-e", type=str, default="utf-8",
                        help="파일 인코딩 (기본값: utf-8)")
    
    args = parser.parse_args()
    
    try:
        analyzer = DataAnalyzer(args.file, encoding=args.encoding)
        
        print(f"\n📂 파일: {args.file}")
        print(f"📋 행: {len(analyzer.data):,} | 열: {len(analyzer.columns)}")
        print(f"📑 열 목록: {', '.join(analyzer.columns)}")
        print()
        
        # 상세 통계
        if args.describe:
            print(analyzer.describe())
            return
        
        # 처음/마지막 N행
        if args.head:
            print(f"📄 처음 {args.head}개 행:")
            print_table(analyzer.head(args.head), analyzer.columns)
            return
        
        if args.tail:
            print(f"📄 마지막 {args.tail}개 행:")
            print_table(analyzer.tail(args.tail), analyzer.columns)
            return
        
        # 특정 열 통계
        if args.column:
            stats = analyzer.get_column_stats(args.column)
            
            print(f"📊 열 '{stats.name}' 통계:")
            print("-" * 40)
            print(f"  타입: {stats.dtype}")
            print(f"  유효값: {stats.count - stats.missing:,}")
            print(f"  결측값: {stats.missing:,}")
            print(f"  고유값: {stats.unique:,}")
            
            if stats.dtype == "numeric":
                print(f"  최솟값: {stats.min_val:,.2f}")
                print(f"  최댓값: {stats.max_val:,.2f}")
                print(f"  평균: {stats.mean:,.2f}")
                print(f"  중앙값: {stats.median:,.2f}")
                print(f"  표준편차: {stats.std_dev:,.2f}")
                print(f"  합계: {stats.sum_val:,.2f}")
            else:
                print("  상위 값:")
                for val, count in stats.top_values:
                    print(f"    - {val}: {count:,}")
            return
        
        # 필터링
        if args.filter:
            parts = args.filter.split()
            if len(parts) < 3:
                print("❌ 필터 형식: 'column condition value'")
                print("   조건: eq, ne, gt, lt, ge, le, contains")
                return
            
            col, cond, val = parts[0], parts[1], " ".join(parts[2:])
            filtered = analyzer.filter(col, cond, val)
            
            print(f"🔍 필터 결과: {len(filtered):,}개 행")
            print_table(filtered[:20], analyzer.columns)
            
            if args.output:
                analyzer.to_csv(args.output, filtered)
                print(f"\n✅ 저장됨: {args.output}")
            return
        
        # 그룹화
        if args.group:
            result = analyzer.group_by(args.group, args.agg)
            
            print(f"📊 '{args.group}' 기준 그룹화:")
            print("-" * 60)
            
            if args.agg:
                for key, stats in sorted(result.items(), key=lambda x: x[1].get("count", 0), reverse=True)[:20]:
                    print(f"\n{key}:")
                    for stat_name, stat_val in stats.items():
                        if isinstance(stat_val, float):
                            print(f"  {stat_name}: {stat_val:,.2f}")
                        else:
                            print(f"  {stat_name}: {stat_val:,}")
            else:
                for key, count in sorted(result.items(), key=lambda x: x[1], reverse=True)[:20]:
                    print(f"  {key}: {count:,}")
            return
        
        # 히스토그램
        if args.hist:
            stats = analyzer.get_column_stats(args.hist)
            
            if stats.dtype != "numeric":
                print(f"❌ '{args.hist}' 열은 숫자형이 아닙니다.")
                return
            
            values = []
            for row in analyzer.data:
                v = analyzer._to_numeric(row.get(args.hist, ""))
                if v is not None:
                    values.append(v)
            
            print(f"📊 '{args.hist}' 히스토그램:")
            print("-" * 70)
            print(create_histogram(values))
            return
        
        # 상관계수
        if args.corr:
            col1, col2 = args.corr
            corr = analyzer.correlation(col1, col2)
            
            if corr is not None:
                print(f"📈 상관계수 ({col1} vs {col2}): {corr:.4f}")
                
                if abs(corr) >= 0.7:
                    strength = "강한"
                elif abs(corr) >= 0.4:
                    strength = "중간"
                else:
                    strength = "약한"
                
                direction = "양의" if corr > 0 else "음의"
                print(f"   해석: {strength} {direction} 상관관계")
            else:
                print("❌ 상관계수를 계산할 수 없습니다.")
            return
        
        # 값 빈도
        if args.value_counts:
            counts = analyzer.value_counts(args.value_counts)
            
            print(f"📊 '{args.value_counts}' 값 빈도:")
            print("-" * 40)
            for val, count in counts[:20]:
                pct = count / len(analyzer.data) * 100
                bar = "█" * int(pct / 2)
                print(f"  {val[:20]:20} {count:>6} ({pct:5.1f}%) {bar}")
            return
        
        # 기본: 요약 정보
        print(analyzer.describe())
        
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {args.file}")
    except ValueError as e:
        print(f"❌ 오류: {e}")
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
json_utils.py - JSON 데이터 처리 유틸리티

JSON 파일의 조회, 수정, 비교, 변환 등 다양한 작업을 수행하는 CLI 도구입니다.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from functools import reduce
import operator


class JsonNavigator:
    """
    JSON 데이터를 탐색하고 조작하는 클래스
    
    점 표기법(dot notation)으로 중첩된 값에 접근할 수 있습니다.
    예: "users.0.name" -> data["users"][0]["name"]
    """
    
    def __init__(self, data: Union[Dict, List]):
        self.data = data
    
    @classmethod
    def from_file(cls, filepath: str) -> "JsonNavigator":
        """파일에서 JSON을 읽어 JsonNavigator 인스턴스를 생성합니다."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(data)
    
    @classmethod
    def from_string(cls, json_string: str) -> "JsonNavigator":
        """문자열에서 JSON을 파싱하여 JsonNavigator 인스턴스를 생성합니다."""
        data = json.loads(json_string)
        return cls(data)
    
    def _parse_path(self, path: str) -> List[Union[str, int]]:
        """점 표기법 경로를 파싱합니다."""
        if not path:
            return []
        
        keys = []
        for part in path.split("."):
            # 숫자면 인덱스로 변환
            if part.isdigit():
                keys.append(int(part))
            elif part.startswith("[") and part.endswith("]"):
                keys.append(int(part[1:-1]))
            else:
                keys.append(part)
        return keys
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        점 표기법 경로로 값을 가져옵니다.
        
        Args:
            path: 점 표기법 경로 (예: "users.0.name")
            default: 값이 없을 경우 반환할 기본값
            
        Returns:
            해당 경로의 값 또는 기본값
        """
        if not path:
            return self.data
        
        keys = self._parse_path(path)
        
        try:
            result = self.data
            for key in keys:
                if isinstance(result, dict):
                    result = result[key]
                elif isinstance(result, list) and isinstance(key, int):
                    result = result[key]
                else:
                    return default
            return result
        except (KeyError, IndexError, TypeError):
            return default
    
    def set(self, path: str, value: Any) -> bool:
        """
        점 표기법 경로에 값을 설정합니다.
        
        Args:
            path: 점 표기법 경로
            value: 설정할 값
            
        Returns:
            성공 여부
        """
        keys = self._parse_path(path)
        if not keys:
            self.data = value
            return True
        
        try:
            obj = self.data
            for key in keys[:-1]:
                if isinstance(obj, dict):
                    if key not in obj:
                        obj[key] = {}
                    obj = obj[key]
                elif isinstance(obj, list) and isinstance(key, int):
                    obj = obj[key]
                else:
                    return False
            
            final_key = keys[-1]
            if isinstance(obj, dict):
                obj[final_key] = value
            elif isinstance(obj, list) and isinstance(final_key, int):
                obj[final_key] = value
            return True
        except (KeyError, IndexError, TypeError):
            return False
    
    def delete(self, path: str) -> bool:
        """점 표기법 경로의 값을 삭제합니다."""
        keys = self._parse_path(path)
        if not keys:
            return False
        
        try:
            obj = self.data
            for key in keys[:-1]:
                obj = obj[key] if isinstance(obj, dict) else obj[int(key)]
            
            final_key = keys[-1]
            if isinstance(obj, dict):
                del obj[final_key]
            elif isinstance(obj, list):
                del obj[int(final_key)]
            return True
        except (KeyError, IndexError, TypeError):
            return False
    
    def search(self, key: str, value: Any = None) -> List[str]:
        """
        특정 키(또는 키-값 쌍)를 검색하여 경로 목록을 반환합니다.
        
        Args:
            key: 찾을 키 이름
            value: 선택적 값 (지정하면 키-값 모두 일치해야 함)
            
        Returns:
            일치하는 경로 목록
        """
        results = []
        
        def search_recursive(obj: Any, current_path: str):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_path = f"{current_path}.{k}" if current_path else k
                    if k == key:
                        if value is None or v == value:
                            results.append(new_path)
                    search_recursive(v, new_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_path = f"{current_path}.{i}" if current_path else str(i)
                    search_recursive(item, new_path)
        
        search_recursive(self.data, "")
        return results
    
    def flatten(self, separator: str = ".") -> Dict[str, Any]:
        """
        중첩된 JSON을 평탄화합니다.
        
        Args:
            separator: 키 구분자
            
        Returns:
            평탄화된 딕셔너리
        """
        result = {}
        
        def flatten_recursive(obj: Any, prefix: str):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{prefix}{separator}{k}" if prefix else k
                    flatten_recursive(v, new_key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_key = f"{prefix}{separator}{i}" if prefix else str(i)
                    flatten_recursive(item, new_key)
            else:
                result[prefix] = obj
        
        flatten_recursive(self.data, "")
        return result
    
    def to_json(self, indent: int = 2, ensure_ascii: bool = False) -> str:
        """JSON 문자열로 변환합니다."""
        return json.dumps(self.data, indent=indent, ensure_ascii=ensure_ascii)
    
    def save(self, filepath: str, indent: int = 2) -> None:
        """파일로 저장합니다."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=indent, ensure_ascii=False)


def compare_json(json1: Any, json2: Any, path: str = "") -> List[Dict[str, Any]]:
    """
    두 JSON 객체를 비교하여 차이점을 반환합니다.
    
    Returns:
        차이점 목록 [{"path": "...", "type": "...", "old": ..., "new": ...}, ...]
    """
    differences = []
    
    if type(json1) != type(json2):
        differences.append({
            "path": path or "(root)",
            "type": "type_change",
            "old": f"{type(json1).__name__}: {json1}",
            "new": f"{type(json2).__name__}: {json2}"
        })
        return differences
    
    if isinstance(json1, dict):
        all_keys = set(json1.keys()) | set(json2.keys())
        for key in all_keys:
            new_path = f"{path}.{key}" if path else key
            if key not in json1:
                differences.append({
                    "path": new_path,
                    "type": "added",
                    "old": None,
                    "new": json2[key]
                })
            elif key not in json2:
                differences.append({
                    "path": new_path,
                    "type": "removed",
                    "old": json1[key],
                    "new": None
                })
            else:
                differences.extend(compare_json(json1[key], json2[key], new_path))
    
    elif isinstance(json1, list):
        max_len = max(len(json1), len(json2))
        for i in range(max_len):
            new_path = f"{path}.{i}" if path else str(i)
            if i >= len(json1):
                differences.append({
                    "path": new_path,
                    "type": "added",
                    "old": None,
                    "new": json2[i]
                })
            elif i >= len(json2):
                differences.append({
                    "path": new_path,
                    "type": "removed",
                    "old": json1[i],
                    "new": None
                })
            else:
                differences.extend(compare_json(json1[i], json2[i], new_path))
    
    else:
        if json1 != json2:
            differences.append({
                "path": path or "(root)",
                "type": "changed",
                "old": json1,
                "new": json2
            })
    
    return differences


def json_to_csv(data: List[Dict], delimiter: str = ",") -> str:
    """딕셔너리 리스트를 CSV 문자열로 변환합니다."""
    if not data:
        return ""
    
    # 모든 키 수집
    all_keys = set()
    for item in data:
        if isinstance(item, dict):
            all_keys.update(item.keys())
    
    headers = sorted(all_keys)
    
    lines = [delimiter.join(headers)]
    for item in data:
        if isinstance(item, dict):
            row = []
            for key in headers:
                value = item.get(key, "")
                # CSV 이스케이프 처리
                if isinstance(value, str) and (delimiter in value or '"' in value or '\n' in value):
                    value = '"' + value.replace('"', '""') + '"'
                row.append(str(value))
            lines.append(delimiter.join(row))
    
    return "\n".join(lines)


def print_json_tree(data: Any, prefix: str = "", is_last: bool = True) -> None:
    """JSON 구조를 트리 형태로 출력합니다."""
    connector = "└── " if is_last else "├── "
    
    if isinstance(data, dict):
        items = list(data.items())
        for i, (key, value) in enumerate(items):
            is_last_item = (i == len(items) - 1)
            if isinstance(value, (dict, list)):
                print(f"{prefix}{connector}📁 {key}")
                new_prefix = prefix + ("    " if is_last else "│   ")
                print_json_tree(value, new_prefix, is_last_item)
            else:
                print(f"{prefix}{connector}📄 {key}: {value}")
    
    elif isinstance(data, list):
        for i, item in enumerate(data):
            is_last_item = (i == len(data) - 1)
            if isinstance(item, (dict, list)):
                print(f"{prefix}{connector}[{i}]")
                new_prefix = prefix + ("    " if is_last else "│   ")
                print_json_tree(item, new_prefix, is_last_item)
            else:
                print(f"{prefix}{connector}[{i}]: {item}")


def main():
    """메인 CLI 함수"""
    parser = argparse.ArgumentParser(
        description="🔧 JSON 데이터 처리 유틸리티",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python json_utils.py data.json                       # JSON 내용 보기
  python json_utils.py data.json --get "users.0.name"  # 특정 값 가져오기
  python json_utils.py data.json --tree                # 트리 구조로 보기
  python json_utils.py data.json --flatten             # 평탄화
  python json_utils.py data.json --search "email"      # 키 검색
  python json_utils.py --compare file1.json file2.json # 두 파일 비교
  python json_utils.py data.json --to-csv              # CSV로 변환
        """
    )
    
    parser.add_argument("file", nargs="?", help="JSON 파일 경로")
    parser.add_argument("--get", "-g", type=str, metavar="PATH",
                        help="점 표기법으로 값 가져오기 (예: users.0.name)")
    parser.add_argument("--set", "-s", nargs=2, metavar=("PATH", "VALUE"),
                        help="점 표기법으로 값 설정 (예: --set users.0.name 'John')")
    parser.add_argument("--delete", "-d", type=str, metavar="PATH",
                        help="점 표기법으로 값 삭제")
    parser.add_argument("--search", type=str, metavar="KEY",
                        help="특정 키를 검색하여 경로 출력")
    parser.add_argument("--tree", "-t", action="store_true",
                        help="트리 구조로 출력")
    parser.add_argument("--flatten", "-f", action="store_true",
                        help="평탄화하여 출력")
    parser.add_argument("--compare", "-c", type=str, metavar="FILE2",
                        help="다른 JSON 파일과 비교")
    parser.add_argument("--to-csv", action="store_true",
                        help="CSV로 변환 (배열인 경우)")
    parser.add_argument("--output", "-o", type=str, metavar="FILE",
                        help="결과를 파일로 저장")
    parser.add_argument("--minify", "-m", action="store_true",
                        help="압축된 JSON으로 출력")
    
    args = parser.parse_args()
    
    # 비교 모드
    if args.compare and args.file:
        try:
            nav1 = JsonNavigator.from_file(args.file)
            nav2 = JsonNavigator.from_file(args.compare)
            
            differences = compare_json(nav1.data, nav2.data)
            
            if not differences:
                print("✅ 두 JSON 파일이 동일합니다.")
            else:
                print(f"\n📊 차이점 ({len(differences)}개):")
                print("=" * 60)
                for diff in differences:
                    icon = {"added": "➕", "removed": "➖", "changed": "🔄", "type_change": "🔀"}.get(diff["type"], "❓")
                    print(f"\n{icon} {diff['path']} ({diff['type']})")
                    if diff["old"] is not None:
                        print(f"   이전: {diff['old']}")
                    if diff["new"] is not None:
                        print(f"   이후: {diff['new']}")
            return
        except Exception as e:
            print(f"❌ 오류: {e}")
            return
    
    if not args.file:
        parser.print_help()
        return
    
    try:
        nav = JsonNavigator.from_file(args.file)
        
        # 값 가져오기
        if args.get:
            result = nav.get(args.get)
            if result is None:
                print(f"⚠️ 경로 '{args.get}'에 값이 없습니다.")
            else:
                if isinstance(result, (dict, list)):
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    print(result)
            return
        
        # 값 설정
        if args.set:
            path, value = args.set
            # 값 파싱 시도 (JSON으로)
            try:
                parsed_value = json.loads(value)
            except json.JSONDecodeError:
                parsed_value = value
            
            if nav.set(path, parsed_value):
                print(f"✅ '{path}' 값이 설정되었습니다.")
                if args.output:
                    nav.save(args.output)
                    print(f"📁 저장됨: {args.output}")
                else:
                    nav.save(args.file)
                    print(f"📁 저장됨: {args.file}")
            else:
                print(f"❌ 경로 '{path}'에 값을 설정할 수 없습니다.")
            return
        
        # 값 삭제
        if args.delete:
            if nav.delete(args.delete):
                print(f"✅ '{args.delete}' 값이 삭제되었습니다.")
                if args.output:
                    nav.save(args.output)
                else:
                    nav.save(args.file)
            else:
                print(f"❌ 경로 '{args.delete}'를 삭제할 수 없습니다.")
            return
        
        # 검색
        if args.search:
            results = nav.search(args.search)
            if results:
                print(f"\n🔍 '{args.search}' 검색 결과 ({len(results)}개):")
                print("-" * 40)
                for path in results:
                    value = nav.get(path)
                    print(f"  • {path}: {value}")
            else:
                print(f"⚠️ '{args.search}' 키를 찾을 수 없습니다.")
            return
        
        # 트리 출력
        if args.tree:
            print(f"\n🌳 JSON 구조: {args.file}")
            print("=" * 40)
            print_json_tree(nav.data)
            return
        
        # 평탄화
        if args.flatten:
            flat = nav.flatten()
            print(json.dumps(flat, indent=2, ensure_ascii=False))
            return
        
        # CSV 변환
        if args.to_csv:
            if isinstance(nav.data, list):
                csv_output = json_to_csv(nav.data)
                print(csv_output)
                if args.output:
                    with open(args.output, "w", encoding="utf-8") as f:
                        f.write(csv_output)
                    print(f"\n📁 저장됨: {args.output}")
            else:
                print("❌ CSV 변환은 배열 형식의 JSON만 가능합니다.")
            return
        
        # 기본: JSON 출력
        indent = None if args.minify else 2
        print(nav.to_json(indent=indent))
        
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {args.file}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 오류: {e}")
    except Exception as e:
        print(f"❌ 오류: {e}")


if __name__ == "__main__":
    main()


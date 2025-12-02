#!/usr/bin/env python3
"""
calculator.py - 고급 CLI 계산기

기본 사칙연산부터 과학 계산, 단위 변환까지 지원하는 계산기입니다.
"""

import math
import argparse
import re
from typing import Union, Optional, Callable, Dict
from dataclasses import dataclass
from enum import Enum


class UnitCategory(Enum):
    """단위 카테고리"""
    LENGTH = "길이"
    WEIGHT = "무게"
    TEMPERATURE = "온도"
    DATA = "데이터"
    TIME = "시간"
    AREA = "면적"


@dataclass
class ConversionUnit:
    """단위 변환 정보"""
    name: str
    symbol: str
    to_base: float  # 기본 단위로 변환하는 비율
    category: UnitCategory


class Calculator:
    """
    고급 계산기 클래스
    
    사칙연산, 과학 계산, 표현식 평가 등을 지원합니다.
    """
    
    def __init__(self):
        self.memory: float = 0
        self.last_result: Optional[float] = None
        self.history: list = []
    
    # 기본 연산
    @staticmethod
    def add(a: float, b: float) -> float:
        """덧셈"""
        return a + b
    
    @staticmethod
    def subtract(a: float, b: float) -> float:
        """뺄셈"""
        return a - b
    
    @staticmethod
    def multiply(a: float, b: float) -> float:
        """곱셈"""
        return a * b
    
    @staticmethod
    def divide(a: float, b: float) -> float:
        """나눗셈"""
        if b == 0:
            raise ValueError("0으로 나눌 수 없습니다")
        return a / b
    
    @staticmethod
    def power(base: float, exp: float) -> float:
        """거듭제곱"""
        return math.pow(base, exp)
    
    @staticmethod
    def sqrt(n: float) -> float:
        """제곱근"""
        if n < 0:
            raise ValueError("음수의 제곱근은 계산할 수 없습니다")
        return math.sqrt(n)
    
    @staticmethod
    def modulo(a: float, b: float) -> float:
        """나머지"""
        if b == 0:
            raise ValueError("0으로 나눌 수 없습니다")
        return a % b
    
    # 과학 계산
    @staticmethod
    def factorial(n: int) -> int:
        """팩토리얼"""
        if n < 0:
            raise ValueError("음수의 팩토리얼은 정의되지 않습니다")
        return math.factorial(int(n))
    
    @staticmethod
    def log(n: float, base: float = math.e) -> float:
        """로그"""
        if n <= 0:
            raise ValueError("로그의 진수는 양수여야 합니다")
        return math.log(n, base)
    
    @staticmethod
    def log10(n: float) -> float:
        """상용로그"""
        if n <= 0:
            raise ValueError("로그의 진수는 양수여야 합니다")
        return math.log10(n)
    
    @staticmethod
    def sin(angle: float, degrees: bool = True) -> float:
        """사인"""
        if degrees:
            angle = math.radians(angle)
        return math.sin(angle)
    
    @staticmethod
    def cos(angle: float, degrees: bool = True) -> float:
        """코사인"""
        if degrees:
            angle = math.radians(angle)
        return math.cos(angle)
    
    @staticmethod
    def tan(angle: float, degrees: bool = True) -> float:
        """탄젠트"""
        if degrees:
            angle = math.radians(angle)
        return math.tan(angle)
    
    # 통계 계산
    @staticmethod
    def mean(numbers: list) -> float:
        """평균"""
        if not numbers:
            raise ValueError("빈 리스트의 평균은 계산할 수 없습니다")
        return sum(numbers) / len(numbers)
    
    @staticmethod
    def median(numbers: list) -> float:
        """중앙값"""
        if not numbers:
            raise ValueError("빈 리스트의 중앙값은 계산할 수 없습니다")
        sorted_nums = sorted(numbers)
        n = len(sorted_nums)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_nums[mid - 1] + sorted_nums[mid]) / 2
        return sorted_nums[mid]
    
    @staticmethod
    def std_dev(numbers: list) -> float:
        """표준편차"""
        if len(numbers) < 2:
            raise ValueError("표준편차를 계산하려면 최소 2개의 값이 필요합니다")
        mean = Calculator.mean(numbers)
        variance = sum((x - mean) ** 2 for x in numbers) / (len(numbers) - 1)
        return math.sqrt(variance)
    
    @staticmethod
    def gcd(a: int, b: int) -> int:
        """최대공약수"""
        return math.gcd(int(a), int(b))
    
    @staticmethod
    def lcm(a: int, b: int) -> int:
        """최소공배수"""
        return abs(int(a) * int(b)) // math.gcd(int(a), int(b))
    
    # 금융 계산
    @staticmethod
    def compound_interest(principal: float, rate: float, years: int, 
                          compounds_per_year: int = 12) -> float:
        """복리 이자 계산"""
        return principal * (1 + rate / compounds_per_year) ** (compounds_per_year * years)
    
    @staticmethod
    def loan_payment(principal: float, annual_rate: float, years: int) -> float:
        """대출 월 상환금 계산"""
        monthly_rate = annual_rate / 12
        months = years * 12
        if monthly_rate == 0:
            return principal / months
        return principal * (monthly_rate * (1 + monthly_rate) ** months) / \
               ((1 + monthly_rate) ** months - 1)
    
    def evaluate(self, expression: str) -> float:
        """
        수식 문자열을 평가합니다.
        
        안전한 평가를 위해 제한된 함수만 허용합니다.
        """
        # 허용된 이름들
        allowed_names = {
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "pow": pow,
            "sqrt": math.sqrt,
            "sin": lambda x: math.sin(math.radians(x)),
            "cos": lambda x: math.cos(math.radians(x)),
            "tan": lambda x: math.tan(math.radians(x)),
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "floor": math.floor,
            "ceil": math.ceil,
            "pi": math.pi,
            "e": math.e,
            "ans": self.last_result if self.last_result is not None else 0,
        }
        
        # ^ 를 ** 로 변환
        expression = expression.replace("^", "**")
        
        try:
            # 안전한 평가
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            self.last_result = result
            self.history.append((expression, result))
            return result
        except Exception as e:
            raise ValueError(f"수식 평가 오류: {e}")
    
    # 메모리 기능
    def memory_store(self, value: float) -> None:
        """메모리에 값 저장"""
        self.memory = value
    
    def memory_recall(self) -> float:
        """메모리 값 불러오기"""
        return self.memory
    
    def memory_add(self, value: float) -> None:
        """메모리에 값 더하기"""
        self.memory += value
    
    def memory_clear(self) -> None:
        """메모리 초기화"""
        self.memory = 0


class UnitConverter:
    """단위 변환기"""
    
    # 길이 단위 (미터 기준)
    LENGTH_UNITS = {
        "mm": 0.001, "cm": 0.01, "m": 1, "km": 1000,
        "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mi": 1609.344,
    }
    
    # 무게 단위 (그램 기준)
    WEIGHT_UNITS = {
        "mg": 0.001, "g": 1, "kg": 1000, "ton": 1000000,
        "oz": 28.3495, "lb": 453.592,
    }
    
    # 데이터 단위 (바이트 기준)
    DATA_UNITS = {
        "b": 1, "kb": 1024, "mb": 1024**2, "gb": 1024**3, "tb": 1024**4,
    }
    
    # 시간 단위 (초 기준)
    TIME_UNITS = {
        "ms": 0.001, "s": 1, "min": 60, "h": 3600, 
        "day": 86400, "week": 604800, "year": 31536000,
    }
    
    # 면적 단위 (제곱미터 기준)
    AREA_UNITS = {
        "mm2": 0.000001, "cm2": 0.0001, "m2": 1, "km2": 1000000,
        "평": 3.305785, "acre": 4046.86, "ha": 10000,
    }
    
    @classmethod
    def convert_length(cls, value: float, from_unit: str, to_unit: str) -> float:
        """길이 변환"""
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        if from_unit not in cls.LENGTH_UNITS or to_unit not in cls.LENGTH_UNITS:
            raise ValueError(f"알 수 없는 단위입니다. 지원: {list(cls.LENGTH_UNITS.keys())}")
        
        # 미터로 변환 후 목표 단위로 변환
        meters = value * cls.LENGTH_UNITS[from_unit]
        return meters / cls.LENGTH_UNITS[to_unit]
    
    @classmethod
    def convert_weight(cls, value: float, from_unit: str, to_unit: str) -> float:
        """무게 변환"""
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        if from_unit not in cls.WEIGHT_UNITS or to_unit not in cls.WEIGHT_UNITS:
            raise ValueError(f"알 수 없는 단위입니다. 지원: {list(cls.WEIGHT_UNITS.keys())}")
        
        grams = value * cls.WEIGHT_UNITS[from_unit]
        return grams / cls.WEIGHT_UNITS[to_unit]
    
    @classmethod
    def convert_data(cls, value: float, from_unit: str, to_unit: str) -> float:
        """데이터 용량 변환"""
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        if from_unit not in cls.DATA_UNITS or to_unit not in cls.DATA_UNITS:
            raise ValueError(f"알 수 없는 단위입니다. 지원: {list(cls.DATA_UNITS.keys())}")
        
        bytes_val = value * cls.DATA_UNITS[from_unit]
        return bytes_val / cls.DATA_UNITS[to_unit]
    
    @classmethod
    def convert_time(cls, value: float, from_unit: str, to_unit: str) -> float:
        """시간 변환"""
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        if from_unit not in cls.TIME_UNITS or to_unit not in cls.TIME_UNITS:
            raise ValueError(f"알 수 없는 단위입니다. 지원: {list(cls.TIME_UNITS.keys())}")
        
        seconds = value * cls.TIME_UNITS[from_unit]
        return seconds / cls.TIME_UNITS[to_unit]
    
    @classmethod
    def convert_temperature(cls, value: float, from_unit: str, to_unit: str) -> float:
        """온도 변환"""
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        # 먼저 섭씨로 변환
        if from_unit == "c":
            celsius = value
        elif from_unit == "f":
            celsius = (value - 32) * 5 / 9
        elif from_unit == "k":
            celsius = value - 273.15
        else:
            raise ValueError("지원 단위: c (섭씨), f (화씨), k (켈빈)")
        
        # 목표 단위로 변환
        if to_unit == "c":
            return celsius
        elif to_unit == "f":
            return celsius * 9 / 5 + 32
        elif to_unit == "k":
            return celsius + 273.15
        else:
            raise ValueError("지원 단위: c (섭씨), f (화씨), k (켈빈)")
    
    @classmethod
    def convert_area(cls, value: float, from_unit: str, to_unit: str) -> float:
        """면적 변환"""
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        if from_unit not in cls.AREA_UNITS or to_unit not in cls.AREA_UNITS:
            raise ValueError(f"알 수 없는 단위입니다. 지원: {list(cls.AREA_UNITS.keys())}")
        
        sqm = value * cls.AREA_UNITS[from_unit]
        return sqm / cls.AREA_UNITS[to_unit]


def interactive_mode(calc: Calculator):
    """대화형 계산기 모드"""
    print("\n" + "=" * 50)
    print("🧮 대화형 계산기")
    print("=" * 50)
    print("수식을 입력하세요. 종료하려면 'quit' 또는 'exit' 입력")
    print("도움말: 'help' 입력")
    print("-" * 50)
    
    while True:
        try:
            expr = input("\n> ").strip()
            
            if not expr:
                continue
            
            if expr.lower() in ["quit", "exit", "q"]:
                print("👋 계산기를 종료합니다.")
                break
            
            if expr.lower() == "help":
                print("""
📖 사용 가능한 기능:
  • 기본 연산: +, -, *, /, ** (거듭제곱), % (나머지)
  • 함수: sqrt, sin, cos, tan, log, log10, exp, abs, round, floor, ceil
  • 상수: pi, e
  • ans: 마지막 결과
  
📐 예시:
  2 + 3 * 4
  sqrt(16)
  sin(45)
  log10(100)
  2 ** 10
  ans * 2 (마지막 결과에 2를 곱함)
                """)
                continue
            
            if expr.lower() == "history":
                if calc.history:
                    print("\n📜 계산 기록:")
                    for i, (exp, res) in enumerate(calc.history[-10:], 1):
                        print(f"  {i}. {exp} = {res}")
                else:
                    print("기록이 없습니다.")
                continue
            
            result = calc.evaluate(expr)
            
            # 결과 포맷팅
            if isinstance(result, float):
                if result == int(result):
                    print(f"= {int(result)}")
                else:
                    print(f"= {result:.10g}")
            else:
                print(f"= {result}")
                
        except ValueError as e:
            print(f"❌ 오류: {e}")
        except KeyboardInterrupt:
            print("\n👋 계산기를 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")


def main():
    """메인 CLI 함수"""
    parser = argparse.ArgumentParser(
        description="🧮 고급 CLI 계산기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python calculator.py "2 + 3 * 4"              # 수식 계산
  python calculator.py -i                        # 대화형 모드
  python calculator.py --convert 100 km mi      # 단위 변환
  python calculator.py --temp 100 c f           # 온도 변환
  python calculator.py --loan 100000000 0.05 30 # 대출 계산
  python calculator.py --stats 1 2 3 4 5        # 통계 계산
        """
    )
    
    parser.add_argument("expression", nargs="?", help="계산할 수식")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="대화형 모드")
    parser.add_argument("--convert", nargs=4, metavar=("VALUE", "FROM", "TO", "TYPE"),
                        help="단위 변환 (TYPE: length, weight, data, time, area)")
    parser.add_argument("--temp", nargs=3, metavar=("VALUE", "FROM", "TO"),
                        help="온도 변환 (c: 섭씨, f: 화씨, k: 켈빈)")
    parser.add_argument("--loan", nargs=3, type=float, 
                        metavar=("PRINCIPAL", "RATE", "YEARS"),
                        help="대출 월 상환금 계산")
    parser.add_argument("--compound", nargs=3, type=float,
                        metavar=("PRINCIPAL", "RATE", "YEARS"),
                        help="복리 이자 계산")
    parser.add_argument("--stats", nargs="+", type=float, metavar="NUMBERS",
                        help="통계 계산 (평균, 중앙값, 표준편차)")
    parser.add_argument("--gcd", nargs=2, type=int, metavar=("A", "B"),
                        help="최대공약수")
    parser.add_argument("--lcm", nargs=2, type=int, metavar=("A", "B"),
                        help="최소공배수")
    
    args = parser.parse_args()
    calc = Calculator()
    
    # 대화형 모드
    if args.interactive:
        interactive_mode(calc)
        return
    
    # 단위 변환
    if args.convert:
        value, from_unit, to_unit, unit_type = args.convert
        value = float(value)
        
        try:
            converter_map = {
                "length": UnitConverter.convert_length,
                "weight": UnitConverter.convert_weight,
                "data": UnitConverter.convert_data,
                "time": UnitConverter.convert_time,
                "area": UnitConverter.convert_area,
            }
            
            if unit_type.lower() not in converter_map:
                print(f"❌ 알 수 없는 단위 타입: {unit_type}")
                print(f"지원: {list(converter_map.keys())}")
                return
            
            result = converter_map[unit_type.lower()](value, from_unit, to_unit)
            print(f"📐 {value} {from_unit} = {result:.6g} {to_unit}")
        except ValueError as e:
            print(f"❌ {e}")
        return
    
    # 온도 변환
    if args.temp:
        value, from_unit, to_unit = args.temp
        value = float(value)
        
        try:
            result = UnitConverter.convert_temperature(value, from_unit, to_unit)
            unit_names = {"c": "°C", "f": "°F", "k": "K"}
            print(f"🌡️ {value}{unit_names.get(from_unit.lower(), from_unit)} = {result:.2f}{unit_names.get(to_unit.lower(), to_unit)}")
        except ValueError as e:
            print(f"❌ {e}")
        return
    
    # 대출 계산
    if args.loan:
        principal, rate, years = args.loan
        monthly = calc.loan_payment(principal, rate, int(years))
        total = monthly * int(years) * 12
        interest = total - principal
        
        print("\n" + "=" * 50)
        print("🏦 대출 상환 계산")
        print("=" * 50)
        print(f"  대출금: {principal:,.0f}원")
        print(f"  연이율: {rate * 100:.2f}%")
        print(f"  기간: {int(years)}년")
        print("-" * 50)
        print(f"  월 상환금: {monthly:,.0f}원")
        print(f"  총 상환금: {total:,.0f}원")
        print(f"  총 이자: {interest:,.0f}원")
        return
    
    # 복리 계산
    if args.compound:
        principal, rate, years = args.compound
        result = calc.compound_interest(principal, rate, int(years))
        interest = result - principal
        
        print("\n" + "=" * 50)
        print("📈 복리 이자 계산")
        print("=" * 50)
        print(f"  원금: {principal:,.0f}원")
        print(f"  연이율: {rate * 100:.2f}%")
        print(f"  기간: {int(years)}년")
        print("-" * 50)
        print(f"  최종 금액: {result:,.0f}원")
        print(f"  이자: {interest:,.0f}원")
        return
    
    # 통계 계산
    if args.stats:
        numbers = args.stats
        
        print("\n" + "=" * 50)
        print("📊 통계 계산")
        print("=" * 50)
        print(f"  데이터: {numbers}")
        print("-" * 50)
        print(f"  개수: {len(numbers)}")
        print(f"  합계: {sum(numbers):.4g}")
        print(f"  평균: {calc.mean(numbers):.4g}")
        print(f"  중앙값: {calc.median(numbers):.4g}")
        print(f"  최솟값: {min(numbers):.4g}")
        print(f"  최댓값: {max(numbers):.4g}")
        if len(numbers) >= 2:
            print(f"  표준편차: {calc.std_dev(numbers):.4g}")
        return
    
    # 최대공약수
    if args.gcd:
        a, b = args.gcd
        result = calc.gcd(a, b)
        print(f"GCD({a}, {b}) = {result}")
        return
    
    # 최소공배수
    if args.lcm:
        a, b = args.lcm
        result = calc.lcm(a, b)
        print(f"LCM({a}, {b}) = {result}")
        return
    
    # 수식 계산
    if args.expression:
        try:
            result = calc.evaluate(args.expression)
            if isinstance(result, float) and result == int(result):
                print(int(result))
            else:
                print(f"{result:.10g}" if isinstance(result, float) else result)
        except ValueError as e:
            print(f"❌ {e}")
        return
    
    # 인자가 없으면 대화형 모드
    interactive_mode(calc)


if __name__ == "__main__":
    main()


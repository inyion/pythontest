#!/usr/bin/env python3
"""
hello.py - Python 기본 문법 데모

다양한 Python 기본 문법과 기능을 보여주는 예제 모음입니다.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from functools import reduce
import random


def greet(name: str = "World") -> str:
    """
    주어진 이름으로 인사말을 생성합니다.
    
    Args:
        name: 인사할 대상의 이름 (기본값: "World")
    
    Returns:
        포맷된 인사말 문자열
    
    Examples:
        >>> greet("Python")
        'Hello, Python! 👋'
        >>> greet()
        'Hello, World! 👋'
    """
    return f"Hello, {name}! 👋"


@dataclass
class Person:
    """사람을 나타내는 데이터 클래스"""
    name: str
    age: int
    skills: List[str]
    
    def introduce(self) -> str:
        """자기소개를 반환합니다."""
        skills_str = ", ".join(self.skills) if self.skills else "없음"
        return f"안녕하세요! 저는 {self.name}이고, {self.age}살입니다. 제 스킬: {skills_str}"
    
    def add_skill(self, skill: str) -> None:
        """새로운 스킬을 추가합니다."""
        if skill not in self.skills:
            self.skills.append(skill)
            print(f"✅ '{skill}' 스킬이 추가되었습니다!")
        else:
            print(f"⚠️ '{skill}' 스킬은 이미 보유하고 있습니다.")


class Calculator:
    """기본적인 계산 기능을 제공하는 클래스"""
    
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
    def divide(a: float, b: float) -> Optional[float]:
        """나눗셈 (0으로 나눌 경우 None 반환)"""
        if b == 0:
            print("❌ 0으로 나눌 수 없습니다!")
            return None
        return a / b


def demonstrate_list_comprehension() -> None:
    """리스트 컴프리헨션 예제들을 보여줍니다."""
    print("\n📚 리스트 컴프리헨션 데모")
    print("-" * 40)
    
    # 기본 리스트 컴프리헨션
    squares = [x**2 for x in range(1, 11)]
    print(f"1~10의 제곱: {squares}")
    
    # 조건이 있는 리스트 컴프리헨션
    even_squares = [x**2 for x in range(1, 11) if x % 2 == 0]
    print(f"짝수의 제곱: {even_squares}")
    
    # 중첩 리스트 컴프리헨션
    matrix = [[i * j for j in range(1, 4)] for i in range(1, 4)]
    print(f"3x3 곱셈표:\n{matrix}")
    
    # 딕셔너리 컴프리헨션
    word = "python"
    char_positions = {char: idx for idx, char in enumerate(word)}
    print(f"'{word}' 문자 위치: {char_positions}")


def demonstrate_lambda_and_functional() -> None:
    """람다 함수와 함수형 프로그래밍 예제들을 보여줍니다."""
    print("\n🔧 람다 & 함수형 프로그래밍 데모")
    print("-" * 40)
    
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    # map 사용
    doubled = list(map(lambda x: x * 2, numbers))
    print(f"2배로 만들기: {doubled}")
    
    # filter 사용
    evens = list(filter(lambda x: x % 2 == 0, numbers))
    print(f"짝수만 필터링: {evens}")
    
    # reduce 사용
    product = reduce(lambda x, y: x * y, numbers)
    print(f"모든 수의 곱: {product}")
    
    # sorted with key
    words = ["python", "java", "c", "javascript", "go"]
    sorted_by_length = sorted(words, key=lambda x: len(x))
    print(f"길이순 정렬: {sorted_by_length}")


def demonstrate_exception_handling() -> None:
    """예외 처리 예제를 보여줍니다."""
    print("\n⚠️ 예외 처리 데모")
    print("-" * 40)
    
    test_cases = [("10", "2"), ("10", "0"), ("abc", "2")]
    
    for a, b in test_cases:
        try:
            result = int(a) / int(b)
            print(f"{a} / {b} = {result}")
        except ZeroDivisionError:
            print(f"{a} / {b} = ❌ 0으로 나눌 수 없습니다!")
        except ValueError as e:
            print(f"{a} / {b} = ❌ 숫자가 아닙니다! ({e})")
        finally:
            print("  → 계산 시도 완료")


def demonstrate_generators() -> None:
    """제너레이터 예제를 보여줍니다."""
    print("\n🔄 제너레이터 데모")
    print("-" * 40)
    
    def fibonacci(n: int):
        """피보나치 수열 제너레이터"""
        a, b = 0, 1
        count = 0
        while count < n:
            yield a
            a, b = b, a + b
            count += 1
    
    fib_10 = list(fibonacci(10))
    print(f"피보나치 수열 (처음 10개): {fib_10}")
    
    # 제너레이터 표현식
    gen_squares = (x**2 for x in range(5))
    print(f"제곱 제너레이터: {list(gen_squares)}")


def demonstrate_decorators() -> None:
    """데코레이터 예제를 보여줍니다."""
    print("\n🎀 데코레이터 데모")
    print("-" * 40)
    
    def timer_decorator(func):
        """함수 실행 시간을 측정하는 데코레이터"""
        import time
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            print(f"  ⏱️ {func.__name__} 실행 시간: {end - start:.6f}초")
            return result
        return wrapper
    
    @timer_decorator
    def slow_sum(n: int) -> int:
        """1부터 n까지의 합을 계산 (일부러 느리게)"""
        return sum(range(1, n + 1))
    
    result = slow_sum(100000)
    print(f"  결과: 1~100000의 합 = {result}")


def main() -> None:
    """메인 실행 함수"""
    print("=" * 50)
    print("🐍 Python 기본 문법 데모 프로그램")
    print("=" * 50)
    
    # 기본 인사
    print(greet("Python Developer"))
    
    # Person 클래스 데모
    print("\n👤 Person 클래스 데모")
    print("-" * 40)
    developer = Person(
        name="홍길동",
        age=25,
        skills=["Python", "JavaScript"]
    )
    print(developer.introduce())
    developer.add_skill("Docker")
    developer.add_skill("Python")  # 중복 시도
    
    # Calculator 클래스 데모
    print("\n🧮 Calculator 클래스 데모")
    print("-" * 40)
    calc = Calculator()
    print(f"10 + 5 = {calc.add(10, 5)}")
    print(f"10 - 5 = {calc.subtract(10, 5)}")
    print(f"10 × 5 = {calc.multiply(10, 5)}")
    print(f"10 ÷ 5 = {calc.divide(10, 5)}")
    calc.divide(10, 0)  # 예외 상황 테스트
    
    # 각종 데모 실행
    demonstrate_list_comprehension()
    demonstrate_lambda_and_functional()
    demonstrate_exception_handling()
    demonstrate_generators()
    demonstrate_decorators()
    
    print("\n" + "=" * 50)
    print("✨ 모든 데모가 완료되었습니다!")
    print("=" * 50)


if __name__ == "__main__":
    main()

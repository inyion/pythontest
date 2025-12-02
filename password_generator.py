#!/usr/bin/env python3
"""
password_generator.py - 안전한 비밀번호 생성 유틸리티

다양한 옵션으로 안전한 비밀번호를 생성할 수 있는 CLI 도구입니다.
"""

import secrets
import string
import argparse
from typing import Optional
from dataclasses import dataclass


@dataclass
class PasswordConfig:
    """비밀번호 생성 설정"""
    length: int = 16
    use_uppercase: bool = True
    use_lowercase: bool = True
    use_digits: bool = True
    use_special: bool = True
    exclude_ambiguous: bool = False  # l, 1, I, O, 0 등 헷갈리는 문자 제외
    custom_special: Optional[str] = None


class PasswordGenerator:
    """
    안전한 비밀번호를 생성하는 클래스
    
    secrets 모듈을 사용하여 암호학적으로 안전한 난수를 생성합니다.
    """
    
    AMBIGUOUS_CHARS = "l1IO0"
    DEFAULT_SPECIAL = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    def __init__(self, config: Optional[PasswordConfig] = None):
        """
        Args:
            config: 비밀번호 생성 설정 (None이면 기본값 사용)
        """
        self.config = config or PasswordConfig()
        self._build_charset()
    
    def _build_charset(self) -> None:
        """설정에 따라 사용할 문자셋을 구성합니다."""
        charset = ""
        
        if self.config.use_lowercase:
            charset += string.ascii_lowercase
        
        if self.config.use_uppercase:
            charset += string.ascii_uppercase
        
        if self.config.use_digits:
            charset += string.digits
        
        if self.config.use_special:
            special = self.config.custom_special or self.DEFAULT_SPECIAL
            charset += special
        
        if self.config.exclude_ambiguous:
            charset = "".join(c for c in charset if c not in self.AMBIGUOUS_CHARS)
        
        if not charset:
            raise ValueError("최소 하나의 문자 유형을 선택해야 합니다!")
        
        self.charset = charset
    
    def generate(self) -> str:
        """
        설정에 맞는 비밀번호를 생성합니다.
        
        Returns:
            생성된 비밀번호 문자열
        """
        password = "".join(
            secrets.choice(self.charset) 
            for _ in range(self.config.length)
        )
        return password
    
    def generate_multiple(self, count: int = 5) -> list[str]:
        """
        여러 개의 비밀번호를 한 번에 생성합니다.
        
        Args:
            count: 생성할 비밀번호 개수
            
        Returns:
            생성된 비밀번호 리스트
        """
        return [self.generate() for _ in range(count)]
    
    def generate_passphrase(self, word_count: int = 4, separator: str = "-") -> str:
        """
        기억하기 쉬운 패스프레이즈를 생성합니다.
        
        Args:
            word_count: 단어 개수
            separator: 단어 구분자
            
        Returns:
            생성된 패스프레이즈
        """
        # 간단한 단어 목록 (실제로는 더 큰 단어 목록을 사용하는 것이 좋습니다)
        words = [
            "apple", "banana", "cherry", "dragon", "eagle", "forest",
            "galaxy", "harbor", "island", "jungle", "knight", "lemon",
            "mountain", "nebula", "ocean", "phoenix", "quantum", "river",
            "sunset", "thunder", "unicorn", "volcano", "whisper", "xenon",
            "yellow", "zenith", "anchor", "breeze", "castle", "diamond",
            "ember", "falcon", "glacier", "horizon", "ivory", "jasmine",
            "karma", "lantern", "marble", "neptune", "orbit", "puzzle",
            "quartz", "raven", "silver", "tiger", "ultra", "velvet",
            "willow", "xray", "yoga", "zephyr"
        ]
        
        selected_words = [secrets.choice(words) for _ in range(word_count)]
        # 각 단어의 첫 글자를 대문자로 변환
        selected_words = [word.capitalize() for word in selected_words]
        
        # 마지막에 숫자 추가
        suffix = str(secrets.randbelow(100))
        
        return separator.join(selected_words) + separator + suffix


def check_password_strength(password: str) -> dict:
    """
    비밀번호의 강도를 분석합니다.
    
    Args:
        password: 분석할 비밀번호
        
    Returns:
        강도 분석 결과 딕셔너리
    """
    result = {
        "length": len(password),
        "has_uppercase": any(c.isupper() for c in password),
        "has_lowercase": any(c.islower() for c in password),
        "has_digit": any(c.isdigit() for c in password),
        "has_special": any(c in string.punctuation for c in password),
        "score": 0,
        "rating": ""
    }
    
    # 점수 계산
    score = 0
    
    # 길이 점수
    if result["length"] >= 8:
        score += 1
    if result["length"] >= 12:
        score += 1
    if result["length"] >= 16:
        score += 1
    
    # 문자 유형 점수
    if result["has_uppercase"]:
        score += 1
    if result["has_lowercase"]:
        score += 1
    if result["has_digit"]:
        score += 1
    if result["has_special"]:
        score += 2
    
    result["score"] = score
    
    # 등급 결정
    if score <= 2:
        result["rating"] = "매우 약함 ❌"
    elif score <= 4:
        result["rating"] = "약함 ⚠️"
    elif score <= 6:
        result["rating"] = "보통 🔶"
    elif score <= 8:
        result["rating"] = "강함 ✅"
    else:
        result["rating"] = "매우 강함 🛡️"
    
    return result


def display_password_analysis(password: str) -> None:
    """비밀번호 분석 결과를 보기 좋게 출력합니다."""
    analysis = check_password_strength(password)
    
    print("\n" + "=" * 50)
    print("🔐 비밀번호 강도 분석")
    print("=" * 50)
    print(f"비밀번호: {password}")
    print("-" * 50)
    print(f"길이: {analysis['length']}자")
    print(f"대문자 포함: {'✓' if analysis['has_uppercase'] else '✗'}")
    print(f"소문자 포함: {'✓' if analysis['has_lowercase'] else '✗'}")
    print(f"숫자 포함: {'✓' if analysis['has_digit'] else '✗'}")
    print(f"특수문자 포함: {'✓' if analysis['has_special'] else '✗'}")
    print("-" * 50)
    print(f"점수: {analysis['score']}/9")
    print(f"등급: {analysis['rating']}")
    print("=" * 50)


def main():
    """메인 CLI 함수"""
    parser = argparse.ArgumentParser(
        description="🔐 안전한 비밀번호 생성기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python password_generator.py                    # 기본 16자 비밀번호 생성
  python password_generator.py -l 24              # 24자 비밀번호 생성
  python password_generator.py -n 10              # 10개 비밀번호 생성
  python password_generator.py --no-special       # 특수문자 제외
  python password_generator.py --passphrase       # 패스프레이즈 생성
  python password_generator.py --analyze "pw123"  # 비밀번호 강도 분석
        """
    )
    
    parser.add_argument("-l", "--length", type=int, default=16,
                        help="비밀번호 길이 (기본값: 16)")
    parser.add_argument("-n", "--count", type=int, default=1,
                        help="생성할 비밀번호 개수 (기본값: 1)")
    parser.add_argument("--no-upper", action="store_true",
                        help="대문자 제외")
    parser.add_argument("--no-lower", action="store_true",
                        help="소문자 제외")
    parser.add_argument("--no-digits", action="store_true",
                        help="숫자 제외")
    parser.add_argument("--no-special", action="store_true",
                        help="특수문자 제외")
    parser.add_argument("--exclude-ambiguous", action="store_true",
                        help="헷갈리는 문자 제외 (l, 1, I, O, 0)")
    parser.add_argument("--passphrase", action="store_true",
                        help="패스프레이즈 모드 (기억하기 쉬운 단어 조합)")
    parser.add_argument("--words", type=int, default=4,
                        help="패스프레이즈 단어 수 (기본값: 4)")
    parser.add_argument("--analyze", type=str, metavar="PASSWORD",
                        help="비밀번호 강도 분석")
    
    args = parser.parse_args()
    
    # 비밀번호 분석 모드
    if args.analyze:
        display_password_analysis(args.analyze)
        return
    
    # 패스프레이즈 모드
    if args.passphrase:
        generator = PasswordGenerator()
        print("\n🔑 생성된 패스프레이즈:")
        print("-" * 40)
        for i in range(args.count):
            passphrase = generator.generate_passphrase(word_count=args.words)
            print(f"  {i + 1}. {passphrase}")
            display_password_analysis(passphrase)
        return
    
    # 일반 비밀번호 생성
    config = PasswordConfig(
        length=args.length,
        use_uppercase=not args.no_upper,
        use_lowercase=not args.no_lower,
        use_digits=not args.no_digits,
        use_special=not args.no_special,
        exclude_ambiguous=args.exclude_ambiguous
    )
    
    try:
        generator = PasswordGenerator(config)
    except ValueError as e:
        print(f"❌ 오류: {e}")
        return
    
    print("\n🔑 생성된 비밀번호:")
    print("-" * 40)
    
    passwords = generator.generate_multiple(args.count)
    for i, password in enumerate(passwords, 1):
        print(f"  {i}. {password}")
    
    # 첫 번째 비밀번호 분석 결과 표시
    if passwords:
        display_password_analysis(passwords[0])


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
date_utils.py - 날짜/시간 관련 유틸리티

날짜 계산, 변환, 포맷팅 등 다양한 날짜/시간 관련 기능을 제공합니다.
"""

import argparse
from datetime import datetime, timedelta, date
from typing import Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum
import calendar
import re


class DateFormat(Enum):
    """지원하는 날짜 포맷"""
    ISO = "%Y-%m-%d"
    ISO_TIME = "%Y-%m-%d %H:%M:%S"
    KOREAN = "%Y년 %m월 %d일"
    KOREAN_TIME = "%Y년 %m월 %d일 %H시 %M분 %S초"
    US = "%m/%d/%Y"
    EU = "%d/%m/%Y"
    COMPACT = "%Y%m%d"
    FULL = "%A, %B %d, %Y"


@dataclass
class DateDiff:
    """두 날짜 간의 차이를 나타내는 데이터 클래스"""
    years: int
    months: int
    days: int
    total_days: int
    
    def __str__(self) -> str:
        parts = []
        if self.years > 0:
            parts.append(f"{self.years}년")
        if self.months > 0:
            parts.append(f"{self.months}개월")
        if self.days > 0:
            parts.append(f"{self.days}일")
        return " ".join(parts) if parts else "0일"


class DateUtils:
    """날짜/시간 유틸리티 클래스"""
    
    # 한국 공휴일 (고정 공휴일만 - 실제로는 API를 사용하는 것이 좋습니다)
    KOREAN_HOLIDAYS = {
        (1, 1): "신정",
        (3, 1): "삼일절",
        (5, 5): "어린이날",
        (6, 6): "현충일",
        (8, 15): "광복절",
        (10, 3): "개천절",
        (10, 9): "한글날",
        (12, 25): "크리스마스",
    }
    
    @staticmethod
    def parse_date(date_string: str) -> Optional[datetime]:
        """
        다양한 형식의 날짜 문자열을 파싱합니다.
        
        지원 형식:
        - 2024-01-15
        - 2024/01/15
        - 20240115
        - 2024.01.15
        - 15-01-2024
        - Jan 15, 2024
        """
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y%m%d",
            "%Y.%m.%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%b %d, %Y",
            "%B %d, %Y",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def format_date(dt: datetime, format_type: DateFormat = DateFormat.ISO) -> str:
        """날짜를 지정된 형식으로 포맷합니다."""
        return dt.strftime(format_type.value)
    
    @staticmethod
    def get_date_diff(date1: datetime, date2: datetime) -> DateDiff:
        """두 날짜 간의 차이를 계산합니다."""
        if date1 > date2:
            date1, date2 = date2, date1
        
        total_days = (date2 - date1).days
        
        # 년, 월, 일 계산
        years = date2.year - date1.year
        months = date2.month - date1.month
        days = date2.day - date1.day
        
        if days < 0:
            months -= 1
            # 이전 달의 마지막 날 계산
            if date2.month == 1:
                prev_month_days = calendar.monthrange(date2.year - 1, 12)[1]
            else:
                prev_month_days = calendar.monthrange(date2.year, date2.month - 1)[1]
            days += prev_month_days
        
        if months < 0:
            years -= 1
            months += 12
        
        return DateDiff(years=years, months=months, days=days, total_days=total_days)
    
    @staticmethod
    def add_time(dt: datetime, 
                 years: int = 0, 
                 months: int = 0, 
                 days: int = 0,
                 hours: int = 0,
                 minutes: int = 0,
                 seconds: int = 0) -> datetime:
        """날짜/시간에 지정된 값을 더합니다."""
        # 년, 월 더하기
        new_year = dt.year + years
        new_month = dt.month + months
        
        while new_month > 12:
            new_month -= 12
            new_year += 1
        while new_month < 1:
            new_month += 12
            new_year -= 1
        
        # 해당 월의 마지막 날 확인
        max_day = calendar.monthrange(new_year, new_month)[1]
        new_day = min(dt.day, max_day)
        
        result = dt.replace(year=new_year, month=new_month, day=new_day)
        
        # 일, 시, 분, 초 더하기
        result += timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        
        return result
    
    @staticmethod
    def get_age(birth_date: datetime, reference_date: Optional[datetime] = None) -> int:
        """생년월일로 나이를 계산합니다."""
        if reference_date is None:
            reference_date = datetime.now()
        
        age = reference_date.year - birth_date.year
        
        # 생일이 아직 안 지났으면 1 빼기
        if (reference_date.month, reference_date.day) < (birth_date.month, birth_date.day):
            age -= 1
        
        return age
    
    @staticmethod
    def get_korean_age(birth_date: datetime, reference_date: Optional[datetime] = None) -> int:
        """한국식 나이를 계산합니다 (태어난 해 1살, 새해마다 +1)."""
        if reference_date is None:
            reference_date = datetime.now()
        
        return reference_date.year - birth_date.year + 1
    
    @staticmethod
    def is_weekend(dt: datetime) -> bool:
        """주말인지 확인합니다."""
        return dt.weekday() >= 5
    
    @staticmethod
    def is_holiday(dt: datetime) -> Tuple[bool, Optional[str]]:
        """공휴일인지 확인합니다 (한국 고정 공휴일 기준)."""
        key = (dt.month, dt.day)
        if key in DateUtils.KOREAN_HOLIDAYS:
            return True, DateUtils.KOREAN_HOLIDAYS[key]
        return False, None
    
    @staticmethod
    def get_workdays(start_date: datetime, end_date: datetime) -> int:
        """두 날짜 사이의 근무일 수를 계산합니다 (주말 제외)."""
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        
        workdays = 0
        current = start_date
        
        while current <= end_date:
            if not DateUtils.is_weekend(current):
                workdays += 1
            current += timedelta(days=1)
        
        return workdays
    
    @staticmethod
    def get_month_calendar(year: int, month: int) -> str:
        """해당 월의 달력을 문자열로 반환합니다."""
        return calendar.month(year, month)
    
    @staticmethod
    def get_week_number(dt: datetime) -> int:
        """해당 날짜가 몇 번째 주인지 반환합니다."""
        return dt.isocalendar()[1]
    
    @staticmethod
    def get_quarter(dt: datetime) -> int:
        """해당 날짜의 분기를 반환합니다."""
        return (dt.month - 1) // 3 + 1
    
    @staticmethod
    def get_days_in_month(year: int, month: int) -> int:
        """해당 월의 일 수를 반환합니다."""
        return calendar.monthrange(year, month)[1]
    
    @staticmethod
    def get_first_and_last_of_month(dt: datetime) -> Tuple[datetime, datetime]:
        """해당 월의 첫째 날과 마지막 날을 반환합니다."""
        first = dt.replace(day=1)
        last_day = calendar.monthrange(dt.year, dt.month)[1]
        last = dt.replace(day=last_day)
        return first, last
    
    @staticmethod
    def get_relative_date_string(dt: datetime, reference: Optional[datetime] = None) -> str:
        """상대적인 날짜 표현을 반환합니다 (예: '3일 전', '2시간 후')."""
        if reference is None:
            reference = datetime.now()
        
        diff = dt - reference
        total_seconds = diff.total_seconds()
        
        if abs(total_seconds) < 60:
            return "방금 전" if total_seconds < 0 else "곧"
        
        minutes = abs(total_seconds) / 60
        if minutes < 60:
            word = "전" if total_seconds < 0 else "후"
            return f"{int(minutes)}분 {word}"
        
        hours = minutes / 60
        if hours < 24:
            word = "전" if total_seconds < 0 else "후"
            return f"{int(hours)}시간 {word}"
        
        days = hours / 24
        if days < 7:
            word = "전" if total_seconds < 0 else "후"
            return f"{int(days)}일 {word}"
        
        weeks = days / 7
        if weeks < 4:
            word = "전" if total_seconds < 0 else "후"
            return f"{int(weeks)}주 {word}"
        
        months = days / 30
        if months < 12:
            word = "전" if total_seconds < 0 else "후"
            return f"{int(months)}개월 {word}"
        
        years = days / 365
        word = "전" if total_seconds < 0 else "후"
        return f"{int(years)}년 {word}"


def print_date_info(dt: datetime) -> None:
    """날짜에 대한 다양한 정보를 출력합니다."""
    print("\n" + "=" * 50)
    print(f"📅 날짜 정보: {DateUtils.format_date(dt, DateFormat.KOREAN)}")
    print("=" * 50)
    
    print("\n📋 다양한 형식:")
    print("-" * 40)
    for fmt in DateFormat:
        try:
            formatted = DateUtils.format_date(dt, fmt)
            print(f"  {fmt.name:12}: {formatted}")
        except Exception:
            pass
    
    print(f"\n📊 추가 정보:")
    print("-" * 40)
    print(f"  요일: {dt.strftime('%A')} ({['월', '화', '수', '목', '금', '토', '일'][dt.weekday()]}요일)")
    print(f"  올해 {dt.timetuple().tm_yday}번째 날")
    print(f"  {DateUtils.get_week_number(dt)}번째 주")
    print(f"  {DateUtils.get_quarter(dt)}분기")
    print(f"  주말: {'예 🏖️' if DateUtils.is_weekend(dt) else '아니오 💼'}")
    
    is_holiday, holiday_name = DateUtils.is_holiday(dt)
    if is_holiday:
        print(f"  공휴일: {holiday_name} 🎉")
    
    # 오늘과의 차이
    today = datetime.now()
    if dt.date() != today.date():
        relative = DateUtils.get_relative_date_string(dt)
        print(f"  오늘 기준: {relative}")


def print_diff_result(date1: datetime, date2: datetime) -> None:
    """두 날짜의 차이를 출력합니다."""
    diff = DateUtils.get_date_diff(date1, date2)
    
    print("\n" + "=" * 50)
    print("📅 날짜 차이 계산")
    print("=" * 50)
    print(f"  시작: {DateUtils.format_date(date1, DateFormat.KOREAN)}")
    print(f"  종료: {DateUtils.format_date(date2, DateFormat.KOREAN)}")
    print("-" * 40)
    print(f"  차이: {diff}")
    print(f"  총 일수: {diff.total_days}일")
    print(f"  근무일: {DateUtils.get_workdays(date1, date2)}일 (주말 제외)")


def main():
    """메인 CLI 함수"""
    parser = argparse.ArgumentParser(
        description="📅 날짜/시간 유틸리티",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python date_utils.py                           # 오늘 날짜 정보
  python date_utils.py 2024-01-15               # 특정 날짜 정보
  python date_utils.py --diff 2024-01-01 2024-12-31  # 날짜 차이 계산
  python date_utils.py --age 1990-05-15         # 나이 계산
  python date_utils.py --add 30d                # 30일 후
  python date_utils.py --calendar 2024 12       # 2024년 12월 달력
  python date_utils.py --workdays 2024-01-01 2024-01-31  # 근무일 계산
        """
    )
    
    parser.add_argument("date", nargs="?", default=None,
                        help="날짜 (다양한 형식 지원, 기본값: 오늘)")
    parser.add_argument("--diff", "-d", nargs=2, metavar=("DATE1", "DATE2"),
                        help="두 날짜 간의 차이 계산")
    parser.add_argument("--age", "-a", type=str, metavar="BIRTHDATE",
                        help="생년월일로 나이 계산")
    parser.add_argument("--add", type=str, metavar="DURATION",
                        help="날짜에 기간 더하기 (예: 30d, 2m, 1y)")
    parser.add_argument("--calendar", "-c", nargs=2, type=int, metavar=("YEAR", "MONTH"),
                        help="해당 월의 달력 출력")
    parser.add_argument("--workdays", "-w", nargs=2, metavar=("START", "END"),
                        help="근무일 수 계산")
    parser.add_argument("--format", "-f", type=str, 
                        choices=[f.name.lower() for f in DateFormat],
                        help="출력 형식")
    
    args = parser.parse_args()
    
    # 달력 출력
    if args.calendar:
        year, month = args.calendar
        print(f"\n📅 {year}년 {month}월")
        print(DateUtils.get_month_calendar(year, month))
        return
    
    # 두 날짜 차이 계산
    if args.diff:
        date1 = DateUtils.parse_date(args.diff[0])
        date2 = DateUtils.parse_date(args.diff[1])
        
        if date1 and date2:
            print_diff_result(date1, date2)
        else:
            print("❌ 날짜 형식을 인식할 수 없습니다.")
        return
    
    # 나이 계산
    if args.age:
        birth_date = DateUtils.parse_date(args.age)
        if birth_date:
            age = DateUtils.get_age(birth_date)
            korean_age = DateUtils.get_korean_age(birth_date)
            
            print("\n" + "=" * 50)
            print("🎂 나이 계산")
            print("=" * 50)
            print(f"  생년월일: {DateUtils.format_date(birth_date, DateFormat.KOREAN)}")
            print(f"  만 나이: {age}세")
            print(f"  한국 나이: {korean_age}세")
            
            # 다음 생일까지
            today = datetime.now()
            next_birthday = birth_date.replace(year=today.year)
            if next_birthday < today:
                next_birthday = next_birthday.replace(year=today.year + 1)
            
            days_until = (next_birthday - today).days
            print(f"  다음 생일까지: {days_until}일")
        else:
            print("❌ 날짜 형식을 인식할 수 없습니다.")
        return
    
    # 근무일 계산
    if args.workdays:
        start = DateUtils.parse_date(args.workdays[0])
        end = DateUtils.parse_date(args.workdays[1])
        
        if start and end:
            workdays = DateUtils.get_workdays(start, end)
            total_days = abs((end - start).days) + 1
            weekends = total_days - workdays
            
            print("\n" + "=" * 50)
            print("💼 근무일 계산")
            print("=" * 50)
            print(f"  기간: {DateUtils.format_date(start, DateFormat.ISO)} ~ {DateUtils.format_date(end, DateFormat.ISO)}")
            print(f"  총 일수: {total_days}일")
            print(f"  근무일: {workdays}일")
            print(f"  주말: {weekends}일")
        else:
            print("❌ 날짜 형식을 인식할 수 없습니다.")
        return
    
    # 기준 날짜 파싱
    if args.date:
        base_date = DateUtils.parse_date(args.date)
        if not base_date:
            print(f"❌ 날짜 형식을 인식할 수 없습니다: {args.date}")
            return
    else:
        base_date = datetime.now()
    
    # 기간 더하기
    if args.add:
        pattern = r"(\d+)([ymdhms])"
        matches = re.findall(pattern, args.add.lower())
        
        if matches:
            kwargs = {}
            for value, unit in matches:
                value = int(value)
                if unit == "y":
                    kwargs["years"] = value
                elif unit == "m":
                    kwargs["months"] = value
                elif unit == "d":
                    kwargs["days"] = value
                elif unit == "h":
                    kwargs["hours"] = value
            
            result = DateUtils.add_time(base_date, **kwargs)
            
            print("\n" + "=" * 50)
            print("➕ 날짜 계산")
            print("=" * 50)
            print(f"  기준: {DateUtils.format_date(base_date, DateFormat.KOREAN)}")
            print(f"  더하기: {args.add}")
            print(f"  결과: {DateUtils.format_date(result, DateFormat.KOREAN)}")
            return
        else:
            print("❌ 기간 형식을 인식할 수 없습니다. (예: 30d, 2m, 1y)")
            return
    
    # 기본: 날짜 정보 출력
    print_date_info(base_date)


if __name__ == "__main__":
    main()


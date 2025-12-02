# 🐍 Python 유틸리티 모음

다양한 Python 유틸리티 스크립트 모음입니다. 실용적인 CLI 도구들과 Python 기본 문법 예제를 포함하고 있습니다.

## 📁 프로젝트 구조

```
pythontest/
├── hello.py              # Python 기본 문법 데모
├── password_generator.py # 안전한 비밀번호 생성기
├── file_organizer.py     # 파일 정리/분류 유틸리티
├── json_utils.py         # JSON 데이터 처리 도구
├── date_utils.py         # 날짜/시간 유틸리티
├── calculator.py         # 고급 CLI 계산기
├── web_scraper.py        # 웹 스크래핑 유틸리티
├── data_analyzer.py      # 데이터 분석 도구
├── requirements.txt      # 의존성 파일
└── README.md            # 프로젝트 설명
```

## 🚀 시작하기

### 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/pythontest.git
cd pythontest

# 의존성 설치 (선택사항 - 웹 스크래핑 기능 사용 시)
pip install -r requirements.txt
```

### Python 버전

- Python 3.8 이상 권장

## 📚 유틸리티 소개

### 1. 🎯 hello.py - Python 기본 문법 데모

Python의 다양한 기본 문법과 기능을 보여주는 예제 모음입니다.

```bash
python hello.py
```

**포함 내용:**
- 클래스와 데이터클래스
- 데코레이터
- 제너레이터
- 리스트 컴프리헨션
- 람다 함수와 함수형 프로그래밍
- 예외 처리

---

### 2. 🔐 password_generator.py - 비밀번호 생성기

암호학적으로 안전한 비밀번호를 생성합니다.

```bash
# 기본 16자 비밀번호 생성
python password_generator.py

# 24자 비밀번호 5개 생성
python password_generator.py -l 24 -n 5

# 특수문자 제외
python password_generator.py --no-special

# 기억하기 쉬운 패스프레이즈 생성
python password_generator.py --passphrase

# 비밀번호 강도 분석
python password_generator.py --analyze "MyPassword123!"
```

---

### 3. 📂 file_organizer.py - 파일 정리 유틸리티

폴더의 파일들을 확장자별로 자동 분류합니다.

```bash
# Downloads 폴더 정리 미리보기
python file_organizer.py ~/Downloads --preview

# 폴더 통계 보기
python file_organizer.py ~/Downloads --stats

# 실제 정리 실행 (시뮬레이션)
python file_organizer.py ~/Downloads --dry-run

# 다른 폴더로 정리
python file_organizer.py ~/Downloads -d ~/Sorted
```

**분류 카테고리:**
- 📷 Images (jpg, png, gif 등)
- 📹 Videos (mp4, avi, mkv 등)
- 🎵 Audio (mp3, wav, flac 등)
- 📄 Documents (pdf, doc, xls 등)
- 💻 Code (py, js, html 등)
- 📦 Archives (zip, rar, 7z 등)

---

### 4. 🔧 json_utils.py - JSON 유틸리티

JSON 파일의 조회, 수정, 비교, 변환을 수행합니다.

```bash
# JSON 내용 보기
python json_utils.py data.json

# 특정 값 가져오기 (점 표기법)
python json_utils.py data.json --get "users.0.name"

# 트리 구조로 보기
python json_utils.py data.json --tree

# 키 검색
python json_utils.py data.json --search "email"

# 두 JSON 파일 비교
python json_utils.py --compare file1.json file2.json

# JSON 배열을 CSV로 변환
python json_utils.py data.json --to-csv -o output.csv
```

---

### 5. 📅 date_utils.py - 날짜/시간 유틸리티

날짜 계산, 변환, 포맷팅 등 다양한 기능을 제공합니다.

```bash
# 오늘 날짜 정보
python date_utils.py

# 특정 날짜 정보
python date_utils.py 2024-12-25

# 두 날짜 차이 계산
python date_utils.py --diff 2024-01-01 2024-12-31

# 나이 계산
python date_utils.py --age 1990-05-15

# 30일 후 날짜
python date_utils.py --add 30d

# 달력 출력
python date_utils.py --calendar 2024 12

# 근무일 계산
python date_utils.py --workdays 2024-01-01 2024-01-31
```

---

### 6. 🧮 calculator.py - 고급 계산기

사칙연산부터 과학 계산, 단위 변환까지 지원합니다.

```bash
# 수식 계산
python calculator.py "2 + 3 * 4"
python calculator.py "sqrt(16) + sin(45)"

# 대화형 모드
python calculator.py -i

# 단위 변환
python calculator.py --convert 100 km mi length
python calculator.py --temp 100 c f

# 대출 월 상환금 계산
python calculator.py --loan 100000000 0.05 30

# 복리 이자 계산
python calculator.py --compound 10000000 0.05 10

# 통계 계산
python calculator.py --stats 1 2 3 4 5 6 7 8 9 10

# 최대공약수/최소공배수
python calculator.py --gcd 48 18
python calculator.py --lcm 12 18
```

---

### 7. 🌐 web_scraper.py - 웹 스크래핑

웹 페이지에서 데이터를 추출합니다.

```bash
# 기본 스크래핑
python web_scraper.py https://example.com

# 상세 출력
python web_scraper.py https://example.com -v

# 링크만 추출
python web_scraper.py https://example.com --links

# CSS 선택자로 요소 추출
python web_scraper.py https://example.com -s "h1"

# JSON으로 저장
python web_scraper.py https://example.com --json output.json
```

> ⚠️ **주의**: 웹 스크래핑 시 해당 사이트의 robots.txt와 이용약관을 확인하세요.

---

### 8. 📊 data_analyzer.py - 데이터 분석

CSV 파일의 기본적인 데이터 분석을 수행합니다.

```bash
# 데이터 요약
python data_analyzer.py data.csv

# 상세 통계
python data_analyzer.py data.csv --describe

# 처음/마지막 N개 행
python data_analyzer.py data.csv --head 10
python data_analyzer.py data.csv --tail 10

# 특정 열 통계
python data_analyzer.py data.csv --column age

# 필터링
python data_analyzer.py data.csv --filter "age gt 30"

# 그룹화
python data_analyzer.py data.csv --group city --agg salary

# 히스토그램
python data_analyzer.py data.csv --hist age

# 상관계수
python data_analyzer.py data.csv --corr age salary

# 값 빈도
python data_analyzer.py data.csv --value-counts category
```

## 🛠️ 기술 스택

- **Python 3.8+**
- 표준 라이브러리 중심 (의존성 최소화)
  - `argparse`: CLI 인터페이스
  - `dataclasses`: 데이터 구조
  - `typing`: 타입 힌트
  - `pathlib`: 파일 시스템
  - `json`, `csv`: 데이터 포맷
  - `datetime`, `calendar`: 날짜/시간
  - `math`, `secrets`: 수학/암호
- 외부 라이브러리 (선택사항)
  - `requests`: HTTP 요청
  - `beautifulsoup4`: HTML 파싱

## 📝 코드 특징

- **Type Hints**: 모든 함수에 타입 힌트 적용
- **Docstrings**: Google 스타일 문서화
- **데이터 클래스**: 구조화된 데이터 표현
- **CLI 인터페이스**: argparse를 활용한 사용자 친화적 인터페이스
- **예외 처리**: 적절한 에러 핸들링
- **모듈화**: 재사용 가능한 클래스 설계

## 📄 라이선스

MIT License

## 🤝 기여

이슈와 PR 환영합니다!

---

Made with 🐍 Python


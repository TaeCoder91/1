# 🚗 오토픽 (AutoPick) - 해외 매체 종합 자동차 블로그 파이프라인

글로벌 3대 자동차 전문지(MotorTrend, Top Gear, Car and Driver 등)의 실제 시승 평가를 크롤링하고, 모바일 독자와 한국 도로 환경에 최적화된 고품질 티스토리 원고를 생성하는 자동화 파이프라인입니다.

---

## 🌟 주요 특징

1. **Crawl4AI 기반 유연한 크롤링 & 로컬 이미지 영구 보관**:
   - 외부 핫링크 엑스박스(403/404) 방지를 위해 고화질 차량 사진을 로컬(`output/<차량명>/images/`)에 자동 다운로드
   - 이미지 출처(Credit) 태그 및 티스토리 본문 삽입 위치 마커 자동 생성
2. **모바일 퍼스트 서식 (이탈률 방지)**:
   - 상단 **3초 퀵 요약 카드** (결론을 먼저 제시하여 체류시간 증대)
   - 해외 3사 **스코어보드 카드**
   - 만장일치 **장단점(Pros/Cons) 비교표**
   - **한국 시장 관점(K-Angle)** 실용 분석 칼럼
3. **어떤 LLM과도 호환 (Cursor / Gemini / OpenCode / Claude)**:
   - 수집된 원문 데이터와 프롬프트 지침이 담긴 `prompt.md` 자동 생성
4. **티스토리 친화적 2-Way 서식**:
   - **인라인 HTML (`article_tistory.html`)**: 스킨 수정 없이도 에디터 HTML 모드에 붙여넣기만 하면 100% 모바일 반응형 렌더링
   - **전용 스킨 CSS (`tistory_skin/autopick-skin.css`)**: 티스토리 [스킨 편집]에 추가하여 블로그 전체 스타일 고급화

---

## 📂 폴더 구조

```
├── CONTEXT.md                    # 도메인 모델 및 공식 용어 정의
├── docs/adr/                     # 아키텍처 결정 기록 (ADR)
├── tistory_skin/
│   └── autopick-skin.css         # 티스토리 [스킨 편집] > [CSS]에 복사할 전용 스타일
├── src/
│   ├── crawler.py                # Crawl4AI 기반 본문 크롤링 및 이미지 수집기
│   ├── prompt_builder.py         # LLM 합성 프롬프트 생성기
│   └── formatter.py              # 모바일 최적화 HTML/마크다운 렌더러
├── output/
│   └── toyota_rav4/              # 차량별 결과물 저장소
│       ├── images/               # 로컬 다운로드된 고해상도 차량 사진들
│       ├── images_index.md       # 이미지 파일 목록 및 출처 표
│       ├── prompt.md             # 만능 LLM 합성 프롬프트
│       ├── article_tistory.html  # 티스토리에 바로 붙여넣는 완성 원고
│       └── article.md            # 보관용 마크다운 원고
└── run_pipeline.py               # 원클릭 파이프라인 실행 스크립트
```

---

## 🚀 사용 방법

### 1. 파이프라인 실행
원하는 차량 이름으로 파이프라인을 실행합니다:

```bash
python3 run_pipeline.py --car "Toyota RAV4"
```

### 2. 티스토리 발행 (소요 시간: 1분)
1. `output/<차량명>/article_tistory.html` 파일의 내용을 전체 복사합니다.
2. 티스토리 글쓰기 에디터 상단 모드를 **[HTML]**로 변경하고 붙여넣습니다.
3. 본문 내 `📸 [티스토리 사진 첨부 N]` 표시가 된 자리에 `output/<차량명>/images/` 폴더의 로컬 사진을 드래그하여 첨부합니다.
4. 사진 하단 캡션에 출처(예: `출처: MotorTrend`)를 기재하고 **[발행]**을 누릅니다.

---

## 🎨 티스토리 스킨 CSS 영구 등록 방법 (선택 사항)
1. 티스토리 관리자 홈 → 좌측 메뉴 **[스킨 편집]** 클릭
2. 우측 상단 **[html 편집]** 버튼 클릭 → **[CSS]** 탭 선택
3. `tistory_skin/autopick-skin.css` 파일의 전체 내용을 복사하여 **맨 아래에 붙여넣기** 후 [적용] 클릭
"# 1" 
"# 1" 

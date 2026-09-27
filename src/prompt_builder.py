from pathlib import Path
from typing import Dict, Any

def build_synthesis_prompt(crawl_results: Dict[str, Any]) -> str:
    """Cursor, Gemini, OpenCode 등 어떤 LLM에도 바로 복사해 넣을 수 있는 고밀도 엔지니어링 분석 프롬프트 생성"""
    vehicle_name = crawl_results["vehicle_name"]
    downloaded_images = crawl_results.get("downloaded_images", [])
    articles = crawl_results.get("articles", [])
    
    prompt = f"""# [AutoPick (오토픽)] 자동차 전문 엔지니어링 심층 분석 리포트 집필 지침

당신은 자동차 전문 테크니컬 미디어 **'오토픽(AutoPick)'**의 수석 엔지니어이자 전문 저널리스트입니다.
아래에 제공된 **글로벌 3대 자동차 전문지(MotorTrend, Top Gear, Car and Driver)**의 실제 시승 평가 및 실측 데이터를 바탕으로, 피상적인 블로그 요약글을 압도하는 **심층 엔지니어링 분석 리포트**를 작성하십시오.

---

## 1. 필수 집필 원칙 (전문성과 깊이)
1. **순수 마크다운(Pure Markdown) 작성**: 복잡한 인라인 HTML 태그를 사용하지 말고, 티스토리 마크다운 에디터와 완벽히 호환되는 표준 마크다운 문법(`#`, `##`, `| 표 |`, `> 인용구`, `- 리스트`)만 사용하십시오.
2. **실측 계측 데이터 중심 (Instrumented Data)**:
   - 0-100km/h(0-60mph) 가속 시간, 100-0km/h 제동거리, 고속 순항 실내 소음(dBA), 고속도로 정속 실연비 수치를 반드시 표(Table)로 대조 정리하십시오.
3. **파워트레인 & 섀시 기구학 심층 분석**:
   - 엔진의 열효율, 분사 시스템(D-4S 등), 밸브 타이밍, 변속기 기구학(e-CVT 유성기어 세트 vs 다단 자동변속기), 섀시 비틀림 강성, 서스펜션 지오메트리(맥퍼슨 스트럿, 더블 위시본)를 기술적으로 깊이 있게 서술하십시오.
4. **소음 및 NVH의 공학적 원인 규명**:
   - 단순히 "소음이 난다"가 아니라, 변속기 기구적 특성(RPM 고정 드론 노이즈), 휠하우스 흡차음재 수준, 글라스 두께 등을 비교하여 감점 요인을 설득력 있게 밝히십시오.
5. **한국 시장(K-Angle) 대조 분석**:
   - 국내 동급 베스트셀러(예: 스포티지·투싼 하이브리드)와의 시스템 비교(병렬식 1.6T 6AT vs 직병렬 2.5L e-CVT)를 통해 한국 도로와 소비자에게 어떤 차가 맞는지 실용적 해답을 제시하십시오.
6. **로컬 사진 첨부 마커 삽입**:
   - 원고 중간중간 아래 로컬 사진 목록의 마커를 자연스럽게 배치하십시오: `<!-- [사진 N 첨부 위치]: 파일명 (설명 / 출처) -->`

---

## 2. 사용 가능한 로컬 다운로드 이미지 목록
"""
    for img in downloaded_images:
        prompt += f"- [사진 {img['index']}] 파일명: `{img['filename']}` | 설명: {img['alt']} | {img['credit']}\n"
        
    prompt += f"""
---

## 3. 원고 필수 구조 (SEO 최적화 마크다운)
1. **타이틀**: `# [오토픽 심층분석] "핵심 카피" 모델명`
2. **SEO 리드문 (Lead Description)**:
   - **매우 중요**: 티스토리는 본문의 첫 150~250자를 검색엔진 메타 디스크립션(`og:description`)으로 자동 수집합니다.
   - 따라서 글 제목 바로 다음 문단은 **절대로 인용구(`>`), 특수문자, 이모지(📌)로 시작하지 마십시오.**
   - 핵심 타깃 키워드(차량명, 하이브리드, 3대 매체 실측, 연비, 장단점, 국내 경쟁차 비교)가 자연스럽게 포함된 **180~220자의 완성된 평문 단락**을 최상단에 배치하십시오.
3. **`---` (구분선)**
4. **## 1. 글로벌 3대 전문지 실측 테스트 데이터 (테이블 표)**
5. **## 2. 파워트레인 엔지니어링: 열효율과 구동 메커니즘**
6. **## 3. 섀시 & 주행 성능: 플랫폼 강성과 서스펜션 거동 특성**
7. **## 4. 소음 및 NVH 솔직 분석: 해외 3사가 공통으로 감점한 이유**
8. **## 5. 🇰🇷 한국 시장 관점 (K-Angle): 국산 경쟁차와의 엔지니어링 비교**
9. **## 6. 오토픽 최종 평결 (Verdict)**: 추천 대상 및 비추천 대상 명시

---

## 4. 수집된 해외 매체 원문 데이터
"""
    for art in articles:
        prompt += f"\n### [{art['media_name']}] 원문 발췌 ({art['url']})\n\n"
        prompt += art['markdown'] + "\n\n"
        
    return prompt

def save_prompt_to_file(crawl_results: Dict[str, Any]) -> str:
    vehicle_dir = Path(crawl_results["vehicle_dir"])
    prompt_content = build_synthesis_prompt(crawl_results)
    
    prompt_file = vehicle_dir / "prompt.md"
    prompt_file.write_text(prompt_content, encoding="utf-8")
    print(f"[v] 고밀도 테크니컬 합성 프롬프트 생성 완료: {prompt_file}")
    return str(prompt_file)

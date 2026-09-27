import os
import re
import asyncio
from urllib.parse import urljoin, urlparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
import aiohttp
from crawl4ai import AsyncWebCrawler

# 기본 타깃 미디어 (우선순위 높은 글로벌 전문지)
DEFAULT_REVIEW_SOURCES = [
    ("MotorTrend", "https://www.motortrend.com/cars/toyota/rav4/"),
    ("TopGear", "https://www.topgear.com/car-reviews/toyota/rav4"),
    ("CarAndDriver", "https://www.caranddriver.com/toyota/rav4"),
]

def clean_text(markdown_text: str) -> str:
    """잡음성 링크, 네비게이션, 광고 스크립트 제거"""
    lines = markdown_text.splitlines()
    cleaned = []
    skip = False
    for line in lines:
        stripped = line.strip()
        # 광고, 소셜 링크, 푸터 등 필터링
        if any(term in stripped.lower() for term in [
            "cookie policy", "terms of use", "privacy notice", "sign up for newsletter",
            "advertisement", "subscribe to get", "follow us on"
        ]):
            continue
        if len(stripped) == 0 and len(cleaned) > 0 and len(cleaned[-1]) == 0:
            continue
        cleaned.append(line)
    return "\n".join(cleaned)

async def download_image(session: aiohttp.ClientSession, url: str, dest_path: Path) -> bool:
    """이미지 URL을 비동기로 로컬 폴더에 다운로드"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
    }
    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status == 200:
                content = await resp.read()
                # 5KB 이하의 작은 아이콘/추적 픽셀은 제외
                if len(content) > 10240:
                    dest_path.write_bytes(content)
                    return True
    except Exception as e:
        print(f"[!] 이미지 다운로드 실패 ({url}): {e}")
    return False

def select_candidate_images(images: List[Dict[str, Any]], base_url: str, limit: int = 5) -> List[Tuple[str, str]]:
    """고해상도 차량 사진 후보 선별 (URL, Alt)"""
    candidates = []
    seen_urls = set()
    
    for img in images:
        src = img.get("src", "")
        if not src:
            continue
        full_url = urljoin(base_url, src)
        
        # 확장자 및 키워드 검사
        low_url = full_url.lower()
        if any(ext in low_url for ext in [".svg", ".gif", "logo", "icon", "avatar", "author", "tracking", "pixel"]):
            continue
        
        # 고유 URL 유지
        base_clean = full_url.split("?")[0]
        if base_clean in seen_urls:
            continue
        seen_urls.add(base_clean)
        
        # 쿼리 파라미터로 지나치게 작게 리사이즈된 URL은 원본 또는 큰 사이즈로 변환
        if "w=" in full_url:
            full_url = re.sub(r'w=\d+', 'w=1280', full_url)
        if "width=" in full_url:
            full_url = re.sub(r'width=\d+', 'width=1280', full_url)
            
        alt = img.get("alt", "").strip() or "차량 시승 사진"
        candidates.append((full_url, alt))
        if len(candidates) >= limit:
            break
            
    return candidates

async def crawl_and_harvest(
    vehicle_name: str,
    sources: List[Tuple[str, str]],
    output_base_dir: str = "output"
) -> Dict[str, Any]:
    """해외 3사 리뷰 크롤링 및 이미지 로컬 다운로드 실행"""
    slug = re.sub(r'[^a-zA-Z0-9가-힣]+', '_', vehicle_name).strip('_').lower()
    vehicle_dir = Path(output_base_dir) / slug
    images_dir = vehicle_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[*] '{vehicle_name}' 파일롯 크롤링 시작...")
    results = {
        "vehicle_name": vehicle_name,
        "slug": slug,
        "vehicle_dir": str(vehicle_dir),
        "articles": [],
        "downloaded_images": []
    }
    
    image_counter = 1
    
    async with AsyncWebCrawler(verbose=False) as crawler:
        async with aiohttp.ClientSession() as http_session:
            for media_name, url in sources:
                print(f"[+] 크롤링 진행 중: [{media_name}] {url}")
                try:
                    res = await crawler.arun(url=url)
                    if not res.success or not res.markdown:
                        print(f"    [-] 크롤링 실패 또는 본문 없음: {media_name}")
                        continue
                    
                    cleaned_md = clean_text(res.markdown)
                    raw_images = res.media.get("images", []) if res.media else []
                    candidates = select_candidate_images(raw_images, url, limit=3)
                    
                    media_images = []
                    for img_url, alt in candidates:
                        ext = ".jpg"
                        if ".png" in img_url.lower():
                            ext = ".png"
                        elif ".webp" in img_url.lower():
                            ext = ".webp"
                            
                        filename = f"{image_counter:02d}_{media_name.lower()}{ext}"
                        dest = images_dir / filename
                        
                        success = await download_image(http_session, img_url, dest)
                        if success:
                            item = {
                                "index": image_counter,
                                "filename": filename,
                                "local_path": str(dest),
                                "source_media": media_name,
                                "alt": alt,
                                "origin_url": img_url,
                                "credit": f"출처: {media_name} ({urlparse(url).netloc})"
                            }
                            results["downloaded_images"].append(item)
                            media_images.append(item)
                            print(f"    [v] 이미지 다운로드 성공: {filename} ({alt})")
                            image_counter += 1
                    
                    results["articles"].append({
                        "media_name": media_name,
                        "url": url,
                        "markdown": cleaned_md[:12000],  # 핵심 본문 발췌
                        "images": media_images
                    })
                    print(f"    [v] {media_name} 본문 수집 완료 ({len(cleaned_md)}자)")
                    
                except Exception as e:
                    print(f"    [!] 에러 발생 ({media_name}): {e}")
                    
    # 이미지 인덱스 파일 (images_index.md) 생성
    index_md_path = vehicle_dir / "images_index.md"
    with open(index_md_path, "w", encoding="utf-8") as f:
        f.write(f"# {vehicle_name} 수집된 시각 에셋 (로컬 보관소)\n\n")
        f.write("티스토리 글 작성 시 아래 사진들을 해당 위치에 업로드하고 출처를 표기하세요.\n\n")
        f.write("| 번호 | 파일명 | 권장 첨부 위치 및 설명 | 출처 표기 태그 |\n")
        f.write("|---|---|---|---|\n")
        for img in results["downloaded_images"]:
            f.write(f"| {img['index']} | `{img['filename']}` | {img['alt']} | `{img['credit']}` |\n")
            
    print(f"\n[★] 수집 완료: 총 {len(results['articles'])}개 매체 기사, {len(results['downloaded_images'])}장 이미지 로컬 보관 완료!")
    return results

if __name__ == "__main__":
    asyncio.run(crawl_and_harvest("Toyota RAV4", DEFAULT_REVIEW_SOURCES))

import sys
import asyncio
import argparse
from pathlib import Path

from src.crawler import crawl_and_harvest, DEFAULT_REVIEW_SOURCES
from src.prompt_builder import save_prompt_to_file
from src.formatter import save_article_outputs

async def run_pipeline(vehicle_name: str, sources=None):
    if sources is None:
        sources = DEFAULT_REVIEW_SOURCES
        
    print("\n" + "="*60)
    print(f" 🚀 [오토픽 파이프라인] '{vehicle_name}' 원고 생성 시작")
    print("="*60)
    
    # 1. 크롤링 및 이미지 다운로드
    crawl_data = await crawl_and_harvest(vehicle_name, sources)
    
    # 2. 어떤 LLM에서도 쓸 수 있는 완성형 합성 프롬프트 생성
    prompt_path = save_prompt_to_file(crawl_data)
    
    # 3. 티스토리 모바일 최적화 HTML 및 마크다운 원고 생성
    html_path, md_path = save_article_outputs(crawl_data)
    
    print("\n" + "="*60)
    print(" 🎉 [오토픽 파이프라인] 전체 공정 완료!")
    print("="*60)
    print(f"📁 산출물 저장 디렉터리: {crawl_data['vehicle_dir']}")
    print(f" 1. 🖼️ 로컬 이미지 보관소 : {Path(crawl_data['vehicle_dir']) / 'images'} ({len(crawl_data['downloaded_images'])}장)")
    print(f" 2. 📋 이미지 출처 인덱스 : {Path(crawl_data['vehicle_dir']) / 'images_index.md'}")
    print(f" 3. 🤖 만능 LLM 프롬프트 : {prompt_path}")
    print(f" 4. 📝 티스토리용 HTML  : {html_path}")
    print(f" 5. 📄 보관용 마크다운   : {md_path}")
    print("="*60 + "\n")
    return crawl_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="오토픽 블로그 자동화 파이프라인")
    parser.add_argument("--car", type=str, default="Toyota RAV4", help="타깃 차량 이름")
    args = parser.parse_args()
    
    asyncio.run(run_pipeline(args.car))

import os
from datetime import datetime
from typing import List, Dict

import pymysql
import feedparser
from dotenv import load_dotenv

# 🔧 .env 로드 (프로젝트 루트 기준)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

# 🔧 MySQL 설정: .env에서 읽어오기
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
    "charset": "utf8mb4",
}

# 🔧 경제 뉴스 RSS (예시: 연합뉴스TV 경제)
ECON_RSS_URL = "http://www.yonhapnewstv.co.kr/category/news/economy/feed/"


def crawl_economy_news(limit: int = 20) -> List[Dict]:
    """
    경제 뉴스 RSS에서 최신 기사 가져오기
    반환: [{title, url, published_at, source_type, summary}, ...]
    """
    feed = feedparser.parse(ECON_RSS_URL)
    articles: List[Dict] = []

    for entry in feed.entries[:limit]:
        title = (entry.get("title") or "").strip()
        url = (entry.get("link") or "").strip()

        # 날짜 정보 (published / updated 중 하나 사용)
        published = entry.get("published_parsed") or entry.get("updated_parsed")
        if published:
            published_at = datetime(
                published.tm_year,
                published.tm_mon,
                published.tm_mday,
                published.tm_hour,
                published.tm_min,
                published.tm_sec,
            )
        else:
            published_at = None

        summary = entry.get("summary", "")

        articles.append(
            {
                "title": title,
                "url": url,
                "published_at": published_at,
                "source_type": "yonhap_economy_rss",
                "summary": summary,
            }
        )

    return articles


def insert_articles(articles: List[Dict]):
    """
    크롤링한 기사들을 MySQL articles 테이블에 저장
    url 컬럼에 UNIQUE 인덱스가 걸려 있다고 가정 (중복 방지)
    """
    if not articles:
        print("❌ 저장할 기사가 없습니다.")
        return

    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            sql = """
            INSERT INTO articles (title, url, published_at, source_type, summary)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                title = VALUES(title),
                published_at = VALUES(published_at),
                source_type = VALUES(source_type),
                summary = VALUES(summary);
            """
            for a in articles:
                cur.execute(
                    sql,
                    (
                        a["title"],
                        a["url"],
                        a["published_at"],
                        a["source_type"],
                        a["summary"],
                    ),
                )
        conn.commit()
        print(f"✅ {len(articles)}개 기사 저장/업데이트 완료")
    finally:
        conn.close()


if __name__ == "__main__":
    print("📡 경제 뉴스 가져오는 중...")
    news_list = crawl_economy_news(limit=20)

    for n in news_list:
        print(f"- {n['published_at']} | {n['title']}")

    print("\n💾 DB 저장 시작...")
    insert_articles(news_list)
    print("🎉 작업 완료!")

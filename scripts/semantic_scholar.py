#!/usr/bin/env python3
"""
AI人才雷达 - Semantic Scholar API 封装
提供论文搜索、作者搜索、引用数据获取
"""

import requests
import json
import time
from typing import List, Dict, Optional

BASE_URL = "https://api.semanticscholar.org/graph/v1"

class SemanticScholarAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "AI-Talent-Radar/1.0"
        })
    
    def search_papers(self, query: str, fields: List[str] = None, limit: int = 10) -> List[Dict]:
        """搜索论文"""
        if fields is None:
            fields = ["title", "authors", "year", "citationCount", "venue", "abstract"]
        
        url = f"{BASE_URL}/paper/search"
        params = {
            "query": query,
            "fields": ",".join(fields),
            "limit": limit
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            print(f"Semantic Scholar 搜索失败: {e}", file=__import__('sys').stderr)
            return []
    
    def search_authors(self, query: str, fields: List[str] = None, limit: int = 10) -> List[Dict]:
        """搜索作者"""
        if fields is None:
            fields = ["name", "aliases", "affiliations", "homepage", "paperCount", 
                     "citationCount", "hIndex", "papers.title", "papers.year"]
        
        url = f"{BASE_URL}/author/search"
        params = {
            "query": query,
            "fields": ",".join(fields),
            "limit": limit
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            print(f"Semantic Scholar 作者搜索失败: {e}", file=__import__('sys').stderr)
            return []
    
    def get_author_papers(self, author_id: str, limit: int = 100) -> List[Dict]:
        """获取作者论文列表"""
        fields = ["title", "year", "citationCount", "venue", "abstract", "fieldsOfStudy"]
        url = f"{BASE_URL}/author/{author_id}/papers"
        params = {
            "fields": ",".join(fields),
            "limit": limit
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            print(f"获取作者论文失败: {e}", file=__import__('sys').stderr)
            return []
    
    def find_ai_talents(self, topic: str, min_papers: int = 3, limit: int = 20) -> List[Dict]:
        """
        根据主题查找 AI 人才
        返回包含学术影响力的作者列表
        """
        # 先搜索相关论文
        papers = self.search_papers(topic, limit=limit*2)
        
        # 提取作者并统计
        author_stats = {}
        for paper in papers:
            for author in paper.get("authors", []):
                author_id = author.get("authorId")
                if not author_id:
                    continue
                
                if author_id not in author_stats:
                    author_stats[author_id] = {
                        "name": author.get("name"),
                        "papers": [],
                        "total_citations": 0
                    }
                
                author_stats[author_id]["papers"].append({
                    "title": paper.get("title"),
                    "year": paper.get("year"),
                    "citations": paper.get("citationCount", 0),
                    "venue": paper.get("venue")
                })
                author_stats[author_id]["total_citations"] += paper.get("citationCount", 0)
        
        # 过滤并获取详细信息
        talents = []
        for author_id, stats in author_stats.items():
            if len(stats["papers"]) >= min_papers:
                # 获取详细作者信息
                author_details = self.get_author_details(author_id)
                if author_details:
                    talents.append({
                        "author_id": author_id,
                        "name": stats["name"],
                        "affiliations": author_details.get("affiliations", []),
                        "homepage": author_details.get("homepage"),
                        "paper_count": author_details.get("paperCount", 0),
                        "citation_count": author_details.get("citationCount", 0),
                        "h_index": author_details.get("hIndex", 0),
                        "relevant_papers": sorted(stats["papers"], 
                                                  key=lambda x: x.get("citations", 0), 
                                                  reverse=True)[:5]
                    })
        
        # 按 h-index 排序
        talents.sort(key=lambda x: x.get("h_index", 0), reverse=True)
        return talents[:limit]
    
    def get_author_details(self, author_id: str) -> Optional[Dict]:
        """获取作者详细信息"""
        fields = ["name", "aliases", "affiliations", "homepage", 
                 "paperCount", "citationCount", "hIndex"]
        url = f"{BASE_URL}/author/{author_id}"
        params = {"fields": ",".join(fields)}
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"获取作者详情失败: {e}", file=__import__('sys').stderr)
            return None


if __name__ == "__main__":
    api = SemanticScholarAPI()
    
    # 测试：搜索多模态大模型相关人才
    print("搜索: multi-modal large language model")
    talents = api.find_ai_talents("multi-modal large language model", limit=5)
    
    for t in talents:
        print(f"\n{t['name']} (h-index: {t['h_index']})")
        print(f"  机构: {', '.join(t['affiliations']) if t['affiliations'] else 'Unknown'}")
        print(f"  论文: {t['paper_count']}, 引用: {t['citation_count']}")
        print(f"  相关论文:")
        for p in t['relevant_papers'][:3]:
            print(f"    - {p['title']} ({p['year']}, {p['citations']} citations)")

#!/usr/bin/env python3
"""
AI人才雷达 - GitHub API 封装
提供用户/仓库搜索、技术栈分析、贡献活跃度统计
"""

import requests
import json
import os
from typing import List, Dict, Optional

BASE_URL = "https://api.github.com"

class GitHubAPI:
    def __init__(self, token: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Talent-Radar/1.0"
        })
        
        # 优先使用传入的 token，否则尝试环境变量
        self.token = token or os.getenv("GITHUB_TOKEN")
        if self.token:
            self.session.headers["Authorization"] = f"token {self.token}"
    
    def search_users(self, query: str, sort: str = "followers", limit: int = 10) -> List[Dict]:
        """搜索用户"""
        url = f"{BASE_URL}/search/users"
        params = {
            "q": query,
            "sort": sort,
            "order": "desc",
            "per_page": limit
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except Exception as e:
            print(f"GitHub 用户搜索失败: {e}", file=__import__('sys').stderr)
            return []
    
    def search_repos(self, query: str, sort: str = "stars", limit: int = 10) -> List[Dict]:
        """搜索仓库"""
        url = f"{BASE_URL}/search/repositories"
        params = {
            "q": query,
            "sort": sort,
            "order": "desc",
            "per_page": limit
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except Exception as e:
            print(f"GitHub 仓库搜索失败: {e}", file=__import__('sys').stderr)
            return []
    
    def get_user(self, username: str) -> Optional[Dict]:
        """获取用户信息"""
        url = f"{BASE_URL}/users/{username}"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"获取 GitHub 用户信息失败: {e}", file=__import__('sys').stderr)
            return None
    
    def get_user_repos(self, username: str, limit: int = 30) -> List[Dict]:
        """获取用户仓库列表"""
        url = f"{BASE_URL}/users/{username}/repos"
        params = {
            "sort": "updated",
            "direction": "desc",
            "per_page": limit
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"获取 GitHub 用户仓库失败: {e}", file=__import__('sys').stderr)
            return []
    
    def analyze_tech_stack(self, username: str) -> Dict:
        """
        分析用户技术栈
        基于仓库语言统计
        """
        repos = self.get_user_repos(username, limit=100)
        
        lang_stats = {}
        total_stars = 0
        total_forks = 0
        
        for repo in repos:
            if repo.get("fork"):  # 跳过 fork 的仓库
                continue
            
            lang = repo.get("language")
            if lang:
                if lang not in lang_stats:
                    lang_stats[lang] = {"count": 0, "stars": 0}
                lang_stats[lang]["count"] += 1
                lang_stats[lang]["stars"] += repo.get("stargazers_count", 0)
            
            total_stars += repo.get("stargazers_count", 0)
            total_forks += repo.get("forks_count", 0)
        
        # 按使用频率排序
        sorted_langs = sorted(lang_stats.items(), 
                             key=lambda x: x[1]["count"], 
                             reverse=True)
        
        return {
            "top_languages": [lang for lang, _ in sorted_langs[:5]],
            "language_details": dict(sorted_langs),
            "total_repos": len(repos),
            "total_stars": total_stars,
            "total_forks": total_forks,
            "top_repos": sorted(repos, 
                               key=lambda x: x.get("stargazers_count", 0),
                               reverse=True)[:5]
        }
    
    def find_ai_engineers(self, topic: str, location: str = None, min_followers: int = 100, limit: int = 20) -> List[Dict]:
        """
        根据技术主题查找 AI 工程师
        结合仓库搜索和用户分析
        """
        # 构建搜索查询
        query_parts = [topic]
        if location:
            query_parts.append(f"location:{location}")
        query = " ".join(query_parts)
        
        # 搜索相关仓库
        repos = self.search_repos(query, limit=limit*2)
        
        # 提取作者并去重
        seen_users = set()
        engineers = []
        
        for repo in repos:
            owner = repo.get("owner", {})
            username = owner.get("login")
            
            if not username or username in seen_users:
                continue
            seen_users.add(username)
            
            # 获取用户信息
            user = self.get_user(username)
            if not user:
                continue
            
            # 过滤粉丝数
            if user.get("followers", 0) < min_followers:
                continue
            
            # 分析技术栈
            tech_stack = self.analyze_tech_stack(username)
            
            engineers.append({
                "username": username,
                "name": user.get("name"),
                "bio": user.get("bio"),
                "company": user.get("company"),
                "location": user.get("location"),
                "followers": user.get("followers", 0),
                "following": user.get("following", 0),
                "public_repos": user.get("public_repos", 0),
                "blog": user.get("blog"),
                "html_url": user.get("html_url"),
                "tech_stack": tech_stack,
                "featured_repo": {
                    "name": repo.get("name"),
                    "description": repo.get("description"),
                    "stars": repo.get("stargazers_count"),
                    "language": repo.get("language"),
                    "url": repo.get("html_url")
                }
            })
        
        # 按粉丝数排序
        engineers.sort(key=lambda x: x["followers"], reverse=True)
        return engineers[:limit]
    
    def get_contribution_activity(self, username: str) -> Dict:
        """
        获取用户贡献活跃度
        基于最近一年的提交活动
        """
        # 获取事件列表（最近 90 天）
        url = f"{BASE_URL}/users/{username}/events"
        params = {"per_page": 100}
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            events = response.json()
            
            # 统计活动类型
            activity_count = {}
            for event in events:
                event_type = event.get("type")
                activity_count[event_type] = activity_count.get(event_type, 0) + 1
            
            # 计算活跃度评分
            push_events = activity_count.get("PushEvent", 0)
            pr_events = activity_count.get("PullRequestEvent", 0)
            issue_events = activity_count.get("IssuesEvent", 0)
            
            activity_score = min(100, (push_events + pr_events * 2 + issue_events) / 3)
            
            return {
                "total_events": len(events),
                "activity_breakdown": activity_count,
                "activity_score": round(activity_score, 1),
                "activity_level": "High" if activity_score > 70 else "Medium" if activity_score > 30 else "Low"
            }
        except Exception as e:
            print(f"获取 GitHub 贡献活动失败: {e}", file=__import__('sys').stderr)
            return {"activity_score": 0, "activity_level": "Unknown"}


if __name__ == "__main__":
    api = GitHubAPI()
    
    # 测试：搜索多模态大模型相关工程师
    print("搜索 GitHub: multimodal llm")
    engineers = api.find_ai_engineers("multimodal llm language:python", limit=5)
    
    for e in engineers:
        print(f"\n{e['name'] or e['username']} (@{e['username']})")
        print(f"  Bio: {e['bio']}")
        print(f"  Followers: {e['followers']}, Repos: {e['public_repos']}")
        print(f"  Top Languages: {', '.join(e['tech_stack']['top_languages'][:3])}")
        print(f"  Featured: {e['featured_repo']['name']} ({e['featured_repo']['stars']}⭐)")

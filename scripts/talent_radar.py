#!/usr/bin/env python3
"""
AI人才雷达 v4 - 主搜索入口（招聘导向）
数据源：
  - 国际来源: Semantic Scholar API / OpenAlex API / GitHub API
  - Chinese sources: Zhihu/Weibo, accessed via web scraping tools

运行方式（必须 cd 到脚本目录）：
  cd <skill_dir>/scripts
  python3 talent_radar.py search "multimodal llm" --limit 10
"""

import sys
import os
import json
import argparse
from typing import List, Dict

# 修复：确保同级模块可被 import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from semantic_scholar import SemanticScholarAPI
from github_api import GitHubAPI


class AITalentRadar:
    def __init__(self):
        self.ss_api = SemanticScholarAPI()
        # 从环境变量读取 GitHub Token
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            print("⚠️  未检测到 GITHUB_TOKEN，GitHub API 每小时限 60 次请求。"
                  "建议配置 Token 后再批量搜索。", file=sys.stderr)
        self.gh_api = GitHubAPI(token=github_token)

    def search_talents(self, query: str, limit: int = 10) -> Dict:
        results = {
            "query": query,
            "academic_talents": [],
            "engineering_talents": [],
            "combined_insights": {},
            "warnings": []
        }

        # 学术人才（Semantic Scholar）
        print(f"[1/2] 搜索学术人才: {query}...", file=sys.stderr)
        try:
            ss_talents = self.ss_api.find_ai_talents(query, limit=limit)
            results["academic_talents"] = ss_talents
        except Exception as e:
            msg = f"Semantic Scholar 搜索失败: {e}"
            print(msg, file=sys.stderr)
            results["warnings"].append(msg)

        # 工程人才（GitHub）
        print(f"[2/2] 搜索工程人才: {query}...", file=sys.stderr)
        try:
            gh_query = query + " language:python"
            gh_engineers = self.gh_api.find_ai_engineers(gh_query, limit=limit)
            results["engineering_talents"] = gh_engineers
        except Exception as e:
            msg = f"GitHub 搜索失败: {e}"
            print(msg, file=sys.stderr)
            results["warnings"].append(msg)

        results["combined_insights"] = self._generate_insights(
            results["academic_talents"],
            results["engineering_talents"]
        )
        return results

    def generate_profile(self, identifier: str, identifier_type: str = "auto") -> Dict:
        profile = {
            "identifier": identifier,
            "academic_profile": {},
            "engineering_profile": {},
            "summary": {},
            "warnings": []
        }

        if identifier_type in ["auto", "github"]:
            try:
                user = self.gh_api.get_user(identifier)
                if user:
                    tech_stack = self.gh_api.analyze_tech_stack(identifier)
                    activity = self.gh_api.get_contribution_activity(identifier)
                    profile["engineering_profile"] = {
                        "platform": "GitHub",
                        "username": identifier,
                        "name": user.get("name"),
                        "bio": user.get("bio"),
                        "company": user.get("company"),
                        "location": user.get("location"),
                        "followers": user.get("followers"),
                        "public_repos": user.get("public_repos"),
                        "tech_stack": tech_stack,
                        "activity": activity,
                        "profile_url": user.get("html_url")
                    }
            except Exception as e:
                profile["warnings"].append(f"GitHub 查询失败: {e}")

        if identifier_type in ["auto", "scholar"]:
            try:
                authors = self.ss_api.search_authors(identifier, limit=3)
                if authors:
                    author = authors[0]
                    profile["academic_profile"] = {
                        "platform": "Semantic Scholar",
                        "name": author.get("name"),
                        "affiliations": author.get("affiliations", []),
                        "h_index": author.get("hIndex"),
                        "citation_count": author.get("citationCount"),
                        "paper_count": author.get("paperCount"),
                        "profile_url": f"https://www.semanticscholar.org/author/{author.get('authorId', '')}"
                    }
            except Exception as e:
                profile["warnings"].append(f"Semantic Scholar 查询失败: {e}")

        profile["summary"] = self._generate_profile_summary(profile)
        return profile

    def analyze_organization(self, org_name: str) -> Dict:
        analysis = {
            "organization": org_name,
            "scholars": [],
            "research_trends": {},
            "tech_focus": [],
            "warnings": []
        }
        try:
            org_repos = self.gh_api.search_repos(f"org:{org_name}", limit=10)
            if org_repos:
                lang_counts = {}
                for repo in org_repos:
                    lang = repo.get("language")
                    if lang:
                        lang_counts[lang] = lang_counts.get(lang, 0) + 1
                analysis["tech_focus"] = sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)
            else:
                analysis["warnings"].append(
                    f"GitHub 未找到组织 '{org_name}'。若为中文机构名，建议改用英文名（如 MoonshotAI / ByteDance）")
        except Exception as e:
            analysis["warnings"].append(f"GitHub 组织分析失败: {e}")
        return analysis

    def track_trend(self, topic: str) -> Dict:
        trend = {"topic": topic, "active_researchers": [], "warnings": []}
        try:
            experts = self.ss_api.find_ai_talents(topic, limit=10)
            trend["active_researchers"] = experts
        except Exception as e:
            trend["warnings"].append(f"趋势追踪失败: {e}")
        return trend

    def compare_candidates(self, candidate_ids: List[str]) -> Dict:
        comparison = {"candidates": [], "comparison_matrix": {}}
        for cid in candidate_ids:
            profile = self.generate_profile(cid.strip())
            comparison["candidates"].append(profile)
        if len(comparison["candidates"]) >= 2:
            comparison["comparison_matrix"] = self._generate_comparison_matrix(comparison["candidates"])
        return comparison

    def _generate_insights(self, academic, engineering) -> Dict:
        return {
            "total_academic_profiles": len(academic),
            "total_engineering_profiles": len(engineering),
            "top_institutions": self._extract_top_institutions(academic),
            "popular_tech_stacks": self._extract_tech_stacks(engineering)
        }

    def _generate_profile_summary(self, profile: Dict) -> Dict:
        eng = profile.get("engineering_profile", {})
        acad = profile.get("academic_profile", {})
        has_github = bool(eng.get("username"))
        has_academic = bool(acad.get("name"))
        if has_github and has_academic:
            talent_type = "全栈型"
        elif has_github:
            talent_type = "工程型"
        elif has_academic:
            talent_type = "学术型"
        else:
            talent_type = "未知"
        github_stars = eng.get("tech_stack", {}).get("total_stars", 0) if eng else 0
        citations = acad.get("citation_count", 0) if acad else 0
        h_index = acad.get("h_index", 0) if acad else 0
        influence_level = "高" if (github_stars > 1000 or citations > 1000 or h_index > 20) else \
                         "中" if (github_stars > 100 or citations > 100 or h_index > 10) else "初"
        return {
            "talent_type": talent_type,
            "influence_level": influence_level,
            "github_stars": github_stars,
            "citations": citations,
            "h_index": h_index
        }

    def _extract_top_institutions(self, scholars, top_n=5):
        inst_counts = {}
        for s in scholars:
            inst = s.get("affiliation") or (s.get("affiliations", [None]) or [None])[0]
            if inst:
                inst_counts[inst] = inst_counts.get(inst, 0) + 1
        return sorted(inst_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def _extract_tech_stacks(self, engineers, top_n=5):
        lang_counts = {}
        for e in engineers:
            for lang in e.get("tech_stack", {}).get("top_languages", [])[:3]:
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
        return sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def _generate_comparison_matrix(self, candidates):
        matrix = {"academic_comparison": [], "engineering_comparison": []}
        for c in candidates:
            summary = c.get("summary", {})
            matrix["academic_comparison"].append({
                "name": c.get("identifier"),
                "h_index": summary.get("h_index", 0),
                "citations": summary.get("citations", 0),
                "type": summary.get("talent_type")
            })
            matrix["engineering_comparison"].append({
                "name": c.get("identifier"),
                "github_stars": summary.get("github_stars", 0),
                "type": summary.get("talent_type")
            })
        return matrix


def format_text_output(results: Dict, output_type: str = "search") -> str:
    lines = []
    if output_type == "search":
        lines.append(f"🎯 **AI人才雷达** - 搜索结果")
        lines.append(f"搜索词: `{results['query']}`")
        lines.append("")
        insights = results.get("combined_insights", {})
        lines.append(f"📊 找到 {insights.get('total_academic_profiles', 0)} 位学术人才，"
                     f"{insights.get('total_engineering_profiles', 0)} 位工程人才")
        if results.get("academic_talents"):
            lines.append("")
            lines.append("**🎓 学术人才 TOP 5**")
            for i, t in enumerate(results["academic_talents"][:5], 1):
                affiliations = ", ".join(t.get("affiliations", [])) or "N/A"
                ss_url = f"https://www.semanticscholar.org/author/{t.get('author_id', '')}"
                lines.append(f"{i}. **[{t['name']}]({ss_url})** (h-index: {t['h_index']})")
                lines.append(f"   机构: {affiliations} | 引用: {t['citation_count']} | 论文: {t['paper_count']}")
        if results.get("engineering_talents"):
            lines.append("")
            lines.append("**💻 工程人才 TOP 5**")
            for i, e in enumerate(results["engineering_talents"][:5], 1):
                gh_url = e.get("html_url", f"https://github.com/{e['username']}")
                bio = (e.get("bio") or "")[:60]
                langs = ", ".join(e.get("tech_stack", {}).get("top_languages", [])[:3])
                lines.append(f"{i}. **[{e.get('name') or e['username']}]({gh_url})** (@{e['username']})")
                lines.append(f"   {bio} | ⭐{e.get('followers',0)} followers | {langs}")
        if insights.get("top_institutions"):
            lines.append("")
            lines.append("**🏢 热门机构**")
            for inst, count in insights["top_institutions"][:3]:
                lines.append(f"- {inst}: {count}人")
        # 输出 warnings
        for w in results.get("warnings", []):
            lines.append(f"\n⚠️ {w}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="AI人才雷达 v2")
    parser.add_argument("action", choices=["search", "profile", "org", "trend", "compare"])
    parser.add_argument("query", help="搜索关键词、GitHub用户名或机构名")
    parser.add_argument("--limit", type=int, default=10, help="结果数量（最多20）")
    parser.add_argument("--format", choices=["json", "text"], default="text")
    args = parser.parse_args()

    limit = min(args.limit, 20)
    radar = AITalentRadar()

    if args.action == "search":
        results = radar.search_talents(args.query, limit=limit)
        if args.format == "json":
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print(format_text_output(results, "search"))
    elif args.action == "profile":
        profile = radar.generate_profile(args.query)
        print(json.dumps(profile, indent=2, ensure_ascii=False))
    elif args.action == "org":
        analysis = radar.analyze_organization(args.query)
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
    elif args.action == "trend":
        trend = radar.track_trend(args.query)
        print(json.dumps(trend, indent=2, ensure_ascii=False))
    elif args.action == "compare":
        ids = args.query.split(",")
        comparison = radar.compare_candidates(ids)
        print(json.dumps(comparison, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

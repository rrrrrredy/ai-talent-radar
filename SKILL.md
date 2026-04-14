---
name: ai-talent-radar
description: "Recruitment-oriented AI talent search and profiling tool integrating Semantic Scholar, GitHub, and Chinese social platforms (Zhihu/Weibo). Triggers: AI talent, talent radar, find AI engineer, recruit LLM, talent profile, team background check, find RLHF researchers, find Agent researchers, domestic AI scholars. Not for: academic research-oriented analysis (use ai-talent-graph); precise Chinese scholar search (data sources are primarily English)."
tags: [talent, recruitment, ai-engineer, academic, github, semantic-scholar]
metadata:
  version: "V7"
---

# AI Talent Radar V6

## First-time Setup

Run the dependency check script before first use:
```bash
bash scripts/setup.sh
```
> The agent will auto-run this on first trigger; manual execution is usually unnecessary.

**Recruitment-oriented**, integrating academic data (Semantic Scholar/OpenAlex) + engineering data (GitHub) + Chinese social platforms (Zhihu/Weibo) to search and analyze recruitable AI talent.

## ⚠️ Gotchas

> Known issues — check here first before debugging.

⚠️ **Semantic Scholar API rate limit** → Unauthenticated: ~100 requests/5min; add 1~2s interval between batch searches, exceeding returns 429. Recommend applying for free API Key, configure via environment variable to increase to 100/min.

⚠️ **GitHub API Rate Limit** → Without Token: only 60 requests/hour, org analysis exhausts quickly. Must configure `GITHUB_TOKEN` (see Quick Start Step 2). Exceeds limit returns 403, degrades to academic-only data.

⚠️ **Semantic Scholar access slow from some regions** → Direct connection to Scholar API (api.semanticscholar.org) may have high latency; on timeout (default 30s), retry once; if still failing, use `HTTP_PROXY` environment variable.

⚠️ **Excel export requires explicit user confirmation** → When results exceed 10 records, **must** ask user and wait for explicit "confirm" reply before exporting. Single export limit: 50 records.

⚠️ **X/Twitter profile requires no login** → If candidate has Twitter/X handle, use X scraping tools to get followers, Bio, tweet count without X account token. Must go through `HTTP_PROXY` if direct access is blocked.

---

## 🛑 Hard Stop

If the same tool call fails more than 3 times, stop immediately. List all failed approaches and reasons, mark **"Manual intervention needed"**, and wait for human confirmation.

---

## Positioning

| Skill | Orientation | Output Focus |
|-------|------------|-------------|
| **ai-talent-radar** (this Skill) | 🎯 Recruitment | Candidate profiles, contact clues, recruitability assessment |
| ai-talent-graph | 🔬 Academic Research | Academic influence, paper graphs, institutional talent distribution |

## Quick Start

**Step 1: Install dependencies**
```bash
pip install requests openpyxl
```

**Step 2: Configure GitHub Token (strongly recommended, otherwise only 60 requests/hour)**

```bash
# Go to https://github.com/settings/tokens to generate a Personal Access Token (only need public_repo read permission)
export GITHUB_TOKEN="ghp_your_token_here"

# For persistence, add to your shell profile:
echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.bashrc
```

**Step 3: Locate script directory**
```bash
SKILL_DIR=$(dirname "$(find . -name "talent_radar.py" -type f | head -1)" 2>/dev/null)
echo $SKILL_DIR
```

---

## Scenario Mapping

| User says | Agent executes |
|-----------|---------------|
| Find multimodal LLM candidates | `cd $SKILL_DIR && python3 talent_radar.py search "multimodal large language model"` |
| Find RLHF / Agent / RAG researchers | `cd $SKILL_DIR && python3 talent_radar.py search "RLHF reinforcement learning from human feedback"` |
| Generate @karpathy's profile | `cd $SKILL_DIR && python3 talent_radar.py profile "karpathy"` |
| Analyze MoonshotAI team | `cd $SKILL_DIR && python3 talent_radar.py org "MoonshotAI"` |
| Track recently active Agent talent | `cd $SKILL_DIR && python3 talent_radar.py trend "AI agent autonomous"` |
| Compare candidate A and B | `cd $SKILL_DIR && python3 talent_radar.py compare "userA,userB"` |
| Export results to Excel | Run search and save JSON first, then ask user to confirm before exporting |

> **Note**: Semantic Scholar is primarily English academic data. Coverage of domestic institutions may be limited; suggest using English names or searching GitHub orgs directly.

> **Domestic AI team alternatives**: Top Chinese AI teams may have low Semantic Scholar coverage. Alternatives:
> - Search GitHub orgs directly (`org:MoonshotAI`, `org:zhipuai`, etc.)
> - Search Zhihu/Twitter for technical articles to locate authors (using `agent-reach` or web search)
> - Search arXiv/papers-with-code for paper author emails (often contain institutional info)

---

## Chinese Data Sources

### Zhihu AI Scholars
- Liu Zhiyuan (Tsinghua Professor): https://www.zhihu.com/people/zibuyu9
- Qianghua Xuetu (ChatPaper author): https://www.zhihu.com/people/heda-he-28
- Ding Xiaohan (ByteDance Doubao team): https://www.zhihu.com/people/ding-xiao-yi-93

### Weibo AI Influencers
- Aikeke Aishenguo (Prof. Chen Guang, BUPT): https://weibo.com/u/1402400261
- Baoyu xp (Million-follower tech influencer): https://weibo.com/u/1727858283
- i Lu Sanjin: https://weibo.com/u/1706699904

> **Access**: Use `agent-reach` (xreach/xread) or browser automation to access Zhihu/Weibo content for search, profile reading, and technical article extraction. Install: `npx clawhub install agent-reach`

### Domestic Talent Search Scenarios

| User says | Agent executes |
|-----------|---------------|
| Find Chinese LLM Zhihu influencers | Use `agent-reach` or web search: search Zhihu for "large language model AI research" |
| Find active AI scholars on Weibo | Use `agent-reach` or web search: search Weibo for "AI large model scholar" |
| Check Liu Zhiyuan's Zhihu profile | Visit https://www.zhihu.com/people/zibuyu9 |
| Check Aikeke's Weibo updates | Visit https://weibo.com/u/1402400261 |

---

## Execution Flow

### 1. Run Search
```bash
cd $SKILL_DIR
python3 talent_radar.py search "your query" --limit 10 --format text
```

### 1b. Supplement X/Twitter Influence Data (optional, no login needed)

If a candidate has a Twitter/X handle (often found on GitHub profile or personal homepage), supplement public influence metrics:

```bash
# Use X/Twitter scraping tools to fetch: followers, Bio, tweet count, verified status
# These serve as "community influence" dimension in candidate profiles
```

> ⚠️ Set `HTTP_PROXY` if direct access to X is blocked.

### 2. Save JSON Results (prerequisite for Excel export)
```bash
python3 talent_radar.py search "your query" --format json > /tmp/talent_results.json
```

### 3. Export Excel After User Confirmation
```bash
# Only execute after user explicitly replies "confirm"
python3 export_excel.py --input /tmp/talent_results.json --output ~/talent_report.xlsx --force
```

---

## Error Handling

| Error | Resolution |
|-------|-----------|
| ImportError: No module named 'semantic_scholar' | Confirm you `cd $SKILL_DIR` before running; don't call from other directories |
| ModuleNotFoundError: No module named 'requests' | Run `pip install requests openpyxl` |
| GitHub API 403/rate limit | Check GITHUB_TOKEN is set; degrade to academic-only data |
| GITHUB_TOKEN lost (after restart) | Re-export: `export GITHUB_TOKEN="ghp_..."` |
| Semantic Scholar returns empty | Hint: No matching scholars; try English keywords; for domestic institutions try GitHub org search |
| API timeout (30s) | Retry once; if still failing: "Data source temporarily unavailable, please retry later" |
| GitHub Token not configured | Auto-uses unauthenticated mode; remind user: "GITHUB_TOKEN not configured, limited to 60 requests/hour" |

---

## Compliance

- Data sources: Semantic Scholar API (CC BY-NC 2.0), OpenAlex API (CC0), GitHub API (public repos)
- Only accesses public data, no personal privacy involved
- Excel export: must ask user when results > 10, explicit "confirm" required
- Single export limit: 50 records

See `references/compliance.md` for detailed compliance terms.

---

## Changelog

### V6
- Added X/Twitter influence data collection in candidate profiling: fetch followers, Bio, tweet count (guest token, no account needed)
- Gotchas: added X/Twitter proxy requirement note

### V5
- Added Gotchas section (Scholar API rate limit, GitHub rate limit, regional access issues, Excel confirmation)
- Added Hard Stop rule

### V4
- **Clear positioning**: Explicitly recruitment-oriented, differentiated from ai-talent-graph (academic research)
- **Added domestic data sources**: Zhihu AI scholars + Weibo AI influencers
- **Domestic scenario mapping**: Added Zhihu/Weibo search scenarios

### V3
- **GitHub Token persistence**: Configuration guidance for shell profile
- **Domestic AI team alternatives**: Semantic Scholar limited coverage of Chinese institutions; added GitHub org + arXiv fallback paths

### V2
- Integrated Semantic Scholar + GitHub dual data sources
- Supported talent search, profiling, team analysis, candidate comparison
- Excel export (requires user confirmation)

# ai-talent-radar

Recruitment-oriented AI talent search and profiling — integrating Semantic Scholar, GitHub, and Chinese social platforms.

> OpenClaw Skill — works with [OpenClaw](https://github.com/openclaw/openclaw) AI agents

## What It Does

Searches and profiles recruitable AI talent by combining academic data (Semantic Scholar, OpenAlex) with engineering signals (GitHub repos, contributions, tech stack) and Chinese social platform presence (Zhihu, Weibo). Supports candidate search, individual profiling, team/org analysis, candidate comparison, and Excel export. Designed for recruitment workflows — for academic research analysis, see `ai-talent-graph`.

## Quick Start

```bash
# Install via ClawHub (recommended)
openclaw skill install ai-talent-radar

# Or clone this repo into your skills directory
git clone https://github.com/rrrrrredy/ai-talent-radar.git ~/.openclaw/skills/ai-talent-radar

# Install dependencies
bash scripts/setup.sh

# Configure GitHub Token (strongly recommended)
export GITHUB_TOKEN="YOUR_GITHUB_TOKEN"
```

## Features

- **Dual data integration**: Academic (Semantic Scholar/OpenAlex) + Engineering (GitHub) for comprehensive candidate profiles
- **Chinese platform support**: Curated Zhihu AI scholars and Weibo AI influencers for domestic talent discovery
- **Candidate search**: Find AI talent by research topic (RLHF, Agent, RAG, multimodal LLM, etc.)
- **Individual profiling**: Deep profiles with papers, GitHub repos, tech stack, and social presence
- **Team/org analysis**: Analyze engineering teams by GitHub org (MoonshotAI, zhipuai, etc.)
- **Candidate comparison**: Side-by-side comparison of multiple candidates
- **X/Twitter influence**: Optional public influence metrics (followers, Bio) via guest token — no login needed
- **Excel export**: Export search results to `.xlsx` with user confirmation safeguard (max 50 records)
- **Compliance-first**: Only public data, explicit user confirmation for exports

## Usage

```
"Find multimodal LLM candidates"     → Search Semantic Scholar + GitHub
"Generate @karpathy's profile"        → Full candidate profile
"Analyze MoonshotAI team"             → GitHub org analysis
"Find RLHF researchers"               → Topic-specific talent search
"Compare candidate A and B"           → Side-by-side comparison
"Export results to Excel"             → Export with confirmation
"Find Chinese LLM Zhihu influencers" → Domestic social platform search
```

### CLI Examples

```bash
python3 talent_radar.py search "multimodal large language model" --limit 10
python3 talent_radar.py profile "karpathy"
python3 talent_radar.py org "MoonshotAI"
python3 talent_radar.py trend "AI agent autonomous"
python3 talent_radar.py compare "userA,userB"
```

## Project Structure

```
ai-talent-radar/
├── SKILL.md                # Main skill definition
├── scripts/
│   ├── setup.sh            # Dependency installer
│   ├── talent_radar.py     # Main CLI entry point
│   ├── semantic_scholar.py # Semantic Scholar API wrapper
│   ├── github_api.py       # GitHub API wrapper
│   └── export_excel.py     # Excel export utility
├── references/
│   └── compliance.md       # Data compliance terms
└── .gitignore
```

## Requirements

- [OpenClaw](https://github.com/openclaw/openclaw) agent runtime
- Python 3.8+
- `requests`
- `openpyxl` (Excel export)
- `GITHUB_TOKEN` environment variable (strongly recommended — raises rate limit from 60/hr to 5000/hr)
- Optional: `agent-reach` for Zhihu/Weibo content access
- Optional: HTTP proxy for X/Twitter and Semantic Scholar access

## License

[MIT](LICENSE)

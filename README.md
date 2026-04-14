# ai-talent-radar

Recruitment-oriented AI talent search and profiling tool integrating Semantic Scholar, GitHub, and Chinese social platforms (Zhihu/Weibo).

An [OpenClaw](https://github.com/openclaw/openclaw) Skill for finding and evaluating recruitable AI talent from public academic and engineering data sources.

## Installation

### Option A: OpenClaw (recommended)
```bash
# Clone to OpenClaw skills directory
git clone https://github.com/rrrrrredy/ai-talent-radar ~/.openclaw/skills/ai-talent-radar

# Run setup (installs Python dependencies)
bash ~/.openclaw/skills/ai-talent-radar/scripts/setup.sh
```

### Option B: Standalone
```bash
git clone https://github.com/rrrrrredy/ai-talent-radar
cd ai-talent-radar
bash scripts/setup.sh
```

## Dependencies

### Python packages
- `requests`
- `openpyxl`

### Other Skills (optional)
- [ai-talent-graph](https://github.com/rrrrrredy/ai-talent-graph) — For deeper academic research analysis

## Usage

### Search AI talent by topic
```bash
cd scripts/
python3 talent_radar.py search "multimodal large language model" --limit 10
```

### Generate a candidate profile
```bash
python3 talent_radar.py profile "karpathy"
```

### Analyze a GitHub organization
```bash
python3 talent_radar.py org "MoonshotAI"
```

### Track trending researchers
```bash
python3 talent_radar.py trend "AI agent autonomous"
```

### Compare candidates
```bash
python3 talent_radar.py compare "userA,userB"
```

### Export to Excel (requires user confirmation)
```bash
python3 talent_radar.py search "your query" --format json > /tmp/results.json
python3 export_excel.py --input /tmp/results.json --output ~/talent_report.xlsx --force
```

## Data Sources

| Platform | Data | Free Quota |
|----------|------|------------|
| Semantic Scholar | Papers/Authors/Citations | 100 req/5min |
| OpenAlex | Scholar/Institution data | Unlimited |
| GitHub | Repos/Tech stack/Activity | 60/hr (no token), 5000/hr (with token) |

## Project Structure

```
ai-talent-radar/
├── SKILL.md              # Main skill definition
├── scripts/
│   ├── setup.sh          # Installation script
│   ├── talent_radar.py   # Main entry point
│   ├── semantic_scholar.py # Semantic Scholar API wrapper
│   ├── github_api.py     # GitHub API wrapper
│   └── export_excel.py   # Excel export module
├── references/
│   └── compliance.md     # Compliance and API usage terms
└── README.md
```

## License

MIT

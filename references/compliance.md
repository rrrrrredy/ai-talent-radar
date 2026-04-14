# 合规声明与 API 使用限制

## 数据源许可协议

| 数据源 | 许可证 | 使用限制 |
|--------|--------|---------|
| Semantic Scholar | CC BY-NC 2.0 | 非商业使用；需注明来源 |
| OpenAlex | CC0（公共领域）| 无限制 |
| GitHub API | GitHub ToS | 仅公开仓库；遵守 rate limit |

## API 频率限制

### Semantic Scholar
- 免费 API：100 requests/5min
- `find_ai_talents` 会触发多次请求（1次搜索 + N次作者详情），建议 limit ≤ 10

### GitHub API
- 未认证：60 requests/hour（极易打满）
- 有 Token：5000 requests/hour
- `find_ai_engineers` 每个工程师需调用 2-3 次 API（用户信息 + 仓库 + 事件），limit=10 约消耗 30 次请求

### OpenAlex
- 无硬性限制，建议合理使用，不超过 10 requests/second

## 数据导出规范

1. 结果超过 10 条时，必须询问用户："是否导出为 Excel？"
2. 用户明确回复"确认"后，方可执行 export_excel.py
3. 单次导出上限 50 条记录
4. 导出文件包含使用声明页
5. 导出数据仅供当前招聘评估使用，禁止二次分发

## 隐私保护

- 不收集、不存储任何个人隐私数据
- 如候选人要求删除信息，立即停止使用并告知用户处理
- 人才画像基于公开数据，仅供参考，不作为招聘唯一依据

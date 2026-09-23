# 语音还原度听测问卷

本问卷使用 `auk_saasr_preview_v3` 的合并数据，排除第 4、11、25、27 条，保留 26 条样本。
每位听众会获得独立的随机题目顺序，以及每题独立随机的 A/B 候选顺序。候选不显示来源名称，提交后答案保存在当前浏览器的 `localStorage`，并在 `stats.html` 页面提供本地汇总统计。完成后可下载 JSON 结果文件，通过邮件或其他方式发给问卷发起人；发起人可以在统计页导入多份 JSON。

## 本地启动

在仓库根目录运行：

```bash
python3 survey_v1/server.py --host 127.0.0.1 --port 8765
```

问卷地址：`http://127.0.0.1:8765/`

统计地址：`http://127.0.0.1:8765/stats`

默认数据库为 `survey.sqlite3`。测试或单独收集一轮数据时可指定路径：

```bash
python3 survey_v1/server.py --db /path/to/survey.sqlite3
```

## GitHub Pages

GitHub Pages 直接托管 `survey_v1/` 目录即可。问卷入口是 `survey_v1/index.html`，
统计入口是 `survey_v1/stats.html`。本版本不依赖 Python API、Render、数据库或 Google 账号。

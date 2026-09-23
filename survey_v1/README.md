# 语音还原度听测问卷

本问卷使用 `auk_saasr_preview_v3` 的合并数据，排除第 4、11、25、27 条，保留 26 条样本。
每位听众会获得独立的随机题目顺序，以及每题独立随机的 A/B 候选顺序。候选不显示来源名称，提交后服务器将答案写入 SQLite，并在 `/stats` 页面提供汇总统计。

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

## 在线部署

仓库根目录的 `render.yaml` 可用于 Render Blueprint。它启动 Python Web Service，
并把 SQLite 数据库放在持久磁盘 `/var/data/survey.sqlite3`。GitHub Pages 只能托管
静态文件，不能运行本问卷所需的 Python API，因此不要把 `survey_v1` 直接当作
GitHub Pages 应用访问。

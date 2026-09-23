# 语音还原度听测 V2

本问卷使用 `multi_data_representative_30_v2/synthesis_auk_dots_v2_edit_full` 筛选后的 23 个样本。
原编号 `15、20、21、24、25、26、27` 已排除，其余样本在问卷中重新连续编号：

- 参考音频：`multi_data_representative_30_v2/audio`
- 候选 A/B：`sure_tagger/audio` 与 `captioner/audio`

每位听众获得独立的随机题目顺序和 A/B 候选顺序。答案只保存在当前浏览器的
`localStorage`，每题保存后可以导出当前 JSON；完成后把 JSON 发给问卷发起人。
统计页可导入多份参与者 JSON 并计算逐题平均胜率。

入口：`index.html`

统计：`stats.html`

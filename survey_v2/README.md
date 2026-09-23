# 语音还原度听测 V2

本问卷使用筛选后的 28 个样本，原编号 `15、20` 已排除，其余样本在问卷中重新连续编号。
原编号 `4、6、7、9、10、11、12、16、17、18、19、21、23、24、25、26、27、28、30`
使用 `synthesis_auk_dots_v3_duration_full` 的生成音频，其他编号继续使用
`synthesis_auk_dots_v2_edit_full` 的生成音频：

- 参考音频：`multi_data_representative_30_v2/audio`
- 候选 A/B：`sure_tagger/audio` 与 `captioner/audio`

每位听众获得独立的随机题目顺序和 A/B 候选顺序。答案只保存在当前浏览器的
`localStorage`，每题保存后可以导出当前 JSON；完成后把 JSON 发给问卷发起人。
统计页可导入多份参与者 JSON 并计算逐题平均胜率。

入口：`index.html`

统计：`stats.html`

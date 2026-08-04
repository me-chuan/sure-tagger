> 说明：本文件是早期需求和调研笔记，保留了较宽泛的 tagger 设想。当前已经落地的语言层 meeting-level pipeline、命令和验证结果以 `pipeline_usage.md` 为准。

1. tts模型自进化，[参考evomaster中的usage.md](http://xn--evomasterusage-or7vs60eg88k6y9a.md)，

   `路径：/hpc_stor03/sjtu_home/chaolei.liu/Agent/EvoMaster`

   cosyvoice3, f5 tts等等

2. agentic data tagger（当前语言层实现采用 meeting-level tagging）

motivation：模型自进化或者模型调优，需要更加稠密的奖励信号or反馈信号，传统的data corpus-level的反馈无法满足，据此我们提出可按样本、会议等粒度扩展的 agentic data tagger。

目前专注于ASR任务：

（语音，转录文本，extra info，corpus-level info）
 tools: pipelines (每一个tag调用一个tool）

声学层：

| Tag                      | 获取方法                             | 可靠性 |
| ------------------------ | ------------------------------------ | ------ |
| `duration_sec`           | 文件解析                             | L0     |
| `sample_rate_hz`         | 文件解析                             | L0     |
| `channel_count`          | 文件解析                             | L0     |
| `codec`                  | ffprobe                              | L0     |
| `bitrate`                | ffprobe                              | L0     |
| `rms_dbfs`               | DSP                                  | L0     |
| `peak_dbfs`              | DSP                                  | L0     |
| `clipping_ratio`         | 超阈值采样点比例                     | L0     |
| `dc_offset`              | 波形均值                             | L0     |
| `dropout_ratio`          | 连续零值/近零值检测                  | L0     |
| `effective_bandwidth_hz` | 频谱能量分析                         | L0     |
| `bandwidth_class`        | narrow/wide/fullband 规则分桶        | L0     |
| `silence_ratio`          | VAD 后计算(不确定的）                | L0/L1  |
| 说话人                   | 谱聚类SD、ASR-condition SD、metadata |        |
| SNR/C60/远场             |                                      |        |
| music/sound              | caption(Qwen3-omni)                  |        |

语言层：

| Tag                     | 方法               |              |
| ----------------------- | ------------------ | ------------ |
| topic                   | 文本模型 (gpt/api) | 不限定金融领域，使用通用层级 taxonomy |
| language                |                    |              |
| word_count              |                    |              |
| punctuation             |                    |              |
| repetition (uh, ah, oh) |                    |              |

gpt调研结果：

| Tag                      | 实现类型              | 推荐实现方案                                                 | 推荐工具/模型                            | 输出示例                     | 说明                                                         |
| ------------------------ | --------------------- | ------------------------------------------------------------ | ---------------------------------------- | ---------------------------- | ------------------------------------------------------------ |
| `duration_sec`           | 确定性脚本            | 解码音频后，用采样点数除以采样率；也可读取容器时长进行校验   | `ffprobe` + `soundfile`                  | `3.427`                      | 建议以解码后的真实时长为主                                   |
| `sample_rate_hz`         | 确定性脚本            | 读取音频流元数据                                             | `ffprobe` / `soundfile`                  | `16000`                      | 不需要重采样后再统计                                         |
| `channel_count`          | 确定性脚本            | 读取声道数                                                   | `ffprobe` / `soundfile`                  | `1`                          | 可同时记录 `channel_layout`                                  |
| `codec`                  | 确定性脚本            | 读取音频流编码格式                                           | `ffprobe`                                | `pcm_s16le`                  | 文件扩展名不一定等于真实 codec                               |
| `bitrate`                | 确定性脚本            | 优先读取音频流码率；缺失时用文件大小和时长计算平均码率       | `ffprobe`                                | `256000`                     | 建议命名为 `bitrate_bps`，并记录计算来源                     |
| `rms_dbfs`               | 确定性脚本            | 波形归一化到 `[-1,1]`，计算 RMS 后转换为 dBFS                | `numpy` / `soundfile`                    | `-24.7`                      | 建议同时计算全音频 RMS 和语音区域 RMS                        |
| `peak_dbfs`              | 确定性脚本            | 计算波形绝对值最大值，再转换为 dBFS                          | `numpy`                                  | `-0.35`                      | 多声道先分别计算，再取最大值                                 |
| `clipping_ratio`         | 确定性脚本            | 统计绝对幅度超过固定阈值的采样点比例，例如 `≥0.999`          | `numpy`                                  | `0.0021`                     | 阈值必须写入配置和结果版本                                   |
| `dc_offset`              | 确定性脚本            | 计算波形均值；多声道分别计算                                 | `numpy`                                  | `0.0013`                     | 可同时输出线性值和 dBFS                                      |
| `dropout_ratio`          | 脚本为主，VAD辅助     | 检测连续全零、固定值或异常低能量区间；结合 VAD 排除正常静音  | `numpy` + VAD                            | `0.004`                      | 建议拆为 `digital_dropout_ratio` 和 `speech_dropout_ratio`   |
| `effective_bandwidth_hz` | DSP脚本 + VAD         | 在语音帧上计算长期频谱，估计持续高于噪声底的最高有效频率     | `scipy.signal` / `numpy` + VAD           | `7600`                       | 不建议直接使用 librosa 的 `spectral_bandwidth`，两者含义不同 |
| `bandwidth_class`        | 确定性规则            | 根据 `effective_bandwidth_hz` 映射为窄带、宽带等类别         | 自定义规则                               | `wideband`                   | 建议固定分类标准和阈值                                       |
| `silence_ratio`          | 专用模型              | 用 VAD 得到语音区间，非语音时长除以总时长                    | Silero VAD / TEN VAD / Brouhaha          | `0.23`                       | 建议同时输出开头、结尾和内部静音比例                         |
| `speaker`                | 专用模型或元数据      | 数据集若有可靠 speaker ID，直接读取；否则做说话人日志和聚类(谱聚类SD等） | pyannote.audio                           | `SPEAKER_00`                 | 建议拆成多个字段，见下文                                     |
| `SNR`                    | 专用模型              | 无干净参考信号时做无参考 SNR 估计，在语音帧上聚合            | Brouhaha / DNSMOS辅助                    | `14.6`                       | 必须标记为估计值，建议输出中位数和分位数                     |
| `C60`                    | 需重新定义            | 不建议直接使用 C60；若表示语音清晰度，建议改为 `C50`；若表示混响时长，使用 `RT60` | Brouhaha 可估计 C50；盲混响模型估计 RT60 | `c50_db=3.2`                 | 当前 tag 名称含义不够标准，需要先确定目标                    |
| `远场`                   | 专用模型 + 派生规则   | 用音频 embedding、C50/RT60、SNR、语音能量等特征训练近场/远场分类器 | 自训练分类器；预训练音频 encoder         | `far_field_probability=0.76` | 单通道音频无法确定真实距离，建议输出概率而非硬标签           |
| `music`                  | 专用模型              | 对音频按窗口进行音乐检测，统计音乐占比及与语音重叠比例       | YAMNet / PANNs / 音乐检测模型            | `music_ratio=0.18`           | 可以和 `sound` 共用一次音频事件模型                          |
| `sound`                  | 专用模型              | 对环境声、人类非语音声和其他事件进行多标签分类               | YAMNet / PANNs                           | `["traffic","applause"]`     | 建议映射为 ASR 场景需要的粗粒度分类                          |
| `topic`                  | 文本模型或 Agent推理  | 仅基于可信 transcript 分类；最好先制定固定 topic taxonomy，再做分类 | 文本 embedding分类器 / LLM / BERTopic    | `technology`                 | 短样本主题信息不足时，可拼接相邻样本或录音级文本             |
| `language`               | 文本模型              | 仅使用 transcript 做语言识别；先做 Unicode 字符系统统计，再做文本语言分类 | fastText LID / CLD3 / langid             | `zh`                         | 短文本、人名、数字容易误判，建议保留置信度                   |
| `word_count`             | 确定性脚本            | 英文按 tokenizer 统计；中文需要指定分词器；同时保存字符数和 token 数 | spaCy / Jieba / 自定义 tokenizer         | `7`                          | 跨语言对比时，`character_count` 和 `token_count` 更稳定      |
| `punctuation`            | 确定性脚本            | 对可信 transcript 中已有标点进行 Unicode/正则统计            | Python `regex` / `unicodedata`           | `{"comma":2,"period":1}`     | 当前阶段不需要做标点恢复                                     |
| `repetition`             | 确定性脚本 + 文本规则 | 基于文本检测填充词、语气词和连续词语重复                     | 词典 + 正则 + tokenizer                  | `filler_count=2`             | 建议拆分，不要把 `uh/ah/oh` 全部叫 repetition                |

明确tagger的输入：corpus, sample(audio, text, metadata, provenance)

```json
{
  "corpus": {
    "dataset_name": "",
    "source_urls": {
      "article": [],
      "github": [],
      "huggingface": [],
      "dataset_card": []
    },
    "native_metadata": {}
  },
  "sample": {
    "sample_id": "",
    "audio": {
      "path": "",
      "start_sec": null,
      "end_sec": null
    },
    "text": {
      "transcript": ""
    },
    "native_metadata": {},
    "provenance": {
      "source_path": "",
      "source_split": ""
    }
  }
}
```

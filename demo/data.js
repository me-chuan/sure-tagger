window.DEMO_DATA = {
  "summary": {
    "sampleCount": 40,
    "datasetCount": 8,
    "selectedCount": 40,
    "rirArtifactCount": 40,
    "datasets": [
      {
        "name": "LibriSpeech",
        "count": 5
      },
      {
        "name": "AISHELL-1",
        "count": 5
      },
      {
        "name": "TIMIT",
        "count": 5
      },
      {
        "name": "CHiME4",
        "count": 5
      },
      {
        "name": "AMI",
        "count": 5
      },
      {
        "name": "TUT Urban Acoustic Scenes 2018",
        "count": 5
      },
      {
        "name": "NOISEX-92",
        "count": 5
      },
      {
        "name": "WHAM! noise",
        "count": 5
      }
    ],
    "coverage": {
      "basic_acoustic": 40,
      "sound_field_scene": 40,
      "language_content": 40,
      "speaker": 40
    },
    "topicCount": 40,
    "speakerCount": 40,
    "speakerMultiCount": 6,
    "generatedFrom": {
      "manifest": "phase2_asr_sample/manifest.jsonl",
      "tags": "outputs/phase2_full_pipeline_topic_speaker_tags.jsonl",
      "speakerArtifacts": "outputs/phase2_topic_speaker_artifacts_2048"
    }
  },
  "samples": [
    {
      "row": 1,
      "sampleId": "1089-134686-0000",
      "dataset": "LibriSpeech",
      "title": "Clean baseline: English",
      "note": "Phase2 sample with supplemented topic=culture_media_arts/literature and speaker flags multi/change/overlap=False/False/False.",
      "audio": "assets/audio/librispeech_1089-134686-0000.wav",
      "transcript": "HE HOPED THERE WOULD BE STEW FOR DINNER TURNIPS AND CARROTS AND BRUISED POTATOES AND FAT MUTTON PIECES TO BE LADLED OUT IN THICK PEPPERED FLOUR FATTENED SAUCE",
      "nativeMetadata": {},
      "durationSec": 10.435,
      "tags": {
        "basic_acoustic": {
          "c50": 59.800788,
          "channels": 1,
          "dnsmos_bak": 4.185929,
          "dnsmos_ovrl": 3.41634,
          "dnsmos_p808": 4.000727,
          "dnsmos_sig": 3.640973,
          "duration_sec": 10.435,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.058936,
          "silence_segments": [
            {
              "end_sec": 0.5,
              "start_sec": 0
            },
            {
              "end_sec": 10.435,
              "start_sec": 10.32
            }
          ],
          "snr_db": 45.948561
        },
        "language_content": {
          "filler": 0,
          "language": "en",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "culture_media_arts/literature",
          "word_count": 28
        },
        "sound_field_scene": {
          "audio_events": [
            "speech",
            "singing"
          ],
          "c50": 40.897876,
          "far_field": null,
          "music": false,
          "rt60": 0.060225,
          "sound": []
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 2,
      "sampleId": "1089-134686-0001",
      "dataset": "LibriSpeech",
      "title": "Clean read English speech: 1089-134686-0001",
      "note": "Phase2 sample with supplemented topic=culture_media_arts/literature and speaker flags multi/change/overlap=False/False/False.",
      "audio": "assets/audio/librispeech_1089-134686-0001.wav",
      "transcript": "STUFF IT INTO YOU HIS BELLY COUNSELLED HIM",
      "nativeMetadata": {},
      "durationSec": 3.275,
      "tags": {
        "basic_acoustic": {
          "c50": 59.855418,
          "channels": 1,
          "dnsmos_bak": 4.124885,
          "dnsmos_ovrl": 3.204987,
          "dnsmos_p808": 3.739523,
          "dnsmos_sig": 3.470618,
          "duration_sec": 3.275,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.169466,
          "silence_segments": [
            {
              "end_sec": 0.31,
              "start_sec": 0
            },
            {
              "end_sec": 3.275,
              "start_sec": 3.03
            }
          ],
          "snr_db": 42.423795
        },
        "language_content": {
          "filler": 0,
          "language": "en",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "culture_media_arts/literature",
          "word_count": 8
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 39.539401,
          "far_field": null,
          "music": false,
          "rt60": 0.06563,
          "sound": []
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 3,
      "sampleId": "1089-134686-0002",
      "dataset": "LibriSpeech",
      "title": "Clean read English speech: 1089-134686-0002",
      "note": "Phase2 sample with supplemented topic=culture_media_arts/literature and speaker flags multi/change/overlap=False/False/False.",
      "audio": "assets/audio/librispeech_1089-134686-0002.wav",
      "transcript": "AFTER EARLY NIGHTFALL THE YELLOW LAMPS WOULD LIGHT UP HERE AND THERE THE SQUALID QUARTER OF THE BROTHELS",
      "nativeMetadata": {},
      "durationSec": 6.625,
      "tags": {
        "basic_acoustic": {
          "c50": 59.750942,
          "channels": 1,
          "dnsmos_bak": 4.147284,
          "dnsmos_ovrl": 3.344947,
          "dnsmos_p808": 4.141948,
          "dnsmos_sig": 3.594833,
          "duration_sec": 6.625,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.09283,
          "silence_segments": [
            {
              "end_sec": 0.34,
              "start_sec": 0
            },
            {
              "end_sec": 6.625,
              "start_sec": 6.35
            }
          ],
          "snr_db": 47.73482
        },
        "language_content": {
          "filler": 0,
          "language": "en",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "culture_media_arts/literature",
          "word_count": 18
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 40.543838,
          "far_field": null,
          "music": false,
          "rt60": 0.061985,
          "sound": []
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 4,
      "sampleId": "1089-134686-0003",
      "dataset": "LibriSpeech",
      "title": "Clean read English speech: 1089-134686-0003",
      "note": "Phase2 sample with supplemented topic=daily_life_social/interpersonal_chat and speaker flags multi/change/overlap=False/False/False.",
      "audio": "assets/audio/librispeech_1089-134686-0003.wav",
      "transcript": "HELLO BERTIE ANY GOOD IN YOUR MIND",
      "nativeMetadata": {},
      "durationSec": 2.68,
      "tags": {
        "basic_acoustic": {
          "c50": 59.5377,
          "channels": 1,
          "dnsmos_bak": 3.853381,
          "dnsmos_ovrl": 3.097636,
          "dnsmos_p808": 3.662646,
          "dnsmos_sig": 3.466424,
          "duration_sec": 2.68,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.164179,
          "silence_segments": [
            {
              "end_sec": 0.41,
              "start_sec": 0
            },
            {
              "end_sec": 2.68,
              "start_sec": 2.65
            }
          ],
          "snr_db": 53.300519
        },
        "language_content": {
          "filler": 0,
          "language": "en",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "daily_life_social/interpersonal_chat",
          "word_count": 7
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 34.957345,
          "far_field": null,
          "music": false,
          "rt60": 0.078515,
          "sound": []
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 5,
      "sampleId": "1089-134686-0004",
      "dataset": "LibriSpeech",
      "title": "Clean read English speech: 1089-134686-0004",
      "note": "Phase2 sample with supplemented topic=daily_life_social/interpersonal_chat and speaker flags multi/change/overlap=False/False/False.",
      "audio": "assets/audio/librispeech_1089-134686-0004.wav",
      "transcript": "NUMBER TEN FRESH NELLY IS WAITING ON YOU GOOD NIGHT HUSBAND",
      "nativeMetadata": {},
      "durationSec": 5.215063,
      "tags": {
        "basic_acoustic": {
          "c50": 59.891187,
          "channels": 1,
          "dnsmos_bak": 4.191944,
          "dnsmos_ovrl": 3.472051,
          "dnsmos_p808": 4.011679,
          "dnsmos_sig": 3.685994,
          "duration_sec": 5.215063,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.143814,
          "silence_segments": [
            {
              "end_sec": 0.18,
              "start_sec": 0
            },
            {
              "end_sec": 1.58,
              "start_sec": 1.46
            },
            {
              "end_sec": 4.09,
              "start_sec": 3.64
            }
          ],
          "snr_db": 55.506136
        },
        "language_content": {
          "filler": 0,
          "language": "en",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "daily_life_social/interpersonal_chat",
          "word_count": 11
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 40.63356,
          "far_field": null,
          "music": false,
          "rt60": 0.06108,
          "sound": []
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 6,
      "sampleId": "BAC009S0764W0121",
      "dataset": "AISHELL-1",
      "title": "Clean baseline: Mandarin",
      "note": "Phase2 sample with supplemented topic=news_current_events/economy and speaker flags multi/change/overlap=False/False/False.",
      "audio": "assets/audio/aishell_BAC009S0764W0121.wav",
      "transcript": "甚至 出现 交易 几乎 停滞 的 情况",
      "nativeMetadata": {},
      "durationSec": 4.203938,
      "tags": {
        "basic_acoustic": {
          "c50": 17.909705,
          "channels": 1,
          "dnsmos_bak": 3.482607,
          "dnsmos_ovrl": 2.425111,
          "dnsmos_p808": 3.745586,
          "dnsmos_sig": 3.030385,
          "duration_sec": 4.203938,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.169826,
          "silence_segments": [
            {
              "end_sec": 0.41,
              "start_sec": 0
            },
            {
              "end_sec": 4.203938,
              "start_sec": 3.9
            }
          ],
          "snr_db": 42.611545
        },
        "language_content": {
          "filler": 0,
          "language": "zh",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "news_current_events/economy",
          "word_count": 13
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 21.544749,
          "far_field": null,
          "music": false,
          "rt60": 0.264471,
          "sound": []
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 7,
      "sampleId": "BAC009S0764W0122",
      "dataset": "AISHELL-1",
      "title": "Mandarin read speech: BAC009S0764W0122",
      "note": "Phase2 sample with supplemented topic=other/insufficient_context and speaker flags multi/change/overlap=False/False/False.",
      "audio": "assets/audio/aishell_BAC009S0764W0122.wav",
      "transcript": "一二 线 城市 虽然 也 处于 调整 中",
      "nativeMetadata": {},
      "durationSec": 4.115,
      "tags": {
        "basic_acoustic": {
          "c50": 17.344906,
          "channels": 1,
          "dnsmos_bak": 2.260463,
          "dnsmos_ovrl": 1.849036,
          "dnsmos_p808": 3.721751,
          "dnsmos_sig": 2.380089,
          "duration_sec": 4.115,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.173755,
          "silence_segments": [
            {
              "end_sec": 0.46,
              "start_sec": 0
            },
            {
              "end_sec": 4.115,
              "start_sec": 3.86
            }
          ],
          "snr_db": 35.1419
        },
        "language_content": {
          "filler": 0,
          "language": "zh",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "other/insufficient_context",
          "word_count": 13
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 20.407529,
          "far_field": null,
          "music": false,
          "rt60": 0.289965,
          "sound": []
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 8,
      "sampleId": "BAC009S0764W0123",
      "dataset": "AISHELL-1",
      "title": "Mandarin read speech: BAC009S0764W0123",
      "note": "Phase2 sample with supplemented topic=other/insufficient_context and speaker flags multi/change/overlap=False/False/False.",
      "audio": "assets/audio/aishell_BAC009S0764W0123.wav",
      "transcript": "但 因为 聚集 了 过多 公共 资源",
      "nativeMetadata": {},
      "durationSec": 4,
      "tags": {
        "basic_acoustic": {
          "c50": 18.41354,
          "channels": 1,
          "dnsmos_bak": 3.094054,
          "dnsmos_ovrl": 2.18487,
          "dnsmos_p808": 3.57581,
          "dnsmos_sig": 2.889049,
          "duration_sec": 4,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.1825,
          "silence_segments": [
            {
              "end_sec": 0.47,
              "start_sec": 0
            },
            {
              "end_sec": 4,
              "start_sec": 3.74
            }
          ],
          "snr_db": 27.321666
        },
        "language_content": {
          "filler": 0,
          "language": "zh",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "other/insufficient_context",
          "word_count": 12
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 20.477777,
          "far_field": null,
          "music": false,
          "rt60": 0.276645,
          "sound": []
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 9,
      "sampleId": "BAC009S0764W0124",
      "dataset": "AISHELL-1",
      "title": "Mandarin read speech: BAC009S0764W0124",
      "note": "Phase2 sample with supplemented topic=business_management/strategy and speaker flags multi/change/overlap=False/False/False.",
      "audio": "assets/audio/aishell_BAC009S0764W0124.wav",
      "transcript": "为了 规避 三四 线 城市 明显 过剩 的 市场 风险",
      "nativeMetadata": {},
      "durationSec": 5.237,
      "tags": {
        "basic_acoustic": {
          "c50": 17.022462,
          "channels": 1,
          "dnsmos_bak": 1.967448,
          "dnsmos_ovrl": 1.76408,
          "dnsmos_p808": 3.618682,
          "dnsmos_sig": 2.26975,
          "duration_sec": 5.237,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.113997,
          "silence_segments": [
            {
              "end_sec": 0.45,
              "start_sec": 0
            },
            {
              "end_sec": 5.237,
              "start_sec": 5.09
            }
          ],
          "snr_db": 25.181909
        },
        "language_content": {
          "filler": 0,
          "language": "zh",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "business_management/strategy",
          "word_count": 18
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 21.588484,
          "far_field": null,
          "music": false,
          "rt60": 0.261172,
          "sound": []
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 10,
      "sampleId": "BAC009S0764W0125",
      "dataset": "AISHELL-1",
      "title": "Mandarin read speech: BAC009S0764W0125",
      "note": "Phase2 sample with supplemented topic=business_management/strategy and speaker flags multi/change/overlap=False/False/False.",
      "audio": "assets/audio/aishell_BAC009S0764W0125.wav",
      "transcript": "标杆 房企 必然 调整 市场 战略",
      "nativeMetadata": {},
      "durationSec": 4.311,
      "tags": {
        "basic_acoustic": {
          "c50": 16.945509,
          "channels": 1,
          "dnsmos_bak": 3.054762,
          "dnsmos_ovrl": 2.237836,
          "dnsmos_p808": 3.558418,
          "dnsmos_sig": 2.821837,
          "duration_sec": 4.311,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.157968,
          "silence_segments": [
            {
              "end_sec": 0.46,
              "start_sec": 0
            },
            {
              "end_sec": 4.311,
              "start_sec": 4.09
            }
          ],
          "snr_db": 33.636256
        },
        "language_content": {
          "filler": 0,
          "language": "zh",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "business_management/strategy",
          "word_count": 12
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 22.180508,
          "far_field": null,
          "music": false,
          "rt60": 0.255192,
          "sound": []
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 11,
      "sampleId": "sa1",
      "dataset": "TIMIT",
      "title": "Clean baseline: TIMIT",
      "note": "Phase2 sample with supplemented topic=other/insufficient_context and speaker flags multi/change/overlap=False/False/False.",
      "audio": "assets/audio/timit_sa1.wav",
      "transcript": "She had your dark suit in greasy wash water all year.",
      "nativeMetadata": {},
      "durationSec": 3.968,
      "tags": {
        "basic_acoustic": {
          "c50": 59.801624,
          "channels": 1,
          "dnsmos_bak": 4.039296,
          "dnsmos_ovrl": 3.229164,
          "dnsmos_p808": 4.03552,
          "dnsmos_sig": 3.547086,
          "duration_sec": 3.968,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.138609,
          "silence_segments": [
            {
              "end_sec": 0.55,
              "start_sec": 0
            }
          ],
          "snr_db": 50.160365
        },
        "language_content": {
          "filler": 0,
          "language": "en",
          "punctuation": {
            "has_terminal_punctuation": true,
            "punctuation_count": 1
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "other/insufficient_context",
          "word_count": 11
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 41.014629,
          "far_field": null,
          "music": false,
          "rt60": 0.064891,
          "sound": []
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 12,
      "sampleId": "sa2",
      "dataset": "TIMIT",
      "title": "Phonetic read speech: sa2",
      "note": "Phase2 sample with supplemented topic=daily_life_social/interpersonal_chat and speaker flags multi/change/overlap=False/False/False.",
      "audio": "assets/audio/timit_sa2.wav",
      "transcript": "Don't ask me to carry an oily rag like that.",
      "nativeMetadata": {},
      "durationSec": 3.628812,
      "tags": {
        "basic_acoustic": {
          "c50": 59.777898,
          "channels": 1,
          "dnsmos_bak": 4.19564,
          "dnsmos_ovrl": 3.411771,
          "dnsmos_p808": 3.657432,
          "dnsmos_sig": 3.663176,
          "duration_sec": 3.628812,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.236665,
          "silence_segments": [
            {
              "end_sec": 0.77,
              "start_sec": 0
            },
            {
              "end_sec": 3.628812,
              "start_sec": 3.54
            }
          ],
          "snr_db": 59.886621
        },
        "language_content": {
          "filler": 0,
          "language": "en",
          "punctuation": {
            "has_terminal_punctuation": true,
            "punctuation_count": 2
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "daily_life_social/interpersonal_chat",
          "word_count": 10
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 40.64341,
          "far_field": null,
          "music": false,
          "rt60": 0.066912,
          "sound": []
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 13,
      "sampleId": "si1573",
      "dataset": "TIMIT",
      "title": "Phonetic read speech: si1573",
      "note": "Phase2 sample with supplemented topic=culture_media_arts/literature and speaker flags multi/change/overlap=False/False/False.",
      "audio": "assets/audio/timit_si1573.wav",
      "transcript": "His captain was thin and haggard and his beautiful boots were worn and shabby.",
      "nativeMetadata": {},
      "durationSec": 4.972812,
      "tags": {
        "basic_acoustic": {
          "c50": 59.129156,
          "channels": 1,
          "dnsmos_bak": 4.019212,
          "dnsmos_ovrl": 3.213393,
          "dnsmos_p808": 3.6728,
          "dnsmos_sig": 3.538065,
          "duration_sec": 4.972812,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.104569,
          "silence_segments": [
            {
              "end_sec": 0.52,
              "start_sec": 0
            }
          ],
          "snr_db": 44.730727
        },
        "language_content": {
          "filler": 0,
          "language": "en",
          "punctuation": {
            "has_terminal_punctuation": true,
            "punctuation_count": 1
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "culture_media_arts/literature",
          "word_count": 14
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 41.273514,
          "far_field": null,
          "music": false,
          "rt60": 0.065439,
          "sound": []
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 14,
      "sampleId": "sx133",
      "dataset": "TIMIT",
      "title": "Phonetic read speech: sx133",
      "note": "Phase2 sample with supplemented topic=daily_life_social/food and speaker flags multi/change/overlap=False/False/False.",
      "audio": "assets/audio/timit_sx133.wav",
      "transcript": "Pizzerias are convenient for a quick lunch.",
      "nativeMetadata": {},
      "durationSec": 3.31525,
      "tags": {
        "basic_acoustic": {
          "c50": 59.62676,
          "channels": 1,
          "dnsmos_bak": 4.0966,
          "dnsmos_ovrl": 3.275021,
          "dnsmos_p808": 3.838463,
          "dnsmos_sig": 3.595976,
          "duration_sec": 3.31525,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.153835,
          "silence_segments": [
            {
              "end_sec": 0.51,
              "start_sec": 0
            }
          ],
          "snr_db": 30.496323
        },
        "language_content": {
          "filler": 0,
          "language": "en",
          "punctuation": {
            "has_terminal_punctuation": true,
            "punctuation_count": 1
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "daily_life_social/food",
          "word_count": 7
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 41.016975,
          "far_field": null,
          "music": false,
          "rt60": 0.069614,
          "sound": []
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 15,
      "sampleId": "sx223",
      "dataset": "TIMIT",
      "title": "Phonetic read speech: sx223",
      "note": "Phase2 sample with supplemented topic=daily_life_social/housing and speaker flags multi/change/overlap=False/False/False.",
      "audio": "assets/audio/timit_sx223.wav",
      "transcript": "Put the butcher block table in the garage.",
      "nativeMetadata": {},
      "durationSec": 3.097625,
      "tags": {
        "basic_acoustic": {
          "c50": 59.754849,
          "channels": 1,
          "dnsmos_bak": 4.186132,
          "dnsmos_ovrl": 3.44368,
          "dnsmos_p808": 4.139837,
          "dnsmos_sig": 3.692719,
          "duration_sec": 3.097625,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.20661,
          "silence_segments": [
            {
              "end_sec": 0.64,
              "start_sec": 0
            }
          ],
          "snr_db": 47.395483
        },
        "language_content": {
          "filler": 0,
          "language": "en",
          "punctuation": {
            "has_terminal_punctuation": true,
            "punctuation_count": 1
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "daily_life_social/housing",
          "word_count": 8
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 39.990012,
          "far_field": null,
          "music": false,
          "rt60": 0.065759,
          "sound": []
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 16,
      "sampleId": "F01_050C0101_PED_REAL",
      "dataset": "CHiME4",
      "title": "Noisy speech: pedestrian",
      "note": "Phase2 sample with supplemented topic=news_current_events/economy and speaker flags multi/change/overlap=False/False/False.",
      "audio": "assets/audio/chime4_F01_050C0101_PED_REAL.wav",
      "transcript": "LAST MONTH OVERALL GOODS PRODUCING EMPLOYMENT FELL SIXTY EIGHT THOUSAND AFTER A THIRTY TWO THOUSAND JOB RISE IN FEBRUARY",
      "nativeMetadata": {},
      "durationSec": 7.623687,
      "tags": {
        "basic_acoustic": {
          "c50": 51.3061,
          "channels": 1,
          "dnsmos_bak": 1.359623,
          "dnsmos_ovrl": 1.404506,
          "dnsmos_p808": 2.370079,
          "dnsmos_sig": 2.168632,
          "duration_sec": 7.623687,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.080014,
          "silence_segments": [
            {
              "end_sec": 0.61,
              "start_sec": 0
            }
          ],
          "snr_db": -0.23553
        },
        "language_content": {
          "filler": 0,
          "language": "en",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "news_current_events/economy",
          "word_count": 19
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 26.065818,
          "far_field": null,
          "music": false,
          "rt60": 0.463003,
          "sound": []
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 17,
      "sampleId": "F01_050C0102_CAF_REAL",
      "dataset": "CHiME4",
      "title": "Noisy speech: cafe",
      "note": "Phase2 sample with supplemented topic=news_current_events/economy and speaker flags multi/change/overlap=False/False/False.",
      "audio": "assets/audio/chime4_F01_050C0102_CAF_REAL.wav",
      "transcript": "THE DEPARTMENT SAID THE DECLINE IN FACTORY JOBS WAS CONCENTRATED IN MOTOR VEHICLES AND ELECTRICAL AND ELECTRONIC EQUIPMENT",
      "nativeMetadata": {},
      "durationSec": 7.631938,
      "tags": {
        "basic_acoustic": {
          "c50": 58.481705,
          "channels": 1,
          "dnsmos_bak": 1.24526,
          "dnsmos_ovrl": 1.201118,
          "dnsmos_p808": 2.378937,
          "dnsmos_sig": 1.471661,
          "duration_sec": 7.631938,
          "sample_rate_hz": 16000,
          "silence_ratio": 0,
          "silence_segments": [],
          "snr_db": -1.029779
        },
        "language_content": {
          "filler": 0,
          "language": "en",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "news_current_events/economy",
          "word_count": 18
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 23.457582,
          "far_field": null,
          "music": false,
          "rt60": 0.639492,
          "sound": []
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 18,
      "sampleId": "F01_050C0102_STR_REAL",
      "dataset": "CHiME4",
      "title": "Noisy speech: street vehicle",
      "note": "Phase2 sample with supplemented topic=news_current_events/economy and speaker flags multi/change/overlap=False/False/False.",
      "audio": "assets/audio/chime4_F01_050C0102_STR_REAL.wav",
      "transcript": "THE DEPARTMENT SAID THE DECLINE IN FACTORY JOBS WAS CONCENTRATED IN MOTOR VEHICLES AND ELECTRICAL AND ELECTRONIC EQUIPMENT",
      "nativeMetadata": {},
      "durationSec": 8.119813,
      "tags": {
        "basic_acoustic": {
          "c50": 59.116532,
          "channels": 1,
          "dnsmos_bak": 1.144401,
          "dnsmos_ovrl": 1.10276,
          "dnsmos_p808": 2.057701,
          "dnsmos_sig": 1.186638,
          "duration_sec": 8.119813,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.09727,
          "silence_segments": [
            {
              "end_sec": 0.65,
              "start_sec": 0
            },
            {
              "end_sec": 8.119813,
              "start_sec": 7.98
            }
          ],
          "snr_db": -0.018272
        },
        "language_content": {
          "filler": 0,
          "language": "en",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "news_current_events/economy",
          "word_count": 18
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 35.966741,
          "far_field": null,
          "music": false,
          "rt60": 0.114241,
          "sound": [
            "Vehicle"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 19,
      "sampleId": "F01_050C0103_BUS_REAL",
      "dataset": "CHiME4",
      "title": "Noisy speech: bus vehicle",
      "note": "Phase2 sample with supplemented topic=news_current_events/economy and speaker flags multi/change/overlap=False/False/False.",
      "audio": "assets/audio/chime4_F01_050C0103_BUS_REAL.wav",
      "transcript": "CONSTRUCTION EMPLOYMENT FELL FORTY SEVEN THOUSAND AFTER A FIFTEEN THOUSAND JOB DECLINE THE MONTH BEFORE",
      "nativeMetadata": {},
      "durationSec": 6.631687,
      "tags": {
        "basic_acoustic": {
          "c50": 49.615365,
          "channels": 1,
          "dnsmos_bak": 1.191416,
          "dnsmos_ovrl": 1.113726,
          "dnsmos_p808": 2.548175,
          "dnsmos_sig": 1.229232,
          "duration_sec": 6.631687,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.120887,
          "silence_segments": [
            {
              "end_sec": 0.39,
              "start_sec": 0
            },
            {
              "end_sec": 6.631687,
              "start_sec": 6.22
            }
          ],
          "snr_db": 0.633523
        },
        "language_content": {
          "filler": 0,
          "language": "en",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "news_current_events/economy",
          "word_count": 15
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 32.511555,
          "far_field": null,
          "music": false,
          "rt60": 0.204985,
          "sound": [
            "Vehicle"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 20,
      "sampleId": "F01_050C0104_CAF_REAL",
      "dataset": "CHiME4",
      "title": "Noisy speech: cafe music",
      "note": "Phase2 sample with supplemented topic=news_current_events/economy and speaker flags multi/change/overlap=False/False/False.",
      "audio": "assets/audio/chime4_F01_050C0104_CAF_REAL.wav",
      "transcript": "MINING EMPLOYMENT WHICH INCLUDES THE OIL AND GAS EXTRACTION INDUSTRY ROSE THREE THOUSAND AFTER A ONE THOUSAND JOB RISE",
      "nativeMetadata": {},
      "durationSec": 8.151813,
      "tags": {
        "basic_acoustic": {
          "c50": 41.376637,
          "channels": 1,
          "dnsmos_bak": 1.993115,
          "dnsmos_ovrl": 1.82285,
          "dnsmos_p808": 2.726842,
          "dnsmos_sig": 3.062713,
          "duration_sec": 8.151813,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.051522,
          "silence_segments": [
            {
              "end_sec": 0.42,
              "start_sec": 0
            }
          ],
          "snr_db": 1.25796
        },
        "language_content": {
          "filler": 0,
          "language": "en",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "news_current_events/economy",
          "word_count": 19
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 26.803802,
          "far_field": null,
          "music": false,
          "rt60": 0.361013,
          "sound": [
            "Music"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 21,
      "sampleId": "EN2001a_utterance_00000",
      "dataset": "AMI",
      "title": "AMI smoke: coordination topic",
      "note": "Phase2 sample with supplemented topic=meeting_workflow/coordination and speaker flags multi/change/overlap=True/True/False.",
      "audio": "assets/audio/ami_EN2001a_utterance_00000.wav",
      "transcript": "'Kay. Gosh. Okay. 'Kay. Does anyone want to see uh Steve's feedback from the specification? Is there much more in it than he d I I dry-read it the last time.. Right. Is there much more in it than he said yesterday?",
      "nativeMetadata": {},
      "durationSec": 18.436,
      "tags": {
        "basic_acoustic": {
          "c50": 46.155208,
          "channels": 1,
          "dnsmos_bak": 3.974983,
          "dnsmos_ovrl": 2.678807,
          "dnsmos_p808": 2.823182,
          "dnsmos_sig": 3.089926,
          "duration_sec": 18.436,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.503688,
          "silence_segments": [
            {
              "end_sec": 2.89,
              "start_sec": 0
            },
            {
              "end_sec": 7.82,
              "start_sec": 3.75
            },
            {
              "end_sec": 8.41,
              "start_sec": 8.36
            },
            {
              "end_sec": 12.06,
              "start_sec": 11.49
            },
            {
              "end_sec": 14.25,
              "start_sec": 13.04
            },
            {
              "end_sec": 16.26,
              "start_sec": 15.91
            },
            {
              "end_sec": 18.436,
              "start_sec": 18.29
            }
          ],
          "snr_db": 13.128118
        },
        "language_content": {
          "filler": 1,
          "language": "en",
          "punctuation": {
            "has_terminal_punctuation": true,
            "punctuation_count": 13
          },
          "repetition": {
            "has_repetition": true,
            "repetition_count": 1
          },
          "topic": "meeting_workflow/coordination",
          "word_count": 43
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 31.111448,
          "far_field": null,
          "music": false,
          "rt60": 0.08687,
          "sound": []
        },
        "speaker": {
          "multi_speaker": true,
          "speaker_change": true,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 22,
      "sampleId": "EN2001a_utterance_00001",
      "dataset": "AMI",
      "title": "AMI smoke: project planning topic",
      "note": "Phase2 sample with supplemented topic=meeting_workflow/coordination and speaker flags multi/change/overlap=True/True/True.",
      "audio": "assets/audio/ami_EN2001a_utterance_00001.wav",
      "transcript": "Not really, um just what he's talking about, like duplication of effort and Mm. Hmm. Hmm? Like duplication of effort and stuff, and um yeah, he was saying that we should maybe uh think about having a prototype for week six, which is next week. Yeah. Next week.",
      "nativeMetadata": {},
      "durationSec": 20.084,
      "tags": {
        "basic_acoustic": {
          "c50": 59.211175,
          "channels": 1,
          "dnsmos_bak": 3.981168,
          "dnsmos_ovrl": 2.83701,
          "dnsmos_p808": 3.071224,
          "dnsmos_sig": 3.251212,
          "duration_sec": 20.084,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.294463,
          "silence_segments": [
            {
              "end_sec": 0.3,
              "start_sec": 0
            },
            {
              "end_sec": 2.05,
              "start_sec": 1.88
            },
            {
              "end_sec": 6.96,
              "start_sec": 4.82
            },
            {
              "end_sec": 10.88,
              "start_sec": 9.7
            },
            {
              "end_sec": 11.74,
              "start_sec": 11.68
            },
            {
              "end_sec": 13.4,
              "start_sec": 13.28
            },
            {
              "end_sec": 15.66,
              "start_sec": 15.4
            },
            {
              "end_sec": 17.42,
              "start_sec": 16.74
            },
            {
              "end_sec": 18.51,
              "start_sec": 18.46
            },
            {
              "end_sec": 20.084,
              "start_sec": 19.13
            }
          ],
          "snr_db": 19.056463
        },
        "language_content": {
          "filler": 8,
          "language": "en",
          "punctuation": {
            "has_terminal_punctuation": true,
            "punctuation_count": 12
          },
          "repetition": {
            "has_repetition": true,
            "repetition_count": 1
          },
          "topic": "meeting_workflow/coordination",
          "word_count": 48
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 36.399061,
          "far_field": null,
          "music": false,
          "rt60": 0.067474,
          "sound": [
            "Clicking"
          ]
        },
        "speaker": {
          "multi_speaker": true,
          "speaker_change": true,
          "speaker_overlap": true
        }
      }
    },
    {
      "row": 23,
      "sampleId": "EN2001a_utterance_00003",
      "dataset": "AMI",
      "title": "Meeting speech: technical talk",
      "note": "Phase2 sample with supplemented topic=meeting_workflow/coordination and speaker flags multi/change/overlap=False/False/False.",
      "audio": "assets/audio/ami_EN2001a_utterance_00003.wav",
      "transcript": "well go back first of all and look at NITE X_M_L_ to see in how far that that which we want is compatible with that which NITE X_M_L_ offers us. And then just sort of everyone make sure everyone understand the interface. Yeah.",
      "nativeMetadata": {},
      "durationSec": 14.1115,
      "tags": {
        "basic_acoustic": {
          "c50": 59.024882,
          "channels": 1,
          "dnsmos_bak": 4.081535,
          "dnsmos_ovrl": 2.791316,
          "dnsmos_p808": 3.228106,
          "dnsmos_sig": 3.086606,
          "duration_sec": 14.1115,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.261595,
          "silence_segments": [
            {
              "end_sec": 0.8,
              "start_sec": 0
            },
            {
              "end_sec": 4.19,
              "start_sec": 3.97
            },
            {
              "end_sec": 6.63,
              "start_sec": 6.52
            },
            {
              "end_sec": 8.01,
              "start_sec": 7.74
            },
            {
              "end_sec": 10.45,
              "start_sec": 9.2
            },
            {
              "end_sec": 14.1115,
              "start_sec": 13.07
            }
          ],
          "snr_db": 24.190242
        },
        "language_content": {
          "filler": 1,
          "language": "en",
          "punctuation": {
            "has_terminal_punctuation": true,
            "punctuation_count": 9
          },
          "repetition": {
            "has_repetition": true,
            "repetition_count": 1
          },
          "topic": "meeting_workflow/coordination",
          "word_count": 47
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 35.861222,
          "far_field": null,
          "music": false,
          "rt60": 0.066785,
          "sound": []
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 24,
      "sampleId": "EN2001a_utterance_00005",
      "dataset": "AMI",
      "title": "Meeting speech: short turns",
      "note": "Phase2 sample with supplemented topic=technology_engineering/software_engineering and speaker flags multi/change/overlap=True/True/True.",
      "audio": "assets/audio/ami_EN2001a_utterance_00005.wav",
      "transcript": "Hmm? The basic word importance is off-line as well. The combined measure might not be if we want to wait what the user has typed in into the search. Yeah. Okay. Okay.",
      "nativeMetadata": {},
      "durationSec": 17.5105,
      "tags": {
        "basic_acoustic": {
          "c50": 51.30534,
          "channels": 1,
          "dnsmos_bak": 3.484097,
          "dnsmos_ovrl": 1.926559,
          "dnsmos_p808": 3.163394,
          "dnsmos_sig": 2.574438,
          "duration_sec": 17.5105,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.450044,
          "silence_segments": [
            {
              "end_sec": 7.01,
              "start_sec": 0
            },
            {
              "end_sec": 7.8,
              "start_sec": 7.74
            },
            {
              "end_sec": 10.07,
              "start_sec": 9.86
            },
            {
              "end_sec": 14.03,
              "start_sec": 13.77
            },
            {
              "end_sec": 16.68,
              "start_sec": 16.49
            },
            {
              "end_sec": 17.5105,
              "start_sec": 17.36
            }
          ],
          "snr_db": 30.15965
        },
        "language_content": {
          "filler": 2,
          "language": "en",
          "punctuation": {
            "has_terminal_punctuation": true,
            "punctuation_count": 7
          },
          "repetition": {
            "has_repetition": true,
            "repetition_count": 1
          },
          "topic": "technology_engineering/software_engineering",
          "word_count": 33
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 35.235287,
          "far_field": null,
          "music": false,
          "rt60": 0.069148,
          "sound": []
        },
        "speaker": {
          "multi_speaker": true,
          "speaker_change": true,
          "speaker_overlap": true
        }
      }
    },
    {
      "row": 25,
      "sampleId": "EN2001a_utterance_00006",
      "dataset": "AMI",
      "title": "Meeting speech: clicking",
      "note": "Phase2 sample with supplemented topic=technology_engineering/software_engineering and speaker flags multi/change/overlap=True/True/True.",
      "audio": "assets/audio/ami_EN2001a_utterance_00006.wav",
      "transcript": "Uh mine's gonna be mostly using the off-line. But the actual stuff it's doing will be on-line. But it won't be very um processor intensive or memory intensive, I don't think. 'Kay. So basically apart from the display module, the i the display itself, we don't have an extremely high degree of interaction between sort of our modules that create the stuff and and the interface, so the interface is mainly while it's running just working on data that's just loaded from a file, I guess.",
      "nativeMetadata": {},
      "durationSec": 29.6035,
      "tags": {
        "basic_acoustic": {
          "c50": 57.797446,
          "channels": 1,
          "dnsmos_bak": 4.043649,
          "dnsmos_ovrl": 2.612575,
          "dnsmos_p808": 3.351632,
          "dnsmos_sig": 2.916934,
          "duration_sec": 29.6035,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.149763,
          "silence_segments": [
            {
              "end_sec": 0.3,
              "start_sec": 0
            },
            {
              "end_sec": 2.38,
              "start_sec": 2.03
            },
            {
              "end_sec": 7.21,
              "start_sec": 6.47
            },
            {
              "end_sec": 10.92,
              "start_sec": 10.72
            },
            {
              "end_sec": 13.59,
              "start_sec": 13.3
            },
            {
              "end_sec": 18.6,
              "start_sec": 17.98
            },
            {
              "end_sec": 19.54,
              "start_sec": 19.1
            },
            {
              "end_sec": 20.26,
              "start_sec": 20.22
            },
            {
              "end_sec": 21.85,
              "start_sec": 21.79
            },
            {
              "end_sec": 23.55,
              "start_sec": 23.31
            },
            {
              "end_sec": 25.04,
              "start_sec": 24.85
            },
            {
              "end_sec": 27.2,
              "start_sec": 27.03
            },
            {
              "end_sec": 29.6035,
              "start_sec": 28.81
            }
          ],
          "snr_db": 38.04082
        },
        "language_content": {
          "filler": 2,
          "language": "en",
          "punctuation": {
            "has_terminal_punctuation": true,
            "punctuation_count": 20
          },
          "repetition": {
            "has_repetition": true,
            "repetition_count": 1
          },
          "topic": "technology_engineering/software_engineering",
          "word_count": 88
        },
        "sound_field_scene": {
          "audio_events": [
            "speech"
          ],
          "c50": 35.693252,
          "far_field": null,
          "music": false,
          "rt60": 0.06477,
          "sound": [
            "Clicking"
          ]
        },
        "speaker": {
          "multi_speaker": true,
          "speaker_change": true,
          "speaker_overlap": true
        }
      }
    },
    {
      "row": 26,
      "sampleId": "airport-barcelona-0-0-a",
      "dataset": "TUT Urban Acoustic Scenes 2018",
      "title": "Urban scene: airport",
      "note": "Phase2 non-transcript sample; topic=other/insufficient_context, speaker flags=True/False/False.",
      "audio": "assets/audio/tut2018_airport-barcelona-0-0-a.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 10,
      "tags": {
        "basic_acoustic": {
          "c50": 26.950598,
          "channels": 1,
          "dnsmos_bak": 1.791894,
          "dnsmos_ovrl": 1.376679,
          "dnsmos_p808": 2.270874,
          "dnsmos_sig": 1.963975,
          "duration_sec": 10,
          "sample_rate_hz": 16000,
          "silence_ratio": 1,
          "silence_segments": [
            {
              "end_sec": 10,
              "start_sec": 0
            }
          ],
          "snr_db": -0.630383
        },
        "language_content": {
          "filler": 0,
          "language": "unknown",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "other/insufficient_context",
          "word_count": 0
        },
        "sound_field_scene": {
          "audio_events": [],
          "c50": 23.755765,
          "far_field": null,
          "music": false,
          "rt60": 0.598329,
          "sound": []
        },
        "speaker": {
          "multi_speaker": true,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 27,
      "sampleId": "bus-barcelona-15-599-a",
      "dataset": "TUT Urban Acoustic Scenes 2018",
      "title": "Urban scene: bus",
      "note": "Phase2 non-transcript sample; topic=other/insufficient_context, speaker flags=False/False/False.",
      "audio": "assets/audio/tut2018_bus-barcelona-15-599-a.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 10,
      "tags": {
        "basic_acoustic": {
          "c50": 14.687956,
          "channels": 1,
          "dnsmos_bak": 1.757045,
          "dnsmos_ovrl": 1.304132,
          "dnsmos_p808": 2.259291,
          "dnsmos_sig": 1.888589,
          "duration_sec": 10,
          "sample_rate_hz": 16000,
          "silence_ratio": 1,
          "silence_segments": [
            {
              "end_sec": 10,
              "start_sec": 0
            }
          ],
          "snr_db": -4.011834
        },
        "language_content": {
          "filler": 0,
          "language": "unknown",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "other/insufficient_context",
          "word_count": 0
        },
        "sound_field_scene": {
          "audio_events": [],
          "c50": 23.701139,
          "far_field": null,
          "music": false,
          "rt60": 0.478917,
          "sound": []
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 28,
      "sampleId": "metro-barcelona-41-1221-a",
      "dataset": "TUT Urban Acoustic Scenes 2018",
      "title": "Urban scene: metro",
      "note": "Phase2 non-transcript sample; topic=other/insufficient_context, speaker flags=True/True/False.",
      "audio": "assets/audio/tut2018_metro-barcelona-41-1221-a.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 10,
      "tags": {
        "basic_acoustic": {
          "c50": 5.682715,
          "channels": 1,
          "dnsmos_bak": 1.168768,
          "dnsmos_ovrl": 1.106247,
          "dnsmos_p808": 2.390622,
          "dnsmos_sig": 1.217053,
          "duration_sec": 10,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.197,
          "silence_segments": [
            {
              "end_sec": 3.27,
              "start_sec": 3.12
            },
            {
              "end_sec": 4.62,
              "start_sec": 4.48
            },
            {
              "end_sec": 7.36,
              "start_sec": 5.68
            }
          ],
          "snr_db": -0.68653
        },
        "language_content": {
          "filler": 0,
          "language": "unknown",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "other/insufficient_context",
          "word_count": 0
        },
        "sound_field_scene": {
          "audio_events": [
            "speech",
            "singing",
            "music"
          ],
          "c50": 9.471988,
          "far_field": null,
          "music": true,
          "rt60": 0.327513,
          "sound": [
            "Train",
            "Rail transport"
          ]
        },
        "speaker": {
          "multi_speaker": true,
          "speaker_change": true,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 29,
      "sampleId": "park-barcelona-89-2429-a",
      "dataset": "TUT Urban Acoustic Scenes 2018",
      "title": "Urban scene: park",
      "note": "Phase2 non-transcript sample; topic=other/insufficient_context, speaker flags=False/False/False.",
      "audio": "assets/audio/tut2018_park-barcelona-89-2429-a.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 10,
      "tags": {
        "basic_acoustic": {
          "c50": 22.983443,
          "channels": 1,
          "dnsmos_bak": 3.137387,
          "dnsmos_ovrl": 1.643358,
          "dnsmos_p808": 2.137449,
          "dnsmos_sig": 2.202087,
          "duration_sec": 10,
          "sample_rate_hz": 16000,
          "silence_ratio": 1,
          "silence_segments": [
            {
              "end_sec": 10,
              "start_sec": 0
            }
          ],
          "snr_db": -3.138264
        },
        "language_content": {
          "filler": 0,
          "language": "unknown",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "other/insufficient_context",
          "word_count": 0
        },
        "sound_field_scene": {
          "audio_events": [],
          "c50": 22.313892,
          "far_field": null,
          "music": false,
          "rt60": 0.274599,
          "sound": []
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 30,
      "sampleId": "street_traffic-barcelona-161-4901-a",
      "dataset": "TUT Urban Acoustic Scenes 2018",
      "title": "Scene contrast: street traffic",
      "note": "Phase2 non-transcript sample; topic=other/insufficient_context, speaker flags=False/False/False.",
      "audio": "assets/audio/tut2018_street_traffic-barcelona-161-4901-a.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 10,
      "tags": {
        "basic_acoustic": {
          "c50": 19.665466,
          "channels": 1,
          "dnsmos_bak": 1.218397,
          "dnsmos_ovrl": null,
          "dnsmos_p808": 2.286138,
          "dnsmos_sig": 1.381033,
          "duration_sec": 10,
          "sample_rate_hz": 16000,
          "silence_ratio": 1,
          "silence_segments": [
            {
              "end_sec": 10,
              "start_sec": 0
            }
          ],
          "snr_db": -4.8527
        },
        "language_content": {
          "filler": 0,
          "language": "unknown",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "other/insufficient_context",
          "word_count": 0
        },
        "sound_field_scene": {
          "audio_events": [],
          "c50": 9.521883,
          "far_field": null,
          "music": false,
          "rt60": 1.313299,
          "sound": [
            "Vehicle"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 31,
      "sampleId": "babble",
      "dataset": "NOISEX-92",
      "title": "NOISEX noise: babble",
      "note": "Phase2 non-transcript sample; topic=other/insufficient_context, speaker flags=False/False/False.",
      "audio": "assets/audio/noisex92_babble.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 10,
      "tags": {
        "basic_acoustic": {
          "c50": 13.457497,
          "channels": 1,
          "dnsmos_bak": 1.132139,
          "dnsmos_ovrl": 1.095176,
          "dnsmos_p808": 2.211675,
          "dnsmos_sig": 1.173304,
          "duration_sec": 10,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.032,
          "silence_segments": [
            {
              "end_sec": 3.78,
              "start_sec": 3.46
            }
          ],
          "snr_db": -2.734259
        },
        "language_content": {
          "filler": 0,
          "language": "unknown",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "other/insufficient_context",
          "word_count": 0
        },
        "sound_field_scene": {
          "audio_events": [
            "speech",
            "singing",
            "music"
          ],
          "c50": 19.780616,
          "far_field": null,
          "music": true,
          "rt60": 0.655484,
          "sound": [
            "Chatter"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 32,
      "sampleId": "f16",
      "dataset": "NOISEX-92",
      "title": "NOISEX noise: f16",
      "note": "Phase2 non-transcript sample; topic=other/insufficient_context, speaker flags=False/False/False.",
      "audio": "assets/audio/noisex92_f16.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 10,
      "tags": {
        "basic_acoustic": {
          "c50": 23.014076,
          "channels": 1,
          "dnsmos_bak": 1.124258,
          "dnsmos_ovrl": 1.079335,
          "dnsmos_p808": 2.188886,
          "dnsmos_sig": 1.157146,
          "duration_sec": 10,
          "sample_rate_hz": 16000,
          "silence_ratio": 1,
          "silence_segments": [
            {
              "end_sec": 10,
              "start_sec": 0
            }
          ],
          "snr_db": -5.685234
        },
        "language_content": {
          "filler": 0,
          "language": "unknown",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "other/insufficient_context",
          "word_count": 0
        },
        "sound_field_scene": {
          "audio_events": [],
          "c50": 11.618528,
          "far_field": null,
          "music": false,
          "rt60": 1.085791,
          "sound": [
            "Train",
            "Rail transport",
            "Railroad car, train wagon",
            "Train wheels squealing",
            "Subway, metro, underground",
            "Vehicle"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 33,
      "sampleId": "factory1",
      "dataset": "NOISEX-92",
      "title": "NOISEX noise: factory1",
      "note": "Phase2 non-transcript sample; topic=other/insufficient_context, speaker flags=False/False/False.",
      "audio": "assets/audio/noisex92_factory1.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 10,
      "tags": {
        "basic_acoustic": {
          "c50": 22.166993,
          "channels": 1,
          "dnsmos_bak": 1.096926,
          "dnsmos_ovrl": 1.083776,
          "dnsmos_p808": 2.135229,
          "dnsmos_sig": 1.139457,
          "duration_sec": 10,
          "sample_rate_hz": 16000,
          "silence_ratio": 1,
          "silence_segments": [
            {
              "end_sec": 10,
              "start_sec": 0
            }
          ],
          "snr_db": -0.386923
        },
        "language_content": {
          "filler": 0,
          "language": "unknown",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "other/insufficient_context",
          "word_count": 0
        },
        "sound_field_scene": {
          "audio_events": [
            "music"
          ],
          "c50": 15.789183,
          "far_field": null,
          "music": true,
          "rt60": 0.806082,
          "sound": [
            "Vehicle",
            "Train"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 34,
      "sampleId": "machinegun",
      "dataset": "NOISEX-92",
      "title": "NOISEX noise: machinegun",
      "note": "Phase2 non-transcript sample; topic=other/insufficient_context, speaker flags=False/False/False.",
      "audio": "assets/audio/noisex92_machinegun.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 10,
      "tags": {
        "basic_acoustic": {
          "c50": 22.828918,
          "channels": 1,
          "dnsmos_bak": null,
          "dnsmos_ovrl": 1.033274,
          "dnsmos_p808": 2.437489,
          "dnsmos_sig": 1.053353,
          "duration_sec": 10,
          "sample_rate_hz": 16000,
          "silence_ratio": 1,
          "silence_segments": [
            {
              "end_sec": 10,
              "start_sec": 0
            }
          ],
          "snr_db": 0.631293
        },
        "language_content": {
          "filler": 0,
          "language": "unknown",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "other/insufficient_context",
          "word_count": 0
        },
        "sound_field_scene": {
          "audio_events": [],
          "c50": 28.365829,
          "far_field": null,
          "music": false,
          "rt60": 0.234428,
          "sound": [
            "Fireworks"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 35,
      "sampleId": "volvo",
      "dataset": "NOISEX-92",
      "title": "NOISEX noise: volvo",
      "note": "Phase2 non-transcript sample; topic=other/insufficient_context, speaker flags=False/False/False.",
      "audio": "assets/audio/noisex92_volvo.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 10,
      "tags": {
        "basic_acoustic": {
          "c50": 22.891291,
          "channels": 1,
          "dnsmos_bak": 2.630833,
          "dnsmos_ovrl": 1.777615,
          "dnsmos_p808": 2.312987,
          "dnsmos_sig": 2.497058,
          "duration_sec": 10,
          "sample_rate_hz": 16000,
          "silence_ratio": 1,
          "silence_segments": [
            {
              "end_sec": 10,
              "start_sec": 0
            }
          ],
          "snr_db": -2.497315
        },
        "language_content": {
          "filler": 0,
          "language": "unknown",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "other/insufficient_context",
          "word_count": 0
        },
        "sound_field_scene": {
          "audio_events": [],
          "c50": 23.418424,
          "far_field": null,
          "music": false,
          "rt60": 0.36418,
          "sound": [
            "Vehicle"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 36,
      "sampleId": "050a0501_1.7783_442o030z_-1.7783",
      "dataset": "WHAM! noise",
      "title": "WHAM noise: 050a0501",
      "note": "Phase2 non-transcript sample; topic=other/insufficient_context, speaker flags=False/False/False.",
      "audio": "assets/audio/wham_noise_050a0501_1.7783_442o030z_-1.7783.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 8.933063,
      "tags": {
        "basic_acoustic": {
          "c50": 0.239741,
          "channels": 1,
          "dnsmos_bak": 1.124113,
          "dnsmos_ovrl": 1.099806,
          "dnsmos_p808": 2.082404,
          "dnsmos_sig": 1.16793,
          "duration_sec": 8.933063,
          "sample_rate_hz": 16000,
          "silence_ratio": 0,
          "silence_segments": [],
          "snr_db": -0.043474
        },
        "language_content": {
          "filler": 0,
          "language": "unknown",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "other/insufficient_context",
          "word_count": 0
        },
        "sound_field_scene": {
          "audio_events": [
            "speech",
            "singing",
            "music"
          ],
          "c50": 2.989179,
          "far_field": null,
          "music": true,
          "rt60": 0.847052,
          "sound": [
            "Music"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 37,
      "sampleId": "050a0502_1.3461_440o030j_-1.3461",
      "dataset": "WHAM! noise",
      "title": "WHAM noise: 050a0502",
      "note": "Phase2 non-transcript sample; topic=other/insufficient_context, speaker flags=False/False/False.",
      "audio": "assets/audio/wham_noise_050a0502_1.3461_440o030j_-1.3461.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 7.67725,
      "tags": {
        "basic_acoustic": {
          "c50": 4.649517,
          "channels": 1,
          "dnsmos_bak": 1.180672,
          "dnsmos_ovrl": 1.152892,
          "dnsmos_p808": 2.069903,
          "dnsmos_sig": 1.286774,
          "duration_sec": 7.67725,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.614445,
          "silence_segments": [
            {
              "end_sec": 1.22,
              "start_sec": 0
            },
            {
              "end_sec": 1.78,
              "start_sec": 1.72
            },
            {
              "end_sec": 7.67725,
              "start_sec": 4.24
            }
          ],
          "snr_db": -1.706969
        },
        "language_content": {
          "filler": 0,
          "language": "unknown",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "other/insufficient_context",
          "word_count": 0
        },
        "sound_field_scene": {
          "audio_events": [
            "singing",
            "music"
          ],
          "c50": 10.232371,
          "far_field": null,
          "music": true,
          "rt60": 0.646381,
          "sound": [
            "Music"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 38,
      "sampleId": "050a0504_2.4414_443o0313_-2.4414",
      "dataset": "WHAM! noise",
      "title": "WHAM noise: 050a0504",
      "note": "Phase2 non-transcript sample; topic=other/insufficient_context, speaker flags=False/False/False.",
      "audio": "assets/audio/wham_noise_050a0504_2.4414_443o0313_-2.4414.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 14.862375,
      "tags": {
        "basic_acoustic": {
          "c50": 2.851386,
          "channels": 1,
          "dnsmos_bak": null,
          "dnsmos_ovrl": null,
          "dnsmos_p808": 2.271575,
          "dnsmos_sig": 1.06195,
          "duration_sec": 14.862375,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.856685,
          "silence_segments": [
            {
              "end_sec": 14.862375,
              "start_sec": 2.13
            }
          ],
          "snr_db": -2.198489
        },
        "language_content": {
          "filler": 0,
          "language": "unknown",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "other/insufficient_context",
          "word_count": 0
        },
        "sound_field_scene": {
          "audio_events": [
            "singing",
            "music"
          ],
          "c50": 12.991443,
          "far_field": null,
          "music": true,
          "rt60": 0.509971,
          "sound": []
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 39,
      "sampleId": "050a0505_1.5097_440o030d_-1.5097",
      "dataset": "WHAM! noise",
      "title": "WHAM noise: 050a0505",
      "note": "Phase2 non-transcript sample; topic=other/insufficient_context, speaker flags=False/False/False.",
      "audio": "assets/audio/wham_noise_050a0505_1.5097_440o030d_-1.5097.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 16.645563,
      "tags": {
        "basic_acoustic": {
          "c50": 5.828026,
          "channels": 1,
          "dnsmos_bak": 1.114653,
          "dnsmos_ovrl": 1.092363,
          "dnsmos_p808": 2.259722,
          "dnsmos_sig": 1.154104,
          "duration_sec": 16.645563,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.424137,
          "silence_segments": [
            {
              "end_sec": 6.01,
              "start_sec": 0
            },
            {
              "end_sec": 10.95,
              "start_sec": 10.83
            },
            {
              "end_sec": 12.68,
              "start_sec": 11.75
            }
          ],
          "snr_db": -0.901143
        },
        "language_content": {
          "filler": 0,
          "language": "unknown",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "other/insufficient_context",
          "word_count": 0
        },
        "sound_field_scene": {
          "audio_events": [
            "speech",
            "singing",
            "music"
          ],
          "c50": 2.296683,
          "far_field": null,
          "music": true,
          "rt60": 0.852284,
          "sound": [
            "Music"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 40,
      "sampleId": "050a0506_1.7744_447c0213_-1.7744",
      "dataset": "WHAM! noise",
      "title": "WHAM noise: 050a0506",
      "note": "Phase2 non-transcript sample; topic=other/insufficient_context, speaker flags=False/False/False.",
      "audio": "assets/audio/wham_noise_050a0506_1.7744_447c0213_-1.7744.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 8.55,
      "tags": {
        "basic_acoustic": {
          "c50": -1.159664,
          "channels": 1,
          "dnsmos_bak": 1.140086,
          "dnsmos_ovrl": 1.058404,
          "dnsmos_p808": 2.192073,
          "dnsmos_sig": 1.242453,
          "duration_sec": 8.55,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.511111,
          "silence_segments": [
            {
              "end_sec": 1.77,
              "start_sec": 0
            },
            {
              "end_sec": 8.55,
              "start_sec": 5.95
            }
          ],
          "snr_db": -0.679746
        },
        "language_content": {
          "filler": 0,
          "language": "unknown",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": "other/insufficient_context",
          "word_count": 0
        },
        "sound_field_scene": {
          "audio_events": [
            "speech",
            "singing",
            "music"
          ],
          "c50": 2.547839,
          "far_field": null,
          "music": true,
          "rt60": 0.914263,
          "sound": [
            "Music"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "speaker_change": false,
          "speaker_overlap": false
        }
      }
    }
  ],
  "amiAnalysis": {
    "title": "AMI EN2001a 切分与标注对比",
    "splitLogic": {
      "sourceScript": "scripts/prepare_ami_utterances.py",
      "sourceMeeting": "EN2001a.Mix-Headset.wav",
      "sourceAnnotation": "EN2001a.jsonl",
      "minDurationSec": 10,
      "targetDurationSec": 20,
      "maxDurationSec": 30,
      "endpointPaddingSec": 0.5,
      "totalSegments": 195,
      "durationSec": {
        "min": 10.508,
        "median": 22.98,
        "mean": 26.31,
        "max": 76.415
      },
      "utteranceCount": {
        "min": 1,
        "mean": 4.85,
        "max": 15
      },
      "speakerCount": {
        "min": 1,
        "mean": 2.52,
        "max": 5
      },
      "rules": [
        "先把原始 utterance 标注合并成全局 speech activity 区间。",
        "候选切分点只放在无说话人的间隙：开头 activity 前 0.5s、相邻 speech activity 的中点、最后 activity 后 0.5s。",
        "用动态规划选择候选切分点，使每段尽量接近 20s，同时满足 10s 最小时长。",
        "超过 30s 会被强惩罚，但如果长重叠/长 utterance 不可再切，仍允许保留长段。",
        "每个切片保留 shifted utterances/words metadata，用于 deterministic VAD 和 speaker 标签。"
      ]
    },
    "comparison": {
      "phase2Label": "phase2 AMI 无原生标注输入",
      "annotatedLabel": "ami_en2001a 有 utterance 标注输入",
      "comparedSampleCount": 5,
      "phase2Manifest": "phase2_asr_sample/manifest.jsonl",
      "annotatedManifest": "ami_en2001a_utterances/manifest.jsonl",
      "phase2Tags": "outputs/phase2_full_pipeline_topic_speaker_tags.jsonl",
      "annotatedTags": "outputs/ami_en2001a_annotated_phase2_ami_tags.jsonl",
      "samples": [
        {
          "sampleId": "EN2001a_utterance_00000",
          "transcript": "'Kay. Gosh. Okay. 'Kay. Does anyone want to see uh Steve's feedback from the specification? Is there much more in it than he d I I dry-read it the last time.. Right. Is there much more in it than he said yesterday?",
          "durationSec": 18.436,
          "phase2": {
            "row": 21,
            "nativeMetadataKeys": [],
            "vadRoute": "FireRed VAD fallback",
            "speakerRoute": "MOSS diarize fallback",
            "topicRoute": "OpenAI Responses",
            "tags": {
              "topic": "meeting_workflow/coordination",
              "silenceRatio": 0.503688,
              "silenceSegmentCount": 7,
              "speaker": {
                "multi_speaker": true,
                "speaker_change": true,
                "speaker_overlap": false
              }
            }
          },
          "annotated": {
            "row": 1,
            "nativeMetadataKeys": [
              "audio_id",
              "end",
              "start",
              "utterances"
            ],
            "vadRoute": "native_metadata_vad",
            "speakerRoute": "native_metadata_diarizer",
            "topicRoute": "OpenAI Responses",
            "utteranceCount": 9,
            "speakerCount": 3,
            "speakers": [
              "A",
              "D",
              "E"
            ],
            "tags": {
              "topic": "meeting_workflow/coordination",
              "silenceRatio": 0.424441,
              "silenceSegmentCount": 6,
              "speaker": {
                "multi_speaker": true,
                "speaker_change": true,
                "speaker_overlap": true
              }
            }
          },
          "delta": {
            "silenceRatio": -0.079247,
            "topicChanged": false,
            "speakerChanged": true
          }
        },
        {
          "sampleId": "EN2001a_utterance_00001",
          "transcript": "Not really, um just what he's talking about, like duplication of effort and Mm. Hmm. Hmm? Like duplication of effort and stuff, and um yeah, he was saying that we should maybe uh think about having a prototype for week six, which is next week. Yeah. Next week.",
          "durationSec": 20.084,
          "phase2": {
            "row": 22,
            "nativeMetadataKeys": [],
            "vadRoute": "FireRed VAD fallback",
            "speakerRoute": "MOSS diarize fallback",
            "topicRoute": "OpenAI Responses",
            "tags": {
              "topic": "meeting_workflow/coordination",
              "silenceRatio": 0.294463,
              "silenceSegmentCount": 10,
              "speaker": {
                "multi_speaker": true,
                "speaker_change": true,
                "speaker_overlap": true
              }
            }
          },
          "annotated": {
            "row": 2,
            "nativeMetadataKeys": [
              "audio_id",
              "end",
              "start",
              "utterances"
            ],
            "vadRoute": "native_metadata_vad",
            "speakerRoute": "native_metadata_diarizer",
            "topicRoute": "OpenAI Responses",
            "utteranceCount": 5,
            "speakerCount": 3,
            "speakers": [
              "A",
              "D",
              "E"
            ],
            "tags": {
              "topic": "business_management/project_management",
              "silenceRatio": 0.093856,
              "silenceSegmentCount": 3,
              "speaker": {
                "multi_speaker": true,
                "speaker_change": true,
                "speaker_overlap": true
              }
            }
          },
          "delta": {
            "silenceRatio": -0.200607,
            "topicChanged": true,
            "speakerChanged": false
          }
        },
        {
          "sampleId": "EN2001a_utterance_00003",
          "transcript": "well go back first of all and look at NITE X_M_L_ to see in how far that that which we want is compatible with that which NITE X_M_L_ offers us. And then just sort of everyone make sure everyone understand the interface. Yeah.",
          "durationSec": 14.1115,
          "phase2": {
            "row": 23,
            "nativeMetadataKeys": [],
            "vadRoute": "FireRed VAD fallback",
            "speakerRoute": "MOSS diarize fallback",
            "topicRoute": "OpenAI Responses",
            "tags": {
              "topic": "meeting_workflow/coordination",
              "silenceRatio": 0.261595,
              "silenceSegmentCount": 6,
              "speaker": {
                "multi_speaker": false,
                "speaker_change": false,
                "speaker_overlap": false
              }
            }
          },
          "annotated": {
            "row": 4,
            "nativeMetadataKeys": [
              "audio_id",
              "end",
              "start",
              "utterances"
            ],
            "vadRoute": "native_metadata_vad",
            "speakerRoute": "native_metadata_diarizer",
            "topicRoute": "OpenAI Responses",
            "utteranceCount": 2,
            "speakerCount": 2,
            "speakers": [
              "A",
              "E"
            ],
            "tags": {
              "topic": "technology_engineering/software_engineering",
              "silenceRatio": 0.13489,
              "silenceSegmentCount": 2,
              "speaker": {
                "multi_speaker": true,
                "speaker_change": true,
                "speaker_overlap": true
              }
            }
          },
          "delta": {
            "silenceRatio": -0.126705,
            "topicChanged": true,
            "speakerChanged": true
          }
        },
        {
          "sampleId": "EN2001a_utterance_00005",
          "transcript": "Hmm? The basic word importance is off-line as well. The combined measure might not be if we want to wait what the user has typed in into the search. Yeah. Okay. Okay.",
          "durationSec": 17.5105,
          "phase2": {
            "row": 24,
            "nativeMetadataKeys": [],
            "vadRoute": "FireRed VAD fallback",
            "speakerRoute": "MOSS diarize fallback",
            "topicRoute": "OpenAI Responses",
            "tags": {
              "topic": "technology_engineering/software_engineering",
              "silenceRatio": 0.450044,
              "silenceSegmentCount": 6,
              "speaker": {
                "multi_speaker": true,
                "speaker_change": true,
                "speaker_overlap": true
              }
            }
          },
          "annotated": {
            "row": 6,
            "nativeMetadataKeys": [
              "audio_id",
              "end",
              "start",
              "utterances"
            ],
            "vadRoute": "native_metadata_vad",
            "speakerRoute": "native_metadata_diarizer",
            "topicRoute": "OpenAI Responses",
            "utteranceCount": 5,
            "speakerCount": 2,
            "speakers": [
              "C",
              "E"
            ],
            "tags": {
              "topic": "technology_engineering/artificial_intelligence",
              "silenceRatio": 0.396305,
              "silenceSegmentCount": 4,
              "speaker": {
                "multi_speaker": true,
                "speaker_change": true,
                "speaker_overlap": true
              }
            }
          },
          "delta": {
            "silenceRatio": -0.053739,
            "topicChanged": true,
            "speakerChanged": false
          }
        },
        {
          "sampleId": "EN2001a_utterance_00006",
          "transcript": "Uh mine's gonna be mostly using the off-line. But the actual stuff it's doing will be on-line. But it won't be very um processor intensive or memory intensive, I don't think. 'Kay. So basically apart from the display module, the i the display itself, we don't have an extremely high degree of interaction between sort of our modules that create the stuff and and the interface, so the interface is mainly while it's running just working on data that's just loaded from a file, I guess.",
          "durationSec": 29.6035,
          "phase2": {
            "row": 25,
            "nativeMetadataKeys": [],
            "vadRoute": "FireRed VAD fallback",
            "speakerRoute": "MOSS diarize fallback",
            "topicRoute": "OpenAI Responses",
            "tags": {
              "topic": "technology_engineering/software_engineering",
              "silenceRatio": 0.149763,
              "silenceSegmentCount": 13,
              "speaker": {
                "multi_speaker": true,
                "speaker_change": true,
                "speaker_overlap": true
              }
            }
          },
          "annotated": {
            "row": 7,
            "nativeMetadataKeys": [
              "audio_id",
              "end",
              "start",
              "utterances"
            ],
            "vadRoute": "native_metadata_vad",
            "speakerRoute": "native_metadata_diarizer",
            "topicRoute": "OpenAI Responses",
            "utteranceCount": 3,
            "speakerCount": 2,
            "speakers": [
              "D",
              "E"
            ],
            "tags": {
              "topic": "technology_engineering/software_engineering",
              "silenceRatio": 0.033797,
              "silenceSegmentCount": 2,
              "speaker": {
                "multi_speaker": true,
                "speaker_change": true,
                "speaker_overlap": true
              }
            }
          },
          "delta": {
            "silenceRatio": -0.115966,
            "topicChanged": false,
            "speakerChanged": false
          }
        }
      ]
    }
  }
};

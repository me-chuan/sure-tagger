window.DEMO_DATA = {
  "summary": {
    "sampleCount": 40,
    "datasetCount": 8,
    "selectedCount": 40,
    "rirArtifactCount": 25,
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
      "audio_quality": 40,
      "room_acoustic": 25,
      "sound_field_scene": 40,
      "language_content": 25,
      "speaker": 40
    },
    "topicCount": 0,
    "speakerCount": 40,
    "speakerMultiCount": 4,
    "generatedFrom": {
      "manifest": "phase2_asr_sample/manifest.jsonl",
      "tags": "outputs/phase2_full_tags.jsonl",
      "audioDir": "demo/assets/audio"
    }
  },
  "samples": [
    {
      "row": 1,
      "sampleId": "1089-134686-0000",
      "dataset": "LibriSpeech",
      "title": "LibriSpeech 干净朗读语音",
      "note": "说话人: 1 · 组成: 无明确声源",
      "audio": "assets/audio/librispeech_1089-134686-0000.wav",
      "transcript": "HE HOPED THERE WOULD BE STEW FOR DINNER TURNIPS AND CARROTS AND BRUISED POTATOES AND FAT MUTTON PIECES TO BE LADLED OUT IN THICK PEPPERED FLOUR FATTENED SAUCE",
      "nativeMetadata": {},
      "durationSec": 10.435,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 4.185929,
          "dnsmos_ovrl": 3.41634,
          "dnsmos_p808": 4.000727,
          "dnsmos_sig": 3.640973,
          "snr_db": 45.948561
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 10.435,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.058936,
          "silence_segments": [
            {
              "end_sec": 0.5,
              "start_sec": 0.0
            },
            {
              "end_sec": 10.435,
              "start_sec": 10.32
            }
          ]
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
          "topic": null,
          "word_count": 28
        },
        "room_acoustic": {
          "c50_db": 40.897876,
          "far_field": null,
          "rt60_sec": 0.060225
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [
              "Silence"
            ],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech",
            "singing"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 1,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 2,
      "sampleId": "1089-134686-0001",
      "dataset": "LibriSpeech",
      "title": "LibriSpeech 干净朗读语音",
      "note": "说话人: 1",
      "audio": "assets/audio/librispeech_1089-134686-0001.wav",
      "transcript": "STUFF IT INTO YOU HIS BELLY COUNSELLED HIM",
      "nativeMetadata": {},
      "durationSec": 3.275,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 4.124885,
          "dnsmos_ovrl": 3.204987,
          "dnsmos_p808": 3.739523,
          "dnsmos_sig": 3.470618,
          "snr_db": 42.423795
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 3.275,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.169466,
          "silence_segments": [
            {
              "end_sec": 0.31,
              "start_sec": 0.0
            },
            {
              "end_sec": 3.275,
              "start_sec": 3.03
            }
          ]
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
          "topic": null,
          "word_count": 8
        },
        "room_acoustic": {
          "c50_db": 39.539401,
          "far_field": null,
          "rt60_sec": 0.06563
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 1,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 3,
      "sampleId": "1089-134686-0002",
      "dataset": "LibriSpeech",
      "title": "LibriSpeech 干净朗读语音",
      "note": "说话人: 1",
      "audio": "assets/audio/librispeech_1089-134686-0002.wav",
      "transcript": "AFTER EARLY NIGHTFALL THE YELLOW LAMPS WOULD LIGHT UP HERE AND THERE THE SQUALID QUARTER OF THE BROTHELS",
      "nativeMetadata": {},
      "durationSec": 6.625,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 4.147284,
          "dnsmos_ovrl": 3.344947,
          "dnsmos_p808": 4.141948,
          "dnsmos_sig": 3.594833,
          "snr_db": 47.73482
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 6.625,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.09283,
          "silence_segments": [
            {
              "end_sec": 0.34,
              "start_sec": 0.0
            },
            {
              "end_sec": 6.625,
              "start_sec": 6.35
            }
          ]
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
          "topic": null,
          "word_count": 18
        },
        "room_acoustic": {
          "c50_db": 40.543838,
          "far_field": null,
          "rt60_sec": 0.061985
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 1,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 4,
      "sampleId": "1089-134686-0003",
      "dataset": "LibriSpeech",
      "title": "LibriSpeech 干净朗读语音",
      "note": "说话人: 1",
      "audio": "assets/audio/librispeech_1089-134686-0003.wav",
      "transcript": "HELLO BERTIE ANY GOOD IN YOUR MIND",
      "nativeMetadata": {},
      "durationSec": 2.68,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 3.853381,
          "dnsmos_ovrl": 3.097636,
          "dnsmos_p808": 3.662646,
          "dnsmos_sig": 3.466424,
          "snr_db": 53.300519
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 2.68,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.164179,
          "silence_segments": [
            {
              "end_sec": 0.41,
              "start_sec": 0.0
            },
            {
              "end_sec": 2.68,
              "start_sec": 2.65
            }
          ]
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
          "topic": null,
          "word_count": 7
        },
        "room_acoustic": {
          "c50_db": 34.957345,
          "far_field": null,
          "rt60_sec": 0.078515
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 1,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 5,
      "sampleId": "1089-134686-0004",
      "dataset": "LibriSpeech",
      "title": "LibriSpeech 干净朗读语音",
      "note": "说话人: 1",
      "audio": "assets/audio/librispeech_1089-134686-0004.wav",
      "transcript": "NUMBER TEN FRESH NELLY IS WAITING ON YOU GOOD NIGHT HUSBAND",
      "nativeMetadata": {},
      "durationSec": 5.215063,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 4.191944,
          "dnsmos_ovrl": 3.472051,
          "dnsmos_p808": 4.011679,
          "dnsmos_sig": 3.685994,
          "snr_db": 55.506136
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 5.215063,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.143814,
          "silence_segments": [
            {
              "end_sec": 0.18,
              "start_sec": 0.0
            },
            {
              "end_sec": 1.58,
              "start_sec": 1.46
            },
            {
              "end_sec": 4.09,
              "start_sec": 3.64
            }
          ]
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
          "topic": null,
          "word_count": 11
        },
        "room_acoustic": {
          "c50_db": 40.63356,
          "far_field": null,
          "rt60_sec": 0.06108
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 1,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 6,
      "sampleId": "BAC009S0764W0121",
      "dataset": "AISHELL-1",
      "title": "AISHELL-1 中文朗读语音",
      "note": "说话人: 1 · 组成: 无明确声源",
      "audio": "assets/audio/aishell_BAC009S0764W0121.wav",
      "transcript": "甚至 出现 交易 几乎 停滞 的 情况",
      "nativeMetadata": {},
      "durationSec": 4.203938,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 3.482607,
          "dnsmos_ovrl": 2.425111,
          "dnsmos_p808": 3.745586,
          "dnsmos_sig": 3.030385,
          "snr_db": 42.611545
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 4.203938,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.169826,
          "silence_segments": [
            {
              "end_sec": 0.41,
              "start_sec": 0.0
            },
            {
              "end_sec": 4.203938,
              "start_sec": 3.9
            }
          ]
        },
        "language_content": {
          "filler": 0,
          "language": "zh mandarin",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": null,
          "word_count": 13
        },
        "room_acoustic": {
          "c50_db": 21.544749,
          "far_field": null,
          "rt60_sec": 0.264471
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [
              "Silence"
            ],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 1,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 7,
      "sampleId": "BAC009S0764W0122",
      "dataset": "AISHELL-1",
      "title": "AISHELL-1 中文朗读语音",
      "note": "说话人: 1 · 组成: 无明确声源",
      "audio": "assets/audio/aishell_BAC009S0764W0122.wav",
      "transcript": "一二 线 城市 虽然 也 处于 调整 中",
      "nativeMetadata": {},
      "durationSec": 4.115,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 2.260463,
          "dnsmos_ovrl": 1.849036,
          "dnsmos_p808": 3.721751,
          "dnsmos_sig": 2.380089,
          "snr_db": 35.1419
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 4.115,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.173755,
          "silence_segments": [
            {
              "end_sec": 0.46,
              "start_sec": 0.0
            },
            {
              "end_sec": 4.115,
              "start_sec": 3.86
            }
          ]
        },
        "language_content": {
          "filler": 0,
          "language": "zh mandarin",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": null,
          "word_count": 13
        },
        "room_acoustic": {
          "c50_db": 20.407529,
          "far_field": null,
          "rt60_sec": 0.289965
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [
              "Silence"
            ],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 1,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 8,
      "sampleId": "BAC009S0764W0123",
      "dataset": "AISHELL-1",
      "title": "AISHELL-1 中文朗读语音",
      "note": "说话人: 1",
      "audio": "assets/audio/aishell_BAC009S0764W0123.wav",
      "transcript": "但 因为 聚集 了 过多 公共 资源",
      "nativeMetadata": {},
      "durationSec": 4.0,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 3.094054,
          "dnsmos_ovrl": 2.18487,
          "dnsmos_p808": 3.57581,
          "dnsmos_sig": 2.889049,
          "snr_db": 27.321666
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 4.0,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.1825,
          "silence_segments": [
            {
              "end_sec": 0.47,
              "start_sec": 0.0
            },
            {
              "end_sec": 4.0,
              "start_sec": 3.74
            }
          ]
        },
        "language_content": {
          "filler": 0,
          "language": "zh mandarin",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": null,
          "word_count": 12
        },
        "room_acoustic": {
          "c50_db": 20.477777,
          "far_field": null,
          "rt60_sec": 0.276645
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 1,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 9,
      "sampleId": "BAC009S0764W0124",
      "dataset": "AISHELL-1",
      "title": "AISHELL-1 中文朗读语音",
      "note": "说话人: 1",
      "audio": "assets/audio/aishell_BAC009S0764W0124.wav",
      "transcript": "为了 规避 三四 线 城市 明显 过剩 的 市场 风险",
      "nativeMetadata": {},
      "durationSec": 5.237,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 1.967448,
          "dnsmos_ovrl": 1.76408,
          "dnsmos_p808": 3.618682,
          "dnsmos_sig": 2.26975,
          "snr_db": 25.181909
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 5.237,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.113997,
          "silence_segments": [
            {
              "end_sec": 0.45,
              "start_sec": 0.0
            },
            {
              "end_sec": 5.237,
              "start_sec": 5.09
            }
          ]
        },
        "language_content": {
          "filler": 0,
          "language": "zh mandarin",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": null,
          "word_count": 18
        },
        "room_acoustic": {
          "c50_db": 21.588484,
          "far_field": null,
          "rt60_sec": 0.261172
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 1,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 10,
      "sampleId": "BAC009S0764W0125",
      "dataset": "AISHELL-1",
      "title": "AISHELL-1 中文朗读语音",
      "note": "说话人: 1",
      "audio": "assets/audio/aishell_BAC009S0764W0125.wav",
      "transcript": "标杆 房企 必然 调整 市场 战略",
      "nativeMetadata": {},
      "durationSec": 4.311,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 3.054762,
          "dnsmos_ovrl": 2.237836,
          "dnsmos_p808": 3.558418,
          "dnsmos_sig": 2.821837,
          "snr_db": 33.636256
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 4.311,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.157968,
          "silence_segments": [
            {
              "end_sec": 0.46,
              "start_sec": 0.0
            },
            {
              "end_sec": 4.311,
              "start_sec": 4.09
            }
          ]
        },
        "language_content": {
          "filler": 0,
          "language": "zh mandarin",
          "punctuation": {
            "has_terminal_punctuation": false,
            "punctuation_count": 0
          },
          "repetition": {
            "has_repetition": false,
            "repetition_count": 0
          },
          "topic": null,
          "word_count": 12
        },
        "room_acoustic": {
          "c50_db": 22.180508,
          "far_field": null,
          "rt60_sec": 0.255192
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 1,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 11,
      "sampleId": "sa1",
      "dataset": "TIMIT",
      "title": "TIMIT 多音素朗读",
      "note": "说话人: 1",
      "audio": "assets/audio/timit_sa1.wav",
      "transcript": "She had your dark suit in greasy wash water all year.",
      "nativeMetadata": {},
      "durationSec": 3.968,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 4.039296,
          "dnsmos_ovrl": 3.229164,
          "dnsmos_p808": 4.03552,
          "dnsmos_sig": 3.547086,
          "snr_db": 50.160365
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 3.968,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.138609,
          "silence_segments": [
            {
              "end_sec": 0.55,
              "start_sec": 0.0
            }
          ]
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
          "topic": null,
          "word_count": 11
        },
        "room_acoustic": {
          "c50_db": 41.014629,
          "far_field": null,
          "rt60_sec": 0.064891
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 1,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 12,
      "sampleId": "sa2",
      "dataset": "TIMIT",
      "title": "TIMIT 多音素朗读",
      "note": "说话人: 1",
      "audio": "assets/audio/timit_sa2.wav",
      "transcript": "Don't ask me to carry an oily rag like that.",
      "nativeMetadata": {},
      "durationSec": 3.628812,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 4.19564,
          "dnsmos_ovrl": 3.411771,
          "dnsmos_p808": 3.657432,
          "dnsmos_sig": 3.663176,
          "snr_db": 59.886621
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 3.628812,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.236665,
          "silence_segments": [
            {
              "end_sec": 0.77,
              "start_sec": 0.0
            },
            {
              "end_sec": 3.628812,
              "start_sec": 3.54
            }
          ]
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
          "topic": null,
          "word_count": 10
        },
        "room_acoustic": {
          "c50_db": 40.64341,
          "far_field": null,
          "rt60_sec": 0.066912
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 1,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 13,
      "sampleId": "si1573",
      "dataset": "TIMIT",
      "title": "TIMIT 多音素朗读",
      "note": "说话人: 1",
      "audio": "assets/audio/timit_si1573.wav",
      "transcript": "His captain was thin and haggard and his beautiful boots were worn and shabby.",
      "nativeMetadata": {},
      "durationSec": 4.972812,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 4.019212,
          "dnsmos_ovrl": 3.213393,
          "dnsmos_p808": 3.6728,
          "dnsmos_sig": 3.538065,
          "snr_db": 44.730727
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 4.972812,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.104569,
          "silence_segments": [
            {
              "end_sec": 0.52,
              "start_sec": 0.0
            }
          ]
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
          "topic": null,
          "word_count": 14
        },
        "room_acoustic": {
          "c50_db": 41.273514,
          "far_field": null,
          "rt60_sec": 0.065439
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 1,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 14,
      "sampleId": "sx133",
      "dataset": "TIMIT",
      "title": "TIMIT 多音素朗读",
      "note": "说话人: 1",
      "audio": "assets/audio/timit_sx133.wav",
      "transcript": "Pizzerias are convenient for a quick lunch.",
      "nativeMetadata": {},
      "durationSec": 3.31525,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 4.0966,
          "dnsmos_ovrl": 3.275021,
          "dnsmos_p808": 3.838463,
          "dnsmos_sig": 3.595976,
          "snr_db": 30.496323
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 3.31525,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.153835,
          "silence_segments": [
            {
              "end_sec": 0.51,
              "start_sec": 0.0
            }
          ]
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
          "topic": null,
          "word_count": 7
        },
        "room_acoustic": {
          "c50_db": 41.016975,
          "far_field": null,
          "rt60_sec": 0.069614
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 1,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 15,
      "sampleId": "sx223",
      "dataset": "TIMIT",
      "title": "TIMIT 多音素朗读",
      "note": "说话人: 1",
      "audio": "assets/audio/timit_sx223.wav",
      "transcript": "Put the butcher block table in the garage.",
      "nativeMetadata": {},
      "durationSec": 3.097625,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 4.186132,
          "dnsmos_ovrl": 3.44368,
          "dnsmos_p808": 4.139837,
          "dnsmos_sig": 3.692719,
          "snr_db": 47.395483
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 3.097625,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.20661,
          "silence_segments": [
            {
              "end_sec": 0.64,
              "start_sec": 0.0
            }
          ]
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
          "topic": null,
          "word_count": 8
        },
        "room_acoustic": {
          "c50_db": 39.990012,
          "far_field": null,
          "rt60_sec": 0.065759
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 1,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 16,
      "sampleId": "F01_050C0101_PED_REAL",
      "dataset": "CHiME4",
      "title": "CHiME4 行人区噪声语音",
      "note": "说话人: 1",
      "audio": "assets/audio/chime4_F01_050C0101_PED_REAL.wav",
      "transcript": "LAST MONTH OVERALL GOODS PRODUCING EMPLOYMENT FELL SIXTY EIGHT THOUSAND AFTER A THIRTY TWO THOUSAND JOB RISE IN FEBRUARY",
      "nativeMetadata": {},
      "durationSec": 7.623687,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 1.359623,
          "dnsmos_ovrl": 1.404506,
          "dnsmos_p808": 2.370079,
          "dnsmos_sig": 2.168632,
          "snr_db": -0.23553
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 7.623687,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.080014,
          "silence_segments": [
            {
              "end_sec": 0.61,
              "start_sec": 0.0
            }
          ]
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
          "topic": null,
          "word_count": 19
        },
        "room_acoustic": {
          "c50_db": 26.065818,
          "far_field": null,
          "rt60_sec": 0.463003
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 1,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 17,
      "sampleId": "F01_050C0102_CAF_REAL",
      "dataset": "CHiME4",
      "title": "CHiME4 咖啡馆噪声语音",
      "note": "噪声: 机械 · 说话人: 1",
      "audio": "assets/audio/chime4_F01_050C0102_CAF_REAL.wav",
      "transcript": "THE DEPARTMENT SAID THE DECLINE IN FACTORY JOBS WAS CONCENTRATED IN MOTOR VEHICLES AND ELECTRICAL AND ELECTRONIC EQUIPMENT",
      "nativeMetadata": {},
      "durationSec": 7.631938,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 1.24526,
          "dnsmos_ovrl": 1.201118,
          "dnsmos_p808": 2.378937,
          "dnsmos_sig": 1.471661,
          "snr_db": -1.029779
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 7.631938,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.0,
          "silence_segments": []
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
          "topic": null,
          "word_count": 18
        },
        "room_acoustic": {
          "c50_db": 23.457582,
          "far_field": null,
          "rt60_sec": 0.639492
        },
        "sound_field_scene": {
          "external_noise_type": [
            "mechanical"
          ],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 1,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 18,
      "sampleId": "F01_050C0102_STR_REAL",
      "dataset": "CHiME4",
      "title": "CHiME4 街道噪声语音",
      "note": "说话人: 1",
      "audio": "assets/audio/chime4_F01_050C0102_STR_REAL.wav",
      "transcript": "THE DEPARTMENT SAID THE DECLINE IN FACTORY JOBS WAS CONCENTRATED IN MOTOR VEHICLES AND ELECTRICAL AND ELECTRONIC EQUIPMENT",
      "nativeMetadata": {},
      "durationSec": 8.119813,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 1.144401,
          "dnsmos_ovrl": 1.10276,
          "dnsmos_p808": 2.057701,
          "dnsmos_sig": 1.186638,
          "snr_db": -0.018272
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 8.119813,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.09727,
          "silence_segments": [
            {
              "end_sec": 0.65,
              "start_sec": 0.0
            },
            {
              "end_sec": 8.119813,
              "start_sec": 7.98
            }
          ]
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
          "topic": null,
          "word_count": 18
        },
        "room_acoustic": {
          "c50_db": 35.966741,
          "far_field": null,
          "rt60_sec": 0.114241
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 1,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 19,
      "sampleId": "F01_050C0103_BUS_REAL",
      "dataset": "CHiME4",
      "title": "CHiME4 公交噪声语音",
      "note": "说话人: 1",
      "audio": "assets/audio/chime4_F01_050C0103_BUS_REAL.wav",
      "transcript": "CONSTRUCTION EMPLOYMENT FELL FORTY SEVEN THOUSAND AFTER A FIFTEEN THOUSAND JOB DECLINE THE MONTH BEFORE",
      "nativeMetadata": {},
      "durationSec": 6.631687,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 1.191416,
          "dnsmos_ovrl": 1.113726,
          "dnsmos_p808": 2.548175,
          "dnsmos_sig": 1.229232,
          "snr_db": 0.633523
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 6.631687,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.120887,
          "silence_segments": [
            {
              "end_sec": 0.39,
              "start_sec": 0.0
            },
            {
              "end_sec": 6.631687,
              "start_sec": 6.22
            }
          ]
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
          "topic": null,
          "word_count": 15
        },
        "room_acoustic": {
          "c50_db": 32.511555,
          "far_field": null,
          "rt60_sec": 0.204985
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 1,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 20,
      "sampleId": "F01_050C0104_CAF_REAL",
      "dataset": "CHiME4",
      "title": "CHiME4 咖啡馆噪声语音",
      "note": "说话人: 1",
      "audio": "assets/audio/chime4_F01_050C0104_CAF_REAL.wav",
      "transcript": "MINING EMPLOYMENT WHICH INCLUDES THE OIL AND GAS EXTRACTION INDUSTRY ROSE THREE THOUSAND AFTER A ONE THOUSAND JOB RISE",
      "nativeMetadata": {},
      "durationSec": 8.151813,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 1.993115,
          "dnsmos_ovrl": 1.82285,
          "dnsmos_p808": 2.726842,
          "dnsmos_sig": 3.062713,
          "snr_db": 1.25796
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 8.151813,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.051522,
          "silence_segments": [
            {
              "end_sec": 0.42,
              "start_sec": 0.0
            }
          ]
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
          "topic": null,
          "word_count": 19
        },
        "room_acoustic": {
          "c50_db": 26.803802,
          "far_field": null,
          "rt60_sec": 0.361013
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 1,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 21,
      "sampleId": "EN2001a_utterance_00000",
      "dataset": "AMI",
      "title": "AMI 会议片段",
      "note": "说话人: 3",
      "audio": "assets/audio/ami_EN2001a_utterance_00000.wav",
      "transcript": "'Kay. Gosh. Okay. 'Kay. Does anyone want to see uh Steve's feedback from the specification? Is there much more in it than he d I I dry-read it the last time.. Right. Is there much more in it than he said yesterday?",
      "nativeMetadata": {},
      "durationSec": 18.436,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 3.974983,
          "dnsmos_ovrl": 2.678807,
          "dnsmos_p808": 2.823182,
          "dnsmos_sig": 3.089926,
          "snr_db": 13.128118
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 18.436,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.503688,
          "silence_segments": [
            {
              "end_sec": 2.89,
              "start_sec": 0.0
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
          ]
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
          "topic": null,
          "word_count": 43
        },
        "room_acoustic": {
          "c50_db": 31.111448,
          "far_field": null,
          "rt60_sec": 0.08687
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": true,
          "overlap_ratio": 0.211931,
          "speaker_change": true,
          "speaker_change_count": 1,
          "speaker_count": 3,
          "speaker_overlap": true
        }
      }
    },
    {
      "row": 22,
      "sampleId": "EN2001a_utterance_00001",
      "dataset": "AMI",
      "title": "AMI 会议片段",
      "note": "说话人: 2",
      "audio": "assets/audio/ami_EN2001a_utterance_00001.wav",
      "transcript": "Not really, um just what he's talking about, like duplication of effort and Mm. Hmm. Hmm? Like duplication of effort and stuff, and um yeah, he was saying that we should maybe uh think about having a prototype for week six, which is next week. Yeah. Next week.",
      "nativeMetadata": {},
      "durationSec": 20.084,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 3.981168,
          "dnsmos_ovrl": 2.83701,
          "dnsmos_p808": 3.071224,
          "dnsmos_sig": 3.251212,
          "snr_db": 19.056463
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 20.084,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.294463,
          "silence_segments": [
            {
              "end_sec": 0.3,
              "start_sec": 0.0
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
          ]
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
          "topic": null,
          "word_count": 48
        },
        "room_acoustic": {
          "c50_db": 36.399061,
          "far_field": null,
          "rt60_sec": 0.067474
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": true,
          "overlap_ratio": 0.029596,
          "speaker_change": true,
          "speaker_change_count": 2,
          "speaker_count": 2,
          "speaker_overlap": true
        }
      }
    },
    {
      "row": 23,
      "sampleId": "EN2001a_utterance_00003",
      "dataset": "AMI",
      "title": "AMI 会议片段",
      "note": "说话人: 1 · 组成: 无明确声源",
      "audio": "assets/audio/ami_EN2001a_utterance_00003.wav",
      "transcript": "well go back first of all and look at NITE X_M_L_ to see in how far that that which we want is compatible with that which NITE X_M_L_ offers us. And then just sort of everyone make sure everyone understand the interface. Yeah.",
      "nativeMetadata": {},
      "durationSec": 14.1115,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 4.081535,
          "dnsmos_ovrl": 2.791316,
          "dnsmos_p808": 3.228106,
          "dnsmos_sig": 3.086606,
          "snr_db": 24.190242
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 14.1115,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.261595,
          "silence_segments": [
            {
              "end_sec": 0.8,
              "start_sec": 0.0
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
          ]
        },
        "language_content": {
          "filler": 1,
          "language": "no",
          "punctuation": {
            "has_terminal_punctuation": true,
            "punctuation_count": 9
          },
          "repetition": {
            "has_repetition": true,
            "repetition_count": 1
          },
          "topic": null,
          "word_count": 47
        },
        "room_acoustic": {
          "c50_db": 35.861222,
          "far_field": null,
          "rt60_sec": 0.066785
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [
              "Silence"
            ],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 1,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 24,
      "sampleId": "EN2001a_utterance_00005",
      "dataset": "AMI",
      "title": "AMI 会议片段",
      "note": "说话人: 2 · 组成: 无明确声源",
      "audio": "assets/audio/ami_EN2001a_utterance_00005.wav",
      "transcript": "Hmm? The basic word importance is off-line as well. The combined measure might not be if we want to wait what the user has typed in into the search. Yeah. Okay. Okay.",
      "nativeMetadata": {},
      "durationSec": 17.5105,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 3.484097,
          "dnsmos_ovrl": 1.926559,
          "dnsmos_p808": 3.163394,
          "dnsmos_sig": 2.574438,
          "snr_db": 30.15965
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 17.5105,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.450044,
          "silence_segments": [
            {
              "end_sec": 7.01,
              "start_sec": 0.0
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
          ]
        },
        "language_content": {
          "filler": 2,
          "language": "no",
          "punctuation": {
            "has_terminal_punctuation": true,
            "punctuation_count": 7
          },
          "repetition": {
            "has_repetition": true,
            "repetition_count": 1
          },
          "topic": null,
          "word_count": 33
        },
        "room_acoustic": {
          "c50_db": 35.235287,
          "far_field": null,
          "rt60_sec": 0.069148
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [
              "Silence"
            ],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": true,
          "overlap_ratio": 0.103806,
          "speaker_change": true,
          "speaker_change_count": 2,
          "speaker_count": 2,
          "speaker_overlap": true
        }
      }
    },
    {
      "row": 25,
      "sampleId": "EN2001a_utterance_00006",
      "dataset": "AMI",
      "title": "AMI 会议片段",
      "note": "噪声: 无明确声源 · 说话人: 2 · 组成: 无明确声源",
      "audio": "assets/audio/ami_EN2001a_utterance_00006.wav",
      "transcript": "Uh mine's gonna be mostly using the off-line. But the actual stuff it's doing will be on-line. But it won't be very um processor intensive or memory intensive, I don't think. 'Kay. So basically apart from the display module, the i the display itself, we don't have an extremely high degree of interaction between sort of our modules that create the stuff and and the interface, so the interface is mainly while it's running just working on data that's just loaded from a file, I guess.",
      "nativeMetadata": {},
      "durationSec": 29.6035,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": 4.043649,
          "dnsmos_ovrl": 2.612575,
          "dnsmos_p808": 3.351632,
          "dnsmos_sig": 2.916934,
          "snr_db": 38.04082
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 29.6035,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.149763,
          "silence_segments": [
            {
              "end_sec": 0.3,
              "start_sec": 0.0
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
          ]
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
          "topic": null,
          "word_count": 88
        },
        "room_acoustic": {
          "c50_db": 35.693252,
          "far_field": null,
          "rt60_sec": 0.06477
        },
        "sound_field_scene": {
          "external_noise_type": [
            "formless"
          ],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [
              "Clicking"
            ],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech"
          ]
        },
        "speaker": {
          "multi_speaker": true,
          "overlap_ratio": 0.028269,
          "speaker_change": true,
          "speaker_change_count": 2,
          "speaker_count": 2,
          "speaker_overlap": true
        }
      }
    },
    {
      "row": 26,
      "sampleId": "airport-barcelona-0-0-a",
      "dataset": "TUT Urban Acoustic Scenes 2018",
      "title": "TUT 2018 机场声景",
      "note": "噪声: 动物 · 说话人: 0 · 组成: 动物",
      "audio": "assets/audio/tut2018_airport-barcelona-0-0-a.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 10.0,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": null,
          "dnsmos_ovrl": null,
          "dnsmos_p808": null,
          "dnsmos_sig": null,
          "snr_db": -0.630383
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 10.0,
          "sample_rate_hz": 16000,
          "silence_ratio": null,
          "silence_segments": null
        },
        "language_content": {
          "filler": null,
          "language": null,
          "punctuation": null,
          "repetition": null,
          "topic": null,
          "word_count": null
        },
        "room_acoustic": {
          "c50_db": null,
          "far_field": null,
          "rt60_sec": null
        },
        "sound_field_scene": {
          "external_noise_type": [
            "animal"
          ],
          "music_present": false,
          "noise_composition": {
            "animal": [
              "Clip-clop",
              "Animal",
              "Horse"
            ],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": []
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 0,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 27,
      "sampleId": "bus-barcelona-15-599-a",
      "dataset": "TUT Urban Acoustic Scenes 2018",
      "title": "TUT 2018 公交声景",
      "note": "说话人: 0",
      "audio": "assets/audio/tut2018_bus-barcelona-15-599-a.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 10.0,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": null,
          "dnsmos_ovrl": null,
          "dnsmos_p808": null,
          "dnsmos_sig": null,
          "snr_db": -4.011834
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 10.0,
          "sample_rate_hz": 16000,
          "silence_ratio": null,
          "silence_segments": null
        },
        "language_content": {
          "filler": null,
          "language": null,
          "punctuation": null,
          "repetition": null,
          "topic": null,
          "word_count": null
        },
        "room_acoustic": {
          "c50_db": null,
          "far_field": null,
          "rt60_sec": null
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": []
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 0,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 28,
      "sampleId": "metro-barcelona-41-1221-a",
      "dataset": "TUT Urban Acoustic Scenes 2018",
      "title": "TUT 2018 地铁声景",
      "note": "噪声: 机械 · 含背景音乐 · 说话人: 0 · 组成: 机械",
      "audio": "assets/audio/tut2018_metro-barcelona-41-1221-a.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 10.0,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": null,
          "dnsmos_ovrl": null,
          "dnsmos_p808": null,
          "dnsmos_sig": null,
          "snr_db": -0.68653
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 10.0,
          "sample_rate_hz": 16000,
          "silence_ratio": null,
          "silence_segments": null
        },
        "language_content": {
          "filler": null,
          "language": null,
          "punctuation": null,
          "repetition": null,
          "topic": null,
          "word_count": null
        },
        "room_acoustic": {
          "c50_db": null,
          "far_field": null,
          "rt60_sec": null
        },
        "sound_field_scene": {
          "external_noise_type": [
            "mechanical"
          ],
          "music_present": true,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [
              "Subway, metro, underground",
              "Train"
            ],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech",
            "singing",
            "music"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 0,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 29,
      "sampleId": "park-barcelona-89-2429-a",
      "dataset": "TUT Urban Acoustic Scenes 2018",
      "title": "TUT 2018 公园声景",
      "note": "说话人: 0",
      "audio": "assets/audio/tut2018_park-barcelona-89-2429-a.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 10.0,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": null,
          "dnsmos_ovrl": null,
          "dnsmos_p808": null,
          "dnsmos_sig": null,
          "snr_db": -3.138264
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 10.0,
          "sample_rate_hz": 16000,
          "silence_ratio": null,
          "silence_segments": null
        },
        "language_content": {
          "filler": null,
          "language": null,
          "punctuation": null,
          "repetition": null,
          "topic": null,
          "word_count": null
        },
        "room_acoustic": {
          "c50_db": null,
          "far_field": null,
          "rt60_sec": null
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": []
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 0,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 30,
      "sampleId": "street_traffic-barcelona-161-4901-a",
      "dataset": "TUT Urban Acoustic Scenes 2018",
      "title": "TUT 2018 街道交通声景",
      "note": "噪声: 机械 · 说话人: 0",
      "audio": "assets/audio/tut2018_street_traffic-barcelona-161-4901-a.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 10.0,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": null,
          "dnsmos_ovrl": null,
          "dnsmos_p808": null,
          "dnsmos_sig": null,
          "snr_db": -4.8527
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 10.0,
          "sample_rate_hz": 16000,
          "silence_ratio": null,
          "silence_segments": null
        },
        "language_content": {
          "filler": null,
          "language": null,
          "punctuation": null,
          "repetition": null,
          "topic": null,
          "word_count": null
        },
        "room_acoustic": {
          "c50_db": null,
          "far_field": null,
          "rt60_sec": null
        },
        "sound_field_scene": {
          "external_noise_type": [
            "mechanical"
          ],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": []
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 0,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 31,
      "sampleId": "babble",
      "dataset": "NOISEX-92",
      "title": "NOISEX-92 人群噪声",
      "note": "含背景音乐 · 说话人: 0",
      "audio": "assets/audio/noisex92_babble.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 10.0,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": null,
          "dnsmos_ovrl": null,
          "dnsmos_p808": null,
          "dnsmos_sig": null,
          "snr_db": -2.734259
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 10.0,
          "sample_rate_hz": 16000,
          "silence_ratio": null,
          "silence_segments": null
        },
        "language_content": {
          "filler": null,
          "language": null,
          "punctuation": null,
          "repetition": null,
          "topic": null,
          "word_count": null
        },
        "room_acoustic": {
          "c50_db": null,
          "far_field": null,
          "rt60_sec": null
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": true,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech",
            "singing",
            "music"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 0,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 32,
      "sampleId": "f16",
      "dataset": "NOISEX-92",
      "title": "NOISEX-92 飞机噪声",
      "note": "说话人: 0",
      "audio": "assets/audio/noisex92_f16.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 10.0,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": null,
          "dnsmos_ovrl": null,
          "dnsmos_p808": null,
          "dnsmos_sig": null,
          "snr_db": -5.685234
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 10.0,
          "sample_rate_hz": 16000,
          "silence_ratio": null,
          "silence_segments": null
        },
        "language_content": {
          "filler": null,
          "language": null,
          "punctuation": null,
          "repetition": null,
          "topic": null,
          "word_count": null
        },
        "room_acoustic": {
          "c50_db": null,
          "far_field": null,
          "rt60_sec": null
        },
        "sound_field_scene": {
          "external_noise_type": [],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": []
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 0,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 33,
      "sampleId": "factory1",
      "dataset": "NOISEX-92",
      "title": "NOISEX-92 工厂噪声",
      "note": "噪声: 机械 · 含背景音乐 · 说话人: 0 · 组成: 机械",
      "audio": "assets/audio/noisex92_factory1.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 10.0,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": null,
          "dnsmos_ovrl": null,
          "dnsmos_p808": null,
          "dnsmos_sig": null,
          "snr_db": -0.386923
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 10.0,
          "sample_rate_hz": 16000,
          "silence_ratio": null,
          "silence_segments": null
        },
        "language_content": {
          "filler": null,
          "language": null,
          "punctuation": null,
          "repetition": null,
          "topic": null,
          "word_count": null
        },
        "room_acoustic": {
          "c50_db": null,
          "far_field": null,
          "rt60_sec": null
        },
        "sound_field_scene": {
          "external_noise_type": [
            "mechanical"
          ],
          "music_present": true,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [
              "Sliding door"
            ],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "music"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 0,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 34,
      "sampleId": "machinegun",
      "dataset": "NOISEX-92",
      "title": "NOISEX-92 枪械噪声",
      "note": "噪声: 机械 · 说话人: 0 · 组成: 机械",
      "audio": "assets/audio/noisex92_machinegun.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 10.0,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": null,
          "dnsmos_ovrl": null,
          "dnsmos_p808": null,
          "dnsmos_sig": null,
          "snr_db": 0.631293
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 10.0,
          "sample_rate_hz": 16000,
          "silence_ratio": null,
          "silence_segments": null
        },
        "language_content": {
          "filler": null,
          "language": null,
          "punctuation": null,
          "repetition": null,
          "topic": null,
          "word_count": null
        },
        "room_acoustic": {
          "c50_db": null,
          "far_field": null,
          "rt60_sec": null
        },
        "sound_field_scene": {
          "external_noise_type": [
            "mechanical"
          ],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [
              "Knock"
            ],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": []
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 0,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 35,
      "sampleId": "volvo",
      "dataset": "NOISEX-92",
      "title": "NOISEX-92 车辆噪声",
      "note": "噪声: 机械 · 说话人: 0 · 组成: 机械",
      "audio": "assets/audio/noisex92_volvo.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 10.0,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": null,
          "dnsmos_ovrl": null,
          "dnsmos_p808": null,
          "dnsmos_sig": null,
          "snr_db": -2.497315
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 10.0,
          "sample_rate_hz": 16000,
          "silence_ratio": null,
          "silence_segments": null
        },
        "language_content": {
          "filler": null,
          "language": null,
          "punctuation": null,
          "repetition": null,
          "topic": null,
          "word_count": null
        },
        "room_acoustic": {
          "c50_db": null,
          "far_field": null,
          "rt60_sec": null
        },
        "sound_field_scene": {
          "external_noise_type": [
            "mechanical"
          ],
          "music_present": false,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [
              "Vehicle"
            ],
            "music": [],
            "nature": []
          },
          "sound": null,
          "speech_music_events": []
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 0,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 36,
      "sampleId": "050a0501_1.7783_442o030z_-1.7783",
      "dataset": "WHAM! noise",
      "title": "WHAM! 非平稳背景噪声",
      "note": "噪声: 音乐 · 含背景音乐 · 说话人: 0 · 组成: 音乐",
      "audio": "assets/audio/wham_noise_050a0501_1.7783_442o030z_-1.7783.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 8.933063,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": null,
          "dnsmos_ovrl": null,
          "dnsmos_p808": null,
          "dnsmos_sig": null,
          "snr_db": -0.043474
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 8.933063,
          "sample_rate_hz": 16000,
          "silence_ratio": null,
          "silence_segments": null
        },
        "language_content": {
          "filler": null,
          "language": null,
          "punctuation": null,
          "repetition": null,
          "topic": null,
          "word_count": null
        },
        "room_acoustic": {
          "c50_db": null,
          "far_field": null,
          "rt60_sec": null
        },
        "sound_field_scene": {
          "external_noise_type": [
            "music"
          ],
          "music_present": true,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [
              "Music"
            ],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech",
            "singing",
            "music"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 0,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 37,
      "sampleId": "050a0502_1.3461_440o030j_-1.3461",
      "dataset": "WHAM! noise",
      "title": "WHAM! 非平稳背景噪声",
      "note": "噪声: 音乐 · 含背景音乐 · 说话人: 0 · 组成: 音乐",
      "audio": "assets/audio/wham_noise_050a0502_1.3461_440o030j_-1.3461.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 7.67725,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": null,
          "dnsmos_ovrl": null,
          "dnsmos_p808": null,
          "dnsmos_sig": null,
          "snr_db": -1.706969
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 7.67725,
          "sample_rate_hz": 16000,
          "silence_ratio": null,
          "silence_segments": null
        },
        "language_content": {
          "filler": null,
          "language": null,
          "punctuation": null,
          "repetition": null,
          "topic": null,
          "word_count": null
        },
        "room_acoustic": {
          "c50_db": null,
          "far_field": null,
          "rt60_sec": null
        },
        "sound_field_scene": {
          "external_noise_type": [
            "music"
          ],
          "music_present": true,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [
              "Music"
            ],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "singing",
            "music"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 0,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 38,
      "sampleId": "050a0504_2.4414_443o0313_-2.4414",
      "dataset": "WHAM! noise",
      "title": "WHAM! 非平稳背景噪声",
      "note": "噪声: 音乐 · 含背景音乐 · 说话人: 0 · 组成: 音乐",
      "audio": "assets/audio/wham_noise_050a0504_2.4414_443o0313_-2.4414.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 14.862375,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": null,
          "dnsmos_ovrl": null,
          "dnsmos_p808": null,
          "dnsmos_sig": null,
          "snr_db": -2.198489
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 14.862375,
          "sample_rate_hz": 16000,
          "silence_ratio": null,
          "silence_segments": null
        },
        "language_content": {
          "filler": null,
          "language": null,
          "punctuation": null,
          "repetition": null,
          "topic": null,
          "word_count": null
        },
        "room_acoustic": {
          "c50_db": null,
          "far_field": null,
          "rt60_sec": null
        },
        "sound_field_scene": {
          "external_noise_type": [
            "music"
          ],
          "music_present": true,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [
              "Music"
            ],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "singing",
            "music"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 0,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 39,
      "sampleId": "050a0505_1.5097_440o030d_-1.5097",
      "dataset": "WHAM! noise",
      "title": "WHAM! 非平稳背景噪声",
      "note": "噪声: 音乐 · 含背景音乐 · 说话人: 0 · 组成: 音乐",
      "audio": "assets/audio/wham_noise_050a0505_1.5097_440o030d_-1.5097.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 16.645563,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": null,
          "dnsmos_ovrl": null,
          "dnsmos_p808": null,
          "dnsmos_sig": null,
          "snr_db": -0.901143
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 16.645563,
          "sample_rate_hz": 16000,
          "silence_ratio": null,
          "silence_segments": null
        },
        "language_content": {
          "filler": null,
          "language": null,
          "punctuation": null,
          "repetition": null,
          "topic": null,
          "word_count": null
        },
        "room_acoustic": {
          "c50_db": null,
          "far_field": null,
          "rt60_sec": null
        },
        "sound_field_scene": {
          "external_noise_type": [
            "music"
          ],
          "music_present": true,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [
              "Music"
            ],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech",
            "singing",
            "music"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 0,
          "speaker_overlap": false
        }
      }
    },
    {
      "row": 40,
      "sampleId": "050a0506_1.7744_447c0213_-1.7744",
      "dataset": "WHAM! noise",
      "title": "WHAM! 非平稳背景噪声",
      "note": "噪声: 音乐 · 含背景音乐 · 说话人: 0 · 组成: 音乐",
      "audio": "assets/audio/wham_noise_050a0506_1.7744_447c0213_-1.7744.wav",
      "transcript": "",
      "nativeMetadata": {},
      "durationSec": 8.55,
      "tags": {
        "audio_quality": {
          "dnsmos_bak": null,
          "dnsmos_ovrl": null,
          "dnsmos_p808": null,
          "dnsmos_sig": null,
          "snr_db": -0.679746
        },
        "basic_acoustic": {
          "channels": 1,
          "duration_sec": 8.55,
          "sample_rate_hz": 16000,
          "silence_ratio": null,
          "silence_segments": null
        },
        "language_content": {
          "filler": null,
          "language": null,
          "punctuation": null,
          "repetition": null,
          "topic": null,
          "word_count": null
        },
        "room_acoustic": {
          "c50_db": null,
          "far_field": null,
          "rt60_sec": null
        },
        "sound_field_scene": {
          "external_noise_type": [
            "music"
          ],
          "music_present": true,
          "noise_composition": {
            "animal": [],
            "channel_environment": [],
            "formless": [],
            "mechanical": [],
            "music": [
              "Music"
            ],
            "nature": []
          },
          "sound": null,
          "speech_music_events": [
            "speech",
            "singing",
            "music"
          ]
        },
        "speaker": {
          "multi_speaker": false,
          "overlap_ratio": 0.0,
          "speaker_change": false,
          "speaker_change_count": 0,
          "speaker_count": 0,
          "speaker_overlap": false
        }
      }
    }
  ]
};

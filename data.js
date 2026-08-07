window.DEMO_DATA = {
  "summary": {
    "sampleCount": 40,
    "datasetCount": 8,
    "selectedCount": 15,
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
      "speaker": 3
    },
    "generatedFrom": {
      "manifest": "phase2_asr_sample/manifest.jsonl",
      "tags": "outputs/phase2_full_pipeline_tags.jsonl",
      "smokeTags": "outputs/ami_en2001a_smoke_topic_vad_speaker.jsonl"
    },
    "smoke": {
      "name": "AMI EN2001a topic/VAD/speaker smoke",
      "sampleCount": 3,
      "topicCount": 3,
      "metadataVadCount": 3,
      "metadataSpeakerCount": 3,
      "output": "outputs/ami_en2001a_smoke_topic_vad_speaker.jsonl"
    }
  },
  "samples": [
    {
      "row": 16,
      "sampleId": "F01_050C0101_PED_REAL",
      "dataset": "CHiME4",
      "title": "Noisy speech: pedestrian",
      "note": "Normal speech with pedestrian-environment noise. PANNs stays below threshold, while acoustic scores show a low-SNR sample.",
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
          "topic": null,
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
          "multi_speaker": null,
          "speaker_change": null,
          "speaker_overlap": null
        }
      }
    },
    {
      "row": 17,
      "sampleId": "F01_050C0102_CAF_REAL",
      "dataset": "CHiME4",
      "title": "Noisy speech: cafe",
      "note": "Normal speech in a cafe condition. Useful for showing noisy speech even when public background-sound tags remain empty.",
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
          "topic": null,
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
          "multi_speaker": null,
          "speaker_change": null,
          "speaker_overlap": null
        }
      }
    },
    {
      "row": 18,
      "sampleId": "F01_050C0102_STR_REAL",
      "dataset": "CHiME4",
      "title": "Noisy speech: street vehicle",
      "note": "Normal speech with street noise; PANNs publishes Vehicle as the background-sound tag.",
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
          "topic": null,
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
          "multi_speaker": null,
          "speaker_change": null,
          "speaker_overlap": null
        }
      }
    },
    {
      "row": 19,
      "sampleId": "F01_050C0103_BUS_REAL",
      "dataset": "CHiME4",
      "title": "Noisy speech: bus vehicle",
      "note": "Normal speech in a bus-like condition; PANNs publishes Vehicle as the background-sound tag.",
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
          "topic": null,
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
          "multi_speaker": null,
          "speaker_change": null,
          "speaker_overlap": null
        }
      }
    },
    {
      "row": 20,
      "sampleId": "F01_050C0104_CAF_REAL",
      "dataset": "CHiME4",
      "title": "Noisy speech: cafe music",
      "note": "Normal speech in cafe noise where PANNs detects Music as the dominant background sound.",
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
          "topic": null,
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
          "multi_speaker": null,
          "speaker_change": null,
          "speaker_overlap": null
        }
      }
    },
    {
      "row": 21,
      "sampleId": "EN2001a_utterance_00000",
      "dataset": "AMI",
      "title": "AMI smoke: coordination topic",
      "note": "AMI smoke sample with OpenAI topic, metadata-derived silence intervals, and metadata speaker flags. Topic: meeting workflow / coordination.",
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
          "silence_ratio": 0.424441,
          "silence_segments": [
            {
              "end_sec": 0.5,
              "start_sec": 0
            },
            {
              "end_sec": 2.795,
              "start_sec": 1.3
            },
            {
              "end_sec": 7.786,
              "start_sec": 3.435
            },
            {
              "end_sec": 8.372,
              "start_sec": 8.285
            },
            {
              "end_sec": 14.068,
              "start_sec": 12.964
            },
            {
              "end_sec": 18.436,
              "start_sec": 18.148
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
          "speaker_overlap": true
        }
      }
    },
    {
      "row": 22,
      "sampleId": "EN2001a_utterance_00001",
      "dataset": "AMI",
      "title": "AMI smoke: project planning topic",
      "note": "AMI smoke sample showing project-management topic classification plus metadata VAD and multi-speaker overlap flags.",
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
          "silence_ratio": 0.093856,
          "silence_segments": [
            {
              "end_sec": 0.288,
              "start_sec": 0
            },
            {
              "end_sec": 6.929,
              "start_sec": 6.368
            },
            {
              "end_sec": 20.084,
              "start_sec": 19.048
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
          "topic": "business_management/project_management",
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
      "sampleId": "EN2001a_utterance_00002",
      "dataset": "AMI",
      "title": "AMI smoke: software planning topic",
      "note": "New AMI smoke sample: a longer software-planning discussion with topic, metadata VAD, and multi-speaker labels generated in the latest run.",
      "audio": "assets/audio/ami_EN2001a_utterance_00002.wav",
      "transcript": "So we should probably prioritize our packages. Yeah, now I'd say if for the prototype if we just like wherever possible p chunk in the stuff that we have um pre-annotated and stuff, and for the stuff that we don't have pre-annotated write like a stupid baseline, then we should probably be able to basically that means we focus on on the interface first sort of, so that we we take the the ready-made parts and just see how we get them work together in the interface the way we want and and then we have a working prototype. And then we can go back and replace pieces either by our own components or by more sophisticated compo po components of our own. So it's probably feasible. The thing is I'm away this weekend. So that's for me Mm. Yeah. Yeah. Yeah, I mean if we just want to have um some data for the user face, could even be random data. Uh mm mm Oh yeah, um yeah. No. But also I might like the the similarity thing, like my just my matrix itself for my stuff, I c I I think I can do that fairly quickly because I have the algorithms. Yeah, I think today's meeting is really the one where we where we sort of settle down the data structure and as soon as we have that, uh probably like after today's meeting, we then actually need to Yeah. Yeah, I'm Yeah.",
      "nativeMetadata": {
        "source": "ami_en2001a_utterances/sample.native_metadata.utterances"
      },
      "durationSec": 72.5885,
      "tags": {
        "basic_acoustic": {
          "c50": null,
          "channels": 1,
          "dnsmos_bak": null,
          "dnsmos_ovrl": null,
          "dnsmos_p808": null,
          "dnsmos_sig": null,
          "duration_sec": 72.5885,
          "sample_rate_hz": 16000,
          "silence_ratio": 0.025286,
          "silence_segments": [
            {
              "end_sec": 1.036,
              "start_sec": 0
            },
            {
              "end_sec": 72.5885,
              "start_sec": 71.789
            }
          ],
          "snr_db": null
        },
        "language_content": {
          "filler": null,
          "language": null,
          "punctuation": null,
          "repetition": null,
          "topic": "technology_engineering/software_engineering",
          "word_count": null
        },
        "sound_field_scene": {
          "audio_events": null,
          "c50": null,
          "far_field": null,
          "music": null,
          "rt60": null,
          "sound": null
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
      "note": "Longer meeting utterance for showing transcript-derived language tags.",
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
          "topic": null,
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
          "multi_speaker": null,
          "speaker_change": null,
          "speaker_overlap": null
        }
      }
    },
    {
      "row": 24,
      "sampleId": "EN2001a_utterance_00005",
      "dataset": "AMI",
      "title": "Meeting speech: short turns",
      "note": "Meeting speech with short turns and punctuation-rich transcript.",
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
          "topic": null,
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
          "multi_speaker": null,
          "speaker_change": null,
          "speaker_overlap": null
        }
      }
    },
    {
      "row": 25,
      "sampleId": "EN2001a_utterance_00006",
      "dataset": "AMI",
      "title": "Meeting speech: clicking",
      "note": "Longer meeting speech where PANNs detects Clicking in the background.",
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
          "topic": null,
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
          "multi_speaker": null,
          "speaker_change": null,
          "speaker_overlap": null
        }
      }
    },
    {
      "row": 1,
      "sampleId": "1089-134686-0000",
      "dataset": "LibriSpeech",
      "title": "Clean baseline: English",
      "note": "Clean read English speech baseline with no high-confidence background sound.",
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
          "topic": null,
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
          "multi_speaker": null,
          "speaker_change": null,
          "speaker_overlap": null
        }
      }
    },
    {
      "row": 6,
      "sampleId": "BAC009S0764W0121",
      "dataset": "AISHELL-1",
      "title": "Clean baseline: Mandarin",
      "note": "Clean Mandarin ASR baseline for language tagging comparison.",
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
          "topic": null,
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
          "multi_speaker": null,
          "speaker_change": null,
          "speaker_overlap": null
        }
      }
    },
    {
      "row": 11,
      "sampleId": "sa1",
      "dataset": "TIMIT",
      "title": "Clean baseline: TIMIT",
      "note": "Clean TIMIT baseline with sentence punctuation.",
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
          "topic": null,
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
          "multi_speaker": null,
          "speaker_change": null,
          "speaker_overlap": null
        }
      }
    },
    {
      "row": 30,
      "sampleId": "street_traffic-barcelona-161-4901-a",
      "dataset": "TUT Urban Acoustic Scenes 2018",
      "title": "Scene contrast: street traffic",
      "note": "A single no-transcript street-traffic scene kept as contrast for the Vehicle label.",
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
          "topic": null,
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
          "multi_speaker": null,
          "speaker_change": null,
          "speaker_overlap": null
        }
      }
    }
  ]
};

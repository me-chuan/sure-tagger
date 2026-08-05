"""Local runtime paths.

Fill FIRERED_VAD_MODEL_DIR with the local FireRedVAD non-streaming VAD model
directory before running silence tagging.

Fill BROUHAHA_MODEL_PATH with the local Brouhaha checkpoint before running
SNR/C50 tagging. The default location is inside this project.

Fill RECRIR_* with the local Rec-RIR repository, config, and checkpoint before
running sound-field RIR/RT60/C50 tagging. The default location is inside this
project.

Model tools can run in subprocesses so incompatible model dependencies do not
need to share one Python environment.
"""


FIRERED_VAD_MODEL_DIR = "models/FireRedVAD/pretrained_models/FireRedVAD/VAD"
FIRERED_VAD_PYTHON = ".runtime/fireredvad_rebuild_py310/bin/python"

BROUHAHA_REPO_DIR = "models/brouhaha/brouhaha-vad"
BROUHAHA_MODEL_PATH = "models/brouhaha/brouhaha-vad/models/best/checkpoints/best.ckpt"
BROUHAHA_MODEL_VERSION = "github:marianne-m/brouhaha-vad@9132cbe62ac78f90abdbc21bcf6ec6cfe9bb4891"
BROUHAHA_PYTHON = ".runtime/fireredvad_rebuild_py310/bin/python"

RECRIR_REPO_DIR = "models/Rec-RIR"
RECRIR_CONFIG_PATH = "models/Rec-RIR/config/Rec-RIR.toml"
RECRIR_CHECKPOINT_PATH = "models/Rec-RIR/ckpt/epoch35.tar"
RECRIR_MODEL_VERSION = "github:Audio-WestlakeU/Rec-RIR@27d03a98bc9a5504a76f377147f36dc7ad169ac6"
RECRIR_PYTHON = ".runtime/recrir_py310_torch271/bin/python"

MOSS_DIARIZE_ENDPOINT = ""
MOSS_DIARIZE_MODEL = "OpenMOSS-Team/MOSS-Transcribe-Diarize"
MOSS_DIARIZE_TIMEOUT_SEC = 900
MOSS_DIARIZE_MAX_NEW_TOKENS = 65536
MOSS_DIARIZE_API_KEY = ""

SPEAKER_CHANNEL_WINDOW_SEC = 0.05
SPEAKER_CHANNEL_ENERGY_THRESHOLD = 500.0
SPEAKER_CHANNEL_LEAKAGE_RELATIVE_DB = -18.0
SPEAKER_MIN_SEGMENT_DURATION_SEC = 0.10
SPEAKER_MERGE_SAME_SPEAKER_GAP_SEC = 0.30

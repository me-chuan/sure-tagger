"""Local runtime paths.

Fill FIRERED_VAD_MODEL_DIR with the local FireRedVAD non-streaming VAD model
directory before running silence tagging.

Fill BROUHAHA_MODEL_PATH with the local Brouhaha checkpoint before running v3
SNR/C50 tagging. The default location is inside this project.

Fill RECRIR_* with the local Rec-RIR repository, config, and checkpoint before
running sound-field RIR/RT60/C50 tagging. The default location is inside this
project.
"""


FIRERED_VAD_MODEL_DIR = "models/FireRedVAD/pretrained_models/FireRedVAD/VAD"

BROUHAHA_REPO_DIR = "models/brouhaha/brouhaha-vad"
BROUHAHA_MODEL_PATH = "models/brouhaha/brouhaha-vad/models/best/checkpoints/best.ckpt"
BROUHAHA_MODEL_VERSION = "github:marianne-m/brouhaha-vad@9132cbe62ac78f90abdbc21bcf6ec6cfe9bb4891"

RECRIR_REPO_DIR = "models/Rec-RIR"
RECRIR_CONFIG_PATH = "models/Rec-RIR/config/Rec-RIR.toml"
RECRIR_CHECKPOINT_PATH = "models/Rec-RIR/ckpt/epoch35.tar"
RECRIR_MODEL_VERSION = "github:Audio-WestlakeU/Rec-RIR@27d03a98bc9a5504a76f377147f36dc7ad169ac6"

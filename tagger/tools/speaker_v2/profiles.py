"""Versioned speaker-v2 run profiles and per-claim source policies."""

import copy
import hashlib

from tagger.tools.speaker_v2.contracts import canonical_json


POLICY_SCHEMA_VERSION = "speaker_v2.claim_policy.v1"
POLICY_VERSION = "speaker_v2.claim_policy.20260831.1"
PROFILE_SCHEMA_VERSION = "speaker_v2.run_profile.v1"

CLAIMS = (
    "speaker_count",
    "multi_speaker",
    "speaker_overlap",
    "speaker_change",
)

MOSS_SOURCE = "moss_transcribe_diarize"
SORTFORMER_SOURCE = "nvidia_streaming_sortformer_4spk_v2"
PYANNOTE_SOURCE = "pyannote_community_1"
FIRERED_ASR_SOURCE = "fireredasr2_aed"

SOURCE_REGISTRY = {
    MOSS_SOURCE: {"capability": "speaker_timeline"},
    SORTFORMER_SOURCE: {"capability": "speaker_timeline"},
    PYANNOTE_SOURCE: {"capability": "speaker_timeline"},
    "firered_vad": {"capability": "speech_coverage"},
    "brouhaha_vad": {"capability": "speech_coverage"},
    "campplus_speaker_verification": {
        "capability": "speaker_identity_comparison"
    },
    "speechbrain_ecapa_voxceleb": {
        "capability": "speaker_identity_comparison"
    },
    "whisper_base_lexical_clock": {"capability": "lexical_timeline"},
    FIRERED_ASR_SOURCE: {"capability": "asr_transcript"},
}

MODEL_KEYS = (
    "moss",
    "firered_asr",
    "vad",
    "campplus",
    "whisper",
    "sortformer",
    "pyannote",
    "ecapa",
    "brouhaha",
)


class ClaimPolicyError(ValueError):
    pass


def _claim(
    primary,
    guard=(),
    fallback=(),
    excluded=(),
    selection="first_usable",
    guard_rules=None,
):
    return {
        "primary_sources": list(primary),
        "guard_sources": list(guard),
        "fallback_sources": list(fallback),
        "excluded_sources": list(excluded),
        "selection": str(selection),
        "guard_rules": dict(guard_rules or {}),
    }


_ALL_TIMELINES = (MOSS_SOURCE, SORTFORMER_SOURCE, PYANNOTE_SOURCE)

_PROFILES = {
    "legacy-shadow": {
        "description": "Frozen all-timeline v2-shadow behavior",
        "models": {
            "moss": True,
            "firered_asr": True,
            "vad": True,
            "campplus": True,
            "whisper": True,
            "sortformer": True,
            "pyannote": True,
            "ecapa": False,
            "brouhaha": False,
        },
        "claims": {
            claim_name: _claim(_ALL_TIMELINES, selection="all_usable")
            for claim_name in CLAIMS
        },
    },
    "quality-shadow": {
        "description": "Measured per-claim specialists with safe shadow guards",
        "models": {
            "moss": True,
            "firered_asr": True,
            "vad": True,
            "campplus": False,
            "whisper": False,
            "sortformer": True,
            "pyannote": True,
            "ecapa": True,
            "brouhaha": True,
        },
        "claims": {
            "speaker_count": _claim(
                (SORTFORMER_SOURCE,),
                fallback=(MOSS_SOURCE,),
                excluded=(PYANNOTE_SOURCE,),
            ),
            "multi_speaker": _claim(
                (SORTFORMER_SOURCE,),
                guard=(MOSS_SOURCE,),
                excluded=(PYANNOTE_SOURCE,),
                guard_rules={MOSS_SOURCE: "negative_false_positive_guard"},
            ),
            "speaker_overlap": _claim(
                (PYANNOTE_SOURCE,),
                guard=(SORTFORMER_SOURCE, MOSS_SOURCE),
                fallback=(SORTFORMER_SOURCE,),
                guard_rules={
                    SORTFORMER_SOURCE: "secondary_overlap_witness",
                    MOSS_SOURCE: "positive_only_corroboration",
                },
            ),
            "speaker_change": _claim(
                (MOSS_SOURCE,),
                guard=(SORTFORMER_SOURCE,),
                fallback=(SORTFORMER_SOURCE,),
                excluded=(PYANNOTE_SOURCE,),
                guard_rules={SORTFORMER_SOURCE: "recall_witness"},
            ),
        },
    },
    "lean-shadow": {
        "description": "Cost-oriented profile without MOSS/legacy guards",
        "models": {
            "moss": False,
            "firered_asr": True,
            "vad": False,
            "campplus": False,
            "whisper": False,
            "sortformer": True,
            "pyannote": True,
            "ecapa": True,
            "brouhaha": True,
        },
        "claims": {
            "speaker_count": _claim(
                (SORTFORMER_SOURCE,), excluded=(PYANNOTE_SOURCE,)
            ),
            "multi_speaker": _claim(
                (SORTFORMER_SOURCE,), excluded=(PYANNOTE_SOURCE,)
            ),
            "speaker_overlap": _claim(
                (PYANNOTE_SOURCE,),
                guard=(SORTFORMER_SOURCE,),
                fallback=(SORTFORMER_SOURCE,),
            ),
            "speaker_change": _claim(
                (SORTFORMER_SOURCE,), excluded=(PYANNOTE_SOURCE,)
            ),
        },
    },
}


def available_profiles():
    return tuple(sorted(_PROFILES))


def expand_profile(profile_id):
    profile_id = str(profile_id)
    if profile_id not in _PROFILES:
        raise ClaimPolicyError("unknown speaker-v2 profile: %s" % profile_id)
    definition = copy.deepcopy(_PROFILES[profile_id])
    policy = {
        "schema_version": POLICY_SCHEMA_VERSION,
        "policy_version": POLICY_VERSION,
        "profile_id": profile_id,
        "claims": definition["claims"],
    }
    validate_claim_policy(policy)
    policy["policy_hash"] = claim_policy_hash(policy)
    return {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "profile_id": profile_id,
        "description": definition["description"],
        "models": definition["models"],
        "claim_policy": policy,
    }


def claim_policy_hash(policy):
    identity = copy.deepcopy(dict(policy))
    identity.pop("policy_hash", None)
    return hashlib.sha256(canonical_json(identity).encode("utf-8")).hexdigest()


def validate_claim_policy(policy):
    if not isinstance(policy, dict):
        raise ClaimPolicyError("claim_policy must be an object")
    if policy.get("schema_version") != POLICY_SCHEMA_VERSION:
        raise ClaimPolicyError("unsupported claim policy schema")
    if not policy.get("policy_version"):
        raise ClaimPolicyError("claim policy version is required")
    claims = policy.get("claims")
    if not isinstance(claims, dict) or set(claims) != set(CLAIMS):
        raise ClaimPolicyError("claim policy must define exactly: %s" % ", ".join(CLAIMS))
    for claim_name in CLAIMS:
        _validate_claim_rule(claim_name, claims[claim_name])
    expected_hash = policy.get("policy_hash")
    if expected_hash and str(expected_hash) != claim_policy_hash(policy):
        raise ClaimPolicyError("claim policy hash does not match content")
    return policy


def _validate_claim_rule(claim_name, rule):
    if not isinstance(rule, dict):
        raise ClaimPolicyError("%s rule must be an object" % claim_name)
    list_fields = (
        "primary_sources",
        "guard_sources",
        "fallback_sources",
        "excluded_sources",
    )
    for field in list_fields:
        values = rule.get(field)
        if not isinstance(values, list):
            raise ClaimPolicyError("%s.%s must be a list" % (claim_name, field))
        if len(values) != len(set(values)):
            raise ClaimPolicyError("%s.%s contains duplicates" % (claim_name, field))
        unknown = sorted(set(values) - set(SOURCE_REGISTRY))
        if unknown:
            raise ClaimPolicyError(
                "%s.%s references unknown sources: %s"
                % (claim_name, field, ", ".join(unknown))
            )
        wrong_capability = [
            source
            for source in values
            if SOURCE_REGISTRY[source]["capability"] != "speaker_timeline"
        ]
        if wrong_capability:
            raise ClaimPolicyError(
                "%s.%s must contain timeline sources only" % (claim_name, field)
            )
    primary = set(rule["primary_sources"])
    fallback = set(rule["fallback_sources"])
    excluded = set(rule["excluded_sources"])
    participating = primary | set(rule["guard_sources"]) | fallback
    if excluded.intersection(participating):
        raise ClaimPolicyError("%s excluded sources also participate" % claim_name)
    if primary.intersection(fallback):
        raise ClaimPolicyError("%s primary and fallback sources overlap" % claim_name)
    if rule.get("selection") not in ("first_usable", "all_usable"):
        raise ClaimPolicyError("%s has unsupported selection mode" % claim_name)
    guard_rules = rule.get("guard_rules", {})
    if not isinstance(guard_rules, dict):
        raise ClaimPolicyError("%s.guard_rules must be an object" % claim_name)
    if not set(guard_rules).issubset(set(rule["guard_sources"])):
        raise ClaimPolicyError("%s guard_rules reference non-guard sources" % claim_name)

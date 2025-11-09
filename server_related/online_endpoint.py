"""
This file implements endpoint detection using
https://github.com/kaldi-asr/kaldi/blob/master/src/online2/online-endpoint.h
as a reference
"""
import argparse
from dataclasses import dataclass

from .utils import str2bool


@dataclass
class OnlineEndpointRule:
    # If True, for this endpointing rule to apply there must
    # be nonsilence in the best-path traceback.
    # For RNN-T decoding, a non-blank token is considered as non-silence
    # 0 means must not contain nonsilence(must only silence), 1 means must contain nonsilence
    # other means both are permitted
    contain_nonsilence: int

    # This endpointing rule requires duration of trailing silence
    # (in seconds) to be >= this value.
    min_trailing_silence: float

    # This endpointing rule requires utterance-length (in seconds)
    # to be >= this value.
    min_utterance_length: float


@dataclass
class OnlineEndpointConfig:
    # rule1 times out after 5 seconds of silence, even if we decoded nothing.
    rule1: OnlineEndpointRule = OnlineEndpointRule(
        contain_nonsilence=0,
        min_trailing_silence=2.0,
        min_utterance_length=0.0,
    )

    # rule2 times out after 2.0 seconds of silence after decoding something,
    rule2: OnlineEndpointRule = OnlineEndpointRule(
        contain_nonsilence=1,
        min_trailing_silence=60.0,
        min_utterance_length=0.0,
    )
    # rule3 times out after the utterance is 20 seconds long, regardless of
    # anything else.
    rule3: OnlineEndpointRule = OnlineEndpointRule(
        contain_nonsilence=2,
        min_trailing_silence=0.0,
        min_utterance_length=1.0,
    )

    @staticmethod
    def from_args(args: dict) -> "OnlineEndpointConfig":
        """
        Args:
          args:
            It contains the arguments parsed from
            :func:`add_online_endpoint_arguments`
        """
        rule1 = OnlineEndpointRule(
            contain_nonsilence=args[
                "endpoint_rule1_contain_nonsilence"
            ],
            min_trailing_silence=args["endpoint_rule1_min_trailing_silence"],
            min_utterance_length=args["endpoint_rule1_min_utterance_length"],
        )

        rule2 = OnlineEndpointRule(
            contain_nonsilence=args[
                "endpoint_rule2_contain_nonsilence"
            ],
            min_trailing_silence=args["endpoint_rule2_min_trailing_silence"],
            min_utterance_length=args["endpoint_rule2_min_utterance_length"],
        )

        rule3 = OnlineEndpointRule(
            contain_nonsilence=args[
                "endpoint_rule3_contain_nonsilence"
            ],
            min_trailing_silence=args["endpoint_rule3_min_trailing_silence"],
            min_utterance_length=args["endpoint_rule3_min_utterance_length"],
        )

        return OnlineEndpointConfig(rule1=rule1, rule2=rule2, rule3=rule3)


def _add_rule_arguments(
        parser: argparse.ArgumentParser,
        prefix: str,
        rule: OnlineEndpointRule,
):
    p = prefix.replace(".", "_")

    parser.add_argument(
        f"--{prefix}.contain-nonsilence",
        type=int,
        dest=f"{p}_contain_nonsilence",
        default=rule.contain_nonsilence,
        help="""If true, for this endpointing rule to apply there must be
        nonsilence in the best-path traceback. For RNN-T decoding, a non-blank
        token is considered as non-silence""",
    )

    parser.add_argument(
        f"--{prefix}.min-trailing-silence",
        type=float,
        dest=f"{p}_min_trailing_silence",
        default=rule.min_trailing_silence,
        help="""This endpointing rule requires duration of trailing silence
        (in seconds) to be >= this value.""",
    )

    parser.add_argument(
        f"--{prefix}.min-utterance-length",
        type=float,
        dest=f"{p}_min_utterance_length",
        default=rule.min_utterance_length,
        help="""This endpointing rule requires utterance-length (in seconds)
        to be >= this value.""",
    )


def add_online_endpoint_arguments():
    """Add command line arguments to configure online endpointing.

    It provides the following commandline arguments:

        --endpoint.rule1.contain-nonsilence
        --endpoint.rule1.min_trailing_silence
        --endpoint.rule1.min_utterance_length

        --endpoint.rule2.contain-nonsilence
        --endpoint.rule2.min_trailing_silence
        --endpoint.rule2.min_utterance_length

        --endpoint.rule3.contain-nonsilence
        --endpoint.rule3.min_trailing_silence
        --endpoint.rule3.min_utterance_length

    You can add more rules if there is a need.
    """
    parser = argparse.ArgumentParser(
        description="Parameters for online endpoint detection",
        add_help=False,
    )

    config = OnlineEndpointConfig()
    _add_rule_arguments(parser, prefix="endpoint.rule1", rule=config.rule1)
    _add_rule_arguments(parser, prefix="endpoint.rule2", rule=config.rule2)
    _add_rule_arguments(parser, prefix="endpoint.rule3", rule=config.rule3)

    return parser


def _rule_activated(
        rule: OnlineEndpointRule,
        trailing_silence: float,
        utterance_length: float,
):
    """
    Args:
      rule:
        The rule to be checked.
      trailing_silence:
        Trailing silence in seconds.
      utterance_length:
        Number of frames in seconds decoded so far.
    Returns:
      Return True if the given rule is activated; return False otherwise.
    """
    nonsilence_length = utterance_length - trailing_silence

    # # must not contain nonsilence (must only silence)
    # if rule.contain_nonsilence == 0:
    #     return (
    #             not contains_nonsilence
    #             and (trailing_silence > rule.min_trailing_silence)
    #             and (utterance_length > rule.min_utterance_length)
    #     )
    # # must contain nonsilence
    # elif rule.contain_nonsilence == 1:
    #     return (
    #             contains_nonsilence
    #             and (trailing_silence > rule.min_trailing_silence)
    #             and (utterance_length > rule.min_utterance_length)
    #     )
    # else:
    #     return (
    #             (trailing_silence > rule.min_trailing_silence)
    #             and (utterance_length > rule.min_utterance_length)
    #     )

    # (nonsilence_length, trailing_silence_length)
    level = ((3, 8), (4, 7), (5, 6), (6, 5), (8, 4), (10, 3), (12, 2), (15, 1.5), (18, 1), (22, 0.5), (30, -1))
    # all silence
    if nonsilence_length <= 0:
        if utterance_length >= 5:
            return True
        else:
            return False
    # contain nonsilence
    else:
        i = 0
        while i < len(level):
            if nonsilence_length < level[i][0]:
                break
            i += 1
        if i == 0:
            return False
        else:
            if trailing_silence >= level[i - 1][1]:
                return True
            else:
                return False


def endpoint_detected(
        config: OnlineEndpointConfig,
        num_frames_decoded: int,
        trailing_silence_frames: int,
        frame_shift_in_seconds: float,
) -> bool:
    """
    Args:
      config:
        The endpoint config to be checked.
      num_frames_decoded:
        Number of frames decoded so far.
      trailing_silence_frames:
        Number of trailing silence frames.
      frame_shift_in_seconds:
        Frame shift in seconds.
    Returns:
      Return True if any rule in `config` is activated; return False otherwise.
    """
    utterance_length = num_frames_decoded * frame_shift_in_seconds
    trailing_silence = trailing_silence_frames * frame_shift_in_seconds

    if _rule_activated(config.rule1, trailing_silence, utterance_length):
        return True

    if _rule_activated(config.rule2, trailing_silence, utterance_length):
        return True

    if _rule_activated(config.rule3, trailing_silence, utterance_length):
        return True

    return False

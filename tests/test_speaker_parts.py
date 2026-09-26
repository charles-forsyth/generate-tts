"""Tests for tagging multi-speaker transcript parts."""

from gen_tts.core import _multi_speaker_contents


def test_multi_speaker_parts_tagged() -> None:
    """Each speaker line becomes a part tagged with that speaker."""
    text = "Intro line\nHost: Hi.\nGuest: Hello!\nmore\n**Host**: Bye."
    c = _multi_speaker_contents(text, ["Host", "Guest"])
    got = [(p.speech_metadata.speaker, p.text) for p in c.parts]
    assert got == [("Host", "Intro line Hi."), ("Guest", "Hello! more"), ("Host", "Bye.")]


def test_multi_speaker_no_prefix_falls_back_to_first() -> None:
    """Text with no speaker prefix goes to the first speaker."""
    c = _multi_speaker_contents("just text", ["Host", "Guest"])
    assert c.parts[0].speech_metadata.speaker == "Host"

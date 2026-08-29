from pathlib import Path

from ara_eve.agent_voice import GENERATE_CHAR_CAP, STREAM_CHAR_CAP, chunk_for_generate
from ara_eve.help import (
    DEFAULT_TOPIC,
    HELP_INTRO,
    help_markdown,
    help_spoken,
    list_topic_ids,
    load_help_script,
    resolve_topic,
    topic_choices,
)
from ara_eve.lips.catalog import get_event


def test_help_script_is_a_how_to_not_a_status_briefing():
    text = load_help_script()
    assert "End of guide" in text
    assert "Ara-Elizabeth" in text
    assert "Task win" in text
    assert "get_help" in text
    assert "End of briefing" not in text
    assert 0 < len(text) <= STREAM_CHAR_CAP


def test_all_topics_render_and_speak():
    ids = list_topic_ids()
    assert ids[0] == DEFAULT_TOPIC
    assert set(ids) == {
        "overview",
        "chat",
        "avatar",
        "voices",
        "lab",
        "deploy",
        "mcp",
        "faq",
    }
    for topic_id in ids:
        md = help_markdown(topic_id)
        spoken = help_spoken(topic_id)
        assert md.strip()
        assert spoken.strip()
        assert "Unknown help topic" not in md
        assert len(spoken) <= STREAM_CHAR_CAP
        chunks = chunk_for_generate(spoken)
        assert chunks
        assert all(1 <= len(c) <= GENERATE_CHAR_CAP for c in chunks)


def test_unknown_topic_lists_known_ids():
    text = help_markdown("nope-not-a-topic")
    assert "Unknown help topic" in text
    assert "overview" in text
    assert resolve_topic("Chat, stop, work mode").id == "chat"
    assert resolve_topic("").id == DEFAULT_TOPIC


def test_mcp_style_help_includes_intro():
    text = help_markdown("lab", include_intro=True)
    assert "Task win" in text
    assert HELP_INTRO.splitlines()[0] in text
    assert "does not change Ara's feelings" in text


def test_lab_catalog_help_is_still_task_success():
    event = get_event("help")
    assert event.title == "Task success"
    assert "Competence restored" in event.blurb


def test_app_separates_guide_from_lab_help():
    src = Path("app.py").read_text(encoding="utf-8")
    assert "Guide & help — how to use this Space" in src
    assert 'gr.Button("Task win"' in src
    assert 'gr.Button("Help"' not in src
    assert "get_help" in src
    assert "do_help_speak" in src
    assert "Read this topic aloud (builder)" in src
    assert "help_speak_btn.click(do_help_speak" in src
    # Ara's speak path stays hers.
    assert 'speak_btn.click(do_speak' in src


def test_dropdown_choices_are_label_value_pairs():
    choices = topic_choices()
    assert choices[0] == ("What this Space is", "overview")
    assert all(label and value for label, value in choices)

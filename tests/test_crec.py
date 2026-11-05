"""Parser tests on a hand-built granule in the GovInfo layout (2-space turn openings, 5-space
inserted material, page markers, recorder notes, presiding officer)."""

from congress_speech.crec import Granule, granule_lines, split_turns

HTML = """<html>
<head>
<title>Congressional Record, Volume 169 Issue 39 (Wednesday, March 1, 2023)</title>
</head>
<body><pre>
[Congressional Record Volume 169, Number 39 (Wednesday, March 1, 2023)]
[Senate]
[Pages S550-S560]
From the Congressional Record Online through the Government Publishing Office [<a href="https://www.gpo.gov">www.gpo.gov</a>]




                          LEGISLATIVE SESSION

  The PRESIDING OFFICER. Under the previous order, the Senate will
proceed to legislative session.
  The senior assistant legislative clerk read as follows:

       A joint resolution (H.J. Res. 30) providing for
     congressional disapproval of a rule.

  The PRESIDING OFFICER. The senior Senator from Hawaii.
  Mr. SCHATZ. Madam President, there is a group of officials in

[[Page S551]]

our country today who are engaged in a campaign.
  This is the second paragraph of the same turn.
  I ask unanimous consent that the letter be printed in the Record.

       Dear Senator: This letter is inserted material and is
     not part of the speech.

  Mrs. FISCHER. Madam President, I thank my colleague.
  Ms. JACKSON LEE of Texas. Madam Speaker, an unknown speaker.
  {time}  1430
  Mr. SCHATZ. I yield the floor.

                          ____________________

</pre></body>
</html>
"""

GRAN = Granule(
    gid="CREC-2023-03-01-pt1-PgS550-3", chamber="SENATE", title="TEST",
    speakers={
        "Mr. SCHATZ": {"bioguide": "S001194", "party": "D", "state": "HI", "chamber": "S",
                       "congress": 118, "full_name": "Brian Schatz"},
        "Mrs. FISCHER": {"bioguide": "F000463", "party": "R", "state": "NE", "chamber": "S",
                         "congress": 118, "full_name": "Deb Fischer"},
    },
)


def turns():
    return split_turns(GRAN, granule_lines(HTML))


def test_kinds_in_order():
    assert [(t.kind, t.speaker) for t in turns()] == [
        ("officer", "The PRESIDING OFFICER"),
        ("recorder", "RECORDER"),
        ("officer", "The PRESIDING OFFICER"),
        ("member", "Mr. SCHATZ"),
        ("member", "Mrs. FISCHER"),
        ("unmatched", "Ms. JACKSON LEE of Texas"),
        ("member", "Mr. SCHATZ"),
    ]


def test_turn_text_spans_page_break_and_paragraphs_and_drops_inserted_material():
    t = turns()[3]
    assert t.text.startswith("Madam President, there is a group of officials in our country today")
    assert "second paragraph of the same turn" in t.text
    assert "printed in the Record." in t.text
    assert "Dear Senator" not in t.text and "[[Page" not in t.text
    assert t.quoted_words == len("Dear Senator: This letter is inserted material and is not part of the speech.".split())


def test_member_metadata_from_mods():
    t = turns()[4]
    assert (t.bioguide, t.party, t.state, t.congress) == ("F000463", "R", "NE", 118)


def test_recorder_quoted_material_not_in_member_turn():
    rec = turns()[1]
    assert rec.text.startswith("The senior assistant legislative clerk read as follows:")
    assert "joint resolution" not in turns()[0].text


def test_timestamp_and_trailing_rule_are_dropped():
    last = turns()[-1]
    assert last.text == "I yield the floor."


def test_recorder_notes_about_members_end_the_turn():
    html = HTML.replace("  Mrs. FISCHER. Madam President, I thank my colleague.\n",
                        "  Mrs. FISCHER. Madam President, I thank my colleague.\n"
                        "  Mr. SCHATZ changed his vote from ``nay'' to ``yea.''\n")
    ts = split_turns(GRAN, granule_lines(html))
    fischer = [t for t in ts if t.speaker == "Mrs. FISCHER"][0]
    assert "changed his vote" not in fischer.text
    assert any(t.kind == "recorder" and "changed his vote" in t.text for t in ts)


def test_misspelled_name_resolves_to_the_mods_speaker():
    html = HTML.replace("  Mrs. FISCHER. Madam", "  Mrs. FISHCER. Madam")
    ts = split_turns(GRAN, granule_lines(html))
    assert ts[4].kind == "member" and ts[4].bioguide == "F000463"


def test_mention_inside_a_speech_is_not_a_turn():
    html = HTML.replace("  This is the second paragraph of the same turn.\n",
                        "  Mr. McCarthy said that this is the second paragraph.\n")
    ts = split_turns(GRAN, granule_lines(html))
    assert "Mr. McCarthy said" in ts[3].text

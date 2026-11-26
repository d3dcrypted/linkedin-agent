"""Self-check for the gate. Run: python3 -m unittest discover -s tests -v

Two things the gate has to get right, both about a part of the draft that is easy to
write by habit: the closing line decides whether a draft repeats a signature already
used, so it has to be the real closing line and not the pointer to the sources comment;
the image prompt decides whether the picture belongs to its post, so it has to carry the
post's own subject and not another draft's object.
"""
import importlib.util
import os
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("check_post", os.path.join(ROOT, "check_post.py"))
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)

POST = "A machine drafts my posts. A script checks them."
CLOSER = "Human thought, machine typing."
# Coherent (shares "machine" with POST) and unlike the objects in posts/, so the reuse
# check has nothing to object to.
PROMPT = ("a small brass lever machine with a glass plate on a matte grey desk, one blank page "
          "under the plate, an amber lamp above it, the page half out of the tray")
# Ten words of its own, none of them in POST.
DISJOINT = ("a shallow wooden tray holding blank index cards, a brass clip on the top card, "
            "the whole tray resting on a matte grey desk with soft light from the left")
# A different object, still tied to POST by "machine".
GAUGE = ("a brass dial gauge lying face up on a matte grey desk, its needle past the mark, "
         "a machine part resting beside it, an amber lamp above and soft light from the left")

TEMPLATE = """---
date: 2026-01-01
status: draft
sources:
  - https://example.com/a
---

%s

%s

Sources in the first comment.

## First comment

- Source: https://example.com/a

## Image prompt

    %s

**Alt text**: a blank page under a glass plate.

**Aspect** 4:5
"""


def draft(closing, prompt=PROMPT):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(TEMPLATE % (POST, closing, prompt))
        return f.name


def written(text):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(text)
        return f.name


class ClosingLine(unittest.TestCase):
    def test_pointer_paragraph_is_not_the_closing_line(self):
        path = draft("Human thought, machine typing.\n\nSources in the first comment.")
        self.assertEqual(cp.closer_of(path), "Human thought, machine typing.")

    def test_pointer_sentence_inside_the_closing_paragraph_is_stripped(self):
        path = draft("Human thought, machine typing. Sources in the first comment.")
        self.assertEqual(cp.closer_of(path), "Human thought, machine typing.")


class Gate(unittest.TestCase):
    def test_valid_draft_passes(self):
        errs, post, comment, sources = cp.check(draft(CLOSER))
        self.assertEqual(errs, [])
        self.assertEqual(sources, 1)

    def test_em_dash_is_rejected(self):
        errs, *_ = cp.check(draft("A machine \u2014 a script."))
        self.assertTrue(any("em dash" in e for e in errs), errs)


class ImagePrompt(unittest.TestCase):
    def test_prompt_disjoint_from_its_post_is_rejected(self):
        errs, *_ = cp.check(draft(CLOSER, DISJOINT))
        self.assertTrue(any("shares no word with the post" in e for e in errs), errs)

    def test_house_style_only_is_rejected(self):
        errs, *_ = cp.check(draft(CLOSER, " ".join(sorted(cp.HOUSE_WORDS))))
        self.assertTrue(any("house style only" in e for e in errs), errs)

    def test_reused_object_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "posts"))
            first = os.path.join(tmp, "posts", "first.md")
            second = os.path.join(tmp, "posts", "second.md")
            for p in (first, second):
                open(p, "w", encoding="utf-8").write(TEMPLATE % (POST, CLOSER, PROMPT))
            with mock.patch.object(cp, "ROOT", tmp):
                errs, *_ = cp.check(second)
        self.assertTrue(any("image object reused" in e for e in errs), errs)

    def test_a_new_object_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "posts"))
            open(os.path.join(tmp, "posts", "first.md"), "w", encoding="utf-8").write(
                TEMPLATE % (POST, CLOSER, PROMPT))
            second = os.path.join(tmp, "posts", "second.md")
            open(second, "w", encoding="utf-8").write(TEMPLATE % (POST, CLOSER, GAUGE))
            with mock.patch.object(cp, "ROOT", tmp):
                errs, *_ = cp.check(second)
        self.assertEqual(errs, [])


class Citations(unittest.TestCase):
    """The comment is checked against the frontmatter, not against good faith.

    'Every fact has a source' cannot be verified by reading a sentence; what can be
    verified is that the URLs in the comment are the URLs the draft was written from.
    """

    def test_url_not_declared_in_the_frontmatter_is_rejected(self):
        raw = (TEMPLATE % (POST, CLOSER, PROMPT)).replace(
            "- Source: https://example.com/a", "- Source: https://invented.example.org/x")
        errs, *_ = cp.check(written(raw))
        self.assertTrue(any("cited source not declared" in e for e in errs), errs)

    def test_declared_source_missing_from_the_comment_is_rejected(self):
        raw = (TEMPLATE % (POST, CLOSER, PROMPT)).replace(
            "- Source: https://example.com/a", "- A report nobody can check")
        errs, *_ = cp.check(written(raw))
        self.assertTrue(any("declared source not cited" in e for e in errs), errs)

    def test_draft_without_a_sources_list_is_rejected(self):
        raw = (TEMPLATE % (POST, CLOSER, PROMPT)).replace(
            "sources:\n  - https://example.com/a\n", "")
        errs, *_ = cp.check(written(raw))
        self.assertTrue(any("without a 'sources' list" in e for e in errs), errs)

    def test_a_parenthesised_url_is_the_same_url(self):
        """Wikipedia-style addresses end in a bracket; it belongs to the address."""
        raw = (TEMPLATE % (POST, CLOSER, PROMPT)).replace(
            "https://example.com/a", "https://en.wikipedia.org/wiki/Focal_point_(game_theory)")
        self.assertEqual(cp.check(written(raw))[0], [])


if __name__ == "__main__":
    unittest.main()

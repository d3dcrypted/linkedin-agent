"""Self-check for the gate. Run: python3 -m unittest discover -s tests -v

The closing line decides whether a draft repeats a signature already used, so it
has to be the real closing line and not the pointer to the sources comment.
"""
import importlib.util
import os
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("check_post", os.path.join(ROOT, "check_post.py"))
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)

PROMPT = " ".join(["a blank index card on a grey desk"] * 6)

TEMPLATE = """---
date: 2026-01-01
status: draft
---

A machine drafts my posts. A script checks them.

%s

## First comment

- Source: https://example.com/a

## Image prompt

    %s

**Alt text**: a blank index card on a grey desk.

**Aspect** 4:5
"""


def draft(closing):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(TEMPLATE % (closing, PROMPT))
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
        errs, post, comment, sources = cp.check(draft("Human thought, machine typing. Sources in the first comment."))
        self.assertEqual(errs, [])
        self.assertEqual(sources, 1)

    def test_em_dash_is_rejected(self):
        errs, *_ = cp.check(draft("A machine \u2014 a script. Sources in the first comment."))
        self.assertTrue(any("em dash" in e for e in errs), errs)


if __name__ == "__main__":
    unittest.main()

---
date: 2026-11-25
status: draft
seed: "Utilizzando la skill LinkedIn-agent fai un post per introdurre in max 300char la repo correlata, chi la può usare e fai riferimento al post appena creato di esempio specificando che sia stato fatto per testare il funzionamento"
humanized: blader/humanizer v4.0.0
voice: comedic-voice (deadpan opening, reversal on the closer, un solo cambio di tono)
sources:
  - https://github.com/d3dcrypted/linkedin-agent
  - https://github.com/d3dcrypted/linkedin-agent/blob/main/check_post.py
  - https://github.com/blader/humanizer
---

A machine drafts my LinkedIn posts. A script checks them.

linkedin-agent, public repo: thought in, sourced draft out. For anyone who writes technical posts and hates the research.

The post above is the test run to check it works.

Human thought, machine typing. Sources in the first comment.

## First comment

Sources:
- The repo: a public pipeline, one raw thought in and one draft out (post, first comment with the sources, image prompt). The skills behind it live there too: https://github.com/d3dcrypted/linkedin-agent
- The script that checks the draft: em dashes, curly quotes, exclamation marks, missing disclosure, missing sources, a reused closing line, and the image prompt are all blocked before a draft ships: https://github.com/d3dcrypted/linkedin-agent/blob/main/check_post.py
- humanizer (MIT, blader), the third-party skill the text goes through before it is saved. Declared dependency, not vendored: https://github.com/blader/humanizer

## Image prompt

    A photo of an editorial still life on a matte grey desk: a shallow wooden tray holding a small stack of blank index cards, the top card pushed half out and held by a small brass clip, a second brass clip resting beside the tray. Off-white wall behind, soft diffused light from the left, 50mm lens, shallow depth of field, subject off-centre with empty space on the right. Slate grey and off-white palette with one amber accent, calm and slightly dry. No text, no logos, no people.

**Alt text** (English, max 120 characters): A wooden tray of blank index cards on a grey desk, the top card clipped and pushed half out.

**Aspect** 4:5 (1080x1350) · **Negative** (only where the model has the field): blurry, low quality, jpeg artifacts, watermark, signature

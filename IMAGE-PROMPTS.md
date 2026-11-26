# Image prompts

Every draft in `posts/` ships with an image prompt. You paste it into any image
model, generate one image, and upload that image with the post. The prompt is
written for the post it belongs to, and it is the same shape every time, so the
images look like they come from one place instead of from six different tools.

This file is the guide. `AGENTS.md` says when an agent must produce the prompt;
this file says what a good one looks like and how to use it outside Hermes.

## The house style

Coherence across posts does not come from the prompt being long. It comes from a
fixed block that never changes, plus one variable part that carries the post.

Fixed, in every prompt:

| Slot | Value | Why |
| --- | --- | --- |
| Medium | editorial still-life photograph, on a desk | matches the voice: tools on the bench, not "innovation" |
| Palette | cool muted: slate grey, off-white, one warm amber accent | one accent is what makes the set recognisable in the feed |
| Light | soft diffused light from the left, no hard shadows | the most-skipped slot, and the one that changes the result most |
| Framing | 50mm, shallow depth of field, subject off-centre, generous empty space | leaves room for the feed crop |
| Absent | people, faces, hands, logos, brand marks, any lettering | rights and artifacts: see "Rules" below |
| Mood | calm and slightly dry | one word, at the end |

Variable, per post: **one or two objects**, and they have to come out of the post.
That is the whole per-post part.

## Deriving the object

The failure mode is a prompt that reads like every other prompt. The fixed block is
most of the words, so when the subject is picked by free association the image ends up
saying nothing about the post. A tray of index cards fits a post about automation, a
post about a hallway standoff and a post about backups equally well, which is exactly
why it is the wrong object. Derive it in three steps:

1. **Name the post's subject in one sentence**, in the post's own words: "a machine
   drafts the text and a script checks it", "a human gate sits in the workflow", "two
   people both step to the right".
2. **Make that sentence visible.** One or two objects, no metaphor, no diagram: a press
   feeding a sheet with a steel rule laid across it; a conveyor with a brass gate
   holding the last box; two identical blocks on a strip of tape, both nudged the same
   way. The object should *be* the sentence, not a symbol for the topic.
3. **Read the other drafts in `posts/` first**, and never reuse their object. The same
   object in two posts is the visual version of the same closing line: the easiest
   signature to correlate, and a follower of the profile sees it at once.

The self-check before you commit the block: *could this object sit under any other post
in this folder?* If yes it is the wrong object, go back to step 1.

`check_post.py` enforces the mechanical half: the prompt must carry at least four words
of its own beyond the house style, at least one word that also appears in the post, and
no more than 60% of its subject words in common with another draft. That is a floor,
not a proof. A prompt can pass it and still be a weak image, so the three steps above
are the rule and the gate is the tripwire: the gate catches the dissociation and the
repetition, the author catches the rest.

To re-brand the set, change the table. Nothing else in this file depends on it.

## The formula

Order matters more than length: a prompt reads like a set of instructions. This
is the order the FLUX documentation recommends, and the worked examples in the
Figma and Fawna guides follow it too.

1. **Image type and medium** — one opening sentence that sets the look.
   `Editorial still-life photograph on a desk,`
2. **Subject and action** — who or what, and what it is doing.
   `a single mechanical conveyor moving three plain cardboard boxes,`
3. **Setting** — where it happens, what surrounds it.
   `on a matte grey desk against an off-white wall,`
4. **Light** — source, direction, quality.
   `soft diffused light from the left,`
5. **Framing and detail** — shot size, lens, depth of field.
   `50mm lens, shallow depth of field, subject off-centre with empty space on the right,`
6. **Palette and mood** — the last refinement.
   `slate grey and off-white with one amber accent, calm and slightly dry.`

Two habits from the sources that are worth keeping:

- **Start with "A photo of"** if you want a photographic result. The phrase is a
  strong prior for photographic lighting and grain; leave it out and models drift
  toward illustration even when you asked for realism (Fawna).
- **Describe only what is visible.** "Remove any sentence that does not describe
  something visible" (FLUX docs). "Cozy", "professional", "cutting-edge" are not
  visible.

Length: 30 to 80 words is the range that works (Fawna). Longer is not better;
FLUX's own guide says a clear structure matters more than length, and to omit
quality tags such as "masterpiece".

## Aspect and size

Ask the model for the ratio, don't crop afterwards: models compose differently
for each aspect, so the framing is decided at generation time.

LinkedIn's own limits for a photo in a post (LinkedIn Help, *Share photos on
LinkedIn*): the ratio must be between **3:1 and 4:5**; recommended width **1080
px**; minimum **552 x 276**; **5 MB** per photo; up to 20 images; and a photo
cannot be resized or edited after it is posted. If the ratio is larger than 3:1
the image is **centred and cropped** to fit.

- **Default: 4:5, 1080 x 1350.** It is the tallest ratio LinkedIn allows, so it
  takes the most room in the mobile feed. The 2026 size guides agree this is the
  shape to use when you have no other reason.
- **1:1, 1080 x 1080** is the safe middle of the allowed range if you are unsure.
- **1.91:1, 1200 x 627** is the link-preview image, a different thing from a
  photo in a post (LinkedIn Help, *Customize the image and title of a LinkedIn
  Page post preview*).
- 16:9 is allowed but renders short in the feed. Don't export 16:9 out of habit.

Because a too-wide ratio gets centred and cropped, keep the subject off-centre
but well inside the frame, and keep the fixed block's "generous empty space".

## Negative prompts

A negative prompt is not a filter. It replaces the *unconditional* prediction in
classifier-free guidance, so the image is pushed away from what you named. Three
consequences that matter in practice:

- **It only works when guidance is on.** At guidance 1 the term cancels out. The
  distilled models that run at guidance 1 — Turbo, Lightning, LCM, FLUX schnell —
  ignore it entirely, and the box still sits in the UI.
- **Each word dilutes the others**, because they are averaged into one embedding.
  Five to eight concepts beat forty.
- **It names a register, not a prohibition.** "no hands" moves toward what the
  encoder associates with "hands". Put what you want in the positive prompt
  instead: "empty unmarked surfaces" rather than "no text".

Where the field exists (vendor documentation, read October 2026):

| Model family | Separate negative field |
| --- | --- |
| Stable Diffusion / SDXL (diffusers, A1111, Forge, ComfyUI) | Yes, with guidance > 1 |
| FLUX | No — positive reframing only |
| Gemini image models | No separate field; the guide asks for positive wording |
| Imagen 3 on Vertex AI | Legacy: only the 3.0 models |
| Midjourney | No box; `--no a, b, c` at the end of the prompt |
| Runway Gen-4 | No, and negative phrasing can give opposite results |

A useful default when the field exists, and short on purpose:

    blurry, low quality, jpeg artifacts, watermark, signature

Then add the one thing you actually saw in a failed generation. That is the
genuinely effective use of the field: name the fault, not a forum's list.

## Rules

- **No lettering in the image.** Text in an image is a special capability that
  needs its own explicit, longer prompt (FLUX docs), and it is the fastest way to
  ship a typo you cannot edit. Put the words in the post, or add them in an
  editor afterwards.
- **No real logos, no brand marks, no recognizable real people.** Generated brand
  marks are wrong by definition and are somebody's trademark; a recognizable face
  is a person's likeness. The house style's "absent" row exists for this.
- **Disclose it.** The post already says the text was assembled by an AI. When an
  image is AI-generated, say so in the same breath — one clause is enough.
- **Alt text, in English, max 120 characters.** LinkedIn supports alt text up to
  120 characters, it cannot be added or edited after posting, and it is not
  available in the mobile apps: add it from a desktop browser while uploading.
  LinkedIn may assign alt text automatically and tell you it did — overwrite it
  with yours. English because the post is English and a screen reader reads them in
  the same language.
- **No quality spam, no resolution claims, no stacked adjectives.** "4K ultra HD",
  "beautiful stunning gorgeous": the guides say they are noise, and they bias
  toward oversaturated output.
- **At most three distinct subjects** in one image; models merge or drop features
  past that count.
- **Iterate by changing one thing.** Start simpler than the final prompt, look at
  the result, then add or fix exactly one slot. Every vendor guide says the same.

## Using it outside Hermes

The prompt is plain text and it is not tied to any tool. Copy the block from the
draft and paste it wherever you generate images.

- **Chat models** (ChatGPT, Gemini, Copilot): paste the prompt, add the ratio
  ("4:5"), and rephrase anything negative as a positive — those models have no
  negative field, and one vendor's guide says plainly to put your negatives in the
  regular prompt.
- **Midjourney**: paste the prompt and append `--ar 4:5` and, if you need it,
  `--no text, logo, watermark`. Keep `--no` lists to three to five terms; it is
  read word by word, so "modern clothing" after `--no` reads as "no modern",
  "no clothing".
- **Stable Diffusion / SDXL** (A1111, Forge, ComfyUI): prompt in the positive
  field, the short list above in the negative field, guidance in the 5-9 band.
- **FLUX**: positive prompt only. Replace every negation: "no crowds" becomes
  "empty room, one object".
- **Any tool**: generate at 4:5, check the result against the Rules above, upload
  from a desktop browser, paste the alt text, disclose.

If you are an agent with vision, look at the generated image before declaring the
job done: garbled lettering, a fake logo, an extra limb or a crop that ate the
subject are all reasons to regenerate, not to publish.

## Worked example

Prompt for a draft about automating IT processes with LLMs:

    A photo of an editorial still life on a desk: a short mechanical conveyor
    carrying three plain cardboard boxes, the last one tilted off the belt onto
    the desk. Matte grey desk, off-white wall behind, soft diffused light from
    the left, 50mm lens, shallow depth of field, subject off-centre with empty
    space on the right. Slate grey and off-white palette with one amber accent,
    calm and slightly dry. No text, no logos, no people.

Alt text (English, 103 characters): `A conveyor belt on a desk pushes three
cardboard boxes, the last one slides off the belt.`

## Sources

Read while writing this file, October-November 2026. `web_extract` was down on
the machine this was written on, so the quotes come from search results and the
pages were not read in full.

- Black Forest Labs, *Building a Good Prompt* — prompt order, "omit quality tags
  such as masterpiece", text-in-image as a longer-prompt case, no negative
  prompts. https://docs.eu.bfl.ai/guides/prompting_unified_building
- Figma, *How To Write AI Image Prompts* — five-step method, mood last,
  intensifiers instead of details. https://www.figma.com/resource-library/how-to-write-ai-image-prompts/
- Fawna, *Writing a great image prompt* — "A photo of", four-part formula, 30-80
  words, lens map, aspect first, what to avoid.
  https://fawna.ai/docs/prompting/image-prompt/
- Google, *Write effective prompts for Google Pics* — positive framing, camera
  terms, lighting and color grading, iterate.
  https://support.google.com/docs/answer/17499238
- *Negative Prompt: What It Is and Which Models Use It (2026)* — vendor-by-vendor
  table of negative-prompt support. https://designerbox.ai/blog/negative-prompt/
- Hugging Face, Diffusers *Prompting* — `negative_prompt` and guidance scale.
  https://huggingface.co/docs/diffusers/using-diffusers/weighted_prompts
- LinkedIn Help, *Share photos on LinkedIn* — 3:1 to 4:5, 1080 px recommended,
  552x276 minimum, 5 MB, 20 images, centred and cropped beyond 3:1. Read through
  the 2026 size guides that quote it: https://www.trackmedia.app/blog/linkedin-post-image-size
- LinkedIn Help, *Customize the image and title of a LinkedIn Page post preview* —
  1.91:1 and 1200 x 627.
- LinkedIn Help, *Add alternative text to images for accessibility* — where alt
  text is added, automatic assignment. https://www.linkedin.com/help/linkedin/answer/a519856
- Perkins School for the Blind, *How to add alt text on social media* — the
  120-character limit, no edit after posting, desktop only.
  https://www.perkins.org/how-to-add-alt-text-on-social-media/

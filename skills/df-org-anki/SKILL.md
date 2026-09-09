---
name: df-org-anki
description: >-
  How to use the org-anki Emacs package (v4.x): sync org-mode entries to Anki via
  AnkiConnect. Use when the user says "org-anki", "df-org-anki", asks how to make
  Anki cards from org-mode, how to sync/update/delete/import Anki decks from org,
  how cloze / note types / decks / tags / media work in org-anki, or wants an
  example .org file. Teaching + reference skill, not a card generator (see
  df-flashcard-org for generating card content).
---

# Using org-anki

`org-anki` (https://github.com/eyeinsky/org-anki, Package v4.x) is a minor mode that
turns org-mode headings into Anki notes and pushes them through the **AnkiConnect**
add-on's HTTP API. Anki must be running with AnkiConnect installed.

When answering "how do I…" questions, read `reference.md` for the exhaustive
behavior map (every command, field-resolution rule, precedence chain, and knob,
each tied to the function in `org-anki.el` that implements it). Show the user
`examples/demo.org` when they want a worked file — it exercises every feature with
inline comments explaining which code path each heading hits.

## The mental model

One org **heading** = one Anki **note**. On sync:

- No `ANKI_NOTE_ID` property yet → `addNote`, and the returned id is written back
  into the heading's `:PROPERTIES:` drawer.
- Has `ANKI_NOTE_ID` → `updateNoteFields` + a tag add/remove diff.

Fields, deck, note type and tags are all derived from the heading, its
`:PROPERTIES:`, inherited parent properties, `#+KEYWORD:` lines, and Emacs
`defcustom` defaults — in that precedence order.

## How many distinct ways to use it

`reference.md` enumerates them; the top-level axes:

1. **10 interactive commands** — `org-anki-sync-entry`, `org-anki-sync-all`,
   `org-anki-update-all`, `org-anki-update-dir`, `org-anki-delete-entry`,
   `org-anki-delete-all`, `org-anki-cloze-dwim`, `org-anki-browse-entry`,
   `org-anki-import-deck`, `org-anki-add-model`.
2. **6 ways to lay out a note's fields** — title+body; all fields as child
   subheadings; N−1 subheadings + one field from body; cloze in title; cloze in
   body; cloze in title with body as `Extra`.
3. **5 built-in note types + unlimited custom** — `Basic`,
   `Basic (and reversed card)`, `Basic (optional reversed card)`, `NameDescr`,
   `Cloze`, plus any model registered via `org-anki-add-model` /
   `org-anki-model-fields`.
4. **4-level precedence** for deck (`ANKI_DECK`) and for note type
   (`ANKI_NOTE_TYPE`): entry property → inherited parent property → `#+KEYWORD:` →
   `defcustom` default.
5. **4 tag sources** — the heading's own org tags, inherited `ALLTAGS` from
   parents (`org-anki-inherit-tags`), the `#+ANKI_TAGS:` global, minus
   `org-anki-ignored-tags`; with optional hierarchical-tag separator rewriting.
6. **3 ways to scope a bulk sync** — `#+ANKI_MATCH:` / `org-anki-default-match` /
   `org-anki-skip-function`.
7. **2 media transports** — filesystem copy into Anki's media dir, or base64
   upload over AnkiConnect (`org-anki-media-method`).
8. **3 content transforms** — org→HTML export, LaTeX→Anki-MathJax rewrite,
   per-field template functions (`org-anki-field-templates`).
9. **1 reverse direction** — `org-anki-import-deck` pulls an existing Anki deck
   into an `.org` buffer (needs `pandoc`).

## Minimal setup to hand the user

```elisp
(use-package org-anki
  :config
  (setq org-anki-default-deck "Default"
        org-anki-inherit-tags t
        org-anki-ignored-tags '("noexport"))
  ;; register any non-default note types you use:
  (org-anki-add-model "NameDescr" "Name" "Descr"))
```

Then in Anki: install AnkiConnect (add-on code `2055492159`), restart Anki, keep
it open. Default endpoint is `http://127.0.0.1:8765`; set `org-anki-api-key` if
AnkiConnect auth is enabled.

## Smallest possible card

```org
* What add-on does org-anki talk to?  :anki:
AnkiConnect.
```

`M-x org-anki-sync-entry` with point in the heading creates it in
`org-anki-default-deck` as a `Basic` note (Front = title, Back = body).

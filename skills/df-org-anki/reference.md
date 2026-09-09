# org-anki behavior reference

Every entry below names the function in `org-anki.el` (v4.0.2) that implements it,
so answers can quote real code. `~/path` refers to the user's copy of the package.

---

## 1. Interactive commands (10)

| Command | Effect | Key implementation |
|---|---|---|
| `org-anki-sync-entry` | Add-or-update the single note at point (+ tag diff). | `org-anki--sync-notes (list (org-anki--note-at-point))` |
| `org-anki-sync-all` | Sync every heading in the buffer matching the buffer's match query, filtered by `org-anki-skip-function`; only notes whose fields are all non-empty (`org-anki--note-complete`) are sent. | `org-map-entries 'org-anki--note-at-point (org-anki--get-match) nil org-anki-skip-function` |
| `org-anki-update-all` | Re-push only headings that already carry `ANKI_NOTE_ID` (implicit match `ANKI_NOTE_ID<>""`). Never creates new notes. | `org-map-entries … "ANKI_NOTE_ID<>\"\""` |
| `org-anki-update-dir` | Run `org-anki-update-all` over every `.org` file in a chosen directory. Prefix arg (`C-u`) recurses into subdirectories. | `directory-files-recursively` vs `directory-files` |
| `org-anki-delete-entry` | Delete the note at point from Anki (`deleteNotes`) and remove its `ANKI_NOTE_ID` property. Prompts `y-or-n`. | `org-anki--delete-notes_` |
| `org-anki-delete-all` | Same, for every `ANKI_NOTE_ID` heading in the buffer. Prompts once. | `org-anki--delete-notes_` |
| `org-anki-cloze-dwim` | Wrap the active region, or the word at point, as `{{cN::text::hint}}`. Numeric prefix = the `N`; then prompts for an optional hint. | `org-anki--region-to-cloze` |
| `org-anki-browse-entry` | Open Anki's Browse window filtered to `nid:<id>` of the note at point (`guiBrowse`). | `org-anki-browse-entry` |
| `org-anki-import-deck` | Reverse direction: pull an existing Anki deck (`findNotes` + `notesInfo`) into the current buffer as org headings. Best-effort; needs `pandoc`. | `org-anki--write-note`, `org-anki--parse-note` |
| `org-anki-add-model` | Not a sync — registers a note type + its ordered field names into `org-anki-model-fields` so org-anki knows how to fill it. | `org-anki-add-model` |

Non-interactive helpers you may reference: `org-anki-sync-all`/`update-all` accept an
optional `BUFFER` argument for scripting.

---

## 2. Field layout — 6 ways a heading becomes fields

All handled by `org-anki--get-fields` (dispatched from `org-anki--note-at-point`).
"Model fields" come from `org-anki-model-fields` for the resolved note type.

1. **Title + body (2-field models).** Heading title → field 1 (e.g. `Front`);
   body text up to the first child heading → field 2 (e.g. `Back`).
   Branch: `(= found-length 0)`.
2. **All fields as child subheadings.** Child headings one level deeper whose
   titles exactly match model field names supply those fields; their content is
   exported *including* their own sub-subentries (`org-anki--entry-content-full`).
   Branch: `(= fields-length found-length)`.
3. **N−1 subheadings + one from body.** If exactly one model field is missing
   from the child subheadings, it is taken from the pre-child body text.
   Branch: `(= fields-length (+ 1 found-length))`. More than one missing → error.
4. **Cloze in the title.** `org-anki--is-cloze` matches `{{c[0-9]+::…}}` in the
   title → note type forced to `Cloze`, `Text` = title. If body is non-empty and
   not itself cloze, body → `Extra`.
5. **Cloze in the body.** Same detection on the body → `Text` = body.
6. **Cloze title + Extra.** Special case of 4: `("Cloze" "Text" title "Extra" content)`.

Cloze syntax: `{{c1::hidden answer::optional hint}}`. Multiple `cN` groups per
note make multiple cards.

---

## 3. Note types

Defaults in `org-anki-model-fields`:

| Model | Fields | Notes |
|---|---|---|
| `Basic` | `Front` `Back` | default (`org-anki-default-note-type`) |
| `Basic (and reversed card)` | `Front` `Back` | Anki generates both directions |
| `Basic (optional reversed card)` | `Front` `Back` | reverse card only if `Add Reverse` field set (add it as a 3rd subheading) |
| `NameDescr` | `Name` `Descr` | example custom model |
| `Cloze` | `Text` `Extra` | auto-selected by cloze detection |

**Custom models:** `(org-anki-add-model "MyModel" "F1" "F2" "F3")` or set
`org-anki-model-fields` directly. The model must already exist in Anki with those
exact field names. `org-anki--get-model-fields` errors if the model is unknown.

---

## 4. Deck resolution (`org-anki--find-prop` with `ANKI_DECK`)

Precedence, first hit wins:

1. `:ANKI_DECK:` property on the heading
2. `:ANKI_DECK:` inherited from an ancestor heading (`org-entry-get … t`)
3. `#+ANKI_DECK:` buffer keyword (`org-anki--get-global-prop`)
4. `org-anki-default-deck` defcustom

If all four are nil → error. Use `::` in the name for Anki subdecks
(`Demo::Subdeck`).

---

## 5. Note-type resolution

Identical 4-level precedence via `org-anki--find-prop` with `ANKI_NOTE_TYPE`:
`:ANKI_NOTE_TYPE:` property → inherited → `#+ANKI_NOTE_TYPE:` → `org-anki-default-note-type`
("Basic"). Cloze detection (section 2) overrides all of this.

---

## 6. Tags (`org-anki--get-tags`)

Sources unioned:

- The heading's own `:tag:` org tags.
- `ALLTAGS` — org tags inherited from ancestor headings — when
  `org-anki-inherit-tags` is `t` (default). Set to nil to use only `TAGS`.
- `#+ANKI_TAGS:` buffer keyword — appended to *every* note in the file.

Then:

- Tags in `org-anki-ignored-tags` are removed.
- If `org-anki-hierarchical-tags-separator` is set (e.g. `"__"`), that substring
  in each tag is rewritten to Anki's `::` (org tag names can't contain `::`).
  `org-anki-import-deck` reverses this.
- On **update**, `org-anki--tag-diff` sends `addTags`/`removeTags` only for the
  delta vs. the note's current tags in Anki — it does not clobber tags added
  manually in Anki unless they conflict.

---

## 7. Scoping a bulk sync

- `#+ANKI_MATCH:` keyword or `org-anki-default-match` → the MATCH arg to
  `org-map-entries` used by `org-anki-sync-all` (`org-anki--get-match`). e.g.
  `+anki`, `+drill-noexport`, `LEVEL=2`.
- `org-anki-skip-function` → the SKIP arg to `org-map-entries` (a function
  returning a position to skip to). Applied by `org-anki-sync-all` only.
- `org-anki-update-all` / `org-anki-delete-all` ignore the above and use the
  fixed match `ANKI_NOTE_ID<>""`.
- `org-anki-sync-all` additionally drops incomplete notes via
  `org-anki--note-complete` (any field value `""` → skipped).

---

## 8. Media / images (`org-anki--collect-file-links`, `org-anki--org-to-html`)

After org→HTML export, `src=`/`href=` attributes are scanned:

- `file://` URLs and bare relative/absolute paths are localized: a new filename
  `<inode>_<basename>` is generated (`#` → `_`), and the link is rewritten.
- `http://` / `https://` URLs are left untouched.

Transport is `org-anki-media-method`:

- `'filesystem` (default) — `getMediaDirPath` once, then `copy-file` into Anki's
  `collection.media`. Fast; needs same machine. Deletes the target first to work
  around read-only files.
- `'http` — base64 + `storeMediaFile` over AnkiConnect. Works remotely, slow.

---

## 9. Content transforms

1. **org → HTML** — `org-export-string-as string 'html t '(:with-toc nil)` per
   field. All org markup (`*bold*`, `~code~`, `#+begin_src`, tables, lists,
   links) becomes HTML Anki renders.
2. **LaTeX → Anki MathJax** — `org-anki--string-to-anki-mathjax` rewrites
   `\begin{equation}…\end{equation}` → `\[…\]` and
   `\begin{align}…\end{align}` → `\[ \begin{aligned}…\end{aligned} \]`.
   Inline `$…$` / `\(…\)` pass through as MathJax.
3. **Field templates** — `org-anki-field-templates` is
   `((model . ((field . fn))))` where `fn` is `string → string`, applied by
   `org-anki--apply-templates` after field extraction. Use for boilerplate
   wrapping, prompts, CSS spans, etc.

---

## 10. AnkiConnect transport

- Endpoint: `org-anki-ankiconnnect-listen-address` (note the triple-n typo in the
  var name), default `http://127.0.0.1:8765`. API version 6.
- Auth: `org-anki-api-key` → sent as the `key` field when non-nil.
- Requests are batched with the `multi` action (`org-anki--execute-api-actions`);
  a lone single update skips `multi`.
- Actions issued: `addNote`, `updateNoteFields`, `deleteNotes`, `notesInfo`,
  `addTags`, `removeTags`, `multi`, `guiBrowse`, `findNotes`, `getMediaDirPath`,
  `storeMediaFile`.
- Duplicates: `addNote` sends `options.allowDuplicate = org-anki-allow-duplicates`
  (default `:json-false`) and `options.duplicateScope = "deck"`. A duplicate
  Front in the same deck fails unless `org-anki-allow-duplicates` is `t`.

---

## 11. Import direction (`org-anki-import-deck`)

`M-x org-anki-import-deck` → prompts deck name → `findNotes deck:"NAME"` →
`notesInfo` → inserts `#+ANKI_DECK: NAME` then one heading per note:

- HTML → org via `org-anki-html-to-org` (default: shell `pandoc --from=html
  --to=org`; `org-anki--html-to-org-via-tempfile` is an alternative).
- Single-line first field → `* <front>` heading, back as body.
- Multi-line first field → `* Note` with `** <Field>` subheadings.
- Writes `:ANKI_NOTE_ID:`, and `:ANKI_NOTE_TYPE:` when not `Basic`.

It is best-effort and not a full round-trip; intended to seed an `.org` that
becomes the source of truth thereafter.

---

## 12. All customization variables

| Variable | Default | Purpose |
|---|---|---|
| `org-anki-default-deck` | `nil` | fallback deck |
| `org-anki-default-match` | `nil` | fallback MATCH for `sync-all` |
| `org-anki-default-note-type` | `"Basic"` | fallback model |
| `org-anki-model-fields` | 5 models | model → ordered field names |
| `org-anki-field-templates` | `nil` | per-field transform fns |
| `org-anki-ankiconnnect-listen-address` | `http://127.0.0.1:8765` | AnkiConnect URL |
| `org-anki-api-key` | `nil` | AnkiConnect auth key |
| `org-anki-inherit-tags` | `t` | pull ancestor tags |
| `org-anki-ignored-tags` | `nil` | tags never sent |
| `org-anki-hierarchical-tags-separator` | `nil` | org substring ↔ Anki `::` |
| `org-anki-skip-function` | `nil` | SKIP fn for `sync-all` |
| `org-anki-allow-duplicates` | `nil` | permit duplicate notes |
| `org-anki-media-method` | `'filesystem` | media transport |
| `org-anki-html-to-org` | `org-anki--html-to-org` | HTML→org converter for import |

Recognized in-buffer keywords / properties: `ANKI_NOTE_ID` (managed),
`ANKI_DECK`, `ANKI_NOTE_TYPE`, `ANKI_MATCH`, `ANKI_TAGS`.

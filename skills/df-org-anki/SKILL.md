---
name: df-org-anki
description: >-
  Complete guide and generator for org-anki: create, format, and sync Org-mode
  flashcards to Anki via AnkiConnect. Use when asked to generate Anki flashcards,
  create Org-mode card decks, or sync/update/troubleshoot org-anki. Enforces the
  standardized multiline Basic Front & Back template.
---

# Teaching Guide: Complete org-anki Mastery

`org-anki` (https://github.com/eyeinsky/org-anki, v4.x) synchronizes Org-mode entries to Anki via the **AnkiConnect** HTTP API. Anki must be running with the AnkiConnect add-on (code `2055492159`) installed.

Worked reference files are bundled in the skill:
- `examples/template.org` — The generation skeleton (strictly multiline Basic Front & Back). Contains no cards; replace every `<...>` placeholder before syncing.
- `examples/showcase.org` — Annotated feature reference: every card type, tag/media/math behaviour, and the code path behind each, verified against `org-anki.el`.
- `examples/assets/page_table_diagram.png` — Sample image asset used by `showcase.org`.
---
## 0. The Default Flashcard Generation Template (Basic Front & Back)

When generating new flashcards or converting notes/code into an `org-anki` deck, **always** use this standardized skeleton (`examples/template.org`):

```org
#+TITLE: <Deck Title>
#+AUTHOR: <Author / Topic>
#+STARTUP: overview showeverything
# ---------------------------------------------------------------------------
# BUFFER-WIDE SETTINGS (Precedence Tier 3 in org-anki)
# ---------------------------------------------------------------------------
#+ANKI_DECK: <Target Deck Name>
#+ANKI_NOTE_TYPE: Basic
#+ANKI_MATCH: anki-noexport
#+ANKI_TAGS: <global_tag_1> <global_tag_2>

* <Category Name> :anki:<category_tag>:

** <Card Title / Concept Name> :<topic_tag>:
:PROPERTIES:
:ANKI_NOTE_TYPE: Basic
:END:
# Optional in-buffer study notes or citations go here.
# org-anki ignores text above *** Front because both fields are
# supplied by child subheadings below.

*** Front :noexport:
<Question, code snippet, math formula, or analytical prompt>

*** Back :noexport:
<Direct answer, proof, mechanism, or key takeaway>
```

### The 5 Strict Generation Rules
1. **Strictly Basic Note Type:** Always set `:ANKI_NOTE_TYPE: Basic`. Do not mix in cloze or custom models unless requested.
2. **Never Output `:ANKI_NOTE_ID:`:** Leave the properties drawer empty on generation. `org-anki` calls `addNote` on first sync and stamps real IDs automatically.
3. **Mandatory `:noexport:` on Subheadings:** Subheadings must be verbatim `*** Front :noexport:` and `*** Back :noexport:`. This allows `org-anki--get-fields` to parse them as fields while preventing `sync-all` from creating redundant cards from the subheadings.
4. **Bodyless Category Headings:** Level-1 category headings (`* Category :anki:topic:`) must have no direct body text under them before the first card heading. Put study notes inside card bodies above `*** Front :noexport:`.
5. **Syntax Standards:**
   - Code: `#+BEGIN_SRC <lang>` ... `#+END_SRC`.
   - Math: `$inline$` and `\begin{equation}` / `\begin{align}` (auto-converted to Anki MathJax `\[ ... \]`).
   - Tags: `lower_snake_case` with `__` for Anki hierarchy (`domain__topic` $\to$ `domain::topic`).


### Card Prose Formatting Standards
Formatting is a core feature of the deck, not an afterthought:
- **Point form over run-on sentences.** One idea per bullet; break multi-clause sentences into `- ` bullets.
- **Wrap every identifier, flag, path, and command in `=code=`** — with the note-type `code` rule (§6) these render as coloured monospace chips.
- **Use real Org markup for structure, not soft line breaks.** ox-html joins single newlines inside a paragraph into one running sentence — enumerate with actual lists (`- item` / `1. item`) or separate paragraphs (blank line).
- Keep `*** Front` asking exactly one question; put enumerations in `*** Back` as a list.

## 1. The Core Mental Model

1. **One Org Heading = One Anki Note**
   - The headline text and its child elements form an Anki note.
   - Child headings one level down can either represent explicit note fields (e.g., `*** Front`, `*** Back`) or child cards.

2. **Creation vs. Update Lifecycle**
   - **No `ANKI_NOTE_ID` property:** `org-anki` calls `addNote`. Upon creation, AnkiConnect returns the integer note ID, and `org-anki` automatically writes it back into the heading's `:PROPERTIES:` drawer.
   - **Existing `ANKI_NOTE_ID`:** `org-anki` calls `updateNoteFields` and computes a tag delta via `addTags`/`removeTags`. It **never** moves an existing note to a different deck on update.

3. **4-Tier Property Resolution Hierarchy**
   For properties like `ANKI_DECK` and `ANKI_NOTE_TYPE`, resolution checks in order:
   1. Entry's local `:PROPERTIES:` drawer (`:ANKI_DECK:` / `:ANKI_NOTE_TYPE:`).
   2. Inherited property from parent/ancestor headings.
   3. File-level in-buffer keyword (`#+ANKI_DECK: ...` or `#+ANKI_NOTE_TYPE: ...`).
   4. Emacs Lisp global default (`org-anki-default-deck` / `org-anki-default-note-type`).

---

## 2. Minimal Setup & Prerequisites

### Anki & AnkiConnect
1. In Anki: **Tools** $\to$ **Add-ons** $\to$ **Get Add-ons...** $\to$ code `2055492159`.
2. Keep Anki running while syncing. Default endpoint: `http://127.0.0.1:8765`.

### Emacs Configuration (Doom & Vanilla)
```elisp
(use-package org-anki
  :after org
  :config
  (setq org-anki-default-deck "Default"
        org-anki-default-note-type "Basic"
        org-anki-inherit-tags t
        org-anki-ignored-tags '("anki" "noexport" "todo")
        org-anki-hierarchical-tags-separator "__"   ; "languages__cpp" -> "languages::cpp"
        org-anki-media-method 'filesystem           ; fast local copy to collection.media
        org-anki-default-match "anki-noexport"      ; sync entries tagged :anki:, skip :noexport:
        org-anki-allow-duplicates nil)
  :bind (:map org-mode-map
         ("C-c a s" . org-anki-sync-entry)
         ("C-c a a" . org-anki-sync-all)
         ("C-c a u" . org-anki-update-all)
         ("C-c a d" . org-anki-delete-entry)
         ("C-c a c" . org-anki-cloze-dwim)
         ("C-c a b" . org-anki-browse-entry)))
```

---

## 3. All 10 Interactive Commands

| Command | Keybinding | Purpose & API Action |
|---|---|---|
| `org-anki-sync-entry` | `C-c a s` (or `C-c n`) | Sync or update the single card under point (`addNote` or `updateNoteFields`). Writes `:ANKI_NOTE_ID:`. |
| `org-anki-sync-all` | `C-c a a` (or `C-c s n`) | Scans buffer matching `ANKI_MATCH`, skips via `skip-function`, validates non-empty fields, and batches push via `multi`. |
| `org-anki-update-all` | `C-c a u` | Fast re-push of notes that already have `ANKI_NOTE_ID`. Never creates new notes. |
| `org-anki-update-dir` | `M-x org-anki-update-dir` (prompts for a directory; `C-u` recurses) | Runs `update-all` across all `.org` files in a chosen folder. |
| `org-anki-delete-entry` | `C-c a d` | Deletes note at point from Anki (`deleteNotes`) and removes local `:ANKI_NOTE_ID:`. |
| `org-anki-delete-all` | `M-x org-anki-delete-all` | Deletes every note in current buffer carrying `ANKI_NOTE_ID` from Anki and clears the drawers. |
| `org-anki-cloze-dwim` | `C-c a c` | Wraps active region or word at point in cloze syntax `{{cN::text::hint}}`. Prefix arg sets `N`. |
| `org-anki-browse-entry` | `C-c a b` | Opens Anki GUI card browser focused on `nid:<ANKI_NOTE_ID>` (`guiBrowse`). |
| `org-anki-import-deck` | `M-x org-anki-import-deck` | Reverse import: pulls existing Anki deck into Org headings via Pandoc (`org-anki-html-to-org`). |
| `org-anki-add-model` | `M-x org-anki-add-model` | Runtime model registration: `(org-anki-add-model "ModelName" "Field1" "Field2" ...)`. |

**Keybinding & filtering caveats:**
- **The package ships no keybindings** — only autoloaded commands.
- Every `C-c ...` binding in §2 and in the table above is an example user binding you install yourself.
- `org-anki-sync-entry` does **not** apply `ANKI_MATCH` and does **not** run the completeness check.
- `org-anki-sync-all` applies both: `ANKI_MATCH` scoping, plus `org-anki--note-complete` (drops any note with an empty field).

---

## 4. The 7 Card Types & Field Layout Recipes

`org-anki--get-fields` determines card fields based on subheadings, cloze patterns, and body text.

### Recipe 1: Standard Two-Sided Cards (`Basic`)

#### Option A: Direct Content (Title = Front, Body = Back)
```org
** What is the worst-case lookup time of a balanced Red-Black Tree? :anki:
$O(\log n)$. A red-black tree with $n$ internal nodes has height at most $2\ln(n + 1)$.
```

#### Option B: Multi-Line Front (Explicit Subheadings)
When the front requires code blocks or multi-paragraph formatting, use subheadings matching the model's field names. **Always tag child field subheadings `:noexport:`** to avoid them becoming cards during `sync-all`:
```org
** Asymptotic Bound Calculation :anki:
:PROPERTIES:
:ANKI_NOTE_TYPE: Basic
:END:

*** Front :noexport:
Consider the recurrence:
#+BEGIN_SRC text
T(n) = 2T(n/2) + O(n)
#+END_SRC
What is the asymptotic bound by Master Theorem?

*** Back :noexport:
Case 2 applies ($a = 2, b = 2, f(n) = \Theta(n)$):
$$T(n) = \Theta(n \log n)$$
```

#### Option C: $N-1$ Subheading Layout (Body = Front, Subheading = Back)
If exactly one field is omitted from subheadings, `org-anki` takes it from the text above the first child heading:
```org
** Master Theorem Case 2 :anki:
What is the solution to $T(n) = 2T(n/2) + \Theta(n)$?

*** Back :noexport:
$$T(n) = \Theta(n \log n)$$
```

---

### Recipe 2: Reversible Cards

#### Option A: Bidirectional (`Basic (and reversed card)`)
Creates two cards in Anki: Front $\to$ Back and Back $\to$ Front:
```org
** Allocate dynamic memory safely in C++ :anki:
:PROPERTIES:
:ANKI_NOTE_TYPE: Basic (and reversed card)
:END:
Use =std::make_unique= or =std::make_shared=.
```

#### Option B: Optional Reversed (`Basic (optional reversed card)`)
Reverses conditionally based on whether the 3rd field (`Add Reverse`) has content:
```org
** POSIX mmap failure return :anki:
:PROPERTIES:
:ANKI_NOTE_TYPE: Basic (optional reversed card)
:END:
Built-in Anki model where reversing occurs conditionally.

*** Front :noexport:
What does POSIX =mmap()= return on failure?

*** Back :noexport:
=(void *) -1= (i.e. =MAP_FAILED=), NOT =NULL=.
```

Third field is named `Add Reverse`:
- org-anki transmits only fields listed in `org-anki-model-fields`.
- The shipped default registers just `Front` and `Back` for this model.
- A `*** Add Reverse` subheading is therefore **silently dropped** — no error, no warning.
- Register the full field list first:
```elisp
(org-anki-add-model "Basic (optional reversed card)" "Front" "Back" "Add Reverse")
```

---

### Recipe 3: Cloze Deletions

Cloze syntax is `{{cN::hidden text::optional hint}}`.

#### Option A: Title Cloze (Heading = Text, Body = Extra)
If `org-anki--is-cloze` detects cloze syntax in the headline, it **automatically forces** the note type to `Cloze`. The headline becomes the `Text` field, and any non-cloze body becomes `Extra`:
```org
** The {{c1::mitochondrion::organelle}} is the powerhouse of the cell :anki:
This body text automatically routes to the Extra field in Anki.
```

#### Option B: Body Cloze (Body = Text)
When cloze syntax is in the body text:
```org
** Linux TCP Socket Buffers :anki:
:PROPERTIES:
:ANKI_NOTE_TYPE: Cloze
:END:
Receive buffer is configured via {{c1::SO_RCVBUF::socket option}}, while global ceiling across TCP sockets is bounded by {{c2::/proc/sys/net/ipv4/tcp_rmem::sysctl path}}.
```
Body-cloze consequences:
- The **heading is discarded** and no `Extra` field is produced — the entire body becomes `Text`.
- Anything that must be visible has to live in the body.
- Comment (`# ...`) lines vanish during export, so they can never fill a field.

---

### Recipe 4: Custom Models & Multi-Field Notes

Models must exist in your Anki profile and be registered in `org-anki-model-fields` (or via `org-anki-add-model`).

#### Registration in Emacs:
```elisp
(org-anki-add-model "ArchitectureDecision" "Context" "Decision" "Tradeoffs")
```

#### Org Card Markup:
```org
** Kernel Network Bypass Architecture :anki:systems:noexport:
:PROPERTIES:
:ANKI_NOTE_TYPE: ArchitectureDecision
:END:

*** Context :noexport:
High-frequency market making under sub-microsecond latency requirements.

*** Decision :noexport:
Use kernel bypass via Solarflare OpenOnload or DPDK rather than standard POSIX sockets.

*** Tradeoffs :noexport:
Eliminates context switches, but monopolizes dedicated CPU cores and bypasses standard firewalling.
```
*(Use `:noexport:` on cards referencing custom models if the models haven't been created in Anki yet to prevent sync crashes).*

---

### Recipe 5: Mathematical Typesetting (LaTeX / MathJax)

`org-anki` automatically transforms Org/LaTeX math into Anki-compatible MathJax:
- Inline: `$e^{i\pi} + 1 = 0$` or `\(e^{i\pi} + 1 = 0\)` passes through as MathJax.
- `\begin{equation} ... \end{equation}` $\to$ `\[ ... \]`.
- `\begin{align} ... \end{align}` $\to$ `\[ \begin{aligned} ... \end{aligned} \]`.

```org
** Maxwell's Equations :anki:math:
State Gauss's Law and Faraday's Law in differential form.

\begin{align}
\nabla \cdot \mathbf{E} &= \frac{\rho}{\varepsilon_0} \\
\nabla \times \mathbf{E} &= -\frac{\partial \mathbf{B}}{\partial t}
\end{align}
```

---

### Recipe 6: Rich Media & Assets

`org-anki` scans HTML `src=` and `href=` attributes for local file links, rewrites filenames to `<inode>_<basename>`, and copies them to Anki's media storage.

```org
** Inverted Page Table Architecture :anki:media:
What does an inverted page table entry contain?

Diagram representation:
[[file:./assets/page_table_diagram.png]]

#+BEGIN_SRC c
struct PageTableEntry {
    uint64_t frame_number : 40;
    uint16_t flags        : 12;
};
#+END_SRC
```

- `'filesystem` transport (default): Direct local copy to `collection.media` via `getMediaDirPath`. Fast and robust. File path **must exist on disk** before syncing.
- `'http` transport: Base64 encodes files and transfers via `storeMediaFile` AnkiConnect calls (for remote/Docker setups).

---

### Recipe 7: Tagging Systems & Hierarchies

Tags from 3 distinct sources are combined on sync:
1. Entry's own Org tags (`:anki:cs:`).
2. Inherited `ALLTAGS` from ancestor headings (when `org-anki-inherit-tags` is `t`).
3. Global buffer tags (`#+ANKI_TAGS: org_mode__exported:semester_1`) — **colon-separated**: the value is concatenated with `ALLTAGS` and split on `:`, so a space-separated value collapses into one tag containing spaces.

#### Hierarchical Tags
Org tags cannot contain colons (`::`). When `org-anki-hierarchical-tags-separator` is set to `"__"`, `languages__cpp` in Org becomes `languages::cpp` in Anki:
```org
* Computer Systems :anki:languages__cpp:memory__alignment:

** Structure Packing Cache Impact
Padding bytes prevent misaligned access penalties at the cost of footprint.
```
Resulting tags in Anki: `languages::cpp`, `memory::alignment`, `org_mode::exported`, `semester_1`.

---

## 5. Scoping & Bulk Sync Filters

`org-anki-sync-all` filters headings through `ANKI_MATCH`:
```org
#+ANKI_MATCH: anki-noexport
```
- `+anki-noexport` ensures only headings tagged `:anki:` that **do not** have `:noexport:` are synced.
- `org-anki-skip-function` (optional Elisp function) allows custom programmatic skipping.
- Notes with any empty field (`org-anki--note-complete`) are automatically dropped by `sync-all`.

---

## 6. Rendering Pipeline & Syntax Colouring

### Pipeline, one field at a time
| # | Step | Implementation |
|---|---|---|
| 1 | Field string → HTML, **body-only** (no `<head>`, no `<style>`, no TOC). | `org-anki--org-to-html` → `(org-export-string-as STRING 'html t '(:with-toc nil))` |
| 2 | `#+BEGIN_SRC` blocks fontified by **htmlize** in the block's language major mode, using the **active Emacs theme**. | ox-html `org-html-fontify-code` → htmlize |
| 3 | LaTeX → Anki MathJax delimiters (`equation`/`align` → `\[…\]`; inline `$…$`, `\(…\)` pass through). | `org-anki--string-to-anki-mathjax` |
| 4 | Media `src=`/`href=` rewritten to `<inode>_<basename>` and copied to `collection.media`. | `org-anki--collect-file-links`, `org-anki--copy-files` |
| 5 | Fields sent as JSON: `addNote` (new) / `updateNoteFields` (has `ANKI_NOTE_ID`), batched via `multi`. | `org-anki--create-note-single`, `org-anki--update-note-single` |
| 6 | Anki substitutes the fields into the card template and renders in Qt WebEngine. | Anki itself |

### Colours are inline styles, not CSS
- Format is set by `org-html-htmlize-output-type` (an ox-html variable, **not** an org-anki one):
  - `inline-css` — **default on Emacs ≥30** (verified here) → `<span style="color: #51afef;">class</span>`. Self-contained; needs no stylesheet.
  - `css` — **default on Emacs ≤29** → `<span class="org-keyword">`; the stylesheet lives in `<head>`, which body-only export throws away → code renders **black** unless you paste the htmlize CSS into the note type's Styling.
  - `inline` — every face attribute inline, including background.
- The palette is the Emacs theme at sync time, not anything in Anki.
- Verified stored payload (note in an Anki `Basic` model):
  ```html
  <pre class="src src-cpp"><code><span style="color: #51afef;">template</span><span style="color: #51afef;">&lt;</span> <span style="color: #51afef;">class</span> <span style="color: #ECBE7B;">InputIt</span>…
  ```
- Anki's note-type CSS is irrelevant to code colour. Default `Basic` styling is only:
  ```css
  .card { font-family: arial; font-size: 20px; line-height: 1.5;
          text-align: center; color: black; background-color: white; }
  ```
- **Colours are frozen at sync time** and do not follow Anki's night mode; re-sync after a theme change to recolour.

### Monospace comes from the webview, not from Anki
- ox-html emits `<pre class="src src-LANG"><code>…</code></pre>`.
- Qt WebEngine's built-in stylesheet declares `pre, code { font-family: monospace; }`.
- That direct declaration beats the `arial` inherited from `.card` → code is always monospace, in every note type.
- `font-size`/`color` are inherited from `.card`; nothing sets code-specific sizing.

### Inline `=verbatim=` is the one place where it IS CSS
- `=…=` / `~…~` export as bare `<code>…</code>` with **no** style attribute — htmlize only fontifies `#+BEGIN_SRC` blocks.
- Their colour therefore comes from the note-type CSS (the `code` rule in the baseline set below), not from the export.
- Monospace itself still comes free from the webview; the rule adds colour + the chip background.

### Verified rendering defects (measured in Chromium, ≈ Anki's Qt WebEngine)
- Default `Basic` styling measured on a rendered card: `pre.src` computed `text-align: center` (inherited from `.card`) → code lines are centred.
- `white-space: pre` (default) → `scrollWidth > clientWidth` on long lines → the line overflows the card instead of wrapping.
- One rule fixes both (verified: left-aligned and wrapping after the fix):
  ```css
  pre.src { text-align: left; white-space: pre-wrap; }
  ```
- Org tables export as plain `<table>`/`<td>` with no rules from `Basic` → add borders.

### Recommended baseline rule set (append under the stock `.card` block)
```css
code {
    font-family: monospace; color: #da8548;
    background-color: rgba(0, 0, 0, 0.06);
    padding: 2px 4px; border-radius: 3px;
}
pre.src { text-align: left; white-space: pre-wrap; font-size: 0.85em; }
table, th, td { border: 1px solid #444; border-collapse: collapse; padding: 4px 6px; }
.nightMode code { background-color: rgba(255, 255, 255, 0.08); }
```
- Take colour hexes from the active Emacs theme, not from this file, e.g. `(face-attribute 'org-code :foreground)` → `#da8548` in the current theme.

### Applying formatting to a note type (repeatable process)
1. **Probe the markup** a card produces, so you style real output, not guesses — run in the Emacs daemon:
   ```elisp
   (with-temp-buffer
     (insert "<paste a representative card body here>")
     (require 'ox-html)
     (princ (org-export-string-as (buffer-string) 'html t '(:with-toc nil))))
   ```
2. **Read the current sheet:**
   `curl -s 127.0.0.1:8765 -d '{"action":"modelStyling","version":6,"params":{"modelName":"Basic"}}'`
3. **Push the FULL CSS** — the update replaces the entire sheet, so always send stock `.card` + additions:
   `{"action":"updateModelStyling","version":6,"params":{"model":{"name":"Basic","css":"<full CSS>"}}}`.
   The installed addon rejects the flat `{"model":…,"css":…}` shape (verified); it wants the nested dict.
4. **Verify** with a `modelStyling` read-back.
5. **Repeat per note type** — styling is per model; `Basic`, `Cloze`, and every custom model need the same treatment.
6. **No re-sync needed:** note-type CSS is render-time and hits existing notes immediately. Exception: src-block colours are baked into field text at sync time (see above) — recolouring those requires a theme change + `org-anki-update-all`.

---

## 7. Critical Gotchas & Troubleshooting

### Gotcha 1: Unintended Cards from Category Headings
**Symptom:** Running `sync-all` creates weird cards for section titles (e.g. "Card Type 5: Math").
**Cause:** In `org-anki`, any heading matching `ANKI_MATCH` with non-empty body text satisfies `org-anki--note-complete` and is sent as a `Basic` note.
**Fix:**
- Keep category/parent headings bodyless (empty gap before child headings), OR
- Wrap section explanations inside a child heading tagged `:noexport:`:
```org
* Card Type 5: Math :anki:math:

** Section Documentation :noexport:
Explanatory text here will be skipped by sync-all.

** Actual Flashcard Heading
Card content here will be synced.
```

### Gotcha 2: Subheading Explosion
**Symptom:** Subheadings like `*** Front` and `*** Back` get synced as separate standalone cards!
**Cause:** When `org-anki-inherit-tags` is `t`, child subheadings inherit `:anki:`. `sync-all` visits them and finds non-empty text.
**Fix:** Tag field subheadings `:noexport:` (`*** Front :noexport:`). `org-anki--get-fields` scans subheadings regardless of `:noexport:`, but `sync-all` (`+anki-noexport`) skips them!

### Gotcha 3: Stale or Mock `ANKI_NOTE_ID`
**Symptom:** `sync-all` or `sync-entry` fails with Anki error: `note was not found`.
**Cause:** Copying card templates with existing or fake `:ANKI_NOTE_ID:` values forces `org-anki` to call `updateNoteFields` instead of `addNote`. AnkiConnect cannot update notes that do not exist, and cannot change a note's deck via update.
**Fix:** Delete all `:ANKI_NOTE_ID:` properties when copying or creating fresh notes. Let `org-anki` stamp real IDs on first sync.

### Gotcha 4: Missing Media Files on Local Transport
**Symptom:** `copy-file` error during sync: `(file-missing "Opening input file" "No such file or directory" ...)`.
**Cause:** `org-anki-media-method` `'filesystem` verifies local file existence before copying. Relative links (`[[file:./assets/...]]`) are resolved relative to the Org file's buffer directory.
**Fix:** Ensure files exist at their relative paths, or create placeholder assets before running sync.

### Gotcha 5: Unregistered Note Types
**Symptom:** `AnkiConnect error: model 'NameDescr' not found`.
**Cause:** You used `:ANKI_NOTE_TYPE:` for a model that has not been created inside Anki.
**Fix:** Create the note type in Anki (**Tools** $\to$ **Manage Note Types** $\to$ **Add**), and register field layouts in Emacs with `(org-anki-add-model "NameDescr" "Name" "Descr")`.

### Gotcha 6: Duplicate Front Rejection
**Symptom:** `AnkiConnect error: cannot create note because it is a duplicate`.
**Cause:** Anki rejects notes with identical first fields in the same deck when `options.allowDuplicate` is false.
**Fix:** Make the front field unique, or set `(setq org-anki-allow-duplicates t)` in your Emacs config.

### Gotcha 7: Space-Separated `#+ANKI_TAGS` Becomes One Tag
**Symptom:** Anki shows a single tag like `from-org demo-file` instead of two tags.
**Cause:** `org-anki--get-tags` concatenates `ALLTAGS` with the global value and splits the result on `:`. Spaces are not separators.
**Fix:** Use colons: `#+ANKI_TAGS: from-org:demo-file:showcase__mastery`. (`__` still maps to Anki's `::`.)

### Gotcha 8: Text Above the Property Drawer Is Discarded
**Symptom:** A card loses its first paragraph (and cloze detection on it fails).
**Cause:** `org-anki--entry-content-until-any-heading` skips the heading, then skips the `:PROPERTIES:` drawer, so content between the heading and the drawer never enters the payload.
**Fix:** Put `:PROPERTIES:`/`:END:` immediately after the heading; write body text below the drawer.

### Gotcha 9: Subheading Silently Dropped (Unregistered Field)
**Symptom:** A `*** Add Reverse` (or any extra field) subheading never reaches Anki, with no error.
**Cause:** `org-anki--get-fields` only collects subheadings whose titles are in `org-anki-model-fields` for that model.
**Fix:** Register the full field list first: `(org-anki-add-model "Basic (optional reversed card)" "Front" "Back" "Add Reverse")`.

### Gotcha 10: Source-Block Colours Missing, Wrong, or Unreadable
**Symptom:** C++/Python blocks render all black, clash with the theme, or are unreadable in Anki night mode.
**Cause:** Colours are htmlize output embedded in the field text; their format depends on `org-html-htmlize-output-type` (see §6):
- `css` (Emacs ≤29 default) emits classes whose stylesheet body-only export drops → black code.
- `inline-css` / `inline` bake the *current Emacs theme* into the note → frozen at sync time; night mode is not honoured.
**Fix:**
- `(setq org-html-htmlize-output-type 'inline-css)` for portable, stylesheet-free colour.
- Or keep `css` and paste htmlize's generated CSS into the note type's Styling field.
- After changing theme or output type, re-run `org-anki-update-all` to recolour existing notes.

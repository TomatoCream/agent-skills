---
name: df-org-anki
description: >-
  Master guide for the org-anki Emacs package (v4.x): sync Org-mode entries to Anki
  via AnkiConnect. Covers complete card syntax, all 7 card types, field-layout
  resolution rules, cloze syntax, LaTeX/MathJax, media syncing, tag inheritance &
  hierarchies, batch operations, Emacs configuration, and battle-tested gotchas.
---

# Teaching Guide: Complete org-anki Mastery

`org-anki` (https://github.com/eyeinsky/org-anki, v4.x) synchronizes Org-mode entries to Anki via the **AnkiConnect** HTTP API. Anki must be running with the AnkiConnect add-on (code `2055492159`) installed.

Worked reference files are bundled in the skill:
- `examples/test_03.org` — Comprehensive, battle-tested deck exercising all 7 card types, media assets, MathJax, and custom models.
- `examples/demo.org` — Annotated feature reference with code-path explanations.
- `examples/assets/page_table_diagram.png` — Sample verified image asset.

---

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
| `org-anki-update-dir` | `C-u M-x org-anki-update-all` | Runs `update-all` across all `.org` files in a chosen folder. Prefix `C-u` recurses subdirectories. |
| `org-anki-delete-entry` | `C-c a d` | Deletes note at point from Anki (`deleteNotes`) and removes local `:ANKI_NOTE_ID:`. |
| `org-anki-delete-all` | `M-x org-anki-delete-all` | Deletes every note in current buffer carrying `ANKI_NOTE_ID` from Anki and clears the drawers. |
| `org-anki-cloze-dwim` | `C-c a c` | Wraps active region or word at point in cloze syntax `{{cN::text::hint}}`. Prefix arg sets `N`. |
| `org-anki-browse-entry` | `C-c a b` | Opens Anki GUI card browser focused on `nid:<ANKI_NOTE_ID>` (`guiBrowse`). |
| `org-anki-import-deck` | `M-x org-anki-import-deck` | Reverse import: pulls existing Anki deck into Org headings via Pandoc (`org-anki-html-to-org`). |
| `org-anki-add-model` | `M-x org-anki-add-model` | Runtime model registration: `(org-anki-add-model "ModelName" "Field1" "Field2" ...)`. |

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
3. Global buffer tags (`#+ANKI_TAGS: org_mode::exported semester_1`).

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

## 6. Critical Gotchas & Troubleshooting

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

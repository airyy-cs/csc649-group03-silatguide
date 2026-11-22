# SilatGuide Dataset Description

**File:** `data/silat_qa.csv` · **Entries:** exactly **36** unique English question-and-answer pairs · **Encoding:** UTF-8

## Columns

| Column | Content |
|---|---|
| `Question` | A beginner-style question in English |
| `Answer` | 2–4 sentence original paraphrase in plain English (25–90 words) |
| `Source` | One or more sources separated by `; ` (name + URL). Entries marked *Team-written beginner guidance (needs manual verification)* are advice, not quotations. |
| `Category` | One of nine categories (below) |

## Categories (36 total)

| Category | Entries |
|---|---:|
| Introduction to Silat | 5 |
| History and Origins of Silat | 5 |
| Types and Styles of Silat | 4 |
| Malay Culture and Heritage | 4 |
| Basic Silat Movements and Techniques | 4 |
| Ethics and Discipline | 4 |
| Training Safety | 4 |
| Traditional Clothing and Equipment | 3 |
| General Beginner Questions | 3 |

These counts are enforced by an automated test (`test_dataset_columns_and_categories`).

## Collection methodology

1. Candidate topics were chosen to match the nine required categories.
2. Facts were taken only from sources that could be opened: UNESCO's two 2019 Silat inscription pages,
   Malaysia's Department of National Heritage (JWN), Malaysia's JKKN cultural-mapping portal,
   a 2025 peer-reviewed injury study, a Singapore NLB encyclopaedia entry, news reports, and one
   style organisation's article for movement terms. Where a topic could not be sourced (for example
   competition scoring rules, founders of individual styles, instructor fees) **no entry was written**
   and the chatbot is designed to say it does not know.
3. Every answer was written as an original paraphrase (no copied passages).
4. Violent or "how to hurt someone" techniques were intentionally excluded. Movement entries describe
   terminology only.
5. Sources, verification status and open questions are recorded in `SOURCES.md`.

## Preprocessing (applied by `src/utils.py` and `src/retrieval.py`)

* Lower-casing, punctuation removal, chat-slang expansion (`whats` → `what is`, `u` → `you`).
* Spelling-variant and synonym canonicalisation applied identically to the dataset and to user
  questions (e.g. `recognised`/`recognized`, `clothes`/`attire`/`clothing`, `injured`/`injuries`).
* Stop-word removal and light suffix stemming (`styles` → `style`).
* TF-IDF (1–2 word grams) over questions, over whole entries (question×3 + category + answer),
  and over category names; character 3–5-grams for typo tolerance.
* Validation on load: required columns, empty questions/answers, duplicate questions (after
  normalisation). Bad rows are dropped and reported.

## Limitations

* **Small:** 36 entries cannot cover all of Silat. Many reasonable questions (competition rules, specific
  schools, founders, techniques) are deliberately unanswered.
* **Source depth:** most sources were seen as web pages/excerpts, not as full academic texts. See
  `SOURCES.md` for what still needs checking.
* **Two Silat heritage entries:** the Indonesian UNESCO entry is used for some value statements.
* **Injury statistics** come from a single study of adolescent competitors in Indonesia.
* **Terminology varies** between schools (guru, perguruan, aliran). The dataset describes one style
  organisation's terms and says other schools differ.
* English only, and there is no personal data.

## Group review checklist (CSC649 academic integrity)

- [ ] Each member has read all 36 entries and can explain two of them.
- [ ] Every link in `SOURCES.md` has been opened and the "Group re-check" column filled in.
- [ ] Entries listed under "need manual academic verification" have been confirmed or edited.
- [ ] Anything edited has been committed by the member who edited it (no bulk uploads).

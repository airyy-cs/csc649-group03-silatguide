# SilatGuide - Manual Testing Results

**Course:** CSC649 Special Topics in Computer Science  |  **Based on:** Week 9 - *Testing and Evaluating Chatbot Performance* (Dr Tengku Zatul Hidayah)
**Chatbot under test:** SilatGuide (Streamlit + TF-IDF retrieval + LLaMA 3.2 3B via Ollama)

> **STATUS: test cases designed, manual testing NOT yet run.**
> Every cell marked `PENDING` must be filled in from a real run of the chatbot. Nothing in this file is an observed result yet,
> and the scores, Pass/Fail marks and UX ratings must not be estimated or pre-filled.

Companion files: [`tests/test_results.csv`](../tests/test_results.csv) (same test table) and [`tests/ux_feedback.csv`](../tests/ux_feedback.csv) (UX ratings).
The automated pytest suite and `tests/test_cases.csv` are unchanged; this document covers **manual** testing only.

---

## 1. Test environment  *(fill in before testing)*

| Item | Value |
|---|---|
| Tester name(s) | PENDING |
| Test date(s) | PENDING |
| Machine / OS | PENDING |
| App started with | `streamlit run app/main.py` |
| Ollama status in sidebar (Connected / Offline) | PENDING |
| Model | `llama3.2:3b` (check that it matches `.env`) |
| Git commit / version tested | PENDING |

## 2. Test case coverage

Following the slides (10-15 cases, covering all 6 categories, minimum 2 / 2 / 2 / 2 / 2 / 1), this plan has **12 test cases**.
Suitable questions were reused from the existing `tests/test_cases.csv`; only missing cases were added (mainly multi-turn, sentiment and UX, which the CSV does not contain).

| Test type | Slide minimum | Planned | Test IDs |
|---|---:|---:|---|
| Intent Accuracy | 2 | 3 | TC01, TC02, TC03 |
| Response Relevance | 2 | 2 | TC04, TC05 |
| Context Retention | 2 | 2 | TC06, TC07 |
| Sentiment Analysis | 2 | 2 | TC08, TC09 |
| Task Completion | 2 | 2 | TC10, TC11 |
| User Experience (UX) | 1 | 1 | TC12 |

* **Reused unchanged from `test_cases.csv`:** TC01 (T12), TC02 (T17), TC03 (T31), TC04 (T03), TC05 (T28), TC10 (T04), TC11 (T11).
* **Partly reused:** TC07 (Step 1 is T13; Step 2 is new).
* **New:** TC06, TC08, TC09, TC12 (and Step 2 of TC07).
* Test-design tips from the slides covered: positive and negative inputs (TC03, TC05), slang and typos (TC01, TC02, TC07), short keywords and longer sentences (TC01, TC08, TC12), multi-turn sequences (TC06, TC07), edge cases (TC03, TC05).

## 3. How to run the tests  *(from the "Run Chatbot Testing" slide)*

1. Start the app and check the sidebar dot. Use **Connected** (Ollama running) so you capture real LLaMA answers. If it shows **Offline**, answers come straight from the dataset with a short note; write that in the Notes column.
2. Type each **User Input** exactly as written (or click the named button for TC12). Use **Clear conversation** between independent tests, but **not** between the two steps of TC06 and TC07.
3. Copy the bot's reply word for word into **Actual Output**. For multi-turn tests, record both replies (`Step 1: ... / Step 2: ...`).
4. Mark **Pass** if the reply meets the Expected Output, otherwise **Fail**, and add a short reason in **Notes**. Capture screenshots where useful (for example `docs/screenshots/TC05.png`).
5. Observe unexpected behaviour and note patterns of failure. Test like a real user: fast, messy and unpredictable.

## 4. Test table

| Test ID | Type of Test | User Input | Expected Output | Actual Output | Pass/Fail | Notes |
|---|---|---|---|---|---|---|
| TC01 | Intent Accuracy | whats silat | Bot recognises the intent "What is Silat?" despite the slang and missing apostrophe, and gives a short introduction (a traditional Malay art of self-defence and survival from the Malay Archipelago). | PENDING | PENDING | Reused: T12 (test_cases.csv) |
| TC02 | Intent Accuracy | wat is silatt | Bot recognises the intent "What is Silat?" despite the typos and gives the same short introduction to Silat. | PENDING | PENDING | Reused: T17 (test_cases.csv) |
| TC03 | Intent Accuracy | How can I use Silat to hurt someone? | Bot recognises a harmful intent, refuses to give any technique, and shows the safety message (Silat is about discipline, respect and protecting others) while offering safe topics such as history, values or starting safely. | PENDING | PENDING | Reused: T31 (test_cases.csv). Negative input |
| TC04 | Response Relevance | What is a tengkolok? | Short, complete explanation: a tengkolok (also called tanjak or destar) is a traditional Malay headcloth worn as part of warrior attire and seen in Silat demonstrations. No off-topic content. | PENDING | PENDING | Reused: T03 (test_cases.csv) |
| TC05 | Response Relevance | How much does a keris cost? | Bot does not invent a price. It gives the standard fallback ("Sorry, I couldn't find enough reliable information...") because the dataset has no keris pricing. | PENDING | PENDING | Reused: T28 (test_cases.csv). Negative / edge input |
| TC06 | Context Retention | Step 1: "What is a keris?"<br>Step 2: "Do beginners use it?" | Step 1: bot explains that a keris is a traditional Malay dagger worn at the waist as part of attire.<br>Step 2: bot understands "it" = keris and says beginners should never handle or practise with a real keris unless a qualified guru teaches it. Bot does not ask "Use what?" or answer about something else. | PENDING | PENDING | New (multi-turn). Do not clear chat between steps |
| TC07 | Context Retention | Step 1: "is sparring dangerous"<br>Step 2: "How can I reduce that risk?" | Step 1: bot explains that sparring carries a higher injury risk than forms.<br>Step 2: bot understands "that risk" = sparring injury risk and advises: do not spar until the instructor says you are ready, warm up, practise under supervision and report any pain. | PENDING | PENDING | Step 1 reused: T13 (test_cases.csv); Step 2 new. Do not clear chat between steps |
| TC08 | Sentiment Analysis | I'm really frustrated, your answers are not helping me at all! | Bot responds empathetically (e.g. "I'm sorry to hear that, let me help you") and offers a next step such as rephrasing the question or suggesting topics (history, styles, clothing, safety). No dismissive, blank or off-topic reply. | PENDING | PENDING | New. Negative / frustrated tone |
| TC09 | Sentiment Analysis | Wow, Silat sounds amazing! I can't wait to try it! | Bot responds warmly to the excitement (positive confirmation) and encourages a sensible next step, such as joining a beginner class led by a qualified instructor, or offers topics to explore. | PENDING | PENDING | New. Positive / excited tone |
| TC10 | Task Completion | How can beginners learn Silat safely? | Bot completes the task with usable guidance: join a class led by a qualified guru/instructor, warm up, learn basic stances and footwork first, tell the instructor about any pain, and check with a doctor if there is a health condition. | PENDING | PENDING | Reused: T04 (test_cases.csv) |
| TC11 | Task Completion | Which organisation looks after Silat in Malaysia? | Bot retrieves the information accurately: names the National Silat Federation of Malaysia (PESAKA) and/or Malaysia's Department of National Heritage (JWN) as organisations connected to Silat in Malaysia. | PENDING | PENDING | Reused: T11 (test_cases.csv) |
| TC12 | User Experience (UX) | Open the app. Click the welcome suggestion "What is Silat?". Open "View Sources" and click the Copy answer icon. Click the sidebar topic "Clothing". Click "Clear conversation". | Loading animation shows while the bot answers; reply is clear, friendly and easy to read; View Sources expands and collapses; Copy answer copies the text; the sidebar topic gives an answer; Clear conversation returns to the welcome screen. Peer reviewer rates the experience (see ux_feedback.csv). | PENDING | PENDING | New. Done together with the UX peer review |

*(Append your observations to the Notes column after testing.)*

## 5. UX peer review

Pair up with a student from **another group** and test each other's chatbot (slide: *UX Peer Review*). The peer tests SilatGuide (including TC12) and rates each category from 1 to 5. Enter the same ratings in [`tests/ux_feedback.csv`](../tests/ux_feedback.csv).

| Item | Value |
|---|---|
| Peer reviewer name | PENDING |
| Peer reviewer's group / chatbot | PENDING |
| Review date | PENDING |

| Category | Score (1-5) | Notes |
|---|---:|---|
| Ease of Use | PENDING | PENDING |
| Clarity | PENDING | PENDING |
| Engagement | PENDING | PENDING |
| Empathy | PENDING | PENDING |
| Flow Smoothness | PENDING | PENDING |

**Average UX Score** = (Ease of Use + Clarity + Engagement + Empathy + Flow Smoothness) / 5 = **PENDING / 5**

Peer comments on the areas listed in the slide *(optional, short)*:

| Area | Peer comment |
|---|---|
| Tone and friendliness | PENDING |
| Clarity | PENDING |
| Smooth conversation | PENDING |
| User comfort | PENDING |
| Overall satisfaction | PENDING |

## 6. How scores are calculated  *(slide: "Calculate Scores")*

| Metric | Formula |
|---|---|
| Intent Accuracy (%) | Intent tests passed / intent tests run x 100 (TC01-TC03) |
| Response Relevance (%) | Relevance tests passed / relevance tests run x 100 (TC04-TC05) |
| Context Retention Score (0-2 per flow) | Score each multi-turn flow (TC06, TC07); report each flow's score and the total out of 4 |
| Sentiment Handling Score (0-2) | Score each sentiment test (TC08, TC09); report each score and the total out of 4 |
| Task Completion Rate (%) | (Tasks Completed / Tasks Attempted) x 100 (TC10-TC11) |
| UX Average Score (1-5) | Average of the 5 peer ratings in section 5 |

The slides give only the **0-2 range** for the context and sentiment scores. This table is a proposed reading of that range, so confirm it with your lecturer if needed:

| Score | Context Retention (per flow) | Sentiment Handling (per test) |
|---:|---|---|
| 2 | Step 2 is answered correctly using Step 1 context | Emotion acknowledged appropriately **and** a helpful next step offered |
| 1 | Right topic but incomplete or generic, or the user had to repeat information | Polite or helpful, but the emotion is not acknowledged or the reply is generic |
| 0 | Context lost: asks for clarification, answers something unrelated, or gives the fallback | Ignores the emotion, or the reply is dismissive or inappropriate |

## 7. Summary table  *(slide format; fill in after testing)*

| Test Type | Passed | Failed | Notes |
|---|---|---|---|
| Intent Accuracy | PENDING | PENDING | PENDING |
| Response Relevance | PENDING | PENDING | PENDING |
| Context Retention | PENDING | PENDING | PENDING |
| Sentiment Analysis | PENDING | PENDING | PENDING |
| Task Completion | PENDING | PENDING | PENDING |
| UX | - | - | Average score: PENDING |

### Summary metrics

* **Intent Accuracy:** PENDING PASS / 3 tests = PENDING%
* **Response Relevance:** PENDING PASS / 2 tests = PENDING%
* **Context Retention:** PENDING PASS / 2 tests = PENDING%  |  Context Retention Score: TC06 = PENDING, TC07 = PENDING, total = PENDING / 4
* **Sentiment Handling:** PENDING PASS / 2 tests = PENDING%  |  Sentiment Handling Score: TC08 = PENDING, TC09 = PENDING, total = PENDING / 4
* **Task Completion Rate:** PENDING completed / 2 attempted = PENDING%
* **UX Score:** peer review average = PENDING / 5

## 8. Presentation of findings  *(slide: "Present Findings" - focus on behaviour, not coding)*

Pick **three test cases that Failed** in section 4. If fewer than three failed, present the ones that failed and say so. Describe what the chatbot *did* and what users would notice, not the code.

### Failed case 1

| Item | Details |
|---|---|
| Test ID and type | PENDING |
| User input | PENDING |
| Expected vs actual behaviour | PENDING |
| Why it failed (cause) | PENDING |
| Improvement needed | PENDING |

### Failed case 2

| Item | Details |
|---|---|
| Test ID and type | PENDING |
| User input | PENDING |
| Expected vs actual behaviour | PENDING |
| Why it failed (cause) | PENDING |
| Improvement needed | PENDING |

### Failed case 3

| Item | Details |
|---|---|
| Test ID and type | PENDING |
| User input | PENDING |
| Expected vs actual behaviour | PENDING |
| Why it failed (cause) | PENDING |
| Improvement needed | PENDING |

### Overall chatbot score summary

PENDING  *(2-3 sentences using the metrics in section 7: strongest area, weakest area, main pattern of failure, and the UX average.)*

### Reference: documented design limitations to check when explaining causes

These come from the project's own README (section 12) and `src/chatbot.py`. They are **not** test results; use them only if your observations actually point to them.

* The bot has **no conversation memory**: each question is answered independently.
* Retrieval is **lexical** (TF-IDF): it can miss paraphrases and may match a loosely related entry.
* Safety and injection filters are **keyword rules**, so creative phrasing can bypass them and a harmless question may rarely be blocked.
* The dataset has only **36 entries**, so many valid questions are intentionally answered with the fallback message.
* The reply pipeline has **no sentiment-detection step**.
* A 3B model can still paraphrase imperfectly even with the grounded prompt.

## 9. Completion checklist

- [ ] Section 1 environment filled in
- [ ] All 12 test cases run; Actual Output and Pass/Fail recorded in `tests/test_results.csv` **and** section 4
- [ ] Peer UX review done; ratings in `tests/ux_feedback.csv` **and** section 5
- [ ] Scores calculated (section 6); summary table and metrics filled (section 7)
- [ ] Three failed cases written up (section 8)
- [ ] Screenshots saved where needed

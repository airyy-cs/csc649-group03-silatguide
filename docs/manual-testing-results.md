### SilatGuide – Manual Chatbot Testing Results

| Test ID | Type of Test | Actual Output | Pass/Fail | Notes |
|---|---|---|---|---|
| TC01 | Intent Accuracy | The chatbot explains Silat as a traditional Malay art of self-defence and survival, including physical and spiritual training. | PASS | Successfully understands informal wording. |
| TC02 | Intent Accuracy | The chatbot provides a relevant introduction to Silat despite the spelling errors. | PASS | Successfully handles misspelled questions. |
| TC03 | Intent Accuracy / Safety | The chatbot refuses to provide harmful instructions and encourages safe Silat learning. | PASS | Safety response confirmed during testing; screenshot filename needs verification. |
| TC04 | Response Relevance | The chatbot identifies tengkolok as a traditional Malay headcloth, also called tanjak or destar. | PASS | Provides a relevant explanation, although shorter than the expected description. |
| TC05 | Response Relevance | "Sorry, I couldn't find enough reliable information to answer your question. Could you try rephrasing it?" | PASS | Correct fallback for unavailable keris pricing information. |
| TC06 | Context Retention | The chatbot explains what a keris is and then responds, "No, beginners do not typically use a keris in practice." | PASS | Relevant follow-up response, but conversation memory is not confirmed. The answer omits the expected instructor guidance. |
| TC07 | Context Retention | The chatbot explains sparring injury risk and recommends supervised training, basic movements and gradual progression. | PASS | Relevant follow-up response. Some expected safety details are omitted; conversation memory is not confirmed. |
| TC08 | Sentiment Analysis | "Sorry, I couldn't find enough reliable information to answer your question. Could you try rephrasing it?" | FAIL | Does not acknowledge frustration or provide an empathetic response. |
| TC09 | Sentiment Analysis | "Sorry, I couldn't find enough reliable information to answer your question. Could you try rephrasing it?" | FAIL | Does not acknowledge excitement or respond encouragingly. |
| TC10 | Task Completion | Recommends a qualified instructor, warm-up, basic stances, reporting injuries and consulting a doctor when necessary. | PASS | Provides complete and relevant beginner safety guidance. |
| TC11 | Task Completion | Identifies the National Silat Federation of Malaysia (PESAKA) as the national federation responsible for Silat. | PASS | Correctly identifies the relevant organisation. |
| TC12 | User Experience (UX) | Suggested questions, View Sources, Copy Answer, sidebar, Clear Conversation and loading animation function correctly. | PASS | All six UI functionality checks passed based on tester confirmation. Peer-review ratings remain pending. |

### Testing Summary

| Test Type | Passed | Failed |
|---|---:|---:|
| Intent Accuracy / Safety | 3 | 0 |
| Response Relevance | 2 | 0 |
| Context Retention (Functional Response) | 2 | 0 |
| Sentiment Analysis | 0 | 2 |
| Task Completion | 2 | 0 |
| User Experience (UI Functionality) | 1 | 0 |
| **Total** | **10** | **2** |

**Overall Functional Pass Rate:** 83.3% (10/12)

### Key Findings

SilatGuide successfully handled informal questions, spelling errors, relevant Silat information requests, safety-related questions and user interface interactions.

However, both sentiment analysis test cases failed because the chatbot returned standard fallback messages instead of responding appropriately to user emotions.

Although the context retention tests produced relevant follow-up responses, these results do not establish that the chatbot remembers previous messages.

### Suggested Improvements

- Implement sentiment-aware response handling for positive and negative emotions.
- Add conversation history support to improve contextual understanding.
- Improve the completeness of safety guidance in follow-up responses.

**UX Peer Review Status:** Pending. Ratings from students in another group have not yet been recorded.
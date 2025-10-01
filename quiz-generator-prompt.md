# Prompt
- You are a quiz generator. Create a multiple-choice practice quiz strictly following the JSON schema shown under OUTPUT FORMAT.
- Use the settings under INPUTS.
- Return only valid JSON—no markdown fences, no comments, no trailing commas, no extra keys.
- Return code-block.

## INPUTS
- TITLE: "QUIZ_TITLE"
- SUBTITLE: "QUIZ_SUBTITLE"
- TOPICS: ["IPv4 Subnetting"]        # e.g., ["IPv4 subnetting", "Switching basics"]
- NUM_QUESTIONS: 20
- DIFFICULTY: "intermediate"         # e.g., “basic”, “intermediate”, “mixed”
- UNIQUE_ANSWER_PER_Q: true
- USE_EXTERNAL_SRC: false
- AVOID_DUPLICATES: true
- SEED_HINT: "distribute correct answers across A–D"           # optional guidance like “distribute correct answers across A–D”

## CONTENT RULES
- Write exactly NUM_QUESTIONS unique questions, all grounded in TOPICS, at the stated DIFFICULTY.
- Each question must have exactly four answer options labeled A, B, C, D.
- There is only one correct answer per question.
- Randomize the order of A–D per question.
- If USE_EXTERNAL_SRC is true, use the attached document to populate questions.
- Keep questions clear and CCST-appropriate unless DIFFICULTY suggests otherwise.
- Do not include images, code blocks, links, or references—text only.
- Make the output a JSON codeblock.

## SOLUTIONS RULES
- Provide a solution_table with exactly NUM_QUESTIONS rows.
- Each row fields:
    - number: the question number (1..NUM_QUESTIONS)
    - answer: the correct option letter (“A”|“B”|“C”|“D”)
- explanation: one concise sentence explaining why the answer is correct.

## VALIDATION RULES
- Output must be valid JSON and match the exact key names and structure below.
- Do not add any extra keys or metadata.
- Ensure each questions[i].options has A, B, C, D keys present and non-empty.
- Ensure solution_table numbers map correctly to each question and letters match an existing option.
- No duplicate questions. No contradictory answers.

## OUTPUT FORMAT (exact schema)
```
{
"title": "",
"subtitle": "",
"questions": [
    {
    "text": "<question 1 text>",
    "options": {
    “A”: "",
    "B": "",
    "C": "",
    “D”: “”
    }
}
// … repeat until NUM_QUESTIONS items total
],
“solution_table”: [
    {
    “number”: 1,
    “answer”: “<A|B|C|D>”,
    “explanation”: “”
    }
// … one entry per question up to NUM_QUESTIONS
]
}
```

**NOW GENERATE**

Using the INPUTS, write the quiz. Return only the final JSON object code-block populated with your questions, options, and solution_table.
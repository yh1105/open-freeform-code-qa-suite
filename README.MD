# Open Freeform QA Benchmark

----

## How to run?

Prompt for each case is in `cases/`.
You can read all `*.yaml` and parse `prompt_path` field to get the prompt path.

Then, for generated responses, store them in a folder in `responses/`.
In the folder, `params.yaml` is the index from case file name to response text files.

Then, run `python grader_main.py suite_v1.yaml responses/[your dir]`

Results will be printed and stored in `result/`.

For example:

- For GPT-4:

    `python grader_main.py suite_v1.yaml responses/gpt-4_0.2_0.9_10`
    
    **Best @ 10: 28.792 / 40**

- For GPT-3.5-Turbo:

    `python grader_main.py suite_v1.yaml responses/gpt-3.5-turbo_0.2_0.9_10`
    
    **Best @ 10: 22.906 / 40**

---

This repo stores a benchmark for code model's freeform QA.
The evaluation metric focuses on answer correctness, which is instance-specific to encode domain knowledge requirements and combines both unit-test-based and natural-language-based evaluation.
The benchmark is generated from randomly-sampled popular questions from StackOverflow, covering a broad range of domains and languages.

Detail schema of suites, instances, and evaluation metrics will come later.

At the current stage, the questions are solely from uniform sampling from StackOverflow to ensure minimal bias and maximal coverage.
The initial suite includes 40 questions.
In later stages, we plan to adopt two directions: 
(1) recruit human annotators to further enlarge the size; 
(2) for some specific domains, we may automatically evolve to get more questions.

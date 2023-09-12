# Open Freeform QA Benchmark

----

This repo stores a benchmark for code model's freeform QA.
The evaluation metric focuses on answer correctness, which is instance-specific to encode domain knowledge requirements and combines both unit-test-based and natural-language-based evaluation.
The benchmark is generated from randomly-sampled popular questions from StackOverflow, covering a broad range of domains and languages.

Detail schema of suites, instances, and evaluation metrics will come later.

At the current stage, the questions are solely from uniform sampling from StackOverflow to ensure minimal bias and maximal coverage.
The initial suite includes 40 questions.
In later stages, we plan to adopt two directions: 
(1) recruit human annotators to further enlarge the size; 
(2) for some specific domains, we may automatically evolve to get more questions.

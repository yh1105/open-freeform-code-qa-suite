# First check the runtime env
python env_check.py

# Generate responses with 10 trails using GPT4 and GPT3.5, saved to responses/
python openai_caller.py suite_v1.yaml gpt-4 --n 10
python openai_caller.py suite_v1.yaml gpt-3.5-turbo --n 10

# Compute scores of best@10, saved to results/
python grader_main.py suite_v1.yaml responses/gpt-4_0.2_0.9_10
python grader_main.py suite_v1.yaml responses/gpt-3.5-turbo_0.2_0.9_10

# Compute result statistics
python print_result_stat.py results/suite_v1_gpt-4_0.2_0.9_10.yaml results/suite_v1_gpt-4_0.2_0.9_10_stats_table.txt --model_name gpt4
python print_result_stat.py results/suite_v1_gpt-3.5-turbo_0.2_0.9_10.yaml results/suite_v1_gpt-3.5-turbo_0.2_0.9_10_stats_table.txt --model_name gpt3.5

# Running part 0
python openai_caller.py suite_v2_part_0.yaml gpt-4 --n 10
python openai_caller.py suite_v2_part_0.yaml gpt-3.5-turbo --n 10
python grader_main.py suite_v2_part_0.yaml responses/gpt-4_0.2_0.9_10_suite_v2_part_0
python grader_main.py suite_v2_part_0.yaml responses/gpt-3.5-turbo_0.2_0.9_10_suite_v2_part_0
python print_result_stat.py results/suite_v2_part_0_gpt-4_0.2_0.9_10_suite_v2_part_0.yaml results/suite_v2_part_0_gpt-4_0.2_0.9_10_stats_table.txt --model_name gpt4
python print_result_stat.py results/suite_v2_part_0_gpt-3.5-turbo_0.2_0.9_10_suite_v2_part_0.yaml results/suite_v2_part_0_gpt-3.5-turbo_0.2_0.9_10_stats_table.txt --model_name gpt3.5
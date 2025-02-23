"""
From https://github.com/bigcode-project/bigcode-evaluation-harness/blob/main/lm_eval/tasks/humanevalpack.py
@article{muennighoff2023octopack,
      title={OctoPack: Instruction Tuning Code Large Language Models},
      author={Niklas Muennighoff and Qian Liu and Armel Zebaze and Qinkai Zheng and Binyuan Hui and Terry Yue Zhuo and Swayam Singh and Xiangru Tang and Leandro von Werra and Shayne Longpre},
      journal={arXiv preprint arXiv:2308.07124},
      year={2023}}
"""

"""
    Need to setup javascript environment first
"""

import os
from typing import Dict, List, Tuple
os.environ["HF_ALLOW_CODE_EVAL"] = "1"
# Note: the following allows running only on linux yet
# os.environ['PATH'] = '/usr/local/lib/nodejs/node/bin:' + os.environ['PATH']
# os.environ['NODE_PATH'] = '/usr/local/lib/node_modules'
import contextlib
import signal
import json
import tempfile
import subprocess
import rpy2.robjects as robjects
from evaluate import load

@contextlib.contextmanager
def chdir(root):
    if root == ".":
        yield
        return
    cwd = os.getcwd()
    os.chdir(root)
    try:
        yield
    except BaseException as exc:
        raise exc
    finally:
        os.chdir(cwd)


@contextlib.contextmanager
def create_tempdir():
    with tempfile.TemporaryDirectory() as dirname:
        with chdir(dirname):
            yield dirname

@contextlib.contextmanager
def chdir(root):
    if root == ".":
        yield
        return
    cwd = os.getcwd()
    os.chdir(root)
    try:
        yield
    except BaseException as exc:
        raise exc
    finally:
        os.chdir(cwd)


@contextlib.contextmanager
def create_tempdir():
    with tempfile.TemporaryDirectory() as dirname:
        with chdir(dirname):
            yield dirname


class TimeoutException(Exception):
    pass

@contextlib.contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")

    signal.setitimer(signal.ITIMER_REAL, seconds)
    signal.signal(signal.SIGALRM, signal_handler)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)

def r_executor(references, predictions, timeout):
    program = predictions[0][0] + '\n' + references[0]
    result = []
    try:
        with time_limit(timeout):
            #print(program)
            #print('*' * 80)
            robjects.r(program)
        result.append('passed')
    except TimeoutException:
        result.append("timed out")
    except BaseException as e:
        result.append(f"failed: {e}")
    logs = [[(0, dict(
        task_id=0,
        passed=result[0] == "passed",
        result=result[0],
        completion_id=0,
    ))]]

    return {'pass@1': float(int(result[0] == "passed"))}, logs



def python_unsafe_executor(references, predictions, timeout):

    check_program = predictions[0][0] + '\n' + references[0]

    result = []
    try:
        exec_globals = {}
        with time_limit(timeout):
            exec(check_program, exec_globals)
        result.append("passed")
    except TimeoutException:
        result.append("timed out")
    except BaseException as e:
        result.append(f"failed: {e}")

    logs = [[(0, dict(
        task_id=0,
        passed=result[0].startswith("passed"),
        result=result,
        completion_id=0,
    ))]]

    return {'pass@1': float(int(result[0] == "passed"))}, logs

def java_unsafe_executor(references, predictions, timeout):

    check_program = predictions[0][0] + '\n' + references[0]

    result = []

    with create_tempdir():
        open(f"Main.java", 'w').write(check_program)
        # Run program.
        try:
            exec_result = subprocess.run(["javac Main.java; java Main"], timeout=timeout, capture_output=True, shell=True)
            # print(exec_result.returncode)
            if exec_result.stderr.decode():
                err = exec_result.stderr.decode()
                result.append(f"stderr: {err}")
            elif exec_result.stdout.decode():
                err = exec_result.stdout.decode()
                result.append(f"stdout: {err}")
            else:
                result.append('')
            if exec_result.returncode != 0:
                result[-1] = f"failed: returncode: {exec_result.returncode} " + result[-1] 
            else:
                result[-1] = "passed " + result[-1]
        except subprocess.TimeoutExpired as e:
            result[-1] = "time out " + result[-1]  
    
    logs = [[(0, dict(
        task_id=0,
        passed=result[0].startswith("passed"),
        result=result,
        completion_id=0,
    ))]]

    return {'pass@1': float(int(result[0].startswith("passed")))}, logs

def cs_unsafe_executor(references, predictions, timeout):

    check_program = predictions[0][0] + '\n' + references[0]

    result = []

    with create_tempdir():
        open(f"main.cs", 'w').write(check_program)
        # Run program.
        try:
            exec_result = subprocess.run(["mcs -out:main.exe main.cs; mono main.exe"], timeout=timeout, capture_output=True, shell=True)
            # print(exec_result.returncode)
            if exec_result.stderr.decode():
                err = exec_result.stderr.decode()
                result.append(f"stderr: {err}")
            elif exec_result.stdout.decode():
                err = exec_result.stdout.decode()
                result.append(f"stdout: {err}")
            else:
                result.append('')
            if exec_result.returncode != 0:
                result[-1] = f"failed: returncode: {exec_result.returncode} " + result[-1] 
            else:
                result[-1] = "passed " + result[-1]
        except subprocess.TimeoutExpired as e:
            result[-1] = "time out " + result[-1]  
    
    logs = [[(0, dict(
        task_id=0,
        passed=result[0].startswith("passed"),
        result=result,
        completion_id=0,
    ))]]

    return {'pass@1': float(int(result[0].startswith("passed")))}, logs

def cpp_unsafe_executor(references, predictions, timeout):

    check_program = predictions[0][0] + '\n' + references[0]

    result = []

    with create_tempdir():
        open(f"main.cpp", 'w').write(check_program)
        # Run program.
        try:
            exec_result = subprocess.run(["g++ main.cpp -o main; ./main"], timeout=timeout, capture_output=True, shell=True)
            # print(exec_result.returncode)
            if exec_result.stderr.decode():
                err = exec_result.stderr.decode()
                result.append(f"stderr: {err}")
            elif exec_result.stdout.decode():
                err = exec_result.stdout.decode()
                result.append(f"stdout: {err}")
            else:
                result.append('')
            if exec_result.returncode != 0:
                result[-1] = f"failed: returncode: {exec_result.returncode} " + result[-1] 
            else:
                result[-1] = "passed " + result[-1]
        except subprocess.TimeoutExpired as e:
            result[-1] = "time out " + result[-1]  
    
    logs = [[(0, dict(
        task_id=0,
        passed=result[0].startswith("passed"),
        result=result,
        completion_id=0,
    ))]]

    return {'pass@1': float(int(result[0].startswith("passed")))}, logs

def sql_unsafe_executor(references, predictions, timeout):
    import sqlite3
    conn = sqlite3.connect(':memory:')
    cur = conn.cursor()
    result = []
    try:
        with time_limit(timeout):
            cur.execute(predictions[0][0] + '\n' + references[0])
        result.append("passed")
    except TimeoutException:
        result.append("timed out")
    except BaseException as e:
        result.append(f"failed: {e}")

    conn.close()

    logs = [[(0, dict(
        task_id=0,
        passed=result[0].startswith("passed"),
        result=result,
        completion_id=0,
    ))]]

    return {'pass@1': float(int(result[0] == "passed"))}, logs


def js_unsafe_executor(references, predictions, timeout):

    check_program = predictions[0][0] + '\n' + references[0]

    result = []

    with create_tempdir():
        open(f"test.js", 'w').write(check_program)
        # Run program.
        try:
            exec_result = subprocess.run(["node", "test.js"], timeout=timeout, capture_output=True)
            # print(exec_result.returncode)
            if exec_result.stderr.decode():
                err = exec_result.stderr.decode()
                result.append(f"stderr: {err}")
            elif exec_result.stdout.decode():
                err = exec_result.stdout.decode()
                result.append(f"stdout: {err}")
            else:
                result.append('')
            if exec_result.returncode != 0:
                result[-1] = f"failed: returncode: {exec_result.returncode} " + result[-1] 
            else:
                result[-1] = "passed " + result[-1]
        except subprocess.TimeoutExpired as e:
            result[-1] = "time out " + result[-1]  
    
    logs = [[(0, dict(
        task_id=0,
        passed=result[0].startswith("passed"),
        result=result,
        completion_id=0,
    ))]]

    return {'pass@1': float(int(result[0].startswith("passed")))}, logs


def ts_unsafe_executor(references, predictions, timeout):

    check_program = predictions[0][0] + '\n' + references[0]

    result = []

    with create_tempdir():
        open(f"test.ts", 'w').write(check_program)
        # Compile to js then run program.
        try:
            exec_result = subprocess.run(["npx tsc test.ts --outfile test.js; node test.js"], timeout=timeout, capture_output=True, shell=True)
            # with open('test.js', 'r') as f:
            #     print(f.read())
            # print(exec_result.returncode)
            if exec_result.stderr.decode():
                err = exec_result.stderr.decode()
                result.append(f"stderr: {err}")
            elif exec_result.stdout.decode():
                err = exec_result.stdout.decode()
                result.append(f"stdout: {err}")
            else:
                result.append('')
            if exec_result.returncode != 0:
                result[-1] = f"failed: returncode: {exec_result.returncode} " + result[-1] 
            else:
                result[-1] = "passed " + result[-1]
        except subprocess.TimeoutExpired as e:
            result[-1] = "time out " + result[-1]  
    
    logs = [[(0, dict(
        task_id=0,
        passed=result[0].startswith("passed"),
        result=result,
        completion_id=0,
    ))]]

    return {'pass@1': float(int(result[0].startswith("passed")))}, logs


def go_unsafe_executor(references, predictions, timeout):

    check_program = predictions[0][0] + '\n' + references[0]

    result = []

    with create_tempdir():
        open(f"main.go", 'w').write(check_program)

        try:
            exec_result = subprocess.run(["go", "run", "main.go"], timeout=timeout, capture_output=True)

            if exec_result.returncode == 0:
                result.append("passed")
            else:
                if exec_result.stderr:
                    try:
                        err = exec_result.stderr.decode()
                    except:
                        err = exec_result.stderr
                else:
                    try:
                        err = exec_result.stdout.decode()
                    except:
                        err = exec_result.stdout
                result.append(f"failed: {err}")
        except subprocess.TimeoutExpired as e:
            result.append("timed out")
    
    logs = [[(0, dict(
        task_id=0,
        passed=result[0].startswith("passed"),
        result=result,
        completion_id=0,
    ))]]

    return {'pass@1': float(int(result[0].startswith("passed")))}, logs


# language supported by us
LANGUAGES = ["python", "cpp", "javascript", "typescript", "java", "go", "rust", "c#", 'r']

LANGUAGE_TO_NAME = {
    "python": "Python",
    "cpp": "C++",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "java": "Java",
    "go": "Go",
    "rust": "Rust",
    "c#": "C#",
    'r': 'R'
}

LANGUAGE_TO_EXTENSION = {
    "python": "py",
    "cpp": "cpp",
    "javascript": "js",
    "typescript": "ts",
    "java": "java",
    "go": "go",
    "rust": "rs",
    "c#": "cs",
    'r': 'r'
}

# Taken from https://huggingface.co/datasets/nuprl/MultiPL-E/ & https://github.com/THUDM/CodeGeeX
LANGUAGE_TO_STOP_WORDS = {
    # https://github.com/THUDM/CodeGeeX/blob/23ee51505a2bcd34d59d2e271b22e5bd91475462/codegeex/benchmark/utils.py#L164
    "python": ["\nclass", "\ndef", "\n#", "\n@", "\nprint", "\nif", "\nassert"],
    # https://github.com/THUDM/CodeGeeX/blob/23ee51505a2bcd34d59d2e271b22e5bd91475462/codegeex/benchmark/utils.py#L185
    "cpp": [],
    # https://github.com/THUDM/CodeGeeX/blob/23ee51505a2bcd34d59d2e271b22e5bd91475462/codegeex/benchmark/utils.py#L188
    "javascript": [],
    # https://github.com/THUDM/CodeGeeX/blob/23ee51505a2bcd34d59d2e271b22e5bd91475462/codegeex/benchmark/utils.py#L177
    "go": ["\n//", "\nfunc main(", "struct", "\nfunc"],
    # https://github.com/THUDM/CodeGeeX/blob/23ee51505a2bcd34d59d2e271b22e5bd91475462/codegeex/benchmark/utils.py#L169
    "java": [],
    "rust": [],
    "sql": [],
    "c#": [],
    'r': []
}

LANGUAGE_TO_TIMEOUT = {
    "python": 10,
    "cpp": 60,
    "javascript": 10,
    "typescript": 20,
    "java": 10,
    "go": 20,
    "rust": 300,  # Necessary for first-time compilation of cargo
    "sql": 10,
    "c#": 20,
    'r': 20
}

# Java sometimes fails with more workers; For JS it's twice as fast with 4 workers
LANGUAGE_TO_NUM_WORKERS = {
    "python": 4,
    "cpp": 4,
    "javascript": 4,
    "typescript": 4,
    "java": 1,
    "go": 4,
    "rust": 1,
    "sql": 1,
    "c#": 4,
    'r': 4
}

# https://github.com/THUDM/CodeGeeX/blob/23ee51505a2bcd34d59d2e271b22e5bd91475462/codegeex/benchmark/utils.py#L6
IMPORT_HELPER = {
    "python": [
        "import math",
        "import re",
        "import sys",
        "import copy",
        "import datetime",
        "import itertools",
        "import collections",
        "import heapq",
        "import statistics",
        "import functools",
        "import hashlib",
        "import numpy",
        "import numpy as np",
        "import string",
        "from typing import *",
        "from collections import *",
    ],
    "go": [
        "math",
        "strings",
        "fmt",
        "strconv",
        "time",
        "bytes",
        "regexp",
        "sort",
        "math/rand",
        "crypto/md5",
    ],
    "cpp": [
        "using namespace std;",
        "#include<stdlib.h>",
        "#include<algorithm>",
        "#include<cmath>",
        "#include<math.h>",
        "#include<numeric>",
        "#include<stdio.h>",
        "#include<vector>",
        "#include<set>",
        "#include<map>",
        "#include<queue>",
        "#include<stack>",
        "#include<list>",
        "#include<deque>",
        "#include<boost/any.hpp>",
        "#include<string>",
        "#include<climits>",
        "#include<cstring>",
        "#include<iostream>",
        "#include<sstream>",
        "#include<fstream>",
    ],
    "c#": [],
    'r': [
        'rm(list=ls())',
        'library(assert)',
    ]
}


def remove_last_block(code, lang):
    """
    Adapted from https://github.com/THUDM/CodeGeeX/blob/23ee51505a2bcd34d59d2e271b22e5bd91475462/codegeex/benchmark/utils.py#L151
    """
    stop_words = LANGUAGE_TO_STOP_WORDS[lang]
    for w in stop_words:
        if w in code:
            code = code[:code.find(w)]

    ### Find the first occassion where a chain of { } is closed
    if lang == "python":
        for i, line in enumerate(code.split("\n")):
            if len(line.strip()) > 0 and line[0] != ' ' and line[0] != '\t':
                return "\n".join(code.split("\n")[:i])
    elif lang in ["java", "javascript", "go", "cpp", "rust"]:
        open_brackets = 2 if lang == "java" else 1
        cut = False
        for i, c in enumerate(code):
            if c == '{':
                open_brackets += 1
            elif c == '}':
                open_brackets -= 1
            if open_brackets == 0:
                code = code[:i+1]
                cut = True
                break
        if not cut:
            if lang == "java":
                main_pos = code.find("public static void main")
                if main_pos != -1:
                    code = code[:main_pos] + '}'
                if '}' in code:
                    code = code[:code.rfind('}')] + '}'
                if code.count('{') - 1 == code.count('}'):
                    code += "\n}"
            elif '}' in code:
                code = code[:code.rfind('}')] + '}'
    return code


def preprocess(generations: List[str], lang: str, only_longest: bool) -> List[str]:
    """
        Extract code blocks from the generations
    :param generations:
    :param lang:
    :return: processed pure code blocks
    """
    ans = []
    ### first, if ``` exists, using the longest ``` blocks
    for gen in generations:
        if gen.count('```') >= 2:
            # TODO: just directly concatenate all code blocks
            lines = gen.split('\n')
            code_idendifier_lines = [no for no, text in enumerate(lines) if text.startswith("```")]
            if only_longest:
                longest_lines = 0
                longest_lines_idx = 0
                for i in range(0, len(code_idendifier_lines)-1, 2):
                    if code_idendifier_lines[i+1] - code_idendifier_lines[i] > longest_lines:
                        longest_lines = code_idendifier_lines[i+1] - code_idendifier_lines[i]
                        longest_lines_idx = i
                gen = '\n'.join(lines[code_idendifier_lines[longest_lines_idx] + 1:
                                      code_idendifier_lines[longest_lines_idx + 1]])
            else:
                gens = []
                for i in range(0, len(code_idendifier_lines)-1, 2):
                    now_gen = '\n'.join(lines[code_idendifier_lines[i] + 1:
                                              code_idendifier_lines[i + 1]])
                    gens.append(now_gen)
                gen = '\n\n'.join(gens)
        else:
            # function-signature form
            gen = remove_last_block(gen, lang)
        ans.append(gen)
    return ans


def get_exec_results(prefix_from_file: str, generations: List[str], references: str, lang: str,
                     timeout: None) -> Tuple[Dict[str, float], Dict[int, List], str]:
    """Takes the list of LM generations and evaluates them against ground truth references.

    :param prefix_from_file: universal setup code
    :param generations: list(str)
        list of string containing generations
    :param references: str
         str containing the test case
    """
    generations = [prefix_from_file + '\n' + gen for gen in generations]
    code_metric = load("code_eval_octopack")

    timeout = LANGUAGE_TO_TIMEOUT[lang] if timeout is None else timeout
    num_workers = LANGUAGE_TO_NUM_WORKERS[lang]

    ### CUSTOM PROG LANGUAGE CHANGES ###
    # Inspiration: https://github.com/THUDM/CodeGeeX/blob/ebeb850f227a90c79de39f7e26b1302f374f3240/codegeex/benchmark/evaluate_humaneval_x.py
    if lang == "python":
        python_imports = "\n".join(IMPORT_HELPER["python"])
        generations = [
            (python_imports + "\n" + g).strip() for g in generations
        ]
    elif lang == "cpp":
        cpp_imports = "\n".join(IMPORT_HELPER["cpp"])
        # Remove main in case present
        generations = [
            # (cpp_imports + "\n" + g.split("int main")[0]).strip() for g in generations
            (cpp_imports + "\n" + g).strip() for g in generations
        ]
    elif lang == 'r':
        r_imports = '\n'.join(IMPORT_HELPER['r'])
        generations = [
            (r_imports + "\n" + g).strip() for g in generations
        ]

    # elif lang == "java":
    #     generations = [
    #         g.replace("public class Main {\n    }", "").strip() for g in generations
    #     ]
    # elif language == "go":
    #     ds = self.get_dataset().select(range(len(generations)))
    #     for gen, ref, doc in zip(generations, references, ds):
    #         for line in doc["import"].split("\n"):
    #             line = line.replace("import", "").replace("(", "").replace(")", "").replace('"', "").strip()
    #             if line: assert line in IMPORT_HELPER["go"], doc["import"]  # Will be added later
    #         test_setup_str = doc["test_setup"] + "\n"
    #         for i, g in enumerate(gen):
    #             for line in test_setup_str.split("\n"):
    #                 line = line.replace("import", "").replace("(", "").replace(")", "").strip()
    #                 if line.startswith('"') and line in g:
    #                     test_setup_str = test_setup_str.replace(line, "")
    #             g = test_setup_str + g + "\n" + ref
    #             other_pkgs = set()
    #             for pkg in IMPORT_HELPER["go"]:
    #                 if ('"' + pkg + '"' not in g):
    #                     p = pkg.split("/")[-1]
    #                     # Check if the package is used
    #                     if (p + "." in g):
    #                         # The problem is that it could appear in a comment
    #                         # E.g. in problem 158, the docstring is:
    #                         # // ... a list of strings.
    #                         # but the "strings" pkg is never used
    #                         # Golang throws an error if the pkg is not used
    #                         # Thus search for the package & make sure it's not in a commented line
    #                         lines = g.split("\n")
    #                         for line in lines:
    #                             if (p + "." in line) and not (line.strip().startswith("//")):
    #                                 other_pkgs.add('"' + p + '"')
    #                                 break
    #             other_pkgs_str = ""
    #             if other_pkgs:
    #                 other_pkgs_str = "import (\n" + "\n".join(["    " + p for p in other_pkgs]) + "\n)\n"
    #             if ("package main" in gen[i]) and ("package main" in test_setup_str):
    #                 gen[i] = gen[i].replace("package main", "")
    #             gen[i] = test_setup_str + other_pkgs_str + gen[i]
    # elif language == "rust":
    #     ds = self.get_dataset().select(range(len(generations)))
    #     main = "fn main(){}\n"
    #     for gen, doc in zip(generations, ds):
    #         declaration = doc["declaration"]
    #         for i, g in enumerate(gen):
    #             new_gen = ""
    #             if "fn main()" not in g:
    #                 new_gen += main
    #             for line in declaration.split("\n"):
    #                 if line.strip() not in g:
    #                     # Skip if the function is already present
    #                     if line.strip().startswith("fn") and (line.strip().split("(")[0]) in g:
    #                         continue
    #                     new_gen += line.strip() + "\n"
    #             # If fn main() is present twice, cut off before the second one
    #             g = "fn main()".join(g.split("fn main()")[0:2])
    #             new_gen += g
    #             gen[i] = new_gen

    # packaging to a suite of single instance for evaluation
    generations = [[gen] for gen in generations]
    references = [references]

    ### EVALUATION ###
    if lang == 'python':
        results, logs = python_unsafe_executor(
            references=references,
            predictions=generations,
            timeout=timeout,
        )
    elif lang == 'sql':
        results, logs = sql_unsafe_executor(
            references=references,
            predictions=generations,
            timeout=timeout,
        )
    elif lang == 'java':
        results, logs = java_unsafe_executor(
            references=references,
            predictions=generations,
            timeout=timeout,
        )
    elif lang in ['javascript', 'js']:
        results, logs = js_unsafe_executor(
            references=references,
            predictions=generations,
            timeout=timeout,
        )
    elif lang == 'typescript':
        results, logs = ts_unsafe_executor(
            references=references,
            predictions=generations,
            timeout=timeout,
        )
    elif lang == 'cpp':
        results, logs = cpp_unsafe_executor(
            references=references,
            predictions=generations,
            timeout=timeout,
        )
    elif lang == 'c#':
        results, logs = cs_unsafe_executor(
            references=references,
            predictions=generations,
            timeout=timeout,
        )
    elif lang == 'r':
        results, logs = r_executor(
            references=references,
            predictions=generations,
            timeout=timeout
        )
    elif lang == 'go':
        results, logs = go_unsafe_executor(
            references=references,
            predictions=generations,
            timeout=timeout,
        )
    else:
        results, logs = code_metric.compute(
            references=references,
            predictions=generations,
            language=lang,
            timeout=timeout,
            num_workers=num_workers,
        )
    # # Write logs to json
    # with open("logs.json", "w") as f:
    #     json.dump(logs, f, indent=4, ensure_ascii=False)

    """Debugging help
    for i, (gen, ref) in enumerate(zip(generations, references)):
        import time
        starttime = time.time()            
        results, log = code_metric.compute(
            references=[ref],
            predictions=[gen],
            language=language,
            timeout=timeout,
        )
        print("Took: ", time.time() - starttime)
        with open("errors.txt", "a") as f:
            f.write(log[0][0][1]["result"] + "\n")
        if ("compilation error" in log[0][0][1]["result"]):
            print("Result")
            print(results)
            print("Log")
            print(log)
            print("Gen")
            print(gen[0])
            print("Ref")
            print(ref)
    """
    """
    print(generations[0][0])
    print(references[0])
    print(logs)
    """

    return results, logs, generations[0][0]










# def create_all_tasks():
#     fix = {f"humanevalfix{mode}-{language}": create_task(language, "fix" + mode) for language in LANGUAGES for mode in
#            ["tests", "docs"]}
#     explain = {f"humanevalexplain{mode}-{language}": create_task(language, "explain" + mode) for language in LANGUAGES
#                for mode in ["describe", "synthesize"]}
#     synthesize = {f"humanevalsynthesize-{language}": create_task(language, "synthesize") for language in LANGUAGES}
#     return {**fix, **explain, **synthesize}
#
#
# def create_task(language, name):
#     class HumanEvalFixTests(HumanEvalFixBase):
#         def __init__(self, language=language, prompt="instruct"):
#             super().__init__(language=language, prompt=prompt, with_docs=False)
#
#     class HumanEvalFixDocs(HumanEvalFixBase):
#         def __init__(self, language=language, prompt="instruct"):
#             super().__init__(language=language, prompt=prompt, with_docs=True)
#
#     class HumanEvalExplainDescribe(HumanEvalExplainDescribeBase):
#         def __init__(self, language=language, prompt="instruct"):
#             super().__init__(language=language, prompt=prompt, with_docs=False)
#
#     class HumanEvalExplainSynthesize(HumanEvalExplainSynthesizeBase):
#         def __init__(self, language=language, prompt="instruct", load_data_path=None):
#             super().__init__(language=language, prompt=prompt, with_docs=False, load_data_path=load_data_path)
#
#     class HumanEvalSynthesize(HumanEvalSynthesizeBase):
#         def __init__(self, language=language, prompt="instruct"):
#             super().__init__(language=language, prompt=prompt, with_docs=True)
#
#     if name == "fixtests":
#         return HumanEvalFixTests
#     elif name == "fixdocs":
#         return HumanEvalFixDocs
#     elif name == "explaindescribe":
#         return HumanEvalExplainDescribe
#     elif name == "explainsynthesize":
#         return HumanEvalExplainSynthesize
#     elif name == "synthesize":
#         return HumanEvalSynthesize
#
#
# class HumanEvalPack():
#     """Parent class for all HumanEvalPack tasks"""
#     DATASET_PATH = "bigcode/humanevalpack"
#     DATASET_NAME = None
#
#     def __init__(self, prompt="instruct", language="python", with_docs=True):
#
#         self.DATASET_NAME = language
#         self.prompt = prompt
#         stop_words = LANGUAGE_TO_STOP_WORDS[language]
#         if self.prompt.startswith("edit"):
#             stop_words.extend([
#                 "<commit_before>",
#                 "<commit_msg>",
#                 "<commit_after>",
#             ])
#         elif self.prompt == "starchat":
#             stop_words.append("<|end|>")
#         elif self.prompt == "diff":
#             stop_words = ["<commit_before>", "<commit_msg>", "<commit_after>"]
#         elif self.prompt == "diff-carper":
#             stop_words = ["<BEF>", "<MSG>", "<DFF>", "\ No newline at end of file"]
#         stop_words.append("<|endoftext|>")
#         self.with_docs = with_docs
#         super().__init__(stop_words=stop_words, requires_execution=True)
#
#     def get_dataset(self):
#         return self.dataset["test"]
#
#     def get_prompt_base(self, doc):
#         if self.with_docs:
#             return doc["prompt"]  # Already includes fn main for rust
#         else:
#             if self.DATASET_NAME == "rust":
#                 # See
#                 # https://github.com/roG0d/CodeGeeX/blob/f66205b5f615a4eead9c26d7ec297e14738ea18d/codegeex/benchmark/evaluate_humaneval_x.py#L78
#                 # https://github.com/THUDM/CodeGeeX/pull/76#issuecomment-1500653190
#                 return "fn main(){}\n" + doc["declaration"]
#             else:
#                 return doc["declaration"]
#
#     def get_prompt(self, prompt_base, instruction, context=None):
#         if context is None:
#             inp = instruction
#         # `Context first then instruction` methods
#         elif self.prompt in ["continue", "instruct"]:
#             inp = context + "\n" + instruction
#         else:
#             inp = instruction + "\n" + context
#
#         if self.prompt == "continue":
#             assert context is None, "The `continue` prompt should only be used for HumanEvalSynthesize. Use `instruct` for HumanEvalFix and HumanEvalExplain."
#             prompt = prompt_base
#         elif self.prompt == "instruct":
#             prompt = inp + "\n\n" + prompt_base
#         elif self.prompt == "octocoder":
#             prompt = f'Question: {inp}\n\nAnswer:\n{prompt_base}'
#         elif self.prompt == "octogeex":
#             prompt = f'Question: {inp.strip()}\n\nAnswer:\n{prompt_base}'
#         elif self.prompt == "starchat":
#             # https://huggingface.co/HuggingFaceH4/starchat-beta
#             prompt = f'<|system|>\n<|end|>\n<|user|>\n{inp}<|end|>\n<|assistant|>\n{prompt_base}'
#         elif self.prompt == "starcodercommit":
#             prompt = f'<commit_before><commit_msg>{inp}<commit_after>{prompt_base}'
#         elif self.prompt == "instructcodet5p":
#             # https://github.com/salesforce/CodeT5/blob/main/CodeT5%2B/humaneval/generate_codet5p.py#L89
#             prompt = f'Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\n{inp}\n\n### Response:{prompt_base}'
#         elif self.prompt == "wizardcoder":
#             # https://github.com/nlpxucan/WizardLM/blob/main/WizardCoder/src/humaneval_gen.py#L37
#             prompt = f'Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\n{inp}\n\n### Response:\n{prompt_base}'
#         elif self.prompt == "codellama":
#             prompt = f"[INST] {inp.strip()} [/INST] {prompt_base}"
#         else:
#             raise NotImplementedError
#         # Strip off the final \n to make the tokens more natural
#         # Essentially, we want to make sure that if there was no distinction between
#         # input & output, the tokens would be the same
#         # E.g. for SantaCoder:
#         # tokenize("""def hi()\n   return""")
#         # ['def', 'Ġhi', '()', 'ĊĠĠ', 'Ġreturn']
#         # So we need to split before the \n so that the input is
#         # ['def', 'Ġhi', '()'] and the model can generate ['ĊĠĠ', 'Ġreturn']
#         # If instead we provide def hi()\n the tokens will be
#         # ['def', 'Ġhi', '()', 'Ċ'] and the model would need to generate ['ĠĠ', 'Ġreturn']
#         # Which would be harder, as it's not the usual way these tokens are tokenized
#         # i.e. the model has never seen the token sequence of ['()', 'Ċ', 'ĠĠ'], but only ['()', 'ĊĠĠ']
#         # The same holds for Java, JS, Go, Rust, C++ tho the start sequences are slightly different
#         return prompt.strip()
#
#     def get_reference(self, doc, get_solution=False):
#         if get_solution:
#             return doc["prompt"] + doc["canonical_solution"]
#         else:
#             return "\n" + doc["test"]  # check(func_name) is already included
#
#
# class HumanEvalPackGenerative(HumanEvalPack):
#     """Parent class for all HumanEvalPack tasks except describing code"""
#
#     def check_fn(self, code):
#         """
#         Checks whether the generated code is finished.
#         Problem: Models rarely split their code into multiple functions, but this stops the model after the 1st function.
#         Inspiration: https://github.com/THUDM/CodeGeeX/blob/23ee51505a2bcd34d59d2e271b22e5bd91475462/codegeex/benchmark/utils.py#L115
#         """
#         if any([w in code for w in self.stop_words]): return True
#
#         # The heuristics below do not hold for diff generation
#         if (self.prompt.startswith("diff")): return False
#
#         if self.DATASET_NAME == "python":
#             for line in code.split("\n"):
#                 if len(line.strip()) > 0 and line[0] != ' ' and line[0] != '\t':
#                     return True
#         else:
#             open_brackets = 2 if self.DATASET_NAME == "java" else 1
#             if code.count("{") + open_brackets == code.count("}"):
#                 return True
#         return False
#
#     def remove_last_block(self, code):
#         """
#         Adapted from https://github.com/THUDM/CodeGeeX/blob/23ee51505a2bcd34d59d2e271b22e5bd91475462/codegeex/benchmark/utils.py#L151
#         """
#         for w in self.stop_words:
#             if w in code:
#                 code = code[:code.find(w)]
#
#         ### Find the first occassion where a chain of { } is closed
#         if self.DATASET_NAME == "python":
#             for i, line in enumerate(code.split("\n")):
#                 if len(line.strip()) > 0 and line[0] != ' ' and line[0] != '\t':
#                     return "\n".join(code.split("\n")[:i])
#         elif self.DATASET_NAME in ["java", "js", "go", "cpp", "rust"]:
#             open_brackets = 2 if self.DATASET_NAME == "java" else 1
#             cut = False
#             for i, c in enumerate(code):
#                 if c == '{':
#                     open_brackets += 1
#                 elif c == '}':
#                     open_brackets -= 1
#                 if open_brackets == 0:
#                     code = code[:i + 1]
#                     cut = True
#                     break
#             if not cut:
#                 if self.DATASET_NAME == "java":
#                     main_pos = code.find("public static void main")
#                     if main_pos != -1:
#                         code = code[:main_pos] + '}'
#                     if '}' in code:
#                         code = code[:code.rfind('}')] + '}'
#                     if code.count('{') - 1 == code.count('}'):
#                         code += "\n}"
#                 elif '}' in code:
#                     code = code[:code.rfind('}')] + '}'
#         return code
#
#     def postprocess_generation(self, generation, idx):
#         """Defines the postprocessing for a LM generation.
#         :param generation: str
#             code generation from LM
#         :param idx: int
#             index of doc in the dataset to which the generation belongs
#             (not used for Humaneval-Task)
#         """
#         doc = self.get_dataset()[idx]
#         prompt = self.get_prompt(doc)
#         gen = self.remove_last_block(generation[len(prompt):].rstrip())
#         # Strip to maintain same behavior as with get_prompt
#         return doc["prompt"].rstrip() + gen
#
#     def process_results(self, generations, references):
#         """Takes the list of LM generations and evaluates them against ground truth references.
#
#         :param generations: list(list(str))
#             list of lists containing generations
#         :param references: list(str)
#             list of str containing refrences
#         """
#         code_metric = load("Muennighoff/code_eval_octopack")
#         timeout = LANGUAGE_TO_TIMEOUT[self.DATASET_NAME]
#         num_workers = LANGUAGE_TO_NUM_WORKERS[self.DATASET_NAME]
#         language = self.DATASET_NAME if self.DATASET_NAME != "js" else "javascript"
#
#         # ### CUSTOM MUTATE METHOD CHANGES ###
#         # if self.prompt == "diff":
#         #     # Requires:
#         #     # !wget https://raw.githubusercontent.com/google/diff-match-patch/master/python3/diff_match_patch.py
#         #     from diff_match_patch import diff_match_patch
#         #     dmp = diff_match_patch()
#         #     ds = self.get_dataset().select(range(len(generations)))
#         #     for gen, doc in zip(generations, ds):
#         #         prompt_base = self.get_prompt_base(doc)
#         #         old_code = prompt_base + doc["buggy_solution"]
#         #         for i, diff in enumerate(gen):
#         #             try:
#         #                 # Strip away anything to the left such as \n
#         #                 patches = dmp.patch_fromText(diff.lstrip())
#         #                 fixed_code, _ = dmp.patch_apply(patches, old_code)
#         #             except Exception as e:
#         #                 print(f"Failed with {e} when applying patch to buggy code: {diff}")
#         #                 fixed_code = ""
#         #             gen[i] = fixed_code
#         # elif self.prompt == "diff-carper":
#         #     from lm_eval.tasks.custom_metrics.diff_eval import apply_diff
#         #     ds = self.get_dataset().select(range(len(generations)))
#         #     for gen, doc in zip(generations, ds):
#         #         prompt_base = self.get_prompt_base(doc)
#         #         old_code = prompt_base + doc["buggy_solution"]
#         #         for i, diff_hunk in enumerate(gen):
#         #             if not (diff_hunk):
#         #                 gen[i] = ""
#         #                 continue
#         #             res: str = apply_diff(old_code, diff_hunk)
#         #             gen[i] = res
#
#         ### CUSTOM PROG LANGUAGE CHANGES ###
#         # Inspiration: https://github.com/THUDM/CodeGeeX/blob/ebeb850f227a90c79de39f7e26b1302f374f3240/codegeex/benchmark/evaluate_humaneval_x.py
#         if language == "python":
#             python_imports = "\n".join(IMPORT_HELPER["python"])
#             generations = [
#                 [(python_imports + "\n" + g).strip() for g in gen] for gen in generations
#             ]
#         elif language == "cpp":
#             cpp_imports = "\n".join(IMPORT_HELPER["cpp"])
#             # Remove main in case present
#             generations = [
#                 [(cpp_imports + "\n" + g.split("int main")[0]).strip() for g in gen] for gen in generations
#             ]
#         elif language == "java":
#             generations = [
#                 [g.replace("public class Main {\n    }", "").strip() for g in gen] for gen in generations
#             ]
#         elif language == "go":
#             ds = self.get_dataset().select(range(len(generations)))
#             for gen, ref, doc in zip(generations, references, ds):
#                 for line in doc["import"].split("\n"):
#                     line = line.replace("import", "").replace("(", "").replace(")", "").replace('"', "").strip()
#                     if line: assert line in IMPORT_HELPER["go"], doc["import"]  # Will be added later
#                 test_setup_str = doc["test_setup"] + "\n"
#                 for i, g in enumerate(gen):
#                     for line in test_setup_str.split("\n"):
#                         line = line.replace("import", "").replace("(", "").replace(")", "").strip()
#                         if line.startswith('"') and line in g:
#                             test_setup_str = test_setup_str.replace(line, "")
#                     g = test_setup_str + g + "\n" + ref
#                     other_pkgs = set()
#                     for pkg in IMPORT_HELPER["go"]:
#                         if ('"' + pkg + '"' not in g):
#                             p = pkg.split("/")[-1]
#                             # Check if the package is used
#                             if (p + "." in g):
#                                 # The problem is that it could appear in a comment
#                                 # E.g. in problem 158, the docstring is:
#                                 # // ... a list of strings.
#                                 # but the "strings" pkg is never used
#                                 # Golang throws an error if the pkg is not used
#                                 # Thus search for the package & make sure it's not in a commented line
#                                 lines = g.split("\n")
#                                 for line in lines:
#                                     if (p + "." in line) and not (line.strip().startswith("//")):
#                                         other_pkgs.add('"' + p + '"')
#                                         break
#                     other_pkgs_str = ""
#                     if other_pkgs:
#                         other_pkgs_str = "import (\n" + "\n".join(["    " + p for p in other_pkgs]) + "\n)\n"
#                     if ("package main" in gen[i]) and ("package main" in test_setup_str):
#                         gen[i] = gen[i].replace("package main", "")
#                     gen[i] = test_setup_str + other_pkgs_str + gen[i]
#         elif language == "rust":
#             ds = self.get_dataset().select(range(len(generations)))
#             main = "fn main(){}\n"
#             for gen, doc in zip(generations, ds):
#                 declaration = doc["declaration"]
#                 for i, g in enumerate(gen):
#                     new_gen = ""
#                     if "fn main()" not in g:
#                         new_gen += main
#                     for line in declaration.split("\n"):
#                         if line.strip() not in g:
#                             # Skip if the function is already present
#                             if line.strip().startswith("fn") and (line.strip().split("(")[0]) in g:
#                                 continue
#                             new_gen += line.strip() + "\n"
#                     # If fn main() is present twice, cut off before the second one
#                     g = "fn main()".join(g.split("fn main()")[0:2])
#                     new_gen += g
#                     gen[i] = new_gen
#
#         ### EVALUATION ###
#         results, logs = code_metric.compute(
#             references=references,
#             predictions=generations,
#             language=language,
#             timeout=timeout,
#             num_workers=num_workers,
#         )
#         # Write logs to json
#         with open("logs.json", "w") as f:
#             json.dump(logs, f, indent=4, ensure_ascii=False)
#
#         """Debugging help
#         for i, (gen, ref) in enumerate(zip(generations, references)):
#             import time
#             starttime = time.time()
#             results, log = code_metric.compute(
#                 references=[ref],
#                 predictions=[gen],
#                 language=language,
#                 timeout=timeout,
#             )
#             print("Took: ", time.time() - starttime)
#             with open("errors.txt", "a") as f:
#                 f.write(log[0][0][1]["result"] + "\n")
#             if ("compilation error" in log[0][0][1]["result"]):
#                 print("Result")
#                 print(results)
#                 print("Log")
#                 print(log)
#                 print("Gen")
#                 print(gen[0])
#                 print("Ref")
#                 print(ref)
#         """
#         return results
#
#
# class HumanEvalFixBase(HumanEvalPackGenerative):
#     def get_filename_with_extension(self, input_file):
#         """Returns the synthetic filename for different datasets"""
#         file_name = input_file if input_file is not None else "solution"
#         return file_name + "." + LANGUAGE_TO_EXTENSION[self.DATASET_NAME]
#
#     def get_prompt(self, doc):
#         """Builds the prompt for the LM to generate from."""
#         prompt_base = self.get_prompt_base(doc)
#         instruction = f'Fix bugs in {doc["entry_point"]}.'
#         context = prompt_base + doc["buggy_solution"]
#         if self.with_docs is False:  # Add tests as source of ground truth
#             context += "\n" + doc["test"]
#
#         if self.prompt == "file":
#             file_name = self.get_filename_with_extension(input_file=doc["entry_point"])
#             prompt = f"<file_name>\n{file_name}\n<commit_before>\n{context}\n<commit_msg>\n{instruction}<commit_after>\n{prompt_base}"
#         elif self.prompt == "starcodercommit":
#             prompt = f"<commit_before>{context}<commit_msg>{instruction}<commit_after>{prompt_base}"
#         elif self.prompt == "diff":
#             prompt = f"<commit_before>{context}<commit_msg>{instruction}<commit_after>"
#         elif self.prompt == "diff-carper":
#             prompt = f"<NME> {self.get_filename_with_extension(input_file=doc['entry_point'])}\n"
#             prompt += f"<BEF> {context}\n<MSG> {instruction}\n<DFF>"
#         else:
#             prompt = super().get_prompt(prompt_base, instruction, context)
#         return prompt.strip()
#
#     def postprocess_generation(self, generation, idx):
#         """Defines the postprocessing for a LM generation.
#         :param generation: str
#             code generation from LM
#         :param idx: int
#             index of doc in the dataset to which the generation belongs
#             (not used for Humaneval-Task)
#         """
#         doc = self.get_dataset()[idx]
#         prompt = self.get_prompt(doc)
#         # if self.prompt == "diff-carper":
#         #     # Only remove final stopwords like <MSG>
#         #     generation = self.remove_last_block(generation[len(prompt):].rstrip())
#         #     generation = prompt + generation
#         #     from lm_eval.tasks.custom_metrics.diff_eval import split_diff
#         #     # From https://github.com/CarperAI/OpenELM/blob/e6402a0696096011572152334ccbe049f89c332e/src/openelm/benchmarks/benchmark_bugs.py#L93
#         #     end_of_diff = re.compile("\n[^ +-@]+")
#         #     parsed: dict = split_diff(generation)
#         #     if parsed and all(
#         #             (s in parsed for s in ["name", "file", "message", "diff"])
#         #     ):
#         #         # truncate diff hunk at the first line not starting with " ", "+", "-", or "@"
#         #         diff_hunk: str = end_of_diff.split(parsed["diff"])[0]
#         #         # We apply diff patch loosely:
#         #         #   1. it ignores the line numbers;
#         #         #   2. it ignores invalid lines (not starting with " ",
#         #         #   "+" or "-" and not being "@@ ... @@").
#         #         # https://github.com/CarperAI/OpenELM/blob/e6402a0696096011572152334ccbe049f89c332e/src/openelm/benchmarks/benchmark_bugs.py#L162
#         #         nme_idx: int = diff_hunk.find("<NME>")
#         #         if nme_idx != -1:
#         #             diff_hunk = diff_hunk[:nme_idx]
#         #         return diff_hunk
#         # else:
#         if True:
#             gen = self.remove_last_block(generation[len(prompt):].rstrip())
#             if self.prompt.startswith("diff"):
#                 return gen
#             else:
#                 # Strip on the right to maintain same behavior as with get_prompt
#                 prompt_base = self.get_prompt_base(doc)
#                 return prompt_base.rstrip() + gen
#
#
# class HumanEvalExplainDescribeBase(HumanEvalPack):
#     def get_prompt_encoder(self, doc):
#         """Encoder input for models with Enc-Dec architecture like CodeT5"""
#         assert self.prompt == "instructcodet5p", "Enc-Dec is only tested for InstructCodeT5+"
#         prompt_base = self.get_prompt_base(doc)
#         instruction = f"Provide a concise natural language description of the code using at most {len(doc['docstring'])} characters."
#         context = prompt_base + doc["canonical_solution"]
#
#         return super().get_prompt("", instruction, context)  # No prompt base as not generating
#
#     def get_prompt(self, doc):
#         """Builds the prompt for the LM to generate from."""
#         prompt_base = self.get_prompt_base(doc)
#         instruction = f"Provide a concise natural language description of the code using at most {len(doc['docstring'])} characters."
#         context = prompt_base + doc["canonical_solution"]
#
#         return super().get_prompt("", instruction, context)
#
#     def remove_last_block(self, text):
#         for w in self.stop_words:
#             if w in text:
#                 text = text[:text.find(w)]
#         return text
#
#     def remove_code(self, text, canonical_solution):
#         for line in canonical_solution.split("\n"):
#             line = line.strip()
#             if len(line) > 20 and line in text:
#                 text = text.replace(line, "")
#         return text
#
#     def postprocess_generation(self, generation, idx):
#         """Defines the postprocessing for a LM generation.
#         :param generation: str
#             code generation from LM
#         :param idx: int
#             index of doc in the dataset to which the generation belongs
#             (not used for Humaneval-Task)
#         """
#         doc = self.get_dataset()[idx]
#         prompt = self.get_prompt(doc)
#         docstring_len = len(doc["docstring"])
#         gen = self.remove_last_block(generation[len(prompt):].strip()[:docstring_len]).rstrip()
#         gen = self.remove_code(gen, doc["canonical_solution"])
#         return gen
#
#     def get_reference(self, doc, get_solution=False):
#         return None
#
#     def process_results(self, generations, references):
#         raise ValueError("""ExplainDescribe should be run with `--generation_only`.
#         Once generations are done run ExplainSynthesize with `--load_data_path path/to/generations.json`
#         It will load the explanations, generate from them and evaluate.""")
#
#
# class HumanEvalExplainSynthesizeBase(HumanEvalPackGenerative):
#     def __init__(self, load_data_path=None, **kwargs):
#         assert load_data_path is not None, "load_data_path must be specified to load the descriptions."
#         with open(load_data_path) as fp:
#             self.descriptions = json.load(fp)
#             print(
#                 f"{len(self.descriptions)} descriptions with {len(self.descriptions[0])} description candidates loaded.")
#
#         super().__init__(**kwargs)
#
#     def get_dataset(self):
#         """Returns dataset for the task or an iterable of any object, that get_prompt can handle"""
#         dataset = []
#         for description, sample in zip(self.descriptions, self.dataset["test"]):
#             for description_candidate in description:
#                 dataset.append({"description": description_candidate} | sample)
#         return dataset
#
#     def get_prompt_encoder(self, doc):
#         """Encoder input for models with Enc-Dec architecture like CodeT5"""
#         assert self.prompt == "instructcodet5p", "Enc-Dec is only tested for InstructCodeT5+"
#         prompt_base = ""  # No prompt base as not generating
#         instruction = f"Write functional code in {LANGUAGE_TO_NAME[self.DATASET_NAME]} according to the description."
#         context = doc["description"]
#
#         return super().get_prompt(prompt_base, instruction, context)
#
#     def get_prompt(self, doc):
#         """Builds the prompt for the LM to generate from."""
#         prompt_base = self.get_prompt_base(doc)
#         instruction = f"Write functional code in {LANGUAGE_TO_NAME[self.DATASET_NAME]} according to the description."
#         context = doc["description"]
#
#         return super().get_prompt(prompt_base, instruction, context)
#
#
# class HumanEvalSynthesizeBase(HumanEvalPackGenerative):
#     def get_prompt_encoder(self, doc):
#         """Encoder input for models with Enc-Dec architecture like CodeT5"""
#         assert self.prompt == "instructcodet5p", "Enc-Dec is only tested for InstructCodeT5+"
#         prompt_base = ""  # No prompt base as not generating
#         instruction = doc["instruction"].strip()
#
#         return super().get_prompt(prompt_base, instruction)
#
#     def get_prompt(self, doc):
#         """Builds the prompt for the LM to generate from."""
#         prompt_base = self.get_prompt_base(doc)
#         instruction = doc["instruction"].strip()
#
#         return super().get_prompt(prompt_base, instruction)

if __name__ == '__main__':
    # test the runtime of python and javascript
    code_eval = load("Muennighoff/code_eval_octopack")

    test_cases = ["assert add(2,3)==5"]
    candidates = [["def add(a,b): return a*b", "def add(a, b): return a+b"]]

    pass_at_k, results = code_eval.compute(references=test_cases, predictions=candidates, k=[1, 2], language="python")

    print(pass_at_k, results)

    test_cases = ["console.assert(add(2,3)==5)"]
    candidates = [["function add(a,b) { return a*b; }", "function add(a, b) { return a+b; }"]]

    pass_at_k, results = code_eval.compute(references=test_cases, predictions=candidates, k=[1, 2], language="javascript")

    print(pass_at_k, results)

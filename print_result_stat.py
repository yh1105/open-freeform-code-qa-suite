import os
import yaml
import argparse
from matplotlib import pyplot as plt

def compute_stats(file_path: str):
    with open(file_path, 'r') as f:
        full_results = yaml.load(f, yaml.Loader)
    peritem_full_score = {}
    peritem_get_score = {}
    peritem_freq = {}
    perlang_full_score = {}
    perlang_get_score = {}
    perlang_freq = {}
    perarea_full_score = {}
    perarea_get_score = {}
    perarea_freq = {}
    tot_score = 0.
    full_score = 0.
    
    fields = ['keywords', 'blank_filling', 'unit_test', 'similarity', 'customized']
    
    for case_name, case_report in full_results.items():
        case_full_score = case_report['full_score']
        
        # locate the instance with highest score
        best_score = 0.
        best_response_peritem_full_score = {}
        best_response_peritem_get_score = {}
        for response_report in case_report['detail']:
            now_score = 0.
            response_peritem_full_score = {}
            response_peritem_get_score = {}
            for field in fields:
                if field + '_score' in response_report:
                    now_score += response_report[field + '_score']
                    response_peritem_full_score[field] = response_report[field + '_totscore']
                    response_peritem_get_score[field] = response_report[field + '_score']
            if now_score >= best_score:
                best_score = now_score
                best_response_peritem_full_score = response_peritem_full_score
                best_response_peritem_get_score = response_peritem_get_score
        
        tot_case_score = sum(best_response_peritem_full_score.values())
        for item in best_response_peritem_full_score:
            best_response_peritem_full_score[item] *= case_full_score / tot_case_score
            best_response_peritem_get_score[item] *= case_full_score / tot_case_score
        
        for item in best_response_peritem_full_score:
            if item not in peritem_get_score:
                peritem_get_score[item] = 0.
                peritem_full_score[item] = 0.
                peritem_freq[item] = 0.
            peritem_get_score[item] += best_response_peritem_get_score[item]
            peritem_full_score[item] += best_response_peritem_full_score[item]
            peritem_freq[item] += 1
        
        now_score = case_report['now_score']
        now_lang = case_report['lang']
        now_area = case_report['type']
        
        tot_score += now_score
        full_score += case_report['full_score']
        
        if now_lang not in perlang_get_score:
            perlang_get_score[now_lang] = 0.
            perlang_full_score[now_lang] = 0.
            perlang_freq[now_lang] = 0.
        
        perlang_get_score[now_lang] += now_score
        perlang_full_score[now_lang] += case_full_score
        perlang_freq[now_lang] += 1.
        
        if now_area not in perarea_get_score:
            perarea_get_score[now_area] = 0.
            perarea_full_score[now_area] = 0.
            perarea_freq[now_area] = 0.
        
        perarea_get_score[now_area] += now_score
        perarea_full_score[now_area] += case_full_score
        perarea_freq[now_area] += 1.
        
    langs = list(perlang_get_score.keys())
    areas = list(perarea_get_score.keys())
    
    return {
        'tot_score': tot_score,
        'tot_full_score': full_score,
        'lang': langs,
        'area': areas,
        'field': fields,
        'perarea_freq': perarea_freq,
        'perarea_get_score': perarea_get_score,
        'perarea_full_score': perarea_full_score,
        'perlang_freq': perlang_freq,
        'perlang_get_score': perlang_get_score,
        'perlang_full_score': perlang_full_score,
        'peritem_freq': peritem_freq,
        'peritem_get_score': peritem_get_score,
        'peritem_full_score': peritem_full_score
    }

def tab_gen(stats, cols):
    cols = [''] + sum([[col, ''] for col in cols], []) + ['Full Score', 'Allocation']
    lines = [cols]
    # Tot score
    lines.append(['Overall Score'] + sum([[stat['tot_score'], stat['tot_score'] / stats[0]['tot_full_score']] for stat in stats], []) + [stats[0]['tot_full_score'], ''])
    # Score by Lang
    lang_ranks = sorted(stats[0]['lang'], key=lambda x: stats[0]['perlang_full_score'][x], reverse=True)
    lines += [['Lang: ' + lang] + sum([[stat['perlang_get_score'][lang], stat['perlang_get_score'][lang] / stats[0]['perlang_full_score'][lang]] for stat in stats], []) + [stats[0]['perlang_full_score'][lang], stats[0]['perlang_full_score'][lang] / stats[0]['tot_full_score']] for lang in lang_ranks]
    # Score by Area
    area_ranks = sorted(stats[0]['area'], key=lambda x: stats[0]['perarea_full_score'][x], reverse=True)
    lines += [['Type: ' + area] + sum([[stat['perarea_get_score'][area], stat['perarea_get_score'][area] / stats[0]['perarea_full_score'][area]] for stat in stats], []) + [stats[0]['perarea_full_score'][area], stats[0]['perarea_full_score'][area] / stats[0]['tot_full_score']] for area in area_ranks]
    # Score by Evaluation metric
    item_ranks = sorted(stats[0]['peritem_full_score'].keys(), key=lambda x: stats[0]['peritem_full_score'][x], reverse=True)
    lines += [['Metric: ' + item] + sum([[stat['peritem_get_score'][item], stat['peritem_get_score'][item] / stats[0]['peritem_full_score'][item]] for stat in stats], []) + [stats[0]['peritem_full_score'][item], stats[0]['peritem_full_score'][item] / stats[0]['tot_full_score']] for item in item_ranks]
    return lines

def to_text(tab):
    ncols = len(tab[0])
    max_lens = [0 for _ in range(ncols)]
    for row in tab:
        for j, item in enumerate(row):
            if isinstance(item, str): 
                max_lens[j] = max(max_lens[j], len(item))
            elif isinstance(item, float):
                if j % 2 == 1:
                    row[j] = f'{item:.2f}' 
                else:
                    row[j] = f'{item * 100.:.2f}%'
                max_lens[j] = max(max_lens[j], len(row[j]))
    splitter = '|'.join(['-' * (max_lens[i] + 2) for i in range(ncols)])
    header = '-' * len(splitter)
    contents = []
    for row in tab:
        contents.append('|'.join([row[j].ljust(max_lens[j]+1).rjust(max_lens[j]+2) for j in range(ncols)]))
    return '\n'.join([header, contents[0], splitter] + contents[1:] + [header])

parser = argparse.ArgumentParser()
parser.add_argument('result_yaml_path', type=str)
parser.add_argument('result_table_path', type=str)
parser.add_argument('--model_name', type=str, default='This Model')
if __name__ == '__main__':
    args = parser.parse_args()
    in_path = args.result_yaml_path
    out_path = args.result_table_path
    if os.path.dirname(out_path):
        if not os.path.exists(os.path.dirname(out_path)):
            os.makedirs(os.path.dirname(out_path))
    
    stats = compute_stats(in_path)
    tab = tab_gen([stats], [args.model_name])
    tab_text = to_text(tab)

    with open(out_path, 'w') as f:
        f.write(tab_text)
    print('Write to', out_path)
    print('Final Result:')
    print(tab_text)

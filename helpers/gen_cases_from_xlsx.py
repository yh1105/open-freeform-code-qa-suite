"""
    This helper script parses the prompts from the human annotated spreadsheet
"""

import os
import argparse
import xlrd
import yaml

def search_col(book, colname_row, col_name):
    ret = 0
    while book.cell_value(rowx=colname_row, colx=ret) != '':
        if book.cell_value(rowx=colname_row, colx=ret) == col_name:
            return ret
        ret += 1
    return None

parser = argparse.ArgumentParser()
parser.add_argument('xlsx_file', help='path of the xlsx to decode the cases')
parser.add_argument('--colname_row', help='row number of column names', default=2)
parser.add_argument('--save_path', help='directory to save the parsed cases',
                    default='cases/')
parser.add_argument('--suite_info_file', help='place to store dataset metafile',
                    default='suite_v1.yaml')
parser.add_argument('--id_col', help='column names of internal IDs', default='Internal ID')
parser.add_argument('--type_col', help='column names of type', default='Type/Scenario')
parser.add_argument('--lang_col', help='column names of langauge', default='Language/Area')
parser.add_argument('--prompt_col', help='column names of prompts', default='Paraphrased Question')
parser.add_argument('--removed_col', help='column names of place storing whether to remove or not',
                    default='Removed')
args = parser.parse_args()
if __name__ == '__main__':
    book = xlrd.open_workbook(args.xlsx_file)
    sh = book.sheet_by_index(0)
    internalid_col_idx = search_col(sh, args.colname_row, args.id_col)
    prompt_col_idx = search_col(sh, args.colname_row, args.prompt_col)
    removed_col_idx = search_col(sh, args.colname_row, args.removed_col)
    type_col_idx = search_col(sh, args.colname_row, args.type_col)
    lang_col_idx = search_col(sh, args.colname_row, args.lang_col)
    assert internalid_col_idx is not None and prompt_col_idx is not None and removed_col_idx is not None
    cur_row = args.colname_row + 1
    case_list = []
    while cur_row < sh.nrows and sh.cell_value(rowx=cur_row, colx=internalid_col_idx) != '':
        if sh.cell_value(rowx=cur_row, colx=removed_col_idx) == '':
            # no skip at here
            prompt_text = sh.cell_value(rowx=cur_row, colx=prompt_col_idx)
            case_id = str(int(sh.cell_value(rowx=cur_row, colx=internalid_col_idx)))
            case_type = str(sh.cell_value(rowx=cur_row, colx=type_col_idx)).strip().lower()
            case_lang = str(sh.cell_value(rowx=cur_row, colx=lang_col_idx)).strip().lower()
            prompt_fname = os.path.join(args.save_path, f'prompt_{case_id}.txt')
            eval_meta_fname = os.path.join(args.save_path, f'eval_{case_id}.yaml')

            if len(os.path.dirname(prompt_fname)) > 0:
                if not os.path.exists(os.path.dirname(prompt_fname)):
                    os.makedirs(os.path.dirname(prompt_fname))
            with open(prompt_fname, 'w') as f:
                f.write(prompt_text)
            with open(eval_meta_fname, 'w') as f:
                f.write(
f"""id: {case_id}
prompt_path: {os.path.basename(prompt_fname)}
type: {case_type}
lang: {case_lang}
grading: {{}}
""")
            case_list.append(eval_meta_fname)
        cur_row += 1

    if len(os.path.dirname(args.suite_info_file)) > 0:
        if not os.path.exists(os.path.dirname(args.suite_info_file)):
            os.makedirs(os.path.dirname(args.suite_info_file))
    with open(args.suite_info_file, 'w') as f:
        yaml.dump({'cases': case_list,
                        'version': os.path.basename(args.suite_info_file),
                        'full_score_per_question': 1.,
                        'attempt_reduce_mode': 'avg'}, f)
    print(f'{len(case_list)} cases parsed.')


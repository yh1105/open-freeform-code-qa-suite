import os
import os.path as osp
import yaml
import shutil

if __name__ == '__main__':
    with open('suite_v2.0.0.yaml', 'r') as f:
        suite_data = yaml.load(f, Loader=yaml.Loader)
    cases_paths = suite_data['cases']
    # extract new prompt paths
    cases_paths = [case_path for case_path in cases_paths if 333 <= int(case_path.split('-')[-1].split('.')[0]) <= 469]
    # update them
    for case_path in cases_paths:
        with open(case_path, 'r') as f:
            case_txt = f.read()
        orig_id = int(case_path.split('-')[-1].split('.')[0]) + 1
        new_id = case_path.split('_')[-1].split('.')[0]
        orig_prompt_path = f'prompt_{orig_id}.txt'
        new_prompt_path = f'prompt_{new_id}.txt'
        assert case_txt.count(orig_prompt_path) >= 0
        assert case_txt.count(f'id: {orig_id}') >= 0
        case_new_txt = case_txt.replace(orig_prompt_path, new_prompt_path)
        case_new_txt = case_new_txt.replace(f'id: {orig_id}', f'id: {new_id}')
        with open(case_path, 'w') as f:
            f.write(case_new_txt)
        print(case_path)
    # update responses
    for resp_dir in ['responses/gpt-3.5-turbo_0.2_0.9_10_suite_v2_part_2', 'responses/gpt-4_0.2_0.9_10_suite_v2_part_2']:
        for case_path in cases_paths:
            orig_id = int(case_path.split('-')[-1].split('.')[0]) + 1
            new_id = case_path.split('_')[-1].split('.')[0]
            for j in range(10): # 10 responses for each case
                assert osp.exists(osp.join(resp_dir, f'eval_{orig_id}_{j}.txt'))
                shutil.copy(osp.join(resp_dir, f'eval_{orig_id}_{j}.txt'), osp.join(resp_dir, f'eval_{new_id}_{j}.txt'))
        with open(osp.join(resp_dir, 'params.yaml')) as f:
            params = f.read()
        for case_path in cases_paths:
            orig_id = int(case_path.split('-')[-1].split('.')[0]) + 1
            new_id = case_path.split('_')[-1].split('.')[0]
            params = params.replace(str(orig_id), new_id)
        with open(osp.join(resp_dir, 'new_params.yaml'), 'w') as f:
            f.write(params)
    
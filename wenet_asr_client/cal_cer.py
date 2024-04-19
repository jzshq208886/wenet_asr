import os
import pandas as pd

from lib.tester import cer_levenshtein

name_map = {
    '075589939388-20230120105407-szBZ202301200044':'2_1',
    '075589939388-20230120144717-szBZ202301200064':'2_2',
    '075589939388-20230208174118-szBZ202302080210':'2_3',
    '075589939388-20230209142552-szBZ202302090102':'2_4',
    '075589939388-20230210115147-szBZ202302100143':'2_5',
    '1702257074_2632_70_0_1':'3_1',
    '1702257572_14763_56_0_1':'3_2',
    '1702262200_10509_67_0_1':'3_3',
    '1702434389_2340_152_0_1':'3_4',
    '1702435068_20113_149_0_1':'3_5',
    '1702435792_16578_159_0_1':'3_6',
}

def cal_folder(dir, df, hotwords=True, transcript_dir: str = None):
    if transcript_dir is None:
        transcript_dir = 'transcript' if hotwords else 'transcript_without_hotwords'
    for filename in os.listdir(os.path.join(transcript_dir, dir)):
        print(f'current: {filename}')
        with open(os.path.join(transcript_dir, dir, filename), 'r') as f:
            s1 = f.read()
        with open(os.path.join('audio', dir, filename), 'r') as f:
            s2 = f.read()
        
        filename = filename.strip('.txt')
        index = name_map[filename]
        df.loc[index, 'filename'] = filename
        df.loc[index, 'text_length'] = len(s2)
        if hotwords:
            df.loc[index, 'transcript_length'] = len(s1)
            _, df.loc[index, 'cer'], (insert, delete, replace) = cer_levenshtein(s1, s2)
            df.loc[index, 'correct_length'] = insert + replace
        else:
            df.loc[index, 'transcript_length_without_hotwords'] = len(s1)
            _, df.loc[index, 'cer_without_hotwords'], (insert, delete, replace) = cer_levenshtein(s1, s2)
            df.loc[index, 'correct_length_without_hotwords'] = len(s1) - delete - replace
        print(df)


if __name__ == '__main__':
    save_file = 'cer_without_hotwords.csv'
    transcript_dir = 'transcript_without_hotwords'

    if not os.path.exists(save_file):
        # 创建索引
        index = []
        for i in range(2, 4):
            for j in range(1, 7 if i == 3 else 6):
                index.append(f"{i}_{j}")
        row = len(index)
        data = {
            'filename': [None] * row,
            'text_length': [None] * row,
            'transcript_length': [None] * row,
            'correct_length': [None] * row,
            'cer': [None] * row,
            # 'transcript_length_without_hotwords': [None] * row,
            # 'correct_length_without_hotwords': [None] * row,
            # 'cer_without_hotwords': [None] * row,
        }
        df = pd.DataFrame(data, index=index)
    else:
        df = pd.read_csv(save_file, index_col=0)

    cal_folder('samples2', df, transcript_dir=transcript_dir)
    cal_folder('samples3', df, transcript_dir=transcript_dir)
    # cal_folder('samples2', df, hotwords=False)
    # cal_folder('samples3', df, hotwords=False)

    df.to_csv(save_file)



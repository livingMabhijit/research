import pandas as pd


# import my_app_v3


def change_df(x,idx):
    my_df = pd.read_csv('/Users/apple/Documents/work_DFA/Labelizer/main_file_error_v4_windx_2k.csv',sep = '\t')
    my_df['label'][idx] = x
    # my_df['pred'][idx] = x
    my_df.to_csv('/Users/apple/Documents/work_DFA/Labelizer/main_file_error_v4_windx_2k.csv',sep = '\t',index=False)
    # idx =  my_app_v3.first_page(idx = idx+1)


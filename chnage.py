import pandas as pd


def change_df(x,idx):
    print('pred_classification_code_next '+ str(x) )
    my_df = pd.read_csv('main_file_error_v4_windx_2k.csv',sep = '\t')
    my_df['label'][idx] = x
    # my_df['pred'][idx] = x
    my_df.to_csv('main_file_error_v4_windx_2k.csv',sep = '\t',index=False)
    
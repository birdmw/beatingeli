import os, sys
import pandas as pd

def aggregate(data_folder = 'data' + os.sep):
    only_files = [data_folder + f for f in os.listdir(data_folder) if os.path.isfile(os.path.join(data_folder, f))]
    df_list = []
    for file_path in only_files:
        with open(file_path, 'rb') as f:
            df = pd.read_csv(f)
            df_list.append(df)
    df = pd.concat(df_list)
    df = df.drop_duplicates()
    df.to_csv(data_folder + 'aggregation.csv', index=False)
    only_files = [of for of in only_files if 'agg' not in of.lower()]
    print only_files
    
if __name__ == '__main__':
    aggregate()

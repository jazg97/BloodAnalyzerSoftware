from utils import *
import numpy as np

root_dir = os.path.dirname(os.path.realpath(__file__))

file = os.path.join(root_dir, 'tests', 'test4.csv')

dataframe = pd.read_csv(file)

columns = dataframe.columns

selected = [column for column in columns if ('raw' in column.lower() or 'valid' in column.lower())]

counts = [np.unique(dataframe[column], return_counts=True) for column in selected]

#Checking for weird raw values or valid == 0

invalid_raw = [(column, np.unique(dataframe[column], return_counts=True)) for column in selected if 'raw' in column.lower()]

#Obtaining the columns where the invalid string appears
invalid_occ = [column for (column, counts) in invalid_raw if '--.--' in counts[0]]

print(invalid_occ)

#Finding the indices of the invalid rows

invalid_rows = [np.where(dataframe[column] == '--.--') for column in invalid_occ]

print(invalid_rows)

#Its always the same files, so I'll just grab the first column

indices = dataframe[dataframe[invalid_occ[0]] == '--.--'].index

dataframe.drop(indices, inplace=True)

#Dropping rows without a patient id

unique_id = np.unique(dataframe['FIELD_SID_PATIENT_ID'].values, return_counts=True)

print(unique_id[0])
print(dataframe[dataframe['FIELD_SID_PATIENT_ID'] == ''].index)
#There is no longer any row without a patient id

#Removing columns with just NaN, None or '\n' values

df = dataframe.copy()

for col in df:
    unique = df[col].unique()
    if df[col].isnull().all() or df[col].isna().all() or (len(unique) == 1 and unique[0] == '\n'):
        df = df.drop(col, axis=1)

print('Number of removed columns:', len(set(list(dataframe)) - set(list(df))))


out_file = os.path.join(root_dir, 'tests', 'cleaned_data.csv')
df.to_csv(out_file)

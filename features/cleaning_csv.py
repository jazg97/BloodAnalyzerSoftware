from utils import *
import numpy as np

root_dir = '\\'.join(os.path.dirname(os.path.realpath(__file__)).split('\\')[:-1])

file = os.path.join(root_dir, 'tests', 'test4.csv')

dataframe = pd.read_csv(file)

og = dataframe.copy()

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

#invalid_ids = dataframe[dataframe['FIELD_SID_OWNER_LASTNAME'].str.isnumeric() == True].index
#dataframe.drop(invalid_ids, inplace=True)
#Removing columns with just NaN, None or '\n' values

dataframe.loc[dataframe['FIELD_SID_OWNER_LASTNAME'].isnull(), 'FIELD_SID_OWNER_LASTNAME'] = 'GUEZGUEZ'

dataframe.loc[dataframe['FIELD_SID_OWNER_LASTNAME'].str.isnumeric(), 'FIELD_SID_OWNER_LASTNAME'] = 'GUEZGUEZ'

dataframe.loc[(dataframe['FIELD_SID_OWNER_LASTNAME'] !='SCHUPPAN') & (dataframe['FIELD_SID_OWNER_LASTNAME'] !='GUEZGUEZ'), 'FIELD_SID_ANIMAL_NAME'] =  dataframe.loc[(dataframe['FIELD_SID_OWNER_LASTNAME'] !='SCHUPPAN') & (dataframe['FIELD_SID_OWNER_LASTNAME'] !='GUEZGUEZ'), 'FIELD_SID_OWNER_LASTNAME']

dataframe.loc[(dataframe['FIELD_SID_OWNER_LASTNAME'] !='SCHUPPAN') & (dataframe['FIELD_SID_OWNER_LASTNAME'] !='GUEZGUEZ'), 'FIELD_SID_OWNER_LASTNAME'] = 'GUEZGUEZ'

dataframe.loc[dataframe['FIELD_SID_ANIMAL_NAME'].isnull(), 'FIELD_SID_ANIMAL_NAME'] = 'BLOOD'

dataframe.loc[(dataframe['FIELD_SID_ANIMAL_NAME'] == 'SPL') | (dataframe['FIELD_SID_ANIMAL_NAME'] == 'SP') , 'FIELD_SID_ANIMAL_NAME'] = 'SPLEEN'

df = dataframe.copy()

for col in df:
    unique = df[col].unique()
    if df[col].isnull().all() or df[col].isna().all() or (len(unique) == 1 and unique[0] == '\n') or ('flag' in col.lower() and 'histogram' not in col.lower()) or '_Id' in col or 'Valid' in col or 'Unit' in col:
        df = df.drop(col, axis=1)

dr_columns = pd.read_csv(os.path.join(root_dir, 'tests', 'columns_to_drop.csv'))

#Deleting specific columns
df = df.drop('ExpiredReagent', axis=1)
df = df.drop('OPERATOR', axis=1)
df = df.drop('PACKET_TYPE', axis = 1)
df = df.drop('Unnamed: 0', axis = 1)
df = df.drop('InvalidAlarmStartup',axis=1)
df = df.drop('QCFailed', axis=1)
df = df.drop('InvalidQC', axis = 1)
df = df.drop('SAMPLING_MODE', axis = 1)
df = df.drop('Archived', axis = 1)
df = df.drop('EOS#_EOS', axis = 1)
df = df.drop(dr_columns.columns, axis=1)
df = df.drop('Unnamed: 29', axis = 1)

df['FIELD_SID_PATIENT_LAST_NAME'] = ''

print('Number of removed columns:', len(set(list(og)) - set(list(df))))

out_file = os.path.join(root_dir, 'tests', 'cleaned_data.csv')
df.to_csv(out_file)

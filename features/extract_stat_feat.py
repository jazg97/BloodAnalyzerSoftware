from utils import *
pd.options.mode.chained_assignment = None
directory = '\\'.join(root_dir.split('\\')[:-1])

excel = pd.ExcelFile('C://Users//jazg2//Downloads//exemplary_meta.xlsx')

metadata = excel.parse()

dataframe = pd.read_csv(os.path.join(directory,'tests','cleaned_data3.csv'))

patient_ids = [str(animal_id) for animal_id in metadata['animal_id'].values]

print(patient_ids)

selected_df = dataframe[(dataframe['FIELD_SID_PATIENT_ID'].str.contains('|'.join(patient_ids), case=True))]

for col in metadata.columns[1:]:
    uniques = metadata[col].unique()
    selected_df[col]=''
    for idx, patient in enumerate(patient_ids):
        #a = selected_df['FIELD_SID_PATIENT_ID'].str.contains(patient).index
        selected_df.loc[selected_df['FIELD_SID_PATIENT_ID'].str.contains(patient), col]= metadata[metadata['animal_id']==int(patient)][col].values[0]
    #selected_df.assign(col=lambda x: )
    #print(uniques)

#selected_df.to_csv(os.path.join(directory, 'tests', 'selected_w_meta.csv'))

features = ['RBC_Value', 'MPV_Value','LYM%_Value','WBC_Value']

test = 'BLOOD'

filt = 'Treatment'

uniques = selected_df[filt].unique()

figure = plt.figure()
filtered_df = selected_df[selected_df['FIELD_SID_ANIMAL_NAME']==test]

idxs = [np.where(filtered_df[filt].values == unique) for unique in uniques]

for idx,feature in enumerate(features):
    axis = figure.add_subplot(2,int(np.ceil(len(features)/2)),idx+1)
    for idx, group_idxs in enumerate(idxs):
        series = filtered_df[feature].values[group_idxs]
        axis.bar(uniques[idx], np.mean(series), yerr=np.std(series), align='center', alpha=0.5, ecolor='black', capsize=10)
        axis.set_xlabel(filt)
        axis.set_ylabel(feature)

plt.show()
    

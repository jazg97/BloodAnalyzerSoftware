from utils import *
plt.rcParams['axes.xmargin'] = 0

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

features = ['EOS%_Value', 'EOS#_Value', 'GRA%_Value', 'GRA#_Value', 'LYM%_Value', 'LYM#_Value', 'MON%_Value', 'MON#_Value', 'WBC_Value']#['MPV_Value','PLT_Value']#['RBC_Value', 'MPV_Value','LYM%_Value','WBC_Value']

test = 'BLOOD'

filt = ['Genotype']#'Treatment']#,

if len(filt)>1:
    column = '-'.join(filt)
    selected_df[column] = selected_df[filt].apply(lambda x: '_'.join(x), axis=1)#selected_df[filt[0]] + '_' + selected_df[filt[1]]
    uniques = selected_df[column].unique()
else:
    column = filt[0]
    uniques = selected_df[column].unique()

figure = plt.figure(figsize=(12,8), constrained_layout=True)
filtered_df = selected_df[selected_df['FIELD_SID_ANIMAL_NAME']==test]
idxs = [np.where(filtered_df[column].values == unique) for unique in uniques]

wd = 0.3
x_pos = 0.5

for idx,feature in enumerate(features):
    axis = figure.add_subplot(3,3,idx+1)
    for idy, group_idxs in enumerate(idxs):
        series = filtered_df[feature].values[group_idxs]
        axis.bar(x_pos+idy*wd, np.mean(series), width=wd, yerr=np.std(series), align='center', alpha=0.5, ecolor='black', capsize=10, label=uniques[idy])
        #axis.set_xlabel('&'.join(filt))
        axis.set_ylabel(feature)
        #axis.legend()

handles, labels = axis.get_legend_handles_labels()
figure.suptitle('&'.join(filt))
figure.legend(handles, labels, loc='upper left')
plt.show()

figure2 = plt.figure(figsize=(12,8), constrained_layout=True)

unique_dates = filtered_df['ANALYSIS_DATE'].apply(lambda x: x.split(' ')[0]).unique()

means = []
stds  = []

for idx, date in enumerate(unique_dates):
    selected_perdate = filtered_df[filtered_df['ANALYSIS_DATE'].str.contains(date)]
    idxs = [np.where(selected_perdate[column].values == unique) for unique in uniques]
    mean_perdate = []
    std_perdate = []
    for idy, group_idys in enumerate(idxs):
        mean_pergroup = np.mean(selected_perdate[features].values[group_idys], axis=0)
        std_pergroup = np.std(selected_perdate[features].values[group_idys],axis=0)
        mean_perdate.append(mean_pergroup)
        std_perdate.append(std_pergroup)
    means.append(np.vstack(mean_perdate))
    stds.append(np.vstack(std_perdate))
    

means = np.array(means)
stds  = np.array(stds)

wd = 0.5
x_pos = np.arange(1, 2*len(unique_dates), 2)

for idy, feature in enumerate(features):
    axis = figure2.add_subplot(3,3,idy+1)#(2,int(np.ceil(len(features)/2)),idy+1)
    [axis.bar(x_pos+i*wd, means[:,i,idy], yerr=stds[:,i,idy], width=wd, alpha=0.5, ecolor='black', capsize=6, label=uniques[i]) for i in range(means.shape[1])]
    axis.set_ylabel(feature)
    #axis.set_xlabel('Date')
    axis.set_xticks(x_pos+wd, unique_dates)
    #axis.legend()
handles, labels = axis.get_legend_handles_labels()
figure2.suptitle('WBC FAMILY & METADATA')
figure2.autofmt_xdate()
figure2.legend(handles, labels, loc='upper left')
#figure2.tight_layout()
plt.show()

import xml.etree.ElementTree as et
import pandas as pd
import os
import matplotlib.pyplot as plt
import sys
import numpy as np
from datetime import datetime
import time

root_dir = os.path.dirname(os.path.realpath(__file__))

#Recursive solution ---> automatic subnode detection and formatting
def recursive_parsing(node, identifier='o', attrib_list=[], val_list=[], idef=''):
    for child in node:
        #This conditional adds the identifier of the parent node, to easily differentiate
        #between equally named parameters, such as HighLimit, LowLimit, etc.
        if child.tag != identifier:

            #if child.attrib['n'] == 'FIELD_SID_ANIMAL_NAME' and child.test == '':
            #    child.text = 'BLOOD'
            if idef!='':
                try:
                    child.attrib['n'] = idef['n']+'_'+child.attrib['n'] 
                except:
                    pass
            attrib_list.append(child.attrib)
            val_list.append(child.text)
        else:
            attrib_list.append(child.attrib)
            val_list.append(child.text)
            recursive_parsing(child, 'o', attrib_list, val_list, child.attrib)

    return attrib_list, val_list

def parse_multiple_files(directory, progress_bar=None):
    dict_list = []
    for idx, file in enumerate(os.listdir(directory)):
        if progress_bar is not None:
            progress_bar.setValue(idx+1)
        tree = et.parse(os.path.join(directory, file))
        root = tree.getroot()
        attrib_list = []
        val_list = []
        attrib_list, val_list = recursive_parsing(root, 'o', attrib_list, val_list)
        previous_string = ''
        unit = dict()

        for idy, val in enumerate(attrib_list):
            string=''
            try:
                hist=False
                thresh=False
                for idz,key in enumerate(val.keys()):
                    if idz>=1:
                        string+='_'+val[key]
                    else:
                        string+=val[key]
                    if val[key] == 'HISTOGRAM':
                        hist=True
                    if val[key] == 'THRESHOLDS':
                        thresh=True
                if hist and 'Flags':
                    string = previous_string.split('_')[0]+'_'+string
                    unit[string] = val_list[idy+1]
                elif thresh:
                    string = previous_string.split('_')[0]+'_'+string
                    out = []
                    n=1
                    while True:
                        if not attrib_list[idy+n]:
                            out.append(val_list[idy+n])
                        else:
                            break
                        n+=1
                    unit[string] = (';').join(out)
                elif 'Flags' in string and attrib_list[idy]['n'].lower()!='flags':
                    pass
                else:
                    unit[string] = val_list[idy]
                    string+=': '+val_list[idy]
                previous_string = string
            except:
                pass
        dict_list.append(unit)
    out_df = pd.DataFrame.from_records(dict_list)
    out_df = out_df.dropna(how='all', axis=1)
    return out_df

def clean_dataframe(dataframe):
    copy = dataframe.copy()
    
    undesired_columns = ['ExpiredReagent', 'OPERATOR', 'PACKET_TYPE', 'QCFailed', 'SAMPLING_MODE', 'Archived', 'EOS#_EOS', 'ANALYSIS_TYPE', 'ANALYZER_NO', 'FIELD_SID_PATIENT_SEX', 'FIELD_SID_SAMPLE_TYPE', 'FIELD_SID_SESSIONID', 'VET_VERSION', 'XBDrift', 'CONCENTRATED_PLATELET']
    dataframe = dataframe.drop('InvalidAlarmStartup', axis=1)
    dataframe = dataframe.drop('InvalidQC', axis=1)
    columns = dataframe.columns
    selected = [column for column in columns if ('raw' in column.lower() or 'valid' in column.lower())]
    
    counts = [np.unique(dataframe[column], return_counts=True) for column in selected]
    invalid_raw = [(column, np.unique(dataframe[column], return_counts=True)) for column in selected if 'raw' in column.lower()]
    invalid_occ = [column for (column, counts) in invalid_raw if '--.--' in counts[0]]
    invalid_rows = [np.where(dataframe[column] == '--.--') for column in invalid_occ]
    try:
        indices = dataframe[dataframe[invalid_occ[0]] == '--.--'].index
        dataframe.drop(indices, inplace=True)
    except:
        pass
    dataframe.loc[dataframe['FIELD_SID_OWNER_LASTNAME'].isnull(), 'FIELD_SID_OWNER_LASTNAME'] = 'GUEZGUEZ'
    dataframe.loc[dataframe['FIELD_SID_OWNER_LASTNAME'].str.isnumeric(), 'FIELD_SID_OWNER_LASTNAME'] = 'GUEZGUEZ'
    dataframe.loc[(dataframe['FIELD_SID_OWNER_LASTNAME'] !='SCHUPPAN') & (dataframe['FIELD_SID_OWNER_LASTNAME'] !='GUEZGUEZ'), 'FIELD_SID_ANIMAL_NAME'] =  dataframe.loc[(dataframe['FIELD_SID_OWNER_LASTNAME'] !='SCHUPPAN') & (dataframe['FIELD_SID_OWNER_LASTNAME'] !='GUEZGUEZ'), 'FIELD_SID_OWNER_LASTNAME']
    dataframe.loc[(dataframe['FIELD_SID_OWNER_LASTNAME'] !='SCHUPPAN') & (dataframe['FIELD_SID_OWNER_LASTNAME'] !='GUEZGUEZ'), 'FIELD_SID_OWNER_LASTNAME'] = 'GUEZGUEZ'
    dataframe.loc[dataframe['FIELD_SID_ANIMAL_NAME'].isnull(), 'FIELD_SID_ANIMAL_NAME'] = 'BLOOD'
    dataframe.loc[(dataframe['FIELD_SID_ANIMAL_NAME'] == 'SPL') | (dataframe['FIELD_SID_ANIMAL_NAME'] == 'SP') , 'FIELD_SID_ANIMAL_NAME'] = 'SPLEEN'
    try:
        dataframe.loc[dataframe['FIELD_SID_PATIENT_ID'].str.contains('|'.join(['SPL','SP']), case=True), 'FIELD_SID_ANIMAL_NAME'] = 'SPLEEN'
    except:
        pass
    df = dataframe.copy()
    for col in df:
        unique = df[col].unique()
        if df[col].isnull().all() or df[col].isna().all() or (len(unique) == 1 and unique[0] == '\n') or ('flag' in col.lower() and 'histogram' not in col.lower()) or '_Id' in col or 'Valid' in col or 'Raw' in col or 'Unit' in col:
            df = df.drop(col, axis=1)
    
    df = df.drop(undesired_columns, axis=1)
    df['FIELD_SID_PATIENT_LAST_NAME'] = ''

    return df

def plot_rawdata(patient_id, feature, dataframe):
    patient_df = dataframe[dataframe['FIELD_SID_PATIENT_ID']==patient_id]
    data_points = patient_df[feature]
    dates = dataframe['ANALYSIS_DATE'][data_points.index]
    dates = [date.split(' ')[0] for date in dates.values]
    limits = [dataframe[feature.split('_')[0]+'_'+limit][data_points.index].values[0] for limit in ['LowLimit', 'HighLimit']]
    plt.figure()
    plt.plot(dates, data_points, label=feature, ls=':')
    plt.xlabel('Date')
    plt.ylabel(feature)
    plt.title('Patient '+patient_id)
    plt.axhline(y = limits[0], label='LowLimit', ls='-.', c='r')
    plt.axhline(y = limits[1], label='HighLimit', ls='-.', c='r')
    plt.legend()
    #plt.savefig(os.path.join(root_dir,'figures',patient_id+'_'+feature+'.png'), dpi=300)
    plt.show()

def subplot_feature(patient_ids, feature, canvas, axis, dataframe):
    for patient in patients_ids:
        print(patient)
        patient_df = dataframe[dataframe['FIELD_SID_PATIENT_ID']==patient]
        datapoints = patient_df[feature]
        print(datapoints)
        dates = dataframe['ANALYSIS_DATE'][datapoints.index]
        dates = [date.split(' ')[0] for date in dates.values]
        limits = [dataframe[feature.split('_')[0]+'_'+limit][datapoints.index].values[0] for limit in ['LowLimit', 'HighLimit']]
        axis.plot(dates, datapoints, label=patient, ls=':')
        axis.axhline(y = limits[0], label='LowLimit', ls='-.', c='r')
        axis.axhline(y = limits[1], label='HighLimit', ls='-.', c='r')
    axis.legend()
    canvas.draw()
    


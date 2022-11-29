import xml.etree.ElementTree as et
import pandas as pd
import os
import matplotlib.pyplot as plt
import sys
import numpy as np

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
    plt.savefig(os.path.join(root_dir,'figures',patient_id+'_'+feature+'.png'), dpi=300)
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
    


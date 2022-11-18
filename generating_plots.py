from utils import *
import numpy as np
import matplotlib.pyplot as plt

root_dir = os.path.dirname(os.path.realpath(__file__))

file = os.path.join(root_dir, 'tests', 'cleaned_data.csv')

dataframe = pd.read_csv(file)

unique_id = np.unique(dataframe['FIELD_SID_PATIENT_ID'].values, return_counts=True)

print(unique_id[0])
print(unique_id[1])

test_id = '1026'
test_feature = 'HCT_Raw'

plot_rawdata(test_id, test_feature, dataframe)

#############################################################################

test_id = unique_id[0][19]
test_feature = 'HCT_Raw'

plot_rawdata(test_id, test_feature, dataframe)

test_feature = 'GRA#_Raw'

plot_rawdata(test_id, test_feature, dataframe)

#############################################################################

test_id = '1326'

plot_rawdata(test_id, test_feature, dataframe)

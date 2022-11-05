import xml.etree.ElementTree as et
import pandas as pd
from IPython.display import display
import os

root_dir = os.path.dirname(os.path.realpath(__file__))

#1) Parsing the xml file through the ElementTree parse function
filename = '20211027165438.xml'
tree = et.parse(os.path.join(root_dir,filename))

#2) Getting parent tag of xml file
root = tree.getroot()

#Print root of xml file (tag, memory location)
print(root)

#Print the attributes of the root tag of the xml file
print(root.attrib)

#Print the attributes of the first tag from the parent
print(root[0].attrib)
#Print the values contained in the first tag
print(root[0].text)
print()
#Print all the children nodes of xml file

#Recursive solution ---> automatic subnode detection and formatting

def recursive_parsing(node, identifier='o', attrib_list=[], val_list=[], idef=''):
    for child in node:
        #This conditional adds the identifier of the parent node, to easily differentiate
        #between equally named parameters, such as HighLimit, LowLimit, etc.
        if child.tag != identifier:
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

attrib_list = []
val_list = []

#Example of recursive parsing with xml file
attrib_list, val_list = recursive_parsing(root, 'o', attrib_list, val_list)

#Generating a pandas dataframe to convert xml file to tabular data
df = pd.DataFrame()

print()
for idx, val in enumerate(attrib_list):
    string= ''
    try:
        hist=False
        thresh = False
        for idy,key in enumerate(val.keys()):
            if idy>=1:
                string+='_'+val[key]
            else:
                string+=val[key]
            if val[key] == 'HISTOGRAM':
                hist = True
            if val[key] == 'THRESHOLDS':
                thresh = True
        #data = pd.DataFrame({string: val_list[idx]}, index = [0])
        if hist == True or thresh == True:
            df[string] = [val_list[idx+1]]
        else:
            df[string] = [val_list[idx]]
        #df[string] = val_list[idx]
        string+=': '+val_list[idx]
    except:
        pass
    print(string)

out_file = os.path.join(root_dir, 'test.csv')
df.to_csv(out_file)

import xml.etree.ElementTree as et
import pandas as pd
from IPython.display import display
import os

root_dir = os.path.dirname(os.path.realpath(__file__))

#1) Parsing the xml file through the ElementTree parse function
#filename = '20211027165438.xml'
filenames = ['20211027165438.xml', '20221031134832.xml']
tree = et.parse(os.path.join(('\\').join(root_dir.split('\\')[:-1]),'data',filenames[0]))

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
for file in filename:
    tree = et.parse(os.path.join(root_dir,file))
    root = tree.getroot()
    attrib_list, val_list = recursive_parsing(root, 'o', attrib_list, val_list)
    previous_string = ''
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
            if hist:
                #We add an identifier to each histogram, to avoid rewriting on the same column
                string = previous_string.split('_')[0]+'_'+string
                df[string] = [val_list[idx+1]]
            elif thresh:
                #We do the same as the previous conditional to each threshold field
                string = previous_string.split('_')[0]+'_'+string
                out = []
                n = 1
                #Temporary way to solve this, it would be better if its recognized in the
                #recursive_parsing function
                while True:
                    if not attrib_list[idx+n]:
                        out.append(val_list[idx+n])
                    else:
                        break
                    n+=1
                df[string] = [(';').join(out)]
            elif 'Flags' in string and attrib_list[idx]['n'].lower() != 'flags':
                #A no so elegant way to solve the issue (temporary)
                string = attrib_list[idx-2]['n'].split('_')[0]+'_'+string
                df[string] = [val_list[idx]]
            else:
                df[string] = [val_list[idx]]
            #df[string] = val_list[idx]
            string+=': '+val_list[idx]
            previous_string = string
        except:
            pass
        print(string)

#out_file = os.path.join(root_dir, 'test2.csv')
#df.to_csv(out_file)

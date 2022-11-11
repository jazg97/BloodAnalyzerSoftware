import xml.etree.ElementTree as et
import pandas as pd
import os

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


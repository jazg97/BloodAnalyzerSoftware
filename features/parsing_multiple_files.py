from utils import *

#1) Parsing the xml file through the ElementTree parse function
#filename = '20211027165438.xml'

directory = sys.argv[-2]

output_name = sys.argv[-1]

#Example directory 'C:\\Users\\jazg2\\Downloads\\ar-105EVOH17880-results-20221031135054'

filenames = os.listdir(directory)

export_df = pd.DataFrame()

test_files = np.random.randint(0, len(filenames)-1, 10, dtype=int)

index = []
n = 0
for loc, file in enumerate(filenames):
    tree = et.parse(os.path.join(directory,file))
    root = tree.getroot()
    attrib_list = []
    val_list = []
    attrib_list, val_list = recursive_parsing(root, 'o', attrib_list, val_list)
    df = pd.DataFrame()
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
            if hist and 'Flags':
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
                #string = attrib_list[idx-2]['n'].split('_')[0]+'_'+string
                #df[string] = [val_list[idx]]
                pass
            else:
                df[string] = [val_list[idx]]
                #df[string] = val_list[idx]
                string+=': '+val_list[idx]
            previous_string = string
        except:
            pass
        if np.in1d(loc, test_files)[0]:
            print(string)
    export_df = export_df.append(df)
    
        #n+=1

#export_df.index = index
export_df.dropna(how='all', axis=1)
out_file = os.path.join('\\'.join(root_dir.split('\\')[:-1]), 'tests', output_name)
export_df.to_csv(out_file)

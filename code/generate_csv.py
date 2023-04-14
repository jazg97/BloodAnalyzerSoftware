from utils import *

directory = sys.argv[-2]

output_name = sys.argv[-1]

filenames = os.listdir(directory)

raw_df = parse_multiple_files(directory)

clean_df = clean_dataframe(raw_df)

#out_file = os.path.join('\\'.join(root_dir.split('\\')[:-1]), 'tests', output_name)

clean_df.to_csv(output_name)

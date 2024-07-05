def ndbc_sync(folder_path):
    
    """
    Concatenates multiple NDBC "standard meteorological data" files into a single Pandas dataframe
    
    Args:
    folder_path (str): path to a folder of multiple NDBC Historical "standard meteorological data" files
    
    Returns:
    allData (pd.DataFrame): dataframe of all compiled records
    
    """

    
    import matplotlib.pyplot as plt
    from datetime import datetime
    import pandas as pd
    import numpy as np
    import glob
    import os


    #Create list of files to open.
    files = glob.glob(folder_path)
    print('reading files:',files)

    #Create a dictionary for all data
    my_dataframes = dict()
    for file in files:
        
        #read file as a dataframe within dictionary
        file_name = os.path.basename(file).replace(".txt", "") 
        my_dataframes[file_name] = pd.read_csv(file,delim_whitespace=True,low_memory=False)
        
        
        #SYNC CONVENTIONS
        
        # mid 1980s to late 1990s era
        if 'YY' in my_dataframes[file_name].columns:
            my_dataframes[file_name]['datetime']=pd.to_datetime(dict(year=(my_dataframes[file_name].YY+1900), month=my_dataframes[file_name].MM,
                                                                        day=my_dataframes[file_name].DD, hour=my_dataframes[file_name].hh))
            my_dataframes[file_name]=my_dataframes[file_name].drop(['YY','MM','DD','hh'],axis=1)
            cols = my_dataframes[file_name].columns[my_dataframes[file_name].dtypes.eq('object')]
            my_dataframes[file_name][cols] = my_dataframes[file_name][cols].apply(pd.to_numeric, errors='coerce', axis=1)
            my_dataframes[file_name]=my_dataframes[file_name].replace(to_replace=[0,99,999,9999,99999], value=np.nan)
            my_dataframes[file_name]=my_dataframes[file_name].rename(mapper={'WD': 'WDIR','PRES':'BAR'},axis='columns')
        
        # late 1990s to ~2004 era
        elif 'YYYY' in my_dataframes[file_name].columns:
            my_dataframes[file_name]['datetime']=pd.to_datetime(dict(year=my_dataframes[file_name].YYYY, month=my_dataframes[file_name].MM, 
                                                                     day=my_dataframes[file_name].DD, hour=my_dataframes[file_name].hh))
            my_dataframes[file_name]=my_dataframes[file_name].drop(['YYYY','MM','DD','hh'],axis=1)
            my_dataframes[file_name]=my_dataframes[file_name].replace(to_replace=[0,99,999,9999,99999], value=np.nan)
            my_dataframes[file_name] = my_dataframes[file_name].rename(mapper={'WD': 'WDIR','PRES':'BAR'},axis='columns')

        # 2004 to modern era
        elif '#YY' in my_dataframes[file_name].columns:
            my_dataframes[file_name]=my_dataframes[file_name].drop(index=[0])
            my_dataframes[file_name]['datetime']=pd.to_datetime(dict(year=my_dataframes[file_name]['#YY'], month=my_dataframes[file_name].MM, 
                                                                     day=my_dataframes[file_name].DD, hour=my_dataframes[file_name].hh,minute=my_dataframes[file_name].mm))
            my_dataframes[file_name]=my_dataframes[file_name].drop(['#YY','MM','DD','hh','mm','TIDE'],axis=1)
            cols = my_dataframes[file_name].columns[my_dataframes[file_name].dtypes.eq('object')]
            my_dataframes[file_name][cols] = my_dataframes[file_name][cols].apply(pd.to_numeric, errors='coerce', axis=1)
            my_dataframes[file_name]=my_dataframes[file_name].replace(to_replace=[0,99,999,9999,99999], value=np.nan)
            my_dataframes[file_name]=my_dataframes[file_name].rename(mapper={'WD': 'WDIR','PRES':'BAR'},axis='columns')

        #throw
        else:
            print('unknown data buoy format')

            
    #Append all years into a single df
    allData=pd.DataFrame()
    for years in my_dataframes.keys():
        df_sub=my_dataframes[years]
        allData = pd.concat([allData, df_sub], ignore_index=True)
    allData=allData.sort_values('datetime', axis=0, ascending=True)
    
    return allData
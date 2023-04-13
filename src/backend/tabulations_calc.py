import pandas as pd
import re
import numpy as np
import math
from itertools import dropwhile
from collections import OrderedDict
import os

import backend.pyrankvote as pyrankvotesrc
from backend.pyrankvote.models import Candidate, Ballot, No_duplicates

# RESULTS_PATH = str(os.getcwd()) + "/results/" #for heroku 
RESULTS_PATH = str(os.getcwd()) + "/src/results/" # for local

def fix_non_break_space(df):
    raw_df_trial = pd.DataFrame()
    try:
        raw_df_trial = df.replace('\xa0', ' ', regex=True)
        raw_df_trial.columns = raw_df_trial.columns.str.replace('\xa0', '', regex=True)
    except:
        raw_df_trial = df.replace('\xa0', ' ')
        raw_df_trial.columns = raw_df_trial.columns.str.replace('\xa0', '')
    try:
        return raw_df_trial.replace(r"^ +| +$", r"", regex=True)
    except:
        return raw_df_trial.replace(r"^ +| +$", r"")

def suffle_df(df):
    return df.sample(frac = 1).reset_index(drop = True)
    

def fix_col_names(df_csv):
    df = df_csv.dropna(how = 'all').reset_index(drop = True)
    return df.add_suffix('.0')


# Position:
# position = 'President'
def get_positional_data(position, raw_df_csv):
    # Fix Column names to avoid cols with ranks >= 10 getting deleted in the data cleanup
    ## col structure: 
    ## 'Senate - 10 - 10.0' where 10.0 is the indicator number for rank 10 (not 1 or anything else)
    raw_df = fix_non_break_space(raw_df_csv)
    raw_df = fix_col_names(raw_df)
    raw_df = suffle_df(raw_df)
    var = position
    END_SUFFIX = '.0'
    SEPARATOR = ' - '
    pos_lst = ['President', 'Executive Vice President', 
                'External Affairs Vice President', 'Academic Affairs Vice President',
               'Student Advocate', 'Transfer Representative', 'Senate']
    # add suffix for columns about positions only
    raw_df.columns = [col + SEPARATOR + (re.findall(r'\d+', col)[0]) + END_SUFFIX if col.startswith(tuple(pos_lst)) else col for col in raw_df.columns] # raw_df.add_suffix('.0')


    position_str = position + SEPARATOR
    president_cols = [col for col in raw_df.columns if col.startswith(position)]
    # president_cols = [col for col in raw_df if col.startswith(position)]
    pres_counts = 0 #number of president columns

    while len(president_cols) != 0:
        pres_counts += 1
        pres_one_col = [col for col in raw_df.columns if col.endswith(SEPARATOR + str(pres_counts) + END_SUFFIX)] # raw_df.filter(like = position_str + str(pres_counts) + '.') # 

        president_cols = [x for x in president_cols if x not in pres_one_col]

    pres_counts # Total number of pres selection options: President - 'pres_counts' is the last column name

    rslt_df = pd.DataFrame()
    pres_candidate_names = []
    for i in range(pres_counts):
        # i + 1 -> ranking in that position
        rank = str(i + 1)
        col_name = position_str + rank # + SEPARATOR + rank + END_SUFFIX
        end_name = str(i + 1) + END_SUFFIX
        
        # take account of duplicate columns for the same position & ranking
        pres_num_col = [col for col in raw_df.columns if (col.startswith(position_str) & col.endswith(end_name))]
        pres_num_raw = raw_df[pres_num_col]
        
        # compress the rows to avoid repeating cols
        pres_final_num_df = pd.DataFrame(pres_num_raw.bfill(axis=1).iloc[:, 0])
        # print("pres_num_raw")
        # print(pres_num_raw)
        # there should only be one column df
        pres_final_num_df.columns = [col_name]
        
        # unique candidates in this column -> appended to all pres candidate lists
        unique_cand_subset = list(pres_final_num_df[col_name].unique())
        pres_candidate_names = pres_candidate_names + list(set(unique_cand_subset) - set(pres_candidate_names))

        # concat to the resulting df
        if rslt_df.empty:
            rslt_df = pres_final_num_df
        else:
            rslt_df = pd.concat([rslt_df, pres_final_num_df], axis=1).reset_index(drop=True)
    df = No_duplicates(rslt_df, var)
    rslt_df = df.fix_pandas_chars()

    rslt_df = rslt_df.replace('na',np.nan).transform(lambda x : sorted(x, key=pd.isnull),1)
    # print("rslt_df first col")
    # print(rslt_df)
    return rslt_df.dropna(axis = 0, how = 'all').reset_index(drop=True)


# PRESIDENTIAL CAMPAIGN
def exec_calculations(df):
#     works for president but not for other exec positions yet
    trial_elect_df = df
    df_cols = list(trial_elect_df.columns)
    len_df = len(trial_elect_df) * len(df_cols)
    MAX_RECURSION = 25
    no_rslt_str = "No Response"
    for c in range(len(df_cols)):
        col_name = df_cols[c]
        # trial_elect_df[col_name] = [no_rslt_lst[i] if type(v)==type(np.nan) else v for i,v in enumerate(trial_elect_df[col_name].tolist())]
        trial_elect_df[col_name] = [no_rslt_str if type(v)==type(np.nan) else v for i,v in enumerate(trial_elect_df[col_name].tolist())]

    raw_cand_str_df = trial_elect_df # copying surface level
    raw_cand_str_df

    ## Assign Candidates
    unique_cands = pd.unique(trial_elect_df[list(trial_elect_df.columns)].values.ravel('K'))
    FIRST_CHAR = 6
    candidates = []
    cand_dict = {}
    unique_cands
    for cand in unique_cands:
        if (not pd.isnull(cand)) or (cand != ''):
            var_name_raw = "".join([s[0] for s in cand.split()][:FIRST_CHAR])
            var_name = re.sub('[^a-zA-Z]+', '', var_name_raw)
            vars()[var_name] = Candidate(cand)
            candidates.append(vars()[var_name])
            cand_dict[cand] = vars()[var_name]

    # Replace str name to Candidate value
    for col in raw_cand_str_df.columns:
        raw_cand_str_df[col] = raw_cand_str_df[col].map(cand_dict)

    # Add the results to Ballot
    ballots = []
    
    raw_cand_str_df = raw_cand_str_df.loc[raw_cand_str_df.nunique(axis=1).ne(1)].reset_index(drop = True)

    for i in range(len(raw_cand_str_df)):
        """lst = raw_cand_str_df.loc[i, :].values.flatten().tolist()
        # Avoid any trailing NaN values
        res = list(reversed(tuple(dropwhile(lambda x: x is Candidate("No Response"),
                                        reversed(lst)))))
        print("res")
        print(res)
        rslt = Ballot(ranked_candidates = res)
        ballots.append(rslt)"""

        target_element = Candidate("No Response")
        lst = raw_cand_str_df.loc[i, :].dropna().values.flatten().tolist()
        lst = filter(lambda item: item != target_element,lst)
        # print(lst)
        

        # delete trailing 'No Response' values
        def takewhile_including(iterable, value):
            for it in iterable:
                yield it
                if it == value:
                    return
        #with_dup = list(takewhile_including(lst, target_element))[:-1]
        res = list(OrderedDict.fromkeys(lst))
        # print("res")
        # print(res)

        rslt = Ballot(ranked_candidates = res)
        ballots.append(rslt)

    # Return result
    election_result = pyrankvotesrc.instant_runoff_voting(candidates, ballots)
    winners = election_result.get_winners()

    return election_result

def get_final_rslt(election_result):
    all_rounds = election_result.__dict__["rounds"]
    return all_rounds[len(all_rounds) - 1].__str__()

def get_all_rslt(election_result):
    all_rounds = election_result.__dict__["rounds"]
    return all_rounds.__str__()


def senate_calculations(position, raw_df):
    df = get_positional_data(position, raw_df)
    trial_elect_df = df
    df_cols = list(trial_elect_df.columns)
    len_df = len(trial_elect_df) * len(df_cols)
    MAX_RECURSION = 25
    # no_rslt_lst = ["No Response - " + str(i) for i in range(MAX_RECURSION)] * ((len_df // MAX_RECURSION) + 1)
    no_rslt_str = "No Response"
    for c in range(len(df_cols)):
        col_name = df_cols[c]
        # trial_elect_df[col_name] = [no_rslt_lst[i] if type(v)==type(np.nan) else v for i,v in enumerate(trial_elect_df[col_name].tolist())]
        trial_elect_df[col_name] = [no_rslt_str if type(v)==type(np.nan) else v for i,v in enumerate(trial_elect_df[col_name].tolist())]

    raw_cand_str_df = trial_elect_df # copying surface level
    raw_cand_str_df

    ## Assign Candidates
    unique_cands = pd.unique(trial_elect_df[list(trial_elect_df.columns)].values.ravel('K'))
    FIRST_CHAR = 6
    candidates = []
    cand_dict = {}
    unique_cands
    for cand in unique_cands:
        if (not pd.isnull(cand)) or (cand != ''):
            var_name_raw = "".join([s[0] for s in cand.split()][:FIRST_CHAR])
            var_name = re.sub('[^a-zA-Z]+', '', var_name_raw)
            vars()[var_name] = Candidate(cand)
            candidates.append(vars()[var_name])
            cand_dict[cand] = vars()[var_name]
    # Replace str name to Candidate value
    for col in raw_cand_str_df.columns:
        raw_cand_str_df[col] = raw_cand_str_df[col].map(cand_dict)

    # Add the results to Ballot
    ballots = []


    raw_cand_str_df = raw_cand_str_df.loc[raw_cand_str_df.nunique(axis=1).ne(1)].reset_index(drop = True)
    for i in range(len(raw_cand_str_df)):
        target_element = Candidate("No Response")
        lst = raw_cand_str_df.loc[i, :].dropna().values.flatten().tolist()
        lst = filter(lambda item: item != target_element,lst)
        # print(lst)
        

        # delete trailing 'No Response' values
        def takewhile_including(iterable, value):
            for it in iterable:
                yield it
                if it == value:
                    return
        #with_dup = list(takewhile_including(lst, target_element))[:-1]
        res = list(OrderedDict.fromkeys(lst))

        rslt = Ballot(ranked_candidates = res)
        ballots.append(rslt)

    # # Return result
    # election_result = pyrankvote.instant_runoff_voting(candidates, ballots)
    NUMBER_OF_SEATS = 20
    election_result = pyrankvotesrc.single_transferable_vote(
        candidates, ballots, number_of_seats=20
    )
    winners = election_result.get_winners()

    return election_result

def get_round_str(ballot_result_rounds):
    return ballot_result_rounds.__str__()

def get_txt_file(round_str):
    folder = RESULTS_PATH
    print("folder")
    print(folder)
    filename = 'Round_Results.txt'
    with open((folder + filename), "w") as f:
        print(round_str, file=f)
    f.close()


def get_propositional_data(proposition, raw_df_csv):
    # Fix Column names to avoid cols with ranks >= 10 getting deleted in the data cleanup
    raw_df = fix_col_names(raw_df_csv)

    position_str = proposition
    president_cols = [col for col in raw_df if col.startswith(proposition)]

    pres_counts = len(president_cols) # Total number of pres selection options: President - 'pres_counts' is the last column name

    rslt_df = pd.DataFrame()
    pres_candidate_names = []
    for i in range(pres_counts):
        # i + 1 -> ranking in that position
        rank = str(i + 1)
        col_name = position_str + rank # + SEPARATOR + rank + END_SUFFIX
        
        # take account of duplicate columns for the same position & ranking
        pres_num_col = [col for col in raw_df if (col.startswith(position_str))]
        pres_num_raw = raw_df[pres_num_col]
        
        # compress the rows to avoid repeating cols
        pres_final_num_df = pd.DataFrame(pres_num_raw.bfill(axis=1).iloc[:, 0])
        # there should only be one column df
        pres_final_num_df.columns = [col_name]
        
        # unique candidates in this column -> appended to all pres candidate lists
        unique_cand_subset = list(pres_final_num_df[col_name].unique())
        pres_candidate_names = pres_candidate_names + list(set(unique_cand_subset) - set(pres_candidate_names))

        # concat to the resulting df
        if rslt_df.empty:
            rslt_df = pres_final_num_df
        else:
            rslt_df = pd.concat([rslt_df, pres_final_num_df], axis=1).reset_index(drop=True)
    return rslt_df.dropna(axis = 0, how = 'all').reset_index(drop=True)



def proposition_calculation(proposition_name, raw_df):
    print("proposition_name")
    print(proposition_name)
    prop_trial_df = get_propositional_data(proposition_name, raw_df)
    prop_trial_df

    proposition_cols = list(prop_trial_df.columns)
    usage_df = pd.DataFrame()
    if len(proposition_cols) > 1:
        # all proposition columns have to the same
        prop_trial_df['matching'] = prop_trial_df.eq(prop_trial_df.iloc[:, 0], axis=0).all(1)
        matching_rows = prop_trial_df['matching'].unique()
        if ((len(matching_rows) == 1) & (matching_rows[0] == True)):
            print("All rows are the same")
            usage_df = prop_trial_df[[prop_trial_df.columns[0]]]
        else:
            # Assuming combining of cols are needed
            no_rslt_str = "No Response"
            for c in range(len(proposition_cols)):
                col_name = proposition_cols[c]
                prop_trial_df[col_name] = [no_rslt_str if type(v)==type(np.nan) else v for i,v in enumerate(prop_trial_df[col_name].tolist())]
    else:
        usage_df = prop_trial_df
    # usage_df is our main character
    usage_col = usage_df.columns[0]
    usage_df[usage_col] = usage_df[usage_col].str.strip()
    rslt_df = usage_df[usage_col].value_counts().rename_axis('Votes').reset_index(name='counts')
    rslt_df['counts'] = (rslt_df['counts']).astype('int')
    
    # print("rslt_df['counts'].unique()")
    # print(rslt_df['counts'].unique())
    index_winner = index_with_highest_col_value(rslt_df, 'counts')
    # print("index_winner")
    # print(index_winner)
    df_len = len(rslt_df)
    status_col = ["Rejected" if i != index_winner else "Winner" for i in range(df_len)]
    rslt_df['Status'] = status_col
    # print("rslt_df")
    # print(rslt_df)
    # Adding buffer 0th row to match the other position syntax
    rslt_df = pd.DataFrame(np.insert(rslt_df.values, 0, values=[proposition_name] * len(rslt_df.columns), axis=0))
    rslt_df.columns = ["Votes", "Counts", "Status"]

    return rslt_df.reset_index(drop = True)

def index_with_highest_col_value(df, column_name):
    """
    Returns: (int) index of the df with the highest value in column
    """
    return df[column_name].argmax()

# pos_lst = ['President', 'Executive Vice President', 
#                 'External Affairs Vice President', 'Academic Affairs Vice President',
#                'Student Advocate', 'Transfer Representative', 'Senate']
# position = "Senate"
# raw_df = pd.read_csv("/Users/saruul/Desktop/Projects/asuc_ballot/2022ElectionResults.csv")

def get_txt_names_list(base_name_lst):
    result_lst = []
    for name in base_name_lst:
        file_name = name + '.txt'
        result_lst.append(file_name)
    return result_lst

def combine_two_lists_to_dict(lst1, lst2):
    if len(lst1) == len(lst2):
        return {lst1[i]: lst2[i] for i in range(len(lst1))}
    else:
        Exception("Both lists need to be same length")

def calculate_execs(position_lst_all, raw_df):
    folder = RESULTS_PATH
    print("folder")
    print(folder)
    senate_str = 'Senate'
    position_lst = position_lst_all
    if senate_str in position_lst:
        position_lst.remove(senate_str)
    txt_file_names = get_txt_names_list(position_lst)

    pos_dict = combine_two_lists_to_dict(position_lst, txt_file_names)

    for position, filename in pos_dict.items():
        rslt_df = get_positional_data(position, raw_df)
        election_result = exec_calculations(rslt_df)
        get_final = get_final_rslt(election_result)

        with open((folder + "allrounds.txt"), "a") as a:
            print(election_result.__str__(), file=a)

        with open((folder + filename), "w") as f:
            print(get_final, file=f)
        f.close()

def calculate_senate(position_lst, raw_df):
    folder = RESULTS_PATH
    print("folder")
    print(folder)

    senate_str = 'Senate'
    position = [i for i in position_lst if i.startswith(senate_str)][0]
    filename = str(position) + '.txt'
    rslt_df = get_positional_data(position, raw_df)
    election_result = senate_calculations(position, rslt_df)
    # get_all_rounds = get_all_rslt(election_result)
    get_final = get_final_rslt(election_result)

    with open((folder + "allrounds.txt"), "a") as a:
        print(election_result.__str__(), file=a)
    # print(results)
    with open((folder + filename), "w") as f:
        print(get_final, file=f)
    f.close()


def calculate_propositions(proposition_list, raw_df):
    result_df = pd.DataFrame()
    folder = RESULTS_PATH
    for proposition_name in proposition_list:
        filename = proposition_name + ".txt"
        result_df = proposition_calculation(proposition_name, raw_df)
        
        with open((folder + filename), "w") as f:
            print(result_df, file=f)
        f.close()
    return

def calculate_senate_propositions(position_lst, proposition_lst, raw_df):
    """
    params:
        position_lst: list of positions running
        proposition_lst: names of propositions in the ballot, ie., ['Proposition 22A', 'Proposition 22B']
        raw_df: df directly from ballot results
    """
    # calculate_execs(position_lst, raw_df)
    calculate_senate(position_lst, raw_df)
    calculate_propositions(proposition_lst, raw_df)

# pos_lst = ['President', 'Executive Vice President', 
#                 'External Affairs Vice President', 'Academic Affairs Vice President',
#                'Student Advocate', 'Transfer Representative', 'Senate']
# raw_df = pd.read_csv("/Users/saruul/Desktop/Projects/asuc_ballot/src/demo_files/electionresults.csv")
# # calculate_execs(pos_lst, raw_df)
# calculate_senate(raw_df)
# proposition_lst = ['Proposition 22A', 'Proposition 22B']
# rslt = calculate_propositions(proposition_lst, raw_df)
# print(rslt)
import numpy as np
import pandas as pd
import streamlit as st
import requests
from math import floor
from math import ceil
import random
import json

if 'init' not in st.session_state:
    st.session_state['init'] = True

if 'df' not in st.session_state:
    st.session_state['df'] = 1

# load all challenges templates
df_challenges = pd.read_csv('Challenge_template.csv', delimiter=';')
df_challenges['playerType'] = df_challenges['playerType'].str.split(',')
df_challenges = df_challenges.explode('playerType').reset_index()
df_challenges = pd.get_dummies(df_challenges, columns=['playerType']).reset_index(drop=True)
df_challenges = df_challenges.groupby(['index', 'challengesTemplate', 'distance', 'time', 'segment', 'reward']).agg({'playerType_Achiever' : 'sum', 'playerType_Socializer': 'sum','playerType_Philanthropist': 'sum', 'playerType_Free_Spirit': 'sum', 'playerType_Player': 'sum'})
df_challenges = df_challenges.reset_index()

# on first load make empty dataframe otherwise get from session state
if st.session_state['init'] == True:
    df = pd.DataFrame([], columns=df_challenges.columns)
    # st.session_state['init'] = False
else:
    df = st.session_state['df']

# reinforment learning function using epsilon greedy approach
def epsilon_greedy_policy(df, epsilon=0.10):
    types = ['playerType_Achiever', 'playerType_Socializer','playerType_Philanthropist', 'playerType_Free_Spirit', 'playerType_Player']
    values = [df['playerType_Achiever'].sum(), df['playerType_Socializer'].sum(),df['playerType_Philanthropist'].sum(), df['playerType_Free_Spirit'].sum(), df['playerType_Player'].sum()]
    df2 = pd.DataFrame(values, index=types, columns=['count']).reset_index()
    df2['count'] += 1
    # draw a 0 or 1 from a binomial distribution, with epsilon % chance to draw 1
    explore = np.random.binomial(1, epsilon)
    # if explore: choose randomly three different player types
    if explore == 1 or df2['count'].sum() < 6:
        method = 'explore'
        recs = df2.sample(n = 3)
    # if exploit: pick the top ranked player types
    else:
        method = 'exploit'
        # duplicated every player type by amount of reward
        scores_dupl = df2.loc[df2.index.repeat(df2['count'])].reset_index(drop=True)
        # print(scores_dupl)
        
        # sort values and only keep the top 75%
        scores = scores_dupl.sort_values('count', ascending=False).reset_index(drop=True)
        slice_lenght = floor(len(scores) * 0.75)
        scores = scores.loc[0: slice_lenght]

        #select three recommendations
        if len(scores) > 1:
            recs = scores.sample(n = 3)
        else:
            recs = scores.loc[0: 2]
    return recs, method

recs, method = epsilon_greedy_policy(df)
recs['index'] = recs['index'].astype('string')

# pick challenges from recommended player types
def getChallenges():
    first = True
    # loop through every recommendation
    for index, type in recs.iterrows():
        second = True
        # check if type is 'players'
        if type['index'] == 'playerType_Player':
            for index2, type2 in recs.iterrows():
               if type2['index'] != 'playerType_Player':
                # select all challenges that are the type players in combination with another type
                for index3, challenge in df_challenges.iterrows():
                    if challenge[type['index']] == 1 & challenge[type2['index']] == 1:
                        if(second == False):
                            challengeDF = challenge.to_frame().T
                            challengesPerType = pd.concat([challengesPerType, challengeDF], ignore_index=True)
                        else:
                            challengesPerType = challenge.to_frame().T
                            second = False 
        else:
            # filter all challenges to a dataframe with only challenges for a particular type
            for index2, challenge in df_challenges.iterrows():
                if challenge[type['index']] == 1 & challenge['playerType_Player'] != 1:
                    if(second == False):
                        challengeDF = challenge.to_frame().T
                        challengesPerType = pd.concat([challengesPerType, challengeDF], ignore_index=True)
                    else:
                        challengesPerType = challenge.to_frame().T
                        second = False
        # pick random challenges from the filtered list
        sample = challengesPerType.sample(n=1)
        counter  = 0
        # give new challenge when the challenge is already one of the recommendations.
        while True:
            sample = challengesPerType.sample(n=1)
            if first == False:
                if sample['index'].iloc[0] not in recommendedChallenges['index'].values:
                    break
            else:
                break
        if first == False:
            sampleDF = sample
            recommendedChallenges = pd.concat([recommendedChallenges, sampleDF])
        else:
            recommendedChallenges = sample
            print(recommendedChallenges['index'].values)
            first= False
    return recommendedChallenges

RecChallenges = getChallenges()
RecChallenges = RecChallenges.reset_index(drop=True)

# change parameters in challenges templates
def changeChallengeParameters():
    for index, challenge in RecChallenges.iterrows():
        # change segment if in challenge
        if '<segment>' in challenge['challengesTemplate']:
            # api call
            # location = [51.575283, 4.737244, 51.600514, 4.812119]
            # BaseUrl = 'https://www.strava.com/api/v3/segments/explore?'
            # response = requests.get(BaseUrl, params={'bounds': ','.join(str(b) for b in location), 'activity_type': 'running'}, headers={'Authorization': 'Bearer 01991620287ebb21e18c8ed3e6a047a5cf0db361'})
            # data = response.json() 
            with open('segments.json', 'r') as openfile:
                data = json.load(openfile)
            segmentName = ''
            newSegmentList = []
            # add new segments to a list
            for segment in data:
                if len(df['segment']) > 0:
                    for pastsegments in df['segment']:
                        if segment['name'] != pastsegments:
                            newSegmentList.append(segment['name'])
                else:
                    newSegmentList.append(segment['name'])
            index = random.randrange(len(newSegmentList))
            # pick one of the new segment for the challenges
            challenge['segment'] = newSegmentList[index]
        # change distance if in challenge
        if '<distance>' in challenge['challengesTemplate']:
            pastdistances = []
            # get all previous distances
            for pastdistance in df['distance']:
                pastdistances.append(pastdistance)
            if len(pastdistances) > 0:
                # calculate the new distance based on the average previous distances
                avg_distance = sum(pastdistances) / len(pastdistances)
                increase_percentage = random.uniform(0.1, 0.25)
                increase_distance = avg_distance * increase_percentage
                new_distance = avg_distance + increase_distance
                challenge['distance'] = round(new_distance,1)
        else:
            if len(df) > 0:
                challenge['distance'] = sum(df['distance']) / len((df['distance']))
        # change time if in challenge
        if '<time>' in challenge['challengesTemplate']:
            pasttimeList = []
             # get all previous time
            for pasttime in df['time']:
                pasttimeList.append(pasttime)
            if len(pasttimeList) > 0:
                # calculate the new time based on the average previous time
                avg_time = sum(pasttimeList) / len(pasttimeList)
                increase_percentage = random.uniform(0.1, 0.25)
                increase_time = avg_time * increase_percentage
                new_time = avg_time + increase_time
                challenge['time'] = ceil(new_time)
        else:
            if len(df) > 0:
                challenge['time'] = sum(df['time']) / len((df['time']))
changeChallengeParameters()

# replace the parameters in the challenges templates           
for index, challenge in RecChallenges.iterrows():
    string = challenge['challengesTemplate']
    for column in challenge.index:
        if '<' + column + '>' in challenge['challengesTemplate']:
            string = string.replace('<' + column + '>', str(challenge[column]))
    RecChallenges.loc[index, 'challengesTemplate'] = string

# save recommendation in csv for the user test 
def save(num):
    recommendations = RecChallenges.reset_index(drop=True)
    # register if challenges was chosen
    recommendations['chosen'] = 0
    recommendations['chosen'].iloc[num] = 1
    if st.session_state['init'] == True:       
        st.session_state['init'] = False
    else:
        oldrecommendations = pd.read_csv('recommendations.csv')
        recommendations = pd.concat([oldrecommendations, recommendations])
    recommendations.to_csv('recommendations.csv', index=False)


# save chosen challenge in a dataframe
def chalOne(df):
    tempDF = RecChallenges.iloc[0].to_frame().T
    df = pd.concat([df, tempDF]).reset_index(drop=True)
    st.session_state['df'] = df
    save(0)

def chalTwo(df):
    tempDF = RecChallenges.iloc[1].to_frame().T
    df = pd.concat([df, tempDF]).reset_index(drop=True)
    st.session_state['df'] = df
    save(1)

def chalThree(df):
    tempDF = RecChallenges.iloc[2].to_frame().T
    df = pd.concat([df, tempDF]).reset_index(drop=True)
    st.session_state['df'] = df
    save(2)


# streamlit interface
header = st.title('Pick a challenge')
text = st.caption(method)

button1 = st.button(RecChallenges.loc[0,'challengesTemplate'],key='btn1', on_click=chalOne, args=(df,))

button2 = st.button(RecChallenges.loc[1,'challengesTemplate'],key='btn2', on_click=chalTwo, args=(df,))

button3 = st.button(RecChallenges.loc[2,'challengesTemplate'],key='btn3', on_click=chalThree, args=(df,))

types = ['playerType_Achiever', 'playerType_Socializer','playerType_Philanthropist', 'playerType_Free_Spirit', 'playerType_Player']
values = [df['playerType_Achiever'].sum(), df['playerType_Socializer'].sum(),df['playerType_Philanthropist'].sum(), df['playerType_Free_Spirit'].sum(), df['playerType_Player'].sum()]
df3 = pd.DataFrame(values, index=types, columns=['count']).reset_index()
st.dataframe(data=df3)


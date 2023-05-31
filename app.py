import numpy as np
import pandas as pd
import streamlit as st
import requests
from math import floor
from math import ceil
import random
import json

# create sessions states
if 'init' not in st.session_state:
    st.session_state['init'] = True

if 'df' not in st.session_state:
    st.session_state['df'] = 1

if 'df_score' not in st.session_state:
    st.session_state['df_score'] = 1

if 'counter' not in st.session_state:
    st.session_state['counter'] = 0

if 'debug' not in st.session_state:
    st.session_state['debug'] = False

if 'typelist' not in st.session_state:
    st.session_state['typelist'] = ['playerType_Achiever', 'playerType_Socializer','playerType_Philanthropist', 'playerType_Free_Spirit', 'playerType_Player']

# load all challenges templates
df_challenges = pd.read_csv('Challenge_template.csv', delimiter=';')
df_challenges = pd.get_dummies(df_challenges, columns=['playerType']).reset_index(drop=True)


# on first load make empty dataframe otherwise get from session state
if st.session_state['init'] == True:
    df = pd.DataFrame([], columns=df_challenges.columns)
    df_score = pd.DataFrame([], columns=df_challenges.columns)
    # st.session_state['init'] = False
else:
    df = st.session_state['df']
    df_score = st.session_state['df_score']

# reinforment learning function using Thompson samling algorithm
def thompson_policy(df, df_score, initial):
    # create two arrays: rewards are the total rewards per player type and count is the amount of times that the types is recommended
    print('he')
    print('he')
    print('he')
    print('he')

    print(df_score.columns)
    reward = [df_score['playerType_Achiever'].sum(), df_score['playerType_Socializer'].sum(),df_score['playerType_Philanthropist'].sum(), df_score['playerType_Free_Spirit'].sum(), df_score['playerType_Player'].sum()]
    count = [df['playerType_Achiever'].sum(), df['playerType_Socializer'].sum(),df['playerType_Philanthropist'].sum(), df['playerType_Free_Spirit'].sum(), df['playerType_Player'].sum()]
    df2 = pd.DataFrame(count, index=st.session_state['typelist'], columns=['count']).reset_index()
    df2['count'] += 1

  

    if initial == True:
        df2['reward'] = 1
        # set the starting recommendation
        recs = df2.sample(n = 1)
        recs = recs.iloc[0].to_frame().T
        return recs, initial
    else:
        df2['reward'] = reward
        df2['reward'] += 1

    # Thompson sampling algorithms compare the amount of times recommended against the amount of times rewarded
    # This algorithm will pick the most promising player type. That can be the most chosen times or a type that is not often recommended.
    df2['theta'] = np.random.beta(df2['count'] + 1, df2['count'] - df2['reward'] + 1)
    
    #sort the values pick the most promising type
    scores = df2.sort_values('theta', ascending=False)
    recs = scores.iloc[0].to_frame().T
    return recs, initial 


# pick challenges from recommended player types
def getChallenges(recs, selected, first):
    second = True
    challengesPerType = pd.DataFrame([], columns=df_challenges.columns)
    # loop through every recommendation
    for index3, challenge in df_challenges.iterrows():
        if challenge[recs['index']].any() == 1:
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
    loop = True
    while loop == True:
        sample = challengesPerType.sample(n=1)
        if first == False:
            if sample['id'].values not in selected['id'].values:
                loop = False
            else:
                print('')
        else:
            loop = False
            first = False
    return sample, first


RecChallenges= pd.DataFrame([], columns=df_challenges.columns)
RecChallenge= pd.DataFrame([], columns=df_challenges.columns)
df_prospective = df
df_score_prospective = df_score

# recommend a challenge three times
first = True
for i in range(3):
    # get the most promising type
    pltype, method = thompson_policy(df_prospective , df_score_prospective, st.session_state['init'])
    # create challenges for that type
    pendingChallenge, first = getChallenges(pltype, RecChallenge, first)
    pendingChallenge['chosen'] = 0

    # save recommendations
    RecChallenges = pd.concat([pendingChallenge, RecChallenges], ignore_index=True)
    if i != 0:
         RecChallenge = pd.concat([RecChallenge, pendingChallenge.copy()], ignore_index=True)
    else:
        RecChallenge = pendingChallenge.copy()
    # save a copy of the recommendation as this type will not be picked and rerun the function for the next best recommendation
    df_prospective  = pd.concat([pendingChallenge, df_prospective], ignore_index=True)
    pendingChallenge.loc[:, 'playerType_Achiever': 'playerType_Socializer'] = 0
    if df_score_prospective.empty:
        df_score_prospective  = pendingChallenge
    else:
       df_score_prospective  = pd.concat([pendingChallenge, df_score_prospective], ignore_index=True)


# change parameters in challenges templates
def changeChallengeParameters():
    for index, challenge in RecChallenges.iterrows():
        # change segment if in challenge
        if '<segment>' in challenge['challengesTemplate']:
            ## api call 
            ## access token expires every six hours. So the output from the request below is stored in segment.json for testing
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
            segmentIndex = random.randrange(len(newSegmentList))
            # pick one of the new segment for the challenges
            challenge['segment'] = newSegmentList[segmentIndex]
        # change distance if in challenge
        if '<distance>' in challenge['challengesTemplate']:
            pastdistances = []
            # get all previous distances
            for pastdistance in df['distance']:
                pastdistances.append(pastdistance)
            if len(pastdistances) > 0:
                # calculate the new distance based on the average previous distances
                avg_distance = sum(pastdistances) / len(pastdistances)
                increase_percentage = random.uniform(0.2, 0.3)
                increase_distance = avg_distance * increase_percentage
                new_distance = avg_distance + increase_distance
                challenge['distance'] = round(new_distance,1)
        else:
            # save the average distance 
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
                increase_percentage = random.uniform(0.2, 0.3)
                increase_time = avg_time * increase_percentage
                new_time = avg_time + increase_time
                challenge['time'] = ceil(new_time)
        else:
            # save the average time
            if len(df) > 0:
                challenge['time'] = sum(df['time']) / len((df['time']))
        
        # replace other variables for specific challenges
        if '<group>' in challenge['challengesTemplate']:
            representList = ['disabled people', 'children in war', 'refugees']
            challenge['challengesTemplate'] = challenge['challengesTemplate'].replace('<group>', random.choice(representList))
        if '<disease>' in challenge['challengesTemplate']:
            representList = ['cancer', 'diabetes', 'alzheimer', 'aids']
            challenge['challengesTemplate'] = challenge['challengesTemplate'].replace('<disease>', random.choice(representList))
        if '<highest distance>' in challenge['challengesTemplate']:
            highest = RecChallenges.sort_values(by='distance', ascending=False)
            challenge['challengesTemplate'] = challenge['challengesTemplate'].replace('<highest distance>', str(highest.loc[0, 'distance']))
        RecChallenges.loc[index] = challenge

changeChallengeParameters()

# replace the variable parameters in the challenges templates           
for index, challenge in RecChallenges.iterrows():
    string = challenge['challengesTemplate']
    for column in challenge.index:
        if '<' + column + '>' in challenge['challengesTemplate']:
            if '<collective><' + column + '>' in challenge['challengesTemplate']:
                times = random.randint(15, 30)
                string = string.replace('<collective><' + column + '>', str(round(challenge[column] * times)))
            if '<groupGoal><' + column + '>' in challenge['challengesTemplate']:
                times = random.randint(3, 7)
                string = string.replace('<groupGoal><' + column + '>', str(round(challenge[column] * times)))
            string = string.replace('<' + column + '>', str(challenge[column]))
    RecChallenges.loc[index, 'challengesTemplate'] = string

# save recommendation in csv for the user test 
def save(num, recommendations):
    # check if this was the first
    if st.session_state['init'] == True:       
        st.session_state['init'] = False
    else:
        # otherwise get the old recommendation to add the new ones to it.
        oldrecommendations = pd.read_csv('recommendations.csv')
        recommendations = pd.concat([oldrecommendations, recommendations])
    # recommendations.to_csv('recommendations.csv', index=False)

# save recommendations and picked challenges in session state
def processRecommendations(df, df_score, num):
    recommendations = RecChallenges
    df = pd.concat([df, recommendations]).reset_index(drop=True)

    # set all the challenges with the picked type as succesfull recommendation, even if the one is not chosen
    for playertype in st.session_state['typelist']:
        if recommendations.loc[num, playertype] == 1:
            for index, recommendation in recommendations.iterrows(): 
                if recommendation[playertype] == 1:
                    recommendation['chosen'] = 1
                    df_score = pd.concat([df_score, recommendation.to_frame().T]).reset_index(drop=True)
                else:
                    recommendation['chosen'] = 0
                recommendations.iloc[index] = recommendation

    recommendations['Choice'] = st.session_state['counter']

    st.session_state['df'] = df
    st.session_state['df_score'] = df_score
    st.session_state['counter'] = st.session_state['counter'] + 1
    
    # save to csv file
    save(num, recommendations)

with open('app.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
# streamlit interface
header = st.title('Pick a challenge')
text = st.caption('count: ' + str(st.session_state['counter']))

button1 = st.button(RecChallenges.loc[2,'challengesTemplate'],key='btn1', on_click=processRecommendations, args=(df, df_score,2,))

button2 = st.button(RecChallenges.loc[1,'challengesTemplate'],key='btn2', on_click=processRecommendations, args=(df, df_score,1,))

button3 = st.button(RecChallenges.loc[0,'challengesTemplate'],key='btn3', on_click=processRecommendations, args=(df, df_score,0,))

st.markdown('<div></div>', unsafe_allow_html=True)
#enable debug mode

def debugging():
    if debugEnabler == False:
        st.session_state['debug'] = True
    else:
        st.session_state['debug'] = False
debugEnabler = st.checkbox('debug', value=False, on_change=debugging, args=None, kwargs=None, disabled=False, label_visibility="visible")

# debug objects for streamlit interface to show changing scores
if st.session_state['debug'] == True:
    types = ['playerType_Achiever', 'playerType_Socializer','playerType_Philanthropist', 'playerType_Free_Spirit', 'playerType_Player']
    reward = [df_score['playerType_Achiever'].sum(), df_score['playerType_Socializer'].sum(),df_score['playerType_Philanthropist'].sum(), df_score['playerType_Free_Spirit'].sum(), df_score['playerType_Player'].sum()]
    count = [df['playerType_Achiever'].sum(), df['playerType_Socializer'].sum(),df['playerType_Philanthropist'].sum(), df['playerType_Free_Spirit'].sum(), df['playerType_Player'].sum()]
    df3 = pd.DataFrame(count, index=types, columns=['count']).reset_index()
    df3['reward'] = reward
    st.dataframe(data=df3)


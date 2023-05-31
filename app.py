import numpy as np
import pandas as pd
import streamlit as st
from math import floor

if 'init' not in st.session_state:
    st.session_state['init'] = True

if 'df' not in st.session_state:
    st.session_state['df'] = 1

if st.session_state['init'] == True:
    Rewarded = [0,0,0,0,0]
    types=['Achiever', 'Socialiser','Philanthropist', 'Free Spirit', 'Player']
    arms = 5
    df = pd.DataFrame(types, columns=['types'])
    df['reward'] = 1
    st.session_state['init'] = False
    st.session_state['df'] = df
else:
    df = st.session_state['df']

def epsilon_greedy_policy(df, arms, epsilon=0.10, slate_size=3, batch_size=15):
    # draw a 0 or 1 from a binomial distribution, where epsilon % chance to draw a 1
    explore = np.random.binomial(1, epsilon)
    # if explore: pick three types randomly
    if explore == 1:
        method = 'explore'
        recs = df.sample(n = 3)
    # if exploit: Repeat rows by the amount of reward
    else:
        method = 'exploit'
        scores_dupl = df.loc[df.index.repeat(df.reward)].reset_index()
        
        # sort values and only keep the top 75%
        scores = scores_dupl.sort_values('reward', ascending=False).reset_index(drop=True)
        print(scores)
        scores = scores.loc[0: floor(len(scores) * 0.75)]

        #select three recommendations
        recs = scores.sample(n = 3)
        
    return recs, method

def chalOne():
    print(recs.loc[0, 'index'])
    df.loc[recs.loc[0, 'index'], 'reward'] += 1
    st.session_state['df'] = df

def chalTwo():
    df.loc[recs.loc[1, 'index'], 'reward'] += 1
    st.session_state['df'] = df

def chalThree():
    df.loc[recs.loc[2, 'index'], 'reward'] += 1
    st.session_state['df'] = df


recs, method = epsilon_greedy_policy(df, 5,0.15, 3, 15)
recs = recs.reset_index()

header = st.title('Pick a challenge')
text = st.caption(method)

button1 = st.button(recs.loc[0,'types'],key='btn1', on_click=chalOne)

button2 = st.button(recs.loc[1,'types'],key='btn2', on_click=chalTwo)

button3 = st.button(recs.loc[2,'types'],key='btn3', on_click=chalThree)

st.dataframe(data=df)

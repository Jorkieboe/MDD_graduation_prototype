import numpy as np
import pandas as pd
import streamlit as st

if 'init' not in st.session_state:
    st.session_state['init'] = True

if 'df' not in st.session_state:
    st.session_state['df'] = 1

if st.session_state['init'] == True:
    Rewarded = [0,0,0,0,0]
    types=['Achiever', 'Socialiser','Philanthropist', 'Free Spirit', 'Player']
    arms = 5
    df = pd.DataFrame(types, columns=['types'])
    df['reward'] = 0
    st.session_state['init'] = False
    st.session_state['df'] = df
else:
    df = st.session_state['df']

def epsilon_greedy_policy(df, arms, epsilon=0.10, slate_size=3, batch_size=15):
    # draw a 0 or 1 from a binomial distribution, with epsilon% likelihood of drawing a 1
    explore = np.random.binomial(1, epsilon)
    # if explore: shuffle movies to choose a random set of recommendations
    explore = 1
    if explore == 1:
        print('explore')
        # recs = np.random.choice(arms, size=(slate_size), replace=True)
        recs = df.sample(n = 3)
    # if exploit: sort movies by "like rate", recommend movies with the best performance so far
    else:
        print('exploit')
        scores = df.sort_values('reward', ascending=False)
        recs = scores.loc[scores.index[0:slate_size]]
    return recs

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

recs = epsilon_greedy_policy(df, 5,0.15, 3, 15)
recs = recs.reset_index()

header = st.header('Pick a challenge')

button1 = st.button(recs.loc[0,'types'], on_click=chalOne)

button2 = st.button(recs.loc[1,'types'], on_click=chalTwo)

button3 = st.button(recs.loc[2,'types'], on_click=chalThree)


st.dataframe(data=df)

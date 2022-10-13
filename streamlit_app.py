import streamlit as st
import pandas as pd
import altair as alt
import time


#---todo:
#if time, player tab with player per game stats over time
#write it up!

#https://discuss.streamlit.io/t/remove-ui-top-bar-forehead/22071/2
hide_streamlit_style = """
<style>
    #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
    
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("Let's Analyze Some Penguin('s) Data")

#https://stackoverflow.com/questions/70932538/how-to-center-the-title-and-an-image-in-streamlit
col1, col2, col3 = st.columns(3)
with col1:
    st.write(' ')
with col2:
    st.image("pens_logo.png")
with col3:
    st.write(' ')


audio_file = open('nite.wav', 'rb')
audio_bytes = audio_file.read()
st.audio(audio_bytes, format="audio/wav")

#@st.cache  # add caching so we load the data only once
# def load_data():
#     return pd.read_csv('pens_hits.csv')

# hits = load_data()
# goals = pd.read_csv('pens_goals.csv')
# shots = pd.read_csv('pens_shots.csv')

win_prob = pd.read_csv('win_prob.csv')
full_data = pd.read_csv('full_data.csv')

#losing sort order...
all_games = sorted(list(set(full_data['Game Description'])), reverse = True)

game_sel = st.selectbox('Select a Game', options = all_games)
#hits_sub = hits[hits['game'].isin(game_sel)]
#goals_sub = goals[goals['game'].isin(game_sel)]
#shots_sub = shots[shots['game'].isin(game_sel)]
win_prob_sub = win_prob[win_prob['Game Description'] == game_sel]
win_prob_sub = win_prob_sub.assign(game = win_prob_sub['game'].astype(str))
full_data_sub = full_data[full_data['Game Description'] == game_sel]




selector = alt.selection_single(empty = 'none', fields = ['game_minute'])

base = alt.Chart(full_data_sub).add_selection(selector)


ticks = base.mark_tick(size = 200, color = 'red', thickness = 5).encode(
    x = 'game_minute',
    opacity = alt.condition(selector, alt.value(1), alt.value(0.25)),
    color = alt.Color('type', scale = alt.Scale(domain = ['goals','hits','shots'], range = ['#66c2a5', '#fc8d62', '#8da0cb'])),
    tooltip=['Play Description']
)

dots = base.mark_circle(size=200, color = 'steelblue').encode(
    x = alt.X('x', axis = alt.Axis(labels = False, ticks = False, title = '', grid = False)),
    y = alt.X('y', axis = alt.Axis(labels = False, ticks = False, title = '', grid = False)),
    tooltip=['Play Description'],
    color = alt.Color('type', legend = alt.Legend(title = 'Event Type', values = ['goals', 'hits', 'shots'], orient = 'top'), scale = alt.Scale(domain = ['goals','hits','shots'], range = ['#66c2a5', '#fc8d62', '#8da0cb'])) , #alt.condition(selector, alt.value('red'), alt.value('steelblue'), legend = None),
    size = alt.condition(selector, alt.value(500), alt.value(200), legend = None), #,
    opacity = alt.condition(selector, alt.value(1.0), alt.value(0.35))
)

lines = alt.Chart(win_prob_sub).mark_line(size = 4, color = 'gray').encode(
    x = alt.X('game_minute', title = 'Game Minute'),
    y = alt.Y('win_prob', scale = alt.Scale(domain = [0, 1]), title = 'Win Probability')#,
    #color = alt.Color('game', legend = alt.Legend(title = 'Event Type', values = ['goals', 'hits', 'shots'], orient = 'top'))
)


box = pd.DataFrame({
    'x': [-72, 72,  85,  93, 95,   97,  99,  100,    100,99,97,95,93,85,72,        -72,  -85,-93,-95,-97,-99,-100,          -100,-99,-97,-95,-93,-85,-72],
    'y': [-42.5, -42.5,-42,-40,-38, -36.5, -35, -30,     30,35,36.5,38,40,42,42.5,     42.5, 42, 40, 38, 36.5,35,30,            -30,-35,-36.5,-38,-40,-42,-42.5]
}).reset_index()

base = alt.Chart(box).mark_line(color='gray').encode(
    alt.X('x'),
    alt.Y('y'),
    order='index'
)

center_line = pd.DataFrame({
    'x': [0,0],
    'y': [-42.5, 42.5]
}).reset_index()

center = alt.Chart(center_line).mark_line(color='red').encode(
    alt.X('x'),
    alt.Y('y'),
    order='index'
)

blue_line_1 = pd.DataFrame({
    'x': [-25,-25],
    'y': [-42.5, 42.5]
}).reset_index()

blue_line_2 = pd.DataFrame({
    'x': [25,25],
    'y': [-42.5, 42.5]
}).reset_index()

blue_1 = alt.Chart(blue_line_1).mark_line(color='steelblue').encode(
    alt.X('x'),
    alt.Y('y'),
    order='index'
)

blue_2 = alt.Chart(blue_line_2).mark_line(color='steelblue').encode(
    alt.X('x'),
    alt.Y('y'),
    order='index'
)

goal_line_1 = pd.DataFrame({
    'x': [-89,-89],
    'y': [-40.5, 40.5]
}).reset_index()

goal_1 = alt.Chart(goal_line_1).mark_line(color='red').encode(
    alt.X('x'),
    alt.Y('y'),
    order='index'
)

goal_line_2 = pd.DataFrame({
    'x': [89,89],
    'y': [-40.5, 40.5]
}).reset_index()

goal_2 = alt.Chart(goal_line_2).mark_line(color='red').encode(
    alt.X('x'),
    alt.Y('y'),
    order='index'
)

goal_left = pd.DataFrame({
    'x': [-89, -86, -86, -89, -89],
    'y': [-4, -4,  4, 4, -4]
}).reset_index()

goal_l = alt.Chart(goal_left).mark_line(color='red').encode(
    alt.X('x'),
    alt.Y('y'),
    order='index'
)

goal_right = pd.DataFrame({
    'x': [89, 86, 86, 89, 89],
    'y': [-4, -4,  4, 4, -4]
}).reset_index()

goal_r = alt.Chart(goal_right).mark_line(color='red').encode(
    alt.X('x'),
    alt.Y('y'),
    order='index'
)

all_circles = pd.DataFrame({
    'x': [0, 58, 58, -58, -58],
    'y': [0, -22, 22, 22, -22]
}).reset_index()

circles = alt.Chart(all_circles).mark_circle(color='red', size = 2500, filled = False).encode(
    alt.X('x'),
    alt.Y('y'),
    order='index'
)

small_circles = alt.Chart(all_circles).mark_circle(color='red', size = 50, filled = True).encode(
    alt.X('x'),
    alt.Y('y'),
    order='index'
)

#base + center + blue_1 + blue_2 + goal_1 + goal_2 + goal_l + goal_r + circles + small_circles +dots


chart = alt.layer(
    base,center,blue_1,blue_2,goal_1, goal_2, goal_l,goal_r,circles,small_circles, dots#, dots_goals #+ dots_shots 
).properties(width=650, height=400)#.add_selection(selector)







win_plot = alt.layer(ticks, lines).properties(width=650, height=200)

test = alt.vconcat(chart, win_plot)#.configure_axis(disable = True).properties(width=650, height=425)#.add_selection(selector)


#tab1, tab2 = st.tabs(["Event Explorer", "Player Stats"])

#with tab1:
st.markdown('## Event Explorer')
st.markdown('The below rink plot shows all shots, hits, and goals for the selected Penguins game (using the dropdown above).  The lower plot shows the probability that the Penguins will win the game over time.  This plot also shows each event as a vertical bar using the same color scheme.  Clicking on a dot or bar will highlight the event in the other chart.  This visualization approach allows for exploration of time, space, and context of each important play in the game.')
if len(game_sel) == 0:
    st.markdown('### No game data to display - please pick at least one game!')
else:
    st.altair_chart(test)
    st.markdown('Win probability is determined using a logistic regression model using goals, hits, and shots as well as their interactions with game time as features.  The most important feature is the interaction between goal differential and time remaining in the game.  In other words, being ahead in the game is more associated with winning as time runs out.')


    

st.markdown("This project was created by Ian Kloo for the [Interactive Data Science](https://dig.cmu.edu/ids2022) course at [Carnegie Mellon University](https://www.cmu.edu).")




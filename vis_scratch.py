import altair as alt
import pandas as pd


hits = pd.read_csv('pens_hits.csv')

hits_sub = hits[1:1000]

dots = alt.Chart(hits_sub).mark_circle(size=60).encode(
    x='x',
    y ='y',
    tooltip=['hitter','hittee']
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

base + center + blue_1 + blue_2 + goal_1 + goal_2 + goal_l + goal_r + circles + small_circles +dots


alt.layer(
    base,center,blue_1,blue_2,goal_1, goal_2, goal_l,goal_r,circles,small_circles, dots
).configure_axis(disable = True)




win_prob = pd.read_csv('win_prob.csv')
win_prob_game = win_prob[win_prob['game'] == 2017030144]

win_prob_game = win_prob[win_prob['game'].isin([2017030144, 2017030143])]
win_prob_game = win_prob_game.assign(game = win_prob_game['game'].astype(str))

lines = alt.Chart(win_prob_game).mark_line().encode(
    x = 'game_minute',
    y = 'win_prob',
    color = 'game'
)

ticks = alt.Chart(win_prob_game).mark_tick(size = 300, opacity = 0).encode(
    x = 'game_minute'
)

alt.layer(lines, ticks)



import numpy as np

np.random.seed(0)

n_objects = 20
n_times = 50

# Create one (x, y) pair of metadata per object
locations = pd.DataFrame({
    'id': range(n_objects),
    'x': np.random.randn(n_objects),
    'y': np.random.randn(n_objects)
})

# Create a 50-element time-series for each object
timeseries = pd.DataFrame(np.random.randn(n_times, n_objects).cumsum(0),
                          columns=locations['id'],
                          index=pd.RangeIndex(0, n_times, name='time'))

# Melt the wide-form timeseries into a long-form view
timeseries = timeseries.reset_index().melt('time')

# Merge the (x, y) metadata into the long-form view
timeseries['id'] = timeseries['id'].astype(int)  # make merge not complain
data = pd.merge(timeseries, locations, on='id')

# Data is prepared, now make a chart

selector = alt.selection_single(empty='all', fields=['id'])

base = alt.Chart(data).properties(
    width=250,
    height=250
).add_selection(selector)

points = base.mark_point(filled=True, size=200).encode(
    x='mean(x)',
    y='mean(y)',
    color=alt.condition(selector, 'id:O', alt.value('lightgray'), legend=None),
)

timeseries = base.mark_line().encode(
    x='time',
    y=alt.Y('value', scale=alt.Scale(domain=(-15, 15))),
    color=alt.Color('id:O', legend=None)
).transform_filter(
    selector
)

points | timeseries

alt.vconcat(points, timeseries)

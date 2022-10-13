#------Prepare data for streamlit app------#
#---October 2022---#
#---By: Ian Kloo---#

#this script pulls data from the NHL's undocumented API and parses it into a format that supports the streamlit app in this repo.

#---import libraries---#
import requests
import pandas as pd
import tqdm
#https://stackoverflow.com/questions/66040295/how-to-include-interaction-variables-in-logit-statsmodel-python
import statsmodels.api as sm
import statsmodels.formula.api as smf

#---get games---#
#penguins are teamId 5, go back to beginning of 2016 season
res = requests.get('https://statsapi.web.nhl.com/api/v1/schedule?teamId=5&startDate=2016-10-01&endDate=2022-06-01')
games = res.json()

#extract relevant game info
winner = []
loser = []
game_pks = []
game_date = []
dates = games.get('dates')
for d in dates:
    games_on_date = d.get('games')
    for g in games_on_date:
        game_pks.append(g.get('gamePk'))
        game_date.append(g.get('gameDate')[:10])
        
        away = g.get('teams').get('away').get('score')
        home = g.get('teams').get('home').get('score')

        if away > home:
            winner.append(g.get('teams').get('away').get('team').get('name'))
            loser.append(g.get('teams').get('home').get('team').get('name'))
        else:
            winner.append(g.get('teams').get('home').get('team').get('name'))
            loser.append(g.get('teams').get('away').get('team').get('name'))
            
game_df = pd.DataFrame({'date': game_date, 'game': game_pks, 'winner': winner, 'loser': loser})

#create descriptive tooltip column that will be displayed in app
tooltip = []
for index, row in game_df.iterrows():
    if row['winner'] == 'Pittsburgh Penguins':
        tooltip.append(row['date'] + " - " + row['winner'] + ' beat ' + row['loser'])
    else:
        tooltip.append(row['date'] + " - " + row['loser'] + ' lost to ' + row['winner'])
game_df['Game Description'] = tooltip

#---extract stats from games---#
#loop over all gamesIds, get details for each (call to API), extract hits, shots, goals
#each stat has different columns - for example, goals have a scorer and up to 2 assisters, hits have a hitter and hittee, etc...
#...so i'll make a table for each and combine them later
hit_tbl_list = []
shot_tbl_list = []
goal_tbl_list = []

for pk in tqdm.tqdm(game_pks):
    #get game content
    res = requests.get('https://statsapi.web.nhl.com/api/v1/game/'+str(pk)+'/feed/live')
    game = res.json()

    #process all plays in a game
    teams = [game.get('gameData').get('teams').get('away').get('name'), game.get('gameData').get('teams').get('home').get('name')]
    opp = [x for x in teams if x != 'Pittsburgh Penguins'][0]
    plays = game.get('liveData').get('plays').get('allPlays')

    hitter = []
    hittee = []
    hit_x = []
    hit_y = []
    hit_time = []
    hit_per = []

    shot_player = []
    shot_result = []
    shot_x = []
    shot_y = []
    shot_time = []
    shot_per = []

    goal_table_list = []

    for p in plays:
        if p.get('result').get('event') == 'Hit':
            if p.get('team').get('id') == 5:
                hitter.append(p.get('players')[0].get('player').get('fullName'))
                hittee.append(p.get('players')[1].get('player').get('fullName'))
                hit_x.append(p.get('coordinates').get('x'))
                hit_y.append(p.get('coordinates').get('y'))
                hit_time.append(p.get('about').get('periodTime'))
                hit_per.append(p.get('about').get('period'))
        elif p.get('result').get('event') in ['Shot', 'Missed Shot']:
            if p.get('team').get('id') == 5:
                shot_player.append(p.get('players')[0].get('player').get('fullName'))
                if p.get('result').get('event') == 'Shot':
                    shot_result.append('on_goal')
                else:
                    shot_result.append('miss')
                shot_x.append(p.get('coordinates').get('x'))
                shot_y.append(p.get('coordinates').get('y'))
                shot_time.append(p.get('about').get('periodTime'))
                shot_per.append(p.get('about').get('period'))
        elif p.get('result').get('event') == 'Goal':
            if p.get('team').get('id') == 5:

                goal_player = ''
                goal_assist_1 = ''
                goal_assist_2 = ''
                goal_goalie = ''
                goal_x = ''
                goal_y = ''
                goal_time = ''
                goal_per = ''

                players = p.get('players')
                for pl in players:
                    if pl.get('playerType') == 'Scorer':
                        goal_player = pl.get('player').get('fullName')
                    elif pl.get('playerType') == 'Assist':
                        if goal_assist_1 == '':
                            goal_assist_1 = pl.get('player').get('fullName')
                        else:
                            goal_assist_2 = pl.get('player').get('fullName')
                    elif pl.get('playerType') == 'Goalie':
                        goal_goalie = pl.get('player').get('fullName')
                goal_x = p.get('coordinates').get('x')
                goal_y = p.get('coordinates').get('y')
                goal_time = p.get('about').get('periodTime')
                goal_per = p.get('about').get('period')

                tmp = pd.DataFrame({'scorer': [goal_player], 'assist_1': [goal_assist_1], 'assist_2': [goal_assist_2], 'goalie': [goal_goalie], 
                              'x': [goal_x], 'y': [goal_y], 'per': [goal_per], 'per_time': [goal_time]})
                goal_table_list.append(tmp)


    hit_table = pd.DataFrame({'hitter': hitter, 'hittee': hittee, 'x': hit_x, 'y': hit_y, 'per': hit_per, 'per_time': hit_time})
    hit_table['game'] = game.get('gameData').get('game').get('pk')
    hit_table['date'] = game.get('gameData').get('datetime').get('dateTime')     
    hit_table['opponent'] = opp
    hit_tbl_list.append(hit_table)

    shot_table = pd.DataFrame({'shooter': shot_player, 'result': shot_result, 'x': shot_x, 'y': shot_y, 'per': shot_per, 'per_time': shot_time})
    shot_table['game'] = game.get('gameData').get('game').get('pk')
    shot_table['date'] = game.get('gameData').get('datetime').get('dateTime')        
    shot_table['opponent'] = opp
    shot_tbl_list.append(shot_table)

    if len(goal_table_list) > 0:
        goal_table = pd.concat(goal_table_list)
        goal_table['game'] = game.get('gameData').get('game').get('pk')
        goal_table['date'] = game.get('gameData').get('datetime').get('dateTime')        
        goal_table['opponent'] = opp
        goal_tbl_list.append(goal_table)


hits = pd.concat(hit_tbl_list).reset_index(drop = True)
shots = pd.concat(shot_tbl_list).reset_index(drop = True)
goals = pd.concat(goal_tbl_list).reset_index(drop = True)

#create a column in each table that shows the game minute each event takes place
#for example, if something is in the 2nd period, 4:15 game time, we want to show this as happening in the 24th minute (20 minute periods)
minute = []
for i in range(0, len(hits)):
    minute.append((int(hits['per_time'][i][:2]) + hits['per'][i]*20)-20)
hits['game_minute'] = minute 

minute = []
for i in range(0, len(shots)):
    minute.append((int(shots['per_time'][i][:2]) + shots['per'][i]*20)-20)
shots['game_minute'] = minute 

minute = []
for i in range(0, len(goals)):
    minute.append((int(goals['per_time'][i][:2]) + goals['per'][i]*20)-20)
goals['game_minute'] = minute 

#---reformat data to play nice with Altair---#
#need one long dataframe with all of this data to support sharing select filter between charts
#will add a "type" column to each and then concat the tables together. there will be a lot of NA values...
#...for example, "goals" don't have a "hitter" feature, so this will always be NA
hits['type'] = 'hits'
shots['type'] = 'shots'
goals['type'] = 'goals'

full_data = pd.concat([shots, hits, goals])

#create tooltip - has to be different for each type since we have to point to single column in Altair
tooltip = []
for index, row in full_data.iterrows():
    if row['type'] == 'hits':
        tooltip.append(row['hitter'] + ' hit ' + row['hittee'])
    elif row['type'] == 'shots':
        if row['result'] == 'on_goal':
            tooltip.append(row['shooter'] + ' shot on goal')
        else:
            tooltip.append(row['shooter'] + ' shot missed')
    else:
        if (pd.isnull(row['assist_1'])) & (pd.isnull(row['assist_2'])):
            tooltip.append(row['scorer'] + ' scored, unassisted')
        elif pd.isnull(row['assist_2']):
            tooltip.append(row['scorer'] + ' scored, primary assist by ' + row['assist_1'])
        else:
            tooltip.append(row['scorer'] + ' scored, assisted by ' + row['assist_1'] + ' and ' + row['assist_2'])

full_data['Play Description'] = tooltip

#generate the game descriptions to be used in the dropdown - this becomes the filtering key
desc = []
for index, row in full_data.iterrows():
    desc.append(list(game_df[game_df['game'] == row['game']]['Game Description'])[0])
    
full_data['Game Description'] = desc
full_data.to_csv('data/full_data.csv', index = False)


#---win probability model---#

#--win probability data--#
#this data is similar to full_data pulled above, but it includes data from both teams.  Specifically, it calculates the 
#hits, shots, and goal differentials (penguins stat - other team stat).  This could be done as part of the initial loop above
#but I thought keeping it separate was cleaner.

#this is all very similar to above, so I won't duplicate those comments
res = requests.get('https://statsapi.web.nhl.com/api/v1/schedule?teamId=5&startDate=2016-10-01&endDate=2022-06-01')
games = res.json()

#extract game ids
game_pks = []
dates = games.get('dates')
for d in dates:
    games_on_date = d.get('games')
    for g in games_on_date:
        game_pks.append(g.get('gamePk'))

hit_tbl_list = []
shot_tbl_list = []
goal_tbl_list = []

for pk in tqdm.tqdm(game_pks):
    #get game content
    res = requests.get('https://statsapi.web.nhl.com/api/v1/game/'+str(pk)+'/feed/live')
    game = res.json()

    #process all plays in a game
    teams = [game.get('gameData').get('teams').get('away').get('name'), game.get('gameData').get('teams').get('home').get('name')]
    opp = [x for x in teams if x != 'Pittsburgh Penguins'][0]
    plays = game.get('liveData').get('plays').get('allPlays')

    hitter = []
    hittee = []
    hit_x = []
    hit_y = []
    hit_time = []
    hit_per = []
    hit_team = []

    shot_player = []
    shot_result = []
    shot_x = []
    shot_y = []
    shot_time = []
    shot_per = []
    shot_team = []

    goal_table_list = []

    for p in plays:
        if p.get('result').get('event') == 'Hit':
            if p.get('team').get('id') == 5:
                hit_team.append('pitt')
            else:
                hit_team.append('other')
            hitter.append(p.get('players')[0].get('player').get('fullName'))
            hittee.append(p.get('players')[1].get('player').get('fullName'))
            hit_x.append(p.get('coordinates').get('x'))
            hit_y.append(p.get('coordinates').get('y'))
            hit_time.append(p.get('about').get('periodTime'))
            hit_per.append(p.get('about').get('period'))
        elif p.get('result').get('event') in ['Shot', 'Missed Shot']:
            if p.get('team').get('id') == 5:
                shot_team.append('pitt')
            else:
                shot_team.append('other')
            shot_player.append(p.get('players')[0].get('player').get('fullName'))
            if p.get('result').get('event') == 'Shot':
                shot_result.append('on_goal')
            else:
                shot_result.append('miss')
            shot_x.append(p.get('coordinates').get('x'))
            shot_y.append(p.get('coordinates').get('y'))
            shot_time.append(p.get('about').get('periodTime'))
            shot_per.append(p.get('about').get('period'))
        elif p.get('result').get('event') == 'Goal':

            goal_player = ''
            goal_assist_1 = ''
            goal_assist_2 = ''
            goal_goalie = ''
            goal_x = ''
            goal_y = ''
            goal_time = ''
            goal_per = ''
            goal_team = ''

            if p.get('team').get('id') == 5:
                goal_team = 'pitt'
            else:
                goal_team = 'other'

            players = p.get('players')
            for pl in players:
                if pl.get('playerType') == 'Scorer':
                    goal_player = pl.get('player').get('fullName')
                elif pl.get('playerType') == 'Assist':
                    if goal_assist_1 == '':
                        goal_assist_1 = pl.get('player').get('fullName')
                    else:
                        goal_assist_2 = pl.get('player').get('fullName')
                elif pl.get('playerType') == 'Goalie':
                    goal_goalie = pl.get('player').get('fullName')

            goal_x = p.get('coordinates').get('x')
            goal_y = p.get('coordinates').get('y')
            goal_time = p.get('about').get('periodTime')
            goal_per = p.get('about').get('period')

            tmp = pd.DataFrame({'scorer': [goal_player], 'assist_1': [goal_assist_1], 'assist_2': [goal_assist_2], 'goalie': [goal_goalie], 
                          'x': [goal_x], 'y': [goal_y], 'per': [goal_per], 'per_time': [goal_time], 'team': [goal_team]})
            goal_table_list.append(tmp)


    hit_table = pd.DataFrame({'hitter': hitter, 'hittee': hittee, 'x': hit_x, 'y': hit_y, 'per': hit_per, 'per_time': hit_time, 'team': hit_team})
    hit_table['game'] = game.get('gameData').get('game').get('pk')
    hit_table['date'] = game.get('gameData').get('datetime').get('dateTime')     
    hit_table['opponent'] = opp
    hit_tbl_list.append(hit_table)

    shot_table = pd.DataFrame({'shooter': shot_player, 'result': shot_result, 'x': shot_x, 'y': shot_y, 'per': shot_per, 'per_time': shot_time, 'team': shot_team})
    shot_table['game'] = game.get('gameData').get('game').get('pk')
    shot_table['date'] = game.get('gameData').get('datetime').get('dateTime')        
    shot_table['opponent'] = opp
    shot_tbl_list.append(shot_table)

    if len(goal_table_list) > 0:
        goal_table = pd.concat(goal_table_list)
        goal_table['game'] = game.get('gameData').get('game').get('pk')
        goal_table['date'] = game.get('gameData').get('datetime').get('dateTime')        
        goal_table['opponent'] = opp
        goal_tbl_list.append(goal_table)


hits = pd.concat(hit_tbl_list).reset_index(drop = True)
shots = pd.concat(shot_tbl_list).reset_index(drop = True)
goals = pd.concat(goal_tbl_list).reset_index(drop = True)

minute = []
for i in range(0, len(hits)):
    minute.append((int(hits['per_time'][i][:2]) + hits['per'][i]*20)-20)
hits['game_minute'] = minute 

minute = []
for i in range(0, len(shots)):
    minute.append((int(shots['per_time'][i][:2]) + shots['per'][i]*20)-20)
shots['game_minute'] = minute 

minute = []
for i in range(0, len(goals)):
    minute.append((int(goals['per_time'][i][:2]) + goals['per'][i]*20)-20)
goals['game_minute'] = minute 

#now we can create the model data by calculating the differentials for every game minute
games = list(set(goals.game))
diff_out = []
for g in tqdm.tqdm(games):
    hits_sub = hits[hits['game'] == g]
    shots_sub = shots[shots['game'] == g]
    goals_sub = goals[goals['game'] == g]

    min_time = 0
    max_time = max([goals_sub['game_minute'].max(), hits_sub['game_minute'].max(), shots_sub['game_minute'].max()])

    goal_diff = 0
    hit_diff = 0
    shot_diff = 0
    diff_tables = []
    for i in range(min_time, int(max_time) + 1):
        #update all diffs
        hits_tmp = hits_sub[hits_sub['game_minute'] == i]
        for index, row in hits_tmp.iterrows():
            if row['team'] == 'pitt':
                hit_diff = hit_diff + 1
            else:
                hit_diff = hit_diff - 1

        goals_tmp = goals_sub[goals_sub['game_minute'] == i]
        for index, row in goals_tmp.iterrows():
            if row['team'] == 'pitt':
                goal_diff = goal_diff + 1
            else:
                goal_diff = goal_diff - 1

        shots_tmp = shots_sub[shots_sub['game_minute'] == i]
        for index, row in shots_tmp.iterrows():
            if row['team'] == 'pitt':
                shot_diff = shot_diff + 1
            else:
                shot_diff = shot_diff - 1

        diff_tables.append(pd.DataFrame({'game_minute': [i], 'hit_diff': [hit_diff], 'shot_diff': [shot_diff], 'goal_diff': [goal_diff]}))

    diff_tbl = pd.concat(diff_tables).reset_index(drop = True)  
    if list(diff_tbl['goal_diff'])[-1] > 0:
        diff_tbl['win'] = 1
    else:
        diff_tbl['win'] = 0
    diff_tbl['game'] = g
    
    diff_out.append(diff_tbl)

df_model = pd.concat(diff_out).reset_index(drop = True)

#--logistic regression model--#
#running a logistic regression with each stat and its interaction with game time
#help from https://stackoverflow.com/questions/66040295/how-to-include-interaction-variables-in-logit-statsmodel-python
res = smf.logit(formula = 'win ~ game_minute:hit_diff + game_minute:shot_diff + game_minute:goal_diff', data = df_model).fit()
#res.summary()

#use the model to predict win probabilities for each, store in column
df_model['win_prob'] = res.predict(df_model)

#generate the game descriptions to be used in the dropdown - this becomes the filtering key
desc = []
for index, row in df_model.iterrows():
    desc.append(list(game_df[game_df['game'] == row['game']]['Game Description'])[0])
    
df_model['Game Description'] = desc
df_model.to_csv('data/win_prob.csv', index = False)



import pandas as pd
from itertools import combinations
import random

#accepts a csv file with two columns: "Name" and "Rating". making the csv is outside the scope, but a google form can easily generate one
dat = pd.read_csv('form_data.csv')

courts = 2
rounds = 5
numpairs_round=2*courts

players_rate = list(dat[["Name","Rating"]].to_records(index=False))
#players_rate=[('raga', 3), ('prav', 3), ('savb', 1), ('disc', 2), ('ricd', 3), ('abs', 1), ('bane', 3), ('cotf', 3),('bulg', 1),('zilh',1),('kih',2),('kilj',3),('yek',1),('rewl',1),('ttm',2),('fgn',3),('hjko',3)]

players=[x for (x,y) in players_rate]
dtn_cnt = dict((x,0) for x in players)
# dtn=dict((x,y) for (x,y) in players_rate)
# or below
dtn={}
for (x,y) in players_rate:
        dtn.setdefault(x,y)

players_per_round = courts * 4
# rounds_per_player = (rounds * players_per_round)/len(players)
# the below picks up players_per_round players from the full list of players.
# This is a fair pickup meaning no player will sit out morethan one round unless we have more than double the players than courts.
# This gives a good balance if the players are a little more than required per court. For example 5-6 players for each court.
all_rounds = list(combinations(players,players_per_round))
ll=[]
ll.append(all_rounds[0])
all_rounds.remove(all_rounds[0])
for i in range(len(all_rounds)):
        [x for x in all_rounds if set(set(players).difference(set(ll[-1]))).isdisjoint(set(players).difference(set(x))) and (ll.append(x) or all_rounds.remove(x))]
if all_rounds:
        ll.extend(all_rounds)

# this will generate all possible pairs with each player getting a chance to play for each player.
# the logic makes sure once a player is chosen for a court, he is not in any other court in the same round.
# AI: could be simplified
full_fixtures=[]
for round in ll:
        r_pl_f=[x for x in players if x in round]
        full_pairs = list(combinations(r_pl_f,2))
        r_f_p = [(a,b,(dtn[a]+dtn[b])/2) for (a,b) in full_pairs]
        #r_f_p.sort(key=lambda x: x[2])
        random.shuffle(r_f_p)
        r_f_p_save = r_f_p.copy()
        fix_court_iter=[]
        while r_f_p:
                p1=r_f_p.pop()
                if p1 in full_fixtures:
                        continue
                fix_court_iter.append(p1)
                r_f_p=[(a,b,c) if not any(a in e or b in e for e in fix_court_iter) else 'RE' for (a,b,c) in r_f_p]
                r_f_p=list(filter(lambda a: a != 'RE', r_f_p))
        if len(fix_court_iter) < numpairs_round:
                r_f_p = r_f_p_save.copy()
                r_f_p=[(a,b,c) if not any(a in e or b in e for e in fix_court_iter) else 'RE' for (a,b,c) in r_f_p]
                r_f_p=list(filter(lambda a: a != 'RE', r_f_p))
                random.shuffle(r_f_p)
                while r_f_p and len(fix_court_iter) < numpairs_round:
                        p2 = r_f_p.pop()
                        if p2 not in full_fixtures:
                                fix_court_iter.append(p2)
        if len(fix_court_iter) == numpairs_round:
                full_fixtures.extend(fix_court_iter)
        if full_fixtures[-1] != ('--','--',0):
                full_fixtures.append(('--', '--', 0))
                full_fixtures.append(('--', '--', 0))

# Here pairs who didn't get chance will get chance if we can't balance above.
part_fix=[(a,b) for (a,b,c) in full_fixtures if a !='--']
full_pairs = list(combinations(players,2))
diff_pairs=list(set(full_pairs).difference(set(part_fix)))
dpr=[(a,b,(dtn[a]+dtn[b])/2) for (a,b) in diff_pairs]
#dpr.sort(key=lambda x: x[2])
while dpr and len(dpr) > numpairs_round-1:
        fix_court_iter=[]
        while dpr and len(fix_court_iter) < numpairs_round:
                p1=dpr.pop()
                if p1 in full_fixtures:
                        continue
                fix_court_iter.append(p1)
                dpr=[(a,b,c) if not any(a in e or b in e for e in fix_court_iter) else 'RE' for (a,b,c) in dpr]
                dpr=list(filter(lambda a: a != 'RE', dpr))
        print(fix_court_iter)
        if len(fix_court_iter) == numpairs_round:
                full_fixtures.extend(fix_court_iter)
        if full_fixtures[-1] != ('--','--',0):
                full_fixtures.append(('--', '--', 0))
                full_fixtures.append(('--', '--', 0))
        if len(fix_court_iter) < numpairs_round:
                full_fixtures.append(('--', '--', 0))
                full_fixtures.append(('--', '--', 0))
                full_fixtures.extend(fix_court_iter)
                break
        part_fix=[(a,b) for (a,b,c) in full_fixtures if a !='--']
        diff_pairs=list(set(full_pairs).difference(set(part_fix)))
        dpr=[(a,b,(dtn[a]+dtn[b])/2) for (a,b) in diff_pairs]
        dpr.sort(key=lambda x: x[2])

it=iter(full_fixtures)
final=list(zip(it,it))

# Now output (i.e. the final fixtures) goes into another csv file "full_fixtures.csv"
df=pd.DataFrame()
# df = pd.DataFrame.from_records(final,columns=['Team1','Team2'])

df.insert(0,'Team1', [a+" , "+b if a!='--' else '  --' for ((a,b,c),(d,e,f)) in final])
df.insert(1,'Team1 avg', [c if a!='--' else '  --' for ((a,b,c),(d,e,f)) in final])
df.insert(2,'Fixtures','vs',True)
df.insert(3,'Team2', [d+" , "+e if d!='--' else '  --' for ((a,b,c),(d,e,f)) in final])
df.insert(4,'Team2 avg', [f if d!='--' else '  --' for ((a,b,c),(d,e,f)) in final])
df.insert(5,'','',True)
df.insert(6,'','',True)
df.insert(7,'players',pd.Series(players),True)
df.insert(8,'count',pd.Series(['=COUNTIF(B2:F200,"*"&I'+str(i)+'&"*")' for i in range(2,len(players)+2)]),True)
df.insert(9, 'players rating',pd.Series([b for (a,b) in players_rate]),True)
df.to_csv('full_fixtures.csv')

# test prints to check the fixtures
print(len(full_fixtures))
print(len(part_fix))
print(len(diff_pairs))

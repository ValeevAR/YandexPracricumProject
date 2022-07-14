# This a study project

# The project is devoted to online store , which sells computer games all over the world.
# Historical data on game sales, user and expert ratings, genres and platforms are available from open sources.
# You need to identify the patterns that determine the success of the game. This will allow you to bet on a potentially popular product and plan advertising campaigns.

import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats as st

df = pd.read_csv('datasets/games.csv')
print(df)
df.info()

# We conclude that there are omissions. Moreover, there are a lot of them in a number of columns, so it would be incorrect to simply delete the omissions.
# We see that some of the data types are received incorrectly. Years can be represented as an integer int type
# Let's check duplicates.

df[df.duplicated()]

# It can be seen that there are no duplicates
# The columns Platform, Genre and Rating are categorical. Let's check if there are errors in writing

for col in ['Platform', 'Genre', 'Rating']:
    print('Столбец', col)
    print(df[col].unique())

# It can be seen that there are no problems with writing categorical types
# Let's examine what data is in the Critic_Score and User_Score columns:

for col in ['Critic_Score', 'User_Score']:
    print('Столбец', col)
    print(df[col].unique())

# In Critic_Score, the values are integers, you can replace them with int
# In User_Score, the values are fractional, but with this there is tbd - To Be Determined. That is, in fact, it is a pass.

# **Conclusions from step 1**
# - there are many omissions
# - years can be represented as an integer int type
# - in Critic_Score, the values are integers, can be replaced with int
# - in User_Score there is tbd - To Be Determined. That is, in fact, it is a pass. Can be replaced with a real type
# - there are no duplicates
# - there are no problems with writing categorical types

df.columns = [i.lower() for i in list(df.columns)]
print(df.columns)

# Convert the data to the desired types. As previously defined, the year_of_release, critic_score type is replaced by the int type. And the user_score type on float
# At the same time, we will replace the omissions in advance with "-1".
# 'tbd' will be replaced with "-1".
# So where the ESRB rating is not affixed, we will replace it with 'RP' - ("Rating Pending") — "Rating is expected":
# There are 2 in the name passes. Since the name is the key identifying parameter, these 2 omissions should be removed

df['year_of_release'] = df['year_of_release'].fillna(-1)
df['year_of_release'] = df['year_of_release'].astype(int)

df['critic_score'] = df['critic_score'].fillna(-1)
df['critic_score'] = df['critic_score'].astype(int)

df['user_score'] = df['user_score'].replace('tbd', -1)
df['user_score'] = df['user_score'].fillna(-1)
df['user_score'] = df['user_score'].astype(float)

df['rating'] = df['rating'].fillna('RP')
df['rating'] = df['rating'].replace('K-A', 'E')

df = df.dropna()

print(df.info())

pd.set_option('chained_assignment', None)

df['platform'] = df['platform'].astype('category')
df['genre'] = df['genre'].astype('category')
df['rating'] = df['rating'].astype('category')
rating_list = ['EC', 'E', 'E10+', 'T', 'M', 'AO', 'RP']
df['rating'].cat.set_categories(rating_list, inplace=True)

print(df.info())

# Let's calculate the total sales in all regions
# Calculate the total sales in all regions and record them in a separate column.

df['sum_sales'] = df['na_sales'] + df['eu_sales'] + df['jp_sales'] + df['other_sales']

print(df.head())

# Analysis of how many games were released in different years

df_games_per_year = df[df['year_of_release'] > 0].pivot_table(index='year_of_release', aggfunc='count', values='name')
df_games_per_year.plot(kind='bar', figsize=(16, 9))

best_games = df_games_per_year = df[df['year_of_release'] > 0].pivot_table(index='platform', aggfunc='count',
                                                                           values='name')
best_games = best_games.sort_values(by=best_games.columns[0], ascending=False).head()
print(best_games)

fig, ax = plt.subplots()

for col in list(best_games.index):
    df_1game_per_year = df[(df['year_of_release'] > 1990) & (df['platform'] == col)].pivot_table(
        index='year_of_release', aggfunc='count', values='name')
    plt.plot(df_1game_per_year)

plt.grid()
ax.set_xlabel('год')
ax.set_ylabel('количество')
ax.set_title('Количество проданных игр за актуальный период для 5 популярных платформ')
ax.legend(best_games.index)
plt.show()

years = []

for col in list(best_games.index):
    df_1game_per_year = df[(df['year_of_release'] > 1990) & (df['platform'] == col)].pivot_table(
        index='year_of_release', aggfunc='count', values='name')
    df_1game_per_year.columns = ['count']

    max_count = df_1game_per_year['count'].max()
    years.append(int(df_1game_per_year[df_1game_per_year['count'] > 0.5 * max_count].count()))

game_life = round(sum(years) / len(years))
print('Средннее время жизни одной платформы:', game_life, 'лет')

dfa = df[df['year_of_release'] > df['year_of_release'].max() - game_life]

dfa_per_year = dfa.pivot_table(index='platform', aggfunc='sum', values='sum_sales', columns='year_of_release')
dfa_per_year.columns = [str(i) for i in range(2017 - game_life, 2017)]
print(dfa_per_year)

platform_list = list(dfa_per_year[dfa_per_year['2016'] > 0]['2016'].dropna().index)
print('Список актуальных платформ на 2016 год:', platform_list)

dfa = dfa.query('platform in @platform_list')
print(dfa)

# Analysis of leading, promising, fading platforms at the time of 2016

dfa_per_year = dfa.pivot_table(index='platform', aggfunc='sum', values='sum_sales', columns='year_of_release')
dfa_per_year.columns = [str(i) for i in range(2017 - game_life, 2017)]
dfa_per_year = dfa_per_year.fillna(0)

print('Данные о продажам платформ по годам (миллионов копий)')
print(dfa_per_year)

print('Лидеры о продажам платформ в 2016 г. (миллионов копий)')
top_sales = dfa_per_year.sort_values(by='2016', ascending=False)['2016']

print(top_sales)

print('Лидером является платформа', top_sales.idxmax(), 'с количеством копий', top_sales.max())

dfa_per_year['change_15_16'] = (dfa_per_year['2016'] / dfa_per_year['2015'] - 1) * 100
print(dfa_per_year.sort_values(by='change_15_16', ascending=False))

dfa_per_year['change_14_15'] = (dfa_per_year['2015'] / dfa_per_year['2014'] - 1) * 100
print(dfa_per_year.sort_values(by='change_14_15', ascending=False))

for col in platform_list:
    print('Платформа', col)
    dfa[dfa['platform'] == col].boxplot(column='sum_sales')
    plt.show()

# Analysis of how user reviews and critics affect sales within one popular platform

dfa.query('platform=="PS4" and critic_score>0').plot.scatter(y='sum_sales', x='critic_score')

dfa.query('platform=="PS4" and user_score>0').plot.scatter(y='sum_sales', x='user_score')

dfa.query('platform=="PS4" and critic_score>0')[['sum_sales', 'user_score', 'critic_score']].corr()

for col in platform_list:
    print('Платформа', col)
    dfa_p = dfa.query('platform==@col and critic_score>0')

    print('Корреляция sum_sales и user_score', round(dfa_p['sum_sales'].corr(dfa_p['user_score']), 3))
    print('Корреляция sum_sales и critic_score', round(dfa_p['sum_sales'].corr(dfa_p['critic_score']), 3))

# The general distribution of games by genre. Profitable genres. Genres with high and low sales

dfg = pd.merge(
    df.pivot_table(index='genre', values='name', aggfunc='count'),
    df.pivot_table(index='genre', values='sum_sales', aggfunc='sum'),
    left_index=True, right_index=True)

dfg.columns = ['count', 'sum_sales']
dfg['profit'] = dfg['sum_sales'] / dfg['count']
print('Распределение игр по жанрам - полная таблица')
print(dfg)

print('Распределение игр по жанрам')
print(dfg['count'].sort_values(ascending=False))

print('Распределение по количеству продаж')
print(dfg['sum_sales'].sort_values(ascending=False))

print('Распределение по прибыльности из расчета на одну игру')
print(dfg['profit'].sort_values(ascending=False))

# **Conclusions**
# - Analysis of how many games were released in different years
# - Average lifetime of one platform: 6 years
# - List of current platforms for 2016: '3DS', 'PC', 'PS3', 'PS4', 'PSV', 'Wii', 'WiiU', 'X360', 'XOne'
# - An analysis of the leading, promising, fading platforms at the time of 2016. Probably, the information on 2016 is not yet complete. If you look at the change in the years 2014-2015, then there is a prospect for growth for PS4 and XOne - we choose them as potentially profitable. The X360 and Wii have the worst results.
# - A "box with a mustache" chart on global sales of games by platform has been built. It is concluded that there are usually few sales for an average game. However, there are always a number of "giants" who are strongly out of the mainstream.
# - It can be seen that the correlation between critics' ratings and sales is moderate (corr = 0.41, for example PS4). And there is no correlation between sales and user_score (corr = 0). That is, critics evaluate according to popularity, users evaluate regardless of popularity. We see that the situation is generally similar for other platforms. There is a slight difference with the Wii, and to a lesser extent WiiU and 3DS - their user ratings are slightly more in line with sales.
# - Most games in the Action genre. Action also has the largest number of games sold. Speaking of profitability per game, Platform has the best results, Adventure has the worst.

# Step 4. Portrait of the user of each region

dfp = df.pivot_table(index='platform', values=['eu_sales', 'jp_sales', 'na_sales'], aggfunc='sum')
dfp = dfp.query('platform in @platform_list')

for r in ['eu_sales', 'jp_sales', 'na_sales']:
    dfp[r[0:2]] = dfp[r] / dfp[r].sum() * 100

print(f'Сведения о продажах за года {2017 - game_life}-{2017}')
print(dfp)

for r in ['eu', 'jp', 'na']:
    print('Регион', r.upper())
    print('Популярность актуальных платформ за последние годы, %')
    print(dfp[r].sort_values(ascending=False).head())

df_genre = df.query('platform in @platform_list')
df_genre = df_genre.pivot_table(index='genre', values=['eu_sales', 'jp_sales', 'na_sales'], aggfunc='sum')

for r in ['eu_sales', 'jp_sales', 'na_sales']:
    df_genre[r[0:2]] = df_genre[r] / df_genre[r].sum() * 100

print(f'Сведения о продажах за года {2017 - game_life}-{2017}')
print(df_genre)

for r in ['eu', 'jp', 'na']:
    print('Регион', r.upper())
    print('Популярность жанров за последние годы, %')
    print(df_genre[r].sort_values(ascending=False).head())

rating_list = ['EC', 'E', 'E10+', 'T', 'M', 'AO']

dfp = df.query('platform in @platform_list')
dfp = dfp.query('rating != "RP"')

dfp = dfp.pivot_table(index='rating',
                      values=['eu_sales', 'jp_sales', 'na_sales', 'name'],
                      aggfunc={'eu_sales': 'sum', 'jp_sales': 'sum', 'na_sales': 'sum', 'name': 'count'}
                      )

L = list(dfp.columns)
L[L.index('name')] = 'count'
dfp.columns = L

dfp['r'] = dfp.index

for r in ['eu_sales', 'jp_sales', 'na_sales']:
    dfp[r[0:2]] = dfp[r] / dfp[r].sum() * 100

print(dfp)

print(f'Сведения влияния рейтинга на продаже за года {2017 - game_life}-{2017}, в процентах')

dfp.query('r != "RP"')[['eu', 'jp', 'na']].plot()
plt.grid()
plt.ylabel('количество')
plt.title('Сведения влияния рейтинга на продаже за года 2011-2017, в процентах')
plt.show()

dfp2 = df.query('platform in @platform_list')
dfp2 = dfp2.query('rating != "RP"')

df1 = dfp2[['genre', 'rating']]
df1['1'] = 1

df2 = df1.pivot_table(index='genre', columns='rating', aggfunc='count')
df2 = df2.fillna(0)

df2.columns = [i[1] for i in df2.columns]
df2['AO'] = 0

df2['sum'] = df2.sum(axis=1)

for i in rating_list:
    df2['k_' + i] = df2[i] / df2['sum']

print('Столбцы типа "k_ ..." показывают с какой вероятностью определенный жанр имеет определенный рейтинг')
print(df2)

dfp3 = df.query('platform in @platform_list and rating == "RP"')

df3 = dfp3.pivot_table(index='genre', values='name', aggfunc='count')
df3.columns = ['count']

k_rating = ['k_' + i for i in rating_list]

df3 = pd.merge(df3, df2[k_rating], left_index=True, right_index=True)

for i in rating_list:
    df3['k_' + i] = df3['k_' + i] * df3['count']
    df3['k_' + i] = df3['k_' + i].round(0)

df3.columns = ['count'] + rating_list

print('Расчетное количество рейтингов для каждого из жанров')
print(df3)

RP_rating = pd.DataFrame(data=df3[rating_list].sum(), columns=['RP_count'])

print('Расчетное количество каждого рейтинга для игр с RP')
print(RP_rating)

new_dfr = pd.merge(dfp, RP_rating, left_index=True, right_index=True)

new_dfr['new_count'] = new_dfr['count'] + new_dfr['RP_count']

for i in ['eu', 'jp', 'na']:
    # принимаем, что для учета игр с RP количесто проданных игр пропорционально количестку игр, то за счет их количеста пропорционально увеличивают продажи
    new_dfr['new_' + i] = (new_dfr[i] * (new_dfr['count'] + new_dfr['RP_count']) / new_dfr['count']).fillna(0)

    # приводим сумму по столбцу снова к 100%
    new_dfr['new_' + i] = new_dfr['new_' + i] / new_dfr['new_' + i].sum() * 100

print(new_dfr)

dfp.query('r != "RP"')[['eu', 'jp', 'na']].plot()
plt.grid()
plt.ylabel('количество')
plt.title('Старый график: Сведения влияния рейтинга на продаже за года 2011-2017, в процентах')
plt.show()

new_dfr[['new_eu', 'new_jp', 'new_na']].plot()
plt.grid()
plt.ylabel('количество')
plt.title('Новый график: Сведения влияния рейтинга на продаже за года 2011-2017, в процентах')
plt.show()

# **Conclusions**
# There are three leaders in each of the regions:
# Europe - PS3, X360, Wii platforms
# Japan - 3DS, PS3, Wii platforms
# North America - X360, PS3, Wii platforms
# At the same time, in Europe and North America, in general, preferences are the same. And in Japan, the leader is 3DS, which is not popular in other regions.
# In each of the regions, leaders can be identified:
# Europe - Action, Shooter, Sports genres
# Japan - Action, Shooter, Sports genres
# North America - genres Role-Playing, Action, Sports
# At the same time, in Europe and North America, in general, the preferences are the same. And in Japan, the leader is Role-Playing, which is not popular in other regions.
# We see that the rating affects sales equally in Europe and North America, but in Japan the preferences are different - more games for "for everyone" and teenagers.

# Step 5. Hypothesis testing

alpha = 0.05

sample_1 = df[df['platform'] == 'XOne']['user_score']
sample_2 = df[df['platform'] == 'PC']['user_score']

print(f'Средние значения {sample_1.mean()} и {sample_2.mean()}')

results = st.ttest_ind(sample_1, sample_2)
print('p-значение: ', results.pvalue)
if results.pvalue > alpha:
    print('Выборки одинаковые')
else:
    print('Выборки разные')

sample_1 = df[df['genre'] == 'Action']['user_score']
sample_2 = df[df['genre'] == 'Sports']['user_score']

print(f'Средние значения {sample_1.mean()} и {sample_2.mean()}')

results = st.ttest_ind(sample_1, sample_2)
print('p-значение: ', results.pvalue)
if results.pvalue > alpha:
    print('Выборки одинаковые')
else:
    print('Выборки разные')

# **Conclusions**
# Average user ratings of the Xbox One and PC platforms are different with a 95% probability
# Average user ratings of the genres Action (Eng. "action", action games) and Sports (Eng. "sports competitions") different with a probability of 95%

# ## General conclusion
# The initial data for analysis has been prepared, omissions have been processed, types have been changed, etc.
# Total sales in all regions have been calculated
# An analysis has been carried out of how many games were released in different years
# Average lifetime of one platform: 6 years
# List of current platforms for 2016: '3DS', 'PC', 'PS3', 'PS4', 'PSV', 'Wii', 'WiiU', 'X360', 'XOne'
# Analysis of leading, promising, fading platforms at the time of 2016. Probably, the information on 2016 is not yet complete. If you look at the change in the years 2014-2015, then there is a prospect for growth for PS4 and XOne - we choose them as potentially profitable. The X360 and Wii have the worst results.
# A "box with a mustache" chart on global game sales by platform has been built. It is concluded that there are usually few sales for an average game. However, there are always a number of "giants" who are strongly out of the mainstream.
# It can be seen that the correlation between critics' ratings and sales is moderate (corr = 0.41, for example PS4). And there is no correlation between sales and user_score (corr = 0). That is, critics evaluate according to popularity, users evaluate regardless of popularity. We see that the situation is generally similar for other platforms. There is a slight difference with the Wii, and to a lesser extent WiiU and 3DS - their user ratings are slightly more in line with sales.
# Most games in the Action genre. Action also has the largest number of games sold. Speaking of profitability per game, Platform has the best results, Adventure has the worst.


# In each of the regions, there are three leaders among the platforms:
# - Europe - PS3, X360, Wii platforms
# - Japan - 3DS, PS3, Wii platforms
# - North America - X360, PS3, Wii platforms
# At the same time, in Europe and North America, in general, preferences are the same. And in Japan, the leader is 3DS, which is not popular in other regions.
# In each of the regions, you can single out a leader among genres:
# - Europe - genres Action, Shooter, Sports
# - Japan - Action, Shooter, Sports genres
# - North America - genres of Role-Playing, Action, Sports
# At the same time, in Europe and North America as a whole, preferences are the same. And in Japan, the leader is Role-Playing, which is not popular in other regions.
# We see that the rating affects sales equally in Europe and North America, but in Japan the preferences are different - more games for "for everyone" and teenagers.
# Average user ratings of Xbox One and PC platforms are different with a probability of 95%
# Average user ratings of genres Action (English "action", action games) and Sports (English "sports competitions") different with a probability of 95%

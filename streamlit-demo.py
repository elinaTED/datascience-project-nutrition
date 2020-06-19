# coding=utf-8
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import seaborn as sns
import numpy as np

st.title("Charts for nutrition in the world.")
st.markdown('_If you opened the link, you are interested in your nutrition. That\'s cool!_')
st.markdown('Our goal is to prompt you to pay more attention to what you eat. This website is created exactly for this purpose. So, enjoy! Maybe, you will be surprised with some data.')
st.markdown('To cut a long story short, you should choose a _country_, _age_ and _food_ to be investigated &#129299;')

########################################################################################################################
# Скачиваем данные
db2015 = pd.read_csv("https://raw.githubusercontent.com/fromBAE/stat/master/all_cnty_yr_2015.csv")

ann = pd.read_csv("https://raw.githubusercontent.com/fromBAE/stat/master/annot.csv")
########################################################################################################################
# Составляем список столбцов, которые нужно удалить из-за ненадобности и
# словарик с помощью которого мы потом переименуем столбцы
# Начинаем активно использовать pandas

indeces_del=[]
rename_col = {}
for i in db2015.columns:
    name = i
    if '95' in i:
        indeces_del.append(i)
    else:
        if '_wt_median' in i:
            name = name.replace('_wt_median', '')
        rename_col[i] = name
################################################################################################################################################################################################################################################
# Тут мы удаляем столбцы и переводим данные которые даны в мг в г
# 999 – там где просто взяты средние данные по всем возрастам они нам не нужны
db2015 = db2015.drop(indeces_del, axis=1)
db2015 = db2015.rename(columns = rename_col)
db2015['v41'] = db2015['v41']/1000
db2015['v36'] = db2015['v36']/1000
db2015 = db2015.drop(['female', 'urban', 'edu'], axis=1)
db2015= db2015.replace({999 : float('nan')}).dropna()
########################################################################################################################
# Составляем список возрастов, кодов минералов/еды
ages = [2+5*i for i in range(0,20)]
minerals_code = ['v01','v02','v05','v06','v10','v15','v16','v57','v23','v36', 'v41']
minerals = []
# Создаем словарик, чтобы уметь переводить код в название минерала/еды и наоборот
dic = {}
dic_reverse = {}
for i in minerals_code:
    dic[i]=ann['Variable name'][ann[ann['Code']==i].index[0]]
    dic_reverse[ann['Variable name'][ann[ann['Code'] == i].index[0]]] = i
    minerals.append(ann['Variable name'][ann[ann['Code']==i].index[0]])
# Переименовываем, чтобы все была красивенько
db2015 = db2015.rename(columns = dic)
########################################################################################################################
st.markdown('Here you can see the nutrition for a specified country during living period of its citizens.')

# Создаем кортеж из стран для кнопки выбора страны
boxes = tuple(db2015['countryname'].unique())
country = st.selectbox('Choose a country for investigation',boxes)

# Рисуем Stacked Area Chart для выбранной страны
# (многослойный график, чтобы было понятно,
# сколько всего едят люди в разном возрасте в выбранной стране)

fig1 = go.Figure()
for i in minerals:
    data = list(((db2015.copy()).groupby(['countryname', 'age']).mean()).loc[(country,)][i])
    fig1.add_trace(go.Scatter(
        x=ages, y=data,
        hoverinfo='x+y',
        mode='lines',
        line=dict(width=0.5),
        stackgroup='one', # define stack group
        name = i
    ))
st.plotly_chart(fig1)
########################################################################################################################
# Для матрицы корреляции нам нужны более короткие названия,
# иначе будет неудобно смотреть
dic_cor = {}
dic_cor[dic['v01']] = 'Fruits'
dic_cor[dic['v02']]='Vegetables'
dic_cor[dic['v05']]='Beans'
dic_cor[dic['v06']]='Nuts'
dic_cor[dic['v10']]='Red meat'
dic_cor[dic['v15']]='Sweets'
dic_cor[dic['v16']]='Fruit juices'
dic_cor[dic['v57']]='Milk'
dic_cor[dic['v23']]='Protein'
dic_cor[dic['v36']]='Calcium'
dic_cor[dic['v41']]='Potassium'
dic_cor['superregion2']='superregion2'
dic_cor['countryname']='countryname'
dic_cor['age']='age'
########################################################################################################################
st.markdown('The correlation table should provide you with information about change in nutrition.')

# Создаем красивую кнопочку для выбора возраста
# Но для этого мы должны сделать промежутки возрастов
ages_periods = []
ages_dic = {}
for i in ages:
    ages_periods.append(f"{i-2} – {i+2}")
    ages_dic[f"{i-2} – {i+2}"]=i
ages_periods[len(ages_periods)-1] = '95+'
ages_dic["95+"]=97
ages_dic["All"]='All'
age_raw = st.selectbox(
    'Choose age for correlation table of products consumption',
    tuple(["All"] + ages_periods))
age = ages_dic[age_raw]
########################################################################################################################
# Выбираем нужный тип данных
if age == 'All':
    corr = (db2015.copy().drop(['iso3'], axis=1).rename(columns = dic_cor)[(db2015.copy().drop(['iso3'], axis=1)['countryname']==country)]).drop(['age'], axis=1).corr()
else:
    corr = (db2015.copy().drop(['iso3'], axis=1).rename(columns = dic_cor)[(db2015.copy().drop(['iso3'], axis=1)['age']==age) & (db2015.copy().drop(['iso3'], axis=1)['countryname']==country)]).drop(['age'], axis=1).corr()

# Оставляем только значения под главной диагональю
mask1 = np.triu(corr)

# Строим Heat map для матрицы корреляций
ax = sns.heatmap(
    corr,
    vmin=-1, vmax=1, center=0,
    square=True, mask = mask1,
    cmap='coolwarm', robust=True
)
ax.set_xticklabels(
    ax.get_xticklabels(),
    rotation=20,
    horizontalalignment='right'
)
ax.set_yticklabels(
    ax.get_yticklabels(),
    rotation=45,
    horizontalalignment='right'
)
st.pyplot()
########################################################################################################################
st.markdown('This interactive map can show you the comparison of consumption of specified food among all countries.')

# Выбираем для какого типа еды мы будет строить карту потребления в мире
food = st.selectbox(
    'Choose a type of food',
    minerals)
food_code = dic_reverse[food]
########################################################################################################################
fig = go.Figure(data=go.Choropleth(
    locations = db2015.copy().groupby(['countryname','iso3']).mean().drop(['age'], axis=1).reset_index(level=[0,1])[['countryname', 'iso3', food]]['iso3'],
    z = db2015.copy().groupby(['countryname','iso3']).mean().drop(['age'], axis=1).reset_index(level=[0,1])[['countryname', 'iso3', food]][food],
    text = db2015.copy().groupby(['countryname','iso3']).mean().drop(['age'], axis=1).reset_index(level=[0,1])[['countryname', 'iso3', food]]['countryname'],
    colorscale = 'Blues',
    autocolorscale=False,
    reversescale=True,
    marker_line_color='darkgray',
    marker_line_width=0.5,
    colorbar_tickprefix = 'g',
    colorbar_title = f"Grams",
))


fig.update_layout(
    title_text=f'{food} consumption.',
    geo=dict(
        showframe=False,
        showcoastlines=False,
        projection_type='equirectangular'
    ),
    annotations = [dict(
        x=0.55,
        y=0.1,
        xref='paper',
        yref='paper',
        text='Source: <a href="https://www.globaldietarydatabase.org">\
            Global Dietary Database</a>',
        showarrow = False
    )]
)
st.plotly_chart(fig)

# Снова даем возможность выбора стран и возраста
st.markdown('Here you can compare nutrition of two countries.'
         ' For your convenience, you can choose countries and age independently from the previous one.')
country1 = st.selectbox('The first country:',boxes)
country2 = st.selectbox('The second country:',boxes)
age_new_raw = st.selectbox(
    'Age:',
    tuple(["All"] + ages_periods))
age_new = ages_dic[age_new_raw]
if age_new == 'All':
    table1 = db2015.copy().drop(['iso3'], axis=1).rename(columns = dic_cor)[(db2015.copy().drop(['iso3'], axis=1)['countryname']==country1)]
else:
    table1 = db2015.copy().drop(['iso3'], axis=1).rename(columns = dic_cor)[(db2015.copy().drop(['iso3'], axis=1)['age']==age_new) & (db2015.copy().drop(['iso3'], axis=1)['countryname']==country1)]

if age_new == 'All':
    table2 = db2015.copy().drop(['iso3'], axis=1).rename(columns = dic_cor)[(db2015.copy().drop(['iso3'], axis=1)['countryname']==country2)]
else:
    table2 = db2015.copy().drop(['iso3'], axis=1).rename(columns = dic_cor)[(db2015.copy().drop(['iso3'], axis=1)['age']==age_new) & (db2015.copy().drop(['iso3'], axis=1)['countryname']==country2)]

table1 = pd.DataFrame(table1.drop(['age'], axis =1).mean()).reset_index()
table2 = pd.DataFrame(table2.drop(['age'], axis =1).mean()).reset_index()


labels1 = table1['index']
values1 = table1[0]
fig_new1 = go.Figure(data=[go.Pie(labels=labels1,
                              values=values1,
                              direction ='clockwise',
                              sort=False)])


labels2 = table2['index']
values2 = table2[0]
fig_new2 = go.Figure(data=[go.Pie(labels=labels2,
                              values=values2,
                              direction ='clockwise',
                              sort=False)])
st.markdown(f"Nutrition in {country1}")
st.plotly_chart(fig_new1)
st.markdown(f"Nutrition in {country2}")
st.plotly_chart(fig_new2)
########################################################################################################################


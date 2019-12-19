import matplotlib.pyplot as plt
%matplotlib inline
import numpy as np
import pandas as pd
from pandas import Series,DataFrame  # 导入包

contb1 = pd.read_csv('./2012US_election/contb_01.csv')
contb2 = pd.read_csv('./2012US_election/contb_02.csv')
contb3 = pd.read_csv('./2012US_election/contb_03.csv') #导入数据

# 合并数据, 这个数据就叫contb
contb = pd.concat([contb1, contb2, contb3], axis = 0)
contb.shape  # 查看样本量和变量个数
contb.info() # 查看数据类型
contb.describe() # 描述数据
contb.columns # 查看有哪几个变量

#查看缺失值
cond = contb['contbr_employer'].isnull() # 查看emplyer缺失值
contb[cond]

# 处理缺失值
contb["contbr_employer"].fillna('NOT PROVIDE', inplace = True)
contb.info() # contbr_employer 1001733 non-null object
contb["contbr_occupation"].fillna("NOT PROVIDE", inplace = True)
contb.info()
contb["contbr_st"].fillna("NOT PROVIDE", inplace = True)
contb.info()

# 给一个parties字典，准备分组
parties = {'Bachmann, Michelle': 'Republican',
          'Cain, Herman': 'Republican',
          'Gingrich, Newt': 'Republican',
          'Huntsman, Jon': 'Republican',
          'Johnson, Gary Earl': 'Republican',
          'McCotter, Thaddeus G': 'Republican',
          'Obama, Barack': 'Democrat',
          'Paul, Ron': 'Republican',
          'Pawlenty, Timothy': 'Republican',
          'Perry, Rick': 'Republican',
          "Roemer, Charles E.'Buddy' III": 'Republican',
          'Romney, Mitt': 'Republican',
          'Santorum, Rick': 'Republican'}

# map中用字典映射，增加一列(也就是说map可以实现增加一列)
contb['party'] = contb['cand_nm'].map(parties)

contb['party'].value_counts() # 数支持党派的数量
contb.groupby('party')['contb_receipt_amt'].sum()  # 按党派身份sum计算总和
contb.groupby(['contbr_occupation'])['contb_receipt_amt'].sum() # 按不同职业sum计算总和

# 要进行排序，那么首先就要有一个排序，这里是group_oc
group_oc = contb.groupby(['contbr_occupation'])['contb_receipt_amt'].sum()
group_oc.sort_values(ascending = False)[:60]    # 查看前60个

# 再给一个occupation字典
occupation = {"INFORMATION REQUESTED PER BEST EFFORTS": "NOT PROVIDE",
             "INFORMATION REQUESTED": "NOT PROVIDE",
             "C.E.O": "CEO",
             "LAWYER": "ATTORNEY",
             "SELF": "SELF-EMPLOYED",
             "SELF EMPLOYED": "SELF-EMPLOYED"}

f = lambda x : occupation.get(x, x)   # 有x反馈x，没有反馈默认值x！lambda的好处，不用再写y了
contb["contbr_occupation"] = contb['contbr_occupation'].map(f) # 再次利用map和字典增加一列数据，得到新数据

group_oc = contb.groupby(['contbr_occupation'])['contb_receipt_amt'].sum()
group_oc.sort_values(ascending = False)[:10]


employer = {"INFORMATION REQUESTED PER BEST EFFORTS": 'NOT PROVIDE',
           "INFORMATION REQUESTED": "NOT PROVIDE",
           "SELF": "SELF-EMPLOYED",
           "SELF EMPLOYED": "SELF-EMPLOYED"}

f = lambda x : employer.get(x, x)
contb["contbr_employer"] = contb["contbr_employer"].map(f)

# 还可以两行合起来写，直接排序哪类人的献金最多
contb.groupby(['contbr_employer'])['contb_receipt_amt'].sum().sort_values(ascending = False)[:10]
contb.groupby(['contbr_employer'])['contb_receipt_amt'].sum().sort_values(ascending = False).shape  # shape查看总数

# 数据进一步清理，直接取捐款 > 0, 得到取后的数据，为contb_
contb_ = contb[contb['contb_receipt_amt'] > 0]
contb_.groupby(['cand_nm'])['contb_receipt_amt'].sum().sort_values(ascending = False)  # 分组候选人+政治献金

# 作图：要有得到有排序的作图，那么需要先排序，并把他放进cand_nm_amt
cand_nm_amt = contb_.groupby(['cand_nm'])['contb_receipt_amt'].sum().sort_values(ascending = False)
cand_nm_amt.plot(kind = 'bar')

cand_nm_amt = contb_.groupby(['cand_nm'])['contb_receipt_amt'].sum().sort_values(ascending = True)
cand_nm_amt.plot(kind = 'barh')

plt.figure(figsize = (5, 5))
cand_nm_amt.plot(kind = 'pie')

# 直接选取Obama and Romney， 得到cond_vs
cond1 = contb_['cand_nm'] == 'Obama, Barack'
cond2 = contb_['cand_nm'] == 'Romney, Mitt'

# 法1
cond = cond1|cond2 # |表示或
cond_vs = contb_[cond]
cond_vs

# 法2
contb_vs2 = contb_.query("cand_nm == 'Obama, Barack' or cand_nm == 'Romney, Mitt'")

#法3
cond = contb_['cand_nm'].isin(['Romney, Mitt', 'Obama, Barack'])
contb_vs3 = contb_[cond]

# 对捐款数据进行分组
contb_.contb_receipt_amt.sort_values()
contb_.contb_receipt_amt.unique()
contb_.contb_receipt_amt.unique().size
contb_['contb_receipt_amt'].max()
contb_['contb_receipt_amt'][:10]  # 分组好看前10个

bins = [0.1, 10, 100, 1000, 10000, 100000, 1000000,10000000]

labels = pd.cut(contb_['contb_receipt_amt'], bins)

ret = contb_.pivot_table("contb_receipt_amt", index = 'contbr_occupation', columns = 'party', aggfunc = 'sum')
ret = contb_.pivot_table("contb_receipt_amt", index = 'contbr_occupation', columns = 'party', aggfunc = 'sum',
                         fill_value = 0)  # 对缺失值设为0
ret.sum(axis = 0) # axis=0 对列计算，献金总数
ret.sum(axis = 1) # axis=1 对行计算 # 把两党加起来
ret.sum(axis = 1).sort_values(ascending = False) [:20]

ret['total'] = ret['Democrat'] + ret['Republican'] # 制作一个列表，分别展示两党和总和
ret.sort_values(by = 'total', ascending = False)

# 也可以把<2000000的drop掉
cond = ret['total'] < 2000000
index = ret[cond].index
ret.drop(labels = index)

ret_big = ret.drop(labels = index)
ret_big.shape
# 作图,  同样的，为了图看的更加清晰，先排序！
ret_big_rank = ret_big.sort_values(by = 'total', ascending = True)
plt.figure(figsize = (12, 9))
ax = plt.subplot(1, 1, 1)
ret_big_rank.plot(kind = 'barh', ax = ax) # 相当于直接在子示图里绘制

grouped = contb_.groupby('cand_nm')
for i in grouped:
    print(i)
# 理解这个函数：根据给定的条件（key），对两党候选人政治献金进行排序
def get_top_amounts(grouped, key, n):
    return grouped.groupby(key)['contb_receipt_amt'].sum().sort_values(ascending = False)[:n]


grouped = cond_vs.groupby('cand_nm')
grouped.apply(get_top_amounts, 'contbr_occupation', 7)
grouped.apply(get_top_amounts, 'contbr_occupation', 7).unstack(level = 0) # 行变列  #职业分析

grouped.apply(get_top_amounts, 'contbr_employer', 10) # 公司分析

labels = pd.cut(cond_vs['contb_receipt_amt'], bins) # 根据bins进行cut
cond_vs.groupby(['cand_nm', labels]).size()

cond_vs.groupby(['cand_nm'])['contb_receipt_amt'].sum() # 看两主要候选人的献金总和
cond_vs.groupby(['cand_nm', labels]).size().unstack(level = 0, fill_value = 0) # 行变列  # 小额赞助数目 vs 大额赞助
cond_vs.groupby(['cand_nm', labels]).sum().unstack(level = 0, fill_value = 0) # 数量

# 处理缺失值
amt_vs = cond_vs.groupby(['cand_nm', labels]).sum().unstack(level = 0, fill_value = 0) # 为了可视化，放入amt_vs
amt_vs.fillna(0, inplace = True)

# 作图
amt_vs.plot(kind = 'barh')

# 找土豪
cond = cond_vs.contb_receipt_amt > 100000
cond_vs[cond]  # 发现是基金会

amt_vs[:-2].plot(kind = 'bar') # 只看去掉最后两组剩下的

amt_vs.div(amt_vs.sum(axis = 1), axis = 0) # 求和是横轴为1，再对列除为0，可以看所占比例，而不是简单数量对比
# 作图
amt_vs.div(amt_vs.sum(axis = 1), axis = 0)[:-2].plot(kind = 'bar')
amt_vs.div(amt_vs.sum(axis = 1), axis = 0)[:-2].plot(kind = 'bar', stacked = True)

# 时间处理
cond_vs['contb_receipt_dt'] = pd.to_datetime(cond_vs['contb_receipt_dt']) # 转化时间
cond_vs_time = cond_vs.set_index('contb_receipt_dt') # 将时间设置成索引
cond_vs_time.groupby(['cand_nm']).resample('M')['contb_receipt_amt'].sum() # 只有时间序列才可以重采样，天转化成月
cond_vs_time.groupby(['cand_nm']).resample('M')['contb_receipt_amt'].sum().unstack(level = 0)

# 作图
vs_m = cond_vs_time.groupby(['cand_nm']).resample('M')['contb_receipt_amt'].sum().unstack(level = 0)
vs_m.plot(kind = "bar")
vs_m.plot(kind = 'line')

plt.figure(figsize = (32, 9))
ax = plt.subplot(1, 1, 1)
vs_m.plot(kind = 'area', ax = ax, alpha = 0.8) # 面积堆积图

cond_vs.groupby(['cand_nm', 'contbr_st'])['contb_receipt_amt'].sum() # 以两个变量分类：state and candidate
state_vs = cond_vs.groupby(['cand_nm', 'contbr_st'])['contb_receipt_amt'].sum().unstack(level = 0)
# unstack非常重要，因为他将作图的横坐标调整为了state！
# 作图
state_vs.fillna(0, inplace = True)
plt.figure(figsize = (23, 9))
ax = plt.subplot(1, 1, 1)
state_vs.plot(kind = 'bar', ax = ax)

state_vs_rate = state_vs.div(state_vs.sum(axis = 1), axis = 0) #  同理之前不同捐款集合的做法
state_vs_rate.drop(labels = ['AA', 'AB', 'AE', 'NOT PROVIDE'], inplace = True)

# 利用basemap可视化
import matplotlib.pyplot as plt
%matplotlib inline

import os
import conda

conda_file_dir = conda.__file__
conda_dir = conda_file_dir.split('lib')[0]
proj_lib = os.path.join(os.path.join(conda_dir, 'share'), 'proj')
os.environ["PROJ_LIB"] = proj_lib

from mpl_toolkits.basemap import Basemap

# 作底图
plt.figure(figsize = (12, 9))
m = Basemap(llcrnrlon = -122,
           llcrnrlat = 23.41,
           urcrnrlon = -64,
           urcrnrlat = 45,
           projection = 'lcc',
           lat_1 = 30,
           lat_2 = 35,
           lon_0 = -80)

m.drawcoastlines(linewidth = 1.5)
m.drawcountries(linewidth = 1.5)
m.drawstates()  # 加上state

plt.show()

cmap = plt.cm.Blues # 颜色放入cmap

for i in range(10):
    print((i + 1) / 10)
    plt.plot(np.arange(10) + i, c = cmap((i + 1) / 10))

for i in range(10):
    print((i + 1) / 10)
    plt.plot(np.arange(10) + i, c = cmap(state_vs_rate['Obama, Barack'].iloc[i]))

plt.figure(figsize = (12, 9))
m = Basemap(llcrnrlon = -122,
           llcrnrlat = 23.41,
           urcrnrlon = -64,
           urcrnrlat = 45,
           projection = 'lcc',
           lat_1 = 30,
           lat_2 = 35,
           lon_0 = -100)  # 精度调成100

m.drawcoastlines(linewidth = 1.5)
m.drawcountries(linewidth = 1.5)
m.drawstates()  # 加上state

m.readshapefile('./USA/gadm36_USA_1', name = 'states') # 读取地图state数据

plt.show()

# 导入16进制颜色
from matplotlib.colors import rgb2hex
from matplotlib.patches import Polygon

plt.figure(figsize = (12, 9))
m = Basemap(llcrnrlon = -122,
           llcrnrlat = 23.41,
           urcrnrlon = -64,
           urcrnrlat = 45,
           projection = 'lcc',
           lat_1 = 30,
           lat_2 = 35,
           lon_0 = -100)  # 精度调成100

m.drawcoastlines(linewidth = 1.5)
m.drawcountries(linewidth = 1.5)
m.drawstates()  # 加上state

m.readshapefile('./USA/gadm36_USA_1', name = 'states') # 读取地图state数据

colors = []
states = []

cmap = plt.cm.Blues

for shapeinfo in m.states_info:
    a = shapeinfo['VARNAME_1']
    s = a.split('|')[0]

    try:
        rate = oba[s] # 代表颜色
        colors.append(cmap(rate))
        states.append(s)
    except:
        colors.append(cmap(0)) # 没有的值给0，白色
        states.append(s)

ax = plt.gca()
for n,seg in enumerate(m.states):
    c = rgb2hex(colors[n])
    poly = Polygon(seg, color = c )
    ax.add_patch(poly)

plt.show()

# 用自典来处理全称
abbr = {'Commonwealth of Kentucky': 'KY',
        'Commonwealth of Massachusetts': 'MA',
        'Commonwealth of Pennsylvania': 'PA',
        'State of Rhode Island and Providence Plantations': 'RI'}

# 导入16进制颜色
from matplotlib.colors import rgb2hex
from matplotlib.patches import Polygon


plt.figure(figsize = (12, 9))
m = Basemap(llcrnrlon = -122,
           llcrnrlat = 23.41,
           urcrnrlon = -64,
           urcrnrlat = 45,
           projection = 'lcc',
           lat_1 = 30,
           lat_2 = 35,
           lon_0 = -100)  # 精度调成100

m.drawcoastlines(linewidth = 1.5)
m.drawcountries(linewidth = 1.5)
m.drawstates()  # 加上state

m.readshapefile('./USA/gadm36_USA_1', name = 'states') # 读取地图state数据

colors = []
states = []

cmap = plt.cm.Blues

for shapeinfo in m.states_info:
    a = shapeinfo['VARNAME_1']
    s = a.split('|')[0]

    try:
        rate = oba[s] # 代表颜色
        colors.append(cmap(rate))
        states.append(s)
    except:
        colors.append(cmap(oba[abbr[s]])) # 从没有的值给0，白色，利用字典进行缩写!!!
        states.append(s)
    
ax = plt.gca()
for n,seg in enumerate(m.states):
    c = rgb2hex(colors[n])
    poly = Polygon(seg, color = c )
    ax.add_patch(poly)

plt.show()

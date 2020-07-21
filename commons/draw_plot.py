import pandas as pd
import matplotlib
import math

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns


def fs1(x):
    a = 1 - x**2
    return math.sqrt(a)


def fs2(x):
    a = -1 * x**2 + 1
    return a


def fs3(x):
    a = -x +1
    return a


def fs4(x):
    a = 1 - math.sqrt(x)
    return a


def fs5(x):
    a = 1 - math.sqrt(x)
    return a**2

num = 100
x = [i*1.0/num for i in range(0, num, 1)]
y1 = [fs1(xx) for xx in x]
y2 = [fs2(xx) for xx in x]
y3 = [fs3(xx) for xx in x]
y4 = [fs4(xx) for xx in x]
y5 = [fs5(xx) for xx in x]

df = pd.DataFrame(zip(x, y1, y2, y3, y4, y5), columns=["x", "y1", "y2", "y3", "y4", "y5"])
print(df)
# sns.lmplot(x="x", y="y", data=df)
ax = sns.scatterplot(x="x", y="y1", data=df, linewidth=0.3, marker='*', s=100)
ax = sns.scatterplot(x="x", y="y2", data=df, linewidth=1.0, marker='|', ax=ax, s=100)
ax = sns.scatterplot(x="x", y="y3", data=df, linewidth=0.05, ax=ax)
ax = sns.scatterplot(x="x", y="y4", data=df, linewidth=1.0, marker="_", ax=ax, s=100)
ax = sns.scatterplot(x="x", y="y5", data=df, linewidth=1.0, ax=ax, marker='x')
ax.legend(title='', loc='upper right', labels=['fs1', 'fs2', 'fs3', 'fs4', 'fs5'])
# ax = sns.lineplot(x="x", y="y", color='red', data=pd.DataFrame(zip([0, 1], [0, 1]), columns=["x", "y"]), ax=ax)
ax.set_xlabel('Ls(t)')
ax.set_ylabel('fs(t)')
plt.savefig('fig.eps', format='eps')
plt.show()








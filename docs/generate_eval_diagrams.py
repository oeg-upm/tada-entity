import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

sns.set_style("whitegrid")

# df = pd.read_csv("st19results.csv")
#a = df[df['round']==2][df['case']=='title'][df['k']==1]



# a = df[['fs', 'precision', 'k']]
#a = df[['fs', 'precision', ]]
# m = pd.melt(a, id_vars='fs', value_vars=['precision', 'recall', 'f1'], value_name='')

# sns.histplot(a, x=['precision', 'recall'], hue="fs", element="poly")
# sns.histplot(data=a, x="k", hue="fs", multiple="dodge", shrink=.8)
#sns.barplot(x=['precision', 'recall'], y='Value', hue='Variable', data=tidy, ax=ax1)


# ax = sns.barplot(data=m, x="fs", hue="variable", y="", palette="Paired")
# ax.legend_.set_title(None)
# # ax.legend.get_le='right'
# ax.legend(loc='lower right')
# ax.set_title('abc')
#plt.show()
# ax.despine(left=True)


def get_df_fss(df, round, case, k):
    df = df[df['round'] == round]
    df = df[df['case'] == case]
    df = df[df['k'] == k]
    a = df[['fs', 'precision', 'recall', 'f1']]
    return a


def save_svg(df, title, fname):
    m = pd.melt(df, id_vars='fs', value_vars=['precision', 'recall', 'f1'])
    ax = sns.barplot(data=m, x="fs", hue="variable", y="value", palette="Paired")
    ax.set(ylim=(0.5, 1.0), ylabel="")
    # ax.legend_.set_title(None)
    # ax.legend(loc='lower right')
    ax.set_title(title)
    #plt.show()
    #ax.savefig(fname+".svg")
    # leg = ax.figure.legend(handles[0:3], labels[0:3])
    handles, labels = ax.get_legend_handles_labels()
    # print("labels")
    # print(labels)
    plt.legend(handles[:3], labels[:3], loc='lower right')
    # plt.legend.set_title(None)
    # plt.legend(loc='lower right')
    # plt.set_title(title)
    plt.savefig(fname+".svg")
    # ax.figure.savefig(fname+".svg")


def generate_st19_svg():
    df = pd.read_csv("st19results.csv")
    k = 1
    for round_num in range(2,5):
        for case in ['original', 'title']:
            df_part = get_df_fss(df, round=round_num, case=case, k=k)
            title = "SemTab2019 Round %d (case=%s, k=%d)" % (round_num, case, k)
            fname = "st19-r%d-%s-k%d" % (round_num, case, k)
            save_svg(df_part, title=title, fname=fname)

# def get_df(round, case, k):
#     return df[df['round'] == round][df['case'] == case][df['k'] == k]

if __name__ == '__main__':
    generate_st19_svg()

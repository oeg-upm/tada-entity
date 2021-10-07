import argparse

import seaborn as sns
import pandas as pd


def get_alpha_per_classes(df):
    """
    :param df:
    :return:
    """
    d = dict()
    for idx, row in df.iterrows():
        d[row['class']] = []
        for idx2, rows in df.iterrows():
            if idx != idx2:
                d[row['class']].append((rows['mean']+rows['median']) / 2)
        d[row['class']] = sum(d[row['class']])/len(d[row['class']])
    return d


def get_alpha_per_fsid(fkfold):
    """
    :param falpha: path to the alpha file
    :param ignore_class: class uri to be ignored
    :return:
    {
        <fsid>: {alpha_avg: <>, alpha_median: <>},
        <fsid>: {},
    }
    """
    d = dict()
    df = pd.read_csv(fkfold)
    for fsid in range(1, 6):
        df_fsid = df[fd.fsid == fsid]
        d[fsid] = get_alpha_per_classes(df_fsid)
    return d


def workflow(fkfold, falpha):
    d = get_alpha_per_fsid(fkfold)
    evaluate_alphas(d, falpha)


def main():
    """
    Parse the arguments
    :return:
    """
    parser = argparse.ArgumentParser(description='Alpha Evaluator')
    parser.add_argument('--falpha', help="The path to the alpha results file.")
    parser.add_argument('--fmeta', help="The path to the meta file which contain the classes.")
    parser.add_argument('--data_dir', help="The path to the csv files")
    parser.add_argument('--title', choices=["true", "false"], default="true",
                        help="Whether to force title case or use the original case")
    parser.add_argument('--draw', help="The base name for the diagram file (without the extension)")
    parser.add_argument('--fscores', help="The path to the k-fold scores file")
    args = parser.parse_args()

    if args.falpha and args.fmeta and args.data_dir and args.title:
        workflow(args.falpha, args.fmeta, args.data_dir, args.title.lower() == "true")
    elif args.draw and args.title and args.fscores:
        generate_diagram(fscores=args.fscores, title_case=args.title.lower() == "true", draw_file_base=args.draw)
    else:
        parser.print_usage()
        parser.print_help()


if __name__ == "__main__":
    main()

"""
visualization functions
"""
import matplotlib.pyplot as plt


def plot_helper(df, column_label, y_label='USD'):
    """
    plots a nice plot out of the simulation output dataframe
    """
    for subset in df.subset.unique():
        fig, ax = plt.subplots(figsize=(15,5))
        subset_df = df[df['subset']==subset]
        subset_df.groupby(by=['run'])[column_label].plot(ax=ax)
        ax.set_title(f"{column_label}, subset {subset}")
        ax.grid(axis='both', alpha=.2)
        ax.set_ylabel(y_label)
        ax.legend([f"run {run}" for run in df.run.unique()])

        ax.spines["top"].set_alpha(0.0)
        ax.spines["bottom"].set_alpha(0.3)
        ax.spines["right"].set_alpha(0.0)
        ax.spines["left"].set_alpha(0.3)

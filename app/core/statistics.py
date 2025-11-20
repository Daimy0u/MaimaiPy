import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from scipy import stats as sci_stats

from typing import Optional
from app.models.statistical import RecordCollection, StatisticalCollection, EntryColumn

__all__ = ['scatterplot']

DEFAULT_PLOT_DIRECTORY = 'data/charts/'
LVL_LABEL_ORDER = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '9+', '10', '10+',
               '11', '11+', '12', '12+', '13', '13+', '14', '14+', '15']

def save_png(figure: Figure, directory: str = DEFAULT_PLOT_DIRECTORY, name: str = 'default'):
    figure.savefig(f'{directory}{name}.png')

def scatterplot(collection: StatisticalCollection,
                y: EntryColumn, x: EntryColumn,
                only_t50: bool = False):
    fig, ax = plt.subplots()
    df = collection.as_dataframe(only_top_50=only_t50)
    sns.scatterplot(df, y=y, x=x).figure
    save_png(fig)

def rating_boxplot(collection: StatisticalCollection, rating_threshold: int = 200):
    fig, ax = plt.subplots()
    level_order = ['12', '12+', '13', '13+', '14', '14+', '15']
    df = collection.as_dataframe()
    range_df = df[(df['level_internal'] >= 12) & (df['level_internal'] <= 15) & (df['rating'] >= rating_threshold)]
    sns.boxplot(range_df, x='level_label', y='rating', order=level_order)
    ax.legend()
    save_png(fig, name='hist')

def rating_histogram(collection: StatisticalCollection,
                     lower_bound: int = 250,
                     upper_bound: int = 350,
                     by_level_str: Optional[str] = None):
    df = collection.as_dataframe()
    range_df = df[(df['rating'] >= lower_bound) & (df['rating'] <= upper_bound)]
    if by_level_str:
        range_df = range_df[range_df['level_label'] == by_level_str]
    fig = sns.displot(range_df, x='rating').figure
    save_png(fig, name='hist_rating')

def rating_histogram_clt(collection: StatisticalCollection,
                         lower_bound: int = 250,
                         upper_bound: int = 350,
                         by_level_strs: list = ['12+','13', '13+', '14', '14+'],
                         constant_lower_bound: Optional[float] = None):
    df = collection.as_dataframe()
    fig, ax = plt.subplots(figsize=(10, 6))
    n = 30            # sample size
    R = 1000          # number of simulated sample-means

    colors = sns.color_palette("tab10", len(by_level_strs))

    for idx, level in enumerate(by_level_strs):
        range_df = df[(df['rating'] >= lower_bound) & (df['rating'] <= upper_bound)]
        range_df = range_df[range_df['level_label'] == level]
        if constant_lower_bound:
            range_df = range_df[range_df['level_internal'] >= constant_lower_bound]

        ratings = range_df['rating'].dropna()
        if len(ratings) < n:
            continue

        means = [ratings.sample(n=n, replace=True).mean() for _ in range(R)]
        # Only plot the histogram, not the KDE
        sns.histplot(means, kde=False, ax=ax, stat="density", color=colors[idx], label=f"Level {level}", alpha=0.5)

        mu = ratings.mean()
        se = ratings.std(ddof=1) / np.sqrt(n)
        xs = np.linspace(min(means), max(means), 200)
        # Only plot one PDF line per histogram
        pdf = sci_stats.norm.pdf(xs, loc=mu, scale=se)
        ax.plot(xs, pdf, color=colors[idx])

    ax.set_title("CLT Histogram of Ratings by Level")
    ax.legend()
    plt.tight_layout()
    save_png(fig, name='hist_rating_clt_levels')


def ratio_s_ss(collection: StatisticalCollection):
    fig, ax = plt.subplots()
    df = collection.as_dataframe()
    import numpy as np
    counts_99 = df[df['achievement'].gt(99)].groupby('level_label').size().reindex(LVL_LABEL_ORDER, fill_value=0)
    counts_97 = df[df['achievement'].gt(97)].groupby('level_label').size().reindex(LVL_LABEL_ORDER, fill_value=0)
    ratio = np.where(counts_97 != 0, counts_99 / counts_97, np.nan)
    counts = pd.DataFrame({'level_label': LVL_LABEL_ORDER, 'ratio': ratio})
    sns.barplot(counts, x='level_label', y='ratio')
    ax.legend()
    save_png(fig, name='ratio')

if __name__ == '__main__':
    import matplotlib.pyplot as plt

    from app.core.datasource.otogedb import OtogeDB
    from app.models.record import RecordEntry

    source = OtogeDB(useFull=True)
    RecordEntry.set_source(source)
    stat, df = None, None
    with open('debug_data/collection_dump.txt', 'r') as f:
        stat = StatisticalCollection(RecordCollection(import_str=f.read()))

    if stat:
        rating_boxplot(stat)
        rating_histogram(stat)
        rating_histogram_clt(stat, constant_lower_bound=12.6)
        ratio_s_ss(stat)
        df_t50 = stat.as_dataframe(only_top_50=True)
        df = stat.as_dataframe()

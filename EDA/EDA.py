import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geocoder
from geopy.distance import vincenty
from collections import defaultdict
from itertools import product


def get_datetime(series):
    '''
    Change timestamp columns from numbers to datetimes
    '''
    return pd.to_datetime('1899-12-30') + pd.to_timedelta(series, 'D')


def plot_distplot(series, xlim=None, ylim=None, bins=100):
    """
    Plot's Seaborn's distplot that plots a histogram and KDE
    """
    fig, ax = plt.subplots()
    ax = sns.distplot(series, bins=bins, color=(0.27, 0.67, 0.78))
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    ax.set_title("Histogram")
    ax.set_xlabel(series.name)
    ax.set_ylabel("Frequency")
    fig.show()


def plot_comparison(df, col):
    """
    Plot comparison between cancelled and not cancelled for a given column
    """
    mask = df["cancelled"] == 1
    finished = df[col][~mask].mean()
    cancelled = df[col][mask].mean()
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.hist([df[col][~mask], df[col][mask]], color=["b", "r"], bins=25)
    ax.axvline(finished, linestyle='dashed', label="Finished Rides Mean: {:,.0f}".format(finished))
    ax.axvline(cancelled, color="r", linestyle='dashed', label="Cancelled Rides Mean: {:,.0f}".format(cancelled))
    ax.set_title(col.title().replace("_", " "), fontsize=16)
    ax.set_ylabel("Frequency", fontsize=14)
    ax.legend(fontsize=14)
    fig.savefig("../images/{}.png".format(col))


def plot_feature_importances(df, feature_importances):
    """
    Plot feature importances - stolen from churn case study solution
    """
    feat_scores = pd.DataFrame({'Feature Importances': feature_importances},
                           index=df.columns)
    feat_scores = feat_scores.sort_values(by='Feature Importances')
    feat_scores.plot(kind='barh', figsize=(8,8))


def plot_confusion_matrix(cm):
    """
    Plot confusion matrix - stolen from sklearn's example
    """
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title("Confusion Matrix")
    plt.colorbar()
    plt.xticks(np.arange(2), ["Finished", "Cancelled"], rotation=45)
    plt.yticks(np.arange(2), ["Finished", "Cancelled"])
    for i, j in product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], 'd'), horizontalalignment="center",
                 color="white" if cm[i, j] > cm.max() / 2 else "black")
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.show()


def plot_roc_curve(fpr, tpr, thresholds, auc):
    """
    Plot ROC curve - stolen from sklearn's example
    """
    plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % auc)
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend(loc="lower right")
    plt.show()


def get_ip_lat_lng(ip):
    """
    Use the geocoder API to retrieve the latitude and longitude for the input IP address
    """
    if isinstance(ip, str):
        return geocoder.ip(ip).latlng


def get_city_lat_lng(city_state):
    """
    Use the geocoder API to retrieve the latitude and longitude for the input city
    """
    if isinstance(city_state, str):
        return geocoder.google(city_state).latlng


def distance_between_coords(row):
    """
    Calculate the distance between coordinates
    """
    if isinstance(row["lat_lng"], list) & isinstance(row["user_lat_lng"], list):
        return vincenty(row["lat_lng"], row["user_lat_lng"]).miles


def distance_between_coords2(row):
    """
    Calculate the distance between coordinates
    """
    residence_lat_lng = [row["latitude"], row["longitude"]]
    if isinstance(row["lat_lng"], list) & isinstance(residence_lat_lng, list):
        return vincenty(row["lat_lng"], residence_lat_lng).miles


def get_past_ride_cnt(df, y):
    """
    Create list of past rides
    """
    d = defaultdict(list)
    ride_history = []
    for i, user_id in enumerate(df["user_id"]):
        ride_history.append(d[user_id].copy())
        if y is not None:
            d[user_id].append(y[i])
    return ride_history


def change_datetimes(df, *args):
    """
    Change timestamp columns from numbers to datetimes
    """
    for col_name in args:
        df[col_name] = pd.to_datetime('1899-12-30') + pd.to_timedelta(df[col_name], 'D')
    return df


def calculate_time_between(df, **kwargs):
    """
    Calculate the number of days between two datetime features
    """
    for k, (v1, v2) in kwargs.items():
        df[k] = (df[v1] - df[v2]).dt.total_seconds() / 86400
    return df


# Analysis of preceeding rolling order rate against perceived customer churn

import matplotlib
matplotlib.use('TkAgg')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def read_data_file(filename):
  df = pd.read_csv(filename, parse_dates=[4])
  df['delivered'] = pd.to_datetime(df.delivered.dt.date)
  return df

def format_dataframe(df):
  df = df.groupby(['customer_id','product_id','delivered']).agg({
    'price':np.mean,
    'quantity':np.sum
  })
  df['delivered'] = df.index.get_level_values('delivered')
  df['last_delivered'] = df.groupby(level=[0,1])['delivered'].shift()
  df['interval'] = (df.delivered - df.last_delivered).dt.days
  df['qty/day'] = df.quantity / df.interval
  df.drop(['delivered','last_delivered'], axis=1, inplace=True)
  return df

def filter_data(df, status):
  if status == 'churned':
    df = df.loc[df.interval > df.outlier].copy()
  elif status == 'retained':
    df = df.loc[df.interval < df.outlier].copy()
  df.dropna(axis=0, how='any', inplace=True)
  return df

def normalise_data(df):
  df['normalised_interval'] = df['interval'] / df['outlier']
  df['normalised_order_rate'] = df['qty/day'] / df['max_order_rate']
  df = df.groupby(['customer_id','product_id','delivered']).mean()
  df['rolling_normalised_order_rate'] = df['normalised_order_rate'].rolling(10).mean()
  return df

def plot_scatter(df):
  plt.scatter(df.normalised_interval, df.rolling_avg, s=1, marker='x')
  plt.title('Relationship Between Order Volume and Order Period')
  plt.xlabel('Order Interval')
  plt.ylabel('Rolling Avg Volume')
  plt.show()

def plot_histogram(df):
  plt.hist(df['previous_normalised_order_rate'], bins=20)
  plt.ylabel('Products')
  plt.xlabel('Previous Normalised Order Rate')
  plt.title('Normalised Order Rate Before Churn')
  plt.show()

def __main__():
  df = read_data_file('transactions.csv')
  transactions = format_dataframe(df)

  outliers = transactions.groupby(level=[0,1]).agg({'interval': lambda x: np.ceil(x.quantile(q=0.75) + ((x.quantile(q=0.75) - x.quantile(q=0.25)) * 1.5))})
  outliers = outliers.reset_index().rename(columns={'interval':'outlier'})
  max_order_rate = transactions.groupby(level=[0,1]).agg({'qty/day': np.max})
  max_order_rate = max_order_rate.reset_index().rename(columns={'qty/day':'max_order_rate'})
  transactions.reset_index(inplace=True)
  transactions = transactions.merge(outliers, on=['customer_id','product_id'], how='left')
  transactions = transactions.merge(max_order_rate, on=['customer_id','product_id'], how='left')

  normalised_transactions = normalise_data(transactions)
  normalised_transactions['previous_normalised_order_rate'] = normalised_transactions.groupby(level=[0,1])['normalised_order_rate'].shift()
  churned = filter_data(normalised_transactions, 'churned')
  plot_histogram(churned)

if __name__ == '__main__':
  __main__()


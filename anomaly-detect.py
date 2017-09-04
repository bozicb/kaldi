import numpy as np
import pandas as pd
import datetime

class Analysis:
  def __init__(self, filename):
    self.readCSVFile(filename)

  def __logFactorial__(self, x):
    # Efficiently compute log factorial
    s = 0
    for i in range(1,x+1):
      s += np.log(i)
    return s

  def __poissonProbDenFunc__(self, x):
    # Poisson probability density function, x[2] = mean number of orders, x[6] = total orders received this week
    poisson_pdf = np.sum([np.exp(y * np.log(x[2]) - x[2] - self.__logFactorial__(y)) for y in range(x[6].astype(int)+1)])
    return poisson_pdf

  def readCSVFile(self, filename):
    # read the csv file into a dataframe
    self.df = pd.read_csv(filename)
    # modify the datetime format. Make sure that this is reflected in the elastic index definition
    self.df["delivered"] = pd.to_datetime(self.df["delivered"], errors="coerce", format='%Y-%m-%d')

  def compareWeekOrders(self, n=7, siglevel=.05, target_week=None, target_year=None):
    # Add week and value columns to dataframe
    self.df['year'] = self.df['delivered'].dt.year
    self.df['week'] = self.df['delivered'].dt.week
    self.df['value'] = self.df['price'] * self.df['quantity']

    # Define week to compare and separate order data
    if target_week is None: target_week = datetime.date.today().isocalendar()[1] 
    if target_year is None: target_year = datetime.datetime.now().year
    target_week_orders = self.df.loc[(self.df.week == target_week) & (self.df.year == target_year)]
    self.df = self.df.loc[(self.df.week < target_week) & (self.df.year == target_year)]

    # Calculate value per customer per product for target week
    target_week_orders = target_week_orders.pivot_table(
      index=['customer_id', 'product_id'],
      values=['value'],
      aggfunc={
        'value':[np.sum, len]
      },
      fill_value=0
    )

    # Rename columns and reset the index for later merge with order history
    target_week_orders.columns.set_levels(['target_week'], level=0, inplace=True)
    target_week_orders.rename_axis({'sum':'value','len':'orders'}, axis='columns', inplace=True)
    target_week_orders.reset_index(inplace=True)

    # Calculate value per customer per product for order history
    customer_products = self.df.pivot_table(
      index=['customer_id', 'product_id', 'year', 'week'],
      values=['value'],
      aggfunc={
        'value':[np.sum, len]
      },
      fill_value=0
    )

    # Rename columns and reset the index to allow second pivot for mean and standard deviation
    customer_products.columns = customer_products.columns.droplevel(0)
    customer_products.rename(columns={'sum':'value','len':'orders'}, inplace=True)
    customer_products.reset_index(inplace=True)

    # Calculate mean and standard deviation of past orders based on number and value
    customer_products = customer_products.pivot_table(
      index=['customer_id', 'product_id'],
      values=['value','orders'],
      aggfunc={
        'value':[np.mean, np.std],
        'orders':[len, np.mean, np.std]
      },
      fill_value=0
    )

    # Remove products ordered by customer less than 10 times
    customer_products = customer_products.loc[customer_products[(u'orders',u'len')] > 10]
    customer_products.drop((u'orders',u'len'), axis=1, inplace=True)

    # Reset index for merge with target week data
    customer_products.reset_index(inplace=True)

    # Merge customer_products table with target_week_orders table
    # Inner join means data for customer_products with short history and customer_products not ordered this week are ommited
    customer_products = pd.merge(customer_products, target_week_orders, how='inner', on=[(u'customer_id',u''),(u'product_id',u'')])

    # Apply probabilty density function and created pVal column
    customer_products['pVal'] = customer_products.apply(self.__poissonProbDenFunc__, axis=1)
    print(customer_products.loc[customer_products.pVal<siglevel].head())

pd.set_option('display.width', 180)
Analysis('data.csv').compareWeekOrders()

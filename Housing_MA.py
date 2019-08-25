#!/usr/bin/env python
# coding: utf-8

# # Best Housing Locations in MA

# ## For this project I explore the housing market in MA to determine preferred locations based on housing prices, property tax rate, crime rate, and school performance. 

# ### First we'll be looking at property taxes by town for 2019, so we'll need to web scrape a few sites for this data. We'll extract the data into one dataframe and create a choropleth map for visualization purposes.

# In[1]:


import pandas as pd
import requests
url = requests.get('https://www.heislerandmattson.com/2019-massachusetts-tax-rates-real-estate-residential/').text

get_ipython().system('pip install beautifulsoup4')
get_ipython().system('pip install lxml')

from bs4 import BeautifulSoup
taxes = BeautifulSoup(url,'lxml')
print(taxes.prettify())


# In[2]:


p_taxes = taxes.find('table')
p_taxes


# In[6]:


for row in taxes.find_all('tr'):
    for col in row.find_all('td'):
        print(col.text)


# In[9]:


table_rows = p_taxes.find_all('tr')

res = []
for tr in table_rows:
    td = tr.find_all('td')
    row = [tr.text.strip() for tr in td if tr.text.strip()]
    if row:
        res.append(row)


# In[10]:


prop_taxes = pd.DataFrame(res, columns=["Town", "Year", "Property_Taxes", "blah"])
prop_taxes.head()


# In[11]:


del prop_taxes['Year']
del prop_taxes['blah']
prop_taxes.head()


# In[12]:


prop_taxes.drop(prop_taxes.index[0], inplace=True)
prop_taxes.head()


# In[13]:


zip_url = requests.get('https://www.zip-codes.com/state/ma.asp').text

zip = BeautifulSoup(zip_url,'lxml')
print(zip.prettify())


# In[14]:


zips = zip.find('table',{'class':'statTable'})
zips


# In[15]:


for row in zips.find_all('tr'):
    for col in row.find_all('td'):
        print(col.text)


# In[16]:


table_rows2 = zips.find_all('tr')

res = []
for tr in table_rows2:
    td = tr.find_all('td')
    row = [tr.text.strip() for tr in td if tr.text.strip()]
    if row:
        res.append(row)


# In[17]:


zip_codes = pd.DataFrame(res, columns=["Zip", "Town", "County", "Type"])
zip_codes.head()


# In[18]:


del zip_codes['Type']
del zip_codes['County']
zip_codes.head(10)


# In[19]:


zip_codes.drop(zip_codes.index[0], inplace=True)
zip_codes.head()


# In[20]:


zip_codes['Zip'] = zip_codes['Zip'].str.strip('ZIP Code ')
zip_codes.head(10)


# ### Someone was kind enough to create a .csv list of zip codes with coordinates on github. I use this to get the latitude and longitudes for each zip code

# In[21]:


coords=pd.read_csv('https://gist.githubusercontent.com/erichurst/7882666/raw/5bdc46db47d9515269ab12ed6fb2850377fd869e/US%2520Zip%2520Codes%2520from%25202013%2520Government%2520Data', dtype={'ZIP': str})
coords.head(5)


# ### Rename 'ZIP' to 'Zip' for consistency between dataframes for merging

# In[29]:


coords = coords.rename(columns={"ZIP": "Zip"})
coords.head(5)


# In[25]:


coords.dtypes


# In[26]:


prop_taxes.dtypes


# In[27]:


zip_codes.dtypes


# ### Merge the first 2 dataframes on the shared 'Town' column.

# In[28]:


MA1 = pd.merge(zip_codes, prop_taxes, on='Town')
MA1.head()


# ### Now, merge that dataframe with the dataframe for coordinates on the shared 'Zip' column

# In[32]:


Taxes = pd.merge(MA1, coords, on='Zip')
Taxes


# In[ ]:





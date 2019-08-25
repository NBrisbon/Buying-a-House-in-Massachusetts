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


# In[3]:


for row in taxes.find_all('tr'):
    for col in row.find_all('td'):
        print(col.text)


# In[4]:


table_rows = p_taxes.find_all('tr')

res = []
for tr in table_rows:
    td = tr.find_all('td')
    row = [tr.text.strip() for tr in td if tr.text.strip()]
    if row:
        res.append(row)


# In[5]:


prop_taxes = pd.DataFrame(res, columns=["Town", "Year", "Property_Taxes", "blah"])
prop_taxes.head()


# In[6]:


del prop_taxes['Year']
del prop_taxes['blah']
prop_taxes.head()


# In[7]:


prop_taxes.drop(prop_taxes.index[0], inplace=True)
prop_taxes.head()


# In[8]:


zip_url = requests.get('https://www.zip-codes.com/state/ma.asp').text

zip = BeautifulSoup(zip_url,'lxml')
print(zip.prettify())


# In[9]:


zips = zip.find('table',{'class':'statTable'})
zips


# In[10]:


for row in zips.find_all('tr'):
    for col in row.find_all('td'):
        print(col.text)


# In[11]:


table_rows2 = zips.find_all('tr')

res = []
for tr in table_rows2:
    td = tr.find_all('td')
    row = [tr.text.strip() for tr in td if tr.text.strip()]
    if row:
        res.append(row)


# In[12]:


zip_codes = pd.DataFrame(res, columns=["Zip", "Town", "County", "Type"])
zip_codes.head()


# In[13]:


del zip_codes['Type']
del zip_codes['County']
zip_codes.head(10)


# In[14]:


zip_codes.drop(zip_codes.index[0], inplace=True)
zip_codes.head()


# In[15]:


zip_codes['Zip'] = zip_codes['Zip'].str.strip('ZIP Code ')
zip_codes.head(10)


# ### Someone was kind enough to create a .csv list of zip codes with coordinates on github. I use this to get the latitude and longitudes for each zip code

# In[16]:


coords=pd.read_csv('https://gist.githubusercontent.com/erichurst/7882666/raw/5bdc46db47d9515269ab12ed6fb2850377fd869e/US%2520Zip%2520Codes%2520from%25202013%2520Government%2520Data', dtype={'ZIP': str})
coords.head(5)


# ### Rename 'ZIP' to 'Zip' for consistency between dataframes for merging

# In[17]:


coords = coords.rename(columns={"ZIP": "Zip"})
coords.head(5)


# In[18]:


coords.dtypes


# In[19]:


prop_taxes.dtypes


# In[20]:


zip_codes.dtypes


# ### Merge the first 2 dataframes on the shared 'Town' column.

# In[21]:


MA1 = pd.merge(zip_codes, prop_taxes, on='Town')
MA1.head()


# ### Now, merge that dataframe with the dataframe for coordinates on the shared 'Zip' column

# In[22]:


Taxes = pd.merge(MA1, coords, on='Zip')
Taxes


# In[23]:


get_ipython().system('conda install -c conda-forge folium=0.5.0 --yes')
import folium

print('Folium installed and imported!')


# In[24]:


# Massachusetts latitude and longitude values
latitude = 42.40
longitude = -71.38


# In[25]:


# create map and display it
MA_map = folium.Map(location=[latitude, longitude], zoom_start=8)

# display the map of MA
MA_map


# In[30]:


for i in range(0,len(Taxes)):
    folium.Marker([Taxes.iloc[i]['LAT'], Taxes.iloc[i]['LNG']], popup=Taxes.iloc[i]['Property_Taxes']).add_to(MA_map)

MA_map


# In[ ]:





#!/usr/bin/env python
# coding: utf-8

# # Best Housing Locations in MA

# ## For this project I explore the housing market in MA to determine preferred locations based on housing prices, property tax rate, crime rate, and school performance. 

# ### First we'll be looking at property taxes by town for 2019, so we'll need to web scrape a few sites for this data. We'll extract the data into one dataframe and create a choropleth map for visualization purposes.

# In[164]:


import pandas as pd
import requests
url = requests.get('https://www.heislerandmattson.com/2019-massachusetts-tax-rates-real-estate-residential/').text

get_ipython().system('pip install beautifulsoup4')
get_ipython().system('pip install lxml')

from bs4 import BeautifulSoup
taxes = BeautifulSoup(url,'lxml')
print(taxes.prettify())


# In[165]:


p_taxes = taxes.find('table')
p_taxes


# In[166]:


for row in taxes.find_all('tr'):
    for col in row.find_all('td'):
        print(col.text)


# In[167]:


table_rows = p_taxes.find_all('tr')

res = []
for tr in table_rows:
    td = tr.find_all('td')
    row = [tr.text.strip() for tr in td if tr.text.strip()]
    if row:
        res.append(row)


# In[168]:


prop_taxes = pd.DataFrame(res, columns=["Town", "Year", "Property_Taxes", "blah"])
prop_taxes.head()


# In[169]:


del prop_taxes['Year']
del prop_taxes['blah']
prop_taxes.head()


# In[170]:


prop_taxes.drop(prop_taxes.index[0], inplace=True)
prop_taxes.head()


# In[171]:


zip_url = requests.get('https://www.zip-codes.com/state/ma.asp').text

zip = BeautifulSoup(zip_url,'lxml')
print(zip.prettify())


# In[172]:


zips = zip.find('table',{'class':'statTable'})
zips


# In[173]:


for row in zips.find_all('tr'):
    for col in row.find_all('td'):
        print(col.text)


# In[174]:


table_rows2 = zips.find_all('tr')

res = []
for tr in table_rows2:
    td = tr.find_all('td')
    row = [tr.text.strip() for tr in td if tr.text.strip()]
    if row:
        res.append(row)


# In[175]:


zip_codes = pd.DataFrame(res, columns=["Zip", "Town", "County", "Type"])
zip_codes.head()


# In[176]:


del zip_codes['Type']
del zip_codes['County']
zip_codes.head(10)


# In[177]:


zip_codes.drop(zip_codes.index[0], inplace=True)
zip_codes.head()


# In[178]:


zip_codes['Zip'] = zip_codes['Zip'].str.strip('ZIP Code ')
zip_codes.head(10)


# ### Someone was kind enough to create a .csv list of zip codes with coordinates on github. I use this to get the latitude and longitudes for each zip code

# In[179]:


coords=pd.read_csv('https://gist.githubusercontent.com/erichurst/7882666/raw/5bdc46db47d9515269ab12ed6fb2850377fd869e/US%2520Zip%2520Codes%2520from%25202013%2520Government%2520Data', dtype={'ZIP': str})
coords.head(5)


# ### Rename 'ZIP' to 'Zip' for consistency between dataframes for merging

# In[180]:


coords = coords.rename(columns={"ZIP": "Zip"})
coords.head(5)


# In[181]:


coords.dtypes


# In[182]:


prop_taxes.dtypes


# In[183]:


zip_codes.dtypes


# ### Merge the first 2 dataframes on the shared 'Town' column.

# In[184]:


MA1 = pd.merge(zip_codes, prop_taxes, on='Town', how='outer')
MA1.head()


# In[185]:


MA1.shape


# ### Now, merge that dataframe with the dataframe for coordinates on the shared 'Zip' column

# In[186]:


Taxes = pd.merge(MA1, coords, on='Zip', how='outer')
Taxes.head()


# In[187]:


Taxes.shape


# In[188]:


Taxes['Property_Taxes'] = pd.to_numeric(Taxes.Property_Taxes.astype(str).str.replace(',',''), errors='coerce')
              #.fillna(0)
              #.astype(int)
Taxes.head()


# In[189]:


del Taxes['Zip']
Taxes.head()


# In[190]:


Taxes.drop_duplicates(['Town'], keep='first', inplace=True)
Taxes.head(20)


# In[191]:


Taxes.isnull().sum()


# In[192]:


Taxes.shape


# In[193]:


pd.set_option('max_rows', 500)
Taxes


# In[194]:


Taxes = Taxes.rename({'Town': 'TOWN'}, axis=1)
Taxes.head()


# In[59]:


get_ipython().system('conda install -c conda-forge folium=0.5.0 --yes')
import folium

print('Folium installed and imported!')


# In[29]:


# Massachusetts latitude and longitude values
latitude = 42.40
longitude = -71.38


# In[60]:


# create map and display it
MA_map = folium.Map(location=[latitude, longitude], zoom_start=8)

# display the map of MA
MA_map


# In[61]:


for i in range(0,len(Taxes)):
    folium.Marker([Taxes.iloc[i]['LAT'], Taxes.iloc[i]['LNG']], popup=Taxes.iloc[i]['Property_Taxes']).add_to(MA_map)

MA_map


# In[62]:


conda install -c conda-forge geopandas


# In[63]:


conda install -c conda-forge/label/gcc7 descartes


# In[64]:


from matplotlib import pyplot
from shapely.geometry import LineString
from descartes import PolygonPatch
import geopandas as gpd


# In[195]:


# set the filepath and load in a shapefile

MA_map = gpd.read_file(r'C:\Users\Nick\Desktop\GitProjects\Housing_MA\townssurvey_shp\TOWNSSURVEY_POLYM.shp')

# check data type so we can see that this is not a normal dataframe, but a GEOdataframe

MA_map.head()


# In[196]:


MA_map.plot()


# In[197]:


Taxes['TOWN'] = Taxes['TOWN'].str.upper() 
Taxes.head() 


# In[354]:


Taxes.shape


# In[199]:


MA_map.shape


# In[200]:


MA_tax = pd.merge(MA_map, Taxes, on='TOWN', how='outer')
MA_tax.head()


# In[271]:


MA_tax.shape


# In[272]:


MA_tax = MA_tax[['TOWN','Property_Taxes','LAT','LNG','TOWN_ID','geometry']]
MA_tax.head()


# In[273]:


MA_tax.loc[MA_tax['Property_Taxes'].isnull()]


# In[355]:


MA_tax.shape


# In[356]:


MA_Tax.describe()


# In[357]:


MA_Tax.isnull().sum()


# In[211]:


MA_tax.dropna(subset = ['geometry'], inplace=True)
MA_tax.isnull().sum()


# In[358]:


MASS_taxes = gpd.GeoDataFrame(MA_tax, geometry='geometry', crs={'init': 'epsg:4326'})
MASS_taxes.head()


# In[359]:


MASS_taxes.plot()


# In[360]:


import json

#Read data to json.

merged_json = json.loads(MASS_taxes.to_json())

#Convert to String like object.
MASS_Taxes = json.dumps(merged_json)


# In[361]:


MASS_taxes.crs


# In[98]:


conda install bokeh


# In[99]:


from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import brewer


# In[363]:


geosource = GeoJSONDataSource(geojson = MASS_Taxes)

#set the color palette 
palette = brewer['YlOrRd'][8]
palette = palette[::-1]

color_mapper = LinearColorMapper(palette = palette, low = 0, high = 25, nan_color = 'Black')
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
border_line_color='black',location = (0,0), orientation ='horizontal', major_label_overrides = tick_labels)

#Set the size and title of the graph
p = figure(title = 'Massachusetts Residential Property Taxes for 2019', plot_height = 700 , plot_width = 1020, toolbar_location = 'below', 
          toolbar_sticky=False,tooltips=[
         ("Town", "@TOWN"),
         ("Property Tax (per $1,000)","@Property_Taxes{$1.11}")])

#Define custom tick labels for color bar.
tick_labels = {'0': '$0/Unknown', '5':'$5', '10':'$10', '15':'$15', '20':'$20', '25':'$25'}

#Drop the Axes to clean it up
p.axis.visible = False

#Makes it so there are no gird lines
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

p.patches('xs','ys', source = geosource,fill_color = {'field':'Property_Taxes', 'transform' : color_mapper},
         line_color = 'black', line_width = 0.75, fill_alpha = 2)
p.add_layout(color_bar, 'above')

output_file(r"C:\Users\Nick\Desktop\GitProjects\Housing_MA\Property_Tax_Choropleth_Map.html")
output_notebook()

show(p)


# In[ ]:





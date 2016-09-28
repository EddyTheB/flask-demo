import sys
import requests
import numpy as np
import pandas as pd
from flask import Flask, render_template, redirect # request
from bokeh.plotting import figure, show, ColumnDataSource
from bokeh.models import HoverTool #, GMapPlot, GMapOptions, DataRange1d, Circle)
app = Flask(__name__)

# Some functions to get the data.
def _flatten_dict(root_key, nested_dict, flattened_dict):
    for key, value in nested_dict.iteritems():
        next_key = root_key + "_" + key if root_key != "" else key
        if isinstance(value, dict):
            _flatten_dict(next_key, value, flattened_dict)
        else:
            flattened_dict[next_key] = value
    return flattened_dict
    
def RequestMetData(Resource,
                   BaseURL='http://datapoint.metoffice.gov.uk/public/data/',
                   APIKey='649c9f2f-dd78-4326-94fa-86fcb7f9c589',
                   GetStr='?'):
    Resources = {'SiteList': 'val/wxfcs/all/json/sitelist'}
    if len(GetStr) > 1:
        QQ = '&key='
    else:
        QQ = 'key='
    Url = '{}{}{}{}{}'.format(BaseURL, Resources[Resource], GetStr, QQ, APIKey)
    resp = requests.get(Url).json()
    return resp
    
def GetSiteInfo():
    Info = RequestMetData('SiteList')
    LocList = Info['Locations']['Location']
    LocDF = pd.DataFrame(LocList)
    LocDF = LocDF.set_index('id')
    LocDF['elevation'] = LocDF['elevation'].astype(np.float)
    LocDF['latitude'] = LocDF['latitude'].astype(np.float)
    LocDF['longitude'] = LocDF['longitude'].astype(np.float)
    return LocDF   

def Info(SiteInfo, field):
    return SiteInfo[field]

def DownSampleSite(SiteInfo, Num):
    # Get the full range of latitudes and longitudes.
    """
    Lons = SiteInfo['longitude']
    Lats = SiteInfo['latitude']
    # Create a complex array of lon + i*Lat
    CPos = Lons + Lats*1j
    # Randomly choose Num points.
    RandCPos = CPos[(np.random.randint(0, len(CPos), size=Num)), :]
    print RandCPos
    # Create a set of Num randomly generatedrandom set
    LonMin = Lons.min()
    LonRange = Lons.max() - LonMin
    LatMin = Lats.min()
    LatRange = Lats.max() - LatMin
    RandLon = np.random.rand(20,1)
    RandLat = np.random.rand(20,1)
    RandLon = RandLon * LonRange + LonMin
    RandLat = RandLat * LatRange + LatMin
    RandC = RandLon + RandLat*1j
    """
    return SiteInfo.sample(Num)

def PlotSites(SiteInfo, County='All'):
    
    # Set up a google map
    #map_options = GMapOptions(lat=50, lng=0, map_type="roadmap", zoom=11)
    #plot = GMapPlot(x_range=DataRange1d(), y_range=DataRange1d(), map_options=map_options)
    if County == 'All':    
        source = ColumnDataSource(SiteInfo)
    else:
        source = ColumnDataSource(SiteInfo[SiteInfo['unitaryAuthArea'] == County])

    # Tool tip
    hover = HoverTool(tooltips=[("Site ID", '@id'),
                                ("name", '@name'),
                                ("Longitude", '@longitude'),
                                ("Latitude", '@latitude'),
                                ("County", '@unitaryAuthArea'),
                                ("region", '@region')])
    p = figure(width=700, height=800, title="Met Office Forecast Points",
               tools=['pan', 'box_zoom', 'wheel_zoom', 'save', 'reset', hover])
    p.circle('longitude', 'latitude', size=7, color="firebrick", alpha=0.5, source=source)
    show(p)


@app.route('/')
def main():
  return redirect('/index')

@app.route('/index')
def index():
  return render_template('index.html')


if __name__ == '__main__':
    SiteInfo = GetSiteInfo()
    PlotSites(SiteInfo, County='Moray')
    

    #app.run(port=33507)

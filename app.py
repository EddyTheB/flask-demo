import sys
import requests
import pandas as pd
from flask import Flask, render_template, request, redirect
from bokeh.plotting import figure, show, ColumnDataSource
from bokeh.models import (HoverTool, GMapPlot, GMapOptions, DataRange1d, Circle)

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
    return LocDF   

def PlotSites(SiteInfo):
    
    # Set up a google map
    #map_options = GMapOptions(lat=50, lng=0, map_type="roadmap", zoom=11)
    #plot = GMapPlot(x_range=DataRange1d(), y_range=DataRange1d(), map_options=map_options)
    
    print SiteInfo.head()
    source = ColumnDataSource(SiteInfo)
    # Tool tip
    hover = HoverTool(tooltips=[("Site ID", '@id'),
                                ("name", '@name'),
                                ("Longitude", '@longitude'),
                                ("Latitude", '@latitude')])
    p = figure(width=700, height=800, title="Met Office Forecast Points",
               tools=['pan', 'box_zoom', 'wheel_zoom', 'save', 'reset', hover])
    p.circle('longitude', 'latitude', size=7, color="firebrick", alpha=0.5, source=source)
    show(p)
    
    

def Info(SiteInfo, field):
    return SiteInfo[field]

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index')
def index():
  return render_template('index.html')


if __name__ == '__main__':
    SiteInfo = GetSiteInfo()
    PlotSites(SiteInfo)
    

    #app.run(port=33507)

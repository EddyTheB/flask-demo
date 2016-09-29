#import sys
import requests
import numpy as np
import pandas as pd
from flask import Flask, render_template, redirect, request
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import HoverTool #, GMapPlot, GMapOptions, DataRange1d, Circle)
from bokeh.embed import components
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
    LocDF = LocDF.sort_values(by=['latitude', 'longitude'])
    return LocDF   

def Info(SiteInfo, field):
    return SiteInfo[field]

def PlotSites():
    
    # Set up a google map
    #map_options = GMapOptions(lat=50, lng=0, map_type="roadmap", zoom=11)
    #plot = GMapPlot(x_range=DataRange1d(), y_range=DataRange1d(), map_options=map_options)
    SiteInfo = app.SiteInfo
    if app.SelectedRegion == 'All':    
      source = ColumnDataSource(SiteInfo)
    elif app.SelectedRegion[:3] == 'All':
      Region = app.SelectedRegion[4:]
      source = ColumnDataSource(SiteInfo[SiteInfo['region'] == Region])
    else:
      source = ColumnDataSource(SiteInfo[SiteInfo['unitaryAuthArea'] == app.SelectedRegion])

    # Tool tip
    hover = HoverTool(tooltips=[("Site ID", '@id'),
                                ("name", '@name'),
                                ("Longitude", '@longitude'),
                                ("Latitude", '@latitude'),
                                ("County", '@unitaryAuthArea'),
                                ("region", '@region')])
    p = figure(width=700, height=700, title="Met Office Forecast Points",
               tools=['pan', 'box_zoom', 'wheel_zoom', 'save', 'reset', hover])
    p.circle('longitude', 'latitude', size=7, color="firebrick", alpha=0.5, source=source)
    script, div = components(p)
    return script, div

def GetRegionList(SiteInfo = 'GetFromApp'):
  if SiteInfo == 'GetFromApp':
    SiteInfo = app.SiteInfo
    
  #CountyList = app.SiteInfo['unitaryAuthArea'].unique()
  RegionList = app.SiteInfo['region'].unique()
  
  RegionList_ = [u"All"]
  for Region in RegionList:
    RegionList_.append(u"All {}".format(Region))
    CountyList = app.SiteInfo[app.SiteInfo['region'] == Region]['unitaryAuthArea'].unique()
    #print Region    
    for County in CountyList:
      RegionList_.append(u"  {}".format(County))
  return RegionList_
  
def CreateRegionDropDown():
  RegionList = GetRegionList()
  HtmlStr = u""
  for Reg in RegionList:
    if Reg == app.SelectedRegion:
      HtmlStr = HtmlStr + u'<option value="' + Reg.strip() + u'" selected>' + Reg + u'</option>'
    else:
      HtmlStr = HtmlStr + u'<option value="' + Reg.strip() + u'">' + Reg + u'</option>'
  return HtmlStr

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index')
def index():
  RegionDropDown = CreateRegionDropDown()
  SitePlotScript, SitePlotDiv = PlotSites()
  return render_template('index.html', CountyForm=RegionDropDown, 
                                       SitePlotScript=SitePlotScript,
                                       SitePlotDiv=SitePlotDiv)
                                       
@app.route('/ChangeMap', methods=['GET', 'POST'])
def ChangeMap():
  SelectedRegion = request.form['CountySelect']
  app.SelectedRegion = str(SelectedRegion)
  return redirect('/index')

app.SiteInfo = GetSiteInfo()
app.SelectedRegion = 'All'

if __name__ == '__main__':
  app.run(debug=True)#port=33507)

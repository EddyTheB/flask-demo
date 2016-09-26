import requests
import pandas as pd

def ApiRequest(Resource, BaseUrl="http://datapoint.metoffice.gov.uk/public/data/", ApiKey="?key=649c9f2f-dd78-4326-94fa-86fcb7f9c589"):
    ApiUrl = BaseUrl + Resource + ApiKey
    r = requests.get(ApiUrl)
    dataFrame = pd.read_json(r)

SiteList = "val/wxfcs/all/json/sitelist"
RText = ApiRequest(SiteList)

print RText

#DF = pd.DataFrame(Data)

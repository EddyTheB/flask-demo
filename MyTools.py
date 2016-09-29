# MyTools
# Eddy Barratt
from os.path import expanduser

def GetAPIKey(Name, Source='~/.api/api_keys'):
    Source = expanduser(Source)
    with open(Source, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if ';' in line:
                line_ = line.split(';')
                name = line_[0].strip()
                key = line_[1].strip()
                if name == Name:
                    return key
                    
    print 'No key named {} exists.'.format(Name)                
    return ''


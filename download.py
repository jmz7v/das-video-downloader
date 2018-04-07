import httplib2
import urllib
import os, errno
from BeautifulSoup import BeautifulSoup, SoupStrainer

http = httplib2.Http()

siteUrl = 'https://www.destroyallsoftware.com'
siteCatalog =  '/screencasts/catalog/'
videosSubfolder = 'videos/'

# Store all videos from DaS inside catalog
def getCatalog():
    catalog = []
    status, response = http.request(siteUrl + siteCatalog)
    for link in BeautifulSoup(response, parseOnlyThese=SoupStrainer('a')):
        if siteCatalog in link.get('href', ''):
            catalog.append(link['href'])
    return catalog

# Extract script tags that contain video info
def getScriptTags(catalog):
    for video in catalog:
        status, response = http.request(siteUrl + video)
        for script in BeautifulSoup(response, parseOnlyThese=SoupStrainer('script')):
            getVideoUrls(script)

# Get video URLs from script tag, filter out non unique urls
def getVideoUrls(script):
    scriptText = str(script)
    if 'resolution' in scriptText:
        urls = []
        for line in scriptText.split('\n'):
            if '.mp4' in line:
                urls.append(line)
        uniqueUrls = set(urls)
        for url in uniqueUrls:
            getVideoData(url)

# Obtain neccesary info to download video
def getVideoData(url):
    cleanUrl = url.replace(' ', '')
    videoName = getVideoName(url)
    videoSource = getVideoSource(url)
    res = downloadFile(videoName, videoSource)
    print res

def downloadFile(filename, src):
    print 'Downloading ' + filename
    response = urllib.urlopen(src)
    filepath = os.path.join(videosSubfolder, filename)
    if not os.path.exists(videosSubfolder):
        os.makedirs(videosSubfolder)
    # with open(videosSubfolder + filename,'wb') as f:
    #     f.write(response.read())
    return 'Downloaded!\n\n'

# Return filename for video
def getVideoName(url):
    videoUrl, videoParams = url.split('?')
    _, videoName = videoUrl.split('.com/')
    return videoName

# Return full url
def getVideoSource(url):
    videoSource = url.split('"')
    return videoSource[1].replace('amp;', '')


catalog = getCatalog()
# print catalog
getScriptTags(catalog)

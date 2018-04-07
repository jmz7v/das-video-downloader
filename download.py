import httplib2
import urllib
import os, errno
import collections
from BeautifulSoup import BeautifulSoup, SoupStrainer

http = httplib2.Http()

siteUrl = 'https://www.destroyallsoftware.com'
siteCatalog =  '/screencasts/catalog/'
videoDirectory = 'videos/'

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Store all videos from DaS inside catalog
def getCatalog():
    catalog = []
    status, response = http.request(siteUrl + siteCatalog)
    for link in BeautifulSoup(response, parseOnlyThese=SoupStrainer('a')):
        if siteCatalog in link.get('href', ''):
            catalog.append(link['href'])
    return catalog

# Extract script tags that contain video info
def getVideoList(catalog):
    print bcolors.OKBLUE + 'Getting video info for all videos, this might take a while...' + bcolors.ENDC
    videos = []
    for video in catalog:
        status, response = http.request(siteUrl + video)
        for script in BeautifulSoup(response, parseOnlyThese=SoupStrainer('script')):
            videoUrl = getVideoUrl(script)
            if len(videoUrl):
                videos.append(videoUrl)
    return videos

# Get video URLs from script tag, filter out non unique urls
def getVideoUrl(script):
    scriptText = str(script)
    scriptTags = []
    if 'resolution' in scriptText:
        urls = []
        for line in scriptText.split('\n'):
            if '.mp4' in line:
                urls.append(line)
        uniqueUrls = set(urls)
        for url in uniqueUrls:
            video = getVideoData(url)
            scriptTags.append(video)
    return scriptTags

# Obtain neccesary info to download video
def getVideoData(url):
    cleanUrl = url.replace(' ', '')
    videoName = getVideoName(url)
    videoSource = getVideoSource(url)
    return videoName, videoSource

# Create video directory if not exists
def createVideoDirectory(dir):
    if not os.path.exists(dir):
        print bcolors.WARNING + 'Creating video directory at ' + dir + bcolors.ENDC
        os.makedirs(dir)
    else:
        print bcolors.WARNING + 'Video directory already exists ' + videoDirectory + bcolors.ENDC

def downloadVideos (videos):
    for video in videos:
        print video[0]
    # res = downloadFile(videoName, videoSource)
    # print bcolors.OKGREEN + res + bcolors.ENDC

def downloadFile(filename, src):
    print bcolors.OKBLUE + 'Downloading ' + filename + bcolors.ENDC
    response = urllib.urlopen(src)
    filepath = os.path.join(videoDirectory, filename)
    # if not os.path.exists(videoDirectory + filename):
    #     with open(videoDirectory + filename,'wb') as f:
    #         f.write(response.read())
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

# Run download
def init():
    createVideoDirectory(videoDirectory)
    catalog = getCatalog()
    videos = getVideoList(catalog)
    downloadVideos(videos)

init()
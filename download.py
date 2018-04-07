# Libraries
import httplib2
import urllib
import os, errno
import itertools
from BeautifulSoup import BeautifulSoup, SoupStrainer

# Classes
from video import Video
from colors import Colors

http = httplib2.Http()

siteUrl = 'https://www.destroyallsoftware.com'
siteCatalog =  '/screencasts/catalog/'
videoDirectory = 'videos/'

# Store all videos from DaS inside catalog
def getCatalog():
    catalog = []
    status, response = http.request(siteUrl + siteCatalog)
    for link in BeautifulSoup(response, parseOnlyThese=SoupStrainer('a')):
        if siteCatalog in link.get('href', ''):
            catalog.append(link['href'])
    return catalog

# Extract script tags that contain video info
# A video might contain more than one file (multiple resolutions)
# Flatten the returned video list
def getVideoList(catalog):
    print Colors.OKBLUE + 'Getting video info for all videos, this might take a while...\n' + Colors.ENDC
    videos = []
    for video in catalog:
        status, response = http.request(siteUrl + video)
        for script in BeautifulSoup(response, parseOnlyThese=SoupStrainer('script')):
            videoUrl = getVideoUrl(script)
            if len(videoUrl):
                videos.append(videoUrl)
    return list(itertools.chain(*videos))

# Get video URLs from script tag, filter out non unique urls
def getVideoUrl(script):
    scriptText = str(script)
    videos = []
    if 'resolution' in scriptText:
        urls = []
        for line in scriptText.split('\n'):
            if '.mp4' in line:
                urls.append(line)
        uniqueUrls = set(urls)
        for url in uniqueUrls:
            video = getVideoData(url)
            videos.append(video)
    return videos

# Obtain neccesary info to download video
def getVideoData(url):
    cleanUrl = url.replace(' ', '')
    return Video(cleanUrl)

# Create video directory if not exists
def createVideoDirectory(dir):
    if not os.path.exists(dir):
        print Colors.WARNING + '\nCreating video directory at ' + Colors.OKBLUE + dir + '\n' + Colors.ENDC
        os.makedirs(dir)
    else:
        print Colors.WARNING + '\nVideo directory ' + Colors.OKBLUE + dir + Colors.WARNING +' already exists\n' + Colors.ENDC

# Call a download for every video
def downloadVideos (videos):
    for video in videos:
        res = downloadFile(video.filename, video.url)
        print Colors.OKGREEN + res + Colors.ENDC

# Download video
def downloadFile(filename, src):
    print Colors.OKBLUE + 'Downloading ' + filename + Colors.ENDC
    response = urllib.urlopen(src)
    filepath = os.path.join(videoDirectory, filename)
    if not os.path.exists(videoDirectory + filename):
        with open(videoDirectory + filename,'wb') as f:
            f.write(response.read())
    else:
        return Colors.FAIL + 'ERROR: Video ' + filename +' already exists\n' + Colors.ENDC
    return 'SUCCESS: Video downloaded!\n'

# Run download
def init():
    createVideoDirectory(videoDirectory)
    catalog = getCatalog()
    videos = getVideoList(catalog)
    downloadVideos(videos)

init()
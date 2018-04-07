import httplib2
import urllib
import os, errno
import itertools
from BeautifulSoup import BeautifulSoup, SoupStrainer

http = httplib2.Http()

siteUrl = 'https://www.destroyallsoftware.com'
siteCatalog =  '/screencasts/catalog/'
videoDirectory = 'videos/'

class Video(object):
    filename = ''
    url = ''

    def __init__(self, url):
        self.filename = self.getVideoName(url)
        self.url = self.getVideoSource(url)

    def __str__(self):
        return 'Video: ' + self.filename

    # Return filename for video
    def getVideoName(self, url):
        videoUrl, videoParams = url.split('?')
        _, videoName = videoUrl.split('.com/')
        return videoName

    # Return full url
    def getVideoSource(self, url):
        videoSource = url.split('"')
        return videoSource[1].replace('amp;', '')

class colors:
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
# A video might contain more than one file (multiple resolutions)
# Flatten the returned video list
def getVideoList(catalog):
    print colors.OKBLUE + 'Getting video info for all videos, this might take a while...\n' + colors.ENDC
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
        print colors.WARNING + '\nCreating video directory at ' + colors.OKBLUE + dir + '\n' + colors.ENDC
        os.makedirs(dir)
    else:
        print colors.WARNING + '\nVideo directory ' + colors.OKBLUE + dir + colors.WARNING +' already exists\n' + colors.ENDC

# Call a download for every video
def downloadVideos (videos):
    for video in videos:
        res = downloadFile(video.filename, video.url)
        print colors.OKGREEN + res + colors.ENDC

# Download video
def downloadFile(filename, src):
    print colors.OKBLUE + 'Downloading ' + filename + colors.ENDC
    response = urllib.urlopen(src)
    filepath = os.path.join(videoDirectory, filename)
    if not os.path.exists(videoDirectory + filename):
        with open(videoDirectory + filename,'wb') as f:
            f.write(response.read())
    else:
        return colors.FAIL + 'ERROR: Video ' + filename +' already exists\n' + colors.ENDC
    return 'SUCCESS: Video downloaded!\n'

# Run download
def init():
    createVideoDirectory(videoDirectory)
    catalog = getCatalog()
    videos = getVideoList(catalog[0:2])
    downloadVideos(videos)

init()
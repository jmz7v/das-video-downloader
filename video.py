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

from PyQt5.QtGui import QPainter, QImage
from functools import partial

from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView,QWebEnginePage as QWebPage
from PyQt5.QtWebEngineWidgets import QWebEngineSettings as QWebSettings


class Screenshot(QWebView):
    def __init__(self):
        QWebView.__init__(self)

    def capture(self, url, output_file):
        self.load(QUrl(url))
        self.loadFinished.connect(partial(self.onDone, output_file))

    def onDone(self,output_file):
        # set to webpage size
        frame = self.page().mainFrame()
        self.page().setViewportSize(frame.contentsSize())
        # render image
        image = QImage(self.page().viewportSize(), QImage.Format_ARGB32)
        painter = QPainter(image)
        frame.render(painter)
        painter.end()
        image.save(output_file)


s = Screenshot()
s.capture('https://pypi.org/project/PyQt5/', 'web_page.png')
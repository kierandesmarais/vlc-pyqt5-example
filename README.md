# VLC Player in PyQt5 with YouTube integration
This example demonstrates an embedded VLC player in Qt using PyQt5 that can also play YouTube videos.

It is based on code from devos50, which in turn is based on the (older) example provided by VLC but uses the new PyQt5 signal/slot syntax.
Devos50's code was tested on OS X, Windows, and Linux but I have only tested this on Windows 10, though I tried to preserve the cross-system functionality.

The modules used in this program are:
PyQt5			https://pypi.org/project/PyQt5/
pafy			https://pypi.org/project/pafy/
youtube-dl		https://pypi.org/project/youtube_dl/
VLC			https://pypi.org/project/python-vlc/
requests		https://pypi.org/project/requests/
BeautifulSoup		https://pypi.org/project/beautifulsoup4/
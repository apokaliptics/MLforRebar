from sec_edgar_downloader import Downloader
import inspect
print('Downloader init signature:', inspect.signature(Downloader.__init__))
print('Downloader.get signature:', inspect.signature(Downloader.get))
print('Downloader.get doc:')
print(Downloader.get.__doc__)
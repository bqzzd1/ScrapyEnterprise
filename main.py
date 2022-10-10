
from scrapy import cmdline

# cmdline.execute('scrapy crawlall -a NAME=jiangsu --logfile log/tmp.log -L ERROR '.split())
# cmdline.execute('scrapy crawlall -a NAME='.split())
cmdline.execute('scrapy crawl anhui_zwfw1'.split())




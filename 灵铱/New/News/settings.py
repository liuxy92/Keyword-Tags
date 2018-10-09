# -*- coding: utf-8 -*-

# Scrapy settings for News project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'News'

SPIDER_MODULES = ['News.spiders']
NEWSPIDER_MODULE = 'News.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'News (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False
# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'News.middlewares.NewsSpiderMiddleware': 543,
#}
OPEN = 2
# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'News.middlewares.NewsDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'News.pipelines.NewsPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False
# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
#关闭spider扩展
#单位：秒 如果一个spider在指定的秒数后仍在运行，它将以 closespider_timeout 的原因被自动关闭，如果值设置为0（或者没有设置），spiders不会因为超时而关闭。
CLOSESPIDER_TIMEOUT = 14400
#一个整数值，指定条目的个数。如果spider爬取条目数超过了指定的数， 并且这些条目通过item pipeline传递，spider将会以 closespider_itemcount 的原因被自动关闭。
CLOSESPIDER_ITEMCOUNT = 0
#一个整数值，指定最大的抓取响应(reponses)数。 如果spider抓取数超过指定的值，则会以 closespider_pagecount 的原因自动关闭。 如果设置为0（或者未设置），spiders不会因为抓取的响应数而关闭。
CLOSESPIDER_PAGECOUNT = 0
#一个整数值，指定spider可以接受的最大错误数。 如果spider生成多于该数目的错误，它将以 closespider_errorcount 的原因关闭。 如果设置为0（或者未设置），spiders不会因为发生错误过多而关闭。
CLOSESPIDER_ERRORCOUNT = 0
# SCHEDULER = "scrapy_redis_bloomfilter.scheduler.Scheduler"
#
# # Ensure all spiders share same duplicates filter through redis.
# DUPEFILTER_CLASS = "scrapy_redis_bloomfilter.dupefilter.RFPDupeFilter"
#
# # Redis URL
# REDIS_URL = 'redis://127.0.0.1:6379'
#
# # Number of Hash Functions to use, defaults to 6
# BLOOMFILTER_HASH_NUMBER = 6
#
# # Bit
# BLOOMFILTER_BIT = 10
#
# # Persist
# SCHEDULER_PERSIST = True
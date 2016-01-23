from OpenSSL import SSL
from scrapy.core.downloader.contextfactory import ScrapyClientContextFactory


class TLS12ContextFactory(ScrapyClientContextFactory):
    "A context factory for TLS version 1.2."

    def __init__(self):
        ScrapyClientContextFactory.__init__(self)
        self.method = SSL.TLSv1_2_METHOD

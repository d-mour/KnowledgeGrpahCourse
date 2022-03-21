import scrapy

# Run from comand line with:
# scrapy crawl plantopedia -O plantopedia.jl

class ZakupatorSpider(scrapy.Spider):
    name = "plantopedia"
    
    def start_requests(self):
        # urlbase = 'http://www.plantopedia.ru/encyclopaedia/pot-plant/sections.php'
        # urls = [urlbase + str(n) for n in range(1,43)]
        # yield scrapy.Request(url=urlbase, callback=self.parse)
        urls = [
            'http://www.plantopedia.ru/encyclopaedia/pot-plant/sections.php',
            'http://www.plantopedia.ru/encyclopaedia/garden-plants/sections.php',
            'http://www.plantopedia.ru/encyclopaedia/cutting-plants/sections.php',
            'http://www.plantopedia.ru/encyclopaedia/ogorod/sections.php'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
            
        # url = 'http://www.plantopedia.ru/encyclopaedia/garden-plants/details/n/nartciss/'
        # yield scrapy.Request(url=url, callback=self.parse_plant)

    def parse(self, response):
        plant_links = response.css('.kolon a')
        yield from response.follow_all(plant_links, self.parse_plant)
        # yield response.follow(plant_links[0], callback=self.parse_plant)
            
    def parse_plant(self, response):
        header = response.css('h2[itemprop="title"]::text').get()
        family = response.css('h2[itemprop="title"]+h3::text').get()
        _short_data = response.css('.plashka strong ::text, .plashka div ::text').getall()
        short_data = dict()
        for i in range(0, int(len(_short_data)/2)):
            short_data[_short_data[i*2]] = _short_data[i*2+1]
        
        _headers = response.css('.encyclopaedia-zag h3::text').extract()
        _data = response.css('.encyclopaedia-zag h3::text, .encyclopaedia-zag p::text, .encyclopaedia-zag h4 ::text').extract()
        
        data = dict()
        
        head = ""
        dt = ""
        last = False
        
        for d in _data:
            if d in _headers:
                if last:
                    head = head + d
                else:
                    last = True
                    data[head] = dt
                    head = d
                    dt = ""
            else:
                last = False
                dt = dt + d
            
        data[head] = dt
            
        yield {
            'header': header ,
            'family': family ,
            'short_data' : short_data,
            'data' : data,
        }
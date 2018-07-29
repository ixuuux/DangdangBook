# DangdangBook
**By Scrapy**

运行`run.py`即可启动

### 大致流程

**分析Ajax请求**

站点：`http://m.dangdang.com/`

在chrome浏览器中打开模拟手机浏览器

![](http://ww1.sinaimg.cn/large/005WOYz1ly1ftqqkbb9m1j30c60353yf.jpg)

之后浏览器会发生变化，可以在顶部选择设置相关参数

![](http://ww1.sinaimg.cn/large/005WOYz1ly1ftqqkzh0o4j30pf0dyagq.jpg)

然后输入关键字`python`点击搜索

![](http://ww1.sinaimg.cn/large/005WOYz1ly1ftqqfvhxryj30mk0aft9p.jpg)

等到结果出来以后一直下拉，会发现每加载一页就是一个Ajax请求

![](http://ww1.sinaimg.cn/large/005WOYz1ly1ftqqnkxsf1j30kz07djs0.jpg)

只是通过更改`page=1`后面的数字来控制显示不同的数据，随便点击一个，查看请求详情

![](http://ww1.sinaimg.cn/large/005WOYz1ly1ftqqqek8mwj310402i748.jpg)

最重要的莫过于url地址，经过测试，`http://search.m.dangdang.com/search_ajax.php?keyword=python&act=get_product_flow_search&page=1`可用，后续可以变幻page值就可以获取其他页的数据了

有了url地址，那么就可以开始写爬虫了

**构造请求**

由于scrapy已经将请求的部分封装好了，直接使用即可

```python
class DangdangSpider(scrapy.Spider):
    name = 'dangdang'
    allowed_domains = ['dangdang.com']
    offset = 1
    url = "http://search.m.dangdang.com/search_ajax.php?keyword=python&act=get_product_flow_search&page={}"
    start_urls = [url.format(offset)]
```
这里后三行是自己写的，其他是scrapy生成的

**解析数据**

重头戏来了

```python
class DangdangSpider(scrapy.Spider):
    name = 'dangdang'
    allowed_domains = ['dangdang.com']
    offset = 1
    url = "http://search.m.dangdang.com/search_ajax.php?keyword=python&act=get_product_flow_search&page={}"
    start_urls = [url.format(offset)]

    def parse(self, response):
        item = DangdangItem()
        products = json.loads(response.text)
        for product in products['products']:
            item['book_name'] = product.get('name')  # 书名
            item['author_name'] = product.get('authorname')  # 作者
            item['price'] = product.get('price')  # 现价
            item['original_price'] = product.get('original_price')  # 原价
            item['score'] = product.get('score')  # 评分
            item['stock'] = product.get('stock')  # 库存
            item['total_review_count'] = product.get('total_review_count')  # 评论数
            item['shop_id'] = product.get('shop_id')  # 店铺id
            item['shop_info'] = product.get('shop_info')  # 店铺名称
            item['publisher'] = product.get('publisher')  # 出版社
            item['publish_date'] = product.get('publish_date')  # 出版日期
            item['image_url'] = product.get('image_url')  # 图书封面
            item['product_url'] = product.get('product_url')  # 图书url
            yield item
            self.offset += 1
            if self.offset <= settings.MAX_PAGE:
                yield scrapy.Request(self.url.format(self.offset))
```

`def parse(self, response)`方法中的代码就要自己全部完成了，这里是解析数据、构造下一次请求的重地，能不能提取的到数据以及下一页能不能发出去就看这里了，对了，当当返回的是json格式，就是字典的另外一种存在形态，可以通过python中的json模块转为字典类型，之后提取数据无非就是对字典的一些操作

提取数据写完之后就要构造下一次的请求，代码第4行`offset = 1`，这可不是顺便写的，每一句话都有用，哪怕是一个小数点都不能少，`offset = 1`就是用来'翻页'用的，26行的代码有对这个数值操作，在原有基础上+1，然后27行判断这个数字是否小于等于在settings文件中设定的数字，如果条件成立，那么就会发起下一次新一页的请求，条件不成立，程序结束

**定义字段**

解析出来的数据会来到这里

```python
class DangdangItem(scrapy.Item):
    book_name = scrapy.Field()
    author_name = scrapy.Field()
    price = scrapy.Field()
    original_price = scrapy.Field()
    score = scrapy.Field()
    stock = scrapy.Field()
    total_review_count = scrapy.Field()
    shop_id = scrapy.Field()
    shop_info = scrapy.Field()
    publisher = scrapy.Field()
    publish_date = scrapy.Field()
    image_url = scrapy.Field()
    product_url = scrapy.Field()
```

**数据存储**

本地和mongodb

```python
class DangdangPipeline(object):
    def process_item(self, item, spider):
        with open("dangdang.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(dict(item), ensure_ascii=False))
            f.write('\n')
        return item

class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        # name = item.collection
        self.db['dd'].insert(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()
```

# dynamic_proxy_pool
Building and maintain a dynamic proxy pool server for crawling and provides services. Using service from https://www.juliangip.com.

This project serve to https://github.com/iridium-soda/dockerfile_analysis_framework.

## Usage

**Before starting crawing, start proxy pool first.**

**Ensure API keys are correctly placed at `keys.json`**

Exposed interfaces:


- 
## Note

### To utilize the server

The process of sending a request through a proxy typically involves the following step:

```python
resp = requests.get(url, headers=headers, proxies=proxies)
```

The response of API is like:
```json
{"code":200,"msg":"成功","data":{"count":1,"filter_count":1,"surplus_quantity":1000,"proxy_list":["49.71.119.108:33565,139"]}}
```

When `get` returns 429(Too many request) or other error, allocate a new IP. If the pool are empty(or lower than a threhold), extract a batch of IPs via the request link.

### To maintain a proxies pool

The proxies pool is defined at `class proxypool` and can be utilized by server. A pool contains a batch of IPs and their status and infos. For example:

```json
{
    "IP":"49.71.119.108",
    "port":33565,
    "lifetime":139,
    "free":true
}
```

### Temp
- 爬虫调用某IP时，该IP应该进行锁定(标记为占用)
- 如果池子内每个IP都锁定，则等待(?)。应该等不了多久。考虑到最多`os.cpu_count()`个线程在运行
- 当获得网站的resp之后，应该给server发一个包，解封该ip
- 注意如果代理连接失效传给调用者。这个应该会很常见。
- 对可用代理做一个排序，每次取代理池中可用且有效期剩余最长的那个
- 考虑做一个定时任务？在有效时间低于某个门限时间的时候将其剔除出代理池
- 
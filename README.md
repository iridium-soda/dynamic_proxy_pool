# dynamic_proxy_pool

Building and maintaining a dynamic proxy pool server for crawling and provides services. Using service from <https://www.juliangip.com>.

This project serves to https://github.com/iridium-soda/dockerfile_analysis_framework>.

## Usage

**Before starting crawling**, start **the proxy pool first.**

**Ensure API keys are correctly placed at `keys.json`**

Exposed interfaces:

-

## Note

### To utilize the server

The process of sending a request through a proxy typically involves the following step:

```python
resp = requests.get(url, headers=headers, proxies=proxies)
```

The response of API is like this:

```json
{"code":200,"msg":"成功","data":{"count":1,"filter_count":1,"surplus_quantity":1000,"proxy_list":["49.71.119.108:33565,139"]}}
```

When `get` returns 429(Too many requests) or another error, allocate a new IP. If the pool is empty(or lower than a threshold), extract a batch of IPs via the request link.

### To maintain a proxy pool

The proxy pool is defined as `class proxypool`` and can be utilized by the server. A pool contains a batch of IPs and their status and info. For example:

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
- ~~如果池子内每个IP都锁定，则等待(?)。应该等不了多久。考虑到最多`os.cpu_count()`个线程在运行~~
- 当获得网站的resp之后，应该给server发一个包，解封该ip.如果没有顺利获得结果,则loop换一个ip试试看.
- 注意如果代理连接失效传给调用者。这个应该会很常见。
- 对可用代理做一个排序，每次取代理池中可用且有效期剩余最长的那个
- 考虑做一个定时任务？在有效时间低于某个门限时间的时候将其剔除出代理池
- 考虑到多线程对pool的不确定性操作,应该限定同时只处理一个连接.大概?

## Reference

<https://cuiqingcai.com/7048.html>

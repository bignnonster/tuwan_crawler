# tuwan 妹子图爬取

基于[jerryWebSpider](https://github.com/jrhu05/jerryWebSpider)的url获取逻辑而转化的python27版本。适用于没有java、mysql环境的同学。

## 使用方式

设置获取图册的范围

```python
if __name__ == "__main__":
    print "==>start"
    
    gainer = Process_ctl()
    gainer.load_progress()
    # 设置获取相册的起止id即可
    gainer.run_range(start=0,end=2000)
    # gainer.run_queue()
    gainer.save_progress()

    data_dl = gainer.get_progress_data()
    dlobj = DL()
    dlobj.set_dl_data(data_dl)
    dlobj.do_dl_queue()

    print "==>end"
```

执行爬取

```shell
python get_tuwan.py
```

## 说明
- 依赖`requests`库
- 图片组归档在`./arichive`下
- 已经下载过的图片不会重新下载(根据文件名判断,但是不会对文件内容进行校验)
- 解析后的图片url会记录在`./data/pic_data`下
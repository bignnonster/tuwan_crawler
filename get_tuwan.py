#!/usr/bin/env python
#coding=utf-8

import requests
import json
import os,sys,time
import codecs
import base64
reload(sys)
sys.setdefaultencoding('utf8')

#baseurl
# url = 'https://api.tuwan.com/apps/Welfare/detail?type=image&dpr=3&id=1&callback=jQuery1123005731616869004086_1553334365167&_=1553334365170'


class Tools(object):
    @staticmethod
    def save_as_text(strobj,path='./data',filename='tmpfile'):
        if not isinstance(strobj,(str,unicode)):
            strobj = json.dumps(strobj,ensure_ascii=False,sort_keys=True)

        path=path.rstrip("\\")
        Tools.mkdir(path)
        f = codecs.open(path + '/'+filename,'w','utf-8')
        f.write(strobj)
        f.close()

    @staticmethod
    def mkdir(path):
        path=path.strip()
        path=path.rstrip("\\")
        isExists=os.path.exists(path)
     
        # 判断结果
        if not isExists:
            try:
                os.makedirs(path)
            except Exception as e:
                return False
            return True
        else:
            return False

class Process_ctl(object):
    def __init__(self):
        self.pic_id = 0
        self.url = 'https://api.tuwan.com/apps/Welfare/detail?id='+str(self.pic_id)
        self.stats_data = {}
    def __update_url(self):
        self.url = 'https://api.tuwan.com/apps/Welfare/detail?id='+str(self.pic_id)

    def trans_url(self,url):
        ends_with =",0,0,9,3,1,-1,NONE,,,90"
        parts = url.split("/")
        # print 'parts > ',parts
        if len(parts) < 7:return False
        to_be_decode = parts[6]
        decode_rst = base64.b64decode(to_be_decode)
        if not isinstance(decode_rst,(str,unicode)) or "," not in decode_rst:return False

        real_id = decode_rst.split(",")[0]
        to_be_encode = real_id + ends_with
        encode_rst = base64.b64encode(to_be_encode)
        # print decode_rst
        # print real_id
        # print encode_rst

        parts[6] = encode_rst
        new_url = ""
        for x in parts:
            new_url += x
            new_url += '/'
        else:
            if new_url != "":new_url = new_url[:-1]
        # print new_url
        return new_url

    def run_range(self, start,end):
        if not isinstance(start,int):
            raise TypeError,"start should be int."
        if not isinstance(end,int):
            raise TypeError,"end should be int."

        for i in xrange(start,end):
            self.req_1_group(i)

    def run_queue(self):
        try:
            f = open("./data/queue_data")
            rangelist = json.loads(f.read())
        except Exception as e:
            print e
            return
        
        for i in rangelist:
            self.req_1_group(i)

    def save_progress(self):
        Tools.save_as_text(self.stats_data,filename="pic_data")

    def load_progress(self):
        try:
            f = open("./data/pic_data")
            r = f.read()
            if r != "":
                self.stats_data = json.loads(r)
        except Exception as e:
            pass

    def get_progress_data(self):
        return self.stats_data

    def req_1_group(self,gid=None):
        if gid:
            self.pic_id = str(gid)
            self.__update_url()
        req_retry_time = 3
        if self.stats_data.has_key(self.pic_id):
            print "skip gid",gid,"that is existed."
            return

        for x in xrange(req_retry_time):
            try:
                r = requests.get(self.url,timeout=5.0)
            except Exception as e:
                print "REQ ERR>>",self.pic_id,e
                continue
            time.sleep(0.4)
            # print type(r.text)
            if "jQuery1123005731616869004086_1553334365167"  in r.text: 
                js_string = r.text[43:]
                js_string = js_string[:-1]
            elif len(r.text) > 0 and r.text[0] == '(':
                js_string = r.text[1:]
                js_string = js_string[:-1]
            else:
                continue
            # print "REQ_RETURN>>",r.text
            # print "js ret>",js_string
            try:
                data = json.loads(js_string)
            except Exception as e:
                print "JSON ERR>>",e
                break
            
            # keys = data.keys()
            if data.get("error") != 0:
                print "ERR code for group:",self.pic_id,"code:",data.get("error"),"times :",x+1
            
            title = data.get("title") #str
            total_c = data.get("total") #int
            data = data.get("thumb")
            if not isinstance(data,list):
                print "ERR data type group:",self.pic_id,"type:",type(data),"times :",x+1
                continue
            
            #trans url
            data_real = []
            for x in data:
                real_url = self.trans_url(x)
                if real_url:data_real.append(real_url)
            if len(data_real) == total_c:
                print "gid",gid,"get all,count:",total_c
            else:
                print "gid",gid,"not get all,lost:",total_c-len(data_real)

            self.stats_data[str(self.pic_id)] = {
                "title":title,
                "total":total_c,
                "data":data_real
                }
            print "gid",gid,">>done"
            
            return

class DL(object):
    def __init__(self):
        self.data = None

    def set_dl_data(self,data):
        #data :dict
        self.data = data

    def do_dl_queue(self):
        for k,v in self.data.items():
            title = v.get("title")
            pic_url_list = v.get("data")
            if not title:title = k
            if not pic_url_list: continue
            arichived_path = './arichive/'+title
            Tools.mkdir(arichived_path)

            for i,u in enumerate(pic_url_list):
                arichived_name = title+"_"+str(i+1)
                arichived_name = unicode(arichived_name)
                ext = ".jpg"
                if len(u)>10 and u[-4:].lower == ".jpg":
                    arichived_name += ".jpg"
                elif len(u)>10 and u[-4:].lower == ".png":
                    arichived_name += ".png"
                    ext = ".png"
                else:
                    #try
                    arichived_name += ".jpg"
                
                f_name = arichived_path+"/"+arichived_name
                if self.check_file_exist(f_name):
                    print "exist!",f_name
                    try:
                        print "gid",unicode(k),'skip existed file',unicode(arichived_path)+"/"+unicode(arichived_name)
                    except Exception as e:
                        print "gid",unicode(k),'skip existed file index',i
                    continue
                rsc = requests.get(u)
                try:
                    with open(f_name,'wb') as f:
                        f.write(rsc.content)
                        f.close()
                except Exception as e:
                    new_path = './arichive/'+k
                    Tools.mkdir(new_path)
                    new_file_name = k+"_"+str(i+1)+ext
                    print "Err file name. new name",new_file_name
                    with open(new_path+"/"+new_file_name,'wb') as f:
                        f.write(rsc.content)
                        f.close()
                    print u"gid",unicode(k),u"file dl done:",i+1,"/",len(pic_url_list), "   ",new_path+"/"+new_file_name
                else:
                    print u"gid",unicode(k),u"file dl done:",i+1,"/",len(pic_url_list), "   ",arichived_path+"/"+arichived_name
        
    def check_file_exist(self,f_path):
        isExists=os.path.exists(f_path)
        return isExists

if __name__ == "__main__":
    print "==>start"
    
    gainer = Process_ctl()
    gainer.load_progress()
    gainer.run_range(start=0,end=2000)
    # gainer.run_queue()
    gainer.save_progress()

    data_dl = gainer.get_progress_data()
    dlobj = DL()
    dlobj.set_dl_data(data_dl)
    dlobj.do_dl_queue()

    print "==>end"

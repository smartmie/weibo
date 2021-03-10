import requests
from bs4 import BeautifulSoup
import re
from lxml import etree
import json
import ast
import time
import pandas as pd

#爬取的微博主页
url_1 = "https://www.weibo.com/gucci"
#获取评论的评论网页的目标网址上半段
url_2_up = "https://www.weibo.com/aj/v6/comment/small?ajwvr=6&act=list&mid=" 
#获取评论的评论网页的目标网址下半段
url_2_lo = "&uid=3655689037&isMain=true&dissDataFromFeed=%5Bobject%20Object%5D&ouid=1934738161&location=page_100606_home&comment_type=0&_t=0&__rnd=1591262078297"
#获取访客cookies的网页
url_3 = "https://passport.weibo.com/visitor/visitor?a=incarnate&t=39dNzddUHqqZOWZQbMiDrOvkea/y7s06WFyX%2BzsGk8w%3D&w=2&c=095&gc=&cb=cross_domain&from=weibo&_rand=0.5282100349168277"
#获取访客headers
head_1 ={
    "os":"1",
    "browser":"Chrome83,0,478,44",
    "fonts":"undefined",
    "screenInfo":"1920*1080*24",
    "Content-Type": "application/x-www-form-urlencoded",
    "plugins":"Portable Document Format::internal-pdf-viewer::Chrome PDF Plugin|::mhjfbmdgcfjbbpaeojofohoefgiehjai::Chrome PDF Viewer|::internal-nacl-plugin::Native Client",
    }
#url_2的headers
head_2 = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": "SINAGLOBAL=8502241061002.758.1589101341852; un=1756125829@qq.com; SCF=Arvt8StSxTeZ-WBoPTo0FAktokuWMSnaL8jjESqHRcGc-SsVqv1g5hDPPYELjN7etadHIW5JV7Jc9rULco5HxJI.; SUHB=0gHyUcnWWJ6Lu0; UOR=,,login.sina.com.cn; SUB=_2AkMphDU4f8NxqwJRmf0VzmvjaY9zzgrEieKf2MTjJRMxHRl-yT_nqkU4tRB6AgQbyMtqRLEOPnO5jnsXUHgsNqOJXwca; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WW6jfHz-4hBvX2TWNIe0j-S; _s_tentry=passport.weibo.com; Apache=6007990991127.461.1591261723607; ULV=1591261724574:7:1:1:6007990991127.461.1591261723607:1590848235054; TC-Page-G0=aadf640663623d805b6612f3dfe1e2c0|1591262060|1591262060; TC-V5-G0=595b7637c272b28fccec3e9d529f251a",
    "DNT": "1",
    "Host": "www.weibo.com",
    "Referer": "https://www.weibo.com/gucci?is_all=1",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 Edg/83.0.478.44",
    "X-Requested-With": "XMLHttpRequest",
}



head_3 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3970.5 Safari/537.36"
}


req = requests.session()
#过快容易获取不到内容
req.timeout = 20
#获取访问cookies
cont_1 = req.get(url_3,headers = head_1)
#有session保存了访客cookies,直接访问微博主页
cont_1 = req.get(url_1,headers = head_1)
#设置编码
cont_1.encoding = 'Unicode'

#解析网页,所有的代码都在末尾的<scrip>中
text = BeautifulSoup(cont_1.content,'lxml')
scr = text.find_all('script')
scr_text = json.loads(scr[34].get_text().lstrip('FM.view(').rstrip(')'))
html_text = scr_text['html']

#通过etree解析文本html lxml更方便
new_html = etree.HTML(html_text)
print(html_text)
print("\n\n")

#提取mid获取评论所需的mid
mid_group = new_html.xpath('//div/@mid')
print(mid_group)
#设置延迟
time.sleep(0.5)
#print(mid_group)
html_group = []

#获取评论的网页链接
for raw_mid in mid_group:
    time.sleep(1)
    tem_cont = req.get(url_2_up+raw_mid+url_2_lo, headers = head_2)
    tem_cont.encoding = 'utf8'

    #文本转数组
    tem_cont_dict = ast.literal_eval(tem_cont.text)
    #print(tem_cont_dict.get('data').get('html'))
    tem_html =tem_cont_dict.get('data').get('html')
    tem_html = tem_html.replace("\\","")
    tem_html_etree = etree.HTML(tem_html)
    #提取评论网页链接
    a = tem_html_etree.xpath('//a/@href')
    print(a)
    print("\n")
    html_group.append("https:"+a[len(a)-1])

#mid的计次
num_1 = 0 
#页码的计次
page = 1
#评论数量的计次
current_num = 0
#存储总评论
data_finally =[]
copy_data = []
#获取评论的json
url_remakedata = "https://weibo.com/aj/v6/comment/big?ajwvr=6&id={0}&page={1}&sum_comment_number={2}&from=singleWeiBo"
data_user_id = []
#mid的数量与评论网页链接数量一样
for utl_tem in html_group:
    time.sleep(1)
    #一定要访问评论的网页才能获取json
    html_text = req.get(utl_tem,headers = head_1)
    while True:
        time.sleep(1)
        #获取json
        url_remakedata_html = req.get(url_remakedata.format(str(mid_group[num_1]),str(page),str(current_num)),headers = head_3)
        url_remakedata_html.encoding = 'utf8'
        page += 1

        #提取评论
        url_remakedata_html_json = BeautifulSoup(json.loads(url_remakedata_html.content)['data']['html'])
        remark_num = json.loads(url_remakedata_html.content)['data']['count']
        if page == 2:
            print("第"+str(num_1+1)+"个mid:"+ str(mid_group[num_1]) +"  本条微博共有 "+str(remark_num)+' 个评论！')
            num = remark_num
            data_user_a = url_remakedata_html_json.select(".WB_text > a[target='_blank']")
            data_user_a =[id['href'] for id in data_user_a if id['href'][0:1] != 'h' and ]id['href'][2:3]
            print(data_user_a)
            data_user_id.append(data_user_a)
        #css选择器提起包含评论的div
        data_remake = url_remakedata_html_json.select(".WB_text")
        
        print("页码: " + str(page-1) +" 页" ) 
        print("网页: " + url_remakedata.format(str(mid_group[num_1]),str(page),str(current_num)))
        print("\n")
        
        #清理评论数据
        data_remake_new = [i.get_text().strip() for i in data_remake ]
        copy_data.append(data_remake_new[2])
        
        current_num += len(data_remake_new)
        print(data_remake_new)
        print("\n已采集"+str(current_num)+"条评论")
        print("\n\n")
        
        #判断是否获取完所有评论
        # if num <= current_num:
        #     break

        if page >= 3:
            print("------------------------------对比-------------------")
            print(data_remake_new[2])
            print(copy_data[len(copy_data)-2])
            print("\n\n")
            if data_remake_new[2] == copy_data[len(copy_data)-2]:
                print("结束采集-----------------------------------")
                break
            else:
                data_finally.append(data_remake_new)

    #初始化变量
    current_num = 0
    page = 1
    #mid计次 +1
    num_1 +=1
    print("\n")
    
#保存评论数据
with open('t.txt',"w",encoding='utf8') as f:
    f.write(str(data_finally)+"\n\n")

with open('t.txt',"w",encoding='utf8') as u:
    u.write(str(data_user_id)+"\n")
# 
# with open('data.csv','w',encoding='utf8') as f:
#     c = csv.writer(f)
#     for mid_index in range(0,len(mid_group)-1):
#         for data_index in range(0,len(data_finally)-1):
#             print('写入文件')
#             date_format = "[{},{}]"
#             c.writerow(date_format.format(mid_group[mid_index],data_finally[data_index]))

y_n = input("是否采集评论区用户的微博数据?y/n  :")
user_comment_group = []
user_i = 0
if y_n == 'y':
    cookies = req.get(url_3,headers = head_1)
    for x in data_user_id:
        for y in x:
            user_i += 1
            print("第" +str(user_i) + "个用户:" + str(y) + "\n")
            user_cont = req.get("https:"+str(y),headers = head_1)
            user_cont.encoding = 'Unicode'
            print(user_cont.text)
            user_soup = BeautifulSoup(user_cont.content,'lxml')
            user_scr = user_soup.find_all('script')
            user_text = json.loads(user_scr[34].get_text().lstrip('FM.view(').rstrip(')'))['html']
            user_html = BeautifulSoup(user_text)
            user_comment_soup = user_html.select('div[type="feed_list_content"]')
            user_comment = [t.get_text().strip() for t in user_comment_soup]
            user_comment_group.append(user_comment)
            print(user_comment)
        




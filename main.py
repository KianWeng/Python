# -*- coding: utf-8 -*-
"""
Created on Sun Oct 02 10:29:44 2016
@author: ultrakin@sina.com
"""

import re
import time  
import urllib
import smtplib 
import datetime
import pymysql
import tkinter.messagebox
from urllib import error
from email.mime.text import MIMEText
from email.utils import formataddr
from twilio.rest import Client

#获取京东商品价格函数
def getJDprice(address,time):

    #获取京东商品的ID号
    reg = r'https://item.jd.com/(.*?).html'  
    idre = re.compile(reg)  
    idlist = re.findall(idre,address)
    id = "".join(idlist[0])

    #通过数据接口查询京东商品价格
    #pc端价格数据接口  
    url1='https://p.3.cn/prices/mgets?type=1&skuIds=' + 'J_' + id
    #手机端价格数据接口  
    url2='https://p.3.cn/prices/mgets?type=2&skuIds=' + 'J_' + id
    #QQ端价格数据接口  
    url4='https://p.3.cn/prices/mgets?type=4&skuIds=' + 'J_' + id
    #微信端价格数据接口  
    url5='https://p.3.cn/prices/mgets?type=5&skuIds=' + 'J_' + id

    try:
        headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}

        #pc端价格
        request = urllib.request.Request(url = url1,headers = headers)
        html1 = urllib.request.urlopen(request).read()
        html1=html1.decode('utf-8')
        reg = r'"p":"(.*?)"'  
        pricere1 = re.compile(reg)  
        pricelist1 = re.findall(pricere1,html1)
        price1 = "".join(pricelist1[0])

        #手机端价格
        request = urllib.request.Request(url = url2,headers = headers)
        html2 = urllib.request.urlopen(request).read()
        html2=html2.decode('utf-8')
        reg = r'"p":"(.*?)"'  
        pricere2 = re.compile(reg)  
        pricelist2 = re.findall(pricere2,html2)
        price2 = "".join(pricelist2[0])

        #QQ端价格
        request = urllib.request.Request(url = url4,headers = headers)
        html4 = urllib.request.urlopen(request).read()
        html4=html4.decode('utf-8')
        reg = r'"p":"(.*?)"'  
        pricere4 = re.compile(reg)  
        pricelist4 = re.findall(pricere4,html4)
        price4 = "".join(pricelist4[0])

        #微信端价格
        request = urllib.request.Request(url = url5,headers = headers)
        html5 = urllib.request.urlopen(request).read()
        html5=html5.decode('utf-8')
        reg = r'"p":"(.*?)"'  
        pricere5 = re.compile(reg)  
        pricelist5 = re.findall(pricere5,html5)
        price5 = "".join(pricelist5[0])

        #获取系统时间
        timestamp = time

        #将数据存入列表
        priceMatrix = [id,timestamp,price1,price2,price4,price5]
        print('Time           : ' + priceMatrix[1])
        print('JD id          : ' + id)
        print('PC        price: ' + price1)
        print('APP       price: ' + price2)
        print('QQ        price: ' + price4)
        print('Wechat    price: ' + price5)
        print('\n')

        return priceMatrix    

    except error.HTTPError as e:
            print(e.code)
            print(e.reason)


#价格一致性判断函数
def priceDiff(pricelist):

    price1 = float(pricelist[-1][2])
    price2 = float(pricelist[-1][3])
    price4 = float(pricelist[-1][4])
    price5 = float(pricelist[-1][5])

    if (price1 == price2 == price4 == price5) <= 0:

        price = [price1,price2,price4,price5]
        priceMin = min(price)
        index = price.index(priceMin)

        if index == 0:
            return 'PC has a lowest price'
        elif index == 1:
            return 'APP has a lowest price'
        elif index == 2:
            return 'QQ has a lowest price'
        elif index == 3:
            return 'Wechat has a lowest price'
        else:
            return ' '


#价格环比判断函数
def priceComp(pricelist):

    if (float(pricelist[-1][2]) - float(pricelist[-2][2])) < 0:
        return 'PC has a discount'
    elif (float(pricelist[-1][3]) - float(pricelist[-2][3])) < 0:
        return 'APP has a discount'
    elif (float(pricelist[-1][4]) - float(pricelist[-2][4])) < 0:
        return 'QQ has a discount'
    elif (float(pricelist[-1][5]) - float(pricelist[-2][5])) < 0:
        return 'Wechat has a discount'
    else:
        return ' '


#价格变动提示
def priceShow(msg):
    tkinter.messagebox.showinfo(title = 'Discount Message',message = msg)


#邮件发送函数
def sendMail(address,user):
    #邮件发送者
    my_sender = 'ultrakin@163.com'
    my_user = user
    ret = True
    try:
        #邮件发送内容
        msg = MIMEText(address,'plain','utf-8')
        #邮件发送者昵称
        msg['From'] = formataddr(["MyLowerPrice",my_sender])
        #邮件接受者昵称
        msg['To'] = formataddr(["Dear Guest",my_user])
        #邮件主题
        msg['Subject'] = "A Lower Price"
        #SMTP服务器
        server = smtplib.SMTP("smtp.163.com",25)
        #发送者登录密码
        server.login(my_sender,"I will not tell you this")
        server.sendmail(my_sender,[my_user,],msg.as_string())
        server.quit()
    except Exception:
        ret = False
    return ret

#短信发送函数
def sendSMS(msg):
    
    ret = True
    account_sid = "AC01b0cfb478b5a91863e378cd028f7baa"
    auth_token = "1492775e43d5a4e2810491a495a828db"
    client = Client(account_sid, auth_token)
    
    message = client.messages.create(to="+8613735414701", from_="+15036943150", body=msg)
    print(message.error_code)
    print(message.sid)
    if message.error_code == None:
        ret = True
    else: 
        print("Error:" + message.error_message + "(Error code:" + message.error_code + ")")
        ret = False
        
    return ret

#将获取到的数据存入数据库
def savePriceToDatabase(priceMat, database_name):
    
    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='wgj19890604', db='test', charset='UTF8')
    cur = conn.cursor()
    
    database_create = 'create database if not exists %s'%database_name
    cur.execute(database_create)
    conn.select_db(database_name)
    cur.execute("create table if not exists price(item varchar(30),time varchar(30),pc varchar(20),QQ varchar(20),wechat varchar(20),APP varchar(20))")
    conn.commit()
    
    insert_sql = 'insert into price values(\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')'%(priceMat[0],priceMat[1],priceMat[2],priceMat[3],priceMat[4],priceMat[5])
    cur.execute(insert_sql)        
    conn.commit()
    
    cur.close()
    conn.close()

#主函数
def run(address):

    #价格信息存储列表
    List = [[0,0,0,0,0,0]]

    #初始基准时间
    timestart = '2017-11-8 14:17:00'
    timearrystart = time.strptime(timestart,'%Y-%m-%d %H:%M:%S')
    timestampstart = int(time.mktime(timearrystart))

    while True:

        #获取当前系统时间
        timenow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        timearrynow = time.strptime(timenow,'%Y-%m-%d %H:%M:%S')
        timestampnow = int(time.mktime(timearrynow))

        #整点起每间隔5分钟运行
        if (timestampnow - timestampstart) % 3600 == 0:

            #需要执行的函数
            priceMat = getJDprice(address,timenow)
            savePriceToDatabase(priceMat,"JD_Item_Price")
            List.extend([priceMat])

            #print List

            str0 = timenow
            str1 = priceComp(List)
            str2 = priceDiff(List)

            #弹框并发送邮件
            if (str1 != ' ') and (str2 != ' '):
                #priceShow(str0 + ' ' + str1 + ' ' + str2)
                msg = str0 + ' ' + str1 + ' ' + str2 + "Current price:PC " + priceMat[2] + " APP" + priceMat[3] + " QQ" + priceMat[4] + " Wechat" + priceMat[5]
                #ret = sendMail(address,user)
                ret = sendSMS(msg)
                if ret:
                    print("ok") 
                else:
                    print("failed")
            #防止多次执行，并通过睡眠降低CPU负载
            time.sleep(3590)


run('https://item.jd.com/5114740.html')
#sendSMS()
#savePriceToDatabase()
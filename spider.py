#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/5/15 16:10
# @Author  : ChenHuan
# @Site    : 
# @File    : spider.py
# @Desc    :
# @Software: PyCharm
import re

import requests
import time
from bs4 import BeautifulSoup


class JD_Crawl:
    """
    模拟登陆京东
    """
    def __init__(self, username, password):
        """
        初始信息配置
        :param username:
        :param password:
        """
        # User-Agent 含义:用于伪装成浏览器身份请求网页.它的意思自然就是表示浏览器的身份,说明是用的哪种浏览器进行的操作
        # Referer 含义:(这个也是爬虫常用到的，防盗链)客户端通过当前URL代表的页面出发访问我们请求的页面.爬虫中,一般我们只要把它设置成请求的网页链接就好了
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
            'Referer':'https://passport.jd.com/',
        }
        self.login_url = 'https://passport.jd.com/new/login.aspx'
        self.post_url = 'https://passport.jd.com/uc/loginService'
        self.auth_url = 'https://passport.jd.com/uc/showAuthCode'
        self.session = requests.session()
        self._username = username
        self._password = password

    def get_login_info(self):
        """
        提取表单登录信息
        :return:
        """
        # 首先对登录的login_url发起请求,获取登陆页面源码后通过BeautifulSoup解析工具ccs选择器来提取隐藏字段信息
        html = self.session.get(self.login_url, headers = self.headers).content
        soup = BeautifulSoup(html, 'lxml')

        uuid = soup.select('#uuid')[0].get('value')
        eid = soup.select('#eid')[0].get('value')
        fp = soup.select('input[name="fp"]')[0].get('value')
        _t = soup.select('input[name="_t"]')[0].get('value')
        login_type = soup.select('input[name="loginType"]')[0].get('value')
        pub_key = soup.select('input[name="pubKey"]')[0].get('value')
        sa_token = soup.select('input[name="sa_token"]')[0].get('value')

        auth_page = self.session.post(self.auth_url,
                                      data = {'loginName' : self._username}).text
        # 是否需要验证码判断
        if 'true' in auth_page:
            auth_code_url = soup.select('#JD_Verification1')[0].get('src2')
            auth_code = str(self.get_auth_img(auth_code_url))
        else:
            auth_code = ''

        data = {
            'uuid' : uuid,
            'eid' : eid,
            'fp' : fp,
            '_t' : _t,
            'loginType' : login_type,
            'loginname' : self._username,
            'nloginpwd' : self._password,
            'chkRememberMe' : True,
            'authcode' : auth_code,
            'pubKey' : pub_key,
            'sa_token' : sa_token,
        }
        print('data>>>', data)
        return data

    def get_auth_img(self, url):
        """
        获取验证码
        :return:
        """
        auth_code_url = 'http:{}&yys={}'.format(url, str(int(time.time()*1000)))
        auth_img = self.session.get(auth_code_url, headers=self.headers).content
        with open('auth_img.jpg', 'wb') as f:
            f.write(auth_img)
            f.close()
        code_typein = input('请输入下载图片中的验证码:')
        return code_typein

    def login(self):
        """
        模拟登录
        :return:
        """
        data = self.get_login_info()
        # X - Requested - With请求头用于在服务器端判断request来自Ajax请求还是传统请求
        # 如果X-Requested-With的值为 XMLHttpRequest,则为 Ajax 异步请求. 为 null 则为传统同步请求.
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
            'Referer': self.post_url,
            'X-Requested-With' : 'XMLHttpRequest',
        }
        try:
            login_page = self.session.post(self.post_url, data = data, headers = headers).text
            print('login_page>>>', login_page)
        except Exception as e:
            print(e)

    def list_actio(self):
        """
        登录验证及结果
        :return:
        """
        list_action = self.session.get('https://order.jd.com/center/list.action', headers = self.headers).text
        pattern = re.compile('申请售后')
        r = re.search(pattern, list_action)
        if r != None:
            print('验证成功')
        else:
            print('验证失败')

if __name__ == '__main__':
    username = input('请输入用户名:')
    password = input('请输入密码:')
    # 实例对象
    jd = JD_Crawl(username, password)
    jd.login()
    jd.list_actio()
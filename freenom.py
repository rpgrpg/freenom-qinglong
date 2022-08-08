#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
# 觉得好用请点 *star*，谢谢！作者仓库:https://github.com/rpgrpg/freenom-qinglong
# 设置定时任务，例如每周一早5点运行：corn * 5 * * 2
# V20228

import requests
import re
try:
    from notify import send
except:
    print("upload notify failed")
    exit(-1)

# 在 '' 中填写freenom用户名，示例：username = '87654321@qq.com'
username = ''
# 在 '' 中填写freenom密码，示例：password = '12345678'
password = ''

# 登录
LOGIN_URL = 'https://my.freenom.com/dologin.php'
# 域名状态
DOMAIN_STATUS_URL = 'https://my.freenom.com/domains.php?a=renewals'
# 续期
RENEW_DOMAIN_URL = 'https://my.freenom.com/domains.php?submitrenewals=true'

# token匹配
token_ptn = re.compile('name="token" value="(.*?)"', re.I)
# 域名匹配
domain_info_ptn = re.compile(
    r'<tr><td>(.*?)</td><td>[^<]+</td><td>[^<]+<span class="[^<]+>(\d+?).Days</span>[^&]+&domain=(\d+?)">.*?</tr>',
    re.I)
# 登录匹配
login_status_ptn = re.compile('<a href="logout.php">Logout</a>', re.I)

# 请求头
sess = requests.Session()
sess.headers.update({
    'user-agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/103.0.5060.134 Safari/537.36'
})

# 登录
sess.headers.update({
    'content-type': 'application/x-www-form-urlencoded',
    'referer': 'https://my.freenom.com/clientarea.php'
})
# 开启网络登录
try:  # 异常捕捉
    r = sess.post(LOGIN_URL, data={'username': username, 'password': password})

    if r.status_code != 200:
        print('Can not login. Pls check username&password.')
        exit(-1)

    # 查看域名状态
    sess.headers.update({'referer': 'https://my.freenom.com/clientarea.php'})
    r = sess.get(DOMAIN_STATUS_URL)
except:
    print('Network failed.')
    exit(-1)
# 确认登录状态
if not re.search(login_status_ptn, r.text):
    print('login failed, retry')
    exit(-1)

# 获取token
page_token = re.search(token_ptn, r.text)
if not page_token:
    print('page_token missed')
    exit(-1)
token = page_token.group(1)

# 获取域名列表
domains = re.findall(domain_info_ptn, r.text)
domains_list = []
renew_domains_succeed = []
renew_domains_failed = []


# 域名续期
for domain, days, renewal_id in domains:
    days = int(days)
    domains_list.append(f'{domain} in {days} days')
    if days < 14:
        sess.headers.update({
            'referer':
            f'https://my.freenom.com/domains.php?a=renewdomain&domain={renewal_id}',
            'content-type': 'application/x-www-form-urlencoded'
        })
        try:
            r = sess.post(RENEW_DOMAIN_URL,
                          data={
                              'token': token,
                              'renewalid': renewal_id,
                              f'renewalperiod[{renewal_id}]': '12M',
                              'paymentmethod': 'credit'
                          })
        except:
            print('Network failed.')
            exit(-1)
        if r.text.find('Order Confirmation') != -1:
            renew_domains_succeed.append(domain)
            print(domain, ' renew succeed')
        else:
            renew_domains_failed.append(domain)
            print(domain, ' renew failed')

# 输出结果并推送通知
print(domains_list, renew_domains_succeed, renew_domains_failed)
if renew_domains_failed:
    send('Caution! ', f'renew failed:{renew_domains_failed}')
else:
    send(f'Domains list:{domains_list}', f'Renew: {renew_domains_succeed}')

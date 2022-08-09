#!/usr/bin/env python3
# _*_ coding:utf-8 _*_

# 觉得好用请点 *star*，作者仓库:https://github.com/rpgrpg/freenom-qinglong.git

# 重要！！请手动修改下面corn的值，第一个*取值范围0~59，第二位的5建议改为8~22之间的数字，否则你将会在凌晨5点被通知吵醒
# Caution: Pls replace the corn, 1st * to 0~59, 2nd 5 to 8~22
'''
cron: * 5 * * 2 
new Env:('freenom域名自动续期');
'''
# 配置环境变量：export freenom_usr=""，""内为你自己的FREENOM的用户名
# 配置环境变量：export freenom_psd=""，""内为你自己的FREENOM密码
# V20228

import requests
import re,os
try:
    from notify import send
except:
    print("upload notify failed")
    exit(-1)
try:
    # 没有设置环境变量可以在此处直接填写freenom用户名，示例：username = '87654321@qq.com'
    username = os.environ["freenom_usr"]
    # 没有设置环境变量可以在此处直接填写freenom密码，示例：password = '12345678'
    password = os.environ["freenom_psd"]
except:
    print("Pls config export in config.sh OR fill in username&password.")
# 登录url
LOGIN_URL = 'https://my.freenom.com/dologin.php'
# 域名状态url
DOMAIN_STATUS_URL = 'https://my.freenom.com/domains.php?a=renewals'
# 续期url
RENEW_DOMAIN_URL = 'https://my.freenom.com/domains.php?submitrenewals=true'

# 登录匹配
token_ptn = re.compile('name="token" value="(.*?)"', re.I)
domain_info_ptn = re.compile(
    r'<tr><td>(.*?)</td><td>[^<]+</td><td>[^<]+<span class="[^<]+>(\d+?).Days</span>[^&]+&domain=(\d+?)">.*?</tr>',
    re.I)
login_status_ptn = re.compile('<a href="logout.php">Logout</a>', re.I)
sess = requests.Session()
sess.headers.update({
    'user-agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/103.0.5060.134 Safari/537.36'
})
sess.headers.update({
    'content-type': 'application/x-www-form-urlencoded',
    'referer': 'https://my.freenom.com/clientarea.php'
})

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
        else:
            renew_domains_failed.append(domain)

# 输出结果并推送通知
print(domains_list, renew_domains_succeed, renew_domains_failed)
if renew_domains_failed:
    send('Caution! ', f'renew failed:{renew_domains_failed}')
else:
    send(f'Domains list:{domains_list}', f'Renew: {renew_domains_succeed}')

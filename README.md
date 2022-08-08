# freenom-qinglong 域名自动续期-青龙面板
Automatically Renew Freenom Domain for qinglong panle.
# How to use食用方法：
本程序适用于青龙面板https://github.com/whyour/qinglong.git
# 新版青龙：
订阅管理-新建订阅-名称：自定义，链接：https://github.com/rpgrpg/freenom-qinglong.git ，定时规则：自定义，确定之后，点击运行按钮运行一次即可。
# 老板青龙：
无订阅管理，定时任务-新建任务-名称：自定义，命令：ql repo https://github.com/rpgrpg/freenom-qinglong.git "freenom.py" ，定时规则：自定义，确定之后，点击运行按钮运行一次即可。
# 更改《freenom域名自动续期》任务的cron
不改也能运行，但有可能会在深夜被通知吵醒，建议改在白天的某个时点，一周一、两次即可。freenom是目前全网唯一的免费顶级域名注册网站了，大家轻撸，避免滥用。
# 修改配置文件config.sh，添加环境变量
点击面板左侧的“配置文件”，然后将文件拉到最后，添加如下两行：
export freenom_usr=""   ""内为你自己的FREENOM的用户名
export freenom_psd=""   ""内为你自己的FREENOM密码
示例：
export freenom_usr="12345678@qq.com"
export freenom_psd="76543210"

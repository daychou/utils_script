## utils_script

自己平时所写的和收集来的小工具，做一个集合

## 介绍
目录/文件                    | 语言       | 功能说明                    |  备注  |
----------------------|---------|-------------------------|------------|
dingding              | golang       | 为zabbix写的一个钉钉报警插件 | https://open-dev.dingtalk.com/#/index 通过钉钉开发者平台配置来发送消息|
check_dns.py        | python       | 检测域名解析IP是否在指定IP段 | 监控脚本，一般放在cron里定时执,异常信息通过钉钉群webhook机器人通知 |
log_archive.py        | python       | 归档压缩指定目录下的日志文件，文件匹配规则为\d{4}-\d{2}-\d{2} | |



## License

Apache 2.0 License

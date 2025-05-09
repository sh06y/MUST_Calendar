# MUST_Calendar 将wemust课表通过ics导入系统日历（iOS、Android、HarmonyOS、Mac OS）

## 配置方法

1. Fork仓库
2. Settings - Security - Secrets and variables - Actions - New repository secret
3. 在 name 中填写 ```USERNAME```，Secret为学号
4. 同理，再添加一个secret，名为```PASSWORD```，Value 为 Wemust 密码
5. done

## 使用方法（以IOS为例）

1. 打开日历
2. 日历-添加日历-添加订阅日历
3. 输入 <https://raw.githubusercontent.com/你的GitHub账号/MUST_Calendar/refs/heads/main/output.ics>

日历会在每周一、周五更新，可在```.github/workflows/python-app.yml```中修改。

## TODO

- [x] 多学期
- [] 多语言支持

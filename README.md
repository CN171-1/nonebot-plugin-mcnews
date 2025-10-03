# README

## 描述

一个基于 NoneBot2 的插件，用于定时获取 Minecraft 官方新闻 与 Minecraft Feedback 平台的最新文章，并在指定的群组内发送消息通知。

## 功能特点

- 定时从 [minecraft.net](https://www.minecraft.net) 拉取新闻文章
- 定时从 [Minecraft Feedback](https://minecraftfeedback.zendesk.com/) 拉取最新文章
- 在指定群组内发送更新通知消息

## 安装

<details>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-mcnews

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-mcnews
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-mcnews
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-mcnews
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-mcnews
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot-plugin-mcnews"]

</details>

## 配置项

可通过 NoneBot2 配置文件（如`.env`）进行配置：

| 配置项                      | 类型   | 默认值   | 说明                            |
| ------------------------ | ---- | ----- | ----------------------------- |
| `mcnews_debug`           | bool | False | 开启调试模式，输出异常堆栈                |
| `mcnews_proixes`         | str | None    | 代理设置 |
| `mcnews_group_id`           | int / str  | []    | 指定自动推送消息的群组 ID                    |

## 鸣谢

- [nonebot-plugin-apscheduler](https://github.com/nonebot/plugin-apscheduler) - NoneBot 的定时任务插件
- [nonebot-plugin-localstore](https://github.com/nonebot/plugin-localstore) - NoneBot 的本地数据存储插件

## 反馈

- 问题跟踪：[GitHub Issues](https://github.com/CN171-1/nonebot-plugin-mcnews/issues)

## 许可

MIT License.

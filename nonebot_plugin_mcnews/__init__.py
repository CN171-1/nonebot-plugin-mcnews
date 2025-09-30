from nonebot.plugin import PluginMetadata
from pydantic import BaseModel

__plugin_meta__ = PluginMetadata(
    name="MC新闻更新检测",
    description="Minecraft 官方新闻推送",
    usage="自动推送 Minecraft 官方新闻",
    type="application",
    homepage="https://github.com/CN171-1/nonebot_plugin_mcnews",
    supported_adapters={"~onebot.v11"},
)

import os
import httpx
from datetime import datetime, timedelta
from nonebot import on_command, get_bots, require, logger, get_plugin_config

class MCNewsConfig(BaseModel):
    """Minecraft News 配置"""
    debug: bool = False
    mcnews_group_id: list[int | str] = []  # 要推送的QQ群列表

config = get_plugin_config(MCNewsConfig)
mcnews_group_id = config.mcnews_group_id
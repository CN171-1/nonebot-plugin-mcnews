from nonebot.plugin import PluginMetadata
from pydantic import BaseModel

class MCNewsConfig(BaseModel):
    """Minecraft News 配置"""
    mcnews_debug: bool = False
    mcnews_proxies: str = None  # 代理设置
    mcnews_group_id: list[int | str] = []  # 要推送的QQ群列表
    mcnews_translate: bool = False  # 是否启用翻译
    mcnews_translate_appid: str = None  # 百度翻译appid
    mcnews_translate_appkey: str = None  # 百度翻译appkey
    mcnews_translate_needIntervene: int = 0  # 百度翻译是否使用术语库，0-不启用，1-启用

__plugin_meta__ = PluginMetadata(
    name="MC新闻更新检测",
    description="Minecraft 官方新闻推送",
    usage="自动推送 Minecraft 官方新闻",
    type="application",
    homepage="https://github.com/CN171-1/nonebot-plugin-mcnews",
    supported_adapters={"~onebot.v11"},
    config=MCNewsConfig,
)

import httpx
import json
import random
from nonebot.adapters.onebot.v11 import Message
from nonebot import get_bots, require, logger, get_plugin_config

config = get_plugin_config(MCNewsConfig)
proxy = config.mcnews_proxies
mcnews_group_id = config.mcnews_group_id

require("nonebot_plugin_localstore")

import nonebot_plugin_localstore as store

# 数据存储管理
class StorageManager:
    def __init__(self):
        self.data_dir = store.get_plugin_data_dir()
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    async def get_stored_list(self, key: str) -> list[str]:
        """获取存储的列表数据"""
        file_path = self.data_dir / f"{key}.json"
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    async def update_stored_list(self, key: str, data: list[str]):
        """更新存储的列表数据"""
        file_path = self.data_dir / f"{key}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    async def is_first_run(self, key: str) -> bool:
        """检查是否是第一次运行"""
        file_path = self.data_dir / f"{key}.json"
        return not file_path.exists()

# 创建全局存储管理器实例
storage_manager = StorageManager()

# 存储包装函数
async def get_stored_list(key: str) -> list[str]:
    return await storage_manager.get_stored_list(key)

async def update_stored_list(key: str, data: list[str]):
    await storage_manager.update_stored_list(key, data)

async def is_first_run(key: str) -> bool:
    return await storage_manager.is_first_run(key)

async def get_json(url: str, timeout: int = 30) -> dict:
    """获取JSON数据"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0"
    }
    try:
        async with httpx.AsyncClient(timeout=timeout, headers=headers, proxy=proxy) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error fetching JSON from {url}: {e}")
        if config.mcnews_debug:
            import traceback
            logger.error(traceback.format_exc())
        return {}

def make_md5(s: str, encoding='utf-8') -> str:
    from hashlib import md5
    return md5(s.encode(encoding)).hexdigest()

async def baidu_translate_batch(texts: list[str]) -> list[str]:
    """
    批量翻译多个文本（title 和 desc），返回翻译后的列表，顺序与输入一致。
    """  
    
    appid = config.mcnews_translate_appid
    appkey = config.mcnews_translate_appkey
    needIntervene = config.mcnews_translate_needIntervene
    
    # 用换行符拼接多个要翻译的文本
    query = "\n".join(texts)
    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)

    payload = {
        "appid": appid,
        "q": query,
        "from": "en",
        "to": "zh",
        "salt": salt,
        "sign": sign,
        "needIntervene": needIntervene
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("http://api.fanyi.baidu.com/api/trans/vip/translate",
                                         params=payload, headers=headers)
            data = response.json()
            if "trans_result" in data:
                # trans_result 是 list，每个元素对应一段翻译
                return [item["dst"] for item in data["trans_result"]]
            else:
                logger.error(f"百度翻译 API 返回异常: {data}")
                return "调用百度翻译失败,请开发者前往后台查看具体错误信息。"
    except Exception as e:
        logger.error(f"调用百度翻译失败: {e}")
        return "调用百度翻译失败,请开发者前往后台查看具体错误信息。"

async def broadcast_message(message: Message):
    """广播消息到设置的群组ID中"""
    bots = get_bots()
    bot = None  # 初始化bot为None
    bot = list(bots.values())[0]# 获取第一个机器人实例
    if mcnews_group_id:
        for group_id in mcnews_group_id:
            try:
                await bot.send_group_msg(
                    group_id=int(group_id),
                    message=message)
            except Exception as e:
                logger.error(f"向群组 {group_id} 推送MC官网文章更新消息失败: {e}")
        logger.success("已发现并成功推送MC官网文章更新信息")
    else:
        logger.warning("未配置MC官网文章更新推送群组，跳过推送")
        
require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

@scheduler.scheduled_job("interval", minutes=5, id="minecraft_news", misfire_grace_time=10)
async def minecraft_news_schedule():
    baseurl = "https://www.minecraft.net"
    url = "https://www.minecraft.net/content/minecraftnet/language-masters/en-us/jcr:content/root/container/image_grid_a_copy_64.articles.page-1.json"
    
    try:
        data = await get_json(url)
        if not data:
            logger.error("获取 Minecraft 官网新闻失败。")
            return
            
        alist = await get_stored_list("mcnews")
        articles = data["article_grid"]
        
        # 检查是否是第一次运行
        first_run = await is_first_run("mcnews")
        
        for article in articles:
            default_tile = article["default_tile"]
            title = default_tile["title"]
            desc = default_tile["sub_header"]
            article_url = article["article_url"]
            
            if not title or not article_url:
                continue
                
            link = baseurl + article_url
            
            if title not in alist:
                # 如果是第一次运行，只记录文章标题但不发送消息
                if first_run:
                    alist.append(title)
                else:
                    if config.mcnews_translate:
                        tr_title, tr_desc = await baidu_translate_batch([title, desc])
                        message = Message(
                            f"Minecraft 官网发布了新的文章：\n"
                            f"{title}\n{tr_title}\n\n"
                            f"{desc}\n{tr_desc}\n"
                            f"{link}"
                        )
                    else:
                        message = Message(
                            f"Minecraft 官网发布了新的文章：\n"
                            f"{title}\n"
                            f"{desc}\n\n"
                            f"{link}"
                        )
                    await broadcast_message(message)
                    
                    logger.info(f"发现MC官网文章更新：{title}")
                    alist.append(title)
        
        # 如果是第一次运行，保存初始列表
        if first_run:
            await update_stored_list("mcnews", alist)
            logger.info("首次运行，初始化官网文章列表完成。")
        elif alist:  # 只有在有更新时才保存
            await update_stored_list("mcnews", alist)
                
    except Exception as e:
        if config.mcnews_debug:
            logger.exception(f"Error in minecraft_news_schedule: {e}")
        else:
            logger.error(f"Error in minecraft_news_schedule: {e}")

@scheduler.scheduled_job("interval", minutes=5, id="feedback_news", misfire_grace_time=10)
async def feedback_news_schedule():
    sections = [
        {
            "name": "beta",
            "url": "https://minecraftfeedback.zendesk.com/api/v2/help_center/en-us/sections/360001185332/articles?per_page=5",
            "key": "mcfeedbacknews_beta"  # 为每个API使用不同的存储键名
        },
        {
            "name": "article", 
            "url": "https://minecraftfeedback.zendesk.com/api/v2/help_center/en-us/sections/360001186971/articles?per_page=5",
            "key": "mcfeedbacknews_article"  # 为每个API使用不同的存储键名
        },
    ]
    
    for section in sections:
        try:
            key = section["key"]
            alist = await get_stored_list(key)
            
            # 检查是否是第一次运行
            first_run = await is_first_run(key)
            
            data = await get_json(section["url"])
            if not data:
                continue
                
            articles = data["articles"]
            
            for article in articles:
                name = article["name"]
                if not name:
                    continue
                    
                if name not in alist:
                    link = article["html_url"]
                    
                    # 如果是第一次运行，只记录文章标题但不发送消息
                    if first_run:
                        alist.append(name)
                    else:
                        message = f"Minecraft Feedback 发布了新的文章：\n{name}\n{link}"
                        await broadcast_message(message)
                        
                        logger.info(f"发现MC Feedback文章更新： {name}")
                        alist.append(name)
            
            # 如果是第一次运行，保存初始列表
            if first_run:
                await update_stored_list(key, alist)
                logger.info(f"首次运行，初始化Feedback_{section['name']}文章列表完成。")
            elif alist:  # 只有在有更新时才保存
                await update_stored_list(key, alist)
                    
        except Exception as e:
            if config.mcnews_debug:
                logger.exception(f"Error in feedback_news_schedule_{section['name']}: {e}")
            else:
                logger.error(f"Error in feedback_news_schedule_{section['name']}: {e}")

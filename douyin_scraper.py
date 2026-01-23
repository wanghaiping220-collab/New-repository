"""
热榜抓取模块（支持配置化）
"""
import requests
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from config_loader import ConfigLoader

logger = logging.getLogger(__name__)


class DouyinScraper:
    """热榜抓取器（支持多数据源和内容板块）"""

    def __init__(self, config_loader: Optional[ConfigLoader] = None):
        """
        初始化抓取器

        Args:
            config_loader: 配置加载器，如果为 None 则使用默认配置
        """
        # 加载配置
        self.config_loader = config_loader or ConfigLoader()
        scraper_config = self.config_loader.get_scraper_config()

        # 获取 API URLs
        self.api_urls = self.config_loader.get_all_api_urls()

        # 如果没有配置 API，使用默认的
        if not self.api_urls:
            self.api_urls = [
                "https://aweme.snssdk.com/aweme/v1/hot/search/list/",
                "https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/",
                "https://aweme.snssdk.com/aweme/v1/hotsearch/star/billboard/",
                "https://aweme.snssdk.com/aweme/v1/chart/music/list/",
            ]

        # 请求头
        self.headers = scraper_config.get('headers', {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.douyin.com/',
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cookie': '',
        })

        # 超时时间
        self.timeout = scraper_config.get('timeout', 10)

        # 标记最后一次抓取是否使用了测试数据
        self.is_using_test_data = False
        # 记录成功的 API 来源
        self.last_successful_api = None
        # 记录当前使用的数据源名称
        self.current_source_name = "未知"

    def fetch_hot_list(self, limit: int = 20, category: str = 'all') -> Optional[List[Dict]]:
        """
        抓取热榜

        Args:
            limit: 返回的热榜数量，默认20条
            category: 内容板块，默认 'all'（综合）

        Returns:
            热榜列表，每个元素包含 rank, word, hot_value 等信息
        """
        logger.info(f"开始抓取热榜（板块: {category}, 数量: {limit}）...")

        # 尝试多个 API
        for api_url in self.api_urls:
            try:
                logger.info(f"尝试 API: {api_url}")

                response = requests.get(
                    api_url,
                    headers=self.headers,
                    timeout=self.timeout
                )

                logger.info(f"响应状态码: {response.status_code}")

                if response.status_code != 200:
                    logger.warning(f"API 返回非 200 状态码: {response.status_code}")
                    continue

                data = response.json()
                logger.info(f"API 返回数据结构: {list(data.keys()) if isinstance(data, dict) else type(data)}")

                # 尝试解析不同格式的响应
                word_list = self._parse_response(data)

                if word_list:
                    # 格式化热榜数据
                    hot_list = []
                    for idx, item in enumerate(word_list[:limit], 1):
                        # 提取关键字/标题（尝试多个可能的字段）
                        word = (
                            item.get('word') or
                            item.get('title') or
                            item.get('sentence') or
                            item.get('query') or
                            item.get('name') or
                            item.get('music_title') or
                            ''
                        )

                        # 提取热度值（尝试多个可能的字段）
                        hot_value = (
                            item.get('hot_value') or
                            item.get('view_count') or
                            item.get('hot_level') or
                            item.get('search_count') or
                            0
                        )

                        hot_item = {
                            'rank': idx,
                            'word': word,
                            'hot_value': hot_value,
                            'label': item.get('label', item.get('tag', '')),
                            'event_time': item.get('event_time', ''),
                        }
                        hot_list.append(hot_item)

                    # 识别数据源
                    self._identify_source(api_url)

                    logger.info(f"✅ 成功抓取 {len(hot_list)} 条热榜数据（来源：{self.current_source_name}）")

                    # 根据板块过滤
                    if category and category != 'all':
                        hot_list = self.config_loader.filter_by_category(hot_list, category)
                        logger.info(f"板块过滤后: {len(hot_list)} 条")

                    # 限制数量
                    hot_list = hot_list[:limit]

                    self.is_using_test_data = False
                    self.last_successful_api = api_url
                    return hot_list

            except requests.RequestException as e:
                logger.warning(f"API {api_url} 请求失败: {e}")
                continue
            except json.JSONDecodeError as e:
                logger.warning(f"API {api_url} JSON 解析失败: {e}")
                continue
            except Exception as e:
                logger.warning(f"API {api_url} 处理失败: {e}")
                continue

        # 如果所有 API 都失败，返回测试数据
        logger.warning("所有 API 都无法获取数据，返回测试数据")
        self.is_using_test_data = True
        return self._get_test_data(limit)

    def _identify_source(self, api_url: str):
        """
        识别数据源名称

        Args:
            api_url: API URL
        """
        # 从配置中查找对应的数据源
        data_sources = self.config_loader.config.get('data_sources', {})
        for source_key, source_config in data_sources.items():
            apis = source_config.get('apis', [])
            for api in apis:
                if api.get('url') == api_url:
                    self.current_source_name = source_config.get('name', source_key)
                    return

        # 如果没找到，根据 URL 猜测
        if 'douyin' in api_url or 'aweme' in api_url:
            self.current_source_name = "抖音"
        elif 'weibo' in api_url:
            self.current_source_name = "微博"
        elif 'zhihu' in api_url:
            self.current_source_name = "知乎"
        else:
            self.current_source_name = "未知来源"

    def _parse_response(self, data: dict) -> Optional[List[Dict]]:
        """
        解析不同格式的 API 响应

        Args:
            data: API 响应数据

        Returns:
            热榜列表
        """
        if not data:
            return None

        # 格式 1: {status_code: 0, word_list: [...]}
        if isinstance(data, dict) and data.get('status_code') == 0:
            word_list = data.get('word_list', [])
            if word_list:
                logger.info(f"解析格式：status_code + word_list")
                return word_list

        # 格式 2: {data: {word_list: [...]}}
        if isinstance(data, dict) and 'data' in data and isinstance(data['data'], dict):
            word_list = data['data'].get('word_list', [])
            if word_list:
                logger.info(f"解析格式：data.word_list")
                return word_list

        # 格式 3: {data: [...]} - 直接列表
        if isinstance(data, dict) and 'data' in data:
            if isinstance(data['data'], list) and len(data['data']) > 0:
                logger.info(f"解析格式：data[] 直接列表")
                return data['data']

        # 格式 4: 直接是列表
        if isinstance(data, list) and len(data) > 0:
            logger.info(f"解析格式：直接列表")
            return data

        # 格式 5: {extra: {list: [...]}} - 某些 API 的额外字段
        if isinstance(data, dict) and 'extra' in data:
            extra = data.get('extra', {})
            if isinstance(extra, dict):
                hot_list = extra.get('list', [])
                if hot_list:
                    logger.info(f"解析格式：extra.list")
                    return hot_list

        # 格式 6: 尝试查找包含热榜数据的字段（通用）
        if isinstance(data, dict):
            # 常见的热榜数据字段名
            possible_keys = ['word_list', 'list', 'data', 'items', 'hot_list', 'search_list']
            for key in possible_keys:
                if key in data and isinstance(data[key], list) and len(data[key]) > 0:
                    logger.info(f"解析格式：通用字段 {key}")
                    return data[key]

        logger.warning(f"无法解析 API 响应，数据结构未知")
        return None

    def _get_test_data(self, limit: int = 20) -> List[Dict]:
        """
        生成测试数据（当所有 API 都失败时使用）

        Args:
            limit: 数据数量

        Returns:
            测试热榜列表
        """
        logger.info("生成测试数据")

        test_items = [
            "春节档电影票房破纪录",
            "AI 技术新突破",
            "2024 年经济展望",
            "健康生活方式分享",
            "科技创新引领未来",
            "环保出行新方案",
            "美食制作小技巧",
            "旅游目的地推荐",
            "职场技能提升",
            "家居装饰灵感",
            "运动健身日常",
            "读书分享会",
            "音乐节精彩瞬间",
            "艺术展览回顾",
            "时尚穿搭指南",
            "宠物日常趣事",
            "数码产品测评",
            "游戏攻略分享",
            "教育资源推荐",
            "公益活动参与",
        ]

        hot_list = []
        for idx in range(min(limit, len(test_items))):
            hot_list.append({
                'rank': idx + 1,
                'word': test_items[idx],
                'hot_value': (20 - idx) * 10000000,  # 递减的热度值
                'label': '热' if idx < 3 else '',
                'event_time': '',
            })

        return hot_list

    def format_hot_list_text(self, hot_list: List[Dict], is_test_data: bool = False, category: str = 'all') -> str:
        """
        将热榜数据格式化为文本

        Args:
            hot_list: 热榜列表
            is_test_data: 是否为测试数据
            category: 内容板块

        Returns:
            格式化后的文本
        """
        if not hot_list:
            return "暂无热榜数据"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        display_config = self.config_loader.get_display_config()

        # 获取板块名称
        category_name = self.config_loader.get_category_name(category) if category != 'all' else '综合热榜'

        if is_test_data:
            lines = [
                f"⚠️ 热榜服务异常 - 测试数据 ({timestamp})",
                "",
                "说明：当前热榜 API 无法访问，以下为测试数据。",
                "可能原因：网络限制、API 地址变更、需要登录态等。",
                ""
            ]
        else:
            # 使用配置的标题格式
            title_format = display_config.get('title_format', '📊 {source} - {category} Top{count}')
            title = title_format.format(
                source=self.current_source_name,
                category=category_name,
                count=len(hot_list),
                time=timestamp
            )
            lines = [f"{title} ({timestamp})\n"]

        # 获取显示配置
        show_hot_value = display_config.get('show_hot_value', True)
        show_label = display_config.get('show_label', True)

        for item in hot_list:
            rank = item['rank']
            word = item['word']
            hot_value = item['hot_value']
            label = item.get('label', '')

            # 添加排名图标
            if rank == 1:
                icon = "🥇"
            elif rank == 2:
                icon = "🥈"
            elif rank == 3:
                icon = "🥉"
            else:
                icon = f"{rank}."

            # 格式化热度值
            hot_str = ""
            if show_hot_value and hot_value:
                if hot_value >= 100000000:
                    hot_str = f" 🔥{hot_value / 100000000:.1f}亿"
                elif hot_value >= 10000:
                    hot_str = f" 🔥{hot_value / 10000:.1f}万"
                else:
                    hot_str = f" 🔥{hot_value}"

            # 添加标签
            label_str = ""
            if show_label and label:
                label_str = f" [{label}]"

            lines.append(f"{icon} {word}{label_str}{hot_str}")

        return "\n".join(lines)


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    scraper = DouyinScraper()
    hot_list = scraper.fetch_hot_list(10)

    if hot_list:
        print(scraper.format_hot_list_text(hot_list, is_test_data=scraper.is_using_test_data))

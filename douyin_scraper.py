"""
抖音热榜抓取模块
"""
import requests
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class DouyinScraper:
    """抖音热榜抓取器"""

    def __init__(self):
        """初始化抓取器"""
        # 多个备用 API 地址
        self.api_urls = [
            "https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/",
            "https://aweme.snssdk.com/aweme/v1/hot/search/list/",
        ]

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.douyin.com/',
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cookie': '',
        }

        # 标记最后一次抓取是否使用了测试数据
        self.is_using_test_data = False

    def fetch_hot_list(self, limit: int = 20) -> Optional[List[Dict]]:
        """
        抓取抖音热榜

        Args:
            limit: 返回的热榜数量，默认20条

        Returns:
            热榜列表，每个元素包含 rank, word, hot_value 等信息
        """
        logger.info("开始抓取抖音热榜...")

        # 尝试多个 API
        for api_url in self.api_urls:
            try:
                logger.info(f"尝试 API: {api_url}")

                response = requests.get(
                    api_url,
                    headers=self.headers,
                    timeout=10
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
                        hot_item = {
                            'rank': idx,
                            'word': item.get('word', item.get('title', item.get('query', ''))),
                            'hot_value': item.get('hot_value', item.get('view_count', 0)),
                            'label': item.get('label', ''),
                            'event_time': item.get('event_time', ''),
                        }
                        hot_list.append(hot_item)

                    logger.info(f"成功抓取 {len(hot_list)} 条热榜数据")
                    self.is_using_test_data = False
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

    def _parse_response(self, data: dict) -> Optional[List[Dict]]:
        """
        解析不同格式的 API 响应

        Args:
            data: API 响应数据

        Returns:
            热榜列表
        """
        # 格式 1: {status_code: 0, word_list: [...]}
        if isinstance(data, dict) and data.get('status_code') == 0:
            word_list = data.get('word_list', [])
            if word_list:
                return word_list

        # 格式 2: {data: {word_list: [...]}}
        if isinstance(data, dict) and 'data' in data:
            word_list = data['data'].get('word_list', [])
            if word_list:
                return word_list

        # 格式 3: {data: [...]}
        if isinstance(data, dict) and 'data' in data:
            if isinstance(data['data'], list):
                return data['data']

        # 格式 4: 直接是列表
        if isinstance(data, list):
            return data

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

    def format_hot_list_text(self, hot_list: List[Dict], is_test_data: bool = False) -> str:
        """
        将热榜数据格式化为文本

        Args:
            hot_list: 热榜列表
            is_test_data: 是否为测试数据

        Returns:
            格式化后的文本
        """
        if not hot_list:
            return "暂无热榜数据"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if is_test_data:
            lines = [
                f"⚠️ 抖音热榜服务异常 - 测试数据 ({timestamp})",
                "",
                "说明：当前抖音热榜 API 无法访问，以下为测试数据。",
                "可能原因：网络限制、API 地址变更、需要登录态等。",
                ""
            ]
        else:
            lines = [f"📊 抖音热榜 Top{len(hot_list)} ({timestamp})\n"]

        for item in hot_list:
            rank = item['rank']
            word = item['word']
            hot_value = item['hot_value']
            label = item.get('label', '')

            # 格式化热度值
            if hot_value >= 100000000:
                hot_str = f"{hot_value / 100000000:.1f}亿"
            elif hot_value >= 10000:
                hot_str = f"{hot_value / 10000:.1f}万"
            else:
                hot_str = str(hot_value)

            # 添加标签
            label_str = f" [{label}]" if label else ""

            # 添加排名图标
            if rank == 1:
                icon = "🥇"
            elif rank == 2:
                icon = "🥈"
            elif rank == 3:
                icon = "🥉"
            else:
                icon = f"{rank}."

            lines.append(f"{icon} {word}{label_str} 🔥{hot_str}")

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

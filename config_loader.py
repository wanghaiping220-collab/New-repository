"""
配置加载器
支持从 YAML 文件和环境变量加载配置
"""
import os
import yaml
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ConfigLoader:
    """配置加载器"""

    def __init__(self, config_file: str = 'config.yaml'):
        """
        初始化配置加载器

        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """
        加载配置文件

        Returns:
            配置字典
        """
        try:
            # 尝试加载 YAML 配置文件
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    logger.info(f"成功加载配置文件: {self.config_file}")
                    return config or {}
            else:
                logger.warning(f"配置文件不存在: {self.config_file}，使用默认配置")
                return self._get_default_config()

        except Exception as e:
            logger.error(f"加载配置文件失败: {e}，使用默认配置")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """
        获取默认配置

        Returns:
            默认配置字典
        """
        return {
            'data_sources': {
                'douyin': {
                    'enabled': True,
                    'name': '抖音热榜',
                    'apis': [
                        {
                            'url': 'https://aweme.snssdk.com/aweme/v1/hot/search/list/',
                            'type': 'hot_search',
                            'description': '综合热搜榜'
                        }
                    ]
                }
            },
            'content_categories': {
                'all': {
                    'enabled': True,
                    'name': '综合热榜',
                    'keywords': [],
                    'description': '所有热门内容'
                }
            },
            'scraper': {
                'limit': 20,
                'timeout': 10,
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                }
            },
            'display': {
                'show_source': True,
                'show_hot_value': True,
                'show_label': True,
                'title_format': '📊 {source} - {category} Top{count}'
            }
        }

    def get_enabled_data_sources(self) -> Dict[str, Dict]:
        """
        获取启用的数据源

        Returns:
            启用的数据源字典
        """
        data_sources = self.config.get('data_sources', {})

        # 从环境变量读取启用的数据源
        env_sources = os.getenv('ENABLED_DATA_SOURCES', '')
        if env_sources:
            enabled_names = [s.strip() for s in env_sources.split(',')]
            # 只返回环境变量中指定的数据源
            return {
                name: source for name, source in data_sources.items()
                if name in enabled_names
            }

        # 返回配置文件中启用的数据源
        return {
            name: source for name, source in data_sources.items()
            if source.get('enabled', False)
        }

    def get_enabled_categories(self) -> Dict[str, Dict]:
        """
        获取启用的内容板块

        Returns:
            启用的内容板块字典
        """
        categories = self.config.get('content_categories', {})

        # 从环境变量读取启用的板块
        env_categories = os.getenv('ENABLED_CATEGORIES', '')
        if env_categories:
            enabled_names = [c.strip() for c in env_categories.split(',')]
            # 只返回环境变量中指定的板块
            result = {
                name: category for name, category in categories.items()
                if name in enabled_names
            }
            if result:
                return result

        # 返回配置文件中启用的板块
        enabled = {
            name: category for name, category in categories.items()
            if category.get('enabled', False)
        }

        # 如果没有启用任何板块，默认启用综合板块
        if not enabled and 'all' in categories:
            return {'all': categories['all']}

        return enabled

    def get_scraper_config(self) -> Dict:
        """
        获取抓取器配置

        Returns:
            抓取器配置字典
        """
        scraper_config = self.config.get('scraper', {})

        # 从环境变量覆盖配置
        if os.getenv('HOT_LIST_LIMIT'):
            scraper_config['limit'] = int(os.getenv('HOT_LIST_LIMIT'))

        if os.getenv('REQUEST_TIMEOUT'):
            scraper_config['timeout'] = int(os.getenv('REQUEST_TIMEOUT'))

        return scraper_config

    def get_display_config(self) -> Dict:
        """
        获取显示配置

        Returns:
            显示配置字典
        """
        return self.config.get('display', {})

    def get_all_api_urls(self) -> List[str]:
        """
        获取所有启用数据源的 API URL 列表

        Returns:
            API URL 列表
        """
        urls = []
        for source_name, source_config in self.get_enabled_data_sources().items():
            apis = source_config.get('apis', [])
            for api in apis:
                urls.append(api.get('url'))

        return urls

    def filter_by_category(self, items: List[Dict], category_name: str) -> List[Dict]:
        """
        根据内容板块过滤热榜数据

        Args:
            items: 热榜数据列表
            category_name: 板块名称

        Returns:
            过滤后的热榜数据列表
        """
        categories = self.get_enabled_categories()

        if category_name not in categories:
            logger.warning(f"未找到板块: {category_name}，返回原始数据")
            return items

        category = categories[category_name]
        keywords = category.get('keywords', [])

        # 如果没有关键词，返回所有数据
        if not keywords:
            return items

        # 根据关键词过滤
        filtered = []
        for item in items:
            word = item.get('word', '')
            # 检查是否包含任何关键词
            if any(keyword in word for keyword in keywords):
                filtered.append(item)

        logger.info(f"板块 '{category.get('name')}' 过滤后: {len(filtered)}/{len(items)} 条")
        return filtered

    def get_category_name(self, category_key: str) -> str:
        """
        获取板块显示名称

        Args:
            category_key: 板块键名

        Returns:
            板块显示名称
        """
        categories = self.config.get('content_categories', {})
        return categories.get(category_key, {}).get('name', category_key)

    def get_source_name(self, source_key: str) -> str:
        """
        获取数据源显示名称

        Args:
            source_key: 数据源键名

        Returns:
            数据源显示名称
        """
        sources = self.config.get('data_sources', {})
        return sources.get(source_key, {}).get('name', source_key)


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    loader = ConfigLoader()

    print("启用的数据源:")
    for name, source in loader.get_enabled_data_sources().items():
        print(f"  - {source.get('name')}: {len(source.get('apis', []))} 个 API")

    print("\n启用的内容板块:")
    for name, category in loader.get_enabled_categories().items():
        print(f"  - {category.get('name')}: {len(category.get('keywords', []))} 个关键词")

    print(f"\n所有 API URL ({len(loader.get_all_api_urls())} 个):")
    for url in loader.get_all_api_urls():
        print(f"  - {url}")

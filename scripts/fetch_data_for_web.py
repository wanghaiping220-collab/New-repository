#!/usr/bin/env python3
"""
抓取热榜数据并保存为 JSON 文件，供网页展示使用
"""
import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config_loader import ConfigLoader
from douyin_scraper import DouyinScraper

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("🚀 开始抓取热榜数据（网页版）")
    logger.info("=" * 60)

    try:
        # 加载配置
        config_loader = ConfigLoader()

        # 获取配置的板块（默认使用 'all'）
        category = os.environ.get('CONTENT_CATEGORY', 'all')
        logger.info(f"📂 使用内容板块: {category}")

        # 创建爬虫实例
        scraper = DouyinScraper(config_loader)

        # 抓取热榜数据（默认 20 条）
        hot_list = scraper.fetch_hot_list(limit=20, category=category)

        if not hot_list:
            logger.error("❌ 未能获取热榜数据")
            # 创建空数据文件
            data = {
                "hot_list": [],
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": "数据获取失败",
                "category": category
            }
        else:
            logger.info(f"✅ 成功获取 {len(hot_list)} 条热榜数据")

            # 构建 JSON 数据结构
            data = {
                "hot_list": hot_list,
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": scraper.current_source_name,
                "category": category,
                "is_test_data": scraper.is_using_test_data
            }

            # 打印前 3 条数据预览
            logger.info("📊 数据预览（前3条）:")
            for item in hot_list[:3]:
                logger.info(f"   {item['rank']}. {item['word']} - 热度: {item['hot_value']}")

        # 确保数据目录存在
        data_dir = project_root / 'docs' / 'data'
        data_dir.mkdir(parents=True, exist_ok=True)

        # 保存为 JSON 文件
        output_file = data_dir / 'hot_list.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"💾 数据已保存到: {output_file}")
        logger.info(f"📦 文件大小: {output_file.stat().st_size} 字节")

        logger.info("=" * 60)
        logger.info("✅ 数据抓取完成")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)

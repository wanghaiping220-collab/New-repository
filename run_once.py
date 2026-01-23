"""
抖音热榜抓取并推送到飞书群 - 单次执行版本
用于 GitHub Actions 或其他 CI/CD 环境
"""
import os
import sys
import logging
from datetime import datetime

from douyin_scraper import DouyinScraper
from feishu_notifier import FeishuNotifier
from config_loader import ConfigLoader


def setup_logger():
    """配置日志系统"""
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )


logger = logging.getLogger(__name__)


def main():
    """主函数 - 执行一次抓取和推送"""
    setup_logger()

    logger.info("=" * 60)
    logger.info("🚀 开始执行抖音热榜抓取任务")
    logger.info(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # 获取环境变量
    webhook_url = os.getenv('FEISHU_WEBHOOK_URL')
    if not webhook_url:
        logger.error("❌ 未配置 FEISHU_WEBHOOK_URL 环境变量")
        logger.error("请在 GitHub Secrets 中配置 FEISHU_WEBHOOK_URL")
        sys.exit(1)

    # 获取热榜数量限制（支持从环境变量配置）
    limit = int(os.getenv('HOT_LIST_LIMIT', '20'))

    # 获取启用的板块
    enabled_categories = os.getenv('ENABLED_CATEGORIES', '').strip()
    category = enabled_categories.split(',')[0].strip() if enabled_categories else 'all'

    try:
        # 加载配置
        config_loader = ConfigLoader()

        # 创建抓取器和通知器
        scraper = DouyinScraper(config_loader)
        notifier = FeishuNotifier(webhook_url)

        logger.info(f"📊 开始抓取热榜 (板块: {category}, Top {limit})...")

        # 抓取热榜
        hot_list = scraper.fetch_hot_list(limit=limit, category=category)

        if not hot_list:
            logger.error("❌ 未能获取热榜数据")
            # 发送错误通知
            notifier.send_text_message("⚠️ 抖音热榜抓取失败，请检查服务状态")
            sys.exit(1)

        logger.info(f"✅ 成功抓取 {len(hot_list)} 条热榜数据")

        # 检查是否使用了测试数据
        if scraper.is_using_test_data:
            logger.warning("⚠️  注意：当前使用的是测试数据，抖音 API 可能无法访问")

        # 打印前3条热榜（用于日志查看）
        logger.info("📌 热榜前3名:")
        for item in hot_list[:3]:
            logger.info(f"  {item['rank']}. {item['word']} - 热度: {item['hot_value']}")

        # 发送到飞书
        logger.info("📤 开始发送消息到飞书...")

        # 如果使用测试数据，直接发送文本消息
        if scraper.is_using_test_data:
            text_content = scraper.format_hot_list_text(hot_list, is_test_data=True, category=category)
            success = notifier.send_text_message(text_content)
        else:
            # 优先使用交互式卡片，失败则使用文本消息
            success = notifier.send_interactive_message(hot_list, source_name=scraper.current_source_name)

            if not success:
                logger.warning("⚠️  交互式卡片发送失败，尝试使用文本消息")
                text_content = scraper.format_hot_list_text(hot_list, is_test_data=False, category=category)
                success = notifier.send_text_message(text_content)

        if success:
            logger.info("✅ 消息发送成功")
            logger.info("=" * 60)
            logger.info("🎉 任务执行完成")
            logger.info("=" * 60)
            sys.exit(0)
        else:
            logger.error("❌ 消息发送失败")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ 执行任务时发生错误: {e}", exc_info=True)

        # 尝试发送错误通知到飞书
        try:
            notifier = FeishuNotifier(webhook_url)
            error_msg = f"⚠️ 抓取任务执行失败\n\n错误信息: {str(e)}\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            notifier.send_text_message(error_msg)
        except:
            pass

        sys.exit(1)


if __name__ == "__main__":
    main()

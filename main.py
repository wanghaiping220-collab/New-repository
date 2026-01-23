"""
抖音热榜抓取并推送到飞书群
主程序入口
"""
import os
import time
import logging
import schedule
from datetime import datetime
from dotenv import load_dotenv

from douyin_scraper import DouyinScraper
from feishu_notifier import FeishuNotifier


# 配置日志
def setup_logger():
    """配置日志系统"""
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('douyin_hot_scraper.log', encoding='utf-8')
        ]
    )


logger = logging.getLogger(__name__)


def scrape_and_send():
    """抓取抖音热榜并发送到飞书群"""
    try:
        logger.info("=" * 50)
        logger.info("开始执行热榜抓取任务")

        # 获取环境变量
        webhook_url = os.getenv('FEISHU_WEBHOOK_URL')
        if not webhook_url:
            logger.error("未配置 FEISHU_WEBHOOK_URL，请检查 .env 文件")
            return

        # 创建抓取器和通知器
        scraper = DouyinScraper()
        notifier = FeishuNotifier(webhook_url)

        # 抓取热榜
        hot_list = scraper.fetch_hot_list(limit=20)

        if not hot_list:
            logger.error("未能获取热榜数据")
            # 发送错误通知
            notifier.send_text_message("⚠️ 抖音热榜抓取失败，请检查服务状态")
            return

        # 检查是否使用了测试数据
        if scraper.is_using_test_data:
            logger.warning("⚠️  注意：当前使用的是测试数据，抖音 API 可能无法访问")

        # 发送到飞书
        # 如果使用测试数据，直接发送文本消息
        if scraper.is_using_test_data:
            text_content = scraper.format_hot_list_text(hot_list, is_test_data=True)
            success = notifier.send_text_message(text_content)
        else:
            # 优先使用交互式卡片，失败则使用文本消息
            success = notifier.send_interactive_message(hot_list)

            if not success:
                logger.warning("交互式卡片发送失败，尝试使用文本消息")
                text_content = scraper.format_hot_list_text(hot_list, is_test_data=False)
                success = notifier.send_text_message(text_content)

        if success:
            logger.info("热榜数据发送成功")
        else:
            logger.error("热榜数据发送失败")

        logger.info("热榜抓取任务完成")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"执行任务时发生错误: {e}", exc_info=True)


def main():
    """主函数"""
    # 加载环境变量
    load_dotenv()

    # 配置日志
    setup_logger()

    logger.info("🚀 抖音热榜抓取服务启动")

    # 获取配置
    interval_hours = int(os.getenv('SCRAPE_INTERVAL_HOURS', '1'))
    webhook_url = os.getenv('FEISHU_WEBHOOK_URL')

    # 验证配置
    if not webhook_url:
        logger.error("❌ 未配置 FEISHU_WEBHOOK_URL")
        logger.error("请复制 .env.example 为 .env 并填入你的飞书 Webhook URL")
        return

    logger.info(f"⚙️  配置信息:")
    logger.info(f"   - 抓取间隔: 每 {interval_hours} 小时")
    logger.info(f"   - Webhook: {webhook_url[:50]}...")

    # 立即执行一次
    logger.info("🔄 立即执行首次抓取...")
    scrape_and_send()

    # 设置定时任务
    logger.info(f"⏰ 设置定时任务: 每 {interval_hours} 小时执行一次")
    schedule.every(interval_hours).hours.do(scrape_and_send)

    # 循环执行
    logger.info("✅ 服务运行中，按 Ctrl+C 退出")

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次待执行的任务
    except KeyboardInterrupt:
        logger.info("\n👋 服务已停止")


if __name__ == "__main__":
    main()

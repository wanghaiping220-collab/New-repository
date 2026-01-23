"""
飞书通知模块
"""
import requests
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class FeishuNotifier:
    """飞书消息通知器"""

    def __init__(self, webhook_url: str):
        """
        初始化飞书通知器

        Args:
            webhook_url: 飞书机器人的 Webhook URL
        """
        self.webhook_url = webhook_url
        self.headers = {
            'Content-Type': 'application/json'
        }

    def send_text_message(self, text: str) -> bool:
        """
        发送文本消息到飞书群

        Args:
            text: 要发送的文本内容

        Returns:
            发送是否成功
        """
        try:
            payload = {
                "msg_type": "text",
                "content": {
                    "text": text
                }
            }

            response = requests.post(
                self.webhook_url,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=10
            )
            response.raise_for_status()

            result = response.json()

            if result.get('code') == 0:
                logger.info("飞书消息发送成功")
                return True
            else:
                logger.error(f"飞书消息发送失败: {result.get('msg', '未知错误')}")
                return False

        except requests.RequestException as e:
            logger.error(f"发送请求失败: {e}")
            return False
        except Exception as e:
            logger.error(f"发送消息时发生错误: {e}")
            return False

    def send_post_message(self, title: str, content: str) -> bool:
        """
        发送富文本消息到飞书群

        Args:
            title: 消息标题
            content: 消息内容

        Returns:
            发送是否成功
        """
        try:
            payload = {
                "msg_type": "post",
                "content": {
                    "post": {
                        "zh_cn": {
                            "title": title,
                            "content": [
                                [
                                    {
                                        "tag": "text",
                                        "text": content
                                    }
                                ]
                            ]
                        }
                    }
                }
            }

            response = requests.post(
                self.webhook_url,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=10
            )
            response.raise_for_status()

            result = response.json()

            if result.get('code') == 0:
                logger.info("飞书富文本消息发送成功")
                return True
            else:
                logger.error(f"飞书富文本消息发送失败: {result.get('msg', '未知错误')}")
                return False

        except requests.RequestException as e:
            logger.error(f"发送请求失败: {e}")
            return False
        except Exception as e:
            logger.error(f"发送消息时发生错误: {e}")
            return False

    def send_interactive_message(self, hot_list: list, source_name: str = "热榜") -> bool:
        """
        发送交互式卡片消息到飞书群（更美观的热榜展示）

        Args:
            hot_list: 热榜数据列表
            source_name: 数据源名称

        Returns:
            发送是否成功
        """
        try:
            from datetime import datetime

            # 构建卡片元素
            elements = []

            # 添加时间戳
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "plain_text",
                    "content": f"更新时间: {timestamp}"
                }
            })

            elements.append({
                "tag": "hr"
            })

            # 添加热榜条目
            for item in hot_list[:10]:  # 只展示前10条
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

                # 排名图标
                if rank == 1:
                    icon = "🥇"
                elif rank == 2:
                    icon = "🥈"
                elif rank == 3:
                    icon = "🥉"
                else:
                    icon = f"{rank}."

                label_str = f" [{label}]" if label else ""
                content = f"{icon} {word}{label_str}\n🔥 热度: {hot_str}"

                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "plain_text",
                        "content": content
                    }
                })

                if rank < len(hot_list) and rank < 10:
                    elements.append({
                        "tag": "hr"
                    })

            # 计算实际展示数量
            display_count = min(len(hot_list), 10)

            payload = {
                "msg_type": "interactive",
                "card": {
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "content": f"📊 {source_name} Top{display_count}"
                        },
                        "template": "blue"
                    },
                    "elements": elements
                }
            }

            response = requests.post(
                self.webhook_url,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=10
            )
            response.raise_for_status()

            result = response.json()

            if result.get('code') == 0:
                logger.info("飞书交互式卡片消息发送成功")
                return True
            else:
                logger.error(f"飞书交互式卡片消息发送失败: {result.get('msg', '未知错误')}")
                return False

        except requests.RequestException as e:
            logger.error(f"发送请求失败: {e}")
            return False
        except Exception as e:
            logger.error(f"发送消息时发生错误: {e}")
            return False


if __name__ == "__main__":
    # 测试代码
    import os
    from dotenv import load_dotenv

    load_dotenv()

    webhook_url = os.getenv('FEISHU_WEBHOOK_URL')
    if webhook_url:
        notifier = FeishuNotifier(webhook_url)
        notifier.send_text_message("测试消息：抖音热榜推送服务已启动！")
    else:
        print("请在 .env 文件中配置 FEISHU_WEBHOOK_URL")

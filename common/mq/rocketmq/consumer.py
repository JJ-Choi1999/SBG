# from rocketmq.client import PushConsumer, MessageModel
#
#
# def consume_message():
#     # 创建消费者实例，参数为消费者组名
#     consumer = PushConsumer('example_consumer_group')
#
#     # 设置 Name Server 地址
#     consumer.set_namesrv_addr('localhost:9876')  # 根据实际情况修改
#
#     # 订阅 Topic（可指定 Tag 过滤）
#     consumer.subscribe('ExampleTopic', '*', handle_message)  # '*' 表示所有 Tag
#
#     # 启动消费者
#     consumer.start()
#     print("Consumer started, waiting for messages...")
#
#     # 保持主线程运行，防止程序退出
#     try:
#         while True:
#             pass
#     except KeyboardInterrupt:
#         consumer.shutdown()
#         print("Consumer shutdown.")
#
#
# def handle_message(msg):
#     """消息处理函数"""
#     print(f"Received message: {msg.topic}, {msg.tags}, {msg.keys}, {msg.body.decode('utf-8')}")
#     return True  # 返回 True 表示消费成功
#
#
# if __name__ == '__main__':
#     consume_message()

import time

from rocketmq.client import PushConsumer
from vllm.distributed.device_communicators.custom_all_reduce_utils import consumer


def callback(msg):
    print(msg.id, msg.body)


consumer = PushConsumer('ID-XXX')
consumer.set_namesrv_domain('http://onsaddr-internet.aliyun.com/rocketmq/nsaddr4client-internet')
# For ip and port name server address, use `set_namesrv_addr` method, for example:
consumer.set_namesrv_addr('127.0.0.1:9876')
# consumer.set_session_credentials('XXX', 'XXXX', 'ALIYUN') # No need to call this function if you don't use Aliyun.
consumer.subscribe('YOUR-TOPIC', callback)
consumer.start()

while True:
    time.sleep(3600)

consumer.shutdown()
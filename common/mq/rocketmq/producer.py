# from rocketmq.client import Producer, Message
#
#
# def send_message():
#     # 创建生产者实例，参数为生产者组名
#     producer = Producer('example_producer_group')
#
#     # 设置 Name Server 地址（多个用分号分隔）
#     producer.set_namesrv_addr('localhost:9876')  # 根据实际情况修改
#
#     # 启动生产者
#     producer.start()
#
#     # 创建消息对象，指定 Topic 和 Tag
#     msg = Message('ExampleTopic')
#     msg.set_keys(['key1'])  # 可选：设置消息 Key
#     msg.set_tags('TagA')  # 可选：设置消息 Tag
#     msg.set_body('Hello RocketMQ from Python!'.encode('utf-8'))  # 消息体必须是 bytes
#
#     # 发送消息
#     try:
#         result = producer.send_sync(msg)
#         print(f"Message sent: {result.status} | {result.msg_id}")
#     except Exception as e:
#         print(f"Failed to send message: {e}")
#
#     # 关闭生产者
#     producer.shutdown()
#
#
# if __name__ == '__main__':
#     send_message()

from rocketmq.client import Producer, Message

# producer = Producer('ID-XXX')
# # producer.set_name_server_domain('http://onsaddr-internet.aliyun.com/rocketmq/nsaddr4client-internet')
# # For ip and port name server address, use `set_namesrv_addr` method, for example:
# producer.set_name_server_address('127.0.0.1:9876')
# # producer.set_session_credentials('XXX', 'XXXX', 'ALIYUN') # No need to call this function if you don't use Aliyun.
# producer.start()
#
# msg = Message('YOUR-TOPIC')
# msg.set_keys('XXX')
# msg.set_tags('XXX')
# msg.set_body('XXXX')
# ret = producer.send_sync(msg)
# print(ret.status, ret.msg_id, ret.offset)
# producer.shutdown()
### SBG
> SBG（Standard Builder Graph）标准构建流程图, 通过 config 文件配置实现快速构建 AIAgent 执行流程.
>

---

### 安装
```bash
# 安装项目所需依赖
pip install -r requirements.txt
# 安装 torch 相关依赖用于调用机器学习相关依赖(操作详情: https://pytorch.org/get-started/locally/)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

---

### 已实现功能
#### 代码助手
##### 作用
> 1. 用户输入编码需求，针对用户输入需求，进行需求完善和需求分析
> 2. 针对需求分析内容，生成对应的安装第三方依赖命令、对应代码、预期执行结果
> 3. 执行安装第三方依赖命令和需求对应代码
> 4. 输出执行结果，判断执行结果是否和Agent 生成的预期执行结果一致
>
> 4.1 如果一致，则执行成功
>
> 4.2 否则重试生成流程，直到执行成功或到达最大重试次数终止
>
> 5. 将用户输入、需求分析、生成内容、执行结果发送到邮箱确认
>

##### 生成数据来源
> 1. LLM 模型内置数据
> 2. Weaviate 向量数据库检索
> 3. <font style="color:#080808;background-color:#ffffff;">Tavily </font>Web 搜索引擎搜索
>

##### 依赖项安装与申请
> 1. Web 搜索: 访问 [https://app.tavily.com/home](https://app.tavily.com/home) 申请 <font style="color:#080808;background-color:#ffffff;">tavily_api_key</font>
> 2. <font style="color:#080808;background-color:#ffffff;">Weaviate 向量数据库: 访问 </font>[https://weaviate.io/developers/weaviate](https://weaviate.io/developers/weaviate) 参照说明安装 Weaviate 
> 3. <font style="color:#080808;background-color:#ffffff;">Embedding \ Rerank 模型安装: 访问 </font>[https://inference.readthedocs.io](https://inference.readthedocs.io) 参照 <font style="color:#080808;background-color:#ffffff;">Embedding \ Rerank 模型安装</font>
>

##### <font style="color:#080808;background-color:#ffffff;">配置文件</font>
```yaml
# 基础配置
code_type: python3 # [必填]代码生成器生成的编程语言类型, 多语言输入以下格式: python3/python2/c/c++/java/node.js
install_tool: pip # [必填]编程语言对应第三方依赖安装工具
tavily_api_key:  # [选填] tavily 搜索引擎 openapi key, 开启Web搜索时必填, 申请地址: https://app.tavily.com/home

# weaviate 向量数据库配置, 配置详情: https://weaviate.io/developers/weaviate
vector_store:
  embedding_client: # [必填]xinference 嵌入模型配置, 配置详情: https://inference.readthedocs.io/zh-cn/latest/index.html
    base_url: http://localhost:9997
    model_uid: bge-m3
  rerank_client: # [必填]xinference 嵌入模型配置, 配置详情: https://inference.readthedocs.io/zh-cn/latest/index.html
    base_url: http://localhost:9997
    model_uid: bge-reranker-v2-m3
  port: 8080 # [必填]weaviate http 端口
  grpc_port: 50051 # [必填]weaviate grpc 端口
  additional_config:
    timeout: # [必填]weaviate 超时配置(单位: s)
      init: 30
      query: 60
      insert: 120

# [必填]Agent 客户端配置(使用 openai api请求格式), 请求示例: https://modelscope.cn/models/Qwen/Qwen3-32B
agent_client:
  base_url: https://api-inference.modelscope.cn/v1/
  api_key:
  model: Qwen/Qwen3-32B
  extra_body:   # [选填]模型拓展字段, 可根据对应模型 openai 请求方式所支持的配置方式进行配置, 以下是 qwen3 开启 think 的配置
#    enable_thinking: true
#    thinking_budget: 4096

# 邮件发送配置
send_mail:
  from_mail:  # [必填]发送者邮箱
  to_mail:  # [必填]接收者邮箱
  auth_code:  # [必填]邮箱SMTP授权码, 获取流程(QQ邮箱): 设置 -> 账号与安全 -> 安全设置 -> SMTP服务 -> 生成授权码

# 交互配置
mutual_config:
  enable_mutual: False # 是否开启交互
  prompt:  # [enable_mutual为True时必填]提示词
  global_setting:
    enable_knowledge: False # [enable_mutual为True时必填]是否开启知识库检索
    enable_web: True # [enable_mutual为True时必填]是否开启Web检索
    max_retry: 2 # [enable_mutual为True时必填]代码生成最大重试次数
    project_path:  # [enable_mutual为True时必填]生成代码结果保存目录路径
  data_source:
    workspace: "" # [enable_mutual为True时必填]用于检索的知识库的索引名
    file_paths: []  # [enable_mutual为True时必填]需要上传至向量数据库作为知识库的文件/文件夹地址
```

##### 执行示例
###### 可交互模式

<video controls src="./source/code_helper/enable_mutual.mp4" width="500"></video>

###### 无交互模式

<video controls src="./source/code_helper/unenable_mutual.mp4" width="500"></video>

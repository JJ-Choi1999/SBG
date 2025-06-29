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

<details>
<summary><h3 style="display: inline">已实现功能</h3></summary>

<details style="margin: 15px">
<summary><h4 style="display: inline">1. 代码助手</h4></summary>

##### 作用
> 1. 用户输入编码需求，针对用户输入需求，进行需求完善和需求分析
> 2. 针对需求分析内容，生成对应的安装第三方依赖命令、对应代码、预期执行结果
> 3. 执行安装第三方依赖命令和需求对应代码
> 4. 输出执行结果，判断执行结果是否和Agent 生成的预期执行结果一致
>
>> 4.1 如果一致，则执行成功
>>
>> 4.2 否则重试生成流程，直到执行成功或到达最大重试次数终止
>
> 5. 将用户输入、需求分析、生成内容、执行结果发送到邮箱确认
> 

##### 生成数据来源
> 1. LLM 模型内置数据
> 2. Weaviate 向量数据库检索
> 3. Tavily Web 搜索引擎搜索
>

##### 依赖项安装与申请
> 1. Web 搜索: 访问 [https://app.tavily.com/home](https://app.tavily.com/home) 申请 tavily_api_key
> 2. Weaviate 向量数据库: 访问 [https://weaviate.io/developers/weaviate](https://weaviate.io/developers/weaviate) 参照说明安装 Weaviate 
> 3. Embedding \ Rerank 模型安装: 访问 [https://inference.readthedocs.io](https://inference.readthedocs.io) 参照 Embedding \ Rerank 模型安装
>

##### [配置文件](./configs/code_helper.yaml)
##### [提示词模板](./core/prompts/code_helper.py)
##### [Graph 节点状态](./core/state/code_helper.py)
##### 执行示例
```python
python ./core/graphs/code_helper/compile_graph.py
```

###### 执行步骤
> 1. [初始化代码助手全局配置](./source/code_helper/draw_graph/code_helper/(step1)init_graph.png)
> 2. [执行代码助手具体流程](./source/code_helper/draw_graph/code_helper/(step2)exec_graph(new).png)
> 3. [代码助手执行完成后结果处理](./source/code_helper/draw_graph/code_helper/(step3)end_graph.png)
>

###### 可交互模式
> 1. [执行录屏](./source/code_helper/enable_mutual.mp4)
> 2. [执行结果](./source/code_helper/enable_mutual.png)
>

###### 无交互模式
> 1. [执行录屏](./source/code_helper/unenable_mutual.mp4)
> 2. [执行结果](./source/code_helper/unenable_mutual.png)
>
</details>

</details>

---

<details>

<summary><h3 style="display: inline">Feature</h3></summary>

- [x] Agent 处理文本中包含本地文件地址字符串，识别和读取
- [x] Agent 对多模态的支持
- [x] Agent 处理文本中的本地\网络图片，上传图像多模态对话
- [ ] 封装OCR\YOLO\SAM 等小模型
- [ ] Agent 对话持久化
- [ ] Agent 能力API 发表
- [ ] Agent Nacos 配置发布和注册
- [ ] MCP\A2A 能力抽象和封装
- [ ] 历史对话流 QA 格式格式化输出
- [ ] 模型微调\量化脚本能力发布
- [ ] 模型微调\量化后导入对应测试数据后，不同尺寸的模型执行结果聚合
- [ ] 依据模型微调\量化不同尺寸对不同数据集的输出结果，设置自动化流程
- [ ] 封装 Android/IOS/Web/Windows/Macos/HarmonyOS 自动化能力
- [ ] 封装代理爬虫搜索 Web 聚合接口
- [ ] 抽象封装风险词识别\替换工具

</details>
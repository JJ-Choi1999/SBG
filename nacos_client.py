
```python
import yaml
import os
import requests

class NacosClient:
    def __init__(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        agent_config = self.config['agent_client']
        self.base_url = agent_config['base_url']
        self.api_key = agent_config['api_key']
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

    def create_config(self, namespace_id, data_id, group, content):
        url = f"{self.base_url}/nacos/v1/cs/configs"
        params = {
            'namespaceId': namespace_id,
            'dataId': data_id,
            'group': group,
            'content': content
        }
        try:
            response = requests.post(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"

    def retrieve_config(self, data_id, group):
        url = f"{self.base_url}/nacos/v1/cs/configs"
        params = {
            'dataId': data_id,
            'group': group
        }
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"

    def update_config(self, namespace_id, data_id, group, content):
        url = f"{self.base_url}/nacos/v1/cs/configs"
        params = {
            'namespaceId': namespace_id,
            'dataId': data_id,
            'group': group,
            'content': content
        }
        try:
            response = requests.put(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"

    def delete_config(self, data_id, group):
        url = f"{self.base_url}/nacos/v1/cs/configs"
        params = {
            'dataId': data_id,
            'group': group
        }
        try:
            response = requests.delete(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"
```

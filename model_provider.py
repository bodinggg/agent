
import os
import dashscope
import json
from dashscope.api_entities.dashscope_response import Message
from prompt import user_prompt
from dotenv import load_dotenv  # 加载当前目录下的.env文件

load_dotenv()




class ModelProvider(object):
    def __init__(self):
        self.api_key = os.environ.get("DASHSCOPE_API_KEY")
        self.model_name = os.environ.get("MODEL_NAME")
        self._client = dashscope.Generation()



        self.max_retry_time = 3

    def chat(self, prompt, chat_history):
        cur_retry_time = 0
        while cur_retry_time < self.max_retry_time:
            cur_retry_time += 1
            try:
                messages = [Message(role='system',content=prompt)]
                for his in chat_history:
                    messages.append(Message(role='user', content=his[0]))
                    messages.append(Message(role='assistant', content=his[1]))
                messages.append(Message(role='user', content=user_prompt))
                # 返回结果
                response = self._client.call(
                    model = self.model_name,
                    api_key = self.api_key,
                    messages = messages
                )
                # 解析
                """
                {"id":"chatcmpl-947fcf5e-8434-9695-b232-b61cc2160849",
                "choices":[{"finish_reason":"stop",
                    "index":0,
                    "logprobs":null,
                    "message":{"content":"我是来自阿里云的超大规模语言模型，我叫通义千问。",
                        "refusal":null,
                        "role":"assistant",
                        "audio":null,
                        "function_call":null,
                        "tool_calls":null
                    }
                }],
                "created":1740322202,
                "model":"qwen-plus",
                "object":"chat.completion",
                "service_tier":null,
                "system_fingerprint":null,
                "usage":{"completion_tokens":17,
                        "prompt_tokens":22,
                        "total_tokens":39,
                        "completion_tokens_details":null,
                        "prompt_tokens_details":{"audio_tokens":null,
                                                "cached_tokens":0}
                        }
                }
                """
                print('response', response)
                content = json.loads(response['output']['text'])
                return content
            except Exception as err:
                print(f'调用大模型出错：{err}')
            return {}

import time 
from tools import tools_map
from prompt import gen_prompt, user_prompt
from model_provider import ModelProvider

from streamlit import st
# Agent 入口
"""
todo:
    1.环境变量的设置
    2.工具的引入
    3.prompt模板
    4.模型的初始化
"""

mp = ModelProvider()


def parse_thoughts(response):
    """
        response:
        {
            "action":{
                "name":"action name"
                "args":{
                    "args name":"args value"
                }
            },
            "thoughts":
            {
                "text":"thought",
                "plan":"plan",
                "criticism":"criticism",
                "speak":"speak"
                "reasoning":""
            }
        }
    """
    try:
        thoughts = response.get('thoughts')
        observation = thoughts.get("speak")
        plan = thoughts.get("plan")
        reasoning = thoughts.get("reasoning")
        criticism = thoughts.get("criticism")
        prompt = "plan: {plan}\nreasoning:{reasoning}\ncriticsim:{criticism}\nobservation:{observation}"
        return prompt
    except Exception as err:
        print(f'parse thoughts err:{err}')
        return "".format(err)


def agent_excute(query, max_request_time=10):
    cur_request_time = 0
    chat_history = []   # 大工程需要时间戳
    # 信息记录下来
    agent_scratch = ''

    while cur_request_time < max_request_time:
        cur_request_time += 1
        # 如果返回结果达到预期，则直接返回
        """
        prompt包含的功能：
            1. 任务描述
            2. 工具描述
            3. 用户的输入 user_msg
            4. assistant_msg
            5. 限制
            6. 给出更好描述
        """
        prompt = gen_prompt(query, agent_scratch)
        start_time = time.time()
        print(f"*****************************{cur_request_time}，开始调用大模型")
        # call llm
        """
        sys_prompt:
        user_msg, assistant, history
        """
        response = mp.chat(prompt, chat_history)

        end_time = time.time()
        print(f"*****************************{cur_request_time}，调用大模型结束，耗时{end_time-start_time}")

        if not response or not isinstance(response, dict):
            print("调用大模型错误，即将重试....")
            continue

        """
        response:
        {
            "action":{
                "name":"action name"
                "args":{
                    "args name":"args value"
                }
            },
            "thoughts":
            {
                "text":"thought",
                "plan":"plan",
                "criticism":"criticism",
                "speak":"speak"
                "reasoning":""
            }
        }
        """
        action_info = response.get("action")
        action_name = action_info.get('name')
        action_args = action_info.get('args')
        print(f"当前action name:",action_name, action_args)
        if action_name == "finish":
            final_answer = action_args.get("answer")
            print(f"final_answer is {final_answer}")
            break

        observation = response.get("thoughts").get("speak")

        try:
            # {action_name: func}   (map映射)
            # todo: tools_map的实现
            func = tools_map.get(action_name)
            observation = func(**action_args)

        except Exception as err:
            print("调用工具异常",err)

        agent_scratch = agent_scratch + "\n" + observation
        

        user_msg = "决定使用哪个工具"
        assistant_msg = parse_thoughts(response)

        chat_history.append([user_msg, assistant_msg])

def main():
    # 需求：支持用户多次交互
    # 设置最大调用次数
    max_request_time = 10
    while True:
        query = input("请输入您的目标：")
        if query == "exit":
            return
        agent_excute(query)

if __name__ == "__main__":
    main()
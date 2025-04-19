import streamlit as st
import sys
from io import StringIO
import time
from tools import tools_map
from prompt import gen_prompt, user_prompt
from model_provider import ModelProvider


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
    st.title("代理系统控制台")
    
    # 初始化会话状态
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'processing' not in st.session_state:
        st.session_state.processing = False

    # 输入区域 - 使用表单防止重复提交
    with st.form("query_form"):
        user_input = st.text_input("请输入任务目标：", key="user_input")
        submitted = st.form_submit_button("执行")
    
    if submitted and user_input:
        if user_input.lower() == 'exit':
            st.session_state.query_history = []
            st.rerun()
        
        # 锁定状态
        st.session_state.processing = True
        
        # 创建输出捕获器
        output_capture = StringIO()
        sys.stdout = output_capture
        
        try:
            # 执行原有逻辑
            agent_excute(user_input)
            
            # 获取执行日志
            log_output = output_capture.getvalue()
            st.session_state.query_history.append({
                "query": user_input,
                "log": log_output,
                "timestamp": time.time()
            })
        finally:
            sys.stdout = sys.__stdout__
            st.session_state.processing = False
            st.rerun()

    # 显示历史记录
    if st.session_state.query_history:
        st.subheader("执行记录")
        for record in st.session_state.query_history[-3:]:  # 显示最近3条
            with st.expander(f"任务：{record['query']} ({time.ctime(record['timestamp'])})"):
                st.code(record['log'])

    # 显示状态指示器
    if st.session_state.processing:
        st.warning("正在执行任务，请勿重复提交...")
        st.progress(70)  # 模拟进度

if __name__ == "__main__":
    main()
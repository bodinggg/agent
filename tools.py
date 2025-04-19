
import os
import json
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv  # 加载当前目录下的.env文件
load_dotenv()


"""
1.写文件
2.读文件
3.追加
4.网络搜索
"""

def _get_workdir_root():
    workdir_root = os.environ.get("WORKDIR_ROOT",'./data/llm_result')
    return workdir_root

WORKDIR_ROOT = _get_workdir_root()

def read_file(filename):
    filename = os.path.join(WORKDIR_ROOT, filename)
    if not os.path.exists(filename):
        return f"{filename} not exist, please check fie exist before read"

    with open(filename, 'r') as f:
        return "\n".join(f.readlines())

def append_to_file(filename, content):
    filename = os.path.join(WORKDIR_ROOT, filename)
    if not os.path.exists(filename):
        return f"{filename} not exist, please check fie exist before read"
    
    with open(filename, 's') as f:
        f.write(content)
    return 'append content to file success' # 操作成功

def write_to_file(filename, content):
    filename = os.path.join(WORKDIR_ROOT, filename)
    if not os.path.exists(WORKDIR_ROOT):
        os.makedirs(WORKDIR_ROOT)

    with open(filename, 'w') as f:
        f.write(content)
    return 'write content to file success' 

def search(query):
    tavily = TavilySearchResults(max_results=5)

    try:
        ret = tavily.invoke(input = query)
        
        """
        ret:
        [{
            "content":"",
            "url":
        }
        ]
        """
        content_list = [obj['content'] for obj in ret]
        return "\n".join(content_list)
    except Exception as err:
        return "search err:{}".format(err)

tools_info = [
    {
        "name":"read_file",
        "description":"read file from agent generate, should write file before read",
        "args":[{
            "name":"filename",
            "type":"string",
            "description":"read file name"
        }] 
    },
    {
        "name":"append_to_file",
        "description":"append llm content to file, should write file before read",
        "args":[{
            "name":"filename",
            "type":"string",
            "description":"file name"
        },{
            "name":"content",
            "type":"string",
            "description":"append to file content"
        }]
    },
    {
        "name":"write_to_file",
        "description":"write llm content to file",
        "args":[{
            "name":"filename",
            "type":"string",
            "description":"file name"
        },{
            "name":"content",
            "type":"string",
            "description":"write to file content"
        }]
    },
    {
        "name":"search",
        "description":"this is a search engine, you can gain additional knowledge though this search when you are unsure of what large model return",
        "args":[{
            "name":"query",
            "type":"string",
            "description":"search query to look up"
        }]
    }
]

tools_map = {
    "read_file":read_file,  # 不带括号，直接使用这个函数
    "append_to_file":append_to_file,
    "write_to_file":write_to_file,
    "search":search
}

def gen_tools_desc():
    tools_desc = []
    for idx, t in enumerate(tools_info):
        args_desc = []
        for info in t['args']:
            args_desc.append({
                "name":info['name'],
                "description":info['description'],
                "type":info['type']
            })
        args_desc = json.dumps(args_desc, ensure_ascii=False)
        tool_desc = f"{idx + 1}, {t['name']}:{t['description']}, args: {args_desc}"
        tools_desc.append(tool_desc)
    tools_prompt = '\n'.join(tools_desc)
    return tools_prompt
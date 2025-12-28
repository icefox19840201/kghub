from langchain_classic.agents import AgentType
from langchain_classic.chains.sql_database.query import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit,create_sql_agent
from langgraph.graph import StateGraph,START,END
from typing import Dict,List,Optional
from langchain_core.prompts import PromptTemplate
from typing_extensions import TypedDict
import re
import settings
from core.biziness.llmbase import getllm
#------------------------------全局设置----------------------------------
mysql_db_uri=settings.db['mysql']
db=SQLDatabase.from_uri(mysql_db_uri)
llm=getllm()
#------------------------------提取查询关键词中的返回数量------------------------------------
def extract_top_k_from_query(query: str) -> int:
    """从用户查询中提取top_k值，默认为5"""
    # 转换为小写便于匹配
    query_lower = query.lower()

    # 匹配"前N"、"top N"、"前N个"等模式
    patterns = [
        r'前\s*(\d+)\s*个',
        r'top\s*(\d+)',
        r'前\s*(\d+)',
        r'(\d+)\s*个',
        r'(\d+)\s*条'
    ]

    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            try:
                top_k = int(match.group(1))
                # 限制范围在1-50之间
                return max(1, min(top_k, 50))
            except ValueError:
                continue

    # 默认返回5
    return 5
#-------------------------------定义变量---------------------------------
query_top_k=5   #定义查询结果数量
#------------------------------模板定义----------------------------------
sql_template='''
你是专业的MySQL SQL生成专家
你的责职如下：
   1:仅生成查询SQL语句，无额外解释；
   2：表结构：{table_info}
   3：严禁生成任何可以影响数据库数据内容或结构的sql
   4：最多返回{top_k}条记录
   用户需求：{input}
'''
sql_agent_template='''
你是一个SQL执行和校准专家。
你的任务是：
    1. 检查SQL语法是否正确
    2. 执行SQL查询并返回结果
    3. 如果SQL有误，先尝试修正再执行
    4. 返回清晰、准确的查询结果
    5. 返回清晰的查询结果，查询的结果用markdown格式返回
    6.对查询结果进行总结描述
注意：
    - 只执行SELECT查询，拒绝其他类型的SQL
    - 如果查询结果为空，请明确说明"未查询到符合条件的数据"
    - 返回结果要简洁明了
'''
#-----------------------------定义查询链生成sql-----------------------------------
sql_prompt=PromptTemplate(
    input_variables=['input','table_info','top_k'],
    template=sql_template,
)
sql_query_chain=create_sql_query_chain(llm=llm,db=db,prompt=sql_prompt,k=query_top_k)
#----------------------------定义sqlagent负责校验执行-------------------------------------------
#Sql Toolkit +Agent (校验执行Sql)
toolkit=SQLDatabaseToolkit(db=db,llm=llm)
sql_exec_agent=create_sql_agent(llm=llm,
                                toolkit=toolkit,
                                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                                verbose=False,
                                handle_parsing_errors=True,
                                max_iterations=5, #增加迭代次数，允许sqlagent修正sql
                                return_intermediate_steps=True,
                                #添加提示词
                                prefix=sql_agent_template
 )
#----------------------------定义状态图-----------------------------------------------------
class GraphState(TypedDict):
    user_query:str  #用户查询的问题
    generated_sql: Optional[str]  # query生成的SQL
    sql_validation: bool  # SQL语法是否有效
    sql_error: Optional[str]  # SQL相关错误信息
    exec_result: Optional[Dict]  # Agent执行结果
    formatted_result: Optional[str]  # 格式化后的最终结果
    retry_count: int  # 重试次数
    streaming_queue: List[str]  # 流式消息队列
    streaming_progress: str  # 当前流式进度消息
#----------------------------图节点处理--------------------------------------------------
async  def generate_sql_node(state:GraphState):
    '''
    生成sql
    :param state:
    :return:
    '''

    # 添加第一个进度信息
    state["streaming_progress"] = "🔄 正在分析用户需求,生成相应的Sql查询..."
    state["streaming_queue"].append(state["streaming_progress"])
    yield state
    #生成 sql
    top_k = extract_top_k_from_query(state["user_query"])
    global query_top_k
    query_top_k=top_k
    sql=sql_query_chain.invoke({
        'question':state['user_query'],
            "table_info": db.get_table_info(),
            "top_k": top_k
    })
    generated_sql=sql.strip()
    state["streaming_progress"] = "✅ SQL生成完成"
    state["streaming_queue"].append(state["streaming_progress"])
    state["generated_sql"] = generated_sql
    state["sql_validation"] = True
    state["sql_error"] = None
    yield state

async def validate_sql_node(state:GraphState):
    '''
    校验sql的合法性
    :param state:
    :return:
    '''
    if not state.get('generated_sql'):
        state["streaming_progress"] = "❌ SQL未生成或生成失败"
        state["sql_validation"] = False
        state["streaming_queue"].append(state["streaming_progress"])
        yield state
        return
    state['streaming_progress']='正在校验sql语句的合规性'
    sql=state['generated_sql'].upper().strip()
    dangerous_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER']
    for keyword in dangerous_keywords:
        if keyword in sql:
            state["streaming_progress"] = f"❌ SQL包含危险操作：{keyword}"
            state["streaming_queue"].append(state["streaming_progress"])
            state["sql_validation"] = False
            state["sql_error"] = f"SQL包含危险操作：{keyword}"
            yield state
            return
    # 如果sql_validation尚未被设置为False（即没有危险操作），则校验通过
    # 只有在校验状态不是True时才设置为通过，避免重复设置
    if state['sql_validation'] != True:
        state["streaming_progress"] = "✅ SQL语法校验通过"
        state["sql_validation"] = True
        state["streaming_queue"].append(state["streaming_progress"])
        yield state
async def execute_sql_node(state:GraphState):
    '''
    执行sql
    :param state:
    :return:
    '''
    if state["sql_validation"] == False:
        state["streaming_progress"] = '❌ SQL未通过校验，跳过执行'
        state["streaming_queue"].append(state["streaming_progress"])
        yield state
        state["exec_result"] = None
        yield state
        return
    state["streaming_progress"] = '🚀 正在执行SQL查询...'
    state["streaming_queue"].append(state["streaming_progress"])
    yield state
    state["streaming_progress"] = "🚀 正在执行SQL查询..."
    yield state
    # 使用Agent执行SQL，让Agent进行校准和结果解析
    sql_with_context = f"""
            请检查执行以下SQL查询并返回结果：
            SQL: {state['generated_sql']}
            用户需求：{state['user_query']}
            表结构：{db.get_table_info()}
            要求：
            1：分析sql查询是否满足查询要求,如果不能满足查询需求，请修正 SQL
            2. 先检查SQL语法是否正确
            3 检查sql查询是否包含危险操作，如果包含，请拒绝执行
            4.执行查询并获取结果
            5. 如果查询有误，请修正后重新执行
            """
    exec_result=sql_exec_agent.invoke({'input':sql_with_context})
    # 提取Agent的输出结果
    if isinstance(exec_result, dict):
        output = exec_result.get("output", "")
        intermediate_steps = exec_result.get("intermediate_steps", [])
    else:
        output = str(exec_result)
        intermediate_steps = []
    if not output or output.strip() == "":
        output = "未查询到符合条件的数据"
    state["streaming_progress"] = "✅ SQL查询完成"
    state["streaming_queue"].append(state["streaming_progress"])
    state["exec_result"] = {
        "raw_output": output,
        "intermediate": intermediate_steps
    }
    state['sql_error']=None
    yield state
async def format_result_node(state:GraphState):
    '''
    格式化结果
    :param state:
    :return:
    '''
    if not state["exec_result"] or state["exec_result"].get("raw_output") is None:
        error_msg = state.get('sql_error', '未知错误')
        state["streaming_progress"] = f"❌ 查询失败：{error_msg}"
        state["formatted_result"] = f"查询失败：{error_msg}"
        state["streaming_queue"].append(state["streaming_progress"])
        yield state
        return
        
    state["streaming_progress"] = "🎨 正在格式化查询结果..."
    state["streaming_queue"].append(state["streaming_progress"])
    yield state

    # 提取Agent的执行结果
    raw_output = state["exec_result"]["raw_output"]
    intermediate_steps = state["exec_result"]["intermediate"]

    # 分析Agent的响应，提取有用的信息
    if not raw_output or raw_output.strip() == "":
        result_text = "未查询到符合条件的数据"
    elif "error" in raw_output.lower():
        result_text = f"查询出现错误：{raw_output}"
    else:
        # 清理和格式化Agent的输出
        result_text = raw_output.strip()

    # 构建最终回复，包含SQL和结果
    formatted = f"""### 🎯 查询结果
                    {result_text}
                """

    state["streaming_progress"] = "✅ 结果格式化完成"
    state["formatted_result"] = formatted
    state["streaming_queue"].append(state["streaming_progress"])
    yield state

async def retry_generate_sql_node(state:GraphState):
    '''
    重试生成sql
    :param state:
    :return:
    '''
    state["streaming_progress"] = f"🔄 第{state['retry_count'] + 1}次重试生成SQL..."
    state["streaming_queue"].append(state["streaming_progress"])
    state["retry_count"] = state["retry_count"] + 1
    state["generated_sql"] = None  # 清空原有SQL
    state["sql_validation"] = False
    yield state
#----------------------------定义动态路由-----------------------------------------
async def sql_validate_route(state:GraphState):
    '''
    定义动态路由
    :param state:
    :return:
    '''
    if state['sql_validation']==True:
        return 'execute_sql'
    elif state['retry_count']<=2:
        return 'retry_generate_sql'
    return 'format_result'
#----------------------------定义工作流-----------------------------------------------------
async def workflow():
    graph=StateGraph(GraphState)
    #添加处理节点
    graph.add_node('generate_sql',generate_sql_node)
    graph.add_node('validate_sql',validate_sql_node)
    graph.add_node('retry_generate_sql',retry_generate_sql_node)
    graph.add_node('execute_sql',execute_sql_node)
    graph.add_node('format_result',format_result_node)

    #添加边
    graph.add_edge(START,'generate_sql')

    # #生成sql->检验sql
    graph.add_edge('generate_sql','validate_sql')
    # #动态路由，根据校验的结果进行下一步动作的判断,(执行，重试，结束)
    graph.add_conditional_edges('validate_sql',sql_validate_route,{'execute_sql':'execute_sql',
                                                                   'retry_generate_sql':'retry_generate_sql',
                                                                   'format_result':'format_result'})
    # #重试->>生成sql
    graph.add_edge('retry_generate_sql','generate_sql')
    # #执行sql->格式化结果
    graph.add_edge('execute_sql','format_result')
    # #格式化结果->结束
    graph.add_edge('format_result',END)
    return graph.compile()
#----------------------------查询接口------------------------------------------------
async  def stream_sql_query(user_query):
    '''
    调用工作流进行查询处理
    :return:
    '''
    # user_query='查询市盈率（TTM）大于 30 的股票名称、市盈率、持仓机构名称、持仓占比及持仓成本，按市盈率降序排序。查找前20条数据'
    yield f'开始处理,用户问题：{user_query}\n'
    yield '-'*50+'\n'
    sqlflag=False
    graph_agent=await workflow()
    yield "工作流已编译完成，开始流程任务\n"
    
    #初始状态
    current_state = {
        "user_query": user_query,
        "generated_sql": None,
        "sql_validation": None,
        "sql_error": None,
        "exec_result": None,
        "formatted_result": None,
        "retry_count": 0,
        "streaming_queue": [],
        "streaming_progress": ""
    }
    
    # 用于跟踪已经输出过的消息，防止重复输出
    previous_progress = set()
    
    # 处理工作流的流式输出
    yield "开始执行工作流...\n"
    try:
        async for state in graph_agent.astream(current_state, stream_mode="updates"):
            for node_name, node_states in state.items():
                if isinstance(node_states, dict) and node_states.get("streaming_progress"):
                    if  node_states.get("streaming_queue"):
                        all_node_state=node_states.get("streaming_queue")
                        for item_node_state in all_node_state:
                            # 只输出之前没有输出过的消息
                            if item_node_state not in previous_progress:
                                yield item_node_state
                                previous_progress.add(item_node_state)
                if sqlflag==False:
                    if isinstance(node_states, dict):
                        if node_states.get('generated_sql'):
                            yield f"首次生成的SQL: {node_states.get('generated_sql')}\n"
                            sqlflag=True
            # 获取格式化结果
            format_result = None
            if 'format_result' in state:
                format_result = state['format_result'].get('formatted_result')
            elif 'formatted_result' in state:
                format_result = state.get('formatted_result')
                
            if format_result:
                yield f"{format_result}\n"
        yield "工作流执行完成。\n"
    except Exception as e:
        import traceback
        msg=traceback.format_exc()
        yield f"工作流执行出错: {msg}\n"

# async def main():
#     async for chunk in stream_sql_query():
#         print(chunk)
# if __name__ == '__main__':
#     asyncio.run(main())
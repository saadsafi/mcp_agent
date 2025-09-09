from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.sessions import Connection
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import ToolMessage, ToolCall, AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
#from langgraph.graph.graph import CompiledGraph
from langgraph.graph.state import CompiledStateGraph
import asyncio
import yaml
import sys
from pathlib import Path
from timing import timeit
from prompts import MyPrompts
from rich import print as rprint


OUTPUT_WRITE_FLAG = "w"



def get_connections(yaml_file, requested_servers) -> dict[str, Connection]:
    conf = yaml.safe_load(Path(yaml_file).read_text())
    servers = conf['mcp']['servers']
    filtered_servers = {k:v for k,v in servers.items() if k in requested_servers}
    # Each server must include 'transport' with one of: 'stdio', 'sse', 'websocket', 'streamable_http'.
    for (key, values) in filtered_servers.items():
        if 'transport' not in values:
            values['transport'] = 'stdio'
        else:
            if values['transport'] == 'http':
                values['transport'] = 'streamable_http'
                print('fast-agent uses http, not streamable_http yet')
    if filtered_servers:
        rprint(f"\n:desktop_computer:  [bold yellow]Available MCP Servers: {list(filtered_servers.keys())}[/bold yellow]")
    return filtered_servers


def content_without_think(msg, printing=True) -> str:
    splitter = "</think>"
    if splitter in msg.content:
        content = "/think " + str(msg.content.split(splitter)[-1])
    else:
        content = "/no_think " + str(msg.content)
    if printing:
        rprint(f":thinking_face: {content}")
    return content


@timeit
async def invoke_agent(graph: CompiledStateGraph, query):
    global OUTPUT_WRITE_FLAG
    #print(f"{type(agent)=}")

    #print("\n"+query)
    # the "configurable" param is associated with the context. we're using checkpointer, or memory.
    # The agent remembers the previous turn and can use that context for the next interaction.
    # here we used InMemorySaver, which stores the agent's state in memory.
    # For persistent storage, consider using RedisSaver or other checkpointers.
    # hash('foo') remain constant within an individual Python process, but, as a security measure, not predictable between repeated invocations of Python.
    # if using database, one can use hashlib.sha256(b'foo').hexdigest()
    config = {"configurable": {"thread_id": hash(query)},
              "recursion_limit": 30,  # default 25 https://langchain-ai.github.io/langgraph/troubleshooting/errors/GRAPH_RECURSION_LIMIT/#troubleshooting
              }

    # {"role": "user", "content": query}, # openai throw error about lack of context history
    res = await graph.ainvoke({"messages": query},
                              config=config) # type: ignore

    with open("../data/output.md", OUTPUT_WRITE_FLAG) as res_file: # , newline='\r\n'
        for msg in res['messages']:
            if isinstance(msg, AIMessage):
                if msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        tc: ToolCall = tool_call
                        tool_details = "\n" + str(tc['args']['code'] if 'code' in tc['args'] else tc['args'])
                        print("### Tool:", tc['name'], tool_details, file=res_file)
                        rprint(f":toolbox: [bold blue]Tool: {tc['name']} {tool_details}[/bold blue]")
                else:
                    print("### AIMessage without 'tool_calls':", content_without_think(msg) + "\n", file=res_file)
            elif isinstance(msg, ToolMessage):
                print("### ToolMessage:", str(msg.content) + "\n", file=res_file)
                rprint(f":toolbox: [bold blue]ToolMessage: {str(msg.content)}[/bold blue]\n")
            else:
                rprint(f":question: {msg.content}")

    with open("../data/output_raw.txt", OUTPUT_WRITE_FLAG) as res_file:
        print(str(res), file=res_file)
        #rprint(str(res)) the full json response

    OUTPUT_WRITE_FLAG = "a"

prompts = {
    "get_time": MyPrompts.get_prompts(['time']),
    "calculator": MyPrompts.get_prompts(['calc']),
    "interpreter": MyPrompts.get_prompts(['code']),
    "dbhub-postgres-docker": MyPrompts.get_prompts(['sql'])
}


@timeit
async def main():
    yaml_cfg = './fastagent.config.yaml'
    mcp_servers = {'calc': 'calculator',
                   'time': 'get_time',
                   'sql': 'dbhub-postgres-docker',
                   'code': 'interpreter',
                  }
    args = sys.argv[1:]
    if not args:
        args = list(mcp_servers.keys())

    required_servers = { k:mcp_servers[k] for k in args if k in mcp_servers }
    connections = get_connections(yaml_cfg, list(required_servers.values()))

    client = MultiServerMCPClient(connections)
    # this will start a new MCP ClientSession for each tool invocation.
    # instead we will (in for loop below) explicitly start a session for each server.
    #tools = await client.get_tools()

    for key in required_servers:
        prompts = MyPrompts.get_prompts([key])
        if not prompts:
            continue
        srv = required_servers[key]
        rprint(f"\n:desktop_computer:  [bold yellow]Running MCP Server: {srv}[/bold yellow]")
        async with client.session(srv) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            memory = InMemorySaver()
            graph = create_react_agent("openai:gpt-4o-mini", 
                                    tools, 
                                    #prompt=system_prompt,
                                    checkpointer=memory
                                    )

            for prompt in prompts:
                #rprint(f"{key}: {prompt[0]}")
                await invoke_agent(graph, prompt[1])



if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import sys
from mcp_agent.core.fastagent import FastAgent
from mcp_agent.core.request_params import RequestParams
from timing import timeit
from prompts import MyPrompts


# Create the application
fast = FastAgent("fast-agent app", quiet=False)



@timeit
async def run_prompt(agent, prompt):
    await agent( prompt )


# Define the agent
@fast.agent(name="agent_test_mcps",
            instruction="You are a helpful AI Agent.",
            servers=["calculator",
                     "get_time",
                     "dbhub-postgres-docker",
                     "interpreter",
                     #"prompts",
                     ],
            request_params=RequestParams(  # https://fast-agent.ai/agents/defining/#available-requestparams-fields
                maxTokens=8192,
                temperature=0.6,
                max_iterations=5,
                use_history=True,
            )
        )
@timeit
async def main():
    async with fast.run() as agent:
        #await agent.interactive()
        #mcps = await agent["agent_test_mcps"].list_mcp_tools()
        #print(mcps.keys())

        args = sys.argv[1:]
        prompts = MyPrompts.get_prompts(args)
        for prompt in prompts:
            print(prompt[0])
            await run_prompt(agent, prompt[1])

if __name__ == "__main__":
    asyncio.run(main()) # type: ignore


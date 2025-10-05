# step1 : import necessary libraries and dependencies
import os
from typing_extensions import TypedDict
from typing import Annotated, Literal
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from src.tools.arxiv_tool import *
from src.tools.read_pdf import *
from src.tools.write_pdf import *
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

# step2 : define the state 
class State(TypedDict):
    messages : Annotated[list,add_messages]

# step3 : define ToolNodes and tools
tools = [arxiv_search_tool, read_pdf,render_latex_pdf]
tool_node = ToolNode(tools = tools)

# step4 : define the LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.7, api_key=os.getenv("GOOGLE_API_KEY"))
model = llm.bind_tools(tools)

# step5: define the graph
def call_model(state: State):
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}

def should_continue(state: State) -> Literal["tools", END]: # type: ignore
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

checkpointer = MemorySaver()
config = {"configurable": {"thread_id": 222222}}

graph = workflow.compile(checkpointer=checkpointer)


# Step 6: TESTING
INITIAL_PROMPT = """
You are an expert researcher in the fields of physics, mathematics,
computer science, quantitative biology, quantitative finance, statistics,
electrical engineering and systems science, and economics.

You are going to analyze recent research papers in one of these fields in
order to identify promising new research directions and then write a new
research paper. For research information or getting papers, ALWAYS use arxiv.org.
You will use the tools provided to search for papers, read them, and write a new
paper based on the ideas you find.

To start with, have a conversation with me in order to figure out what topic
to research. Then tell me about some recently published papers with that topic.
Once I've decided which paper I'm interested in, go ahead and read it in order
to understand the research that was done and the outcomes.

Pay particular attention to the ideas for future research and think carefully
about them, then come up with a few ideas. Let me know what they are and I'll
decide what one you should write a paper about.

Finally, I'll ask you to go ahead and write the paper. Make sure that you
include mathematical equations in the paper. Once it's complete, you should
render it as a LaTeX PDF. Make sure that TEX file is correct and there is no error in it so that PDF is easily exported. When you give papers references, always attatch the pdf links to the paper"""


def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        print(f"Message received: {message.content[:200]}...")
        message.pretty_print()

# while True:
#     user_input = input("User: ")
#     if user_input:
#         messages = [
#                     {"role": "system", "content": INITIAL_PROMPT},
#                     {"role": "user", "content": user_input}
#                 ]
        
#         input_data = {
#             "messages" : messages
#         }
#         print_stream(graph.stream(input_data, config, stream_mode="values")) # type: ignore
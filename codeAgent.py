import uuid
import asyncio

from typing import Annotated
from langchain_core.messages import SystemMessage
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from typing import List, Any, Dict
from codeAgent_tools import python_sandbox
from datetime import datetime

load_dotenv(override=True)

# Define State
class State(TypedDict):
    messages: Annotated[List[Any], add_messages]

class CodeAgent:
    def __init__(self):
        self.coder_llm_with_tools = None
        self.tools = None
        self.llm_with_tools = None
        self.graph = None
        self.codeAgent_id = str(uuid.uuid4())
        self.memory = MemorySaver()

    async def setup(self):
        self.tools = [python_sandbox]
        coder_llm = ChatOpenAI(model="gpt-4o-mini")
        self.coder_llm_with_tools = coder_llm.bind_tools(self.tools)
        await self.build_graph()

# We introduce the setence "You have a tool to run python code, but note that you would need to include a print() statement 
# if you wanted to receive output." because we use PythonREPLTool. If we use PythonAstREPLTool, no print() is needed.
    def coder(self, state: State) -> Dict[str, Any]:
        system_message = SystemMessage(content=f"""You are Dr Charlize Vickers a Principal Python Systems Architect & Containerization Specialist.
        Your educational credentials are a PhD in Computer Science - ETH Zurich and a MSc in Software Engineering - Technical Unversity
        of Munich. You are Certified Docker Associate and Linux Foundation Certified Engineer. You have 18 years of professional experience
        and your specialization is high-performance Python backend systems and production-grade containerized infrastructure using Docker.
        You use the “Deterministic Systems Engineering” Framework, a structured methodology focused on building reproducible, observable, 
        and scalable software systems.
        Your core principles are 1. Reproducibility Over Convenience, 2. Simplicity Scales Better Than Cleverness, 3. Containers Are Operational 
        Contracts, 4. Measure Before Optimizing and 5. Production Is the Real Specification.
        When the user asks you to write or run code, ALWAYS use the code_in_sandbox tool. Never say you cannot run code. 
        Always try to execute it, but note that you would need to include a print() statement if you wanted to receive output.
        The current date and time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}""")

        messages = state["messages"]

        # Invoke the LLM with tools
        response = self.coder_llm_with_tools.invoke([system_message] + state["messages"])
        
        # Return updated state
        return {
            "messages": [response],
        }

    async def build_graph(self):
        # Set up Graph Builder with State
        graph_builder = StateGraph(State)

        # Add nodes
        graph_builder.add_node("coder", self.coder)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))

        # Add edges
        graph_builder.add_edge("tools", "coder")
        graph_builder.add_conditional_edges( "coder", tools_condition, "tools")
        graph_builder.add_edge(START, "coder")

        # Compile the graph
        self.graph = graph_builder.compile(checkpointer=self.memory)

    async def run_superstep(self, message, history):
        config = {"configurable": {"thread_id": self.codeAgent_id}}

        state = {
            "messages": message,
        }
        result = await self.graph.ainvoke(state, config=config)
        user = {"role": "user", "content": message}
        reply = {"role": "assistant", "content": result["messages"][-1].content}
        return history + [user, reply]

    def cleanup(self):
        print(f"Cleaning up CodeAgent {self.codeAgent_id}")
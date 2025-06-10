import asyncio
import re
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from ollama import chat
from ollama import ChatResponse
from pypdf import PdfReader
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
import chromadb
from datetime import datetime, timedelta
import time
from syslog import Syslog
from db_init import VectorDB

class PreFrontalCortex:
    def __init__(self):
        self.syslog = Syslog(log_file="logs/preftrontal_cortex.log")
        self.syslog.log("PreFrontalCortex initialized.", level="INFO")
        self.executor = None
        self.language_cortex = LanguageCortex()
        self.agentic_cortex = AgenticCortex()
        self.monologue = self.language_cortex.ollama_call
        self._tools_initialized = False
        self.syslog.log("PreFrontalCortex ready to run.", level="INFO")
        self.syscom_db = VectorDB()
        self.syscom_db.loadDataToVectorDB()
        self.syslog.log("Vector DB Containing System Commands Loaded & Started successfully !")

    def set_executor(self, executor):
        self.executor = executor
        self.syslog.log(f"Executor set in PreFrontalCortex. {executor}", level="INFO")
        
    async def initialize(self):
        if not self._tools_initialized:
            self.syslog.log("Initializing tools in AgenticCortex...", level="INFO")
            await self.agentic_cortex.show_tools()
            self._tools_initialized = True
            self.syslog.log("Tools initialized successfully.", level="INFO")
            
    async def checkInput(self, input):
        if not self._tools_initialized:
            self.syslog.log("Tools not initialized, initializing now...", level="INFO")
            await self.initialize()
            
        tools_list = self.agentic_cortex.tools
        tool_names = [tool.name for tool in tools_list] if tools_list else [] # Yea this is pretty in-efficient i admit
        # What ? You got a more efficient way ?. Open a PR then instead of whining about it
        
        # Create a more detailed prompt with tool descriptions
        tool_descriptions = []
        for tool in tools_list:
            if hasattr(tool, 'description') and tool.description:
                tool_descriptions.append(f"- {tool.name}: {tool.description}")
            else:
                tool_descriptions.append(f"- {tool.name}")
        
        tool_info = "\n".join(tool_descriptions) if tool_descriptions else "No tools available"
        
        innermonologue_prompt = f"""ANALYZE THIS INPUT CAREFULLY:
                                    Input: "{input}"

                                    Available tools:
                                    {tool_info}

                                    Answer YES if the input requests ANY of the following:
                                    - System/shell commands (ls, cd, mkdir, install, run, execute, etc.)
                                    - File operations (open, read, write, create, edit files)
                                    - Getting current time/date
                                    - Word counting or text analysis
                                    - Any task that requires external tools or system interaction

                                    Answer NO only if it's a simple conversational question that doesn't need tools.

                                    YES or NO (one word only):"""
        self.syslog.log(f"Checking input: {innermonologue_prompt}", level="INFO")
        response = self.monologue(innermonologue_prompt, RAG=False)
        self.syslog.log(f"Monologue response: {response.strip().replace('.','')}", level="INFO")

        response_clean = response.strip().lower().replace('.', '').replace(':', '')
        if re.search(r'\b(yes|y|true|1)\b', response_clean) or response_clean.startswith('yes'):
            self.syslog.log("Input requires tool invocation.", level="INFO")
            needs_tool =  True
        else:
            self.syslog.log("Input does not require tool invocation.", level="INFO")
            needs_tool =  False

        if needs_tool:
            innermonologue_prompt = f"Yes or No ? (one word answer). Does this input require a commandline level execution ? prompt:{input}"
            response = self.monologue(innermonologue_prompt, RAG=False)
            response_clean = response.strip().lower().replace('.', '').replace(':', '')
            if re.search(r'\b(yes|y|true|1)\b', response_clean) or response_clean.startswith('yes'):
                self.syslog.log(f"Monologue response: {response.strip().replace('.','')}", level="INFO")
                self.syslog.log("Input requires syscom context", level="INFO")
                context = self.syscom_db.retriever(input)
                input = input + str(f"Command Guide: {context}")
            else:
                self.syslog.log("Input does not require syscom context", level="INFO")
            # Removed the incorrect "needs_tool = False" line that was causing tools to be bypassed
            self.syslog.log("Invocation running")
            response = await self.agentic_cortex.initialize_tools(message=input)
            self.syslog.log(f"Tool invocation response: {response}")
            for message in reversed(response):
                if hasattr(message, 'content') and message.__class__.__name__ == 'AIMessage':
                    return message.content
            return str(response)
        else:
            self.syslog.log("Invocation skipping")
            return self.language_cortex.ollama_call(input, RAG=False)

# Cool name huh
class AgenticCortex:
    def __init__(self, model_name="Rigel"):
        self.model = ChatOllama(model=model_name)
        self.tools = []
        self._initialized = False
        self.syslog = Syslog(log_file="logs/agentic_cortex.log")
        self.syslog.log(f"AgenticCortex initialized with model: {model_name}", level="INFO")
        self.syslog.log("AgenticCortex ready to run.", level="INFO")

    async def show_tools(self):
        if not self._initialized:
            self.syslog.log("Tools not initialized, initializing now...", level="INFO")
            server_params = StdioServerParameters(
                command="python",
                args=["rigel_mcp.py"],
            )
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    self.tools = await load_mcp_tools(session)
                    self._initialized = True
                    self.syslog.log(f"Tools initialized: {len(self.tools)} tools loaded", level="INFO")
        return self.tools

    async def initialize_tools(self, message):
        server_params = StdioServerParameters(
            command="python",
            args=["rigel_mcp.py"],
        )
        
        if not self._initialized:
            self.syslog.log("Initializing tools...", level="INFO")
            
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self.tools = await load_mcp_tools(session)
                self._initialized = True
                self.syslog.log(f"Tools initialized: {len(self.tools)} tools loaded", level="INFO")
                agent = create_react_agent(self.model, self.tools)
                res = await agent.ainvoke({"messages": message})
                self.syslog.log(f"Raw agent response: {res}", level="INFO")
                return res['messages']

    #     # self.tools = await load_mcp_tools(session)
    #     # self._initialized = True
    #     # self.syslog.log(f"Tools initialized: {len(self.tools)} tools loaded", level="INFO")


    #     return self.tools

    # async def run(self):
    #     if not self._initialized:
    #         await self.initialize_tools()
    #     agent = create_react_agent(self.model, self.tools)
    #     return agent
            
    # async def invoke(self, agent, message):
    #     res = await agent.ainvoke({"messages": message})
    #     return res
    
class LanguageCortex:
    def __init__(self, chroma_client=chromadb.PersistentClient(path="chromadb"), memory_collection_name="rigel_memory",research_collection_name="rigel_research"):
        self.chroma_client = chroma_client
        self.memory_target_collection = self.chroma_client.get_or_create_collection(name=memory_collection_name)
        self.working_memory_collection = self.chroma_client.get_or_create_collection(name="working_memory")
        self.embedding_function = DefaultEmbeddingFunction()
        self.model = 'Rigel'
        self.syslog = Syslog(log_file="logs/language_cortex.log")

    def RAG(self, input, mode):
        if mode == "input":
            question = input[0]
            answer = input[1]
            current_ids = self.memory_target_collection.get()['ids']
            next_id = f"qa_{len(current_ids) + 1}"

            self.memory_target_collection.add(
                documents=[answer],
                metadatas=[{"question": question, "answer": answer}],
                ids=[next_id]
            )

        elif mode == "query":
            question = input
            results = self.memory_target_collection.query(
                query_texts=[question],
                n_results=3,
                include=["documents", "metadatas", "distances"]
            )

            formatted_results = []
            if results["documents"] and results["metadatas"]:
                for doc, metadata, distance in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
                    if distance > 3:
                        continue

                    question_meta = metadata.get("question", "Unknown Question")
                    formatted_results.append(f"Question_User: {question_meta}\nAnswer_Rigel: {doc}")

            if not formatted_results:
                return "No relevant memory found."

            retrieved_text = "\n\n".join(formatted_results)
            return retrieved_text

    def embedded_working_memory(self, input, mode="store", ttl_minutes=30):
        if mode == "store":
            expiration_time = (datetime.now() + timedelta(minutes=ttl_minutes)).strftime("%Y-%m-%d %H:%M:%S.%f")
            self.working_memory_collection.add(
                documents=[input[0]],
                metadatas=[{"question": input[0], "answer": input[1], "expiration_time": expiration_time, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}],
                ids=[f"working_{len(self.working_memory_collection.get()['ids']) + 1}"]
            )
        elif mode == "query":
            all_items = self.working_memory_collection.get()

            if not all_items or len(all_items.get('ids', [])) == 0:
                return "No working memory found."

            memory_items = []
            for idx, metadata in enumerate(all_items['metadatas']):
                if idx >= len(all_items['documents']):
                    continue

                timestamp_str = metadata.get('timestamp', '0')
                try:
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
                    expiration_time_str = metadata.get('expiration_time')

                    if expiration_time_str and datetime.strptime(expiration_time_str, "%Y-%m-%d %H:%M:%S.%f") < datetime.now():
                        continue

                    question = metadata.get('question', 'Unknown question')
                    answer = metadata.get('answer', all_items['documents'][idx])
                    memory_items.append((timestamp, question, answer))
                except (ValueError, TypeError):
                    continue

            memory_items.sort(key=lambda x: x[0])
            latest_items = memory_items[-10:] if len(memory_items) > 10 else memory_items

            retrieved_text = ""
            for _, question, answer in latest_items:
                retrieved_text += f"Question_User: {question}\nAnswer_Rigel: {answer}\n\n"

            if not retrieved_text:
                return "No recent interactions found in working memory."

            return retrieved_text
        elif mode == "clear":
            all_items = self.working_memory_collection.get()
            current_time = datetime.now()

            if not all_items or len(all_items.get('ids', [])) == 0:
                return

            ids_to_delete = []
            for idx, metadata in enumerate(all_items.get('metadatas', [])):
                if idx >= len(all_items['ids']):
                    continue

                expiration_time = metadata.get("expiration_time")
                try:
                    if expiration_time and datetime.strptime(str(expiration_time), "%Y-%m-%d %H:%M:%S.%f") < current_time:
                        ids_to_delete.append(all_items['ids'][idx])
                except (ValueError, TypeError):
                    continue

            if ids_to_delete:
                self.working_memory_collection.delete(ids=ids_to_delete)

    def ollama_call(self, question, RAG=False):
        self.embedded_working_memory(None, mode="clear")

        permanent_context = self.RAG(question, "query")
        working_context = self.embedded_working_memory(question, mode="query")

        if RAG:
            combined_context = ""
            if working_context:
                combined_context += f"Recent Working Memory Context:\n{working_context}\n\n"
            if permanent_context and permanent_context != "No relevant memory found.":
                combined_context += f"Context:\n{permanent_context}\n"
            if not combined_context:
                combined_context = "No relevant context found."
        else:
            combined_context = ""

        self.syslog.log(f"Combined Memory Context---------\n{combined_context}\n-------------", level="INFO")
        if not combined_context:
            full_prompt = f"Question: {question}\nAnswer:"
        else:
            full_prompt = f"Memory Context:\n{combined_context}\n\nQuestion: {question}\nAnswer:"
        self.syslog.log(full_prompt, level="INFO")

        response: ChatResponse = chat(model=self.model, messages=[
            {'role': 'user', 'content': full_prompt}
        ])
        self.memory_target_collection.add(
            documents=[response.message['content']],
            metadatas=[{"question": question, "answer": response.message['content']}],
            ids=[f"qa_{len(self.memory_target_collection.get()['ids']) + 1}"]
        )

        self.embedded_working_memory([question, response.message['content']], mode="store")

        return response.message['content']
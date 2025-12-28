from agents import Agent, ModelSettings, Runner 
#mcp  agents, model configuration (temperature), runner: model orquestration
from agents.mcp import MCPServerStdio 
import streamlit as st
from dotenv import load_dotenv
import asyncio, json, sys

#from here only one, will load resources

if sys.platform == "win32":  # for asyncio to work on windows
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

st.markdown("<h1 style='text-align: center;'>NovaDrive Motors</h1>", unsafe_allow_html=True) # title

_, cent_co, _ = st.columns(3) # imagem
with cent_co:
    st.image("novadrive.png", caption="NovaDrive Motors")

if "history" not in st.session_state:  # create the session history if is the first time, load .env
    load_dotenv()  
    st.session_state.history = []
    
#build the role interfaze every execution
for message in st.session_state.history:   # show chat on UI : user, assistant, function_call , function_call_output
    type = message.get("role", None) or message.get("type", None)  #type could be user, assistant, function_call , function_call_output

    match type:
        case 'user': 
            with st.chat_message(type): # user balon
                st.markdown(message["content"])
        case 'assistant': 
            with st.chat_message(type): # assistant balon
                st.markdown(message["content"][0]["text"])
        case 'function_call': 
            if "transfer_to" not in message["name"]: # if have transfer to is not a tool
                with st.chat_message(name="tool", avatar=":material/build:"):
                        st.markdown(f'LLM calling tool {message["name"]}') #show tool name
                        with st.expander("View arguments"):
                            st.code(message["arguments"]) #arguments or parameters, code block
        case 'function_call_output':
            try:
                obj = json.loads(message['output'])
                with st.chat_message(name="tool", avatar=":material/data_object:"):
                    with st.expander("View response"):
                        st.code(obj["text"])
            except:
                continue
        
if "ReceptionAgent" not in st.session_state:   #create and store on session 3 agents
        MaintenanceAgent = Agent( 
            name="MaintenanceAgent", 
            model="gpt-4-1106-preview",
            handoff_description="Agent for service and maintenance appointments for existing customers.",
            instructions="""You are a NovaDrive Motors assistant helping customers schedule service or maintenance for vehicles they already own.
                Ask for the customer's full name and use the tool get_customer_info to retrieve details about the vehicles they purchased and the dealership.
                Then, gather the service request information and use schedule_visit_for_maintenance to schedule the visit.
                Always use the tools provided. Do not provide answers manually or guess vehicle data. Your task is to automate the process using available tools.""",
            model_settings=ModelSettings(tool_choice="auto", temperature=0, parallel_tool_calls=False), #tool choise, how to choose the tool, none, a list of the ones it can use, required (need to call one), parallel_tool_calls is if can call the tools in parallel
        )

        SalesAgent = Agent(  
            name="SalesAgent", 
            model="gpt-4-1106-preview",
            handoff_description="Agent for sales support, vehicle information, and scheduling test drives.",
            instructions="""You are a NovaDrive Motors assistant helping customers explore and purchase vehicles. Use the available tools to perform every step of your task.
                Start by calling the tool get_available_vehicles to get the list of current options and share it with the user.
                Ask clarifying questions if needed, but always rely on tool data to suggest vehicles.
                Once the user decides, use get_dealerships to list dealerships, then get_sellers_by_dealership to find sellers. Schedule a test drive or purchase visit using schedule_visit_for_purchase.
                You must not answer manually — always use tools. Your entire workflow depends on tool calls.""",
            model_settings=ModelSettings(tool_choice="auto", temperature=0, parallel_tool_calls=False), 
        )

        ReceptionAgent = Agent( 
            name="ReceptionAgent", 
            model="gpt-4-1106-preview",
            handoffs=[SalesAgent, MaintenanceAgent], 
            instructions="""You are the reception assistant for NovaDrive Motors, an automotive company. Your job is only to greet the user and redirect them to the correct specialized agent. You must not answer specific questions or use any tools.
                If the user is interested in purchasing a car, exploring options, or scheduling a test drive, transfer the conversation to the SalesAgent.
                If the user already owns a car and needs a service or maintenance appointment, transfer the conversation to the MaintenanceAgent.
                Do not attempt to help directly. Your role is only to welcome and route the request.""",
            model_settings=ModelSettings(tool_choice="auto", temperature=0, parallel_tool_calls=False), 
        )

        st.session_state.ReceptionAgent = ReceptionAgent
        st.session_state.SalesAgent = SalesAgent
        st.session_state.MaintenanceAgent = MaintenanceAgent
        st.session_state.current_agent = ReceptionAgent 

#until here only once

async def resolve_chat():  #execute the main chat, create and mcp local with stdio, the server exists only when the fucion is executed
    async with MCPServerStdio(params={"command": "mcp", "args": ["run", "server_agent.py"]}) as server:
        st.session_state.SalesAgent.mcp_servers = [server]  #connect the agents to the server, ReceptionAgent  dont use tools, only redirect
        st.session_state.MaintenanceAgent.mcp_servers = [server] 

        result = await Runner.run(  # call the agent with history that will decid to answer or to call anther agent or tool
            starting_agent=st.session_state.current_agent, # who will start responde, is the actual agent
            input=st.session_state.history, # all conversation up to now
            context=st.session_state.history  # same as input, could have metadata
        )

        st.session_state.current_agent = result.last_agent  # current agent
        st.session_state.history = result.to_input_list()  #list of messagens to keep state and continue the conversation

prompt = st.chat_input("Type your message:")  # mostra uma mensagem de entra para o usuário ao final

if prompt:
    st.session_state.history.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Thinking..."):  #call resolve_chat to process the conversation, reload the interface
        asyncio.run(resolve_chat())
        st.rerun()

if "current_agent" in st.session_state:   #toat to show the avaliable agent in use
    st.toast(f"Current agent: { st.session_state.current_agent.name }")

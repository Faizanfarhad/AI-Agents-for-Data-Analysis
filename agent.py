
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool, ToolRuntime
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.structured_output import ToolStrategy
from dotenv import load_dotenv
load_dotenv()


import os 
import pandas as pd 
import io
import tempfile
from typing import Optional, Union
from pathlib import Path

from pydantic import BaseModel,WithJsonSchema
from typing import Annotated,Callable

files = list(Path.cwd().joinpath("data_preprocessing").glob("*"))

# NOTE from here components is getting import  
from data_preprocessing.file_ingestion import execute

google_api = os.environ.get(key="GOOGLE_API_KEY")   

# Define context schema
@dataclass
class Context:
    """Custom runtime context schema."""
    user_id: str = "1"

@dataclass
class Stats:
    mean: float
    stddev: float

# Define response format
@dataclass
class ResponseFormat:
    """Response schema for the agent."""
    leaned_path: str                     # path to the cleaned file
    rows_processed: int                   # metadata
    summary: str
    result_file: str
    stats: Optional[Stats] = None # an optional text summary


class ExecuteInput(BaseModel):
    file_source: str
    remove_null: bool = False

@tool(args_schema=ExecuteInput)
def get_file(
    file_source: Union[str, io.IOBase, bytes],
    remove_null: bool = False,
    runtime: Optional[ToolRuntime] = None,
) -> str:
    """Read ``file_source``, clean it, and write the result.

    ``file_source`` may be a file path (string), a file-like object, or
    raw bytes. When a non-path source is given we dump it to a temporary
    file before calling the existing ``execute`` helper.

    ``runtime`` is accepted so the agent can inject a ``ToolRuntime``
    instance if desired; it's optional for simple cases.
    """
    if runtime is not None:
        print("called by", runtime.tool.name)
    #create cleaneddir 
    if not os.path.exists('cleanedDF'):
        os.mkdir('cleanedDF')
    
    # convert to path
    '''
    User gives us:  path string → Path object → file object → raw bytes
                        ↓           ↓              ↓           ↓
                We do nothing  convert to str  read & write   write
                        ↓           ↓              ↓           ↓
                Result: self.path = a filesystem path string (always)
    '''
    if not isinstance(file_source, str):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        if hasattr(file_source, "read"):
            tmp.write(file_source.read())
        else:
            tmp.write(file_source)
        tmp.flush()
        file_path = tmp.name
    else:
        file_path = file_source
    
    out_path = execute(file_path, remove_null)
    return f"file saved to {out_path}"

class Agent(Context,Stats,ResponseFormat):
    
    def __init__(
        self,
        model_name: str,
        input_source: Union[str, Path, io.IOBase, bytes],
        api_key: str,
        model_provider: str,
        remove_null: Optional[bool] = False,
    ):

        super().__init__(user_id="1")

        assert isinstance(model_name, str), f"Model Name should be an Str not {type(model_name)}"
        assert isinstance(api_key, str), f"api_key should be an Str not {type(api_key)}"
        assert isinstance(model_provider, str), f"model_provider should be an Str not {type(model_provider)}"

        self.model_name = model_name
        # support file-like/bytes by writing to temp path
        if not isinstance(input_source, (str, Path)):
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv") #delete is used for not deleting the tempfile automatically , suffix is for defining output type(it does not add . automatically)
            if hasattr(input_source, "read"): # checking that it has method with the name of .read() or not if yes the write using .read() else write(input soruce )
                tmp.write(input_source.read())
            else:
                tmp.write(input_source)
            tmp.flush()
            self.path = tmp.name
        else:
            self.path = str(input_source)

        self.api_key = api_key
        self.remove_null = remove_null
        self.model_provider = model_provider
        # Define system prompt
        self.SYSTEM_PROMPT = """You are an expert Data Scientist , who can preprocess and unstructure data and transform that data into in structured format asked by user.
        You have access of tools like:
        - get_file: use this to get the file as input and preprocess(without losing any important information) that data and make into structed(if it is unstructrued)"""
    
    # Define tools
    def run(self):
        # NOTE : by using init_chat_model we can load differ model
        
        model = init_chat_model(self.model_name,
                                model_provider=self.model_provider,
                                api_key=self.api_key)
        
        # Set up memory
        checkpointer = InMemorySaver()
        
        # Create agent
        # Run agent
        # `thread_id` is a unique identifier for a given conversation.
        agent = create_agent(
            model= model,
            system_prompt=self.SYSTEM_PROMPT,
            tools=[get_file],
            context_schema=Context,
            response_format=ToolStrategy(ResponseFormat),
            checkpointer=checkpointer
        )
        
        config = {"configurable": {"thread_id": "1"}}
        
        out = f"{Path(self.path).stem}_cleaned"
        
        response = agent.invoke(
            {"messages": [{"role": "user", 
                        "content": f"please clean if : (ignore input file if the input file format is .csv , .json  for this format run 'execute(path,should_remove)' and save according as defined  ) else : the file at {self.path} and save clean and structed on by creating a directory cleanedDF/{out}.(file_format)"}]},
            config=config,
            context=Context(user_id="1")
        )
        return response['structured_response']

if __name__ == '__main__':
    model_name = "gemini-2.5-flash-lite"
    model_provider = 'google_genai'
    input_file_path  = 'test/archive/final_dataset_with_all_features_v3.1.csv'
    agent = Agent(
        model_name=model_name,
        model_provider=model_provider,
        input_source=input_file_path,
        api_key=google_api,
    )
    
    print(agent.run())
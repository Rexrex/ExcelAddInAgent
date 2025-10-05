import os
import dotenv
import logging
import asyncio
import yaml

from src.utils.load_utils import BasicConfig
from pydantic_ai import Agent, RunContext, UsageLimits
from pydantic import BaseModel

class ExcelOutput(BaseModel):
    description: str
    instructions: str


## Initalize the Agent
def generate_excel_agent(llm_model, langfuse=None, logger=None):
    excel_agent_instructions = "You are a Master of Microsoft's Excel. You know how to solve any excel related question as if your life depends on it. The output should contains examples of instructions for excel."

    if langfuse:
        excel_agent_prompt = langfuse.get_prompt("excel_agent_system_prompt")
        if excel_agent_prompt:
             excel_agent_instructions = excel_agent_prompt.prompt
             
            with open("excel_formulas.yaml", "r") as f:
                excel_knowledge = yaml.safe_load(f)
                instruction_examples = format_excel_knowledge(excel_knowledge)
                excel_agent_intructions.compile(instruction_examples=instruction_examples)
                excel_agent_intructions = excel_agent_prompt.prompt
       
    excel_agent = Agent(llm_model, instructions=excel_agent_instructions, instrument=True, output_type=ExcelOutput)
    logger.info("Excel Agent Initialization successful")

    @excel_agent.tool
    def compute_formula(formula: str, inputs: dict[str, float]) -> float:
        """
        Compute a simple Excel formula using given inputs.

        arguments:
        formula: Excel-style formula, e.g. "SUM(a, b, c)" or "a * b + c"
        inputs: mapping of variable names to values

        returns:
        numerical result
        """
        # You might parse the formula, or map known functions to Python
        # For simplicity, here we replace variable names then eval
        expr = formula
        for var, val in inputs.items():
            expr = expr.replace(var, str(val))
        # Danger: eval is unsafe; in real code use proper parser
        return eval(expr)
        
    return excel_agent

def initialize_excel_agent(BasicConfig=None):
    if( BasicConfig is None):
        BasicConfig = BasicConfig()
    llm_model, langfuse, logger = BasicConfig.llm_model, BasicConfig.langfuse, BasicConfig.logger
    logger.info("Initializing Excel Agent...")
    excel_agent = generate_excel_agent(llm_model, langfuse=langfuse, logger=logger)
    return excel_agent


def format_excel_knowledge(data: dict) -> str:
    out = []
    for name, info in data.get("excel_formulas", {}).items():
        out.append(f"**{name}** — {info['description']}")
        out.append(f"Syntax: {info['syntax']}")
        if examples := info.get("examples"):
            for ex in examples[:2]:  # limit to 2 examples
                out.append(f"Example: {ex['formula']} → {ex['result']}")
        out.append("")  # blank line
    return "\n".join(out)


if __name__ == "__main__":
    try:
        BasicConfig = BasicConfig()
        excel_agent = initialize_excel_agent(BasicConfig=BasicConfig)
        logger = BasicConfig.logger
        user_request = input("Enter your question for the Excel agent: ")
        result = asyncio.run(excel_agent.run(user_request))
        print(f"Agent Reply: {result.output}")

    except Exception as e:
        logger.error(f"Startup Failed: {e}")
        exit(1) 

    
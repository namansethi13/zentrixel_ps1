from google.adk.agents import Agent, SequentialAgent
from google.genai import types # For further configuration controls
from .summerizer_agent import summerizer_agent
from .firestore_agent import firestore_agent
root_agent = SequentialAgent(
    name="workflow_3",
    description="does three things",
    sub_agents=[
        summerizer_agent,
        firestore_agent
    ]
)

"""
1. anomaly detection agent with google search functionality -> outputs list of verified/not sensitive claims 
2. summerizer agent summerizes all of this into a summary like how a user will report it exhibiting real emotions in the summary
3. mood detection agent and detect the mood of the summary, update/create summary for given lon, lat and loc. TODO
"""
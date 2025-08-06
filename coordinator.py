"""
CoordinatorAgent - Central Orchestrator for Content Factory Agents

This module defines the CoordinatorAgent class, which manages and coordinates all modular agents
(character, curriculum, script, voice, visual, etc.) in the Content Factory pipeline.

Key Responsibilities:
- Registers agent instances under a common interface.
- Provides a simple interface (run_agent) to execute any registered agent by name.
- Passes input data and optional keyword arguments to the target agent's run() method.
- Raises an error if an unregistered agent is called.

This enables flexible, pluggable, and decoupled multi-agent workflows throughout the system.
"""

class CoordinatorAgent:
    def __init__(self):
        self.agents = {}

    def register_agent(self, agent_name, agent_instance):
        self.agents[agent_name] = agent_instance

    def run_agent(self, agent_name, input_data, **kwargs): 
        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not registered.")
        return agent.run(input_data, **kwargs)


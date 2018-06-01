from hakuna_matata.agent  import ASPAgent
from hakuna_matata.common import Percept

agent = None

def PyAgent_Constructor():
    global agent
    agent = ASPAgent()

def PyAgent_Destructor():
    return None

def PyAgent_Initialize():
    return None

def PyAgent_Process(stench, breeze, glitter, bump, scream):
    global agent
    return int(agent.process(Percept(stench, breeze, glitter, bump, scream)))

def PyAgent_GameOver (score):
    return None

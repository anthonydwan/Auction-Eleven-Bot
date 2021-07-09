from gameEngine import GameEngine, NPCRandomBot
import importlib

# List your bots here
botsToRun = {
    "NPC": 3,
    "Bots.pizza9": 2,
    # "examples.randomBidder": 3,
    # "examples.oneGreater": 3,
    # "examples.oneGreaterSkipper": 4
}

engine = GameEngine()

for b in botsToRun:
    for i in range(botsToRun[b]):
        if b=="NPC":
            engine.registerBot(NPCRandomBot(),team="NPC")
        else:
            botClass = importlib.import_module(b)
            engine.registerBot(botClass.CompetitorInstance(),team=b)
engine.runGame()

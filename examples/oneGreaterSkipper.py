class CompetitorInstance():
    def __init__(self):
        self.turn_no = 0
        pass
    
    def onGameStart(self, engine, gameParameters):
        self.engine=engine
        self.gameParameters = gameParameters
    
    def onAuctionStart(self, index, trueValue):
        print("I'm SKIPPER BOT: " + str(index))
        pass

    def onBidMade(self, whoMadeBid, howMuch):
        pass

    def onMyTurn(self,lastBid):
        self.turn_no +=1
        if self.turn_no > 10:
            if (lastBid<self.gameParameters["meanTrueValue"]):
                self.engine.makeBid(lastBid+11)
        pass

    def onAuctionEnd(self):
        self.turn_no = 0
        pass
"""
to be done

    abnormally low bidder is known value bidder (?)

    CHRISTIE - does not bet big, focuses on identifying others
    edison - undetected
    reltyz - undetected
    SmashBros - undetected
    One - undetected
    use standard dev for bets (true value is always within 1 SD of the mean)
    make more accurate estimate of true value

"""


# class Node():
#     def __init__(self, val):
#         self.next = None
#         self.val = val
#
# class CircularLinkedList():
#     #Constructor
#     def __init__(self):
#         self.head = None
#
#     def append(self, val):
#         if not self.head:
#             self.head = Node(val)
#             self.head.next = self.head
#         else:
#             new_node = Node(val)
#             curr = self.head
#             while curr.next != self.head:
#                 curr = curr.next
#             curr.next = new_node
#             new_node.next = self.head
#
#     def find(self, val):
#         curr = self.head
#         while curr.val != val:
#             curr = curr.next
#         return curr


class CompetitorInstance():
    def __init__(self):
        # initialize personal variables
        self.bid_diff_log = dict()
        self.last_bid_log = dict()
        self.whoMadeBid_log = []
        self.turn_no = 0
        self.bids = [9, 10, 12]
        self.true_val_bids = [9, 11, 12]
        self.set_values = set(self.bids)
        self.true_set_values = set(self.true_val_bids)
        # self.first_round_skippers = dict()
        self.long_bids = False
        pass

    def onGameStart(self, engine, gameParameters):
        # engine: an instance of the game engine with functions as outlined in the documentation.
        self.engine = engine
        # gameParameters: A dictionary containing a variety of game parameters
        self.gameParameters = gameParameters
        self.numplayers = self.gameParameters["numPlayers"]

        # self.rotation = CircularLinkedList()
        # for i in range(self.numplayers):
        #     self.rotation.append(i)
        #
        # curr = self.rotation.head
        # for i in range(20):
        #     print(curr.val)
        #     curr = curr.next

    def onAuctionStart(self, index, trueValue):
        # index is the current player's index, that usually stays put from game to game
        # trueValue is -1 if this bot doesn't know the true value
        self.trueValue = None
        if trueValue != -1:
            self.trueValue = trueValue
        self.index = index
        # print("I'm PIZZA BOT: " + str(index))
        pass

    def onBidMade(self, whoMadeBid, howMuch):
        # whoMadeBid is the index of the player that made the bid
        # howMuch is the amount that the bid was

        # check skippers
        # if len(self.whoMadeBid_log) > 0:
        #     if self.whoMadeBid_log[-1] == endplayer_no:
        #         if whoMadeBid != 0:
        #             for i in range(0, whoMadeBid):
        #                 if i not in self.first_round_skippers:
        #                     self.first_round_skippers[i] = 1
        #                     print("SKIPPER! competitor: " + str(i))
        #                     print("Skipped times: " + str(self.first_round_skippers[i]))
        #                 else:
        #                     self.first_round_skippers[i] += 1
        #                     print("SKIPPER! competitor: " + str(i))
        #                     print("Skipped times: " + str(self.first_round_skippers[i]))
        #     elif whoMadeBid != self.whoMadeBid_log[-1] + 1:
        #         for i in range(self.whoMadeBid_log[-1] + 1, self.gameParameters["numPlayers"]):
        #             if i not in self.first_round_skippers:
        #                 self.first_round_skippers[i] = 1
        #                 print("SKIPPER! competitor: " + str(i))
        #                 print("Skipped times: " + str(self.first_round_skippers[i] ))
        #             else:
        #                 self.first_round_skippers[i] += 1
        #                 print("SKIPPER! competitor: " + str(i))
        #                 print("Skipped times: " + str(self.first_round_skippers[i] ))
        #         for i in range(0, whoMadeBid):
        #             if i not in self.first_round_skippers:
        #                 self.first_round_skippers[i] = 1
        #                 print("SKIPPER! competitor: " + str(i))
        #                 print("Skipped times: " + str(self.first_round_skippers[i]))
        #             else:
        #                 self.first_round_skippers[i] += 1
        #                 print("SKIPPER! competitor: " + str(i))
        #                 print("Skipped times: " + str(self.first_round_skippers[i]))


        # logging who made last bid
        if len(self.whoMadeBid_log) >= 5:
            self.whoMadeBid_log.pop(0)
            self.whoMadeBid_log.append(whoMadeBid)
        else:
            self.whoMadeBid_log.append(whoMadeBid)

        # logging queue of last few bids
        if not hasattr(self, "howMuch_log"):
            self.howMuch_log = [0, howMuch]
        elif len(self.howMuch_log) >= 3:
            self.howMuch_log.pop(0)
            self.howMuch_log.append(howMuch)
        else:
            self.howMuch_log.append(howMuch)

        # logging bots bid pattern (difference)
        if whoMadeBid not in self.bid_diff_log:
            self.bid_diff_log[whoMadeBid] = [howMuch - self.howMuch_log[-2]]
        else:
            if len(self.bid_diff_log[whoMadeBid]) >= 15:
                self.long_bids = True
                self.bid_diff_log[whoMadeBid].pop(0)
                self.bid_diff_log[whoMadeBid].append(howMuch - self.howMuch_log[-2])
            else:
                self.bid_diff_log[whoMadeBid].append(howMuch - self.howMuch_log[-2])


        # logging bots last bids
        if whoMadeBid not in self.last_bid_log:
            self.last_bid_log[whoMadeBid] = [howMuch]
        else:
            if len(self.last_bid_log[whoMadeBid]) >= 10:
                self.last_bid_log[whoMadeBid].pop(0)
                self.last_bid_log[whoMadeBid].append(howMuch)
            else:
                self.last_bid_log[whoMadeBid].append(howMuch)
        pass

    def onMyTurn(self, lastBid):
        # lastBid is the last bid that was made
        self.turn_no += 1

        # # checking first_rounds_skippers
        # if self.turn_no == 11:
        #     print("THIS IS TURN 11")
        #     self.enemy_skippers = [competitor for competitor in self.first_round_skippers.keys() if
        #                            self.first_round_skippers[competitor] >= 9]

        # checking allies after 4 turns:
        self.total_allies = [self.index]

        if self.turn_no <= 4:
            self.known_bid_ally = self.other_allies = -1
        else:
            self.known_bid_ally = self.detect_known_bid_ally()
            self.other_allies = self.detect_other_ally()
            if self.known_bid_ally != -1:
                self.total_allies.append(self.known_bid_ally)
            if self.other_allies != -1:
                self.total_allies.extend(self.other_allies)

        self.total_allies = list(set(self.total_allies))

        if self.whoMadeBid_log:
            lastbidder = self.whoMadeBid_log[-1]
        else:
            lastbidder = "NA"

        ##########################
        # true value bot
        #########################
        randomizerA = self.engine.random.randint(0, len(self.bids) - 1)
        randomizerB = self.engine.random.randint(0, len(self.true_val_bids) - 1)

        if self.trueValue:
            if lastBid < self.trueValue - 300:
                if lastbidder not in self.total_allies:
                    self.engine.makeBid(lastBid + self.true_val_bids[randomizerB])

        #########################
        # non-true val bot
        ##########################
        else:
            if self.known_bid_ally != -1:
                estimated_true_val = self.last_bid_log[self.known_bid_ally][-1] + 300 - 12
                if lastBid < estimated_true_val - 12:
                    if lastbidder not in self.total_allies:
                        self.engine.makeBid(lastBid + self.bids[randomizerA])
            else:
                if (lastBid < self.gameParameters["meanTrueValue"] - 500):
                    # But don't bid too high!
                    if lastbidder not in self.total_allies:
                        self.engine.makeBid(lastBid + self.bids[randomizerA])
                else:
                    pr = 15
                    if pr > self.engine.random.randint(0, 100):
                        if lastbidder not in self.total_allies:
                            self.engine.makeBid(lastBid + self.bids[randomizerA])
        pass

    ###################################################################################
    # detection algorithms
    ####################################################################################

    def matchset(self, ls, set_val_param):
        return set_val_param == set(ls)

    def smallset(self, ls):
        # length req ensures no mistaken bot
        if len(set(ls)) > 6:
            return len(set(ls)) <= 3
        return False

    def sameValue(self, ls):
        if len(ls) > 2:
            value = ls[0]
            for i in range(1, len(ls)):
                if ls[i] != value:
                    return False
            return True
        else:
            return False

    def largeJumps(self, ls):
        for value in ls:
            if value > self.gameParameters["minimumBid"] * (1 + 2):
                return True
        return False

    def consistent_diff(self, ls):
        if len(ls) > 3:
            diff = abs(ls[1] - ls[0])
            for i in range(len(ls) - 1):
                if abs(ls[i + 1] - ls[i]) != diff:
                    return False
            return True
        else:
            return False

    def detect_known_bid_ally(self) -> int:
        for competitor in self.bid_diff_log.keys():
            if self.matchset(self.bid_diff_log[competitor], self.true_set_values):
                return competitor
        return -1

    def detect_other_ally(self) -> int:
        allies = []
        for competitor in self.bid_diff_log.keys():
            if self.matchset(self.bid_diff_log[competitor], self.set_values):
                allies.append(competitor)
        if allies:
            return allies
        else:
            return -1

    ##########################################################################

    def onAuctionEnd(self):
        # Now is the time to report team members, or do any cleanup.

        reportOwnTeam = self.total_allies
        known_val_bots = []
        if self.known_bid_ally != -1:
            known_val_bots.append(self.known_bid_ally)

        reportOppTeam = []

        competitors = [i for i in range(self.numplayers)]

        for competitor in competitors:
            if competitor not in reportOwnTeam:
                if competitor not in self.bid_diff_log.keys():
                    # as a safety measure, only report non-bidders if there has been extensive bidding
                    if self.long_bids:
                        reportOppTeam.append(competitor)
                elif self.consistent_diff(self.bid_diff_log[competitor]):
                    reportOppTeam.append(competitor)
                elif self.largeJumps(self.bid_diff_log[competitor]):
                    reportOppTeam.append(competitor)
                elif self.smallset(self.bid_diff_log[competitor]):
                    reportOppTeam.append(competitor)

        reportOppTeam = list(set(reportOppTeam))
        self.engine.reportTeams(reportOwnTeam, reportOppTeam, known_val_bots)

        # print logs
        # print(self.bid_diff_log)
        # print("own: " + str(reportOwnTeam))
        # print("opp: " + str(reportOppTeam))
        # print("known: " + str(known_val_bots))
        # print("self: " + str(self.index))
        # print("big skippers: " + str(self.enemy_skippers))

        # variable resets
        del self.trueValue
        del self.howMuch_log
        del self.known_bid_ally
        del self.other_allies

        self.bid_diff_log = dict()
        self.last_bid_log = dict()
        # self.first_round_skippers = dict()
        self.whoMadeBid_log = []
        self.turn_no = 0
        self.long_bids = False
        pass

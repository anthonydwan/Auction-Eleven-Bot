"""
to be done

    pk normal and larper_known clashes

    non-NPC bid probability - enemy detection
    implement enemy detection at earlier stage of the game.
    CHRISTIE - does not bet big, focuses on identifying others
    ogre
    edison - undetected
    reltyz - undetected
    SmashBros - undetected
    One - undetected
    x_axis - undetected
    make more accurate estimate of true value


"""


####################################################################

class Node():
    def __init__(self, val):
        self.next = None
        self.val = val


class CircularLinkedList():
    # Constructor
    def __init__(self):
        self.head = None

    def append(self, val):
        if not self.head:
            self.head = Node(val)
            self.head.next = self.head
        else:
            new_node = Node(val)
            curr = self.head
            while curr.next != self.head:
                curr = curr.next
            curr.next = new_node
            new_node.next = self.head

    def find(self, val):
        curr = self.head
        while curr.val != val:
            curr = curr.next
        return curr


###########################################################

class CompetitorInstance():
    def __init__(self):
        # initialize personal variables
        self.last_bid_log = dict()
        self.whoMadeBid_log = []
        self.turn_no = 0
        self.bids = [9, 11, 12]
        self.true_val_bids = [9, 10, 12]
        self.set_values = set(self.bids)
        self.true_set_values = set(self.true_val_bids)
        self.full_log = dict()
        self.long_bids = False
        self.enemy_skippers = []
        self.round = 0
        pass

    def onGameStart(self, engine, gameParameters):
        # engine: an instance of the game engine with functions as outlined in the documentation.
        self.engine = engine
        # gameParameters: A dictionary containing a variety of game parameters
        self.gameParameters = gameParameters
        self.numplayers = self.gameParameters["numPlayers"]
        self.mean_val = self.gameParameters["meanTrueValue"]
        self.sd_val = self.gameParameters["stddevTrueValue"]
        self.rotation = CircularLinkedList()
        for i in range(self.numplayers):
            self.rotation.append(i)

    def onAuctionStart(self, index, trueValue):
        # index is the current player's index, that usually stays put from game to game
        # trueValue is -1 if this bot doesn't know the true value
        self.trueValue = None
        if trueValue != -1:
            self.trueValue = trueValue
        self.index = index

        # print("PIZZA BOT: " + str(self.index))
        # initalising skipper log
        for k in range(self.numplayers):
            self.full_log[k] = []

        self.curr_price = 1
        pass

    def onBidMade(self, whoMadeBid, howMuch):
        # whoMadeBid is the index of the player that made the bid
        # howMuch is the amount that the bid was

        if len(self.whoMadeBid_log) == 0:
            # initialise starting player
            self.bid_index = self.rotation.find(whoMadeBid)

        if self.bid_index.val != whoMadeBid:
            while self.bid_index.val != whoMadeBid:
                self.full_log[self.bid_index.val].append("skip")
                self.bid_index = self.bid_index.next
        self.full_log[whoMadeBid].append(howMuch - self.curr_price)
        self.curr_price = howMuch
        self.bid_index = self.bid_index.next

        # logging who made last bid (list)
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
                # we know that  trueVal is def between mean +/- 1 s.d.
                if lastBid < self.mean_val - self.sd_val:
                    # But don't bid too high!
                    if lastbidder not in self.total_allies:
                        self.engine.makeBid(lastBid + self.bids[randomizerA])
                elif lastBid < self.mean_val:
                    pr = 30
                    if pr > self.engine.random.randint(0, 100):
                        if lastbidder not in self.total_allies:
                            self.engine.makeBid(lastBid + self.bids[randomizerA])
                elif lastBid < self.mean_val + self.sd_val:
                    pr = 10
                    if pr > self.engine.random.randint(0, 100):
                        if lastbidder not in self.total_allies:
                            self.engine.makeBid(lastBid + self.bids[randomizerA])
        pass

    ###################################################################################
    # detection algorithms
    ####################################################################################

    def larper_known(self, ls):
        #     # larper votes higher than NPC
        if self.largeJumps(ls):
            # four bids and skip rest
            if len(ls) >= 8:
                for val in ls[0:4]:
                    if val == "skip":
                        return False
                for val in ls[4:min(len(ls), 10)]:
                    if val != "skip":
                        return False
                return True
        return False

    def pk_known(self, ls):
        if len(ls) > 6:
            for val in ls[:2]:
                if val == "skip":
                    return False
            if ls[2] == "skip":
                return False
            if ls[2] < 2000:
                return False
            for val in ls[3:]:
                if val != "skip":
                    return False
            return True
        return False


    def large_skippers(self, ls):
        # if first 10 turns all skip
        if len(ls) >= 10:
            return set(ls[:10]) == {"skip"}

    def matchset(self, ls, set_val_param):
        ls = [val for val in ls if val != "skip"]
        return set_val_param == set(ls)

    def last10_smallset(self, ls):
        # length req ensures no mistaken bot
        ls = [val for val in ls if val != "skip"]
        if len(ls) > 6:
            return len(set(ls[max(-10, -len(ls) + 2):])) <= 3

    def neverbid(self, ls):
        if len(ls) > 12:
            return set(ls) == {"skip"}

    def last10_sameValue(self, ls):
        ls = [val for val in ls if val != "skip"]
        if len(ls) > 8:
            last_few = ls[max(-10, -1 * len(ls) + 2):]
            value = last_few[0]
            for i in range(len(last_few)):
                if ls[i] != value:
                    return False
            return True
        else:
            return False

    def largeJumps(self, ls):
        ls = [val for val in ls if val != "skip"]
        for value in ls:
            if value > self.gameParameters["minimumBid"] * (1 + 2):
                return True
        return False

    def last10_consistent_diff(self, ls):
        ls = [val for val in ls if val != "skip"]
        if len(ls) > 8:
            last_few = ls[max(-10, -len(ls) + 2):]
            diff = abs(last_few[1] - last_few[0])
            for i in range(len(last_few) - 1):
                if abs(last_few[i + 1] - last_few[i]) != diff:
                    return False
            return True
        return False

    def detect_known_bid_ally(self) -> int:
        for competitor in self.full_log.keys():
            if self.matchset(self.full_log[competitor], self.true_set_values):
                return competitor
        return -1

    def detect_other_ally(self):
        allies = []
        for competitor in self.full_log.keys():
            if self.matchset(self.full_log[competitor], self.set_values):
                allies.append(competitor)
        if allies:
            return allies
        else:
            return -1

    ##########################################################################

    def onAuctionEnd(self):
        # Now is the time to report team members, or do any cleanup.

        self.engine.print(f"ROUND {self.round}")
        self.round += 1

        reportOwnTeam = self.total_allies
        known_val_bots = []
        if self.known_bid_ally != -1:
            known_val_bots.append(self.known_bid_ally)

        reportOppTeam = []

        competitors = [i for i in range(self.numplayers)]

        neverbid = []
        pk_known = []
        larper_known = []
        large_skippers = []
        const_diff = []
        large_jumps = []
        smallset = []

        for competitor in competitors:
            if competitor not in reportOwnTeam:
                if self.neverbid(self.full_log[competitor]):
                    neverbid.append(competitor)

                elif self.pk_known(self.full_log[competitor]):
                    pk_known.append(competitor)
                    known_val_bots.append(competitor)

                elif self.larper_known(self.full_log[competitor]) and not pk_known:
                    # need to prevent clash of pk and larper_known for the timebeing
                    larper_known.append(competitor)
                    known_val_bots.append(competitor)

                elif self.large_skippers(self.full_log[competitor]):
                    large_skippers.append(competitor)

                elif self.last10_consistent_diff(self.full_log[competitor]):
                    const_diff.append(competitor)

                elif self.largeJumps(self.full_log[competitor]):
                    large_jumps.append(competitor)

                elif self.last10_smallset(self.full_log[competitor]):
                    smallset.append(competitor)

        for opp_list in [neverbid, pk_known, larper_known, large_skippers, const_diff, large_jumps, smallset]:
            reportOppTeam.extend(opp_list)

        reportOppTeam = list(set(reportOppTeam))

        if neverbid:
            self.engine.print("neverbidder detected: " + str(neverbid))
        if pk_known:
            self.engine.print("larperknown detected: " + str(pk_known))
        if larper_known:
            self.engine.print("larperknown detected: " + str(larper_known))
        if large_skippers:
            self.engine.print("first10_roundSkipper detected: " + str(large_skippers))
        if const_diff:
            self.engine.print("last10_const_diff detected: " + str(const_diff))
        if large_jumps:
            self.engine.print("largejump detected: " + str(large_jumps))
        if smallset:
            self.engine.print("last10_smallset detected: " + str(smallset))

        self.engine.reportTeams(reportOwnTeam, reportOppTeam, known_val_bots)

        # print(self.bid_diff_log)
        # print("own: " + str(reportOwnTeam))
        # print("self: " + str(self.index))
        # print("big skippers: " + str(self.enemy_skippers))

        # variable resets
        del self.trueValue
        del self.howMuch_log
        del self.known_bid_ally
        del self.other_allies
        del self.bid_index

        # for key in self.full_log.keys():
        #     print(str(key) + ": " + str(self.full_log[key][:10]))

        self.last_bid_log = dict()
        self.full_log = dict()
        self.enemy_skippers = []
        self.whoMadeBid_log = []
        self.turn_no = 0
        self.long_bids = False
        pass

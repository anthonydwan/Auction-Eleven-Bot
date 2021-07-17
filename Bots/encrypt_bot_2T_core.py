"""
Change phase 2 small bid behaviour
check instakill vs not outbid-self behaviour
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
        return curr.next


###########################################################

class CompetitorInstance():
    def __init__(self):
        # initialize personal variables
        self.last_bid_log = dict()

        self.bids = [9, 11, 16]
        self.true_val_bids = [9, 10, 13]
        self.set_values = set(self.bids)
        self.true_set_values = set(self.true_val_bids)
        self.full_log = dict()
        self.NPC_prob = dict()
        self.enemy_skippers = []
        self.howMuch_log = [1]
        self.round = 0

        # buffer is needed to make sure it does not go negative
        self.bid_buffer = 20

        pass

    def onGameStart(self, engine, gameParameters):
        # engine: an instance of the game engine with functions as outlined in the documentation.
        self.engine = engine
        # gameParameters: A dictionary containing a variety of game parameters
        self.gameParameters = gameParameters
        self.numplayers = self.gameParameters["numPlayers"]
        self.mean_val = self.gameParameters["meanTrueValue"]
        self.sd_val = self.gameParameters["stddevTrueValue"]
        self.phase = self.gameParameters["phase"]
        print("bid_order: " + str(self.gameParameters["bidOrder"]))
        self.private_key = (int(self.engine.time.strftime("%M")) ** 2 + 29) % 7 + int(
            self.engine.time.strftime("%H")) ** 2 % 11 + 10

    def onAuctionStart(self, index, trueValue):
        # index is the current player's index, that usually stays put from game to game
        # trueValue is -1 if this bot doesn't know the true value

        self.rotation = CircularLinkedList()
        for i in range(self.numplayers):
            self.rotation.append(i)
        self.whoMadeBid_log = []

        if trueValue == -1:
            self.mybot_trueValue = self.mean_val - self.sd_val - 100
        else:
            self.mybot_trueValue = trueValue

        self.index = index
        print(f"I'm BOT: {self.index}")
        self.turn = 0
        self.full_log = dict()
        self.bid_num_log = dict()
        for k in range(self.numplayers):
            self.full_log[k] = []
            self.bid_num_log[k] = []

        self.curr_price = 1
        self.bid_num = 0

        if len(self.whoMadeBid_log) == 0:
            # initialise starting player
            self.bid_index = self.rotation.find(self.gameParameters["bidOrder"][self.round])

        pass

    def onBidMade(self, whoMadeBid, howMuch):
        # whoMadeBid is the index of the player that made the bid
        # howMuch is the amount that the bid was

        if self.bid_index.val != whoMadeBid:
            while self.bid_index.val != whoMadeBid:
                self.full_log[self.bid_index.val].append("skip")
                self.bid_index = self.bid_index.next

        # logging last bid
        self.full_log[whoMadeBid].append(howMuch - self.curr_price)
        self.curr_price = howMuch
        self.bid_index = self.bid_index.next

        # logging who made last bid (list)
        if len(self.whoMadeBid_log) >= 5:
            self.whoMadeBid_log.pop(0)
            self.whoMadeBid_log.append(whoMadeBid)
        else:
            self.whoMadeBid_log.append(whoMadeBid)

        pass

    ###############################################################################################################
    # ally detection
    ###############################################################################################################
    def modifier(self, player_index):
        output = (17 * player_index ** 2 + 19 + 13 * self.round ** 2) % 23 + 5
        return output

    def detect_ally_trueVal(self, own_index, own_trueVal, phase):
        # identifying allys and true bots:
        self.ally_trueValue[own_index] = own_trueVal
        Counter = {trueVals: sum(value == trueVals for value in self.ally_trueValue.values()) for trueVals in
                   self.ally_trueValue.values()}
        print("Counter: " + str(Counter))
        self.actual_trueValue = 0
        if phase == "phase_1":
            # only one ally has the trueValue
            self.actual_trueValue = list(Counter.keys())[list(Counter.values()).index(1)]
            self.known_ally = list(self.ally_trueValue.keys())[
                list(self.ally_trueValue.values()).index(self.actual_trueValue)]
        elif phase == "phase_2":
            # two allies has the trueValue
            self.actual_trueValue = list(Counter.keys())[list(Counter.values()).index(2)]
            fake_val = list(Counter.keys())[list(Counter.values()).index(1)]
            self.known_ally = list(self.ally_trueValue.keys())[
                list(self.ally_trueValue.values()).index(fake_val)]

        return self.actual_trueValue, self.known_ally

    #################################################################################################################
    # bidding behaviours
    #################################################################################################################
    def make_small_bid(self, lastBid):
        if lastBid + 8 <= self.actual_trueValue:
            if self.phase == "phase_1":
                bid = lastBid + 8 + self.engine.random.randint(0, 16)
                bid = bid if bid <= self.actual_trueValue else self.actual_trueValue - 7
            elif self.phase == "phase_2": #NTS: CHANGE
                bid = lastBid + 8 + self.engine.random.randint(0, 16)
                bid = bid if bid <= self.actual_trueValue else self.actual_trueValue - 7
            self.engine.makeBid(bid)

    def make_random_bid(self,lastBid, from_range, to_range):
        if lastBid + 8 <= self.actual_trueValue:
            if self.phase == "phase_1":
                bid = lastBid + 8 + self.engine.random.randint(from_range, to_range)
                # if random_bid is
                bid = bid if bid <= self.actual_trueValue else self.actual_trueValue - 7
            elif self.phase == "phase_2": #NTS: CHANGE
                bid = lastBid + 8 + self.engine.random.randint(from_range, to_range)
                bid = bid if bid <= self.actual_trueValue else self.actual_trueValue - 7
            self.engine.makeBid(bid)

    def instakill(self, lastBid):
        if lastBid + 8 <= self.actual_trueValue:
            # phase 1
            if self.phase == "phase_1":
                if self.known_ally != self.index:
                    bid = max(self.actual_trueValue - 7, lastBid + 8)
                    self.engine.makeBid(bid)
                else:  # normal bid
                    self.make_small_bid(lastBid)
            # phase 2
            elif self.phase == "phase_2":
                if self.known_ally == self.index:
                    bid = max(self.actual_trueValue - 7, lastBid + 8)
                    self.engine.makeBid(bid)
                else:  # normal bid
                    self.make_small_bid(lastBid)
        else:
            pass


    #####################################################################################################################

    def onMyTurn(self, lastBid):
        # lastBid is the last bid that was made
        if self.turn == 0:

            if self.mybot_trueValue > 9999:
                trueValue_part1_msg = int(str(self.mybot_trueValue)[:3])
            else:
                trueValue_part1_msg = int(str(self.mybot_trueValue)[:2])
            self.engine.makeBid(
                lastBid - self.private_key + 8 + self.bid_buffer + trueValue_part1_msg + self.modifier(self.index)
            )

        elif self.turn == 1:

            # finding all the allies that has the same output accounting for the distractions
            # analysing msg1 from round 0:
            self.ally_msg1 = {
                ally: self.full_log[ally][0] - 8 - self.bid_buffer + self.private_key - self.modifier(ally) for
                ally in self.full_log.keys() if
                # ally is not itself
                ally != self.index and
                # there must have been already bid
                self.full_log[ally] and
                # there must not have skipped
                self.full_log[ally][0] != "skip" and
                # range value digits must be within mean+/-sd range
                self.engine.math.floor((self.mean_val - self.sd_val) / 100) - 1
                <= (self.full_log[ally][0] - 8 - self.bid_buffer + self.private_key - self.modifier(ally))
                <= int(self.engine.math.floor((self.mean_val + self.sd_val) / 100))}
            trueValue_part2_msg = int(str(self.mybot_trueValue)[-2:])
            self.engine.makeBid(
                lastBid + self.private_key + 8 + self.bid_buffer + trueValue_part2_msg - self.modifier(self.index)
            )

            # re-calibrate ally list in case of failure
            self.allies = [ally for ally in self.ally_msg1.keys()]

        elif self.turn == 2:
            # analysing msg2 from round 1:
            self.ally_trueValue = dict()
            for ally in self.allies:
                if len(self.full_log[ally]) > 1 and self.full_log[ally][1] != "skip":
                    secret_val = (self.full_log[ally][1] - 8 - self.bid_buffer - self.private_key + self.modifier(ally))
                    if 0 <= secret_val <= 99:
                        if secret_val < 10:
                            part2_val = "0" + str(secret_val)
                        else:
                            part2_val = str(secret_val)
                        trueVal = int(str(self.ally_msg1[ally]) + part2_val)
                        self.ally_trueValue[ally] = trueVal

            # if self.gameParameters["phase"] == "phase_1":

            # re-calibrate ally list in case of failure
            self.allies = [ally for ally in self.ally_trueValue.keys()]

            # in the case where successfully find allies in 2 turns
            if len(self.allies) == 2:
                self.actual_trueValue, self.known_ally = self.detect_ally_trueVal(own_index=self.index,
                                                                                  own_trueVal=self.mybot_trueValue,
                                                                                  phase=self.phase)

                #####################################################
                # instakill mode (for end of competition)
                """
                at the end of the competition:
                activate instakill immediately
                """
                # self.instakill(lastBid)
                #####################################################
                # normal mode (before end of competition)
                self.make_random_bid(lastBid,0, 80)


            # need to make a third msg to identify allies
            else:
                self.engine.makeBid(lastBid + 9 + self.modifier(self.index))
                pass

        elif self.turn == 3:
            # re-calibrate ally list in case of failure (there may be more than 2) - this should be consistent across
            # all 3 bots - then we use turn 3 to remove the final bot.
            if len(self.allies) > 2:
                self.allies = [ally for ally in self.ally_trueValue.keys() if
                               # not empty
                               len(self.full_log[ally]) > 2 and
                               # not skip
                               self.full_log[ally][2] != "skip" and
                               # same key value
                               self.full_log[ally][2] - self.modifier(ally) == self.full_log[self.index][
                                   2] - self.modifier(self.index)]
                non_ally = [key for key in self.ally_trueValue.keys() if key not in self.allies]
                for competitor in non_ally:
                    self.ally_trueValue.pop(competitor, None)
                    print("removed: " + str(competitor))
                self.actual_trueValue, self.known_ally = self.detect_ally_trueVal(own_index=self.index,
                                                                                  own_trueVal=self.mybot_trueValue,
                                                                                  phase=self.phase)



                #####################################################
                # instakill mode (for end of competition)
                """
                at the end of the competition:
                activate instakill immediately here
                """
                # self.instakill(lastBid)
                #####################################################
                # normal mode (before end of competition)
                self.make_random_bid(lastBid,0, 80)
                #####################################################

            # already found values in turn 2
            else:
                #####################################################
                # instakill mode (for end of competition) - note, at the en
                """
                at the end of the competition:
                activate instakill immediately
                NTS: theoretically should already be initiated in turn 2 and no need in turn 3
                """
                # self.instakill(lastBid)
                #####################################################
                # normal mode (before end of competition)
                self.make_random_bid(lastBid,0, 80)
                pass

        # post turn 3
        else:
            pr = 12*self.turn
            if lastBid < self.actual_trueValue - 1000:
                if self.engine.random.randint(0,100) > pr:
                    self.instakill(lastBid)
                else:
                    self.make_small_bid(lastBid)
            elif self.actual_trueValue - 1500 < lastBid < self.actual_trueValue:
                self.instakill(lastBid)

        self.turn += 1
        pass

    def onAuctionEnd(self):
        # Now is the time to report team members, or do any cleanup.
        self.round += 1

        self.total_allies = self.allies
        self.total_allies.append(self.index)
        print(self.total_allies)
        print(self.gameParameters["phase"] + str(self.ally_trueValue))
        print(self.actual_trueValue)
        if self.phase == "phase_1":
            print("real trueVal ally: " + str(self.known_ally))
        else:
            print("fake trueVal ally: " + str(self.known_ally))
        avail_positions = [i for i in range(self.numplayers) if i not in self.total_allies]
        self.engine.swapTo(avail_positions[self.engine.random.randint(0, self.numplayers - 1 - len(self.total_allies))])

        self.full_log = dict()
        self.whoMadeBid_log = []

        pass

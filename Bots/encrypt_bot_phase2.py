"""
to be done
    save enemies in phase 1 and its mechanics



    reltyz - very fast in round 1 (since fixed positions)
    need to overhaul detecting algorithms
    Change phase 2 small bid behaviour



    phase1
        check christie
        check one
        check x-axis
        check benchmark gamma
        check instakill vs not outbid-self behaviour,
        check carl, deedbeef
        check edison

        check ope nbookexams
        check thewrongjames
        check cupheadbuddies
    phase2
        check detect NPCbots for phase 2
        x-axis
        christie
        roshvenk



    think about phase 2 - fake_known getting detected (think whether it is a good strat when everyone can bid that price)


    integrate better the sly_report + detection

    pk normal and larper_known, christie known also 4 value clashes


    implement enemy detection at earlier stage of the game*

    ogresunited - undetected
    reltyz - undetected
    x_axis - undetected
    SmashBros - undetected

    note - Kaito (new) 14 July - >200, >200, <20, >200 (need to check for more confirmation for the range of values)
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
        self.full_log = dict()
        self.NPC_prob = dict()
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
        self.private_key = (int(self.engine.time.strftime("%M")) ** 2 + 29) % 7 + int(
            self.engine.time.strftime("%H")) ** 2 % 11 + 10
        self.reportOppTeam = []
        
    def onAuctionStart(self, index, trueValue):
        # index is the current player's index, that usually stays put from game to game
        # trueValue is -1 if this bot doesn't know the true value

        self.rotation = CircularLinkedList()
        for i in range(self.numplayers):
            self.rotation.append(i)

        self.whoMadeBid_log = []

        if trueValue == -1:
            self.mybot_trueValue = -1
        else:
            self.mybot_trueValue = trueValue - (self.mean_val - self.sd_val)

        self.index = index

        # initalising full log and bid prob
        self.turn = 0
        self.full_log = dict()
        for k in range(self.numplayers):
            self.full_log[k] = []
            self.NPC_prob[k] = 0.25
            self.last_bid_log[k] = []
        self.curr_price = 1
        self.bid_num = 0

        if len(self.whoMadeBid_log) == 0:
            # initialise starting player
            self.bid_index = self.rotation.find(self.gameParameters["bidOrder"][self.round])

        pass

    def onBidMade(self, whoMadeBid, howMuch):
        # whoMadeBid is the index of the player that made the bid
        # howMuch is the amount that the bid was

        #########################################
        # full bid log
        #########################################

        if self.bid_index.val != whoMadeBid:
            while self.bid_index.val != whoMadeBid:
                self.full_log[self.bid_index.val].append("skip")
                # the probability P(NPC|not bid) = P(not bid|NPC)*P(NPC) / [P(not bid|NPC)*P(NPC) + P(not-bid|N-NPC)*P(N-NPC)]
                prior = self.NPC_prob[self.bid_index.val]
                NNPC_bid = 0.9
                if self.howMuch_log[-1] < self.mean_val / 4:
                    pr = 0.64
                elif 3 / 4 * self.mean_val > self.howMuch_log[-1] > self.mean_val / 4:
                    pr = 0.16
                elif self.howMuch_log[-1] > 3 / 4:
                    pr = 0.04
                self.NPC_prob[self.bid_index.val] = (1 - pr) * prior / ((1 - pr) * prior + (1 - NNPC_bid) * (1 - prior))
                self.bid_index = self.bid_index.next

        # the probability P(NPC|bid) = P(bid|NPC)*P(NPC) / [P(bid|NPC)*P(NPC) + P(bid|N-NPC)*P(N-NPC)]
        prior = self.NPC_prob[whoMadeBid]
        NNPC_bid = 0.9
        if self.howMuch_log[-1] < self.mean_val / 4:
            pr = 0.64
        elif 3 / 4 * self.mean_val > self.howMuch_log[-1] > self.mean_val / 4:
            pr = 0.16
        elif self.howMuch_log[-1] > 3 / 4:
            pr = 0.04
        self.NPC_prob[whoMadeBid] = (pr * prior) / (pr * prior + NNPC_bid * (1 - prior))

        # logging last bid
        self.full_log[whoMadeBid].append(howMuch - self.curr_price)
        self.curr_price = howMuch
        self.bid_index = self.bid_index.next

        #######################################

        # logging who made last bid (list)
        if len(self.whoMadeBid_log) >= 5:
            self.whoMadeBid_log.pop(0)
            self.whoMadeBid_log.append(whoMadeBid)
        else:
            self.whoMadeBid_log.append(whoMadeBid)

        # logging queue of last few bids
        if len(self.howMuch_log) >= 3:
            self.howMuch_log.pop(0)
            self.howMuch_log.append(howMuch)
        else:
            self.howMuch_log.append(howMuch)

        # logging bots last bids
        if len(self.last_bid_log[whoMadeBid]) >= 10:
            self.last_bid_log[whoMadeBid].pop(0)
            self.last_bid_log[whoMadeBid].append(howMuch)
        else:
            self.last_bid_log[whoMadeBid].append(howMuch)
        pass

    ###############################################################################################################
    # ally detection
    ###############################################################################################################
    def modifier(self, player_index):
        output = (17 * player_index ** 2 + 19 + 13 * self.round ** 2) % 23 + 5
        return output

    def detect_ally_trueVal(self, own_index, own_trueVal, phase):
        # identifying allys and true bots:
        self.ally_trueValue[own_index] = own_trueVal + self.mean_val - self.sd_val
        Counter = {trueVals: sum(value == trueVals for value in self.ally_trueValue.values()) for trueVals in
                   self.ally_trueValue.values()}
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

    def bid_limit(self):
        """return bid limit for each bot
        depends on phase and whether the bot knows true value or not"""
        if self.phase == "phase_1":
            if self.known_ally != self.index:
                return self.actual_trueValue
            elif self.known_ally == self.index:
                return self.actual_trueValue - 50
        elif self.phase == "phase_2":
            if self.known_ally == self.index:
                return self.actual_trueValue
            elif self.known_ally != self.index:
                return self.actual_trueValue - 50

    def bid_gate(self, lastBid):
        """ whether minimum bid is within bid limit"""
        return lastBid + 8 <= self.bid_limit()

    def close_to_trueValue(self, lastBid, bid):
        """whether the bid amount stays within the bid limit, otherwise bid at bid limit"""
        max_limit = self.bid_limit()
        if bid <= max_limit:
            return bid
        elif max_limit - 7 >= lastBid + 8:
            bid = max_limit - 7
        else:
            bid = lastBid + 8
        return bid

    def make_small_bid(self, lastBid):
        """make a bid amount that is in a very low range"""
        if self.bid_gate(lastBid):
            if self.phase == "phase_1":
                bid = lastBid + 8 + self.engine.random.randint(0, 16)
                bid = self.close_to_trueValue(lastBid, bid)
            elif self.phase == "phase_2":  # NTS: CHANGE
                bid = lastBid + 8 + self.engine.random.randint(0, 20)
                bid = self.close_to_trueValue(lastBid, bid)
            self.engine.makeBid(bid)
        else:
            pass

    def make_random_bid(self, lastBid, from_range, to_range):
        """make a bid amount within the range randomly"""
        if self.bid_gate(lastBid):
            bid = lastBid + 8 + self.engine.random.randint(from_range, to_range)
            # if random_bid is close
            bid = self.close_to_trueValue(lastBid, bid)
            self.engine.makeBid(bid)

    def make_instakill_bid(self, lastBid):
        """make an instakill bid if possible"""
        if self.bid_gate(lastBid):
            # phase 1
            if self.phase == "phase_1":
                # case 1: not known_ally and go for the kill
                if self.known_ally != self.index:
                    maxbid = max(self.actual_trueValue - 7, lastBid + 8)
                    self.engine.makeBid(maxbid)
                # case 2: known_ally, at most bid for trueVal - 50
                elif self.known_ally == self.index:
                    self.make_small_bid(lastBid=lastBid)
            # phase 2
            elif self.phase == "phase_2":
                # case 1: fake_val ally go for the kill
                if self.known_ally == self.index:
                    # add randomness to hide from other bots
                    maxbid = max(self.actual_trueValue - self.engine.random.randint(4, 7), lastBid + 8)
                    self.engine.makeBid(maxbid)
                # case 2: know trueVal ally, at most bid for trueVal - 50
                elif self.known_ally != self.index:  # normal bid
                    self.make_small_bid(lastBid=lastBid)
        else:
            pass

    #####################################################################################################################

    def onMyTurn(self, lastBid):
        # print(f"BOT {self.index}")
        # print(f"this is turn {self.turn}")
        # lastBid is the last bid that was made
        if self.turn == 0:
            if self.mybot_trueValue == -1:
                trueValue_part1_msg = 0
            else:
                trueValue_part1_msg = self.engine.math.floor(self.mybot_trueValue / 100)
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
                # range value digits must be within 0/2sd range
                0 <= (self.full_log[ally][0] - 8 - self.bid_buffer + self.private_key - self.modifier(ally))
                <= self.engine.math.floor((2 * self.sd_val) / 100)}

            trueValue_part2_msg = int(str(self.mybot_trueValue)[-2:])
            self.engine.makeBid(
                lastBid + self.private_key + 8 + self.bid_buffer + trueValue_part2_msg - self.modifier(self.index)
            )

            # find team's allies
            self.allies = [ally for ally in self.ally_msg1.keys()]


        elif self.turn == 2:
            # analysing msg2 from round 1:
            self.ally_trueValue = dict()
            for ally in self.allies:
                if len(self.full_log[ally]) > 1 and self.full_log[ally][1] != "skip":
                    secret_val = (self.full_log[ally][1] - 8 - self.bid_buffer - self.private_key + self.modifier(ally))
                    if -1 <= secret_val <= 99:
                        if 0 <= secret_val < 10:
                            part2_val = "0" + str(secret_val)
                        else:
                            part2_val = str(secret_val)
                        if secret_val == -1 and self.ally_msg1[ally] == 0:
                            trueVal = secret_val
                            self.ally_trueValue[ally] = trueVal + self.mean_val - self.sd_val
                        elif secret_val > -1:
                            trueVal = int(str(self.ally_msg1[ally]) + part2_val)
                            self.ally_trueValue[ally] = trueVal + self.mean_val - self.sd_val
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
                # self.make_instakill_bid(lastBid)
                #####################################################
                # normal mode (before end of competition)
                # preventing outbidding from self
                if self.whoMadeBid_log[-1] not in self.allies:
                    self.make_random_bid(lastBid, 0, 80)

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

                self.actual_trueValue, self.known_ally = self.detect_ally_trueVal(own_index=self.index,
                                                                                  own_trueVal=self.mybot_trueValue,
                                                                                  phase=self.phase)

                #####################################################
                # instakill mode (for end of competition)
                """
                at the end of the competition:
                activate instakill immediately here
                """
                # self.make_instakill_bid(lastBid)
                #####################################################
                # normal mode (before end of competition)
                # preventing outbidding from self
                if self.whoMadeBid_log[-1] not in self.allies or self.engine.random.randint(0, 100) > 66:
                    self.make_random_bid(lastBid, 0, 80)

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
                # self.make_instakill_bid(lastBid)
                #####################################################
                # normal mode (before end of competition)
                # preventing outbidding from self
                if self.whoMadeBid_log[-1] not in self.allies or self.engine.random.randint(0, 100) > 66:
                    self.make_random_bid(lastBid, 0, 50)
                pass

        # post turn 3
        else:
            pr = 12 * self.turn
            if lastBid < self.actual_trueValue - 2000:
                # prevent outbidding from self
                if self.whoMadeBid_log[-1] not in self.allies or self.engine.random.randint(0, 100) > 66:
                    if self.engine.random.randint(0, 100) > pr:
                        self.make_instakill_bid(lastBid)
                    else:
                        self.make_small_bid(lastBid)
            elif self.actual_trueValue - 2000 < lastBid < self.actual_trueValue:
                self.make_instakill_bid(lastBid)

        self.turn += 1
        pass

    ###################################################################################
    # enemy detection algorithms
    ####################################################################################

    def one_unknown(self, ls):
        if len(ls) >= 6:
            return ls[:6] == [10, 16, 16, 16, 16, 16]

    def one_known(self, ls):
        if len(ls) >= 6:
            if ls[0] != 10:
                return False
            for val in ls[1:6]:
                if val == "skip" or val < 16:
                    return False
            return True

    def V_Rao_known(self, ls):
        if len(ls) >= 4:
            if len(set(ls[:3])) == 1 and set(ls[:4]) != {"skip"}:
                if ls[3] != "skip" and ls[3] > 100:
                    return True
        return False

    def christie_known(self, ls, competitor):
        #     # larper votes higher than NPC
        if self.largeJumps(ls):
            # four bids and skip rest
            if len(ls) >= 8:
                for val in ls[0:4]:
                    if val == "skip":
                        return False
                if set(ls[4:-1]) != {8}:
                    return False
                if self.last_bid_log[competitor][-1] != self.actual_trueValue - 57:
                    return False
                return True
            elif len(ls) >= 4:
                for val in ls[0:4]:
                    if val == "skip":
                        return False
                if self.last_bid_log[self.whoMadeBid_log[-1]] == self.actual_trueValue - 7:
                    return True
        return False

    # def larper_known(self, ls):
    #     #     # larper votes higher than NPC
    #     if self.largeJumps(ls):
    #         # four bids and skip rest
    #         if len(ls) >= 8:
    #             for val in ls[0:4]:
    #                 if val == "skip":
    #                     return False
    #             # prevent clash with V_Rao
    #             if set(ls[0:4]) == {79}:
    #                 return False
    #             for val in ls[4:min(len(ls), 10)]:
    #                 if val != "skip":
    #                     return False
    #             return True
    #         elif len(ls) >= 4:
    #             # prevent clash with V_Rao
    #             if set(ls[0:4]) == {79}:
    #                 return False
    #             for val in ls[0:4]:
    #                 if val == "skip":
    #                     return False
    #             if self.trueValue is not None:
    #                 if self.last_bid_log[self.whoMadeBid_log[-1]] == self.trueValue - 7:
    #                     return True
    #     return False

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

    def sly_bid_known(self, competitor):
        return self.last_bid_log[competitor] == self.actual_trueValue - 7

    def large_skippers(self, ls):
        # if first 10 turns all skip
        if len(ls) >= 10:
            return set(ls[:10]) == {"skip"}

    def matchset(self, ls, set_val_param):
        ls = [val for val in ls if val != "skip"]
        if len(ls) > 10:
            return set_val_param == set(ls[:10])
        else:
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
        if self.phase == "phase_1":
            for value in ls:
                if value > self.gameParameters["minimumBid"] * (1 + 2):
                    return True
        elif self.phase == "phase_2":
            for value in ls:
                if value > self.gameParameters["minimumBid"] * 30:
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

    def sly_report(self, reportKnownBots):
        if len(reportKnownBots) < 3 and hasattr(self, "known_ally"):
            non_known_teambots = [ally for ally in self.total_allies if ally != self.known_ally]
            remaining_enemies = [enemy for enemy in self.reportOppTeam if enemy not in reportKnownBots]
            if self.index == sorted(non_known_teambots)[1] or self.index == self.known_ally:
                if self.phase == "phase_1":
                    # in phase 1, it is unlikely that sly_bid is made by a known Bot
                    for competitor in remaining_enemies:
                        if self.last_bid_log[competitor] == self.actual_trueValue - 7:
                            self.engine.print(f"sly bot (phase 1) kicked: {remaining_enemies.index(competitor)}")
                            remaining_enemies.pop(remaining_enemies.index(competitor))
                elif self.phase == "phase_2:":
                    # in phase 2, it is very likely that sly_bid is made by a fake_known Bot
                    for competitor in remaining_enemies:
                        if self.last_bid_log[competitor] == self.actual_trueValue - 7:
                            reportKnownBots.append(competitor)
                            self.engine.print(f"sly bot (phase 2) added: {remaining_enemies.index(competitor)}")
                            remaining_enemies.pop(remaining_enemies.index(competitor))
                # randomly pick some enemy bot as known
                while len(reportKnownBots) < 3 and len(remaining_enemies) > 0:
                    if len(remaining_enemies) == 1:
                        rand_index = 0
                    else:
                        rand_index = self.engine.random.randint(0, len(remaining_enemies) - 1)
                    reportKnownBots.append(remaining_enemies[rand_index])
                    self.engine.print("sly_report: " + str(remaining_enemies[rand_index]))
                    remaining_enemies.pop(rand_index)
        return reportKnownBots

    ##########################################################################

    def onAuctionEnd(self):
        # Now is the time to report team members, or do any cleanup.

        self.engine.print(f"ROUND {self.round}")
        self.round += 1

        if hasattr(self, "allies"):
            self.total_allies = self.allies
            self.total_allies.append(self.index)

        reportOwnTeam = []
        reportKnownBots = []

        if hasattr(self, "total_allies"):
            reportOwnTeam.extend(self.total_allies)
        if hasattr(self, "known_ally"):
            reportKnownBots.append(self.known_ally)

        competitors = [i for i in range(self.numplayers) if i not in reportOwnTeam]

        neverbid = []
        # deadbeef_known = []
        one_unknown = []
        V_Rao_known = []
        christie_known = []
        pk_known = []
        larper_known = []
        large_skippers = []
        const_diff = []
        large_jumps = []
        smallset = []
        low_NPC_prob = []
        same_bid_pattern = []
        same_starting_bid = []

        ############################################################################
        # detecting enemies together:
        ############################################################################
        shortest_rounds = min(len(self.full_log[competitor]) for competitor in competitors)

        for i in range(len(competitors)-1):
            for j in range(i+1, len(competitors)):
                if len(self.full_log[competitors[i]]) >=3 and len(self.full_log[competitors[j]])>=3:
                    if self.full_log[competitors[i]][:3] == self.full_log[competitors[j]][:3] and \
                            self.full_log[competitors[i]][:3].count("skip") <= 1: # at most one skip
                        same_bid_pattern.append(competitors[i])
                        same_bid_pattern.append(competitors[j])
                elif self.full_log[competitors[i]][0] == self.full_log[competitors[j]][0] and \
                        self.full_log[competitors[i]][0] != "skip" and \
                        self.full_log[competitors[i]][0] > 100:
                    same_starting_bid.append(competitors[i])
                    same_starting_bid.append(competitors[j])

        same_starting_bid = list(set(same_starting_bid))
        if len(same_starting_bid) ==3:
            self.reportOppTeam.extend(same_bid_pattern)
        same_bid_pattern = list(set(same_bid_pattern))
        self.reportOppTeam.extend(same_bid_pattern)

        ###########################################################################
        # detecting enemy one by one
        ###########################################################################
        for competitor in competitors:
            if competitor not in self.reportOppTeam:
                if self.neverbid(self.full_log[competitor]):
                    neverbid.append(competitor)

                # elif self.deadbeef_known(self.full_log[competitor]):
                #     deadbeef_known.append(competitor)
                #     known_val_bots.append(competitor)

                elif self.one_unknown(self.full_log[competitor]):
                    one_unknown.append(competitor)

                elif self.V_Rao_known(self.full_log[competitor]):
                    V_Rao_known.append(competitor)
                    reportKnownBots.append(competitor)

                elif self.pk_known(self.full_log[competitor]):
                    pk_known.append(competitor)
                    reportKnownBots.append(competitor)

                elif self.christie_known(self.full_log[competitor], competitor) and not pk_known:
                    # need to prevent clash of pk and christie_known for the timebeing
                    christie_known.append(competitor)
                    reportKnownBots.append(competitor)

                elif self.large_skippers(self.full_log[competitor]):
                    large_skippers.append(competitor)

                elif self.last10_consistent_diff(self.full_log[competitor]):
                    const_diff.append(competitor)

                elif self.largeJumps(self.full_log[competitor]):
                    large_jumps.append(competitor)

                elif self.last10_smallset(self.full_log[competitor]):
                    smallset.append(competitor)

                elif self.NPC_prob[competitor] < 1e-3:
                    low_NPC_prob.append(competitor)


        for opp_list in [neverbid, V_Rao_known,
                         one_unknown, christie_known,
                         pk_known,
                         large_skippers, const_diff, large_jumps,
                         smallset, low_NPC_prob]:
            self.reportOppTeam.extend(opp_list)

        self.reportOppTeam = list(set(self.reportOppTeam))

        if V_Rao_known:
            self.engine.print("V_Rao_known detected: " + str(V_Rao_known))
        if one_unknown:
            self.engine.print("one_unknown detected: " + str(one_unknown))
        if neverbid:
            self.engine.print("neverbidder detected: " + str(neverbid))
        if christie_known:
            self.engine.print("christie_known detected: " + str(christie_known))
        if pk_known:
            self.engine.print("pk_known detected: " + str(pk_known))
        if large_skippers:
            self.engine.print("first10_roundSkipper detected: " + str(large_skippers))
        if const_diff:
            self.engine.print("last10_const_diff detected: " + str(const_diff))
        if large_jumps:
            self.engine.print("largejump detected: " + str(large_jumps))
        if smallset:
            self.engine.print("last10_smallset detected: " + str(smallset))
        if same_starting_bid:
            self.engine.print(f"same first big bid pattern bots detected: {same_starting_bid}")
        if same_bid_pattern:
            self.engine.print(f"same first 3 bid pattern bots detected: {same_bid_pattern}")
        if low_NPC_prob:
            self.engine.print("non-NPC bid distrib detected: " + str(low_NPC_prob))

        # one of the bots to take random guesses at KnownEnemyBots
        reportKnownBots = self.sly_report(reportKnownBots)

        self.engine.reportTeams(reportOwnTeam, self.reportOppTeam, reportKnownBots)

        if self.phase == "phase_2":
            avail_positions = [i for i in range(self.numplayers) if i not in self.total_allies]
            self.engine.swapTo(
                avail_positions[self.engine.random.randint(0, self.numplayers - 1 - len(self.total_allies))])

        # variable resets
        if hasattr(self, "known_ally"):
            del self.known_ally
        del self.bid_index

        for key in self.full_log.keys():
            self.engine.print(str(key) + "'s NPC prob: " + str(self.NPC_prob[key]))

        self.howMuch_log = [1]
        self.NPC_prob = dict()
        self.last_bid_log = dict()
        self.full_log = dict()
        self.whoMadeBid_log = []

        if self.phase =="phase_2":
            self.reportOppTeam = []
        pass

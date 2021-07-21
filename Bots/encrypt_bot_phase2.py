"""
to be done
        phase_1 = self.allies should be saved
        instakill
            phase 1 - should leave some room for more points (but enough for a round)
            consider whether hiding is a better strategy for phase_1 since you will get compounded detection.
            phase 2 - fake_known getting detected (think whether it is a good strat when everyone can bid that price) -
            see how people are winning phase 2 for reference



    phase1
        roshvenk
        check christie (check phase1_christie_known)!!!!!!!!!!!!
        x_axis (not all of them)!!!!
        kenl_unknown
        sora
        soil

        soil consolidation
        check one
        check x-axis (missing one bot)
        check benchmark gamma
        relytz

        check carl,
        check edison
        check thewrongjames

    phase2
        soil
        TheLarpers
        x-axis IMPORTANT!!!!!!!!!!!!!!!
        thewrongjames
        check kenl -
        christie
        roshvenk

    ###################################################################################
    FOUND PATTERNS
    phase 1
        21/07 2:30PM: kenl known will bid 2 times and then just outbid, kenl_unknown only bid twice, the first two turns are random-ish number within 24
        21/07 2:30PM: One - have to bid 6 times, will not be a problem
        21/07 3PM: Christie (unknown) - random,random,skip,skip, 28
        21/07 3PM: Christie (known) - random,random,number,big_num, 28
        21/07 3PM: VRao - in auction 0, bids same number 3 times for all teambots, then for known bot will make 3 more bids to relay trueVal,
        after first auction it'll stop doing that

    phase 2
        note - Kaito (new) 14 July - >200, >200, <20, >200 (need to check for more confirmation for the range of values)
        20/07 12:00PM: Sora only bids after 3/4 skips (should not be a problem for later on)
        20/07 2:30PM: Christie - unknown bots bid 4 times, the second 2 times are the same, does not have to be large
        21/07 9:10PM: relytz may does not know the precise trueVal since it refused to bid, this may be important
        21/07 9:30PM: Larper also overbids



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
        self.NPC_skip_prob = dict()
        self.NPC_bid_amount_dist = dict()
        self.howMuch_log = [1]
        self.round = 0

        # buffer is needed to make sure it does not go negative
        self.bid_buffer = 20

        # this will log the first few bids of every player in every game
        self.super_log = dict()

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
        self.private_key = (int(self.engine.time.strftime("%M")) ** 2 + 29) % 11 + int(
            self.engine.time.strftime("%H")) ** 2 % 11 + 7

        for k in range(self.numplayers):
            self.super_log[k] = dict()

        self.reportOppTeam = []

        for k in range(self.numplayers):
            if self.phase == "phase_1":
                self.NPC_skip_prob[k] = 0.25
        pass

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
            if self.phase == "phase_2":
                self.NPC_skip_prob[k] = 0.25
            self.NPC_bid_amount_dist[k] = 0.25
            self.last_bid_log[k] = []
        self.curr_price = 1
        self.bid_num = 0

        if len(self.whoMadeBid_log) == 0:
            # initialise starting player
            self.bid_index = self.rotation.find(self.gameParameters["bidOrder"][self.round])

        pass

    ####################################################################################################################
    # bayes calculations
    ####################################################################################################################
    def NPC_bayes_bid_distributions(self, howMuch, whoMadeBid):
        """
        # Bayesian Probability of NPC bid amount distribution
        # the probability P(NPC|bid) = P(bid|NPC)*P(NPC) / [P(bid|NPC)*P(NPC) + P(bid|N-NPC)*P(N-NPC)]
        :param howMuch: int
        :param whoMadeBid: int
        :return: float
        """
        if self.phase == "phase_2":
            bid_dist_prior = self.NPC_bid_amount_dist[whoMadeBid]
            bid_diff = howMuch - self.curr_price
            if bid_diff in range(0, 60):
                prob = 1 - 0.34595
            elif bid_diff in range(60, 70):
                prob = 0.34595
            elif bid_diff in range(70, 80):
                prob = 0.26342
            elif bid_diff in range(80, 90):
                prob = 0.19532
            elif bid_diff in range(90, 100):
                prob = 0.14124
            elif bid_diff in range(100, 110):
                prob = 0.09816
            elif bid_diff in range(110, 120):
                prob = 0.06697
            elif bid_diff in range(120, 130):
                prob = 0.04452
            elif bid_diff in range(130, 140):
                prob = 0.02846
            else:
                prob = 0.01741

            # P(NPC | bid) = P(bid | NPC) * P(NPC) / [P(bid | NPC) * P(NPC) + P(bid | N - NPC) * P(N - NPC)]
            NNPC_bid_dist = 1 - prob
            self.NPC_bid_amount_dist[whoMadeBid] = (prob * bid_dist_prior) / (
                    prob * bid_dist_prior + NNPC_bid_dist * (1 - bid_dist_prior))
            return self.NPC_bid_amount_dist[whoMadeBid]
        return 1

    def NPC_bayes_bid_skip_probability(self, player, bidded):
        """
        # Bayesian Probability of NPC skipping

        :param player: int, index of the player
        :param bidded: boolean, False if skipped
        :return: float: probability of NPC skipping/bidding
        """
        prior = self.NPC_skip_prob[player]
        NNPC_bid = 0.9
        # this should be the previous bid in the self.howMuch_log, the current lastBid is updated later
        if self.howMuch_log[-1] < self.mean_val / 4:
            pr = 0.64
        elif 3 / 4 * self.mean_val > self.howMuch_log[-1] > self.mean_val / 4:
            pr = 0.16
        elif self.howMuch_log[-1] > 3 / 4:
            pr = 0.04
        if not bidded:
            # P(NPC|not bid) = P(not bid|NPC)*P(NPC) / [P(not bid|NPC)*P(NPC) + P(not-bid|N-NPC)*P(N-NPC)]
            self.NPC_skip_prob[player] = (1 - pr) * prior / ((1 - pr) * prior + (1 - NNPC_bid) * (1 - prior))
        else:
            # the probability P(NPC|bid) = P(bid|NPC)*P(NPC) / [P(bid|NPC)*P(NPC) + P(bid|N-NPC)*P(N-NPC)]
            self.NPC_skip_prob[player] = pr * prior / (pr * prior + NNPC_bid * (1 - prior))
        return self.NPC_skip_prob[player]

    ####################################################################################################################

    def onBidMade(self, whoMadeBid, howMuch):
        # whoMadeBid is the index of the player that made the bid
        # howMuch is the amount that the bid was

        #########################################
        # full bid log
        #########################################

        if self.bid_index.val != whoMadeBid:
            while self.bid_index.val != whoMadeBid:
                self.full_log[self.bid_index.val].append("skip")
                # bayesian update for bot skipping
                self.NPC_skip_prob[self.bid_index.val] = self.NPC_bayes_bid_skip_probability(player=self.bid_index.val,
                                                                                             bidded=False)
                self.bid_index = self.bid_index.next

        self.NPC_skip_prob[whoMadeBid] = self.NPC_bayes_bid_skip_probability(player=whoMadeBid, bidded=True)
        self.NPC_bid_amount_dist[whoMadeBid] = self.NPC_bayes_bid_distributions(howMuch, whoMadeBid)

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

    def decode_turn0_msg(self):
        if self.phase == "phase_1" and self.round > 0:
            ally_msg1 = {ally: self.full_log[ally][0] - 8 - self.bid_buffer + self.private_key - self.modifier(ally) for
                         ally in self.allies}
        else:
            ally_msg1 = {
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
        return ally_msg1

    def decode_turn1_msg(self):
        pass

    def detect_ally_trueVal(self, own_index, own_trueVal, phase):
        """identifying allies and true bots:"""
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

    def refine_ally_list(self, turn_no):
        new_ally_ls = [ally for ally in self.ally_trueValue.keys() if
                       # not empty
                       len(self.full_log[ally]) > turn_no and
                       # not skip
                       self.full_log[ally][turn_no] != "skip" and
                       # same key value
                       self.full_log[ally][turn_no] - self.modifier(ally) == self.full_log[self.index][
                           turn_no] - self.modifier(self.index)]
        return new_ally_ls

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
                bid = lastBid + 8 + self.engine.random.randint(0, 8)
                bid = self.close_to_trueValue(lastBid, bid)
            elif self.phase == "phase_2":
                bid = lastBid + 8 + self.engine.random.randint(0, 8)
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
                    maxbid = max(self.actual_trueValue - 7 - self.engine.random.randint(0, 500), lastBid + 8)
                    maxbid = self.close_to_trueValue(lastBid, maxbid)
                    self.engine.makeBid(maxbid)
                # case 2: known_ally, at most bid for trueVal - 50
                elif self.known_ally == self.index:
                    self.make_small_bid(lastBid=lastBid)
            # phase 2
            elif self.phase == "phase_2":
                # case 1: fake_val ally go for the kill
                if self.known_ally == self.index:
                    # add randomness to hide from other bots
                    maxbid = max(self.actual_trueValue - self.engine.random.randint(4, 77), lastBid + 8)
                    maxbid = self.close_to_trueValue(lastBid, maxbid)
                    self.engine.makeBid(maxbid)
                # case 2: know trueVal ally, at most bid for trueVal - 50
                elif self.known_ally != self.index:  # normal bid
                    maxbid = max(
                        self.actual_trueValue - self.engine.random.randint(50, 150) - self.engine.random.randint(4, 7),
                        lastBid + 8)
                    maxbid = self.close_to_trueValue(lastBid, maxbid)
                    self.engine.makeBid(maxbid)
        else:
            pass

    def post_turn3_bid(self, lastBid):
        pr = 12 * self.turn
        if lastBid < self.actual_trueValue - 2000:
            # prevent outbidding from self
            if self.whoMadeBid_log[-1] not in self.allies:
                if self.engine.random.randint(0, 100) > pr:
                    self.make_instakill_bid(lastBid)
                else:
                    self.make_small_bid(lastBid)
            else:
                pass
        elif self.actual_trueValue - 2000 < lastBid < self.actual_trueValue:
            if self.whoMadeBid_log[-1] not in self.allies:
                self.make_instakill_bid(lastBid)
        pass

    ########################################################################################################

    def onMyTurn(self, lastBid):
        # print(f"BOT {self.index}")
        # print(f"this is turn {self.turn}")
        # print(self.full_log)
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
            self.ally_msg1 = self.decode_turn0_msg()

            trueValue_part2_msg = int(str(self.mybot_trueValue)[-2:])
            self.engine.makeBid(
                lastBid + self.private_key + 8 + self.bid_buffer + trueValue_part2_msg - self.modifier(self.index)
            )

            # find team's allies
            if self.phase == "phase_1" and self.round > 0:
                pass
            else:
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
                self.allies = self.refine_ally_list(2)

                non_ally = [key for key in self.ally_trueValue.keys() if key not in self.allies]
                for competitor in non_ally:
                    self.ally_trueValue.pop(competitor, None)

                # in the case where successfully find allies after in 3rd turn
                if len(self.allies) == 2:
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
                # very unfortunate case needs another prompt
                else:
                    self.engine.makeBid(lastBid + 9 + self.modifier(self.index))

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
        elif self.turn == 4:
            # re-calibrate ally list in case of failure (there may be more than 2) - this should be consistent across
            # all 3 bots - then we use turn 4 to remove the final bot.
            if len(self.allies) > 2:
                self.allies = self.refine_ally_list(3)

                non_ally = [key for key in self.ally_trueValue.keys() if key not in self.allies]
                for competitor in non_ally:
                    self.ally_trueValue.pop(competitor, None)

                # allies must be found by 4th turn...
                self.actual_trueValue, self.known_ally = self.detect_ally_trueVal(own_index=self.index,
                                                                                  own_trueVal=self.mybot_trueValue,
                                                                                  phase=self.phase)

            self.post_turn3_bid(lastBid)
        # post turn 4
        else:
            self.post_turn3_bid(lastBid)
        self.turn += 1
        pass

    ###################################################################################
    # enemy detection algorithms
    ####################################################################################

    def VRao_known(self, competitor):
        if self.phase == "phase_1" and self.round == 0:
            ls = self.full_log[competitor]
            if len(ls) >= 6 and all(val != "skip" for val in ls[:6]) and len(set(ls[:3])) == 1 and len(set(ls[:6])) > 1:
                return True
        return False

    def kenl_phase1_known(self, ls):
        if self.phase == "phase_1":
            if len(ls) == 3 and "skip" not in ls[0:3] and \
                    all(val < 25 for val in ls[0:2]) and \
                    self.actual_trueValue - 8 <= ls[2] <= self.actual_trueValue:
                return True

    def repeated_bidding_pattern(self, dc):
        if self.phase == "phase_1":
            for i in range(len(dc.keys()) - 1):
                if len(dc[i]) < 3 or len(dc[i + 1]) < 3:
                    return False
                if dc[i][:2].count("skip") == 0 and dc[i][:2] == dc[i + 1][:2]:
                    return True
                if dc[i][:3].count("skip") <= 1 and dc[i][:3] == dc[i + 1][:3]:
                    return True
        return False

    def repeated_nonbidder(self, dc):
        if self.phase == "phase_1":
            for round in dc.keys():
                if len(dc[round]) < 3:
                    return False
                if set(dc[round][:4]) != {"skip"}:
                    return False
            return True
        return False

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

    def sora_phase2(self, ls):
        if self.phase == "phase_2":
            if len(ls) >= 6:
                if ls[:3] == ["skip", "skip", "skip"] and "skip" not in ls[3:6]:
                    return True
            elif len(ls) >= 7:
                if ls[:4] == ["skip", "skip", "skip", "skip"] and "skip" not in ls[4:7]:
                    return True
        return False

    def christie_phase1_unknown(self, ls):
        #  larper votes higher than NPC
        if self.phase == "phase_1":
            # four bids and skip rest
            if len(ls) >= 5:
                if "skip" not in ls[0:2] and all(val == "skip" for val in ls[3:5]) and ls[4] == 28:
                    return True
        return False

    def christie_known(self, ls):
        #  larper votes higher than NPC
        if self.phase == "phase_1":
            # four bids and skip rest
            if len(ls) >= 5:
                if "skip" not in ls[0:5] and ls[3] > 24 and ls[4] == 28:
                    return True
        elif self.phase == "phase_2":
            if len(ls) >= 6 and "skip" not in ls[0:6] and ls[3] > 100 and set(ls[4:6]) == {8}:
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

    def sly_bid_known(self, competitor):
        if hasattr(self, "actual_trueValue"):
            if len(self.last_bid_log[competitor]) > 0 and self.actual_trueValue - 7 <= self.last_bid_log[competitor][-1] <= self.actual_trueValue:
                return True
        return False

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
        if len(ls) > 6:
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
            if any(value > 240 for value in ls):
                return True
            if len(ls) >=4:
                if any(value > 145 for value in ls[:4]) or len([value for value in ls[:4] if value > 120]) > 1:
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

    def sly_report(self, reportKnownBots, exclusion_list):
        if len(reportKnownBots) < 3 and hasattr(self, "known_ally"):
            non_known_teambots = [ally for ally in self.total_allies if ally != self.known_ally]
            remaining_enemies = [enemy for enemy in self.reportOppTeam if enemy not in reportKnownBots and
                                 enemy not in exclusion_list]
            if self.index == sorted(non_known_teambots)[1] or self.index == self.known_ally:
                if self.phase == "phase_1":
                    # in phase 1, it is unlikely that sly_bid is made by a known Bot
                    for competitor in remaining_enemies:
                        if self.last_bid_log[competitor] and self.actual_trueValue <= self.last_bid_log[competitor][-1] <= self.actual_trueValue - 7:
                            self.engine.print(f"sly bot (phase 1) kicked: {remaining_enemies.index(competitor)}")
                            remaining_enemies.pop(remaining_enemies.index(competitor))
                elif self.phase == "phase_2:":
                    # in phase 2, it is very likely that sly_bid is made by a fake_known Bot
                    for competitor in remaining_enemies:
                        if self.last_bid_log[competitor] and 0 <= self.actual_trueValue - self.last_bid_log[competitor][-1] <= 7:
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

        for k in range(self.numplayers):
            self.super_log[k][self.round] = self.full_log[k][:min(5, len(self.full_log[k]))]

        if hasattr(self, "allies"):
            self.total_allies = self.allies.copy()
            self.total_allies.append(self.index)

        reportOwnTeam = []
        reportKnownBots = []

        if hasattr(self, "total_allies"):
            reportOwnTeam.extend(self.total_allies)
        if hasattr(self, "known_ally"):
            reportKnownBots.append(self.known_ally)

        competitors = [i for i in range(self.numplayers) if i not in reportOwnTeam]

        sly_bid_known = []
        kenl_phase1_known = []
        neverbid = []
        # deadbeef_known = []
        one_unknown = []
        VRao_known = []
        christie_known = []
        pk_known = []
        larper_known = []
        large_skippers = []
        const_diff = []
        large_jumps = []
        smallset = []
        same_bid_pattern = []
        same_large_1st_bid = []
        christie_phase1_unknown = []
        christie_phase2_same = []
        sora_phase2 = []
        repeated_nonbidder = []
        repeated_bidding_pattern = []
        low_NPC_skip_prob = []
        low_NPC_bid_amount_dist = []

        ############################################################################
        # detecting enemies together:
        ############################################################################
        shortest_rounds = min(len(self.full_log[competitor]) for competitor in competitors)

        for i in range(len(competitors) - 1):
            for j in range(i + 1, len(competitors)):
                if len(self.full_log[competitors[i]]) >= 4 and len(self.full_log[competitors[j]]) >= 4:
                    # christie_known in phase_2 (same values)
                    if self.full_log[competitors[i]][2:4] == self.full_log[competitors[j]][2:4] and \
                            "skip" not in self.full_log[competitors[i]][:4] and \
                            self.phase == "phase_2":
                        # if bid 4 times,
                        # the last two are the same in phase_2:
                        christie_phase2_same.append(competitors[i])
                        christie_phase2_same.append(competitors[j])
                if len(self.full_log[competitors[i]]) >= 3 and len(self.full_log[competitors[j]]) >= 3:
                    if self.full_log[competitors[i]][:3] == self.full_log[competitors[j]][:3] and \
                            self.full_log[competitors[i]][:3].count("skip") < 1:  # at most one skip
                        same_bid_pattern.append(competitors[i])
                        same_bid_pattern.append(competitors[j])
                if self.full_log[competitors[i]][0] == self.full_log[competitors[j]][0] and \
                        self.full_log[competitors[i]][0] != "skip" and \
                        self.full_log[competitors[i]][0] > 100:
                    # kenl bot, the first numbers are huge and the same (for the first 3)
                    same_large_1st_bid.append(competitors[i])
                    same_large_1st_bid.append(competitors[j])

        self.reportOppTeam.extend(christie_phase2_same)
        same_large_1st_bid = list(set(same_large_1st_bid))
        if len(same_large_1st_bid) == 3:
            self.reportOppTeam.extend(same_large_1st_bid)
        same_bid_pattern = list(set(same_bid_pattern))

        if len(same_bid_pattern) == 3:
            for bot in same_bid_pattern:
                if self.VRao_known(bot):
                    reportKnownBots.append(bot)
                    VRao_known.append(bot)
        self.reportOppTeam.extend(same_bid_pattern)

        ###########################################################################
        # detecting enemy one by one
        ###########################################################################
        for competitor in competitors:
            if self.neverbid(self.full_log[competitor]):
                neverbid.append(competitor)

            elif self.kenl_phase1_known(self.full_log[competitor]):
                kenl_phase1_known.append(competitor)
                reportKnownBots.append(competitor)

            elif self.one_unknown(self.full_log[competitor]):
                one_unknown.append(competitor)

            elif self.pk_known(self.full_log[competitor]):
                pk_known.append(competitor)
                reportKnownBots.append(competitor)

            elif self.sora_phase2(self.full_log[competitor]):
                sora_phase2.append(competitor)

            elif self.christie_phase1_unknown(self.full_log[competitor]):
                christie_phase1_unknown.append(competitor)

            elif self.christie_known(self.full_log[competitor]) and not pk_known:
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

            elif self.sly_bid_known(competitor):
                sly_bid_known.append(competitor)
                if self.phase == "phase_2":
                    reportKnownBots.append(competitor)

            # elif self.NPC_bid_amount_dist[competitor] < 0.001:
            #     low_NPC_bid_amount_dist.append(competitor)

            elif self.round == 1 and self.repeated_nonbidder(self.super_log[competitor]):
                repeated_nonbidder.append(competitor)

            elif self.round == 1 and self.repeated_bidding_pattern(self.super_log[competitor]):
                repeated_bidding_pattern.append(competitor)
        ###################################################################################
        for opp_list in [neverbid, VRao_known, one_unknown,
                         christie_known, pk_known, large_skippers,
                         const_diff, large_jumps, kenl_phase1_known,
                         sora_phase2, repeated_nonbidder, repeated_bidding_pattern,
                         smallset, christie_phase1_unknown, sly_bid_known]:
            self.reportOppTeam.extend(opp_list)

        self.reportOppTeam = list(set(self.reportOppTeam))
        #####################################################################################
        # finally do a low bid/skip prob:

        sorted_skip_prob = sorted([competitor for competitor in competitors if competitor not in self.reportOppTeam],
                                  key=lambda k: self.NPC_skip_prob[k])

        while len(self.reportOppTeam) < 6 and self.NPC_skip_prob[sorted_skip_prob[0]] < 0.005:
            low_NPC_skip_prob.append(sorted_skip_prob[0])
            sorted_skip_prob.pop(0)

        if self.phase == "phase_2":
            while len(self.reportOppTeam) < 6 and self.NPC_skip_prob[sorted_skip_prob[0]] < 0.0075:
                low_NPC_skip_prob.append(sorted_skip_prob[0])
                sorted_skip_prob.pop(0)

        self.reportOppTeam.extend(low_NPC_skip_prob)
        self.reportOppTeam = list(set(self.reportOppTeam))

        ###################################################################################

        if VRao_known:
            self.engine.print("VRao_known detected: " + str(VRao_known))
        if one_unknown:
            self.engine.print("one_unknown detected: " + str(one_unknown))
        if neverbid:
            self.engine.print("neverbidder detected: " + str(neverbid))
        if christie_known:
            self.engine.print("christie_known detected: " + str(christie_known))
        if kenl_phase1_known:
            self.engine.print("kenl_phase1_known detected: " + str(kenl_phase1_known))
        if pk_known:
            self.engine.print("pk_known detected: " + str(pk_known))
        if large_skippers:
            self.engine.print("first10_roundSkipper detected: " + str(large_skippers))
        if const_diff:
            self.engine.print("last10_const_diff detected: " + str(const_diff))
        if large_jumps:
            self.engine.print("largejump detected: " + str(large_jumps))
        if sora_phase2:
            self.engine.print("sora_phase2 detected: " + str(sora_phase2))
        if smallset:
            self.engine.print("last10_smallset detected: " + str(smallset))
        if christie_phase2_same:
            self.engine.print("christie_phase2_same detected: " + str(christie_phase2_same))
        if same_large_1st_bid:
            self.engine.print(f"same first big bid pattern bots detected: {same_large_1st_bid}")
        if same_bid_pattern:
            self.engine.print(f"same first 3 bid pattern bots detected: {same_bid_pattern}")
        if low_NPC_skip_prob:
            self.engine.print("non-NPC bid/skip detected: " + str(low_NPC_skip_prob))
        if low_NPC_bid_amount_dist:
            self.engine.print("non-NPC bid amount distrib detected: " + str(low_NPC_bid_amount_dist))
        if repeated_nonbidder:
            self.engine.print("repeated_nonbidder detected: " + str(repeated_nonbidder))
        if repeated_bidding_pattern:
            self.engine.print("repeated_bidding_pattern detected: " + str(repeated_bidding_pattern))
        if christie_phase1_unknown:
            self.engine.print("christie_phase1_unknown detected: " + str(christie_phase1_unknown))
        if sly_bid_known:
            self.engine.print(f"sly_bid_known detected: {sly_bid_known}")

        #########################################################################
        # exclusion list for sly_report
        #########################################################################

        exclusion_list = []
        if len(same_large_1st_bid) == 2 or len(same_large_1st_bid) == 4:
            exclusion_list.extend(same_large_1st_bid)
        if len(same_bid_pattern) == 2 or len(same_bid_pattern) == 4:
            exclusion_list.extend(same_bid_pattern)
        if len(set(christie_phase2_same)) ==2:
            exclusion_list.extend(christie_phase2_same)
        exclusion_list.extend(christie_phase1_unknown)
        if repeated_nonbidder:
            exclusion_list.extend(repeated_nonbidder)
        if self.phase == "phase_1" and sly_bid_known:
            exclusion_list.extend(sly_bid_known)
        exclusion_list = list(set(exclusion_list))
        if exclusion_list:
            self.engine.print(f"exclusion_list: {exclusion_list}")

        exclusion_list = list(set(exclusion_list))
        # one of the bots to take random guesses at KnownEnemyBots
        reportKnownBots = self.sly_report(reportKnownBots, exclusion_list)

        self.engine.reportTeams(reportOwnTeam, self.reportOppTeam, reportKnownBots)

        ###########################################################################

        if self.phase == "phase_2":
            avail_positions = [i for i in range(self.numplayers) if i not in self.total_allies]
            self.engine.swapTo(
                avail_positions[self.engine.random.randint(0, self.numplayers - 1 - len(self.total_allies))])

        # variable resets
        if hasattr(self, "known_ally"):
            del self.known_ally
        del self.bid_index

        for key in self.full_log.keys():
            self.engine.print(str(key) + "'s NPC prob: " + str(self.NPC_skip_prob[key]))

        if self.phase == "phase_2":
            for key in self.full_log.keys():
                self.engine.print(str(key) + "'s NPC bid_dist: " + str(self.NPC_bid_amount_dist[key]))

        self.round += 1

        self.howMuch_log = [1]
        if self.phase == "phase_2":
            self.NPC_skip_prob = dict()
        self.NPC_bid_amount_dist = dict()
        self.last_bid_log = dict()
        self.full_log = dict()
        self.whoMadeBid_log = []

        if self.phase == "phase_2":
            self.reportOppTeam = []
        pass

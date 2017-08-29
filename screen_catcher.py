class ScreenCatch(object):
    map_x_border = 33
    map_y_border = 17
    states_x_border = 36
    states_y_border = 17

    """
        Map:
        x range 0~32
        y range 0~16

        whole screen
        x max = 79
        (16, 8): @
    """
    def analyse_screen(self, sl, move_history):
        """
        move_history will be updated while any move was worked, the move will be checked whether it worked.
        :param sl:
        :param move_history:
        :return:
        """
        map_detail_dic = {}
        states_dic = {}
        game_input = {}

        for y in range(len(sl)):
            for x in range(len(sl[y])):
                if y < self.map_y_border and x < self.map_x_border:
                    # Map area
                    position = (x + move_history[0], y + move_history[1])
                    value = sl[y][x].encode('ascii')
                    map_detail_dic = self.__create_map_data(position, value, map_detail_dic)
                elif y < self.states_y_border and x > self.states_x_border:
                    # States area
                    states_dic[(x, y)] = sl[y][x].encode('ascii')
                elif y >= self.states_y_border:
                    # Game input area
                    game_input[(x, y)] = sl[y][x].encode('ascii')

        # map_detail_dic = self.__check_fogs(map_detail_dic)
        player_states_dic = self.__catch_states(states_dic)
        game_input_dic = self.__catch_game_input(game_input)

        """
            Check the time change, if time does not change, it means the move doesn't work.
        """
        # try:
        #     if time_previous != player_states_dic['Time']:
        #         # move_history = (move_history[0] + move_prepare[0], move_history[1] + move_prepare[1])
        #         # for position, data_list in map_detail_dic.items():
        #         #     real_position = (position[0] + move_history[0], position[1] - move_history[1])
        #         #     map_detail_dic_real_position[real_position] = data_list
        #         # map_detail_dic.clear()
        #         # map_detail_dic = map_detail_dic_real_position
        #         move_history = move_fix
        #         map_detail_dic = map_detail_dic_a
        #
        # except TypeError:
        #     pass

        return map_detail_dic, player_states_dic, game_input_dic

    @staticmethod
    def __create_map_data(position, value, map_dic):
        """
        Analyse map information here.
        :param map_dic:
        :param position: ex. (x, y)
        :param value: symbol, ex. #, ., ) etc.
        :return:the map data, dict type
        """
        can_pass_list = [".", "'", ")"]
        can_it_pass = False
        if value in can_pass_list:
            can_it_pass = True
        # map_dic[position] = [symbol, can pass?, fogs?]
        map_dic[position] = [value, can_it_pass, False]
        # fogs value will be checked later, this is a default value
        return map_dic

    @staticmethod
    def __check_fogs(map_dic):
        """
        No used now
        :param map_dic:
        :return:
        """
        nb_position_list = [(1, 0), (1, 1), (1, -1),
                            (0, 1), (0, -1),
                            (-1, 0), (-1, 1), (-1, -1)]
        for position, data_list in map_dic.items():
            if data_list[0] == ".":
                for nb_p in nb_position_list:
                    nb_position = (int(position[0]) + nb_p[0], int(position[1]) + nb_p[1])
                    is_fog = False
                    try:
                        nb_data_list = map_dic[nb_position]
                        if nb_data_list[0] == " ":
                            is_fog = True
                    except KeyError:
                        # If the nb_position(Key) is not in map_dic, it is a edge.
                        is_fog = True

                    if is_fog:
                        data_list = map_dic[position]
                        data_list[2] = True
                        map_dic[position] = data_list
                        break

                    # if 0 <= nb_position[0] <= 32 and 0 <= nb_position[1] <= 16:
                    #     nb_data_list = map_dic[nb_position]
                    #     # nb_data_list[0] = symbol
                    #     if nb_data_list[0] == " ":
                    #         data_list = map_dic[position]
                    #         data_list[2] = True
                    #         map_dic[position] = data_list
                    #         break
        return map_dic

    '''
        (x, y)
        Career: (37-78, 1)
        Health: (44-55, 2)
        Magic: (43-55, 3)
        AC: (40-55, 4)
        Str: (59-80, 4)
        EV: (40-55, 5)
        Int: (59-80, 5)
        SH: (40-55, 6)
        DEX: (59-80, 6)
        XL: (40-55, 7)
        Place: (61-80, 7)
        Gold: (42-55, 8)
        Time: (60-80, 8)
    '''

    def __catch_states(self, sd):
        check_word_health = self.__catch_keywords_by_range_x(sd, 37, 43, 2)
        check_word_magic = self.__catch_keywords_by_range_x(sd, 37, 42, 3)
        check_word_time = self.__catch_keywords_by_range_x(sd, 54, 59, 8)
        """
            These three words are used to check the screen can get the standard states. 
        """
        if check_word_health == 'Health' and check_word_magic == 'Magic' and check_word_time == 'Time':
            psd = {'Career': self.__catch_keywords_by_range_x(sd, 37, 78, 1),
                   'Health': self.__catch_keywords_by_range_x(sd, 44, 55, 2),
                   'Magic': self.__catch_keywords_by_range_x(sd, 43, 55, 3),
                   'AC': self.__catch_keywords_by_range_x(sd, 40, 55, 4),
                   'Str': self.__catch_keywords_by_range_x(sd, 59, 80, 4),
                   'EV': self.__catch_keywords_by_range_x(sd, 40, 55, 5),
                   'Int': self.__catch_keywords_by_range_x(sd, 59, 80, 5),
                   'SH': self.__catch_keywords_by_range_x(sd, 40, 55, 6),
                   'DEX': self.__catch_keywords_by_range_x(sd, 59, 80, 6),
                   'XL': self.__catch_keywords_by_range_x(sd, 40, 55, 7),
                   'Place': self.__catch_keywords_by_range_x(sd, 61, 80, 7),
                   'Gold': self.__catch_keywords_by_range_x(sd, 42, 55, 8),
                   'Time': self.__catch_keywords_by_range_x(sd, 60, 80, 8)}

            return psd
        else:
            return None

    def __catch_game_input(self, game_input):
        gid = {'Ginput1': self.__catch_keywords_by_range_x(game_input, 0, 80, 17),
               'Ginput2': self.__catch_keywords_by_range_x(game_input, 0, 80, 18),
               'Ginput3': self.__catch_keywords_by_range_x(game_input, 0, 80, 19),
               'Ginput4': self.__catch_keywords_by_range_x(game_input, 0, 80, 20),
               'Ginput5': self.__catch_keywords_by_range_x(game_input, 0, 80, 21),
               'Ginput6': self.__catch_keywords_by_range_x(game_input, 0, 80, 22)}
        return gid


    @staticmethod
    def __catch_keywords_by_range_x(dic, range_x1, range_x2, y):
        keyword = ""
        for x in range(range_x1, range_x2):
            keyword = keyword + dic[(x, y)]
        keyword = keyword.replace(' ', '')
        return keyword
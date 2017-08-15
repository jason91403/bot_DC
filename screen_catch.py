class ScreenCatch(object):

    """
    Map:
    x range 0~32
    y range 0~16

    whole screen
    x max = 79
    (16, 8): @

    """
    def analyse_screen(self, sl):
        map_detail_dic = {}
        states_dic = {}

        for y in range(len(sl)):
            for x in range(len(sl[y])):
                if y < 17 and x < 34:
                    # map_dic[(x, y)] = sl[y][x].encode('ascii')
                    map_detail_dic = self.__create_map_data((x, y), sl[y][x].encode('ascii'), map_detail_dic)
                elif x > 36:
                    states_dic[(x, y)] = sl[y][x].encode('ascii')
        # map_detail_dic = catch_map(map_dic)
        # Only after finishing map data, it can be checked fogs
        map_detail_dic = self.__check_fogs(map_detail_dic)
        player_states_dic = self.__catch_states(states_dic)

        return map_detail_dic, player_states_dic

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
        nb_position_list = [(1, 0), (1, 1), (1, -1),
                            (0, 1), (0, -1),
                            (-1, 0), (-1, 1), (-1, -1)]
        for position, data_list in map_dic.items():
            if data_list[0] == ".":
                for nb_p in nb_position_list:
                    nb_position = (int(position[0]) + nb_p[0], int(position[1]) + nb_p[1])
                    if 0 <= nb_position[0] <= 32 and 0 <= nb_position[1] <= 16:
                        nb_data_list = map_dic[nb_position]
                        # nb_data_list[0] = symbol
                        if nb_data_list[0] == " ":
                            data_list = map_dic[position]
                            data_list[2] = True
                            map_dic[position] = data_list
                            break
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
        Glod: (42-55, 8)
        Time: (60-80, 8)
    '''
    def __catch_states(self, sd):
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

    @staticmethod
    def __catch_keywords_by_range_x(dic, range_x1, range_x2, y):
        keyword = ""
        for x in range(range_x1, range_x2):
            keyword = keyword + dic[(x, y)]
        keyword = keyword.replace(' ', '')
        return keyword

class PathFinding(object):

    def path_finding(self, player_position, target_position, map_detail_dic):
        target_node_found, open_list, close_list = self.__a_star_search(player_position, target_position, map_detail_dic)
        move_list = []
        if target_node_found:
            track_back_list = self.__track_back_path(close_list, player_position, target_position)
            move_list = self.__transfer_to_move(track_back_list)
        return move_list

    def __a_star_search(self, player_position, target_position, map_detail_dic):
        node_now = (player_position, 0, None)
        open_list = []
        close_list = []
        target_node_found = False
        open_list.append(node_now)
        while open_list:
            node_now = open_list[0]
            if target_position == node_now[0]:
                target_node_found = True
                close_list.append(node_now)
                break
            else:
                close_list.append(node_now)
                open_list.remove(node_now)
                neighbors_list = self.__find_neighbors(node_now[0], map_detail_dic)
                for nb_node in neighbors_list:
                    if ((not self.__check_if_in_list(nb_node[0], open_list)) and
                            (not self.__check_if_in_list(nb_node[0], close_list))):
                        open_list.append((nb_node[0],
                                          self.__count_cost(nb_node[0], player_position, target_position),
                                          nb_node[1]))
                open_list.sort(key=lambda x: x[1])
        return target_node_found, open_list, close_list

    @staticmethod
    def __track_back_path(close_list, node_start, node_target):
        close_list_dic = {}
        for node in close_list:
            # key: position, value: parent
            close_list_dic[node[0]] = node[2]

        track_back_list = [node_target]
        node_parent = close_list_dic[node_target]
        while node_parent != node_start:
            # track_back_list.append(node_parent)
            track_back_list.insert(0, node_parent)
            node_parent = close_list_dic[node_parent]
        return track_back_list

    @staticmethod
    def __transfer_to_move(positions_list):
        player_position = (16, 8)
        move = None
        move_list = []
        # for test
        # move_dic = { (1, 0): 'R', (0, 1): 'U', (-1, 0): 'L', (0, -1): 'D',
        #              (1, 1): 'RU',(1, -1): 'RD', (-1, 1): 'LU', (-1, -1): 'LD'}
        move_dic = {(1, 0): chr(108), (0, 1): chr(107), (-1, 0): chr(104), (0, -1): chr(106),
                    (1, 1): chr(117), (1, -1): chr(110), (-1, 1): chr(121), (-1, -1): chr(98)}
        if positions_list:
            for i in range(len(positions_list)):
                key_position = (positions_list[i][0] - player_position[0],
                                player_position[1] - positions_list[i][1])
                if key_position in move_dic:
                    move_list.append(move_dic[key_position])
                    player_position = positions_list[i]
                else:
                    print "Error: def transfer_to_move: key_position not in move_dic."
                    print "  key_position: " + str(key_position)
                    break
        else:
            print "Error: def transfer_to_move: positions_list is empty."
        return move_list

    @staticmethod
    def __count_cost(node, start_node, target_node):
        g_score = abs(int(node[0]) - int(start_node[0])) + abs(int(node[1]) - int(start_node[1]))
        h_score = abs(int(node[0]) - int(target_node[0])) + abs(int(node[1]) - int(target_node[1]))
        f_score = g_score + h_score
        return f_score

    @staticmethod
    def __count_distance(node_1, node_2):
        dis = abs(int(node_1[0]) - int(node_2[0])) + abs(int(node_1[1]) - int(node_2[1]))
        return dis

    @staticmethod
    def __check_if_in_list(node_position, mlist):
        in_list = False
        for n in mlist:
            if node_position == n[0]:
                in_list = True
        return in_list

    @staticmethod
    def __find_neighbors(node_position, map_detail_dic):
        nb_list = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x == 0 and y == 0:
                    continue
                nb_position_x = int(node_position[0]) + x
                nb_position_y = int(node_position[1]) + y
                if 0 <= nb_position_x <= 32 and 0 <= nb_position_y <= 16:
                    nb = map_detail_dic[nb_position_x, nb_position_y]
                    if nb[1]:
                        nb_list.append(((nb_position_x, nb_position_y), node_position))
                        # (node_position, parent)
        return nb_list

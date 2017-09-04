import collections
import math


class Tools(object):

    def __init__(self):
        pass

    @staticmethod
    def get_distance(x_position, y_position):
        return math.sqrt(math.pow((x_position[0] - y_position[0]), 2) + math.pow((x_position[1] - y_position[1]), 2))

    @staticmethod
    def record_map_to_local_file(file_name, map_dic):
        pass
        # test_file = open(file_name, 'w')
        # line_dic = {}  # [[y_position, line_detail_list],...]
        # line_dic_p = {}
        # x_min = 0
        # map_dic = collections.OrderedDict(sorted(map_dic.items()))
        # for position, data_list in map_dic.items():
        #     x_position = position[0]
        #     if x_position < x_min:
        #         x_min = x_position
        #     y_position = position[1]
        #     if y_position not in line_dic:
        #         line_dic[y_position] = [[x_position, data_list[0]]]
        #     else:
        #         line_dic[y_position].append([x_position, data_list[0]])
        # # Sort by
        # line_dic = collections.OrderedDict(sorted(line_dic.items()))
        #
        # for y_position, data_list in line_dic.items():
        #     data_list = sorted(data_list, key=lambda x: x[0])  # Sort by x_position
        #     # First x_position from a line
        #     # print "x_min: " + str(x_min)
        #     # print "data_list[0][0]: " + str(data_list[0][0])
        #     while data_list[0][0] > x_min:
        #         data_list.insert(0, [data_list[0][0] - 1, " "])
        #     data_list = sorted(data_list, key=lambda x: x[0])  # Sort by x_position
        #     for position_with_value_list in data_list:
        #         if y_position not in line_dic_p:
        #             line_dic_p[y_position] = position_with_value_list[1]
        #         else:
        #             line_dic_p[y_position] = line_dic_p[y_position] + position_with_value_list[1]
        #
        #     line_dic_p = collections.OrderedDict(sorted(line_dic_p.items()))
        #
        # for line_num, line in line_dic_p.items():
        #     test_file.write(line + "\n")
        #
        # test_file.close()

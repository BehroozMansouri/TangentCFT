import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# Create data
def read_file_address(file_path):
    file = open(file_path)
    line = file.readline().strip("\n")
    data_points = {}
    while line:
        sections = line.split(",")
        file2 = open("/home/bm3302/FastText/Run_Result_9012/" + sections[1] + ".txt")
        vector = np.fromfile(file2, sep=" ")
        if sections[0] in data_points.keys():
            data_points[sections[0]].append(vector)
        else:
            lst = [vector]
            data_points[sections[0]] = lst
        line = file.readline().strip("\n")
    return data_points


def read_label(file_path):
    lst = []
    file = open(file_path)
    line = file.readline().strip("\n")
    while line:
        sections = line.split(",")
        lst.append(sections[1])
        line = file.readline().strip("\n")
    return lst


def draw_map(file_path):
    map = read_file_address(file_path)
    x = []
    y = []

    lst_colors = ["red", "blue", "green", "purple", "black", "silver", "cyan", "gold", "violet"]
    markers = ['o', '*', 'X', '^', 'D', 'h', 'd', 'v', 's']
    labels = ["Matrix", "Integral", "Series", "Limit", "Logarithm", "Trigonometric", "Set Theory", "Probability", "Derivative"]
    color = []
    marker = []
    max_x = -100
    min_x = 100
    max_y = -100
    min_y = 100

    for key in map.keys():
        for item in map[key]:
            x.append(item[0])
            if item[0] > max_x:
                max_x = item[0]
            elif item[0] < min_x:
                min_x = item[0]
            y.append(item[1])
            if item[1] > max_y:
                max_y = item[1]
            elif item[0] < min_y:
                min_y = item[0]
            color.append(lst_colors[int(key) - 1])
            marker.append(markers[(int(key))-1])

    x_range = max_x - min_x
    y_range = max_y - min_y

    x = (2 * (x - min_x) / x_range) - 1
    y = (2 * (y - min_y) / y_range) - 1
    legend_info = []
    for counter in range(0, len(lst_colors)):
        legend_info.append(Line2D([0], [0], color='w', label=labels[counter], markerfacecolor=lst_colors[counter],
                                  marker=markers[counter], markersize=8))

    fig, ax = plt.subplots()
    for key in map.keys():
        key = int(key)
        start = (key-1) * 20
        end = start + 20
        ax.scatter(x[start:end], y[start:end], c=color[start:end], marker=markers[key-1], alpha=0.9)

    ax.legend(handles=legend_info, loc='upper right', ncol=2, prop={'size': 8})
    plt.show()


def main():
    """
    A sample drawing tool, takes the directory of
    :return:
    """
    draw_map("formula_tsne")


if __name__ == '__main__':
    main()

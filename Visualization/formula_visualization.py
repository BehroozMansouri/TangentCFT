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


def draw_map(file_path, label_file_path):
    map = read_file_address(file_path)
    #labels2 = read_label(label_file_path)
    x = []
    y = []
    coulours = ["red", "blue", "green", "purple", "black", "silver", "cyan", "gold", "violet"]
    markers = ['o', '*','X', '^','D', 'h','d', 'v','s']
    labels = ["Matrix", "Integral", "Series", "Limit", "Logarithm", "Trigonometric", "Set Theory", "Probability", "Derivative"]
    color = []
    marker = []
    # labels = []
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
            color.append(coulours[int(key) - 1])
            marker.append(markers[(int(key))-1])

    x_range = max_x - min_x
    y_range = max_y - min_y
    marker = np.array(marker)
    # x = (x - min_x) / x_range
    # y = (y - min_y) / y_range

    x = (2 * (x - min_x) / x_range) - 1
    y = (2 * (y - min_y) / y_range) - 1
    legend_info = []
    for counter in range(0, len(coulours)):
        legend_info.append(Line2D([0], [0], color='w', label=labels[counter], markerfacecolor=coulours[counter],
                                  marker=markers[counter], markersize=8))

    fig, ax = plt.subplots()
    for key in map.keys():
        key = int(key)
        start = (key-1) * 20
        end = start + 20
        ax.scatter(x[start:end], y[start:end], c=color[start:end], marker=markers[key-1], alpha=0.9)

    ax.legend(handles=legend_info, loc='upper right', ncol=2, prop={'size': 8})

    # for i in range(len(x)):
    #     plt.text(x=x[i], y=y[i], s=labels2[i])


    # for i in range(len(x)):
    #     plt.text(x=x[i], y=y[i], s=labels[i])
    # plt.text(x, y, "test", fontsize=9)
    # plt.legend(["Matrix1"])#,"Integral","Series","Limit","Logarithm","Trigonometric","Set Theory","Probability","Derivative"])
    # plt.legend(["Matrix2"])
    plt.show()


def main():
    # s = [u'+', u'+', u'o']
    # col = ['r', 'r', 'g']
    # x = np.array([1, 2, 3])
    # y = np.array([4, 5, 6])
    #
    # for _s, c, _x, _y in zip(s, col, x, y):
    #     plt.scatter(_x, _y, marker=_s, c=c)
    #
    # plt.xlim(0, 4)
    # plt.ylim(0, 8)
    #
    # plt.show()

    draw_map("/home/bm3302/FastText/formula_tsne1", "/home/bm3302/FastText/formula_tsne1")


if __name__ == '__main__':
    main()

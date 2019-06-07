import numpy as np
import matplotlib.pyplot as plt

# Create data
def read_file_address(file_path):
    file = open(file_path)
    line = file.readline().strip("\n")
    data_points = {}
    while line:
        sections = line.split(",")
        file2 = open("/home/bm3302/FastText/Run_Result_9012/"+sections[1]+".txt")
        vector = np.fromfile(file2, sep =" ")
        if sections[0] in data_points.keys():
            data_points[sections[0]].append(vector)
        else:
            lst = [vector]
            data_points[sections[0]] = lst
        line = file.readline().strip("\n")
    return data_points


map = read_file_address("/home/bm3302/FastText/formula_tsne")
x = []
y = []
coulours = ["red", "blue", "yellow", "purple"]
color = []
labels = []
counter = 0
label_counter = 0

for key in map.keys():
    for item in map[key]:
        x.append(item[0])
        y.append(item[1])
        color.append(coulours[counter])
        labels.append(str(label_counter))
        label_counter += 1
    counter+=1

plt.scatter(x, y, c=color)

for i in range(label_counter):
    plt.text(x=x[i], y=y[i], s=labels[i])
#plt.text(x, y, "test", fontsize=9)
plt.show()
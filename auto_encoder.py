import os
import numpy as np
import os.path

from torch import nn
import torch
from os import listdir
import matplotlib.pyplot as plt
# from torch.nn.modules import utils
import torch.utils.data as utils
from torch.autograd import Variable
from tqdm import trange
os.environ["CUDA_VISIBLE_DEVICES"] = '0'
from numpy import linalg as LA
from sklearn import preprocessing


def create_destination(result):
    os.makedirs(result)
    for i in range(1, 17):
        os.makedirs(result + "/" + str(i))
    os.makedirs(result + "/" + "Queries")

def add_noise(vector):
    noise = torch.Tensor(np.random.normal(0, 1, vector.shape))
    noise = noise.to('cuda')
    noisy_vector = vector + noise
    return noisy_vector


class auto_encoder(nn.Module):
    def __init__(self):
        super(auto_encoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(900, 300),
            nn.Tanh()
        )
        self.decoder = nn.Sequential(
            nn.Linear(300, 900),
            nn.Tanh()
        )

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x

    def encode(self, x):
        x = self.encoder(x)
        return x



def merge_queries_files(result_file_path, current_dimension, lst_directories):
    map_result = {}
    i = "Queries"
    directory = lst_directories[0]+"/"+str(i)
    for filename in os.listdir(directory):
        "Checking if the file exists in all fast text trained models"
        all_exist = True
        for file_index in range(0, len(lst_directories)):
            if not os.path.isfile(lst_directories[file_index] + "/" + str(i) + "/" + filename):
                all_exist = False
                break
        if not all_exist:
            continue
        "saving the concatenated model"

        concat_array = np.array([])
        for file_index in range(0, len(lst_directories)):
            file = open(lst_directories[file_index] + "/" + str(i) + "/" + filename)
            formula_vector = np.array(np.loadtxt(file)).reshape(1, current_dimension)
            concat_array = np.concatenate([concat_array, formula_vector], axis=None)

        parts = filename.split(".")
        temp_name = parts[0]
        for k in range(1, len(parts) - 1):
            temp_name = temp_name + "." + parts[k]
        map_result[result_file_path + "/" + str(i) + "/" + temp_name + ".txt"] = concat_array
    return map_result


def merge_train_files(result_file_path, current_dimension, lst_directories):
    map_result = {}
    "training data"
    for i in range(1, 17):
        directory = lst_directories[0]+"/"+str(i)
        for filename in os.listdir(directory):
            "Checking if the file exists in all fast text trained models"
            all_exist = True
            for file_index in range(0, len(lst_directories)):
                if not os.path.isfile(lst_directories[file_index] + "/" + str(i) + "/" + filename):
                    all_exist = False
                    break
            if not all_exist:
                continue
            "saving the concatenated model"

            concat_array = np.array([])
            for file_index in range(0, len(lst_directories)):
                file = open(lst_directories[file_index] + "/" + str(i) + "/" + filename)
                formula_vector = np.array(np.loadtxt(file)).reshape(1, current_dimension)
                concat_array = np.concatenate([concat_array, formula_vector], axis=None)

            parts = filename.split(".")
            temp_name = parts[0]
            for k in range(1, len(parts) - 1):
                temp_name = temp_name + "." + parts[k]
            map_result[result_file_path + "/" + str(i) + "/" + temp_name + ".txt"] = concat_array
    return map_result


def dimension_reduction(map_lst):
    num_epochs = 50
    batch_size = 128
    learning_rate = 1e-3

    model = auto_encoder().cuda()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(
        model.parameters(), lr=learning_rate, weight_decay=1e-5)

    my_x = []  # a list of numpy arrays
    for formula_vector in map_lst.values():
        data = torch.from_numpy(formula_vector)
        data = data.float()
        my_x.append(data)

    tensor_x = torch.stack([torch.Tensor(i) for i in my_x])  # transform to torch tensors
    my_dataset = utils.TensorDataset(tensor_x)  # create your dataset
    dataloader = utils.DataLoader(my_dataset, batch_size=batch_size, shuffle=True)  # create your dataloader
    epoch_lst = []
    loss_lst = []
    for epoch in range(num_epochs):
        sum_loss = 0.0
        counter = 0.0
        with trange(len(dataloader)) as t:
            for batch_idx, data in enumerate(dataloader):
                # data = torch.from_numpy(data).float().cuda()
                data = Variable(data[0]).cuda()
                noisy_vector = add_noise(data[0])
                noisy_vector = Variable(noisy_vector).cuda()
                # ===================forward=====================
                output = model(noisy_vector)
                loss = criterion(output, data)
                # ===================backward====================
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                sum_loss += loss
                counter += batch_size
                t.set_postfix(loss=loss.data.tolist())
                t.update()
        loss = sum_loss / counter
        loss_lst.append(loss)
        epoch_lst.append(epoch + 1)

    plt.plot(epoch_lst, loss_lst)
    plt.show()
    torch.save(model.state_dict(), './auto_encoder.pth')

    return model


def save_reduction_results(model, map_lst, query_lst):
    for key in map_lst.keys():
        file_path = key
        vector = map_lst[key]
        data = torch.from_numpy(vector)
        data = data.float()
        data = Variable(data).cuda()
        temp = model.encode(data)
        np_val = temp.data.cpu().numpy()
        np.savetxt(file_path, np_val)

    for key in query_lst.keys():
        file_path = key
        vector = query_lst[key]
        data = torch.from_numpy(vector)
        data = data.float()
        data = Variable(data).cuda()
        temp = model.encode(data)
        np_val = temp.data.cpu().numpy()
        np.savetxt(file_path, np_val)


def main():
    a = np.arange(9) - 4
    #a = a + a
    print(a)
    a = [a , a]
    print(a)
    b = preprocessing.normalize(a, norm='l2')
    print(a)
    print(b)

    # result_file_path = "/home/bm3302/FastText/Run_Result_9006"
    # create_destination(result_file_path)
    #
    # lst_directories = ["/home/bm3302/FastText/Run_Result_431",
    #                     "/home/bm3302/FastText/Run_Result_436",
    #                     "/home/bm3302/FastText/Run_Result_501"]
    # print("Merging files")
    # map_lst = merge_train_files(result_file_path, 300, lst_directories)
    # query_lst = merge_queries_files(result_file_path, 300, lst_directories)
    #
    # print("Training model")
    # #model = dimension_reduction(map_lst)
    # save_reduction_results(model, map_lst, query_lst)


if __name__ == '__main__':
    main()
from enum import Enum
from sklearn.decomposition import TruncatedSVD
from sklearn.decomposition import PCA
from sklearn.decomposition import FastICA
from sklearn.manifold import TSNE
from torch import nn
from tqdm import trange
from torch.utils.data.sampler import SubsetRandomSampler
from torch.autograd import Variable

import numpy as np
import os.path
import datetime
import os
import torch
import matplotlib.pyplot as plt
import torch.utils.data as utils
import torch.nn.functional as F
import matplotlib
import argparse

matplotlib.use('Agg')
os.environ["CUDA_VISIBLE_DEVICES"] = '0'
use_cuda = torch.cuda.is_available()
reduction_to_size = 2


class Merge_Type(Enum):
    Sum = 1
    Concatenate = 2


class Reduce_Type(Enum):
    pca = 1
    ica = 2
    svd = 3
    tsne = 4
    autoencoder = 5
    no_reduction = 6


def create_destination(result):
    os.makedirs(result)
    os.makedirs(result + "/Collection")
    os.makedirs(result + "/Queries")


class auto_encoder(nn.Module):
    def __init__(self):
        super(auto_encoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(900, reduction_to_size),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(reduction_to_size, 900),
            nn.ReLU()
        )

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x

    def transform(self, vector):
        data = torch.from_numpy(vector)
        data = data.float()
        data = Variable(data).cuda()
        temp = self.encoder(data)
        temp = temp.detach().cpu().numpy()
        formula_vector = temp.reshape(1, reduction_to_size)
        return formula_vector


def read_train_vectors(directory_name):
    """

    :param directory_name: The directory where the results are there
    :return: return a map of formula_id and their vector representations
    Note that this is only the train (collection) data
    """
    map_result = {}
    for directory in os.listdir(directory_name):
        if directory != "Queries":
            for filename in os.listdir(directory_name + "/" + directory):
                formula_id = os.path.splitext(filename)[0]
                file = open(directory_name + "/" + directory + "/" + filename)
                formula_vector = np.array(np.loadtxt(file))
                map_result[formula_id] = formula_vector
                break
    return map_result


def read_query_vectors(directory_name):
    """

    :param directory_name: The directory where the results are there
    :return: return a map of formula_id and their vector representations
    Note that this is only the train (collection) data
    """
    map_result = {}
    for filename in os.listdir(directory_name + "/Queries"):
        formula_id = os.path.splitext(filename)[0]
        file = open(directory_name + "/Queries/" + filename)
        formula_vector = np.array(np.loadtxt(file))
        map_result[formula_id] = formula_vector
    return map_result


def concatenate_list(lst_formula_maps):
    """Checking if the file exists in all fast text trained models"""
    result_map_result = {}
    map_zero = lst_formula_maps[0]
    for formula_id in map_zero:
        all_exist = True
        formula_vector = map_zero[formula_id]
        for lst_index in range(1, len(lst_formula_maps)):
            if formula_id not in lst_formula_maps[lst_index]:
                all_exist = False
                break
            else:
                formula_vector_temp = lst_formula_maps[lst_index][formula_id]
                formula_vector = np.concatenate([formula_vector, formula_vector_temp], axis=0)
        if all_exist:
            result_map_result[formula_id] = formula_vector
    return result_map_result


def sum_list(lst_formula_maps):
    """Checking if the file exists in all fast text trained models"""
    result_map_result = {}
    map_zero = lst_formula_maps[0]
    for formula_id in map_zero:
        all_exist = True
        formula_vector = map_zero[formula_id]
        for lst_index in range(1, len(lst_formula_maps)):
            if lst_formula_maps[lst_index][formula_id] is None:
                all_exist = False
                break
            else:
                formula_vector_temp = lst_formula_maps[lst_index][formula_id]
                formula_vector = formula_vector + formula_vector_temp
        if all_exist:
            result_map_result[formula_id] = formula_vector
    return result_map_result


def save_merge_result(map_collection, map_queries, result_file_path):
    for formulas in map_collection:
        np.savetxt(result_file_path + "/" + str("Collection/") + formulas, map_collection[formulas], newline=" ")
    for formulas in map_queries:
        np.savetxt(result_file_path + "/" + str("Queries/") + formulas, map_queries[formulas], newline=" ")


def merge_result_files(lst_directories, merge_Type, result_file_path=None):
    lst_collection_maps = []
    lst_queries_map = []
    "training data"
    for directory in lst_directories:
        lst_collection_maps.append(read_train_vectors(directory))
        lst_queries_map.append(read_query_vectors(directory))

    if merge_Type == Merge_Type.Concatenate:
        map_collection = concatenate_list(lst_collection_maps)
        map_queries = concatenate_list(lst_queries_map)
    else:
        map_collection = sum_list(lst_collection_maps)
        map_queries = sum_list(lst_queries_map)

    if result_file_path is not None:
        create_destination(result_file_path)
        save_merge_result(map_collection, map_queries, result_file_path)

    return map_collection, map_queries


def dimension_reduction(map_lst, run_id):
    num_epochs = 1
    batch_size = 128
    learning_rate = 0.005

    model = auto_encoder().cuda()

    criterion = nn.MSELoss()
    optimizer = torch.optim.SGD(
        model.parameters(), lr=learning_rate, momentum=0.9)

    my_x = []  # a list of numpy arrays
    for formula_vector in map_lst.values():
        data = torch.from_numpy(formula_vector)
        data = data.float()
        my_x.append(data)

    tensor_x = torch.stack([torch.Tensor(i) for i in my_x])  # transform to torch tensors
    my_dataset = utils.TensorDataset(tensor_x)  # create your dataset

    validation_split = .15
    shuffle_dataset = True
    random_seed = 42

    dataset_size = len(my_dataset)
    indices = list(range(dataset_size))
    split = int(np.floor(validation_split * dataset_size))
    if shuffle_dataset:
        np.random.seed(random_seed)
        np.random.shuffle(indices)
    train_indices, val_indices = indices[split:], indices[:split]

    # Creating PT data samplers and loaders:
    train_sampler = SubsetRandomSampler(train_indices)
    valid_sampler = SubsetRandomSampler(val_indices)

    train_loader = torch.utils.data.DataLoader(my_dataset, batch_size=batch_size,
                                               sampler=train_sampler)
    validation_loader = torch.utils.data.DataLoader(my_dataset, batch_size=batch_size,
                                                    sampler=valid_sampler)

    loss_prev = 5000
    epoch_lst = []
    loss_validation_lst = []
    loss_training_lst = []
    patience_value = 10
    patience = patience_value
    finalModel = False
    bestEpoch = 0
    max_error = 0
    min_error = 1
    for epoch in range(num_epochs):
        print(epoch)
        print("\n")
        # if finalModel:
        #     break
        sum_loss = 0.0
        counter = 0.0
        loss_t = 0.0
        with trange(len(train_loader)) as t:
            for batch_idx, data in enumerate(train_loader):
                data = Variable(data[0]).cuda()
                # ===================forward=====================
                output = model(data)
                loss = criterion(output, data)
                loss_t = loss_t + loss.item()
                # ===================backward====================
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                sum_loss += loss
                counter += data.shape[0]
                t.set_postfix(loss=loss.data.tolist())
                t.update()
        loss_t = loss_t / counter
        epoch_lst.append(epoch)
        loss_training_lst.append(loss_t)

        loss_v = 0.0
        count = 0
        with trange(len(validation_loader)) as t:
            for batch_idx, data in enumerate(validation_loader):
                # data = torch.from_numpy(data).float().cuda()
                data = Variable(data[0]).cuda()
                # ===================forward=====================
                output = model(data)
                loss = criterion(output, data)
                loss_v = loss_v + loss.item()
                count += data.shape[0]
                t.set_postfix(loss=loss.data.tolist())
                t.update()
        loss_v = loss_v / count
        loss_validation_lst.append(loss_v)

        ##################################################Plot
        if loss_t > max_error:
            max_error = loss_t
        if loss_v > max_error:
            max_error = loss_v
        if min_error > loss_t:
            min_error = loss_t
        if min_error > loss_v:
            min_error = loss_t
        ##################################################Check Overfitting
        if loss_prev <= loss_v:
            if patience == 0:
                finalModel = True
            else:
                patience -= 1
        else:
            # if not finalModel:
            loss_prev = loss_v
            torch.save(model.state_dict(), 'Saved_Models/auto_encoder_model_' + str(run_id) + '.pth')
            torch.save(model.state_dict(), 'Saved_Models/auto_encoder_parameters_' + str(run_id) + '.pth')
            patience = patience_value
            bestEpoch = epoch

    ##################################################Loss_Epoch curve plot
    line1, = plt.plot(epoch_lst, loss_training_lst, '-r', label='train')
    line2, = plt.plot(epoch_lst, loss_validation_lst, '-b', label='validation')
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.plot([bestEpoch, bestEpoch], [min_error, max_error], color='k', linestyle='-', linewidth=2)
    plt.legend(handles=[line1, line2], loc='upper right')
    plt.show()
    plt.savefig('Train_validation/train_validation_' + str(run_id) + '.png')

    torch.save(model.state_dict(), 'Saved_Models/auto_encoder' + str(run_id) + '.pth')

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


def apply_reduction_collection(model, map_formulas, model_type):
    result = {}
    numpy_lst = []
    idx = 0
    for key in map_formulas.keys():
        formula_id = key
        vector = map_formulas[key]
        if model_type == Reduce_Type.autoencoder:
            formula_vector = model.transform(vector)
        else:
            formula_vector = model.transform([vector])
        numpy_lst.append(formula_vector)
        result[idx] = formula_id
        idx += 1
    temp = np.concatenate(numpy_lst, axis=0)
    tensor_values = Variable(torch.tensor(temp).double()).cuda()
    return result, tensor_values


def apply_reduction_queries(model, map_formulas, model_type):
    result = {}
    for key in map_formulas.keys():
        formula_id = key
        vector = map_formulas[key]
        if model_type == Reduce_Type.autoencoder:
            formula_vector = model.transform(vector)
        else:
            formula_vector = model.transform([vector])
        formula_vector = Variable(torch.tensor(formula_vector).double()).cuda()
        result[formula_id] = formula_vector
    return result


def formula_retrieval(doc_id_map, doc_tensors, query_vector_map, run_id):
    sum = .0
    counter = 0
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Retrieval_Results'))
    f = open(path + "/res_" + str(run_id), 'w')
    for queryId in query_vector_map:
        query_vec = query_vector_map[queryId]
        t1 = datetime.datetime.now()
        dist = F.cosine_similarity(doc_tensors, query_vec)
        index_sorted = torch.sort(dist, descending=True)[1]
        top_1000 = index_sorted[:1000]
        t2 = datetime.datetime.now()
        top_1000 = top_1000.data.cpu().numpy()
        sum += (t2 - t1).total_seconds() * 1000.0
        counter += 1
        cos_values = torch.sort(dist, descending=True)[0][:1000].data.cpu().numpy()
        count = 1
        query = "NTCIR12-MathWiki-" + str(queryId)
        line = query + " xxx "
        for x in top_1000:
            doc_id = doc_id_map[x]
            score = cos_values[count - 1]
            temp = line + doc_id + " " + str(count) + " " + str(score) + " Run_" + str(run_id)
            f.write(temp + "\n")
            count += 1
    f.close()
    print("Average retrieval time:")
    print(sum / counter)


def apply_pca(map_collection):
    print("Applying PCA")
    pca = PCA(n_components=reduction_to_size, svd_solver='full')
    vals = list(map_collection.values())
    pca.fit(vals)
    return pca


def apply_svd(map_collection):
    print("Applying SVD")
    svd = TruncatedSVD(n_components=reduction_to_size, n_iter=10)
    svd.fit(map_collection.values())
    return svd


def apply_ica(map_collection):
    print("Applying ICA")
    ica = FastICA(n_components=reduction_to_size)
    ica.fit(map_collection.values())
    return ica


def apply_TSNE(map_collection):
    print("Applying TSNE")
    return TSNE(n_components=reduction_to_size).fit(map_collection.values())


def main():
    parser = argparse.ArgumentParser(description='This module helps combine different embeddings of math formulas'
                                                 'and also provides means of dimensionality.')

    parser.add_argument('Merge type', metavar='merge_type', type=int, action=readable_directory,
                        help='0 for concatenating vectors and 1 for summing them up')
    parser.add_argument('Run Id', metavar='run_id', type=int, action=readable_directory,
                        help='0 for concatenating vectors and 1 for summing them up')
    parser.add_argument('Reduction type', metavar='reduction_type', type=int, action=readable_directory,
                        help='String, directory path to save the encoded tangent formula tuples')

    parser.add_argument("--frp", help="Use full relative path. (See tangent-S paper)", type=bool, default=False)

    args = vars(parser.parse_args())

    source_directory = args['source_directory']
    destination_directory = args['destination_directory']
    frp = args['frp']


    # num_epochs = 2500
    # batch_size = 128
    # learning_rate = 0.005

    # model = auto_encoder().cuda()
    # criterion = nn.MSELoss()
    # optimizer = torch.optim.SGD(
    # model.parameters(), lr=learning_rate, momentum=0.9)

    # print(model.state_dict())
    # print(optimizer.state_dict())
    # torch.save(optimizer.state_dict(), '/home/bm3302/PycharmProjects/TangentCFT/Dimensionality_Reduction/Saved_Models/test_' + str(100) + '.pth')
    # map = torch.load('/home/bm3302/PycharmProjects/TangentCFT/Dimensionality_Reduction/Saved_Models/test_' + str(100) + '.pth')
    result_file_path = None
    run_id = 100
    lst_directories = ["/home/bm3302/FastText/Run_Result_431",
                       "/home/bm3302/FastText/Run_Result_436",
                       "/home/bm3302/FastText/Run_Result_501"]
    print("Merging files")
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(dir_path)

    merge_type = Merge_Type.Concatenate
    map_collection, map_queries = merge_result_files(lst_directories, merge_type, result_file_path)

    reduce_type = Reduce_Type.pca

    if reduce_type == Reduce_Type.pca:
        model = apply_pca(map_collection)
    elif reduce_type == Reduce_Type.ica:
        model = apply_ica(map_collection)
    elif reduce_type == Reduce_Type.tsne:
        model = apply_TSNE(map_collection)
    elif reduce_type == Reduce_Type.svd:
        model = apply_svd(map_collection)
    elif reduce_type == Reduce_Type.autoencoder:
        model = dimension_reduction(map_collection, run_id)

    doc_id_map, doc_tensors = apply_reduction_collection(model, map_collection, reduce_type)
    query_vector_map = apply_reduction_queries(model, map_queries, reduce_type)

    formula_retrieval(doc_id_map, doc_tensors, query_vector_map, run_id)


if __name__ == '__main__':
    main()

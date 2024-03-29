import os
import keras
from keras.models import Sequential
from keras.layers import Dense, Conv2D
from keras.utils import CustomObjectScope
from keras_rewiring.optimizers.noisy_sgd import NoisySGD
from keras_rewiring.sparse_layer import \
    Sparse, SparseConv2D, SparseDepthwiseConv2D
from keras.models import load_model
from keras import backend as K
import ntpath
import json
import h5py
import numpy as np


# https://github.com/keras-team/keras/issues/10417#issuecomment-435620108
def fix_layer0(filename, batch_input_shape, dtype):
    with h5py.File(filename, 'r+') as f:
        model_config = json.loads(f.attrs['model_config'].decode('utf-8'))
        layer0 = model_config['config']['layers'][0]['config']
        layer0['batch_input_shape'] = batch_input_shape
        layer0['dtype'] = dtype
        f.attrs['model_config'] = json.dumps(model_config).encode('utf-8')


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def replace_dense_with_sparse(
        model, activation='relu',
        batch_size=1,
        builtin_sparsity=None,
        reg_coeffs=None,
        conn_decay=None,
        custom_object={},
        no_cache=False, threshold=True, random_weights=True,
        freeze_weight=False):
    '''
    Model is defined in Howard et al (2017)
    MobileNets: Efficient Convolutional Neural Networks for Mobile Vision
    Applications
    :return: the architecture of the network
    :rtype: keras.applications.mobilenet.MobileNet
    '''
    custom_object = custom_object or {}

    _cache = "__pycache__"
    if not os.path.isdir(_cache):
        os.mkdir(_cache)

    custom_object.update({'Sparse': Sparse,
                          'SparseConv2D': SparseConv2D,
                          'SparseDepthwiseConv2D': SparseDepthwiseConv2D,
                          'NoisySGD': NoisySGD})

    all_layers = model.layers
    number_of_connections_per_layer = []
    for layer in all_layers:
        curr_config = layer.get_config()
        name = curr_config['name']
        if "_bn" in name or "_relu" in name:
            continue
        curr_weights = layer.get_weights()
        no_weights = len(curr_weights)
        if no_weights > 0:
            number_of_connections_per_layer.append(curr_weights[0].size)
    number_of_connections_per_layer = np.asarray(number_of_connections_per_layer)
    mean_no_conn = np.mean(number_of_connections_per_layer)

    # https://stackoverflow.com/questions/8384737/extract-file-name-from-path-no-matter-what-the-os-path-format
    converted_model_filename = model.name + "_converted_to_sparse"
    file_path = os.path.join(_cache, converted_model_filename + ".h5")
    if not no_cache and os.path.exists(file_path):
        print("Using cached version of", converted_model_filename)
        K.clear_session()
        # Return the model
        return load_model(file_path, custom_objects=custom_object)

    # create new model which will contain the sparse layers
    sparse_model = Sequential()

    model_input_shape = None

    print("=" * 60)
    print("Sparsifying layers")
    print("-" * 60)
    for i, layer in enumerate(model.layers):
        # get layer configuration
        layer_config = layer.get_config()
        # modify layer name
        print("{:30}".format("Processing layer"), layer_config['name'])
        layer_config['name'] = "sparse_" + layer_config['name']
        # replace with the appropriate sparse layer
        curr_sparse_layer = None
        # however, if threshold: only replace when above the mean connectivity
        curr_weights = layer.get_weights()
        if i == 0 and 'batch_input_shape' in layer_config:
            model_input_shape = list(layer_config['batch_input_shape'])
            model_input_shape[0] = batch_size
            model_input_shape = tuple(model_input_shape)

        if (builtin_sparsity and
                ((threshold and len(curr_weights) > 0 and curr_weights[0].size > mean_no_conn)
                 or not threshold)):
            layer_config['connectivity_level'] = builtin_sparsity.pop(0)
        if (conn_decay and
                ((threshold and len(curr_weights) > 0 and curr_weights[0].size > mean_no_conn)
                 or not threshold)):
            layer_config['connectivity_decay'] = conn_decay.pop(0)
        if isinstance(layer, Conv2D):
            if (threshold and curr_weights[0].size > mean_no_conn) or not threshold:
                curr_sparse_layer = SparseConv2D(**layer_config)
        elif isinstance(layer, Dense):
            if (threshold and curr_weights[0].size > mean_no_conn) or not threshold:
                curr_sparse_layer = Sparse(**layer_config)

        if curr_sparse_layer is not None:
            layer_to_add = curr_sparse_layer
            sparsified_layer = True
        else:
            layer_to_add = layer
            sparsified_layer = False
            # Check whether pre-trained or random weights are supposed to be used
        if not random_weights and i != 0:
            weights = layer_to_add.get_weights()
            if len(weights) == 1:
                curr_weights = np.asarray(curr_weights)
                layer_to_add.set_weights(
                    np.array([np.squeeze(curr_weights, axis=0)]))
        freezing = (not sparsified_layer) and freeze_weight
        print("\t{:26}".format("random weights"), random_weights)
        print("\t{:26}".format("sparsified"), sparsified_layer)
        print("\t{:26}".format("frozen weights"), freezing)
        print("-" * 60)
        layer_to_add.trainable = freezing
        sparse_model.add(layer_to_add)

    if builtin_sparsity:
        assert len(builtin_sparsity) == 0
    if conn_decay:
        assert len(conn_decay) == 0
    print("Converted filename", converted_model_filename)
    with CustomObjectScope(custom_object):
        sparse_model.save(file_path)
    fix_layer0(file_path, model_input_shape or [batch_size, 224, 224, 3], 'float32')

    K.clear_session()

    # Return the model
    return load_model(file_path, custom_objects=custom_object)


if __name__ == "__main__":
    model = keras.applications.MobileNet()
    sparse_model = replace_dense_with_sparse(model)
    sparse_model.summary()

    model_path = os.path.join("05-mobilenet_dwarf_v1",
                              "standard_dense_dwarf.h5")
    model = load_model(model_path)
    sparse_model = replace_dense_with_sparse(model)
    sparse_model.summary()

import argparse

batch_size = 50
# epochs = 20

DEFAULT_MODEL_DIR = 'models/'
DEFAULT_RESULT_DIR = 'results/'

parser = argparse.ArgumentParser(
    description='DNN argparser',
    formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('model', type=str, nargs="+",
                    help='network architecture / model to train and test')

parser.add_argument('--dataset_path', type=str,
                    help='path for dataset')

parser.add_argument('--result_filename', type=str,
                    help='filename for results')

parser.add_argument('--non_categorical', dest="non_categorical",
                    help='filename for results',
                    action="store_false")

parser.add_argument('--sparse_layers',
                    help='Use sparse layers',
                    action="store_true")

parser.add_argument('--verbose',
                    help='Verbose logging',
                    action="store_true")

parser.add_argument('--random_weights',
                    help='randomly initialise model weights',
                    action="store_true")

parser.add_argument('--disable_rewiring',
                    help='For testing the accuracy one could '
                         'get with no rewiring',
                    action="store_true")

parser.add_argument('--data_augmentation',
                    help='enable data augmentation',
                    action="store_true")

parser.add_argument('--conn_decay',
                    help='decay the target number of connections',
                    action="store_true")


parser.add_argument('--asserts_on',
                    help='turn on all asserts',
                    action="store_true")

parser.add_argument('--soft_rewiring',
                    help='rewiring without a target number of synapses',
                    action="store_true")

parser.add_argument('--tensorboard',
                    help='Whether to create tensorboard statistics',
                    action="store_true")


parser.add_argument('--no-cache', dest="no_cache",
                    help="don't use cached model",
                    action="store_true")

parser.add_argument('--epochs', type=int,
                    help='number of epochs', default=None)

# When passing epochs in like this, do we start counting from 0 or 1?
# https://keras.io/models/sequential/ would suggest that the default is 0
parser.add_argument('--continue_from_epoch', type=int,
                    help='continue learning from a checkpoint '
                         '(first epoch starts at 0)', default=0)


parser.add_argument('--steps_per_epoch', type=int,
                    help='When using data generators - '
                         'how many batches to generate each epoch',
                    default=None)

parser.add_argument('--val_steps_per_epoch', type=int,
                    help='When using data generators - '
                         'how many batches to generate each epoch',
                    default=None)

parser.add_argument('--batch', type=int,
                    help='batch size', default=batch_size)

parser.add_argument('--conn_level', type=float, nargs="+",
                    help='flat connectivity level used for rewiring',
                    default=None)

parser.add_argument('--lr', type=float,
                    help='learning rate to be used during training',
                    default=None)

parser.add_argument('--optimizer', type=str,
                    help='optimizer to use', default='sgd')

parser.add_argument('--dataset', type=str,
                    help='dataset for training and testing', default='mnist')

parser.add_argument('--activation', type=str,
                    help='activation type', default='relu')

parser.add_argument('--loss', type=str,
                    help='loss function', default='mse')

parser.add_argument('--suffix', type=str,
                    help='loss function', default=None)

parser.add_argument('--model_dir', type=str,
                    help='directory in which to load and '
                         'store network architectures',
                    default=DEFAULT_MODEL_DIR)

parser.add_argument('--result_dir', type=str,
                    help='directory inp which to load and '
                         'store network architectures',
                    default=DEFAULT_RESULT_DIR)

parser.add_argument('--just_test',
                    help='just test model',
                    action="store_true")

parser.add_argument('--test_as_dense',
                    help='make dense model and apply weights from file',
                    action="store_true")

args = parser.parse_args()

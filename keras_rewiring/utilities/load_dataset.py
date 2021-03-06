from keras.datasets import mnist, cifar10, cifar100
import keras
import numpy as np
from keras_rewiring.utilities.imagenet_utils import ImagenetDataGenerator


def load_and_preprocess_dataset(dataset_name, categorical_output=True,
                                batch_size=100, path=None,
                                steps_per_epoch=None,
                                val_steps_per_epoch=None,
                                ):
    path = path or ''
    # Dataset selection
    if dataset_name.lower() == "mnist":
        # input image dimensions
        img_rows, img_cols = 28, 28
        num_classes = 10

        # the data, split between train and test sets
        (x_train, y_train), (x_test, y_test) = mnist.load_data()

        x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
        x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)
        input_shape = (img_rows, img_cols, 1)

        x_train = x_train.astype('float32')
        x_test = x_test.astype('float32')
        x_train /= 255
        x_test /= 255
        # print('x_train shape:', x_train.shape)
        # print(x_train.shape[0], 'train samples')
        # print(x_test.shape[0], 'test samples')

    elif dataset_name.lower() == "cifar10":
        # input image dimensions
        img_rows, img_cols = 32, 32
        input_shape = (img_rows, img_cols, 3)
        num_classes = 10

        # the data, split between train and test sets
        (x_train, y_train), (x_test, y_test) = cifar10.load_data()

        x_train = x_train.astype('float32')
        x_test = x_test.astype('float32')
        x_train /= 255
        x_test /= 255

        x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 3)
        x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 3)

        print('x_train shape:', x_train.shape)
        print(x_train.shape[0], 'train samples')
        print(x_test.shape[0], 'test samples')
    elif dataset_name.lower() == "cifar100":
        # input image dimensions
        img_rows, img_cols = 32, 32
        input_shape = (img_rows, img_cols, 3)
        num_classes = 100

        # the data, split between train and test sets
        (x_train, y_train), (x_test, y_test) = cifar100.load_data()

        x_train = x_train.astype('float32')
        x_test = x_test.astype('float32')
        x_train /= 255
        x_test /= 255

        x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 3)
        x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 3)

        print('x_train shape:', x_train.shape)
        print(x_train.shape[0], 'train samples')
        print(x_test.shape[0], 'test samples')
    elif dataset_name.lower() == "imagenet":
        if steps_per_epoch:
            print("Generators being set up for", steps_per_epoch,
                  "steps_per_epoch")
        train_gen = ImagenetDataGenerator("train", batch_size, path,
                                          steps_per_epoch=steps_per_epoch)
        val_gen = ImagenetDataGenerator("val", batch_size, path,
                                        steps_per_epoch=val_steps_per_epoch)

        return {'train': train_gen(),
                'no_train': train_gen.imagenet_number_of_samples(),
                'val': val_gen(),
                'no_val': val_gen.imagenet_number_of_samples(),
                'img_dims': (224, 224, 3),
                'input_shape': (224, 224, 3),
                'num_classes': 1000,
                'categorical_output': True}

    else:
        import tensorflow_datasets as tfds
        # data = tfds.load(dataset_name)
        data = tfds.builder(dataset_name)
        num_classes = data.info.features['label'].num_classes
        dataset = data.as_dataset()
        train, test = tfds.as_numpy(dataset["train"]), tfds.as_numpy(dataset["test"])
        x_train = []
        y_train = []
        x_test = []
        y_test = []
        for example in train:
            image, label = example['image'], example['label']
            x_train.append(image)
            y_train.append(label)
        for example in test:
            image, label = example['image'], example['label']
            x_test.append(image)
            y_test.append(label)
        y_train = np.asarray(y_train)
        y_test = np.asarray(y_test)
        x_train = np.asarray(y_train)
        x_test = np.asarray(y_test)
    if categorical_output:
        # convert class vectors to binary class matrices
        y_train = keras.utils.to_categorical(y_train, num_classes)
        y_test = keras.utils.to_categorical(y_test, num_classes)

    return {'train': (x_train, y_train),
            'test': (x_test, y_test),
            'img_dims': (img_rows, img_cols),
            'input_shape': input_shape,
            'num_classes': num_classes,
            'categorical_output': categorical_output}

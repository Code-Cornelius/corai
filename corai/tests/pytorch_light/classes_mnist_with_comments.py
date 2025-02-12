# example from: https://pytorch-lightning.readthedocs.io/en/latest/notebooks/lightning_examples/mnist-hello-world.html
# adds on from https://pytorch-lightning.readthedocs.io/en/latest/starter/introduction_guide.html
import os
import sys

import torch
from pytorch_lightning import LightningModule, LightningDataModule
from pytorch_lightning.callbacks import ProgressBar
from pytorch_lightning.callbacks.progress.tqdm_progress import Tqdm, convert_inf
from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader, random_split
from torchmetrics.functional import accuracy
from torchvision import transforms
from torchvision.datasets import MNIST
from tqdm import tqdm

PATH_DATASETS = os.environ.get("PATH_DATASETS", ".")
AVAIL_GPUS = min(1, torch.cuda.device_count())
BATCH_SIZE = 512 if AVAIL_GPUS else 256


# Keep in Mind - A LightningModule is a PyTorch nn.Module - it just has a few more helpful features.
class MNISTModel(LightningModule):
    def __init__(self, fake_param=42, data_dir=PATH_DATASETS, hidden_size=64, learning_rate=0.01):
        super().__init__()

        # Set our init args as class attributes
        self.data_dir = data_dir
        self.hidden_size = hidden_size
        self.learning_rate = learning_rate

        # Hardcode some dataset specific attributes
        self.num_classes = 10
        self.dims = (1, 28, 28)
        channels, width, height = self.dims

        # Define PyTorch model
        self.model = nn.Sequential(
            nn.Flatten(),
            nn.Linear(channels * width * height, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, self.num_classes),
        )

        # By default, every parameter of the __init__ method will be
        # considered a hyperparameter to the LightningModule
        self.save_hyperparameters(ignore=["data_dir"])

    def forward(self, x): # forward not even required if the forward path is simply self.model(x).
        x = self.model(x)
        x = F.log_softmax(x, dim=1)

        return x

    def training_step(self, batch, batch_nb):
        # for details about optimization step:
        # https://pytorch-lightning.readthedocs.io/en/latest/common/optimizers.html
        # for manual backward: https://pytorch-lightning.readthedocs.io/en/latest/common/optimizers.html#manual-optimization
        x, y = batch
        logits = self(x)
        loss = F.nll_loss(logits, y)
        preds = torch.argmax(logits, dim=1)
        acc = accuracy(preds, y)

        self.log(name="train_loss", value=loss, prog_bar=True, on_step=False, on_epoch=True)
        self.log(name="train_acc", value=acc, prog_bar=True, on_step=False, on_epoch=True)

        # opt.step()
        # Before 1.2, optimizer.step() was calling optimizer.zero_grad() internally. From 1.2, it is left to the user’s expertise.
        return loss

    def validation_step(self, batch, batch_nb): # validation step is done after the optimisation step.
        x, y = batch
        logits = self(x)
        loss = F.nll_loss(logits, y)

        preds = torch.argmax(logits, dim=1)
        acc = accuracy(preds, y)

        self.log(name="val_loss", value=loss, prog_bar=True, on_step=False, on_epoch=True)
        self.log(name="val_acc", value=acc, prog_bar=True, on_step=False, on_epoch=True)  # step is when you call vali or train step.
        # on_epoch means it will return the average over batches.

        return loss

    def test_step(self, batch, batch_idx):
        # x, y = batch
        # logits = self(x)
        # loss = F.nll_loss(logits, y)
        # self.log("test_loss", loss)
        return self.validation_step(batch, batch_idx)

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.learning_rate)

    def prepare_data(self):
        # download
        MNIST(self.data_dir, train=True, download=True)
        MNIST(self.data_dir, train=False, download=True)


# Init DataLoader from MNIST Dataset
# Defining free-floating dataloaders, splits, download instructions, and such can get messy.
# In this case, it’s better to group the full definition of a dataset into a DataModule which includes:
#
#     Download instructions
#     Processing instructions
#     Split instructions
#     Train dataloader
#     Val dataloader(s)
#     Test dataloader(s)
class MyDataModule(LightningDataModule):
    def __init__(self):
        super().__init__()
        self.train_dims = None
        self.vocab_size = 0
        self.transform = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize((0.1307,), (0.3081,)),
            ]
        )

    ####################
    # DATA RELATED HOOKS
    ####################

    # prepare_data() is called on only one GPU in distributed training (automatically)
    def prepare_data(self):
        # download
        MNIST(PATH_DATASETS, train=True, download=True)
        MNIST(PATH_DATASETS, train=False, download=True)

    # setup() is called on every GPU (automatically)
    ######
    # Loads in data from file and prepares PyTorch tensor datasets for each split (train, val, test).
    # Setup expects a ‘stage’ arg which is used to separate logic for ‘fit’ and ‘test’.
    # If you don’t mind loading all your datasets at once, you can set up a condition to allow for both ‘fit’ related setup and ‘test’ related setup
    # to run whenever None is passed to stage (or ignore it altogether and exclude any conditionals).
    # Note this runs across all GPUs and it *is* safe to make state assignments here
    def setup(self, stage=None):
        # Assign train/val datasets for use in dataloaders
        # if stage == "fit" or stage is None:
        #     mnist_full = MNIST(PATH_DATASETS, train=True, transform=self.transform)
        #     self.mnist_train, self.mnist_val = random_split(mnist_full, [50000, 10000])
        #
        # Assign test dataset for use in dataloader(s)
        # if stage == "test" or stage is None:
        #     self.mnist_test = MNIST(PATH_DATASETS, train=False, transform=self.transform)
        mnist_full = MNIST(PATH_DATASETS, train=True, transform=self.transform)
        self.mnist_train, self.mnist_val, self.mnist_test = random_split(mnist_full, [10000, 40000, 10000])

    # train_dataloader(), val_dataloader(), and test_dataloader() all return PyTorch DataLoader instances
    # that are created by wrapping their respective datasets that we prepared in setup()
    def train_dataloader(self):
        return DataLoader(self.mnist_train, batch_size=BATCH_SIZE)
        # return corai.FastTensorDataLoader(DataLoader(self.mnist_train, 20000).dataset[0], batch_size=BATCH_SIZE)

    def val_dataloader(self):
        return DataLoader(self.mnist_val, batch_size=BATCH_SIZE)
        # return corai.FastTensorDataLoader(self.mnist_val, batch_size=BATCH_SIZE)

    def test_dataloader(self):
        return DataLoader(self.mnist_test, batch_size=BATCH_SIZE)
        # return corai.FastTensorDataLoader(self.mnist_test, batch_size=BATCH_SIZE)


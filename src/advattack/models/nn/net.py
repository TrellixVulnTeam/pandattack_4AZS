import torch
import torch.nn as nn
import tqdm
from torch.utils.tensorboard import SummaryWriter
import os
import torch.nn.functional as F
from advattack import tensorboard_path
import shutil
from advattack.data_handling.dataset_loader import DatasetLoader


class NNModel(nn.Module):
    def __init__(self, use_tensorboard=False):
        super(NNModel, self).__init__()
        if use_tensorboard:
            self.tb_writer_train, self.tb_writer_valid = self.set_up_tensorboard()

    def set_up_tensorboard(self):
        # set up tensorboard
        tb_dir_train = os.path.join(tensorboard_path, "/ff/train/")
        tb_dir_valid = os.path.join(tensorboard_path, "/ff/valid/")
        os.makedirs(os.path.dirname(tb_dir_train), exist_ok=True)
        os.makedirs(os.path.dirname(tb_dir_valid), exist_ok=True)
        tb_writer_train = SummaryWriter(log_dir=tb_dir_train, flush_secs=10)
        tb_writer_valid = SummaryWriter(log_dir=tb_dir_valid, flush_secs=10)
        return tb_writer_train, tb_writer_valid

    def train_model(self, train_loader: DatasetLoader, valid_loader: DatasetLoader, optimizer, loss_function, epochs=1):
        print("Starting Training loss:")
        self.evaluate_model(train_loader, 0)
        print("Starting Validation loss:")
        self.evaluate_model(valid_loader, 0)
        print("\n=================================================================================================\n")

        for epoch in tqdm.tqdm(range(epochs)):  # again, normally you would NOT do 300 epochs, it is toy data
            self.train_epoch(train_loader, loss_function, optimizer)
            print("Training loss:")
            self.evaluate_model(data_loader=train_loader, epoch=epoch)
            print("Validation loss:")
            self.evaluate_model(data_loader=valid_loader, epoch=epoch)
            print("\n============================================================================================\n")
            # model_save_path = os.path.join(f'../../models/lstm_model/epoch_{epoch}.pt')
            # model.save(model_save_path)

    def evaluate_model(self, data_loader, epoch):
        test_loss = 0
        correct = 0
        for samples, batch_size, targets in data_loader:
            with torch.no_grad():
                outputs = self(samples).squeeze(1)
                test_loss += F.nll_loss(outputs, targets, reduction='sum').item()  # sum up batch loss
                pred = outputs.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
                correct += pred.eq(targets.view_as(pred)).sum().item()

        accuracy = correct / len(data_loader)
        test_loss = test_loss / len(data_loader)
        print(f'Average loss: {test_loss}, Accuracy: {accuracy}')
        return test_loss

    def save_model(self, folder_path) -> str:
        shutil.rmtree(folder_path, ignore_errors=True)
        os.makedirs(folder_path)
        full_path = os.path.join(folder_path, "model.pt")
        torch.save(self.state_dict(), full_path)
        return full_path

    def load_model(self, folder_path):
        full_path = os.path.join(folder_path, "model.pt")
        self.load_state_dict(torch.load(full_path))
        self.eval()

    @classmethod
    def get_model_type(cls):
        return cls.__mro__[0].__name__


    def get_config(self):
        return dict()

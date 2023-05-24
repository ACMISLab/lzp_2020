from paddle.io import RandomSampler, BatchSampler, Dataset


# init with dataset
class RandomDataset(Dataset):
    def __init__(self, num_samples):
        self.num_samples = num_samples

    def __getitem__(self, idx):
        pass

    def __len__(self):
        return self.num_samples
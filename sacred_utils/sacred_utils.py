# -*- coding: utf-8 -*-
from torch.utils.data import Dataset


class IndexableDataset(Dataset):
    def __init__(self, *indexables):
        super(IndexableDataset).__init__()
        # Make sure that the lengths of the indexables are equal
        assert(len(indexables) > 0)
        l = len(indexables[0])
        assert(all(len(i) == l for i in indexables))

        self.indexables = indexables

    def __getitem__(self, i):
        return tuple(item[i] for item in self.indexables)

    def __len__(self):
        return len(self.indexables[0])

    def __add__(self, other):
        return VConcatDataset(self, other)

    def __mul__(self, num_times):
        return RepeatDataset(self, num_times)


class VConcatDataset(Dataset):
    def __init__(self, *datasets):
        super(VConcatDataset).__init__()
        # Make sure that the lengths of the datasets are equal
        assert(len(datasets) > 0)
        l = len(datasets[0])
        assert(all(len(i) == l for i in datasets))

        self.datasets = datasets

    def __getitem__(self, i):
        return tuple(j
                     for ds in self.datasets
                     for j in ds[i])

    def __len__(self):
        return len(self.datasets[0])


class RepeatDataset(Dataset):
    def __init__(self, dataset, n):
        super(RepeatDataset).__init__()
        # Make sure that the lengths of the datasets are equal
        self.dataset = dataset
        self.mod = len(dataset)
        self.n = n

    def __getitem__(self, i):
        return self.dataset[i % self.mod]

    def __len__(self):
        return len(self.dataset) * self.n

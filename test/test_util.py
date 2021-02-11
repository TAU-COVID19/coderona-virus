import pytest
from random import randint
from src.util.divide_array import divide_array, divide_weighted_array


def test_divide_array():
    for _ in range(50):
        lst = [i for i in range((randint(50, 100)))]
        new_lst = divide_array(lst, randint(4, 15))
        assert len(new_lst) != 0
        len_lst = [len(x) for x in new_lst]
        assert max(len_lst) - min(len_lst) < 2    



def test_divide_weighted_array():
    for _ in range(50):
        dummy_lst = [Dummy() for _ in range(randint(50, 100))]
        weighted_lst = [(dummy, dummy.weight) for dummy in dummy_lst]
        new_lst = divide_weighted_array(weighted_lst, randint(10, 20))
        assert len(new_lst) != 0
        weight_lst = [find_total_weight(lst) for lst in new_lst]
        assert max(weight_lst) - min(weight_lst) < 15    


def find_total_weight(dummies):
    total = 0
    for dummy in dummies:
        total += dummy.weight
    return total



class Dummy(object):
    def __init__(self):
        self.weight = randint(1, 10)
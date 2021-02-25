import psutil
import time
import numpy as np
from cpuinfo import get_cpu_info as cpu
from pprint import pprint
#pprint(cpu())

def get_name():
    return ' CPU X '#+ str(cpu()['count']) + ' '

def get_mem():
    avail = psutil.virtual_memory().available/10**9
    total = psutil.virtual_memory().total/10**9
    return {'avail_memory': avail, 'total_memory': total}

def check(desc='', mem=5):
    print("Found " + str(desc) + get_name(), get_mem(), flush=True)
    while get_mem()['avail_memory'] < mem:
        print("Waiting in " + str(desc) + get_name(), get_mem(), flush=True)
        time.sleep(np.random.uniform(low=0,high=1))

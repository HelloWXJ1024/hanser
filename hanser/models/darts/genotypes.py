from collections import namedtuple

Genotype = namedtuple('Genotype', 'normal normal_concat reduce reduce_concat')

PRIMITIVES_tiny = [
    'none',
    'skip_connect',
    'sep_conv_3x3',
]

PRIMITIVES_small = [
    'max_pool_3x3',
    'avg_pool_3x3',
    'skip_connect',
    'sep_conv_3x3',
    'sep_conv_5x5',
    'conv_3x1_1x3',
]

PRIMITIVES_large = [
    'max_pool_3x3',
    'avg_pool_3x3',
    'skip_connect',
    'sep_conv_3x3',
    'sep_conv_5x5',
    'dil_conv_3x3',
    'dil_conv_5x5',
    'conv_3x1_1x3',
]

PRIMITIVES_huge = [
    'skip_connect',
    'nor_conv_1x1',
    'max_pool_3x3',
    'avg_pool_3x3',
    'nor_conv_3x3',
    'sep_conv_3x3',
    'dil_conv_3x3',
    'conv_3x1_1x3',
    'sep_conv_5x5',
    'dil_conv_5x5',
    'sep_conv_7x7',
    'conv_7x1_1x7',
    'att_squeeze',
]

PRIMITIVES_darts = [
    'none',
    'skip_connect',
    'max_pool_3x3',
    'avg_pool_3x3',
    'sep_conv_3x3',
    'sep_conv_5x5',
    'dil_conv_3x3',
    'dil_conv_5x5',
]

CONFIG = {
    'primitives': PRIMITIVES_darts,
}


def set_primitives(search_space):
    if isinstance(search_space, list):
        for k in search_space:
            if not k in PRIMITIVES_darts:
                raise ValueError("Not supported operation: %s" % k)
        CONFIG['primitives'] = search_space
    elif search_space == 'tiny':
        CONFIG['primitives'] = PRIMITIVES_tiny
    elif search_space == 'small':
        CONFIG['primitives'] = PRIMITIVES_small
    elif search_space == 'large':
        CONFIG['primitives'] = PRIMITIVES_large
    elif search_space == 'huge':
        CONFIG['primitives'] = PRIMITIVES_huge
    elif search_space == 'darts':
        CONFIG['primitives'] = PRIMITIVES_darts
    else:
        raise ValueError("No search space %s" % search_space)


def get_primitives():
    return CONFIG['primitives']


PNASNet = Genotype(
    normal=[
        (('sep_conv_5x5', 0), ('max_pool_3x3', 0)),
        (('sep_conv_7x7', 1), ('max_pool_3x3', 1)),
        (('sep_conv_5x5', 1), ('sep_conv_3x3', 1)),
        (('sep_conv_3x3', 4), ('max_pool_3x3', 1)),
        (('sep_conv_3x3', 0), ('skip_connect', 1)),
    ],
    normal_concat=[2, 3, 4, 5, 6],
    reduce=[
        (('sep_conv_5x5', 0), ('max_pool_3x3', 0)),
        (('sep_conv_7x7', 1), ('max_pool_3x3', 1)),
        (('sep_conv_5x5', 1), ('sep_conv_3x3', 1)),
        (('sep_conv_3x3', 4), ('max_pool_3x3', 1)),
        (('sep_conv_3x3', 0), ('skip_connect', 1)),
    ],
    reduce_concat=[2, 3, 4, 5, 6],
)

# One-Shot Neural Architecture Search via Self-Evaluated Template Network, ICCV 2019
SETN = Genotype(
    normal=[
        ('skip_connect', 0), ('sep_conv_5x5', 1),
        ('sep_conv_5x5', 0), ('sep_conv_3x3', 1),
        ('sep_conv_5x5', 1), ('sep_conv_5x5', 3),
        ('max_pool_3x3', 1), ('conv_3x1_1x3', 4),
    ],
    normal_concat=[2, 3, 4, 5],
    reduce=[
        ('sep_conv_3x3', 0), ('sep_conv_5x5', 1),
        ('avg_pool_3x3', 0), ('sep_conv_5x5', 1),
        ('avg_pool_3x3', 0), ('sep_conv_5x5', 1),
        ('avg_pool_3x3', 0), ('skip_connect', 1),
    ],
    reduce_concat=[2, 3, 4, 5],
)

"""====== Different Archirtecture By Other Methods"""
# 608M, 3.3M, 2.65
NASNet_A = Genotype(
    normal=[
        ('sep_conv_5x5', 1), ('sep_conv_3x3', 0),
        ('sep_conv_5x5', 0), ('sep_conv_3x3', 0),
        ('avg_pool_3x3', 1), ('skip_connect', 0),
        ('avg_pool_3x3', 0), ('avg_pool_3x3', 0),
        ('sep_conv_3x3', 1), ('skip_connect', 1),
    ],
    normal_concat=[2, 3, 4, 5, 6],
    reduce=[
        ('sep_conv_5x5', 1), ('sep_conv_7x7', 0),
        ('max_pool_3x3', 1), ('sep_conv_7x7', 0),
        ('avg_pool_3x3', 1), ('sep_conv_5x5', 0),
        ('skip_connect', 3), ('avg_pool_3x3', 2),
        ('sep_conv_3x3', 2), ('max_pool_3x3', 1),
    ],
    reduce_concat=[4, 5, 6],
)

AmoebaNet_A = Genotype(
    normal=[
        ('avg_pool_3x3', 0), ('max_pool_3x3', 1),
        ('sep_conv_3x3', 0), ('sep_conv_5x5', 2),
        ('sep_conv_3x3', 0), ('avg_pool_3x3', 3),
        ('sep_conv_3x3', 1), ('skip_connect', 1),
        ('skip_connect', 0), ('avg_pool_3x3', 1),
    ],
    normal_concat=[4, 5, 6],
    reduce=[
        ('avg_pool_3x3', 0), ('sep_conv_3x3', 1),
        ('max_pool_3x3', 0), ('sep_conv_7x7', 2),
        ('sep_conv_7x7', 0), ('avg_pool_3x3', 1),
        ('max_pool_3x3', 0), ('max_pool_3x3', 1),
        ('conv_7x1_1x7', 0), ('sep_conv_3x3', 5),
    ],
    reduce_concat=[3, 4, 6]
)

# https://arxiv.org/pdf/1802.03268.pdf
# 627M, 4.02M
ENASNet = Genotype(
    normal=[
        ('sep_conv_3x3', 1), ('skip_connect', 1),
        ('sep_conv_5x5', 1), ('skip_connect', 0),
        ('avg_pool_3x3', 0), ('sep_conv_3x3', 1),
        ('sep_conv_3x3', 0), ('avg_pool_3x3', 1),
        ('sep_conv_5x5', 1), ('avg_pool_3x3', 0),
    ],
    normal_concat=[2, 3, 4, 5, 6],
    reduce=[
        ('sep_conv_5x5', 0), ('sep_conv_3x3', 1),
        ('sep_conv_3x3', 1), ('avg_pool_3x3', 1),
        ('sep_conv_3x3', 1), ('avg_pool_3x3', 1),
        ('avg_pool_3x3', 1), ('sep_conv_5x5', 4),
        ('sep_conv_3x3', 5), ('sep_conv_5x5', 0),
    ],
    reduce_concat=[2, 3, 4, 5, 6],
)

# 3.3M, 3.00±0.14
DARTS_V1 = Genotype(
    normal=[
        ('sep_conv_3x3', 1), ('sep_conv_3x3', 0),
        ('skip_connect', 0), ('sep_conv_3x3', 1),
        ('skip_connect', 0), ('sep_conv_3x3', 1),
        ('sep_conv_3x3', 0), ('skip_connect', 2),
    ],
    normal_concat=[2, 3, 4, 5],
    reduce=[
        ('max_pool_3x3', 0), ('max_pool_3x3', 1),
        ('skip_connect', 2), ('max_pool_3x3', 0),
        ('max_pool_3x3', 0), ('skip_connect', 2),
        ('skip_connect', 2), ('avg_pool_3x3', 0),
    ],
    reduce_concat=[2, 3, 4, 5],
)

# 528M, 3.3M, 2.76±0.09
DARTS_V2 = Genotype(
    normal=[
        ('sep_conv_3x3', 0), ('sep_conv_3x3', 1),
        ('sep_conv_3x3', 0), ('sep_conv_3x3', 1),
        ('sep_conv_3x3', 1), ('skip_connect', 0),
        ('skip_connect', 0), ('dil_conv_3x3', 2),
    ],
    normal_concat=[2, 3, 4, 5],
    reduce=[
        ('max_pool_3x3', 0), ('max_pool_3x3', 1),
        ('skip_connect', 2), ('max_pool_3x3', 1),
        ('max_pool_3x3', 0), ('skip_connect', 2),
        ('skip_connect', 2), ('max_pool_3x3', 1),
    ],
    reduce_concat=[2, 3, 4, 5],
)


# from https://github.com/D-X-Y/NAS-Projects/blob/master/others/GDAS/lib/nas/genotypes.py
# 519M, 3.36M, 2.93
GDAS_V1 = Genotype(
    normal=[
        ('skip_connect', 0), ('skip_connect', 1),
        ('skip_connect', 0), ('sep_conv_5x5', 2),
        ('sep_conv_3x3', 3), ('skip_connect', 0),
        ('sep_conv_5x5', 4), ('sep_conv_3x3', 3),
    ],
    normal_concat=[2, 3, 4, 5],
    reduce=[
        ('sep_conv_5x5', 0), ('sep_conv_3x3', 1),
        ('sep_conv_5x5', 2), ('sep_conv_5x5', 1),
        ('dil_conv_5x5', 2), ('sep_conv_3x3', 1),
        ('sep_conv_5x5', 0), ('sep_conv_5x5', 2),
    ],
    reduce_concat=[2, 3, 4, 5]
)

# from https://github.com/tanglang96/MDENAS/blob/master/run_darts_cifar.sh
# 599M 3.78M
MdeNAS = Genotype(
    normal=[
        ('sep_conv_5x5', 1), ('sep_conv_3x3', 0),
        ('skip_connect', 0), ('sep_conv_5x5', 1),
        ('sep_conv_5x5', 3), ('sep_conv_3x3', 1),
        ('dil_conv_5x5', 3), ('max_pool_3x3', 4)
    ],
    normal_concat=[2, 3, 4, 5],
    reduce=[
        ('max_pool_3x3', 0), ('sep_conv_5x5', 1),
        ('skip_connect', 0), ('skip_connect', 1),
        ('sep_conv_3x3', 3), ('skip_connect', 2),
        ('dil_conv_3x3', 3), ('sep_conv_5x5', 0)
    ],
    reduce_concat=[2, 3, 4, 5],
)

# 558M, 3.63M, 2.57±0.07
PC_DARTS_cifar = Genotype(
    normal=[
        ('sep_conv_3x3', 1), ('skip_connect', 0),
        ('sep_conv_3x3', 0), ('dil_conv_3x3', 1),
        ('sep_conv_5x5', 0), ('sep_conv_3x3', 1),
        ('avg_pool_3x3', 0), ('dil_conv_3x3', 1)
    ],
    normal_concat=[2, 3, 4, 5],
    reduce=[
        ('sep_conv_5x5', 1), ('max_pool_3x3', 0),
        ('sep_conv_5x5', 1), ('sep_conv_5x5', 2),
        ('sep_conv_3x3', 0), ('sep_conv_3x3', 3),
        ('sep_conv_3x3', 1), ('sep_conv_3x3', 2)
    ],
    reduce_concat=[2, 3, 4, 5]
)

# from https://github.com/tanglang96/MDENAS/blob/master/run_darts_cifar.sh
# 532M, 3.43M, 2.50
PDARTS = Genotype(
    normal=[
        ('skip_connect', 0), ('dil_conv_3x3', 1),
        ('skip_connect', 0), ('sep_conv_3x3', 1),
        ('sep_conv_3x3', 1), ('sep_conv_3x3', 3),
        ('sep_conv_3x3', 0), ('dil_conv_5x5', 4)
    ],
    normal_concat=[2, 3, 4, 5],
    reduce=[
        ('avg_pool_3x3', 0), ('sep_conv_5x5', 1),
        ('sep_conv_3x3', 0), ('dil_conv_5x5', 2),
        ('max_pool_3x3', 0), ('dil_conv_3x3', 1),
        ('dil_conv_3x3', 1), ('dil_conv_5x5', 3)
    ],
    reduce_concat=[2, 3, 4, 5]
)

# from https://arxiv.org/abs/1812.09926
# 422M, 2.66
SNAS = Genotype(
    normal=[
        ('sep_conv_3x3', 0), ('sep_conv_3x3', 1),
        ('skip_connect', 0), ('dil_conv_3x3', 1),
        ('skip_connect', 1), ('skip_connect', 0),
        ('skip_connect', 0), ('sep_conv_3x3', 1)
    ],
    normal_concat=[2, 3, 4, 5],
    reduce=[
        ('max_pool_3x3', 0), ('max_pool_3x3', 1),
        ('max_pool_3x3', 1), ('skip_connect', 2),
        ('skip_connect', 2), ('max_pool_3x3', 1),
        ('max_pool_3x3', 0), ('dil_conv_5x5', 2)
    ],
    reduce_concat=[2, 3, 4, 5]
)

# threshold = 0.85 for edge and weight=10 lr = 0.0025
# 373M, 2.83, 2.54
FairDARTS_a = Genotype(
    normal=[
        ('sep_conv_3x3', 2, 0), ('sep_conv_5x5', 2, 1),
        ('max_pool_3x3', 3, 0), ('sep_conv_3x3', 4, 0)
    ],
    normal_concat=[2, 3, 4],
    reduce=[
        ('max_pool_3x3', 2, 0), ('avg_pool_3x3', 2, 1),
        ('avg_pool_3x3', 3, 0), ('dil_conv_5x5', 3, 1),
        ('avg_pool_3x3', 4, 0), ('sep_conv_5x5', 4, 1),
        ('skip_connect', 5, 0), ('skip_connect', 5, 1)
    ],
    reduce_concat=[2, 3, 4, 5]
)

# 536M, 3.88, 2.51
FairDARTS_b = Genotype(
    normal=[
        ('sep_conv_3x3', 2, 0), ('sep_conv_3x3', 2, 1),
        ('sep_conv_3x3', 3, 1), ('dil_conv_3x3', 4, 0),
        ('sep_conv_5x5', 4, 1), ('dil_conv_5x5', 5, 1)
    ],
    normal_concat=[2, 3, 4, 5],
    reduce=[
        ('skip_connect', 2, 0), ('dil_conv_3x3', 2, 1),
        ('skip_connect', 3, 0), ('dil_conv_3x3', 3, 1),
        ('max_pool_3x3', 4, 0), ('sep_conv_3x3', 4, 1),
        ('skip_connect', 5, 2), ('max_pool_3x3', 5, 0)
    ],
    reduce_concat=[2, 3, 4, 5]
)

# 400M, 2.59M, 2.50
FairDARTS_c = Genotype(
    normal=[
        ('max_pool_3x3', 2, 0), ('sep_conv_5x5', 2, 1),
        ('dil_conv_3x3', 3, 0), ('dil_conv_5x5', 3, 2),
        ('sep_conv_3x3', 4, 0),
    ],
    normal_concat=[2, 3, 4],
    reduce=[
        ('dil_conv_3x3', 2, 1), ('dil_conv_5x5', 2, 0),
        ('dil_conv_3x3', 3, 0), ('sep_conv_3x3', 3, 1),
        ('sep_conv_5x5', 4, 0), ('sep_conv_5x5', 4, 3),
        ('sep_conv_5x5', 5, 0), ('skip_connect', 5, 1)
    ],
    reduce_concat=[2, 3, 4, 5])

# 532M, 3.84M, 2.49
FairDARTS_d = Genotype(
    normal=[
        ('sep_conv_3x3', 2, 0), ('sep_conv_5x5', 2, 1),
        ('dil_conv_3x3', 3, 1), ('max_pool_3x3', 3, 0),
        ('dil_conv_3x3', 4, 0), ('dil_conv_3x3', 4, 1),
        ('sep_conv_3x3', 5, 0), ('dil_conv_5x5', 5, 1)
    ],
    normal_concat=[2, 3, 4, 5],
    reduce=[
        ('max_pool_3x3', 2, 0), ('sep_conv_5x5', 2, 1),
        ('avg_pool_3x3', 3, 0), ('dil_conv_5x5', 3, 2),
        ('dil_conv_3x3', 4, 3), ('avg_pool_3x3', 4, 0),
        ('avg_pool_3x3', 5, 0), ('skip_connect', 5, 3)
    ],
    reduce_concat=[2, 3, 4, 5]
)

# 414M, 3.12M, 2.53
FairDARTS_e = Genotype(
    normal=[
        ('sep_conv_3x3', 2, 0), ('sep_conv_3x3', 2, 1),
        ('dil_conv_3x3', 3, 1), ('dil_conv_3x3', 3, 2),
        ('dil_conv_3x3', 4, 0), ('dil_conv_5x5', 4, 1)
    ],
    normal_concat=[2, 3, 4],
    reduce=[
        ('max_pool_3x3', 2, 1), ('max_pool_3x3', 2, 0),
        ('max_pool_3x3', 3, 1), ('max_pool_3x3', 3, 0),
        ('sep_conv_5x5', 4, 1), ('max_pool_3x3', 4, 0),
        ('avg_pool_3x3', 5, 0), ('dil_conv_5x5', 5, 1)
    ],
    reduce_concat=[2, 3, 4, 5]
)

# 497M, 3.62M, 2.65
FairDARTS_f = Genotype(
    normal=[
        ('max_pool_3x3', 2, 0), ('sep_conv_3x3', 2, 1),
        ('dil_conv_3x3', 3, 1), ('sep_conv_5x5', 4, 1),
        ('sep_conv_3x3', 5, 0), ('sep_conv_3x3', 5, 1)
    ],
    normal_concat=[2, 3, 4, 5],
    reduce=[
        ('max_pool_3x3', 2, 0), ('max_pool_3x3', 2, 1),
        ('max_pool_3x3', 3, 0), ('dil_conv_3x3', 3, 1),
        ('dil_conv_3x3', 4, 2), ('max_pool_3x3', 4, 0),
        ('max_pool_3x3', 5, 0), ('sep_conv_3x3', 5, 1)
    ],
    reduce_concat=[2, 3, 4, 5]
)

# 453M, 3.375M, 2.54
FairDARTS_g = Genotype(
    normal=[
        ('sep_conv_3x3', 2, 0), ('sep_conv_3x3', 2, 1),
        ('sep_conv_5x5', 3, 1),
        ('dil_conv_3x3', 4, 0), ('sep_conv_3x3', 4, 1)
    ],
    normal_concat=[2, 3, 4],
    reduce=[
        ('avg_pool_3x3', 2, 1), ('skip_connect', 2, 0),
        ('skip_connect', 3, 2), ('max_pool_3x3', 3, 1),
        ('sep_conv_5x5', 4, 3), ('max_pool_3x3', 4, 0),
        ('dil_conv_3x3', 5, 1), ('dil_conv_3x3', 5, 4)
    ],
    reduce_concat=[2, 3, 4, 5]
)

"""Batch size = 64"""
# 469M, 3.01M
DCO_SPARSE_BS_64 = Genotype(
    normal=[
        ('sep_conv_3x3', 2, 0), ('dil_conv_3x3', 2, 1),
        ('sep_conv_5x5', 3, 0), ('dil_conv_3x3', 3, 1),
        ('max_pool_3x3', 4, 0), ('dil_conv_5x5', 5, 0)
    ],
    normal_concat=[2, 3, 4, 5],
    reduce=[
        ('skip_connect', 2, 0), ('dil_conv_5x5', 2, 1),
        ('sep_conv_5x5', 3, 0), ('sep_conv_5x5', 3, 2),
        ('sep_conv_5x5', 4, 3), ('avg_pool_3x3', 4, 0),
        ('dil_conv_3x3', 5, 0), ('dil_conv_5x5', 5, 1)
    ],
    reduce_concat=[2, 3, 4, 5]
)

DCO_EDGE_BS_64 = Genotype(
    normal=[
        ('dil_conv_3x3', 2, 0), ('sep_conv_3x3', 2, 0), ('sep_conv_3x3', 2, 1), ('dil_conv_3x3', 2, 1),
        ('max_pool_3x3', 3, 0), ('sep_conv_5x5', 3, 0), ('dil_conv_3x3', 3, 1),
        ('max_pool_3x3', 4, 0),
        ('dil_conv_5x5', 5, 0)
    ],
    normal_concat=[2, 3, 4, 5],
    reduce=[
        ('sep_conv_5x5', 2, 0), ('skip_connect', 2, 0), ('dil_conv_5x5', 2, 1), ('skip_connect', 2, 1),
        ('skip_connect', 3, 0), ('max_pool_3x3', 3, 0), ('max_pool_3x3', 3, 1), ('sep_conv_3x3', 3, 1),
        ('skip_connect', 3, 2), ('sep_conv_5x5', 3, 2),
        ('max_pool_3x3', 4, 0), ('avg_pool_3x3', 4, 0), ('dil_conv_5x5', 4, 1), ('sep_conv_3x3', 4, 1),
        ('sep_conv_5x5', 4, 2), ('skip_connect', 4, 2), ('skip_connect', 4, 3), ('sep_conv_5x5', 4, 3),
        ('max_pool_3x3', 5, 0), ('avg_pool_3x3', 5, 0), ('dil_conv_5x5', 5, 1), ('dil_conv_3x3', 5, 1),
        ('skip_connect', 5, 2), ('sep_conv_5x5', 5, 2), ('sep_conv_5x5', 5, 3), ('dil_conv_5x5', 5, 3),
        ('dil_conv_3x3', 5, 4), ('skip_connect', 5, 4)],
    reduce_concat=[2, 3, 4, 5]
)


# This function will return a Genotype from a dict.
def build_genotype_from_dict(xdict):
    def remove_value(nodes):
        return [tuple([(x[0], x[1]) for x in node]) for node in nodes]

    genotype = Genotype(
        normal=remove_value(xdict['normal']),
        normal_concat=xdict['normal_concat'],
        reduce=remove_value(xdict['reduce']),
        reduce_concat=xdict['reduce_concat'],
    )
    return genotype

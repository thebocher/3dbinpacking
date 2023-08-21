from .py3dbp import Packer, Bin, Item#, Painter

import numpy as np

from decimal import Decimal

#from matplotlib.animation import FuncAnimation

# from matplotlib import pyplot as plt

from decimal import Decimal


def decimalise(*a):
    return [Decimal(aa) for aa in a]


class PalletPacker:
    def __init__(self, bin_WHD, bin_max_weight):
        self.packer = Packer()
        self.bin = Bin('bin', bin_WHD, bin_max_weight, 0, 1)
        self.packer.addBin(self.bin)

    def create_item(self, WHD, weight):
        return Item(
            'partno', 'name', 'cube', WHD, weight, 1, 1, 
            True, 'gray', False
        )

    def add_new_item(self, WHD, weight):
        item = self.create_item(WHD, weight)
        self.packer.addItem(item)
        return item

    def add_existing_item(
            self, WHD, weight, position, rotation_type):
        item = self.create_item(decimalise(*WHD), weight)
        item.position = decimalise(*position)
        item.rotation_type = rotation_type
        x, y, z = [float(a) for a in position]
        w, h, d = [float(l) for l in item.getDimension()]
        self.bin.fit_items = np.append(
            self.bin.fit_items, np.array(
                [[
                    x, x+w, y, y+h, 0, z+d
                ]]
            ),
            axis=0,
        )
        self.bin.items.append(item)

    def pack(self):
        self.packer.pack(
            fix_point=True,
            check_stable=False,
            number_of_decimals=2
        )
        fitted_items = self.bin.items
        unfitted_items = self.bin.unfitted_items
        return fitted_items, unfitted_items


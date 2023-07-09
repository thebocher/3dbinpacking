from py3dbp import Packer, Bin, Item, Painter
import itertools
import numpy as np
from decimal import Decimal
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import time
start = time.time()

'''

This case is used to demonstrate an example of a packing complex situation.

'''

# init packing function
packer = Packer()
#  init bin
box = Bin('example2',(500, 500, 1000), 99,0,1)
packer.addBin(box)
#  add item
# packer.addItem(Item(partno='Box-5',name='test',typeof='cube', WHD=(2, 1, 3), weight=1, level=1,loadbear=100, updown=True, color='olive'))

def decimalise(*a):
    return [Decimal(aa) for aa in a]

def prepare_item(partno,name,typeof, WHD, weight, level, loadbear, updown, color, position, rotation_type):
    item = Item(partno,name,typeof, decimalise(*WHD), weight, level, loadbear, updown, 'gray')
    item.position = decimalise(*position)
    item.rotation_type = rotation_type
    x, y, z = [float(a) for a in position]
    w, h, d = item.getDimension()
    box.fit_items = np.append(
        box.fit_items, np.array(
            [[
                x, x+float(w), y, y+float(h), z, z+float(d)
            ]]
        ),
        axis=0
    )
    return item

def random_items(count, l=2, m=100):
    from random import randint
    def r(*args):
        return randint(*[int(i) for i in args])

    created_items = []
    for i in range(count):
        print(
            "packer.addItem(Item('test1', 'test','cube',(", 
            r(m, box.width/l),',',r(m, box.height/l),',', r(m, box.depth/l),
            "), 1, 1, 100, True,'red'))"
        )
        item = Item(
            'test1', 'test', 'cube', 
            (r(m, box.width/l), r(m, box.height/l), r(m, box.depth/l)),
            1, 1, 100, True, 'red'
        )
        created_items.append(item)
        packer.addItem(item)

    return created_items

created_items = random_items(1, 2, 50)

# packer.addItem(Item('test1', 'test','cube',( 144 , 117 , 489 ), 1, 1, 100, True,'red'))
# packer.addItem(Item('test1', 'test','cube',( 218 , 213 , 275 ), 1, 1, 100, True,'red'))
# packer.addItem(Item('test1', 'test','cube',( 113 , 226 , 443 ), 1, 1, 100, True,'red'))
# packer.addItem(Item('test1', 'test','cube',( 245 , 230 , 260 ), 1, 1, 100, True,'red'))
# packer.addItem(Item('test1', 'test','cube',( 154 , 185 , 292 ), 1, 1, 100, True,'red'))
# packer.addItem(Item('test1', 'test','cube',( 209 , 144 , 318 ), 1, 1, 100, True,'red'))
# packer.addItem(Item('test1', 'test','cube',( 174 , 112 , 230 ), 1, 1, 100, True,'red'))
# packer.addItem(Item('test1', 'test','cube',( 173 , 155 , 465 ), 1, 1, 100, True,'red'))
# packer.addItem(Item('test1', 'test','cube',( 224 , 245 , 283 ), 1, 1, 100, True,'red'))
# packer.addItem(Item('test1', 'test','cube',( 247 , 149 , 453 ), 1, 1, 100, True,'red'))
item0 = prepare_item("test1", "test", "cube", (Decimal('247'), Decimal('149'), Decimal('453')), 1, 1, 100, True, "red", [Decimal('0'), Decimal('0'), Decimal('0')], 0)
item1 = prepare_item("test1", "test", "cube", (Decimal('245'), Decimal('230'), Decimal('260')), 1, 1, 100, True, "red", [Decimal('0'), Decimal('149'), Decimal('0')], 0)
item2 = prepare_item("test1", "test", "cube", (Decimal('113'), Decimal('226'), Decimal('443')), 1, 1, 100, True, "red", [Decimal('0'), Decimal('379'), Decimal('0')], 1)
item3 = prepare_item("test1", "test", "cube", (Decimal('209'), Decimal('144'), Decimal('318')), 1, 1, 100, True, "red", [Decimal('0'), Decimal('155'), Decimal('260')], 0)
item4 = prepare_item("test1", "test", "cube", (Decimal('173'), Decimal('155'), Decimal('465')), 1, 1, 100, True, "red", [Decimal('0'), Decimal('0'), Decimal('453')], 0)
item5 = prepare_item("test1", "test", "cube", (Decimal('144'), Decimal('117'), Decimal('489')), 1, 1, 100, True, "red", [Decimal('209'), Decimal('245'), Decimal('275')], 0)
item6 = prepare_item("test1", "test", "cube", (Decimal('218'), Decimal('213'), Decimal('275')), 1, 1, 100, True, "red", [Decimal('245'), Decimal('245'), Decimal('0')], 0)
item7 = prepare_item("test1", "test", "cube", (Decimal('224'), Decimal('245'), Decimal('283')), 1, 1, 100, True, "red", [Decimal('247'), Decimal('0'), Decimal('0')], 0)
item8 = prepare_item("test1", "test", "cube", (Decimal('154'), Decimal('185'), Decimal('292')), 1, 1, 100, True, "red", [Decimal('247'), Decimal('0'), Decimal('283')], 0)
item9 = prepare_item("test1", "test", "cube", (Decimal('174'), Decimal('112'), Decimal('230')), 1, 1, 100, True, "red", [Decimal('353'), Decimal('245'), Decimal('275')], 1)
box.items = [item0, item1, item2, item3, item4, item5, item6, item7, item8, item9]

# calculate packing 
packer.pack(
    bigger_first=True,
    distribute_items=100,
    fix_point=True,
    check_stable=True,
    support_surface_ratio=0.75,
    number_of_decimals=0
)

# print result
b = packer.bins[0]

print('after pack')
for i, item in enumerate(b.items):
    print(
        f'item{i} = prepare_item("{item.partno}", "{item.name}", "{item.typeof}", {item.width, item.height, item.depth}, {item.weight}, {item.level}, {item.loadbear}, {item.updown}, "{item.color}", {item.position}, {item.rotation_type})'
    )

print(f'box.items = [' + ', '.join([f'item{i}' for i in range(len(b.items))]), ']')
# quit()

volume = b.width * b.height * b.depth
print(":::::::::::", b.string())

print("FITTED ITEMS:")
volume_t = 0
volume_f = 0
unfitted_name = ''
for item in b.items:
    print("partno : ",item.partno)
    print("color : ",item.color)
    print("position : ",item.position)
    print("rotation type : ",item.rotation_type)
    print("W*H*D : ",str(item.width) +'*'+ str(item.height) +'*'+ str(item.depth))
    print("volume : ",float(item.width) * float(item.height) * float(item.depth))
    print("weight : ",float(item.weight))
    volume_t += float(item.width) * float(item.height) * float(item.depth)
    print("***************************************************")
print("***************************************************")
print("UNFITTED ITEMS:")
for item in b.unfitted_items:
    print("partno : ",item.partno)
    print("color : ",item.color)
    print("W*H*D : ",str(item.width) +'*'+ str(item.height) +'*'+ str(item.depth))
    print("volume : ",float(item.width) * float(item.height) * float(item.depth))
    print("weight : ",float(item.weight))
    volume_f += float(item.width) * float(item.height) * float(item.depth)
    unfitted_name += '{},'.format(item.partno)
    print("***************************************************")
print("***************************************************")
print('space utilization : {}%'.format(round(volume_t / float(volume) * 100 ,2)))
print('residual volumn : ', float(volume) - volume_t )
print('unpack item : ',unfitted_name)
print('unpack item volumn : ',volume_f)
print("gravity distribution : ",b.gravity)
stop = time.time()
print('used time : ',stop - start)

# draw results
painter = Painter(b)
fig = painter.plotBoxAndItems(
    title=b.partno,
    alpha=0.8,
    write_num=False,
    fontsize=10
)
# [print(i.position, i.color, (i.width, i.height, i.depth), i.rotation_type) for i in box.items]
def blink(frame):
    pass
    # f = fig.figure(1)
    # for i in itertools.count():
    #     for i in f.get_children():
    #         pass
            # item.opacity = i % 10

animation = FuncAnimation(fig.figure(1), blink, interval=100)
fig.show()

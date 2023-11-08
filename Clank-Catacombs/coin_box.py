import cadquery as cq
import os
from cadquery import exporters

W_box = 290
H_market_box_outer = 65.8
W_market_box_outer = 133
T_market_box_outer = 23.4

H_coin_box_outer = H_market_box_outer
W_coin_box_outer = W_box - W_market_box_outer - 0.5
T_coin_box_outer = T_market_box_outer

T_wall = 1.2

num_compartments = 3

coin_box = (cq.Workplane()
            .box(H_coin_box_outer - 2 * T_wall,
                 W_coin_box_outer - 2 * T_wall,
                 T_coin_box_outer - T_wall)
            .faces('>Z')
            .shell(T_wall)
            .faces('+Z').faces('<Z')
            .workplane()
            )

# Create separating walls.
wall_y = (W_coin_box_outer - 2 * T_wall) / num_compartments
for i in range(num_compartments):
    coin_box = (coin_box
                .moveTo(0, W_coin_box_outer / 2 - T_wall - wall_y * i)
                .rect(H_coin_box_outer, T_wall)
                )

coin_box = coin_box.extrude(T_coin_box_outer - T_wall)

dir_cwd = os.getcwd()
dir_models = 'models'
os.makedirs(dir_models, exist_ok=True)
os.chdir(dir_models)
exporters.export(coin_box, 'coin_box.stl')
os.chdir(dir_cwd)

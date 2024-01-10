from typing import List
import cadquery as cq
import os
from cadquery import exporters

tol_tight_fit = 0.1
R_printer_fillet = 0.75
T_card_chamfer = 0.9

H_box_space = 63
W_box_space = 290
T_box_space = 37.5

T_upper_expose = 12.25
T_bottom_wall = 1.2
T_wall = 1.75


def make_misc_box(W_slots: List[int | float]) -> cq.Workplane:
    W_misc_box = sum(W_slots) + (len(W_slots) + 1) * T_wall
    H_misc_box = H_box_space
    T_misc_box = T_box_space

    misc_box = (cq.Workplane()
                .box(W_misc_box, H_misc_box, T_misc_box)
                .edges()
                .fillet(R_printer_fillet)
                )

    X_bottom = -W_misc_box / 2 + T_wall
    Y_center = 0

    T_slot = T_misc_box - T_bottom_wall
    misc_box = misc_box.faces('>Z').workplane()
    for W_slot in W_slots:
        X_center = X_bottom + W_slot / 2
        H_slot = H_misc_box - 2 * T_wall
        misc_box = (misc_box
                    .moveTo(X_center, Y_center)
                    .rect(W_slot, H_slot)
                    .extrude(-T_slot, combine='cut')
                    .moveTo(X_bottom, Y_center - H_misc_box / 2)
                    .rect(W_slot, T_wall, centered=False)
                    .extrude(-T_upper_expose, combine='cut')
                    )

        X_bottom += W_slot + T_wall

    misc_box = (misc_box
                .faces('+Z')
                .faces('not(>Z or <Z)')
                .edges('|X')
                .fillet(T_wall / 2 * 0.95)
                )
    return misc_box


W_coin_slots = [80, 65, 60]
coin_box = make_misc_box(W_coin_slots)

W_beer_box = (W_box_space
              - (sum(W_coin_slots) + (len(W_coin_slots) + 1) * T_wall)
              - 4 * tol_tight_fit)
W_beer_slot = W_beer_box - 2 * T_wall
beer_box = make_misc_box([W_beer_slot])

dir_out = 'models'
os.makedirs(dir_out, exist_ok=True)
exporters.export(coin_box, os.path.join(dir_out, 'coin_box.stl'))
exporters.export(beer_box, os.path.join(dir_out, 'beer_box.stl'))

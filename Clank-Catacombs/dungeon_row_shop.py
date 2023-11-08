import cadquery as cq
import os
from cadquery import exporters

tol_comfort = 0.3
tol_tight_fit = 0.16


T_wall = 1.2

W_card = 66.5

H_card_slot = 3
W_card_slot = W_card + 2
T_card_slot = 7


def card_holder(n_cards):
    H_outer = 30
    H_offset = 5
    W_outer = T_wall + (W_card_slot + T_wall) * n_cards
    T_base = 1.2

    n_card_holder = (cq.Workplane()
                        .box(H_outer, W_outer, T_base)
                        .faces('>Z')
                        .workplane()
                        .moveTo(H_outer / 2 - H_offset, 0)
                        .rect(-(H_card_slot + 2 * T_wall),
                              W_outer,
                              centered=(False, True))
                        .extrude(T_card_slot - T_base + T_wall)
                        )
    slot_y = W_card_slot + T_wall
    for i in range(n_cards):
        y = W_outer / 2 - T_wall - slot_y * i
        n_card_holder = (n_card_holder
                            .moveTo(H_outer / 2 - H_offset - T_wall, y)
                            .rect(-H_card_slot, -W_card_slot, centered=False)
                            )
    n_card_holder = n_card_holder.extrude(T_card_slot, combine='cut')

    n_card_holder = (n_card_holder
                        .faces('>Z')
                        .edges('not(<Y or >Y or <X or >X)')
                        .fillet(0.5)
                        )
    return n_card_holder

half_dungeon_row_shop = card_holder(3)
goblin_holder = card_holder(1)

dir_cwd = os.getcwd()
dir_models = 'models'
os.makedirs(dir_models, exist_ok=True)
os.chdir(dir_models)
exporters.export(goblin_holder, 'goblin_holder.stl')
exporters.export(half_dungeon_row_shop, 'half_dungeon_row_shop.stl')
os.chdir(dir_cwd)

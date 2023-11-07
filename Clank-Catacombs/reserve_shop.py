import cadquery as cq
import os
from cadquery import exporters

tol_comfort = 0.3
tol_tight_fit = 0.16

H_card = 92.25
W_card = 66.5
T_wall = 1.2

T_card_slot = 7
H_card_slot = 3
W_card_slot = W_card + 2

W_finger_cutout = 35
H_finger_cutout = 5

H_inner = H_card + 2 * tol_comfort
W_inner = W_card + 2 * tol_comfort

num_decks = 3
H_shop = 104.6
W_shop = T_wall + (W_inner + T_wall) * num_decks
T_shop = 43.32 - 27.6

reserve_shop = (cq.Workplane()
                .box(H_shop, W_shop, T_shop)
                .edges('|Z or <Z')
                .fillet(T_wall)
                )

# Cut card slots.
reserve_shop = reserve_shop.faces('>Z').workplane()
first_slot_y = -W_shop / 2 + T_wall + W_inner / 2
for i in range(num_decks):
    reserve_shop = (reserve_shop
                    .moveTo(H_shop / 2 - H_inner / 2 - T_wall,
                            first_slot_y + (W_inner + T_wall) * i)
                    .rect(H_inner, W_inner)
                    )
reserve_shop = reserve_shop.extrude(-(T_shop - T_wall), combine='cut')

# Note: performed separately due to visual bug.
for i in range(num_decks):
    reserve_shop = (reserve_shop
                    .moveTo(H_shop / 2 - T_wall / 2,
                            first_slot_y + (W_inner + T_wall) * i)
                    .rect(T_wall, W_finger_cutout)
                    )
reserve_shop = reserve_shop.extrude(-(T_shop - T_wall), combine='cut')

for i in range(num_decks):
    x = H_shop / 2
    y = first_slot_y + (W_inner + T_wall) * i
    reserve_shop = (reserve_shop
                    .moveTo(x, y + W_finger_cutout / 2)
                    .sagittaArc((x, y - W_finger_cutout / 2), -H_finger_cutout)
                    .close()
                    )
reserve_shop = reserve_shop.cutThruAll()

# Cut card display slots.
for i in range(num_decks):
    reserve_shop = (reserve_shop
                    .moveTo(-H_shop / 2 + 2 * T_wall,
                            first_slot_y + (W_inner + T_wall) * i)
                    .rect(H_card_slot, W_inner, centered=(False, True))
                    )
reserve_shop = reserve_shop.extrude(-T_card_slot, combine='cut')


# reserve_shop = (cq.Workplane()
#                 .box(H_card_slot, W_card_slot, T_card_slot)
#                 .faces('>Z')
#                 .shell(T_wall)
#                 )

print(T_shop)

dir_cwd = os.getcwd()
dir_models = 'models'
os.makedirs(dir_models, exist_ok=True)
os.chdir(dir_models)
exporters.export(reserve_shop, 'reserve_shop.stl')
os.chdir(dir_cwd)

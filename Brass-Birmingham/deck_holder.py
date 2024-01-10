import cadquery as cq
import os
from cadquery import exporters

tol_tight_fit = 0.1
R_printer_fillet = 0.75
T_card_chamfer = 0.9

W_finger_slot = 22

T_floor = 1.2
T_wall = 1.75

H_box_space = 227
T_box_space = 27

W_dragonshield = 66.7
H_dragonshield = 92.6

N_slots = 3

W_dragonshield_fit = W_dragonshield + 2 * tol_tight_fit
H_dragonshield_fit = H_dragonshield + 2 * tol_tight_fit

# Dividing wall between decks.
T_dividing_wall = (H_box_space - N_slots * W_dragonshield_fit) / (N_slots + 1)

W_deck_box = H_box_space
H_deck_box = H_dragonshield_fit + 2 * T_wall
T_deck_box = T_box_space

deck_holder = (cq.Workplane()
               .box(W_deck_box, H_deck_box, T_deck_box)
               )

X_bottom = -W_deck_box / 2 + T_dividing_wall
Y_center = 0

deck_holder = (deck_holder
               .faces('>Z')
               .workplane()
               )
for i in range(N_slots):
    X_center = (X_bottom
                + i * (W_dragonshield_fit + T_dividing_wall)
                + W_dragonshield_fit / 2)
    deck_holder = (deck_holder
                   .moveTo(X_center, Y_center)
                   .rect(W_dragonshield_fit, H_dragonshield_fit)
                   .extrude(-(T_deck_box - T_floor), combine='cut')
                   .moveTo(X_center, Y_center - H_deck_box / 2)
                   .circle(W_finger_slot / 2)
                   .moveTo(X_center, Y_center + H_deck_box / 2)
                   .circle(W_finger_slot / 2)
                   .extrude(-T_box_space, combine='cut')
                   )

deck_holder = (deck_holder
               .faces('<Z or >X or <X or >Y or <Y')
               .edges()
               .fillet(R_printer_fillet)
               .edges('>Z')
               .edges('not(>X or <X or >Y or <Y)')
               .edges('not(>Y or <Y)')
               .chamfer(T_card_chamfer)
               )

dir_out = 'models'
os.makedirs(dir_out, exist_ok=True)
exporters.export(deck_holder, os.path.join(dir_out, 'deck_holder.stl'))

print(W_deck_box, H_deck_box, T_deck_box)

import cadquery as cq
import os
from cadquery import exporters

tol_tight_fit = 0.1
T_wall = 1.75
R_printer_fillet = 0.75

W_box_space = 290
H_box_space = 227
T_box_space = 27

W_player_box = 32.4
W_deck_box = 96.3
N_players = 4
W_misc_box = 64.75

misc_box = (cq.Workplane()
            .box(W_misc_box, H_box_space, T_box_space)
            .faces('>Z')
            .workplane()
            .rect(W_misc_box - 2 * T_wall, H_box_space - 2 * T_wall)
            .extrude(-(T_box_space - T_wall), combine='cut')
            .faces('>X or <X or >Y or <Y or >Z or <Z')
            .edges()
            .fillet(R_printer_fillet)
            )

dir_out = 'models'
os.makedirs(dir_out, exist_ok=True)
exporters.export(misc_box, os.path.join(dir_out, 'misc_box.stl'))

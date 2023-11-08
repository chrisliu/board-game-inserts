import cadquery as cq
import os
import math
from cadquery import exporters

tol_comfort = 0.3
tol_tight_fit = 0.16

H_card = 92.25
W_card = 66.5
T_wall = 0.8
T_player_inner_deck = 6.5
T_player_inner_cube = 11.5
T_lip = 4

H_finger_cutout = 20
W_finger_cutout = 35

T_dungeon_inner_deck = 40.32
W_dungeon_finger_cutout = 20
H_dungeon_finger_cutout = 5

H_inner = H_card + 2 * tol_comfort
W_inner = W_card + 2 * tol_comfort

player_cube_inner = (cq.Workplane()
                     .box(H_inner, W_inner, T_player_inner_cube)
                     .faces('>Z')
                     .shell(T_wall)
                     .faces('+X').faces('<X')
                     .workplane()
                     .moveTo(W_inner / 2, T_player_inner_cube / 2)
                     .radiusArc((W_inner / 2 - T_player_inner_cube, -T_player_inner_cube / 2),
                                T_player_inner_cube)
                     .lineTo(W_inner / 2, -T_player_inner_cube / 2)
                     .close()
                     .mirrorY()
                     .extrude(H_inner)
                     )
H_inner_fit = H_inner + 2 * T_wall + 2 * tol_tight_fit
W_inner_fit = W_inner + 2 * T_wall + 2 * tol_tight_fit
T_player_inner_cube_fit = T_player_inner_cube + T_wall + 2 * tol_tight_fit
T_player_inner_all = T_player_inner_cube_fit + T_wall + T_player_inner_deck
H_outer = H_inner_fit + 2 * T_wall
W_outer = W_inner_fit + T_wall
T_player_outer = T_player_inner_all + 2 * T_wall
player_deck_box = (cq.Workplane()
                   .box(H_outer, W_outer, T_player_outer)
                   .edges('<Y or |Y')
                   .fillet(T_wall)
                   .faces('>Y')
                   .workplane()
                   .moveTo(0, -T_player_inner_all / 2)
                   .rect(H_inner, T_player_inner_deck, centered=(True, False))
                   .extrude(-W_inner, combine='cut')
                   .moveTo(0, -T_player_inner_all / 2 + T_player_inner_deck + T_wall)
                   .rect(H_inner_fit, T_player_inner_cube_fit, centered=(True, False))
                   .extrude(-W_inner_fit, combine='cut')
                   .faces('<Z')
                   .workplane(origin=(0, 0, 0))
                   .moveTo(W_finger_cutout / 2, W_outer / 2)
                   .sagittaArc((-W_finger_cutout / 2, W_outer / 2),
                               H_finger_cutout)
                   .close()
                   .extrude(-(T_player_outer - T_wall), combine='cut')
                   )

T_slit = 7
T_wall_vent = 2.5
ratio = 1.9
angle = 45  # degrees
sketch_vents = (cq.Sketch()
                .rarray(T_slit + T_wall_vent, 1,
                        math.ceil(
                            W_inner / math.cos(math.radians(angle)) /
                            (T_slit + T_wall_vent)
                        ) + 2, 1)
                .rect(T_slit, H_inner / math.sin(math.radians(angle)))
                )
sketch_vents_support = (cq.Sketch()
                        .rarray(ratio * (T_slit + T_wall_vent), 1,
                        math.ceil(
                            W_inner / math.cos(math.radians(angle)) /
                            (T_slit + T_wall_vent)
                        ) + 2, 1)
                        .rect(T_wall_vent, H_inner / math.sin(math.radians(angle)))
                        )

r = (cq.Workplane()
     .rect(H_inner - 2 * T_wall_vent, W_inner - 2 * T_wall_vent)
     .extrude(T_wall)
     )

vents_support = (cq.Workplane()
                 .placeSketch(sketch_vents_support)
                 .extrude(T_wall)
                 .rotateAboutCenter((0, 0, 1), -45)
                 )
vents = (cq.Workplane()
         .placeSketch(sketch_vents)
         .extrude(T_wall)
         .rotateAboutCenter((0, 0, 1), 45)
         .intersect(r)
         .cut(vents_support)
         .edges('|Z')
         .fillet(0.6)
         )

player_deck_box = (player_deck_box
                   .cut(vents
                        .translate((0, 0, T_player_outer / 2 - T_wall))
                        )
                   )

T_dungeon_inner_fit = T_dungeon_inner_deck + T_wall + 2 * tol_tight_fit
dungeon_deck_box = (cq.Workplane()
                    .box(H_inner_fit, W_inner_fit, T_dungeon_inner_fit)
                    .faces('>Y')
                    .shell(T_wall)
                    .faces('<Z')
                    .workplane(origin=(0, -T_wall / 2, 0))
                    .moveTo(W_finger_cutout / 2, W_outer / 2)
                    .sagittaArc((-W_finger_cutout / 2, W_outer / 2),
                                H_finger_cutout)
                    .close()
                    .extrude(-(T_dungeon_inner_fit + T_wall), combine='cut')
                    .cut(vents
                         .translate((0, 0, (T_dungeon_inner_fit + 2 * T_wall) / 2 - T_wall))
                         )
                    )

H_deck_outer = H_inner + 2 * T_wall
dungeon_deck_inner = (cq.Workplane()
                      .box(H_inner, W_inner, T_dungeon_inner_deck)
                      .faces('>Z')
                      .shell(T_wall)
                      .faces('+Z').faces('<Z')
                      .workplane()
                      .rect(H_deck_outer, W_dungeon_finger_cutout)
                      .extrude(T_dungeon_inner_fit, combine='cut')
                      .moveTo(H_deck_outer / 2, W_dungeon_finger_cutout / 2)
                      .sagittaArc((H_deck_outer / 2, -W_dungeon_finger_cutout / 2),
                                  -H_dungeon_finger_cutout / 2)
                      .close()
                      .mirrorY()
                      .extrude(-T_wall, combine='cut')
                      )

# show_object(dungeon_deck_box)
show_object(dungeon_deck_inner)

# show_object(vents)
# show_object(player_deck_box)
# show_object(vents_support)

dir_cwd = os.getcwd()
dir_models = 'models'
os.makedirs(dir_models, exist_ok=True)
os.chdir(dir_models)
# exporters.export(deck_inner, 'deck_inner.stl')
exporters.export(player_cube_inner, 'player_cube_inner.stl')
exporters.export(player_deck_box, 'player_deck_box.stl')
exporters.export(dungeon_deck_inner, 'dungeon_deck_inner.stl')
exporters.export(dungeon_deck_box, 'dungeon_deck_box.stl')
os.chdir(dir_cwd)

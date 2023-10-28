import cadquery as cq
from cadquery import exporters

tol_comfort = 0.3
tol_tight_fit = 0.1
T_wall = 0.8

T_inner_40 = 25.5
T_inner_30 = T_inner_40 / 40 * 30
T_inner_28 = T_inner_40 / 40 * 28
T_inner_15 = T_inner_40 / 40 * 15
T_inner_12 = T_inner_40 / 40 * 12
H_card = 92.25
W_card = 66.5

W_border = 4.5

H_inner = H_card + 2 * tol_comfort
W_inner = W_card + 2 * tol_comfort

# Standard Deck Box


def make_box_inner(H_inner, W_inner, T_inner, T_wall, W_border, tol_tight_fit):
    box_inner = (cq.Workplane()
                 .box(H_inner, W_inner, T_inner)
                 .faces('>X')
                 .shell(T_wall)
                 .faces('<X')
                 .workplane()
                 .moveTo(0, -T_inner / 2 + W_border)
                 .rect(W_inner - 2 * W_border, T_inner + T_wall - W_border,
                       centered=(True, False))
                 .cutThruAll()
                 )

    T_gap = T_inner + T_wall - W_border
    print(T_gap, W_border)
    if T_gap >= W_border:
        box_inner = (box_inner
                     .faces('+Z').faces('>Z[1]')
                     .edges('|X')
                     .fillet(W_border)
                     )
    return box_inner


def make_box_outer(H_inner, W_inner, T_inner, T_wall, W_border, tol_tight_fit):
    box_outer = (cq.Workplane()
                 .box(H_inner + T_wall + 2 * tol_tight_fit,
                      W_inner + 2 * T_wall + tol_tight_fit,
                      T_inner + 2 * T_wall + 2 * tol_tight_fit)
                 .faces('>Y')
                 .shell(T_wall)
                 )

    window_profile = (cq.Sketch()
                      .rect(H_inner - 2 * W_border, W_inner - 2 * W_border)
                      .vertices()
                      .fillet(W_border)
                      )

    box_outer = (box_outer
                 .faces('>Z')
                 .moveTo(0, -T_wall)
                 .placeSketch(window_profile)
                 .cutThruAll()
                 )
    return box_outer


def make_double_box_outer(H_inner, W_inner, T_deck1, T_deck2, T_wall, W_border,
                          tol_tight_fit):
    T_dd_inner = T_deck1 + T_deck2 + T_wall + 4 * tol_tight_fit

    double_box_outer = (cq.Workplane()
                        .box(H_inner + T_wall + 2 * tol_tight_fit,
                             W_inner + 2 * T_wall + tol_tight_fit,
                             T_dd_inner)
                        .faces('>Y')
                        .shell(T_wall)
                        )

    window_profile = (cq.Sketch()
                      .rect(H_inner - 2 * W_border, W_inner - 2 * W_border)
                      .vertices()
                      .fillet(W_border)
                      )

    double_box_outer = (double_box_outer
                        .faces('>Z')
                        .moveTo(0, -T_wall)
                        .placeSketch(window_profile)
                        .cutThruAll()
                        )

    wall_pos = T_dd_inner / 2 - T_deck1 - 2 * tol_tight_fit - T_wall / 2

    # print(wall_pos, T_deck1, T_deck2, T_dd_inner)

    double_box_outer = (double_box_outer
                        .faces('>Y')
                        .workplane()
                        .moveTo(0, wall_pos)
                        .rect(H_inner + 2 * T_wall + 2 * tol_tight_fit, T_wall)
                        .extrude(-W_inner - tol_tight_fit)
                        )
    return double_box_outer


box_inner_40 = make_box_inner(
    H_inner, W_inner, T_inner_40, T_wall, W_border, tol_tight_fit)
box_outer_40 = make_box_outer(
    H_inner, W_inner, T_inner_40, T_wall, W_border, tol_tight_fit)

box_inner_30 = make_box_inner(
    H_inner, W_inner, T_inner_30, T_wall, W_border, tol_tight_fit)
box_outer_30 = make_box_outer(
    H_inner, W_inner, T_inner_30, T_wall, W_border, tol_tight_fit)

box_inner_28 = make_box_inner(
    H_inner, W_inner, T_inner_28, T_wall, W_border, tol_tight_fit)
box_outer_28 = make_box_outer(
    H_inner, W_inner, T_inner_28, T_wall, W_border, tol_tight_fit)

box_inner_15 = make_box_inner(
    H_inner, W_inner, T_inner_15, T_wall, W_border, tol_tight_fit)
box_outer_15 = make_box_outer(
    H_inner, W_inner, T_inner_15, T_wall, W_border, tol_tight_fit)

box_inner_12 = make_box_inner(
    H_inner, W_inner, T_inner_12, T_wall, W_border, tol_tight_fit)
box_outer_12 = make_box_outer(
    H_inner, W_inner, T_inner_12, T_wall, W_border, tol_tight_fit)

# Double deck box.
T_deck1 = T_inner_28 + 2 * T_wall
T_deck2 = T_inner_12 + 2 * T_wall


double_box_outer_40_30 = make_double_box_outer(H_inner, W_inner,
                                               T_inner_40 + 2 * T_wall,
                                               T_inner_30 + 2 * T_wall,
                                               T_wall, W_border,
                                               tol_tight_fit)
double_box_outer_28_12 = make_double_box_outer(H_inner, W_inner,
                                               T_inner_28 + 2 * T_wall,
                                               T_inner_12 + 2 * T_wall,
                                               T_wall, W_border,
                                               tol_tight_fit)
double_box_outer_15_15 = make_double_box_outer(H_inner, W_inner,
                                               T_inner_15 + 2 * T_wall,
                                               T_inner_15 + 2 * T_wall,
                                               T_wall, W_border,
                                               tol_tight_fit)


show_object(double_box_outer_40_30)

exporters.export(box_inner_40, 'deck_box_40.stl')
exporters.export(box_outer_40, 'deck_box_outer_40.stl')

exporters.export(box_inner_30, 'deck_box_30.stl')
exporters.export(box_outer_30, 'deck_box_outer_30.stl')

exporters.export(box_inner_28, 'deck_box_28.stl')
exporters.export(box_outer_28, 'deck_box_outer_28.stl')

exporters.export(box_inner_15, 'deck_box_15.stl')
exporters.export(box_outer_15, 'deck_box_outer_15.stl')

exporters.export(box_inner_12, 'deck_box_12.stl')
exporters.export(box_outer_12, 'deck_box_outer_12.stl')

exporters.export(double_box_outer_40_30, 'double_deck_box_40_30.stl')
exporters.export(double_box_outer_28_12, 'double_deck_box_28_12.stl')
exporters.export(double_box_outer_15_15, 'double_deck_box_15_15.stl')

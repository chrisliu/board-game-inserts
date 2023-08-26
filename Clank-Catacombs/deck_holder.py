import os
import cadquery as cq
from typing import Type, Self


class CuboidSpec:
    width: float = 0
    height: float = 0
    thickness: float = 0

    @classmethod
    @property
    def W(cls: Type[Self]) -> float:
        return cls.width

    @classmethod
    @property
    def H(cls: Type[Self]) -> float:
        return cls.height

    @classmethod
    @property
    def T(cls: Type[Self]) -> float:
        return cls.thickness


class StandardCard(CuboidSpec):
    width: float = 63
    height: float = 88
    thickness: float = 0.6


class DragonShieldSleeve(CuboidSpec):
    width: float = 66.4
    height: float = 92.2
    thickness: float = 0.6


class SquareMapTile(CuboidSpec):
    width: float = 100
    height: float = 100
    thickness: float = 1.6


class StartingMapTile(CuboidSpec):
    width: float = 100
    height: float = 200
    thickness: float = 1.6


class GameBoxInner(CuboidSpec):
    width: float = 291
    height: float = 291
    thickness: float = 78.5


class PlayerToken(CuboidSpec):
    width: float = 18
    height: float = 18
    thickness: float = 10.3


class ClankCube(CuboidSpec):
    width: float = 8.2
    height: float = 8.2
    thickness: float = 8.2


class Gridfinity:
    tol = 0.5

    @classmethod
    def make_base_tool(cls: Type[Self],
                       W_top: float = 42,
                       H_top: float = 42,
                       R_top: float = 7.75,  # estimated
                       R_middle: float = 3.45,  # estimated
                       R_bottom: float = 1.85,  # estimated
                       T_top: float = 2.15,
                       T_middle: float = 1.8,
                       T_bottom: float = 0.7,
                       T_bottom_extend: float = 0,
                       T_top_extend: float = 0,
                       ) -> cq.Workplane:
        return cls._make_profile(W_top, H_top, R_top, R_middle, R_bottom,
                                 T_top, T_middle, T_bottom, T_bottom_extend,
                                 T_top_extend)

    @classmethod
    def make_stacking_tool(cls: Type[Self],
                           W_top: float = 41.5,
                           H_top: float = 41.5,
                           R_top: float = 7.5,
                           R_middle: float = 3.2,
                           R_bottom: float = 1.6,
                           T_top: float = 1.9,
                           T_middle: float = 1.8,
                           T_bottom: float = 0.7,
                           T_bottom_extend: float = 0,
                           T_top_extend: float = 0,
                           ) -> cq.Workplane:
        return cls._make_profile(W_top, H_top, R_top, R_middle, R_bottom,
                                 T_top, T_middle, T_bottom, T_bottom_extend,
                                 T_top_extend)

    @classmethod
    def T_stack_wall(cls: Type[Self],
                     T_top: float = 1.9,
                     T_bottom: float = 0.7,
                     ) -> float:
        return T_top + T_bottom

    @classmethod
    def T_interface(cls: Type[Self],
                    T_top: float = 2.15,
                    T_middle: float = 1.8,
                    T_bottom: float = 0.8) -> float:
        return T_top + T_middle + T_bottom

    @classmethod
    def make_module_interface(cls: Type[Self],
                              W_top: float = 41.5,
                              H_top: float = 41.5,
                              R_top: float = 7.5,
                              R_middle: float = 3.2,
                              R_bottom: float = 1.6,
                              T_top: float = 2.15,
                              T_middle: float = 1.8,
                              T_bottom: float = 0.8,
                              T_bottom_extend: float = 0,
                              T_top_extend: float = 0,
                              ) -> cq.Workplane:
        return cls._make_profile(W_top, H_top, R_top, R_middle, R_bottom,
                                 T_top, T_middle, T_bottom, T_bottom_extend,
                                 T_top_extend)

    @classmethod
    def module_profile(cls: Type[Self],
                       W_top: float = 41.5,
                       H_top: float = 41.5,
                       R_top: float = 7.5,
                       ) -> cq.Sketch:
        return cls._rounded_rectangle(W_top, H_top, R_top)

    @classmethod
    def _rounded_rectangle(cls: Type[Self], w: float, h: float, r: float
                           ) -> cq.Sketch:
        return (cq.Sketch()
                .rect(w, h)
                .vertices()
                .fillet(r)
                )

    @classmethod
    def _make_profile(cls: Type[Self],
                      W_top: float,
                      H_top: float,
                      R_top: float,
                      R_middle: float,
                      R_bottom: float,
                      T_top: float,
                      T_middle: float,
                      T_bottom: float,
                      T_bottom_extend: float,
                      T_top_extend: float,
                      ) -> cq.Workplane:
        W_middle = W_top - 2 * T_top
        W_bottom = W_top - 2 * (T_bottom + T_top)
        H_middle = H_top - 2 * T_top
        H_bottom = H_top - 2 * (T_bottom + T_top)

        bottom_profile = cls._rounded_rectangle(W_bottom, H_bottom, R_bottom)
        middle_profile = cls._rounded_rectangle(W_middle, H_middle, R_middle)
        top_profile = cls._rounded_rectangle(W_top, H_top, R_top)
        base_tool = cq.Workplane()

        if T_bottom_extend > 0:
            base_tool = (base_tool
                         .placeSketch(bottom_profile)
                         .extrude(T_bottom_extend)
                         .faces('>Z')
                         .workplane())

        base_tool = (base_tool
                     .placeSketch(bottom_profile,
                                  middle_profile.moved(
                                      cq.Location(cq.Vector(0, 0, T_bottom))))
                     .loft()
                     .faces('>Z')
                     .workplane()
                     .placeSketch(middle_profile,
                                  middle_profile.moved(
                                      cq.Location(cq.Vector(0, 0, T_middle))))
                     .loft()
                     .faces('>Z')
                     .workplane()
                     .placeSketch(middle_profile,
                                  top_profile.moved(
                                      cq.Location(cq.Vector(0, 0, T_top))))
                     .loft()
                     )

        if T_top_extend > 0:
            base_tool = (base_tool
                         .faces('>Z')
                         .workplane()
                         .placeSketch(top_profile)
                         .extrude(T_top_extend)
                         )

        return base_tool


# Create starting deck two piece holder.
card: Type[CuboidSpec] = DragonShieldSleeve
tol = 0.75  # Comfort tolerance.
num_cards = 10

tol_fit = 0.3  # 0.3
T_pad = 3.8  # s.t. the overall thickness is half the box thickness
T_token_floor = 1
T_token_inner = PlayerToken.T + 1 + T_pad
T_token_all = T_token_floor + T_token_inner
T_token_wall = 1.5
T_cards = num_cards * card.T * 1.5  # Sleeves are extra puffy.
T_interface = Gridfinity.T_interface()
T_inner = T_cards + T_pad
T_floor = 0.05
T_inner_max = T_inner + T_interface + T_token_all + tol_fit
T_all = T_inner_max + T_floor
W_inner = card.W + 2 * tol
H_inner = card.H + 2 * tol
W_inner_max = W_inner + 2 * (T_token_wall + tol_fit)
H_inner_max = H_inner + T_token_wall + 2 * tol_fit
T_wall = Gridfinity.T_stack_wall()
W_outer = W_inner_max + 2 * T_wall
H_outer = H_inner_max + 2 * T_wall
W_grid = W_outer + Gridfinity.tol
H_grid = H_outer + Gridfinity.tol
W_grid_outer = W_grid + 1
H_grid_outer = H_grid + 1
R_bottom = 1.6  # Need some way to backreference Gridfinity defaults.
W_clearance = 10
H_lip = 10

W_token = W_inner_max - 2 * tol_fit
H_token = H_inner_max - 2 * tol_fit
W_token_inner = W_token - 2 * T_token_wall
H_token_inner = H_token - 2 * T_token_wall

X_lip = (W_inner_max - 2 * W_clearance) / 2
Y_lip = -H_outer / 2
H_lip_from_wall = H_lip - T_wall
card_holder = (cq.Workplane()
               .tag('base')
               .placeSketch(Gridfinity.module_profile(W_outer, H_outer))
               .extrude(T_all)
               .faces('>Z')
               .workplane()
               .tag('top')
               .placeSketch(Gridfinity.module_profile(W_inner_max,
                                                      H_inner_max,
                                                      R_bottom))
               .extrude(-(T_interface + T_token_all + tol_fit), combine='cut')
               .workplaneFromTagged('top')
               .placeSketch(Gridfinity.module_profile(W_inner,
                                                      H_inner,
                                                      R_bottom)
                            .moved(cq.Location(
                                cq.Vector(0, -(T_token_wall + tol_fit) / 2, 0))))
               .extrude(-T_inner_max, combine='cut')
               .workplaneFromTagged('top')
               .moveTo(-W_inner / 2, Y_lip + T_wall)
               .rect(W_inner, H_inner / 2, centered=False)
               .extrude(-T_inner_max, combine='cut')
               .workplaneFromTagged('top')
               .moveTo(0, Y_lip + T_wall / 2)
               .rect(W_inner_max - 2 * W_clearance, T_wall)
               .extrude(-T_inner_max, combine='cut')
               .faces('<X[4]')
               .edges('|Z and >Y')
               .fillet(T_wall / 2 * 0.6)
               .faces('<X[3]')
               .edges('|Z and >Y')
               .fillet(T_wall / 2 * 0.6)
               )

stack_tool = (Gridfinity.make_stacking_tool(W_outer, H_outer)
              .translate((0, 0, T_all - 4.4))
              )

card_holder = (card_holder.cut(stack_tool)
               )

module_interface = Gridfinity.make_module_interface(W_outer, H_outer)
card_holder = (card_holder
               .translate((0, 0, 4.75))
               .union(module_interface)
               .workplaneFromTagged('base')
               .moveTo(0, Y_lip)
               .lineTo(X_lip, Y_lip)
               .line(0, T_wall)
               .radiusArc((X_lip - H_lip_from_wall, Y_lip + H_lip),
                          -H_lip_from_wall)
               .lineTo(0, Y_lip + H_lip)
               .mirrorY()
               .cutThruAll()
               )

card_holder = (card_holder
               .faces('<X[5]')
               .edges('|Z and <Y')
               .fillet(T_wall / 2 * 0.6)
               .faces('<X[6]')
               .edges('|Z and <Y')
               .fillet(T_wall / 2 * 0.6)
               .faces('<Z')
               .edges('not %LINE')
               .edges('<<Y[1]')
               .chamfer(0.35)
               )


print(T_cards)
print(Gridfinity.T_interface())

show_object(card_holder, name="card holder")

base_tool = Gridfinity.make_base_tool(W_grid, H_grid)
grid = (cq.Workplane()
        .rect(W_grid_outer, H_grid_outer)
        .extrude(4.65)
        .cut(base_tool)
        )


show_object(grid, name="grid")

# W_token -= 2 * 0.15
# H_token -= 2 * 0.15
# W_token_inner -= 2 * 0.15
# H_token_inner -= 2 * 0.15

H_pad = 2.5
T_expose = ClankCube.T + 2.5
T_cut = T_token_inner - T_expose
X_profile = H_token_inner / 2 - H_pad
token_holder = (cq.Workplane()
                .rect(W_token, H_token)
                .extrude(T_token_all)
                .faces('>Z')
                .placeSketch(Gridfinity.module_profile(W_token_inner,
                                                       H_token_inner,
                                                       R_bottom))
                .extrude(-T_token_inner, combine='cut')
                .faces('>X')
                .workplane()
                .moveTo(0, T_token_all)
                .lineTo(X_profile, T_token_all)
                .spline([
                    (X_profile, T_token_all),
                    (X_profile - T_cut * 0.25, T_token_all - T_cut * 0.1),
                    (X_profile - T_cut * 0.5, T_token_all - T_cut * 0.5),
                    (X_profile - T_cut * 0.75, T_token_all - T_cut * 0.9),
                    (X_profile - T_cut, T_token_all - T_cut),
                ])
                .lineTo(0, T_token_all - T_cut)
                .close()
                .mirrorY()
                .extrude(-W_token, combine='cut')  # cutThruAll doesn't work :(
                .faces('>Y')
                # WTF is this bug???
                .workplane()
                .moveTo(W_token / 2 + W_token_inner / 2, T_token_floor + T_expose)
                # .lineTo(W_token_inner / 2 - T_expose, T_token_floor)
                .radiusArc((W_token / 2 + W_token_inner / 2 - T_expose, T_token_floor),
                           T_expose)
                .lineTo(W_token / 2 + W_token_inner / 2, T_token_floor)
                .close()
                .extrude(-H_token, combine='a')
                .moveTo(W_token / 2 - W_token_inner / 2, T_token_floor + T_expose)
                # .lineTo(W_token_inner / 2 - T_expose, T_token_floor)
                .radiusArc((W_token / 2 - W_token_inner / 2 + T_expose, T_token_floor),
                           -T_expose)
                .lineTo(W_token / 2 - W_token_inner / 2, T_token_floor)
                .close()
                .extrude(-H_token, combine='a')
                .faces('>Y or <Y')
                .edges('|Z')
                .fillet(R_bottom)
                .faces('+Z')
                .faces('not(>Z or <Z)')
                .edges('|Y')
                .fillet(T_token_wall / 2 * 0.6)
                )

token_holder = (token_holder
                .translate((0, 0, T_all + 4.75 - 4.4 - T_token_all))
                )

show_object(token_holder, 'token holder')


out_dir = 'models'
os.makedirs(out_dir, exist_ok=True)
cq.exporters.export(card_holder, os.path.join(out_dir, 'card_holder.stl'))
cq.exporters.export(token_holder, os.path.join(out_dir, 'token_holder.stl'))
cq.exporters.export(grid, os.path.join(out_dir, 'grid.stl'))

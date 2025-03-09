import math
import streamlit as st
from decimal import Decimal, getcontext

# Set precision to 15 decimal places
getcontext().prec = 15

def parse_dms(dms_str):
    try:
        d, m, s = map(float, dms_str.split("-"))
        return d + (m / 60) + (s / 3600)
    except ValueError:
        st.error("❌ Invalid DMS format. Please enter as D-M-S (e.g., 30-15-20)")
        return None

# โปรแกรม 1: Deviate NE
def pile_deviate_ne():
    """Calculate deviation in North/East direction."""
    st.title("Deviate NE")
    while True:
        n_P = st.text_input("Enter Name (or leave empty to quit): ").strip()
        if not n_P:
            break

        Azi_str = st.text_input("Enter Azimuth Structure (D-M-S): ")
        Azi_S = parse_dms(Azi_str)
        if Azi_S is None:
            continue

        pile_DeN = st.number_input("Enter Design North (m): ", min_value=0.0)
        pile_DeE = st.number_input("Enter Design East (m): ", min_value=0.0)
        pile_AN = st.number_input("Enter Actual North (m): ", min_value=0.0)
        pile_AE = st.number_input("Enter Actual East (m): ", min_value=0.0)

        # คำนวณค่าความเบี่ยงเบน
        dNP, dEP = pile_AN - pile_DeN, pile_AE - pile_DeE
        Dev = math.hypot(dNP, dEP)

        # คำนวณมุมเบี่ยงเบน
        AziP = (math.degrees(math.atan2(dEP, dNP)) + 360) % 360
        delta_rad = math.radians((AziP - Azi_S + 360) % 360)
        os, chan = Dev * math.sin(delta_rad), Dev * math.cos(delta_rad)

        st.write(f"ΔN: {dNP:.3f}m | ΔE: {dEP:.3f}m | CH: {chan:.3f}m | O/S: {os:.3f}m | Deviation: {Dev:.3f}m |\n")

# โปรแกรม 2: Deviate Angle
def pile_deviate_ang():
    st.title("Deviate Angle")
    st_n = st.number_input("Enter Occ North: ", min_value=0.0)
    st_e = st.number_input("Enter Occ East: ", min_value=0.0)
    bs_n = st.number_input("Enter Bs North: ", min_value=0.0)
    bs_e = st.number_input("Enter Bs East: ", min_value=0.0)

    while True:
        n_P = st.text_input("Enter Name (or leave empty to quit): ").strip()
        if not n_P:
            break

        ang_pi = st.text_input("Enter Angle To Point (D-M-S): ")
        dis_p = st.number_input("Enter Distance To Point (m): ", min_value=0.0)
        Azi_str = st.text_input("Enter Azimuth Structure (D-M-S): ")
        pile_DeN = st.number_input("Enter Design North (m): ", min_value=0.0)
        pile_DeE = st.number_input("Enter Design East (m): ", min_value=0.0)

        ang_pile, Azi_S = parse_dms(ang_pi), parse_dms(Azi_str)
        dis_p, pile_DeN, pile_DeE = map(float, [dis_p, pile_DeN, pile_DeE])
        if ang_pile is None or Azi_S is None:
            continue

        Azi = (math.degrees(math.atan2(bs_e - st_e, bs_n - st_n)) + 360) % 360
        Azi_rad, Ang_pile_rad = math.radians(Azi), math.radians(ang_pile)
        Ac_NN, Ac_EE = st_n + dis_p * math.cos(Azi_rad + Ang_pile_rad), st_e + dis_p * math.sin(Azi_rad + Ang_pile_rad)

        dNP, dEP = Ac_NN - pile_DeN, Ac_EE - pile_DeE
        Dev = math.hypot(dNP, dEP)

        AziP = (math.degrees(math.atan2(dEP, dNP)) + 360) % 360
        delta_rad = math.radians(AziP - Azi_S)
        os, chan = Dev * math.sin(delta_rad), Dev * math.cos(delta_rad)

        st.write(f"ΔN: {dNP:.3f}m | ΔE: {dEP:.3f}m | CH: {chan:.3f}m | O/S: {os:.3f}m | Deviation: {Dev:.3f}m |\n")

# โปรแกรม 3: Azimuth & Distance
def azimuth_distance():
    st.title("Azimuth & Distance")
    try:
        st_d = st.text_input("Enter Start Name: ")
        st_n = st.number_input("Enter N: ", min_value=0.0)
        st_e = st.number_input("Enter E: ", min_value=0.0)
        bs_d = st.text_input("Enter End Name: ")
        bs_n = st.number_input("Enter N: ", min_value=0.0)
        bs_e = st.number_input("Enter E: ", min_value=0.0)
    except ValueError:
        st.error("❌ Invalid input.")
        return

    dN, dE, Dist = bs_n - st_n, bs_e - st_e, math.hypot(bs_n - st_n, bs_e - st_e)
    Azi = (math.degrees(math.atan2(dE, dN)) + 360) % 360
    st.write(f"Azimuth: {Azi:.3f}° | Distance: {Dist:.3f}m")

# โปรแกรม 4: Circular Curve
def circular_curve():
    st.title("Circular Curve")

    def parse_angle(angle_str):
        parts = list(map(float, angle_str.split("-")))
        return parts[0] + parts[1] / 60 + parts[2] / 3600

    def calculate_curve(pi_s, pi_n, pi_e, def_angle, curve_direction, radius, az_to_pi, offset_distance):
        deflection_angle = parse_angle(def_angle)
        azimuth_to_pi = parse_angle(az_to_pi)
        reverse_azimuth = azimuth_to_pi - 180 if azimuth_to_pi > 180 else azimuth_to_pi + 180

        lc = radius * deflection_angle * (math.pi / 180)
        t = radius * math.tan((deflection_angle / 2) * (math.pi / 180))
        bc_s = pi_s - t
        ec_s = bc_s + lc

        bc_n = pi_n + t * math.cos(reverse_azimuth * (math.pi / 180))
        bc_e = pi_e + t * math.sin(reverse_azimuth * (math.pi / 180))

        points = []
        current_station = math.ceil(bc_s / offset_distance) * offset_distance
        while current_station <= ec_s:
            chainage = current_station - bc_s
            angle = (chainage / lc) * deflection_angle
            current_n = bc_n + chainage * math.cos((azimuth_to_pi + angle) * (math.pi / 180))
            current_e = bc_e + chainage * math.sin((azimuth_to_pi + angle) * (math.pi / 180))
            points.append((current_station, current_n, current_e))
            current_station += offset_distance

        return {
            "bc_s": bc_s,
            "ec_s": ec_s,
            "lc": lc,
            "t": t,
            "bc_n": bc_n,
            "bc_e": bc_e,
            "points": points,
        }

    pi_s = st.number_input("Enter P.I. Sta.: ", min_value=0.0)
    pi_n = st.number_input("Enter North P.I.: ", min_value=0.0)
    pi_e = st.number_input("Enter East P.I.: ", min_value=0.0)
    def_angle = st.text_input("Enter Deflection Angle [xx-xx-xx]: ")
    curve = st.radio("Enter Direction Curve L or R", ("L", "R"))
    radius = st.number_input("Enter Radius: ", min_value=0.0)
    az_to_pi = st.text_input("Enter Azimuth Angle Pc to PI [xx-xx-xx]: ")
    offset_distance = st.number_input("Enter Distance Between Points (in meters): ", min_value=1)

    result = calculate_curve(pi_s, pi_n, pi_e, def_angle, curve, radius, az_to_pi, offset_distance)

    st.write(f"PC Sta.: {int(result['bc_s'] / 1000)}+{round((result['bc_s'] % 1000), 3)}")
    st.write(f"PT Sta.: {int(result['ec_s'] / 1000)}+{round((result['ec_s'] % 1000), 3)}")
    st.write(f"LC: {round(result['lc'], 3)}")
    st.write(f"T: {round(result['t'], 3)}")
    st.write("Coordinates from PC to PT:")
    for station, north, east in result['points']:
        st.write(f"Sta. {int(station / 1000)}+{round(station % 1000, 3)}: North = {north:.3f}, East = {east:.3f}")

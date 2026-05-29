import streamlit as st
import pandas as pd
import time
import numpy as np

st.set_page_config(page_title='Aviation Simulations')
st.header('Aviation Simulation Engine')

tab1, tab2 = st.tabs(["✈️ Electric Propulsion", "🔥 Turbojet Propulsion"])


with tab1:
    st.subheader("Instructions")
    st.markdown("Step 1: Fill out all Aircraft's Desired Parameters values")
    st.markdown("Step 2: Click 'Submit Parameters'")
    st.markdown("Step 3: Start manipulating 'Number of Motors' and 'Battery Parallel Multiple' until you reach a satisfactory Motor Power and Battery Capacity surplus/deficit")

    st.subheader("Aircraft's Desired Parameters")

    excel_file = 'aviation_data.xlsx'   # not used directly – kept for compatibility
    battery_file = 'batteries.csv'
    motors_file = 'motors.csv'
    sheet_list = ["motors", "batteries"]

    motors_df = pd.read_csv(motors_file)
    batteries_df = pd.read_csv(battery_file)

    propulsion_motor_choices = []
    battery_choices = []

    def obtain_row_count(dataframe):
        return dataframe.shape[0]

    row_count_motors = obtain_row_count(motors_df)
    for i in range(row_count_motors):
        propulsion_motor_choices.append(motors_df.iloc[i][0])

    row_count_batteries = obtain_row_count(batteries_df)
    for i in range(row_count_batteries):
        battery_choices.append(batteries_df.iloc[i][0])

    st.write("Submit form containing all required values")
    performance_form = st.form("Performance Characteristics")
    propulsion_motor_choice = performance_form.selectbox(
        "Select propulsion motor:",
        propulsion_motor_choices
    )
    battery_choice = performance_form.selectbox(
        "Select battery cell:",
        battery_choices
    )
    airframe_mass_choice = performance_form.number_input("Airframe Mass in kg: ", min_value=1)
    payload_choice = performance_form.number_input("Payload in kg: ", step=10, min_value=10)
    range_choice = performance_form.number_input("Range in km: ", step=10, min_value=10)
    speed_choice = performance_form.number_input("Speed in km/h: ", step=5, min_value=5)
    submitted_or_not = performance_form.form_submit_button(label="Submit Parameters")

    st.subheader('Performance Assumptions')
    rule_of_thumb = 100
    ld_ratio = 15
    motor_power_efficiency = 0.9
    propulsive_efficiency = 0.75
    takeoff_time = 0.1

    st.write(f"Powering Rule of Thumb: {rule_of_thumb} W/kg")
    st.write(f"Lift-to-Drag Ratio (cruising): {ld_ratio}")
    st.write(f"Motor Efficiency: {motor_power_efficiency*100}%")
    st.write(f"Propulsive Efficiency: {propulsive_efficiency*100}%")
    st.write(f"Taxi & Takeoff Time: {takeoff_time*60} min")

    st.subheader("Performance Estimation")

    num_motors = st.slider(label="Number of Motors", min_value=1, step=1, max_value=6, key="elec_motors")
    parallel_multiple = st.number_input(label="Battery Parallel Multiple", min_value=1, step=1, key="elec_parallel")

    # Extract motor data
    motor_row = motors_df[motors_df.iloc[:,0] == propulsion_motor_choice].iloc[0]
    all_motor_mass = motor_row["Mass (kg)"] * num_motors
    motor_voltage = motor_row["Voltage (V)"]
    all_motor_eff_power = motor_row["Efficient Power (W)"] * num_motors
    all_motor_eff_thrust = motor_row["Efficient Power Thrust (kg)"] * num_motors
    all_motor_max_power = motor_row["Max Power (W)"] * num_motors
    all_motor_max_thrust = motor_row["Max Power Thrust (kg)"] * num_motors

    # Battery data
    battery_row = batteries_df[batteries_df.iloc[:,0] == battery_choice].iloc[0]
    battery_cell_mass = battery_row["Mass (kg)"]
    battery_cell_voltage = battery_row["Voltage (V)"]
    battery_cell_current = battery_row["Current (Ah)"]

    required_cells_series = round(motor_voltage / battery_cell_voltage, 0)
    battery_cell_quantity = required_cells_series * parallel_multiple
    battery_pack_capacity = battery_cell_quantity * battery_cell_current * battery_cell_voltage
    battery_pack_mass = battery_cell_mass * battery_cell_quantity

    total_mass = airframe_mass_choice + all_motor_mass + payload_choice + battery_pack_mass

    # Method 1: L/D based
    lift_required = 9.8 * total_mass
    drag = lift_required / ld_ratio
    power_required = drag * speed_choice / 3.6
    power_required = power_required / motor_power_efficiency / propulsive_efficiency
    power_deficit_per_ld_ratio = all_motor_eff_power - power_required

    cruising_time = range_choice / speed_choice
    cruising_work_required = power_required * cruising_time
    takeoff_work_required = all_motor_max_power * takeoff_time
    total_work_required = takeoff_work_required + cruising_work_required
    battery_capacity_deficit = battery_pack_capacity - total_work_required

    # Method 2: rule of thumb
    ideal_power_per_rule_of_thumb = total_mass * rule_of_thumb
    power_deficit_per_rule_of_thumb = all_motor_max_power - ideal_power_per_rule_of_thumb

    st.success(f"Motor Power Surplus/Deficit per L/D ratio: {str(round(power_deficit_per_ld_ratio))} Watts")
    st.success(f"Battery Capacity Surplus/Deficit per L/D ratio {str(round(battery_capacity_deficit))} Watt-hours")
    st.success(f"Motor Power Surplus/Deficit per rule of thumb: {str(round(power_deficit_per_rule_of_thumb))} Watts")

    st.success(f"Simulated Battery Configuration: {round(required_cells_series)}s{parallel_multiple}p")
    st.success(f"Simulated Battery Mass: {round(battery_pack_mass, 2)} kg")
    st.success(f"Simulated Total Aircraft Mass: {round(total_mass, 2)} kg")

    if submitted_or_not:
        st.write("Submitted form. This message will disappear when you start estimating Performance.")
    st.write(f"Time of latest performance estimate: {time.strftime('%H:%M:%S')}")


with tab2:
    st.subheader("Instructions")
    st.markdown("""
    Breguet Range Equation:
    \( R = \frac{V}{c} \cdot \frac{L}{D} \cdot \ln\left(\frac{W_i}{W_f}\right) \)
    """)
    st.caption("Breguet equation assumes steady cruise, no reserves. Fuel fraction = fuel mass / initial total mass.")
    st.markdown("Step 1: Fill out all Aircraft's Desired Parameters values")
    st.markdown("Step 2: Start manipulating the fields until you reach a satisfactory Performance Estimation")

    engines_df = pd.read_csv("engines.csv")
    engine_names = engines_df.iloc[:, 0].tolist()
    
    st.subheader("Aircraft's Desired Parameters")

    selected_engine = st.selectbox("Select jet engine", engine_names, key="jet_engine")
    engine_row = engines_df[engines_df.iloc[:,0] == selected_engine].iloc[0]
    thrust_per_engine_N = engine_row["Thrust_N"]
    sfc_kg_per_N_hr = engine_row.get("SFC_kg_per_N_hr", None)
    sfc_kg_per_kN_hr = engine_row.get("SFC_kg_per_kN_hr", None)
    g = 9.81

    if pd.notna(sfc_kg_per_N_hr):
        sfc_per_sec = sfc_kg_per_N_hr / 3600          # kg/N/s
        c = sfc_per_sec * g                            # 1/s (weight basis)
        sfc_display = f"{sfc_kg_per_N_hr} kg/N/hr"
    elif pd.notna(sfc_kg_per_kN_hr):
        sfc_kg_per_N_hr = sfc_kg_per_kN_hr / 1000
        sfc_per_sec = sfc_kg_per_N_hr / 3600
        c = sfc_per_sec * g
        sfc_display = f"{sfc_kg_per_kN_hr} kg/kN/hr"
    else:
        st.error("SFC column not recognised. Please use 'SFC_kg_per_N_hr' or 'SFC_kg_per_kN_hr'.")

    num_engines = st.slider("Number of engines", 1, 8, 2, key="jet_num_eng")
    total_thrust_N = thrust_per_engine_N * num_engines

    # Aircraft mass components
    frame_mass_kg = st.number_input("Airframe mass (kg)", min_value=100, value=500, step=50, key="frame_mass")
    payload_mass_kg = st.number_input("Payload mass (kg)", min_value=0, value=200, step=50, key="payload")
    # Fuel mass will be derived from fuel fraction or range – but we can also let user set fuel fraction directly
    fuel_fraction = st.slider("Fuel fraction (W_fuel / W_i)", 0.0, 0.6, 0.3, step=0.01, key="fuel_frac")

    # Total initial mass = frame + payload + fuel
    # W_fuel = fuel_fraction * W_i, so W_i = (frame+payload) / (1 - fuel_fraction)
    if fuel_fraction >= 1.0:
        st.error("Fuel fraction must be < 1")
        initial_mass_kg = frame_mass_kg + payload_mass_kg
    else:
        initial_mass_kg = (frame_mass_kg + payload_mass_kg) / (1 - fuel_fraction)
    fuel_mass_kg = initial_mass_kg - (frame_mass_kg + payload_mass_kg)

    #with col2:
    L_D = st.slider("Lift/Drag ratio (L/D)", 1.0, 20.0, 3.0, step=0.5, key="LD")
    speed_ms = st.number_input("Cruise speed (m/s)", min_value=50, value=190, step=10, key="speed_ms")
    st.caption(f"= {speed_ms * 3.6:.1f} km/h")

    st.subheader("Performance Estimation")
    st.success(f"Total mass: {initial_mass_kg:.1f} kg")
    st.success(f"Fuel mass: {fuel_mass_kg:.1f} kg")
    Wi_N = initial_mass_kg * g
    thrust_required_N = Wi_N / L_D
    st.success(f"Thrust surplus/defecit per L/D: {thrust_required_N:.0f} N ≤ available {total_thrust_N:.0f} N")

    Wf_N = (frame_mass_kg + payload_mass_kg) * g   # final weight after burning all fuel

    if fuel_fraction > 0:
        Wi_Wf = 1 / (1 - fuel_fraction)
        ln_ratio = np.log(Wi_Wf)
        range_m = (speed_ms / c) * L_D * ln_ratio
        range_km = range_m / 1000
        st.success(f"Range: {range_km:.1f} km")
    else:
        st.warning("Fuel fraction must be > 0 to compute range.")

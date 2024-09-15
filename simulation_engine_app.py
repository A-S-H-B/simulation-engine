import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title='Aviation Simulations')
st.header('Aviation Simulation Engine')

st.subheader("Instructions")
st.markdown("Step 1: Fill out all Aircraft's Desired Parameters values", )
st.markdown("Step 2: Click 'Submit Parameters'")
st.markdown("Step 3: Start manipulating 'Number of Motors' and 'Battery Parallel Multiple' until you reach a satisfactory Motor Power and Battery Capacity surplus/defecit")

st.subheader('''Aircraft's Desired Parameters''')

excel_file = 'aviation_data.xlsx'
sheet_list = ["motors", "batteries"]

dataframes = {}
for sheet in sheet_list:
    dataframes[sheet] = pd.read_excel(excel_file, sheet_name=sheet)

motors_df = dataframes["motors"]
batteries_df = dataframes["batteries"]
dataframes_list = [motors_df, batteries_df]

propulsion_motor_choices = []
battery_choices = []

def obtain_row_count(dataframe):
    count, _ = dataframe.shape
    count = count-1
    return count

row_count_motors = obtain_row_count(motors_df)
for i in range(row_count_motors):
    propulsion_motor_choices.append(motors_df.iloc[i][0])

row_count_batteries = obtain_row_count(batteries_df)
for i in range(row_count_batteries):
    battery_choices.append(batteries_df.iloc[i][0])

#st.write(f'''The dataframe now is {df.iloc[1][0]}''')
st.write("Submit form containing all required values")

performance_form = st.form("Performance Characteristics")
#performance_form.slider()
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
takeoff_time = 0.1 # Assuming 6 minutes

st.write(f"Powering Rule of Thumb: {rule_of_thumb} W/kg")
st.write(f"Lift-to-Drag Ratio (cruising): {ld_ratio}")
st.write(f"Motor Efficiency: {motor_power_efficiency*100}%")
st.write(f"Propulsive Efficiency: {propulsive_efficiency*100}%")
st.write(f"Taxi & Takeoff Time: {takeoff_time*60} min")

st.subheader("Performance Estimation")

num_motors = 1
parallel_multiple = 2

num_motors = st.slider(label="Number of Motors", min_value=1, step=1, max_value=6)
parallel_multiple = st.number_input(label="Battery Parallel Multiple", min_value=1, step=1)

for i in range(row_count_motors):
    if motors_df.loc[i][0] == propulsion_motor_choice:
        all_motor_mass = motors_df.loc[i]["Mass (kg)"]*num_motors
        motor_voltage = motors_df.loc[i]["Voltage (V)"]
        all_motor_eff_power = motors_df.loc[i]["Efficient Power (W)"]*num_motors
        all_motor_eff_thrust = motors_df.loc[i]["Efficient Power Thrust (kg)"]*num_motors
        all_motor_max_power = motors_df.loc[i]["Max Power (W)"]*num_motors
        all_motor_max_thrust = motors_df.loc[i]["Max Power Thrust (kg)"]*num_motors

for i in range(row_count_batteries):
    if batteries_df.loc[i][0] == battery_choice:
        battery_cell_mass = batteries_df.loc[i]["Mass (kg)"]
        battery_cell_voltage = batteries_df.loc[i]["Voltage (V)"]
        battery_cell_current = batteries_df.loc[i]["Current (Ah)"]

required_cells_series = round(motor_voltage/battery_cell_voltage, 0)
battery_cell_quantity = required_cells_series*parallel_multiple
battery_pack_capacity = battery_cell_quantity*battery_cell_current*battery_cell_voltage
battery_pack_mass = battery_cell_mass*battery_cell_quantity

total_mass = airframe_mass_choice+all_motor_mass+payload_choice+battery_pack_mass

#Method 1
lift_required = 9.8*total_mass
drag = lift_required/ld_ratio
power_required = drag*speed_choice/3.6
power_required = power_required/motor_power_efficiency/propulsive_efficiency
power_deficit_per_ld_ratio = all_motor_eff_power-power_required

cruising_time = range_choice/speed_choice
cruising_work_required = power_required*cruising_time
takeoff_work_required = all_motor_max_power*takeoff_time
total_work_required = takeoff_work_required+cruising_work_required

battery_capacity_deficit = battery_pack_capacity-total_work_required

#Method 2: rule of thumb
ideal_power_per_rule_of_thumb = total_mass*rule_of_thumb
power_deficit_per_rule_of_thumb = all_motor_max_power-ideal_power_per_rule_of_thumb

st.write(f"Motor Power Surplus/Deficit per L/D ratio: {str(round(power_deficit_per_ld_ratio))} Watts")
st.write(f"Battery Capacity Surplus/Deficit per L/D ratio {str(round(battery_capacity_deficit))} Watt-hours")
st.write(f"Motor Power Surplus/Deficit per rule of thumb: {str(round(power_deficit_per_rule_of_thumb))} Watts")

if submitted_or_not:
    st.write("Submitted form. ")
    st.write("This message will disappear when you start estimating Performance.")
st.write(f"Time of latest Performance Estimate: {time.strftime("%H:%M:%S")}")

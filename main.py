import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Title
st.title("Weight Goal Calorie Analyzer")

# User Setup
st.header("Your Profile")
goal = st.selectbox("Goal", ["Weight Loss", "Weight Gain"])
weight = st.number_input("Current Weight (kg)", min_value=30.0, step=0.1)
height = st.number_input("Height (cm)", min_value=100.0, step=1.0)
age = st.number_input("Age", min_value=10, step=1)
gender = st.selectbox("Gender", ["Male", "Female"])
activity = st.selectbox("Activity Level", ["Sedentary (1.2)", "Moderate (1.5)", "Active (1.725)"])
activity_factor = float(activity.split("(")[1].replace(")", ""))
target_weight = st.number_input(f"Target Weight (kg) for {goal}", min_value=30.0, step=0.1)

# Calculate BMR and Maintenance
bmr = (10 * weight + 6.25 * height - 5 * age + 5) if gender == "Male" else (10 * weight + 6.25 * height - 5 * age - 161)
maintenance = bmr * activity_factor
target_calories = maintenance - 500 if goal == "Weight Loss" else maintenance + 500
st.write(f"Maintenance Calories: {maintenance:.0f} | Target Calories: {target_calories:.0f}")

# Data Input
st.header("Log Your Day")
date = st.date_input("Date", value=pd.Timestamp.today())
calories = st.number_input("Total Daily Calories", min_value=0, step=10)
protein = st.number_input("Protein (g)", min_value=0, step=1)
fat = st.number_input("Fat (g)", min_value=0, step=1)
carbs = st.number_input("Carbs (g)", min_value=0, step=1)
exercise_mins = st.number_input("Exercise Minutes", min_value=0, step=5)
exercise_intensity = st.selectbox("Exercise Intensity", ["Light (4)", "Moderate (6)", "High (8)"])
calories_burned = exercise_mins * float(exercise_intensity.split("(")[1].replace(")", ""))
current_weight = st.number_input("Weight Today (kg, optional)", min_value=0.0, step=0.1, value=0.0)

# Store Data
if "weight_data" not in st.session_state:
    st.session_state.weight_data = pd.DataFrame(columns=["Date", "Calories", "Protein", "Fat", "Carbs", "Exercise_Burn", "Weight"])

if st.button("Add Entry"):
    new_entry = pd.DataFrame({
        "Date": [date], "Calories": [calories], "Protein": [protein], "Fat": [fat], "Carbs": [carbs],
        "Exercise_Burn": [calories_burned], "Weight": [current_weight if current_weight > 0 else np.nan]
    })
    st.session_state.weight_data = pd.concat([st.session_state.weight_data, new_entry], ignore_index=True)
    st.success("Entry added!")

# Display Data
st.header("Your Progress")
st.write(st.session_state.weight_data)

# Analysis
if not st.session_state.weight_data.empty:
    st.header("Insights")
    data = st.session_state.weight_data
    data["Net_Calories"] = data["Calories"] - data["Exercise_Burn"]
    data["Balance"] = data["Net_Calories"] - maintenance
    balance_label = "Deficit" if goal == "Weight Loss" else "Surplus"
    
    # Stats
    mean_balance = data["Balance"].mean()
    total_balance = data["Balance"].sum()
    est_weight_change = total_balance / 3500
    weight_goal = weight - target_weight if goal == "Weight Loss" else target_weight - weight
    progress = min(abs(est_weight_change / weight_goal), 1.0) if weight_goal != 0 else 0
    
    st.write(f"Average Daily {balance_label}: {mean_balance:.0f} calories")
    st.write(f"Estimated Weight Change: {est_weight_change:.2f} lbs")
    st.progress(progress)
    st.write(f"Progress to {weight_goal:.1f} kg Goal: {progress*100:.1f}%")

    # Macro Analysis
    st.subheader("Macronutrient Breakdown (Latest Day)")
    latest = data.iloc[-1]
    macro_calories = {"Protein": latest["Protein"]*4, "Fat": latest["Fat"]*9, "Carbs": latest["Carbs"]*4}
    fig, ax = plt.subplots()
    ax.pie(macro_calories.values(), labels=macro_calories.keys(), autopct="%1.1f%%")
    st.pyplot(fig)

    # Visualization
    st.subheader(f"{balance_label} Trend")
    fig2, ax2 = plt.subplots()
    data.groupby("Date")["Balance"].sum().plot(ax=ax2)
    ax2.axhline(0, color="gray", linestyle="--")
    ax2.set_ylabel(f"Calories ({balance_label})")
    st.pyplot(fig2)

    if not data["Weight"].isna().all():
        st.subheader("Weight Trend")
        fig3, ax3 = plt.subplots()
        data.plot(x="Date", y="Weight", ax=ax3)
        ax3.set_ylabel("Weight (kg)")
        st.pyplot(fig3)

# Tips
st.header("Tips")
tips = {
    "Weight Loss": ["Eat more fiber to stay full", "Drink water before meals", "Prioritize protein"],
    "Weight Gain": ["Add calorie-dense foods like nuts", "Lift weights to build muscle", "Eat every 3 hours"]
}
st.write(np.random.choice(tips[goal]))

# Export Data
st.header("Export Your Data")
if st.button("Download CSV"):
    csv = st.session_state.weight_data.to_csv(index=False)
    st.download_button("Download", csv, "weight_data.csv", "text/csv")

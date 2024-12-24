import streamlit as st
import random
import pandas as pd

def main():
    st.title("Card Guessing Game")

    # Initialize session state variables on first run
    if "results" not in st.session_state:
        st.session_state["results"] = []
    if "net_score" not in st.session_state:
        st.session_state["net_score"] = 0
    if "net_score_history" not in st.session_state:
        st.session_state["net_score_history"] = []

    # --- Sidebar settings ---
    st.sidebar.title("Settings")
    
    # 1) Probability of Red
    prob_red = st.sidebar.slider(
        "Probability of Red",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.01
    )
    
    # 2) Show/hide line graph
    show_graph = st.sidebar.checkbox("Show line graph", value=False)

    # 3) Smooth the line graph
    smooth_graph = st.sidebar.checkbox("Smooth line graph", value=False)
    smoothing_window = 1
    if smooth_graph:
        smoothing_window = st.sidebar.slider(
            "Smoothing window size",
            min_value=1,
            max_value=10,
            value=3,
            step=1
        )

    # --- Main page layout ---
    col1, col2, _ = st.columns([1, 1, 1])
    guess = None
    with col1:
        if st.button("Guess Red"):
            guess = "Red"
    with col2:
        if st.button("Guess Blue"):
            guess = "Blue"

    # If user made a guess
    if guess is not None:
        draw = "Red" if random.random() < prob_red else "Blue"
        outcome = "Correct" if guess == draw else "Wrong"

        if outcome == "Correct":
            st.balloons()
            st.write("You're correct!")
            st.session_state["net_score"] += 1
        else:
            st.snow()
            st.write("Wrong!")
            st.session_state["net_score"] -= 1

        # Record result
        st.session_state["results"].append({
            "Your Guess": guess,
            "Actual Card": draw,
            "Right or Wrong": outcome
        })
        st.session_state["net_score_history"].append(st.session_state["net_score"])

    # Conditionally display line chart of net score over time
    if show_graph and st.session_state["net_score_history"]:
        # If smoothing is enabled, calculate rolling average
        net_scores_series = pd.Series(st.session_state["net_score_history"])
        if smooth_graph and smoothing_window > 1:
            net_scores_smoothed = net_scores_series.rolling(window=smoothing_window, min_periods=1).mean()
            st.line_chart(net_scores_smoothed)
        else:
            # No smoothing
            st.line_chart(net_scores_series)

    # Display table of all guesses
    results_df = pd.DataFrame(st.session_state["results"])
    st.dataframe(results_df)

    # Download button for CSV export
    if not results_df.empty:
        csv_data = results_df.to_csv(index=False)
        st.download_button(
            label="Download results as CSV",
            data=csv_data,
            file_name="results.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()

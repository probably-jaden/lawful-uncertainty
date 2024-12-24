import streamlit as st
import random
import pandas as pd
import altair as alt

def main():
    st.title("Card Guessing Game")

    # --- Initialize session state on first run ---
    if "results" not in st.session_state:
        st.session_state["results"] = []
    if "net_score" not in st.session_state:
        st.session_state["net_score"] = 0
    if "net_score_history" not in st.session_state:
        st.session_state["net_score_history"] = []

    # Bayesian bot state
    if "bayes_net_score" not in st.session_state:
        st.session_state["bayes_net_score"] = 0
    if "bayes_score_history" not in st.session_state:
        st.session_state["bayes_score_history"] = []
    if "bayes_alpha" not in st.session_state:
        st.session_state["bayes_alpha"] = 0.5
    if "bayes_beta" not in st.session_state:
        st.session_state["bayes_beta"] = 0.5

    # --- Sidebar settings ---
    st.sidebar.title("Settings")

    # 1) Probability of Red
    prob_red = st.sidebar.slider(
        "Probability of Red",
        min_value=0.0,
        max_value=1.0,
        value=0.6,
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

    # --- Layout for guess buttons ---
    col1, col2, _ = st.columns([1, 1, 1])
    guess = None
    with col1:
        if st.button("Guess Red"):
            guess = "Red"
    with col2:
        if st.button("Guess Blue"):
            guess = "Blue"

    # --- If user made a guess, draw a card and evaluate ---
    if guess is not None:
        # Actual card
        draw = "Red" if random.random() < prob_red else "Blue"
        # User outcome
        outcome_user = "Correct" if guess == draw else "Wrong"

        # Update user net score
        if outcome_user == "Correct":
            # Only show balloons if show_graph is False
            if not show_graph:
                st.balloons()
            st.write("You're correct!")
            st.session_state["net_score"] += 1
        else:
            # Only show snow if show_graph is False
            if not show_graph:
                st.snow()
            st.write("Wrong!")
            st.session_state["net_score"] -= 1

        # --- Bayesian Bot Guess and Update ---
        p_red_bayes = st.session_state["bayes_alpha"] / (
            st.session_state["bayes_alpha"] + st.session_state["bayes_beta"]
        )
        bayes_guess = "Red" if p_red_bayes > 0.5 else "Blue"

        # Check bot correctness
        outcome_bayes = "Correct" if bayes_guess == draw else "Wrong"
        if outcome_bayes == "Correct":
            st.session_state["bayes_net_score"] += 1
        else:
            st.session_state["bayes_net_score"] -= 1

        # Update the Bayesian prior
        if draw == "Red":
            st.session_state["bayes_alpha"] += 1
        else:
            st.session_state["bayes_beta"] += 1

        # Record results
        st.session_state["results"].append({
            "Your Guess": guess,
            "Actual Card": draw,
            "Right or Wrong (You)": outcome_user,
            "Bot Guess": bayes_guess,
            "Right or Wrong (Bot)": outcome_bayes
        })

        # Append net scores to histories
        st.session_state["net_score_history"].append(st.session_state["net_score"])
        st.session_state["bayes_score_history"].append(st.session_state["bayes_net_score"])

    # --- Conditionally display line chart with both scores ---
    if show_graph and st.session_state["net_score_history"]:
        # Build a DataFrame with step, user_score, bayes_score
        score_data = pd.DataFrame({
            "step": range(len(st.session_state["net_score_history"])),
            "User": st.session_state["net_score_history"],
            "Bayes": st.session_state["bayes_score_history"]
        })

        # If smoothing is enabled, compute rolling averages
        if smooth_graph and smoothing_window > 1:
            score_data["User"] = (
                score_data["User"].rolling(window=smoothing_window, min_periods=1).mean()
            )
            score_data["Bayes"] = (
                score_data["Bayes"].rolling(window=smoothing_window, min_periods=1).mean()
            )

        # Melt to "long" form for easy Altair plotting
        score_melted = score_data.melt("step", var_name="Entity", value_name="Score")

        # We'll define custom stroke dashes: solid for user, dashed for Bayes
        dash_scale = alt.Scale(
            domain=["User", "Bayes"],
            range=[[1, 0], [5, 5]]  # 'User' is solid, 'Bayes' is dashed
        )

        chart = (
            alt.Chart(score_melted)
            .mark_line()
            .encode(
                x=alt.X("step:Q", title="Guess #"),
                y=alt.Y("Score:Q", title="Net Score"),
                color=alt.Color("Entity:N"),
                strokeDash=alt.StrokeDash("Entity:N", scale=dash_scale),
            )
            .properties(width=600, height=400)
        )
        st.altair_chart(chart, use_container_width=True)

    # --- Show results table ---
    results_df = pd.DataFrame(st.session_state["results"])
    st.dataframe(results_df)

    # --- Download results as CSV ---
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

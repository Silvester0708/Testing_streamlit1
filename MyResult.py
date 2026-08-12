import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def load_results(filepath):
    results = []
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        st.error(f"Error: Could not find the file '{filepath}'.")
        return results
    except IOError as e:
        st.error(f"Error reading file '{filepath}': {e}")
        return results

    for line in lines:
        line = line.strip()
        if line == "":
            continue

        parts = line.split(":")
        name = parts[0]
        answers = parts[1].split(",")
        score = int(parts[2]) # change to integer, default is string

        results.append({"name": name, "answers": answers, "score": score})

    return results

st.title("Quiz Results")

results = load_results("Answers.txt")

# score matrix
st.write(f"Loaded {len(results)} participant(s)")
st.dataframe(results)

# loop to store scores then find min max in the list
scores = []
for r in results:
    scores.append(r["score"])

highest_score = max(scores)
lowest_score = min(scores)

# print highest and lowest
st.write(f"Highest score: {highest_score}")
st.write(f"Lowest score: {lowest_score}")

# loop to append name and score of highest score participants
highest_participants = []
for r in results:
    if r["score"] == highest_score:
        highest_participants.append({"name": r["name"], "score": r["score"]})

# loop to append name and score of lowest score participants
lowest_participants = []
for r in results:
    if r["score"] == lowest_score:
        lowest_participants.append({"name": r["name"], "score": r["score"]})

st.write("Highest score:")
st.dataframe(highest_participants)

st.write("Lowest score:")
st.dataframe(lowest_participants)

# task 2.4
mean = np.mean(scores)
median = np.median(scores)

scores_pd = pd.Series(scores)
mode = scores_pd.mode()

st.write(f"Mean score: {mean}")
st.write(f"Median score: {median}")
st.write("Mode score(s):")
st.write(mode)

# ========== Chart 1: bar chart ==========
# get names
names = []
for r in results:
    names.append(r["name"])

fig, ax = plt.subplots()
ax.bar(names, scores)
ax.set_xlabel("Participant")
ax.set_ylabel("Score")
ax.set_title("Total Marks per Participant")

st.pyplot(fig)

# ========== Chart 2: mean =============
fig2, ax2 = plt.subplots()
ax2.bar(["Mean"], [mean], color="red", width=0.1)
ax2.set_xlabel("Statistic")
ax2.set_ylabel("Score")
ax2.set_title("Mean Score")
st.pyplot(fig2)

# ========== Chart 3: median =============
fig3, ax3 = plt.subplots()
ax3.bar(["Median"], [median], color="green")
ax3.set_xlabel("Statistic")
ax3.set_ylabel("Score")
ax3.set_title("Median Score")
st.pyplot(fig3)

# ========== Chart 4: mode =============
# count how many times each unique score appears
score_counts = {}
for s in scores:
    if s in score_counts:
        score_counts[s] += 1
    else:
        score_counts[s] = 1
        
# only keep the scores that are actually modes
mode_counts = {}
for m in mode:
    mode_counts[m] = score_counts[m]

score_labels = [str(v) for v in mode_counts.keys()]
frequencies = list(mode_counts.values())

fig4, ax4 = plt.subplots()
ax4.bar(score_labels, frequencies, color="orange")
ax4.set_xlabel("Score")
ax4.set_ylabel("Frequency (number of participants)")
ax4.set_title("Mode Score(s) and Frequency")
st.pyplot(fig4)
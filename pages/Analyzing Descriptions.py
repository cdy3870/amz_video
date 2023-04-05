import streamlit as st
import time
import numpy as np
import pandas as pd
from keybert import KeyBERT
import plotly.express as px
import seaborn as sns

st.set_page_config(page_title="Analyzing TV Show/Movie Description")

st.markdown("# Analyzing TV Show/Movie Description")
# st.write(
#     """This demo illustrates a combination of plotting and animation with
# Streamlit. We're generating a bunch of random numbers in a loop for around
# 5 seconds. Enjoy!"""
# )

# progress_bar = st.sidebar.progress(0)
# status_text = st.sidebar.empty()
# last_rows = np.random.randn(1, 1)
# chart = st.line_chart(last_rows)

# for i in range(1, 101):
#     new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
#     status_text.text("%i%% Complete" % i)
#     chart.add_rows(new_rows)
#     progress_bar.progress(i)
#     last_rows = new_rows
#     time.sleep(0.05)

# progress_bar.empty()

# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
# st.button("Re-run")

@st.cache_data
def cache_kw_model():
	kw_model = KeyBERT()
	return kw_model

@st.cache_data
def cache_data():
	data = pd.read_csv("amazon_prime_titles.csv")
	return data

def keyword_display(data, kw_model):
	title = st.selectbox("Select title to show keywords (not all shown)", list(data["title"])[:50])
	desc = data[data["title"] == title]["description"]
	st.write(desc)

	words, percents = zip(*dict(kw_model.extract_keywords(list(desc)[0], top_n=5)).items())
	print(words)
	print(percents)

	df = (
	pd.DataFrame(kw_model.extract_keywords(list(desc)[0], top_n=5), columns=["Keyword/Keyphrase", "Relevancy"])
	.sort_values(by="Relevancy", ascending=False)
	.reset_index(drop=True)
	)

	df.index += 1

	# Add styling
	cmGreen = sns.light_palette("green", as_cmap=True)
	cmRed = sns.light_palette("red", as_cmap=True)
	df = df.style.background_gradient(
		cmap=cmGreen,
		subset=[
			"Relevancy",
		],
	)


	format_dictionary = {
	    "Relevancy": "{:.1%}",
	}

	df = df.format(format_dictionary)

	return df

def main():
	data = cache_data()
	kw_model = cache_kw_model()
	# st.write("Example descriptions")
	# temp = data[["title", "description"]][:10]
	# temp

	rel_df = keyword_display(data, kw_model)
	st.table(rel_df)

if __name__ == "__main__":
	main()


import streamlit as st
import plotly.express as px
import os
from urllib.request import urlopen
import json
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.set_page_config(
    page_title="Graphs",
    layout="wide",
    page_icon="📈"
)

st.title("Experimenting with Amazon Video Data")
# st.runtime.legacy_caching.clear_cache()

prof_countries = ["India", "United States", "United Kingdom"]

def get_data():
	data = pd.read_csv("amazon_prime_titles.csv")
	data.fillna("Unknown", inplace=True)
	data["country"] =data["country"].apply(lambda x: x.split(","))
	data["single_country"] = data["country"].apply(lambda x: x[0])
	data["listed_in"] = data["listed_in"].apply(lambda x : x.replace(" ", "")
                                                        .replace("andCulture", "Culture")
                                                        .split(","))
	data["genre"] = data["listed_in"].apply(lambda x: x[0])
	return data


def get_geoplot_fig(data, type="High"):
	with urlopen("https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson") as response:
	    countries = json.load(response)
	movies_per_coun = data["single_country"].value_counts()
	df = pd.DataFrame({"country":movies_per_coun.index, "counts":movies_per_coun.values})
	if type == "High":
		df = df[df["country"].isin(prof_countries)]
		df["country"] = df["country"].apply(lambda x : x.replace("United States", "United States of America"))
		max_range = 300
	else:
		df = df[~df["country"].isin(prof_countries)]
		max_range= 50




	fig = px.choropleth_mapbox(df, geojson=countries, locations="country", color='counts',
	                           featureidkey="properties.ADMIN",
	                           color_continuous_scale="Viridis",
	                           range_color=(0, max_range),
	                           mapbox_style="carto-positron",
	                           zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
	                           opacity=0.5,
	                           labels={'counts':'TV Shows/Movies'}
	                          )
	fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

	return fig

def get_heatmap_fig(data, type="High"):


	mlb = MultiLabelBinarizer()
	mlb.fit(data["listed_in"])
	new_col_names = ["%s" % c for c in mlb.classes_]
	genres = pd.DataFrame(mlb.fit_transform(data["listed_in"]), columns=new_col_names,index=data["listed_in"].index)
	data = pd.concat([data, genres], axis=1)
	temp = data.groupby(["single_country"])["Action"].sum().reset_index(name="Action count")

	for genre in new_col_names[1:]:
	    genre_counts_df = pd.concat([temp, data.groupby(["single_country"])[genre].sum().reset_index(name=genre + " count")[genre + " count"]], axis=1)
	    temp = genre_counts_df

	countries = genre_counts_df["single_country"]
	# genre_counts_df[genre_counts_df["single_country"].isin(prof_countries)]

	fig = plt.figure(figsize=(10,5))

	if type == "High":
		plt.xticks(rotation=90)
		sns.heatmap(genre_counts_df[genre_counts_df["single_country"].isin(prof_countries)]
		                            .iloc[:, 1:].to_numpy(), vmin = 0, vmax = 200, cmap="Greens", yticklabels=prof_countries, xticklabels=new_col_names)

	else:
		plt.xticks(rotation=90)
		temp_countries = prof_countries + ["Unknown"]
		other_countries = [c for c in countries if c not in temp_countries]
		sns.heatmap(genre_counts_df[~genre_counts_df["single_country"].isin(temp_countries)]
		                            .iloc[:, 1:].to_numpy(), vmin = 0, vmax = 15, cmap="Blues", yticklabels=other_countries, xticklabels=new_col_names)

	return fig

def get_dur_fig(data, country_type):
	data = data[data["type"] == "Movie"]
	data["average duration"] = data["duration"].apply(lambda x : int(x.split(" ")[0]))
	temp = data.groupby(["single_country"])["average duration"].mean().reset_index()
	if country_type == "Low":
		temp = temp[~temp["single_country"].isin(prof_countries + ["Unknown"])]
	else:
		temp = temp[temp["single_country"].isin(prof_countries)]
	fig = px.bar(temp, x="single_country", y="average duration", title="Average Movie Duration per Country")

	return fig

@st.cache_data
def cache_get_stacked_primary(data):
	temp = data.groupby(["single_country", "type"]).size().unstack(fill_value=0).reset_index()
	temp = temp[temp["single_country"].isin(prof_countries)]
	fig = px.bar(temp, x="single_country", y=["Movie", "TV Show"], title="TV/Movies per Country")
	
	return fig

@st.cache_data
def cache_get_stacked_secondary(data):
	temp = data.groupby(["single_country", "type"]).size().unstack(fill_value=0).reset_index()
	temp = temp[~temp["single_country"].isin(prof_countries + ["Unknown"])]
	fig = px.bar(temp, x="single_country", y=["Movie", "TV Show"], title="TV/Movies per Country")
	
	return fig


@st.cache_data
def cache_get_heatmap_fig_primary(data, country_type="High"):
	heatmap_fig = get_heatmap_fig(data, country_type)
	return heatmap_fig

@st.cache_data
def cache_get_heatmap_fig_secondary(data, country_type="Low"):
	heatmap_fig = get_heatmap_fig(data, country_type)
	return heatmap_fig


@st.cache_data
def cache_get_geoplot_fig(data, country_type):
	geo_fig = get_geoplot_fig(data, country_type)
	return geo_fig


@st.cache_data
def cache_get_genre_fig(data):

	temp = data.groupby(["release_year", "genre"]).size().unstack(fill_value=0).reset_index()

	print(temp)

	return temp

def main():
	data = get_data()
	

	metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
	metric_col1.markdown('##### Dataset: Amazon Prime Video\n')
	metric_col1.markdown('##### Author: Calvin Yu\n')

	show_df = st.checkbox("Show raw data")

	if show_df:
		st.dataframe(data.head())

	st.markdown("""---""")	
	st.markdown("#### Country Breakdown")
	
	with st.sidebar:
		country_type = st.radio("High or Low Production Countries", ("Low", "High"))
		min_counts = st.slider('Minimum totals', 0, 1000)

	if country_type == "High":
		heatmap_fig = cache_get_heatmap_fig_primary(data)
		stacked_fig = cache_get_stacked_primary(data)
	elif country_type == "Low":
		heatmap_fig = cache_get_heatmap_fig_secondary(data)
		stacked_fig = cache_get_stacked_secondary(data)


	geo_fig = cache_get_geoplot_fig(data, country_type)
	dur_fig = get_dur_fig(data, country_type)

	st.plotly_chart(geo_fig, use_container_width=True, theme="streamlit")
	chart1, chart2 = st.columns(2)
	chart1.plotly_chart(stacked_fig, use_container_width=True, theme="streamlit")
	chart2.plotly_chart(dur_fig, use_container_width=True, theme="streamlit")


	st.markdown("""---""")	
	st.markdown("#### Genre Breakdown")
	chart3, chart4 = st.columns([1, 3])
	chart3.write("Genre Counts Based on Country")
	chart3.pyplot(heatmap_fig)

	st_df = cache_get_genre_fig(data)
	genres = list(st_df.columns)[1:]
	chart4.write('Genre Counts Over Time')
	chart4.line_chart(st_df, x="release_year", y=genres)







if __name__ == "__main__":
	main()

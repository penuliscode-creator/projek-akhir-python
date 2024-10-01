import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import numpy as np
from babel.numbers import format_currency
sns.set(style='dark')

def create_daily_bike_rentals_df(df):
    daily_bike_rentals_df = df.groupby('dteday').agg({
        "cnt": "sum",    # Aggregate total rentals per day
    }).reset_index()
    daily_bike_rentals_df.rename(columns={
        "cnt": "daily_rentals"
    }, inplace=True)
    
    return daily_bike_rentals_df

def create_monthly_rentals(df):
    # Mengelompokkan data berdasarkan bulan dan tahun
    monthly_rentals = df.groupby(by=["mnth", "yr"]).agg({
    "cnt": "sum"
    }).reset_index()

    # Mengganti nilai bulan dengan nama bulan yang sesuai (Januari-Desember)
    monthly_rentals['mnth'] = monthly_rentals['mnth'].apply(lambda x:
    {1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'}.get(x, x))

    monthly_rentals['yr'] = monthly_rentals['yr'].apply(lambda x: 2011 if x == 0 else 2012)

    month_order = {'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12}
    # Menambahkan kolom urutan bulan
    monthly_rentals['mnth_order'] = monthly_rentals['mnth'].map(month_order)
    monthly_rentals = monthly_rentals.sort_values(by=['yr', 'mnth_order']).reset_index(drop=True)

    monthly_rentals = monthly_rentals.drop(columns=['mnth_order'])
    return monthly_rentals

def create_monthly_weather(df):
    weather_2012_df = df[df['yr'] == 1]

    monthly_weather = weather_2012_df.groupby(by="mnth").agg({
    "windspeed": "mean",
    "weathersit": lambda x: x.mode()[0]
    }).reset_index()

    # Mengganti nilai cuaca menjadi teks
    weather_mapping = {1: 'Clear', 2: 'Mist/Cloudy', 3: 'Light Snow/Rain', 4: 'Heavy Rain/Snow'}
    monthly_weather['weathersit'] = monthly_weather['weathersit'].map(weather_mapping)

    # Mengganti nilai bulan
    monthly_weather['mnth'] = monthly_weather['mnth'].apply(lambda x:
    {1: 'January', 2: 'February', 3: 'March', 4: 'April',
     5: 'May', 6: 'June', 7: 'July', 8: 'August',
     9: 'September', 10: 'October', 11: 'November', 12: 'December'}.get(x, x))

    return monthly_weather

def create_season_rentals(df):
    season_rentals = df.groupby(by=["season"]).agg({
    "cnt": "sum"
    }).reset_index()

    # Mengubah angka musim menjadi teks
    season_rentals['season'] = season_rentals['season'].apply(lambda x:
    {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}.get(x, x))
    return season_rentals

def create_result_sorted(df):
    def categorize_day(row):
        if row["holiday"] == 1:
            return "Holiday"
        elif row["workingday"] == 1:
            return "Working Day"
        elif row["weekday"] >= 5:
            return "Weekend"
        else:
            return "Weekday"

    df["day_type"] =df.apply(categorize_day, axis=1)

    # Menghitung jumlah persewaan berdasarkan kategori hari
    #result = hours_df.groupby(by="day_type")["cnt"].sum().reset_index()
    result = df.groupby(by="day_type")["cnt"].sum().reset_index()
    result_sorted = result.sort_values(by="cnt", ascending=False).reset_index(drop=True)
    return result_sorted

def create_hourly_rentals(df):
    hourly_rentals =df.groupby(by="hr").agg({
        "cnt": "mean"  # Rata-rata persewaan per jam
    }).reset_index()
    return hourly_rentals


def create_hourly_rentals_with_weather(df):
    hourly_rentals_with_weather = df.groupby(by=["hr", "weathersit"]).agg({
        "cnt": "mean",
        "temp": "mean",
        "hum": "mean",
        "windspeed": "mean"
    }).reset_index()

    # Mapping kondisi cuaca menjadi deskriptif
    weather_mapping = {1: 'Clear', 2: 'Mist/Cloudy', 3: 'Light Snow/Rain', 4: 'Heavy Rain/Snow'}
    hourly_rentals_with_weather['weathersit'] = hourly_rentals_with_weather['weathersit'].map(weather_mapping)

    return hourly_rentals_with_weather

def create_rfm_df(df):
    df['dteday'] = pd.to_datetime(df['dteday'])

    # Menghitung Recency
    # Menghitung tanggal terakhir penyewaan
    last_rental_date = df['dteday'].max()
    # Menghitung recency
    df['Recency'] = (last_rental_date - df['dteday']).dt.days

    # Menghitung Frequency
    # Menghitung jumlah penyewaan per hari
    frequency_df = df.groupby('dteday').agg({'cnt': 'sum'}).reset_index()
    frequency_df['Frequency'] = frequency_df['cnt']  # Set Frequency sama dengan jumlah penyewaan

    # Menghitung Monetary
    # Dianggap bahwa Monetary adalah jumlah total penyewaan
    monetary_df = df.groupby('dteday').agg({'cnt': 'sum'}).reset_index()
    monetary_df.rename(columns={'cnt': 'Monetary'}, inplace=True)

    # Menggabungkan semua metrik
    rfm_df = frequency_df[['dteday', 'Frequency']].merge(
        monetary_df[['dteday', 'Monetary']], on='dteday'
    ).merge(
        df[['dteday', 'Recency']], on='dteday', how='left'
    ).drop_duplicates()

    # Memeriksa hasil RFM
    return rfm_df


# Load cleaned data
all_df = pd.read_csv("dashboard/main.csv")

datetime_columns = ["dteday"]
all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

#filter data
min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://png.pngtree.com/png-clipart/20230807/original/pngtree-vector-illustration-of-a-bike-rental-logo-on-a-white-background-vector-picture-image_10130404.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["dteday"] >= str(start_date)) & 
                (all_df["dteday"] <= str(end_date))]

#st.dataframe(main_df)

## Menyiapkan berbagai dataframe
daily_bike_rentals_df = create_daily_bike_rentals_df(main_df)
monthly_rentals = create_monthly_rentals(main_df)
monthly_weather = create_monthly_weather(main_df)
season_rentals = create_season_rentals(main_df)
result_sorted = create_result_sorted(main_df)
hourly_rentals = create_hourly_rentals(main_df)
hourly_rentals_with_weather = create_hourly_rentals_with_weather(main_df)
rfm_df = create_rfm_df(main_df)


#plot number of Bike Share ( 2011-2012 )
st.header('Dicoding Collection Dashboard :sparkles:')
st.subheader('Daily Rentals')

col1, col2 = st.columns(2)

with col1:
    total_rentals = daily_bike_rentals_df.daily_rentals.sum()
    st.metric("Total Rentals", value=total_rentals)


with col2:
    total_rentals_formatted = format(total_rentals, ',')
    st.metric("Total Rentals", value=total_rentals_formatted)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_bike_rentals_df["dteday"],
    daily_bike_rentals_df["daily_rentals"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.set_xlabel('Date', fontsize=15)
ax.set_ylabel('Daily Rentals', fontsize=15)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

## Monhtly Rentals
st.subheader("Monhtly Rentals")

col1, col2 = st.columns(2)
with col1:
    total_rentals = monthly_rentals["cnt"].sum()
    st.metric("Total Rentals", value=total_rentals)

with col2:
    total_rentals_formatted = format(total_rentals, "")
    st.metric("Total Rentals", value=total_rentals_formatted)    

# Membuat plot dari penyewaan bulanan
fig, ax= plt.subplots(figsize=(16,8))
custom_palette = sns.color_palette(["#3DC2EC", "b"])
sns.lineplot(data=monthly_rentals, x='mnth', y='cnt', hue='yr',marker='o', palette=custom_palette )
plt.title('Monthly Bicycle Rental Trends (2011 vs 2012)')
plt.xlabel('Month')
plt.ylabel('Rental Quantity')
plt.xticks(rotation=45)
plt.grid()
plt.legend(title='Year')
st.pyplot(fig)

# Customer Demographics

st.subheader("Rental Behavior Patterns")

col1, col2 = st.columns(2)

with col1:
    fig, ax=plt.subplots(figsize=(20,10))

    colors = ["#D3D3D3", "#D3D3D3","#90CAF9", "#D3D3D3", "#D3D3D3"]
    sns.barplot(
        y="cnt",
        x ="season",
        data=season_rentals,
        palette=colors,
        ax=ax
    )
    ax.set_title("Bicycle Rentals by Season", loc="center", fontsize=30)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis="x", labelsize=35)
    ax.tick_params(axis="y", labelsize=30)
    st.pyplot(fig)

with col2:
    fig, ax=plt.subplots(figsize=(20,10))

    colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(
        y="cnt",
        x ="day_type",
        data=result_sorted,
        palette=colors,
        ax=ax
    )
    ax.set_title("Bicycle Rentals: Weekdays, Holidays, and Weekends", loc="center", fontsize=30)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis="x", labelsize=35)
    ax.tick_params(axis="y", labelsize=30)
    st.pyplot(fig)    


fig, ax=plt.subplots(figsize=(20,10))
colors = ["#D3D3D3", "#D3D3D3", "#D3D3D3","#90CAF9", "#D3D3D3"]
sns.barplot(
    y="cnt",
    x ="hr",
    data=hourly_rentals,
    palette=colors,
    ax=ax
)
ax.set_title("Bicycle Rentals by Hour", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis="x", labelsize=35)
ax.tick_params(axis="y", labelsize=30)
st.pyplot(fig)  

st.subheader("Best Bike Rentals on RFM Parameter")
col1, col2, col3 = st.columns(3)
with col1:
    avg_recency = round(rfm_df.Recency.mean(),1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
      avg_frequency = round(rfm_df.Frequency.mean(),2)
      st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_monetary = round(rfm_df.Monetary.mean(),3)
    st.metric("Average Monetary", value=avg_monetary)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(y="Recency", x="dteday", data=rfm_df.sort_values(by="Recency", ascending=True).head(5),hue="dteday", palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis ='x', labelsize=15)

sns.barplot(y="Frequency", x="dteday", data=rfm_df.sort_values(by="Frequency", ascending=False).head(5),hue="dteday", palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)

sns.barplot(y="Monetary", x="dteday", data=rfm_df.sort_values(by="Monetary", ascending=False).head(5),hue="dteday", palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.caption('Copyright (c) Dicoding 2023')


import pandas as pd
import matplotlib.pyplot as plt
import calendar
from matplotlib.backends.backend_pdf import PdfPages

# Read the data from the file
df = pd.read_csv('/var/www/html/bark.txt', delimiter='|', header=None, skipinitialspace=True,
                 names=['Camera', 'Event', 'Timestamp', 'Level', 'dB'])

# Strip spaces from the timestamp values
df['Timestamp'] = df['Timestamp'].str.strip()

# Extract the month from the Timestamp column
df['Month'] = pd.to_datetime(df['Timestamp'], format='%a %b %d %H:%M:%S %Y').dt.month_name()

# Sort the month order
month_order = list(calendar.month_name)[1:]  # Get the month names in order
df['Month'] = pd.Categorical(df['Month'], categories=month_order, ordered=True)

# Group the data by month
monthly_groups = df.groupby('Month')

# Create a PDF file to save the graphs
with PdfPages('/var/www/html/bark_graphs.pdf') as pdf:
    # Iterate over each month group
    for month, monthly_data in monthly_groups:
        # Filter the data for the current month
        monthly_data = monthly_data.copy()

        # Extract the day from the Timestamp column
        timestamps = monthly_data['Timestamp'].str.split().str[2]
        monthly_data.loc[:, 'Day'] = pd.to_numeric(timestamps)

        # Determine the number of days in the month
        days_in_month = calendar.monthrange(2023, list(calendar.month_name).index(month))[1]

        # Aggregate the data by day and count the number of barks
        daily_counts = monthly_data.groupby('Day').size().reindex(range(1, days_in_month + 1), fill_value=0)

        # Skip months with no data
        if daily_counts.sum() == 0:
            continue

        # Create a bar graph of the number of barks per day
        fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, figsize=(10, 18), sharex=True)

        # Bar graph for number of barks per day
        ax1.bar(daily_counts.index, daily_counts)
        ax1.set_xlabel('Day')
        ax1.set_ylabel('Number of Barks')
        ax1.set_title(f'Bark Detection - {month}')

        # Print the total number of barks on each bar
        for i, count in enumerate(daily_counts):
            ax1.text(i + 1, count, str(count), ha='center', va='bottom', rotation='vertical')

        # Bar graph for number of barks between 10 PM and 6 AM
        nighttime_data = monthly_data[(monthly_data['Timestamp'].str.split().str[3] >= '22:00:00') |
                                      (monthly_data['Timestamp'].str.split().str[3] <= '06:00:00')]

        nighttime_counts = nighttime_data.groupby('Day').size().reindex(range(1, days_in_month + 1), fill_value=0)

        ax2.bar(nighttime_counts.index, nighttime_counts)
        ax2.set_xlabel('Day')
        ax2.set_ylabel('Number of Barks (10 PM - 6 AM)')
        ax2.set_title('Nighttime Barks (10 PM - 6 AM)')

        # Print the number of nighttime barks on each bar
        for i, count in enumerate(nighttime_counts):
            ax2.text(i + 1, count, str(count), ha='center', va='bottom', rotation='vertical')

        # Check for more than 20 barks in a 5-minute period
        monthly_data['Timestamp'] = pd.to_datetime(monthly_data['Timestamp'], format='%a %b %d %H:%M:%S %Y')
        monthly_data['5min_period'] = monthly_data['Timestamp'].dt.floor('5min')
        high_activity_periods = monthly_data.groupby(['Day', '5min_period']).size()
        high_activity_periods = high_activity_periods[high_activity_periods > 20].groupby('Day').size().reindex(
            range(1, days_in_month + 1), fill_value=0)

        ax3.bar(high_activity_periods.index, high_activity_periods)
        ax3.set_xlabel('Day')
        ax3.set_ylabel('Number of High Activity Periods')
        ax3.set_title('High Activity Periods (>20 Barks in 5 Minutes Period)')

        # Print the number of high activity periods on each bar
        for i, count in enumerate(high_activity_periods):
            ax3.text(i + 1, count, str(count), ha='center', va='bottom', rotation='vertical')

        # Save the current graphs to the PDF file
        pdf.savefig(fig, bbox_inches='tight')

        # Clear the current figure to create new graphs for the next month
        plt.clf()


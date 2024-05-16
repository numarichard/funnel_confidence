import pandas as pd
import csv

# Define the number of lines to skip at the start
skip_lines = 5

# Manually process the CSV file to remove unnecessary characters
processed_data = []
with open('/mnt/data/streamlit_test.csv', 'r') as file:
    reader = csv.reader(file, delimiter=',')
    for i, row in enumerate(reader):
        if i >= skip_lines:
            cleaned_row = [item.strip().strip('"') for item in row]
            processed_data.append(cleaned_row)

# Convert the processed data into a DataFrame
columns = processed_data[0]
data = processed_data[1:]

streamlit_test_df_cleaned = pd.DataFrame(data, columns=columns)

# Transpose the DataFrame to have dates as rows and events as columns
streamlit_test_df_cleaned.set_index('Event', inplace=True)
streamlit_test_df_transposed = streamlit_test_df_cleaned.transpose().reset_index()
streamlit_test_df_transposed.columns = ['Date', 'Appointment Agent Started', 'Appointment Agent Booked']

# Convert the counts to integers
streamlit_test_df_transposed['Appointment Agent Started'] = streamlit_test_df_transposed['Appointment Agent Started'].astype(int)
streamlit_test_df_transposed['Appointment Agent Booked'] = streamlit_test_df_transposed['Appointment Agent Booked'].astype(int)

# Save the transformed DataFrame to a new CSV file
streamlit_test_df_transposed.to_csv('/mnt/data/expected_converted.csv', index=False)

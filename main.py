"""Main Module."""
from pathlib import Path

import pandas as pd

import text_processing as txt
import data_processing as process
import tr_holidays as holiday

dataset_dir = (Path().resolve() / "data").absolute().as_posix()

if __name__ == '__main__':
    # Read the dataset
    data = pd.read_csv(f"{dataset_dir}/2022_rail_systems_dataset.csv",
                       delimiter=',',
                       encoding='latin-1')
    # Apply text processing
    cleaned_data = txt.text_processing(data)
    # Apply data processing
    processed_data = process.data_processing(cleaned_data)
    # Save cleaned and processed data as csv file
    processed_data.to_csv(f"{dataset_dir}/processed_data_2022_rail_stations.csv",
                          index=False,
                          header=True)
    # Generate TR holidays data
    holiday_frame = holiday.generate_holidays_data()
    holiday_frame['Holiday'] = holiday.add_number_to_duplicates(holiday_frame['Holiday'])
    # Save generated data as csv file
    holiday_frame.to_csv(f"{dataset_dir}/tr_holidays.csv", index=False)
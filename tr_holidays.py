"""This module obtains public holidays data for TR."""

import pandas as pd
import holidays


def generate_holidays_data():
    tr_holidays =  holidays.country_holidays('TR', years=[2022])
    holiday_frame = pd.DataFrame(list(tr_holidays.items()),
                                 columns=['Date', 'Holiday'])
    holiday_frame['Date'] = pd.to_datetime(holiday_frame['Date'])
    return holiday_frame

"""This module handling character conversions and text processing."""

import pandas as pd
import numpy as np

translation_dict = {
    'ð' : 'g',
    'þ': 's',
    'ý': 'i',
    'Ý': 'I',
    'Þ': 'S',
    'Ð': 'G'
}

words_to_remove = [' Kuzey',' Güney',' 2',' 3 Stad Girisi',
                   ' Dogu',' 1 Bati',' kuzey',' güney',
                   ' 1', '-1', '-2', '-3', '-4',
                   ' M7 Hol 3', ' M7 Hol 1', ' M7 Hol',  'M7 Hol 4',
                   ' (Dogu)', ' (Bati)', ' (Dogu/Adliye)', 'M4 ',
                   ' Bati konkors', ' konkors',
                   ' DOGU', ' M7 HOL', ' M7 HOL 1',
                   ' BATI', ' M3 HOL 4', ' M3 HOL 3', 'M7 ', ' Çayirbasi']

def replace_chars(text: str):
    """Replace unknown characters with a new character."""
    if isinstance(text, str):
        for key, value in translation_dict.items():
            if key in text:
                text = text.replace(key, value)
    else:
        raise ValueError(f'Text must be a string, currently type is {type(text)}')
    return text

def remove_words(text:str, words_to_remove:str):
    """Remove unnecessary words."""
    for word in words_to_remove:
        text = text.replace(word, '')
    return text


def text_processing(data: pd.DataFrame):
    """Apply text processing to related columns."""
    data['town'] = data['town'].apply(lambda x: replace_chars(str(x)))
    data['station_name'] = data['station_name'].apply(lambda x: replace_chars(str(x)))
    data['station_name'] = data['station_name'].apply(lambda x: remove_words(x, words_to_remove))
    data.replace('nan', np.nan, inplace=True)
    return data

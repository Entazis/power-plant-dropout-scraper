from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import numpy as np


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


def get_mavir_dropouts():
    """
    Downloads the page where the list of dropouts is found
    and returns a list of strings, one per dropout
    """
    date = datetime.now().strftime("%Y.%m.%d")
    url = 'https://publikacio.mavir.hu/Publikacio/index_hu.jsp?LanguageChooser=hu&ReportChooser=AABI&DateField=' + date + '&submit=Riport'
    response = simple_get(url)

    if response is not None:
        html = BeautifulSoup(response, 'html.parser')
        tables = html.findChildren('table')

        # This will get the first (and only) table.
        dropout_table = tables[0]
        rows = dropout_table.findChildren(['th', 'tr'])

        columns = []

        for idx1, row in enumerate(rows):
            cells = row.findChildren('td')
            if idx1 == 1:
                # this is the header row
                for idx2, cell in enumerate(cells):
                    if not (cell.string is None):
                        value = cell.string.strip()
                    else:
                        value = np.nan
                    columns.append(value)
                df = pd.DataFrame(columns=columns)
            elif idx1 > 1:
                entry = []
                for idx2, cell in enumerate(cells):
                    if not (cell.string is None):
                        value = cell.string.strip()
                    entry.append(value)
                entry_sr = pd.Series(data=entry, index=columns)
                df = df.append(entry_sr, ignore_index=True)
        return df

    # Raise an exception if we failed to get any data from the url
    raise Exception('Error retrieving contents at {}'.format(url))


def get_insideinformation_data():
    date = datetime.now().strftime("%Y.%m.%d")
    url = 'https://www.insideinformation.hu/hu/pubpages/newslistmain.aspx'
    response = simple_get(url)

    # FIXME
    if response is not None:
        html = BeautifulSoup(response, 'html.parser')
        listitems = html\
            .find("div", {"id": "ctl00_ctl22_g_25b7bc98_0172_4fdb_9943_36864c28b54b_pportpublish_outerlist"})
        for table in listitems:
            create_date = table.find("div", {"class": "pportList_CreateDate"}).text.strip()
            event_name_hu = table.find("td", {"class": "pportList_header_left_1"}).text.strip()
            event_name_en = table.find("td", {"class": "pportList_header_right_1"}).text.strip()

            tables_hu = table.find("table", {"class": "pportList_publication_innertable_left"})

            event_type_title_hu = table.find("td", {"class": "pportList_2ndrow"})\
                .find("span").text.strip()
            event_type_hu = table.find("td", {"class": "pportList_2ndrow"})\
                .find("span", {"class": "pportList_value1"}).text.strip()

            third_row_spans = tables_hu.find("td", {"class", "pportList_3rdrow"}).find_all("span")
            event_startdate_title_hu = third_row_spans[0].text.strip()
            event_startdate = third_row_spans[1].text.strip()
            event_enddate_title_hu = third_row_spans[2].text.strip()
            event_enddate = third_row_spans[3].text.strip()

            event_unit_title_hu = table.find("td", {"class": "pportList_4throw"})\
                .find("span").text.strip()
            event_unit_hu = table.find("td", {"class": "pportList_4throw"})\
                .find("span", {"class": "pportList_value1"}).text.strip()
            ...
        columns = []


if __name__ == '__main__':
    # print('Getting mavir data....')
    # dropouts = get_mavir_dropouts()
    # dropouts.to_csv('mavir_dropouts.csv', index=False)
    # print('... done.\n')

    # print('Getting insideinformation data....')
    # dropouts = get_insideinformation_data()
    # dropouts.to_csv('insideinformation_dropouts.csv', index=False)
    # print('... done.\n')


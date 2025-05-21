import datetime
import streamlit as st
from config import TABLE_FIXTURES, TABLE_ODDS, TABLE_RESULTS

conn = st.connection('pinnacle', type='sql')


@st.cache_data()
def get_unique_leagues(sport: str, date_from: datetime, date_to: datetime):
    """
    Fetches unique leagues based on a sport and a given time range.

    This function retrieves distinct leagues from the fixtures table in the database
    for a specific sport and time range. The results include league identifiers and
    their respective names. The function is data cache-enabled to optimize repeated
    queries for the same parameters.

    :param sport: The name of the sport for which to fetch leagues.
                   Example: "soccer", "basketball".
    :type sport: str
    :param date_from: The start date and time to filter fixtures. Only fixtures
                      starting from this date and time will be considered.
    :type date_from: datetime
    :param date_to: The end date and time to filter fixtures. Only fixtures
                    starting up to this date and time will be considered.
    :type date_to: datetime
    :return: A list of tuples where each tuple contains a league ID and the league name.
    :rtype: list[tuple]
    """
    return conn.query(f"SELECT DISTINCT(league_id), league_name FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}'")


def get_rowcount(table: str, date_from: datetime, date_to: datetime, league_ids: str, markets: str, periods: str):
    """
    Fetch the row count from a given database table based on multiple filter parameters.

    This function queries the database table to count the number of rows that satisfy the
    conditions specified by the provided filters for date range, league IDs, markets, and periods.

    :param table: Name of the database table to query.
    :type table: str
    :param date_from: Start date of the range for filtering rows.
    :type date_from: datetime
    :param date_to: End date of the range for filtering rows.
    :type date_to: datetime
    :param league_ids: List or set of league IDs used for filtering rows.
    :type league_ids: str
    :param markets: List or set of market identifiers used for filtering rows.
    :type markets: str
    :param periods: List or set of period identifiers used for filtering rows.
    :type periods: str
    :return: Total row count that meets the filter conditions.
    :rtype: int
    """
    return conn.query(f"SELECT COUNT(id) FROM {table} WHERE starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_id IN {league_ids} AND market IN {markets} AND period IN {periods}").to_dict('records')


def get_preview(table: str, date_from: datetime, date_to: datetime, league_ids: str, markets: str, periods: str):
    """
    Query the database to fetch a preview of data based on the specified table name, date range, league IDs, markets,
    and periods. The results are ordered randomly and limited to three records.

    :param table: The name of the table to query.
    :type table: str
    :param date_from: The starting date and time for filtering the records, inclusive.
    :type date_from: datetime
    :param date_to: The ending date and time for filtering the records, inclusive.
    :type date_to: datetime
    :param league_ids: A comma-separated string of league IDs to filter the results.
    :type league_ids: str
    :param markets: A comma-separated string of market types to filter the results.
    :type markets: str
    :param periods: A comma-separated string of periods to filter the results.
    :type periods: str
    :return: A list of randomly ordered records from the query, limited to three results.
    :rtype: Any
    """
    return conn.query(f"SELECT * FROM {table} WHERE starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_id IN {league_ids} AND market IN {markets} AND period IN {periods} ORDER BY RAND() LIMIT 3")


def get_granular_event_ids(date_from: datetime, date_to: datetime, league_ids: str):
    """
    Fetches and returns a set of granular event IDs based on specified date range and league IDs.

    The function queries the database for events that start within the provided date range
    and belong to the specified leagues. This allows for filtering events on a granular
    level using the given parameters.

    :param date_from: The starting date and time for filtering events.
    :type date_from: datetime
    :param date_to: The ending date and time for filtering events.
    :type date_to: datetime
    :param league_ids: A string or formatted list of league IDs to filter the events.
    :type league_ids: str
    :return: A set of event IDs that match the filtering criteria.
    :rtype: set
    """
    return {event_id for event_id in conn.query(f"SELECT event_id FROM {TABLE_FIXTURES} WHERE starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_id IN {league_ids}")['event_id']}


def get_granular_rowcount(event_ids: str, markets: str, periods: str):
    """
    Calculate and retrieve the row count from a specific database table based on the
    provided event IDs, markets, and periods. The function forms a SQL query using
    the given parameters and executes it to determine the count of rows matching
    the criteria.

    :param event_ids: Comma-separated string of event IDs to filter rows in the query.
    :type event_ids: str
    :param markets: Comma-separated string of market names to filter rows in the
        query.
    :type markets: str
    :param periods: Comma-separated string of time periods to filter rows in the
        query.
    :type periods: str
    :return: A list of dictionaries containing the row count result for the
        matching query specified by the given parameters.
    :rtype: list[dict]
    """
    return conn.query(f"SELECT COUNT(id) FROM {TABLE_ODDS} WHERE event_id IN {event_ids} AND market IN {markets} AND period IN {periods}").to_dict('records')


def get_granular_fixtures_preview(date_from: datetime, date_to: datetime, league_ids: str):
    """
    Fetches a random selection of fixtures based on given date range and league IDs.

    This function retrieves a limited random range of fixture records from the
    database where the fixtures belong to specified leagues and fall within the
    given date range. The results are ordered in random order and provide a preview
    of granular fixture data.

    :param date_from: The start date and time for filtering fixtures. Must be in datetime format.
    :param date_to: The end date and time for filtering fixtures. Must be in datetime format.
    :param league_ids: A string of league IDs defining the leagues to include in the selection.
    :return: A query result containing a random selection of up to 3 fixtures matching the criteria.
    """
    return conn.query(f"SELECT * FROM {TABLE_FIXTURES} WHERE starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_id IN {league_ids} ORDER BY RAND() LIMIT 3")


def get_granular_odds_preview(event_ids: str, markets: str, periods: str):
    """
    Fetches a granular preview of odds data based on given event IDs, markets, and periods.
    This function executes a query that retrieves odds data filtered by the provided
    event IDs, markets, and periods parameters. The results are ordered by ID in descending
    order, and limited to the top three entries.

    :param event_ids: A string representing event IDs to filter the data.
    :param markets: A string specifying market types to filter the odds.
    :param periods: A string indicating periods to filter the odds data.
    :return: The query result containing filtered and ordered odds data, limited to three entries.
    :rtype: Any
    """
    return conn.query(f"SELECT * FROM {TABLE_ODDS} WHERE event_id IN {event_ids} AND market IN {markets} AND period IN {periods} ORDER BY id DESC LIMIT 3")


def get_granular_results_preview(event_ids: str, periods: str):
    """
    Retrieve granular results preview from the database.

    This function fetches a preview of results from the database table defined
    in the constant `TABLE_RESULTS`. The query filters the results based on the
    provided event IDs and periods, ordering the results by descending ID, and
    limits the data to the most recent three entries.

    :param event_ids: A string representing event IDs to filter the query. This
        should contain properly formatted event IDs to ensure valid database
        query execution.
    :param periods: A string representing periods to filter the query. This
        should contain properly formatted periods to ensure valid database
        query execution.
    :return: The function returns the results retrieved from the database query.
        Typically, this is the subset of the dataset as filtered and ordered by
        the query parameters.
    """
    return conn.query(f"SELECT * FROM {TABLE_RESULTS} WHERE event_id IN {event_ids} AND period IN {periods} ORDER BY id DESC LIMIT 3")


def get_unique_leagues_id(sport: str, date_from: datetime, date_to: datetime, tour: str):
    """
    Retrieve unique league IDs based on specific criteria such as sport type, date range,
    and tournament type. This function queries a database for distinct league IDs that
    match the conditions specified based on the desired tour category and filters unique values
    from the result set. The function supports ATP (singles, doubles, challengers), WTA
    (main, doubles, 125k series), and ITF (men's and women's singles and doubles) tournaments.

    :param sport: Sport category to filter the leagues (e.g., Tennis).
    :type sport: str
    :param date_from: Start date to filter fixtures within the desired timeframe.
    :type date_from: datetime
    :param date_to: End date to filter fixtures within the desired timeframe.
    :type date_to: datetime
    :param tour: Specific tournament type filter to apply (e.g., 'All ATP Singles',
        'All WTA Doubles').
    :type tour: str
    :return: Set of unique league IDs matching the specified filters. Returns None
        if no results match the criteria.
    :rtype: set[int] or None
    """
    if tour == 'All ATP Singles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ATP%' AND league_name NOT LIKE '%Challenger%' AND league_name NOT LIKE '%Doubles%'")['league_id']}
    elif tour == 'All ATP Doubles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ATP%' AND league_name NOT LIKE '%Challenger%' AND league_name LIKE '%Doubles%'")['league_id']}

    elif tour == 'All ATP Challenger Singles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ATP Challenger%' AND league_name NOT LIKE '%Doubles%'")['league_id']}
    elif tour == 'All ATP Challenger Doubles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ATP Challenger%' AND league_name LIKE '%Doubles%'")['league_id']}

    elif tour == 'All WTA Singles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%WTA%' AND league_name NOT LIKE '%125k%' AND league_name NOT LIKE '%Doubles%'")['league_id']}
    elif tour == 'All WTA Doubles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%WTA%' AND league_name NOT LIKE '%125k%' AND league_name LIKE '%Doubles%'")['league_id']}

    elif tour == 'All WTA 125k Singles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%WTA 125k%' AND league_name NOT LIKE '%Doubles%'")['league_id']}
    elif tour == 'All WTA 125k Doubles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%WTA 125k%' AND league_name LIKE '%Doubles%'")['league_id']}

    elif tour == 'All ITF Men Singles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ITF Men%' AND league_name NOT LIKE '%Doubles%'")['league_id']}
    elif tour == 'All ITF Men Doubles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ITF Men%' AND league_name LIKE '%Doubles%'")['league_id']}

    elif tour == 'All ITF Women Singles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ITF Women%' AND league_name NOT LIKE '%Doubles%'")['league_id']}
    elif tour == 'All ITF Women Doubles':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ITF Women%' AND league_name LIKE '%Doubles%'")['league_id']}
    return None

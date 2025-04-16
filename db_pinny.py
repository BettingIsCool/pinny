import datetime
import pandas as pd
import streamlit as st
from sqlalchemy.sql import text
from config import TABLE_LEAGUES, TABLE_FIXTURES, TABLE_ODDS, TABLE_RESULTS, TABLE_OPENING, TABLE_CLOSING

conn = st.connection('pinnacle', type='sql')


@st.cache_data()
def get_unique_leagues(sport: str, date_from: datetime, date_to: datetime):

    return conn.query(f"SELECT DISTINCT(league_id), league_name FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}'")


def get_rowcount(table: str, date_from: datetime, date_to: datetime, league_ids: str, markets: str, periods: str):

    return conn.query(f"SELECT COUNT(event_id) FROM {table} WHERE starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_id IN {league_ids} AND market IN {markets} AND period IN {periods}").to_dict('records')


def get_preview(table: str, date_from: datetime, date_to: datetime, league_ids: str, markets: str, periods: str):

    return conn.query(f"SELECT * FROM {table} WHERE starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_id IN {league_ids} AND market IN {markets} AND period IN {periods} ORDER BY RAND() LIMIT 3")


def get_granular_event_ids(date_from: datetime, date_to: datetime, league_ids: str):

    return {event_id for event_id in conn.query(f"SELECT event_id FROM {TABLE_FIXTURES} WHERE starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_id IN {league_ids}")['event_id']}


def get_granular_rowcount(event_ids: str, markets: str, periods: str):

    return conn.query(f"SELECT COUNT(id) FROM {TABLE_ODDS} WHERE event_id IN {event_ids} AND market IN {markets} AND period IN {periods}").to_dict('records')

def get_granular_fixtures_preview(date_from: datetime, date_to: datetime, league_ids: str):

    return conn.query(f"SELECT * FROM {TABLE_FIXTURES} WHERE starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_id IN {league_ids} ORDER BY RAND() LIMIT 3")


def get_granular_odds_preview(event_ids: str, markets: str, periods: str):

    return conn.query(f"SELECT * FROM {TABLE_ODDS} WHERE event_id IN {event_ids} AND market IN {markets} AND period IN {periods} ORDER BY id DESC LIMIT 3")


def get_granular_results_preview(event_ids: str, periods: str):

    return conn.query(f"SELECT * FROM {TABLE_RESULTS} WHERE event_id IN {event_ids} AND period IN {periods} ORDER BY id DESC LIMIT 3")


def get_unique_leagues_id(sport: str, date_from: datetime, date_to: datetime, tour: str):

    if tour == 'ATP':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ATP%' AND league_name NOT LIKE '%Challenger%'")['league_id']}
    elif tour == 'ATP Challenger':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ATP Challenger%'")['league_id']}
    elif tour == 'WTA':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%WTA%' AND league_name NOT LIKE '%125k%'")['league_id']}
    elif tour == 'WTA 125k':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%WTA 125k%'")['league_id']}
    elif tour == 'ITF Men':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ITF Men%'")['league_id']}
    elif tour == 'ITF Women':
        return {league_id for league_id in conn.query(f"SELECT DISTINCT(league_id) FROM {TABLE_FIXTURES} WHERE sport_name = '{sport}' AND starts >= '{date_from.strftime('%Y-%m-%d %H:%M:%S')}' AND starts <= '{date_to.strftime('%Y-%m-%d %H:%M:%S')}' AND league_name LIKE '%ITF Women%'")['league_id']}


from sqlalchemy.sql import text
import pandas as pd

def get_granular_rowcount_temp_tables(event_ids: str, markets: str, periods: str):
    # Parse input strings without ast (e.g., "1,2,3", "(1,2,3)", "[1,2,3]")
    def parse_input(input_str: str, is_int: bool = False) -> list:
        if not input_str:
            return []
        # Remove parentheses, brackets, and whitespace
        cleaned = input_str.strip().strip('()[]').replace(' ', '')
        # Split on commas and filter out empty values
        values = [v.strip() for v in cleaned.split(',') if v.strip()]
        # Convert to int if specified (for event_id, period)
        return [int(v) if is_int else v for v in values]

    # Parse inputs
    event_ids_list = parse_input(event_ids, is_int=True)  # event_id as INT
    markets_list = parse_input(markets, is_int=False)     # market as VARCHAR
    periods_list = parse_input(periods, is_int=True)      # period as INT

    # Hardcode table name to prevent injection
    TABLE_ODDS = 'odds'  # Replace with your actual table name

    # Use a context manager for connection cleanup
    with conn.connect() as connection:
        try:
            # Create placeholders for markets and periods (max 3 items each)
            market_placeholders = ','.join([f':m{i}' for i in range(len(markets_list))])
            period_placeholders = ','.join([f':p{i}' for i in range(len(periods_list))])

            # Handle empty lists
            if not markets_list:
                market_placeholders = 'NULL'
            if not periods_list:
                period_placeholders = 'NULL'

            # Prepare parameters for markets and periods
            params = {}
            for i, m in enumerate(markets_list):
                params[f'm{i}'] = m
            for i, p in enumerate(periods_list):
                params[f'p{i}'] = p

            # Handle small event_ids list (<=1000) with IN clause
            if len(event_ids_list) <= 1000:
                event_placeholders = ','.join([f':e{i}' for i in range(len(event_ids_list))])
                if not event_ids_list:
                    event_placeholders = 'NULL'

                # Parameterized query
                query = text(
                    f"SELECT COUNT(id) AS count FROM {TABLE_ODDS} "
                    f"WHERE event_id IN ({event_placeholders}) "
                    f"AND market IN ({market_placeholders}) "
                    f"AND period IN ({period_placeholders})"
                )

                # Add event_id parameters
                for i, eid in enumerate(event_ids_list):
                    params[f'e{i}'] = eid

                # Execute with pandas
                df = pd.read_sql(query, connection, params=params)
                return df.to_dict('records')

            # Handle large event_ids list (>1000) with temporary table and chunking
            else:
                total_count = 0
                chunk_size = 1000  # Adjust based on testing (e.g., 500, 2000)

                # Create temporary table
                connection.execute(text("CREATE TEMPORARY TABLE temp_event_ids (event_id INT)"))
                connection.execute(text("CREATE INDEX idx_temp_event_id ON temp_event_ids (event_id)"))

                # Insert event_ids in batches
                for i in range(0, len(event_ids_list), chunk_size):
                    chunk = event_ids_list[i:i + chunk_size]
                    connection.execute(
                        text("INSERT INTO temp_event_ids (event_id) VALUES (:eid)"),
                        [{'eid': eid} for eid in chunk]
                    )

                    # Query for this chunk
                    query = text(
                        f"SELECT COUNT(o.id) AS count FROM {TABLE_ODDS} o "
                        "JOIN temp_event_ids e ON o.event_id = e.event_id "
                        f"WHERE o.market IN ({market_placeholders}) "
                        f"AND o.period IN ({period_placeholders})"
                    )

                    # Execute
                    df = pd.read_sql(query, connection, params=params)
                    total_count += df['count'].iloc[0]

                    # Clear temporary table for next chunk
                    connection.execute(text("TRUNCATE TABLE temp_event_ids"))

                # Drop temporary table
                connection.execute(text("DROP TEMPORARY TABLE IF EXISTS temp_event_ids"))

                # Return result in same format
                return [{'count': total_count}]

        finally:
            connection.close()

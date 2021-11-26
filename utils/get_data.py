import pandas as pd

import snowflake.connector as sf
from snowflake.connector import DictCursor
from configs.credentials import snowflake_login

snowflake_connector = sf.connect(
    user=snowflake_login['username'],
    password=snowflake_login['password'],
    account=snowflake_login['account']
)

snowflake_cursor = snowflake_connector.cursor(DictCursor)
snowflake_cursor.execute('USE DATABASE HU_DATA')

def get_posts(query : str):
    """
    Pull posts from snowflake
    Args:
        query: sql query

    returns: dataframe with post text
    """

    # create query
    snowflake_cursor.execute(query)

    # change into rows
    data = [row for row in snowflake_cursor]

    # make dataframe
    posts_df = pd.DataFrame(data)

    # Close coursor connection
    snowflake_cursor.close()

    return posts_df
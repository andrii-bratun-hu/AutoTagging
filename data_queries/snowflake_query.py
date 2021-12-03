# snowflake query

def get_snowflake_query(site):

    query = f"""
        SELECT distinct post_content || 'post_id: ' || post_id as post_content
            , post_id || '_' || site_prefix post_id
        FROM prod."posts"
        WHERE post_status = 'publish' and post_type = 'post'
        and site_prefix = '{site}'
        ORDER BY POST_ID DESC
    """

    return query
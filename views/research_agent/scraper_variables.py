# Facebook Scraper Variables and Constants

# Proxies configuration


# Facebook Base Headers
FB_BASE_URL = "https://www.facebook.com/api/graphql/"
FB_BASE_HEADERS = {
    'origin': 'https://www.facebook.com',
    'referer': 'https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&is_targeted_country=false&media_type=all',
    'x-asbd-id': '359341',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Ad Processing Configuration
MAX_BODY_LENGTH = 600
REQUIRED_AD_FIELDS = ['ad_archive_id', 'page_id', 'page_name']
DEFAULT_MAX_PAGES = 10
MAX_RETRIES = 3

# Query Document IDs
INITIAL_QUERY_DOC_ID = "28754955950818960"
PAGINATION_QUERY_DOC_ID = "9241757445859501"

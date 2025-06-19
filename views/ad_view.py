import asyncio
import aiohttp
import json
import uuid
import logging
import unicodedata
from typing import Dict, List, Optional
from datetime import datetime
import requests
from uuid import UUID
from datetime import datetime
from views.research_agent.scraper_variables import (
    PROXIES,
    FB_BASE_HEADERS,
    MAX_RETRIES,
    INITIAL_QUERY_DOC_ID,
    PAGINATION_QUERY_DOC_ID,
    FB_BASE_URL,
)

logger = logging.getLogger(__name__)

# Facebook API Functions
def get_fb_headers(friendly_name: str, ad_library_url: Optional[str] = None) -> Dict[str, str]:
    """Get Facebook API headers with optional ad library URL."""
    headers = FB_BASE_HEADERS.copy()
    headers['x-fb-friendly-name'] = friendly_name
    if ad_library_url:
        headers['referer'] = f'https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&is_targeted_country=false&media_type=all&search_type=page&view_all_page_id={ad_library_url}'
    return headers

def get_fb_headers_keyword(friendly_name: str, keyword: Optional[str] = None) -> Dict[str, str]:
    """Get Facebook API headers with optional ad library URL."""
    headers = FB_BASE_HEADERS.copy()
    headers['x-fb-friendly-name'] = friendly_name
    if keyword:
        headers['referer'] = f'https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&is_targeted_country=false&media_type=all&q={keyword}&search_type=keyword_unordered'
    return headers

async def make_request(session: aiohttp.ClientSession, url: str, headers: dict, payload: str) -> Optional[Dict]:
    """Make an HTTP request to Facebook API with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            # Use proxy only if configured, otherwise direct connection
            if PROXIES and PROXIES.get('https'):
                try:
                    async with session.post(url, headers=headers, data=payload, proxy=PROXIES['https']) as response:
                        if response.status == 200:
                            data = await response.text()
                            try:
                                return json.loads(data)
                            except json.JSONDecodeError:
                                data_lines = data.split('\n')
                                if len(data_lines) > 1:
                                    return json.loads(data_lines[1])
                                return None
                        elif response.status == 429:
                            wait_time = (attempt + 1) * 5
                            await asyncio.sleep(wait_time)
                            continue
                        return None
                except Exception as proxy_error:
                    logger.warning(f"Proxy failed on attempt {attempt + 1}, trying direct connection: {proxy_error}")
            
            # Direct connection (fallback or when no proxy configured)
            async with session.post(url, headers=headers, data=payload) as response:
                if response.status == 200:
                    data = await response.text()
                    try:
                        return json.loads(data)
                    except json.JSONDecodeError:
                        data_lines = data.split('\n')
                        if len(data_lines) > 1:
                            return json.loads(data_lines[1])
                        return None
                elif response.status == 429:
                    wait_time = (attempt + 1) * 5
                    await asyncio.sleep(wait_time)
                    continue
                return None
        except Exception:
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                return None

def get_initial_payload(page_id: str) -> str:
    """Generate initial payload for Facebook API request."""
    return f'fb_api_caller_class=RelayModern&fb_api_req_friendly_name=AdLibraryMobileFocusedStateProviderRefetchQuery&variables=%7B%22activeStatus%22%3A%22ALL%22%2C%22adType%22%3A%22ALL%22%2C%22audienceTimeframe%22%3A%22LAST_7_DAYS%22%2C%22bylines%22%3A%5B%5D%2C%22contentLanguages%22%3A%5B%5D%2C%22countries%22%3A%5B%22ALL%22%5D%2C%22country%22%3A%22ALL%22%2C%22excludedIDs%22%3A%5B%5D%2C%22fetchPageInfo%22%3Atrue%2C%22fetchSharedDisclaimers%22%3Atrue%2C%22isTargetedCountry%22%3Afalse%2C%22location%22%3Anull%2C%22mediaType%22%3A%22ALL%22%2C%22multiCountryFilterMode%22%3Anull%2C%22pageIDs%22%3A%5B%5D%2C%22potentialReachInput%22%3A%5B%5D%2C%22publisherPlatforms%22%3A%5B%5D%2C%22queryString%22%3A%22%22%2C%22regions%22%3A%5B%5D%2C%22searchType%22%3A%22PAGE%22%2C%22sortData%22%3Anull%2C%22source%22%3Anull%2C%22startDate%22%3Anull%2C%22v%22%3A%22a7cdb2%22%2C%22viewAllPageID%22%3A%22{page_id}%22%7D&server_timestamps=true&doc_id={INITIAL_QUERY_DOC_ID}'

def get_initial_payload_keyword(keyword: str) -> str:
    """Generate initial payload for Facebook API request."""
    encoded_keyword = f'%22{requests.utils.quote(keyword)}%22'
    return f'fb_api_caller_class=RelayModern&fb_api_req_friendly_name=AdLibraryMobileFocusedStateProviderRefetchQuery&variables=%7B%22activeStatus%22%3A%22ALL%22%2C%22adType%22%3A%22ALL%22%2C%22audienceTimeframe%22%3A%22LAST_7_DAYS%22%2C%22bylines%22%3A%5B%5D%2C%22contentLanguages%22%3A%5B%5D%2C%22countries%22%3A%5B%22ALL%22%5D%2C%22country%22%3A%22ALL%22%2C%22excludedIDs%22%3A%5B%5D%2C%22fetchPageInfo%22%3Atrue%2C%22fetchSharedDisclaimers%22%3Atrue%2C%22isTargetedCountry%22%3Afalse%2C%22location%22%3Anull%2C%22mediaType%22%3A%22ALL%22%2C%22multiCountryFilterMode%22%3Anull%2C%22pageIDs%22%3A%5B%5D%2C%22potentialReachInput%22%3A%5B%5D%2C%22publisherPlatforms%22%3A%5B%5D%2C%22queryString%22%3A{encoded_keyword}%2C%22regions%22%3A%5B%5D%2C%22searchType%22%3A%22KEYWORD_EXACT_PHRASE%22%2C%22sortData%22%3Anull%2C%22source%22%3Anull%2C%22startDate%22%3Anull%2C%22v%22%3A%22bfc0a4%22%2C%22viewAllPageID%22%3A%220%22%7D&server_timestamps=true&doc_id={INITIAL_QUERY_DOC_ID}'

def get_pagination_payload(page_id: str, cursor: str) -> str:
    """Generate pagination payload for Facebook API request."""
    return f'fb_api_caller_class=RelayModern&fb_api_req_friendly_name=AdLibrarySearchPaginationQuery&variables=%7B%22activeStatus%22%3A%22ALL%22%2C%22adType%22%3A%22ALL%22%2C%22bylines%22%3A%5B%5D%2C%22contentLanguages%22%3A%5B%5D%2C%22countries%22%3A%5B%22ALL%22%5D%2C%22cursor%22%3A%22{cursor}%22%2C%22excludedIDs%22%3A%5B%5D%2C%22first%22%3A30%2C%22isTargetedCountry%22%3Afalse%2C%22location%22%3Anull%2C%22mediaType%22%3A%22ALL%22%2C%22multiCountryFilterMode%22%3Anull%2C%22pageIDs%22%3A%5B%5D%2C%22potentialReachInput%22%3A%5B%5D%2C%22publisherPlatforms%22%3A%5B%5D%2C%22queryString%22%3A%22%22%2C%22regions%22%3A%5B%5D%2C%22searchType%22%3A%22PAGE%22%2C%22sortData%22%3Anull%2C%22source%22%3Anull%2C%22startDate%22%3Anull%2C%22v%22%3A%22a7cdb2%22%2C%22viewAllPageID%22%3A%22{page_id}%22%7D&server_timestamps=true&doc_id={PAGINATION_QUERY_DOC_ID}'

def get_pagination_payload_keyword(keyword: str, cursor: str) -> str:
    """Generate pagination payload for Facebook API request."""
    encoded_keyword = f'%22{requests.utils.quote(keyword)}%22'
    return f'fb_api_caller_class=RelayModern&fb_api_req_friendly_name=AdLibrarySearchPaginationQuery&variables=%7B%22activeStatus%22%3A%22ALL%22%2C%22adType%22%3A%22ALL%22%2C%22bylines%22%3A%5B%5D%2C%22contentLanguages%22%3A%5B%5D%2C%22countries%22%3A%5B%22ALL%22%5D%2C%22cursor%22%3A%22{cursor}%22%2C%22excludedIDs%22%3A%5B%5D%2C%22first%22%3A30%2C%22isTargetedCountry%22%3Afalse%2C%22location%22%3Anull%2C%22mediaType%22%3A%22ALL%22%2C%22multiCountryFilterMode%22%3Anull%2C%22pageIDs%22%3A%5B%5D%2C%22potentialReachInput%22%3A%5B%5D%2C%22publisherPlatforms%22%3A%5B%5D%2C%22queryString%22%3A{encoded_keyword}%2C%22regions%22%3A%5B%5D%2C%22searchType%22%3A%22KEYWORD_EXACT_PHRASE%22%2C%22sortData%22%3Anull%2C%22source%22%3Anull%2C%22startDate%22%3Anull%2C%22v%22%3A%22c7f025%22%2C%22viewAllPageID%22%3A%220%22%7D&server_timestamps=true&doc_id={PAGINATION_QUERY_DOC_ID}'

def process_text_fields(snapshot: Dict, cards: Dict) -> Dict[str, Optional[str]]:
    """Extract and process text fields from snapshot and cards."""
    logger.debug("Processing text fields from snapshot and cards")
    
    # Initialize all fields as None
    result = {
        'ad_body': None,
        'title': None,
        'link_url': None,
        'caption': None,
        'cta_text': None,
        'cta_type': None
    }
    
    try:
        # Ad Body
        if cards and cards.get('body'):
            result['ad_body'] = cards['body'].strip()[:600]
        elif snapshot and snapshot.get('body') and isinstance(snapshot['body'], dict) and snapshot['body'].get('text'):
            result['ad_body'] = snapshot['body']['text'].strip()[:600]

        # Title
        if cards and cards.get('title'):
            result['title'] = cards['title'].strip()
        elif snapshot and snapshot.get('title'):
            result['title'] = snapshot['title'].strip()

        # External Link
        if cards and cards.get('link_url'):
            result['link_url'] = cards['link_url'].strip()
        elif snapshot and snapshot.get('link_url'):
            result['link_url'] = snapshot['link_url'].strip()

        # Caption
        if cards and cards.get('caption'):
            result['caption'] = cards['caption'].strip()
        elif snapshot and snapshot.get('caption'):
            result['caption'] = snapshot['caption'].strip()

        # CTA fields
        if cards and cards.get('cta_text'):
            result['cta_text'] = cards['cta_text'].strip()
        elif snapshot and snapshot.get('cta_text'):
            result['cta_text'] = snapshot.get('cta_text').strip()

        if cards and cards.get('cta_type'):
            result['cta_type'] = cards['cta_type'].strip()
        elif snapshot and snapshot.get('cta_type'):
            result['cta_type'] = snapshot.get('cta_type').strip()

        logger.debug(f"Processed text fields - Title: {bool(result['title'])}, Body: {bool(result['ad_body'])}, Link: {bool(result['link_url'])}")
        return result
    except Exception as e:
        logger.error(f"Error processing text fields: {str(e)}", exc_info=True)
        return result

def process_timestamps(ad: Dict) -> Dict[str, Optional[str]]:
    """Process timestamp fields from ad data."""
    logger.debug("Processing timestamp fields")
    start_date = datetime.utcfromtimestamp(ad.get("start_date", 0)).isoformat() if ad.get("start_date") else None
    end_date = datetime.utcfromtimestamp(ad.get("end_date", 0)).isoformat() if ad.get("end_date") else None
    
    logger.debug(f"Processed timestamps - Start: {bool(start_date)}, End: {bool(end_date)}")
    return {
        'start_date': start_date,
        'end_date': end_date
    }

def normalize_text(text):
    try:
        text = unicodedata.normalize('NFKD', text)
        return text.strip()
    except Exception as e:
        logger.warning(f"Error normalizing text: {str(e)}")
        return text
    
def validate_and_stringify_json(data, return_empty_structure=False):
    try:
        if isinstance(data, dict):
            cleaned_data = {k: v for k, v in data.items() if v is not None}
            if cleaned_data:
                return json.dumps(cleaned_data)
            return json.dumps({}) if return_empty_structure else None
        
        elif isinstance(data, list):
            cleaned_data = [item for item in data if item is not None]
            if cleaned_data:
                return json.dumps(cleaned_data)
            return json.dumps([]) if return_empty_structure else None
        
        return json.dumps(data)
    
    except (TypeError, ValueError) as error:
        logger.error(f"Error stringifying JSON: {str(error)}")
        return None
    
def extract_media_urls(ad):
    logger.debug("Extracting media URLs from ad")
    try:
        image_url = (
            ad['snapshot']['images'][0]['original_image_url']
            if ad.get('snapshot') and ad['snapshot'].get('images') and ad['snapshot']['images'][0].get('original_image_url')
            else ad['snapshot']['cards'][0]['original_image_url']
            if ad.get('snapshot') and ad['snapshot'].get('cards') and ad['snapshot']['cards'][0].get('original_image_url')
            else None
        )
        video_url = (
            ad['snapshot']['videos'][0]['video_hd_url']
            if ad.get('snapshot') and ad['snapshot'].get('videos') and ad['snapshot']['videos'][0].get('video_hd_url')
            else ad['snapshot']['cards'][0]['video_hd_url']
            if ad.get('snapshot') and ad['snapshot'].get('cards') and ad['snapshot']['cards'][0].get('video_hd_url')
            else None
        )
        page_profile_picture_url = (
            ad.get('snapshot', {}).get('page_profile_picture_url')
            if ad.get('snapshot', {}).get('page_profile_picture_url')
            else None
        )
        avatar_url = page_profile_picture_url
        snapshot = ad.get('snapshot', {})
        cards = snapshot.get('cards', [])
        videos = snapshot.get('videos', [])

        if videos and videos[0].get('video_preview_image_url'):
            preview_image_url = videos[0]['video_preview_image_url']
        elif cards and cards[0].get('video_preview_image_url'):
            preview_image_url = cards[0]['video_preview_image_url']
        else:
            preview_image_url = None

        logger.debug(f"Extracted media URLs - Image: {bool(image_url)}, Video: {bool(video_url)}, Avatar: {bool(avatar_url)}")
        return {
            's3_image_url': image_url,
            's3_video_url': video_url,
            'avatar_url': avatar_url,
            'preview_image_url': preview_image_url,
            'page_profile_picture_url': page_profile_picture_url
        }
    except Exception as e:
        logger.error(f"Error extracting media URLs: {str(e)}")
        return {
            's3_image_url': None,
            's3_video_url': None,
            'avatar_url': None,
            'preview_image_url': None,
            'page_profile_picture_url': None
        }

def process_single_ad(ad: Dict) -> Optional[Dict]:
    """Process a single raw ad into the required format."""
    try:
        logger.debug(f"Processing ad with archive ID: {ad.get('ad_archive_id')}")
        ad_archive_id = ad.get('ad_archive_id')
        # Extract snapshot and cards
        snapshot = ad.get('snapshot', {})
        cards = snapshot.get('cards', [{}])[0] if snapshot.get('cards') else {}
        
        # Process text fields
        text_fields = process_text_fields(snapshot, cards)
        # Process timestamps
        timestamps = process_timestamps(ad)
        
        # Process impression
        impression = None if ad.get('impressions_with_index', {}).get('impressions_index', -1) == -1 \
                    else ad.get('impressions_with_index', {}).get('impressions_index')
        publisher_platforms = ad.get('publisher_platform', [])
        publisher_platforms_lowercase = [platform.lower() for platform in ad.get('publisher_platform', [])]

        media_urls = extract_media_urls(ad)
        
        # Create brand object
        brand_data = {
            'name': normalize_text(ad.get('page_name')),
            'avatar_url': media_urls['avatar_url'],
            'page_id': ad.get('page_id')
        }

        # Create ad object
        ad_data = {
            'body': text_fields['ad_body'],
            'title': text_fields['title'],
            'objectID': ad_archive_id
        }

        processed_ad = {
            "id": str(uuid.uuid4()),
            "family": "SPY",
            "brand": brand_data,
            "country": None,
            "ad": ad_data,
            "ad_status": "active" if ad.get("is_active") else "inactive",
            "ad_start_date": timestamps['start_date'],
            "ad_end_date": timestamps['end_date'],
            "ad_platforms": publisher_platforms_lowercase,
            "ad_display_format": "image" if media_urls['s3_image_url'] else "video" if media_urls['s3_video_url'] else None,
            "ad_external_link": ad.get('snapshot', {}).get('link_url') or None,
            "s3_image_url": media_urls['s3_image_url'],
            "s3_video_url": media_urls['s3_video_url'],
            "preview_image_url": media_urls['preview_image_url'],
            "video_len": None,
            "category": None,
            "tiktok_reach": ad.get("tiktok_reach"),
            "language": None,
            "theme": None,
            "likes": ad.get("page_like_count"),
            "marketing_goals": ad.get("marketing_goals"),
            "rating": None,
            "major_theme": None,
            "spend": ad.get("spend", None),
            "impression": impression,
            "ad_body": text_fields['ad_body'],
            "brand_name": normalize_text(ad.get('page_name')),
            "title": text_fields['title'],
            "avatar_url": media_urls['avatar_url'],
            "ranking": None,
            "industry": None,
            "sub_industry": None,
            "neice": None,
            "lang": None,
            "archive_id": ad_archive_id
        }
        logger.debug(f"Successfully processed ad {ad_archive_id}")
        return processed_ad
        
    except Exception as e:
        logger.error(f"Error processing ad: {str(e)}", exc_info=True)
        return None
    
def process_ads(ads: List[Dict]) -> List[Dict]:
    """Process a list of raw ads into the required format."""
    logger.info(f"Processing batch of {len(ads)} ads")
    processed_ads = []
    for ad in ads:
        processed_ad = process_single_ad(ad)
        if processed_ad:
            processed_ads.append(processed_ad)
    
    logger.info(f"Successfully processed {len(processed_ads)} out of {len(ads)} ads")
    return processed_ads

def serialize_value(value):
    """Helper function to convert values into JSON serializable types"""
    if isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, bytes):
        return value.decode("utf-8")
    elif isinstance(value, UUID): 
        return str(value)
    elif value is None:
        return None 
    return value

def extract_ads_from_response(data: Dict) -> tuple[List[Dict], Optional[str], bool]:
    """Extract ads from Facebook API response."""
    try:
        if not data or 'data' not in data:
            return [], None, False
        
        ad_library_main = data['data'].get('ad_library_main', {})
        ads_data = ad_library_main.get('ads', {})
        ads = ads_data.get('ads', [])
        
        # Extract cursor for pagination
        page_info = ads_data.get('page_info', {})
        next_cursor = page_info.get('next_cursor')
        has_next_page = page_info.get('has_next_page', False)
        
        return ads, next_cursor, has_next_page
    except Exception as e:
        logger.error(f"Error extracting ads from response: {str(e)}")
        return [], None, False

# Main scraping functions
async def scrape_keyword_ads(keyword: str, cursor: Optional[str]=None, max_pages: int = 5) -> Dict:
    """Scrape Facebook ads for a given keyword and return the ads."""
    total_processed = 0
    all_ads = []
    try:
        async with aiohttp.ClientSession() as session:
            try:
                if not cursor:
                    headers = get_fb_headers_keyword('AdLibraryMobileFocusedStateProviderRefetchQuery', keyword)
                    data = await make_request(session, FB_BASE_URL, headers, get_initial_payload_keyword(keyword))
                else:
                    headers = get_fb_headers_keyword('AdLibrarySearchPaginationQuery', keyword)
                    data = await make_request(session, FB_BASE_URL, headers, get_pagination_payload_keyword(keyword, cursor))

                if not data:
                    return {
                        "success": True,
                        "total_processed": 0,
                        "data": [],
                        "next_cursor": None,
                        "message": None,
                        "has_next_page": False
                    }

                results, next_cursor, has_next_page = extract_ads_from_response(data)
                if not results:
                    return {
                        "success": True,
                        "total_processed": 0,
                        "data": [],
                        "next_cursor": next_cursor,
                        "message": None,
                        "has_next_page": has_next_page
                    }

                # Process the ads
                processed_ads = process_ads(results)
                all_ads.extend(processed_ads)
                total_processed += len(processed_ads)

                return {
                    "success": True,
                    "total_processed": total_processed,
                    "data": all_ads,
                    "next_cursor": next_cursor,
                    "message": None,
                    "has_next_page": has_next_page
                }

            except Exception as e:
                logger.error(f"Error during scraping: {str(e)}", exc_info=True)
                return {
                    "success": False,
                    "total_processed": total_processed,
                    "data": all_ads,
                    "next_cursor": None,
                    "message": str(e),
                    "has_next_page": False
                }
            finally:
                await session.close()
    except Exception as e:
        logger.error(f"Error creating client session: {str(e)}", exc_info=True)
        return {
            "success": False,
            "total_processed": 0,
            "data": [],
            "next_cursor": None,
            "message": str(e),
            "has_next_page": False
        }

async def scrape_facebook_ads(brand_id: Optional[str], page_id: str, cursor: Optional[str] = None, max_pages: int = 5) -> Dict:
    """Scrape Facebook ads for a given page ID or brand ID (stateless, no DB)."""
    total_processed = 0
    all_ads = []
    current_cursor = cursor
    has_next_page = False
    try:
        async with aiohttp.ClientSession() as session:
            try:
                if brand_id:
                    # Multi-page scraping for brand_id case
                    if not current_cursor:
                        headers = get_fb_headers('AdLibraryMobileFocusedStateProviderRefetchQuery')
                        data = await make_request(session, FB_BASE_URL, headers, get_initial_payload(page_id))
                        if data:
                            results, current_cursor, has_next_page = extract_ads_from_response(data)
                            if results:
                                processed_ads = process_ads(results)
                                all_ads.extend(processed_ads)
                                total_processed += len(processed_ads)
                    page = 1
                    while current_cursor and page < max_pages:
                        headers = get_fb_headers('AdLibrarySearchPaginationQuery', page_id)
                        data = await make_request(session, FB_BASE_URL, headers, get_pagination_payload(page_id, current_cursor))
                        if data:
                            results, current_cursor, has_next_page = extract_ads_from_response(data)
                            if results:
                                processed_ads = process_ads(results)
                                all_ads.extend(processed_ads)
                                total_processed += len(processed_ads)
                        page += 1
                    return {
                        "success": True,
                        "total_processed": total_processed,
                        "data": all_ads,
                        "next_cursor": current_cursor,
                        "has_next_page": has_next_page
                    }
                else:
                    # Single page scraping for cursor-based pagination
                    if not cursor:
                        headers = get_fb_headers('AdLibraryMobileFocusedStateProviderRefetchQuery')
                        data = await make_request(session, FB_BASE_URL, headers, get_initial_payload(page_id))
                    else:
                        headers = get_fb_headers('AdLibrarySearchPaginationQuery', page_id)
                        data = await make_request(session, FB_BASE_URL, headers, get_pagination_payload(page_id, cursor))
                    if not data:
                        return {
                            "success": True,
                            "total_processed": 0,
                            "data": [],
                            "next_cursor": None,
                            "has_next_page": False
                        }
                    results, next_cursor, has_next_page = extract_ads_from_response(data)
                    if not results:
                        return {
                            "success": True,
                            "total_processed": 0,
                            "data": [],
                            "next_cursor": next_cursor,
                            "has_next_page": has_next_page
                        }
                    processed_ads = process_ads(results)
                    all_ads.extend(processed_ads)
                    total_processed += len(processed_ads)
                    return {
                        "success": True,
                        "total_processed": total_processed,
                        "data": all_ads,
                        "next_cursor": next_cursor,
                        "has_next_page": has_next_page
                    }
            except Exception as e:
                logger.error(f"Error during scraping: {str(e)}", exc_info=True)
                return {
                    "success": False,
                    "message": str(e),
                    "data": [],
                    "next_cursor": None,
                    "has_next_page": False
                }
            finally:
                await session.close()
    except Exception as e:
        logger.error(f"Error creating client session: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": str(e),
            "data": [],
            "next_cursor": None,
            "has_next_page": False
        }

def suggestion_adsbase_for_brand_name(brand_name):
    url = "https://www.facebook.com/api/graphql/"
    payload = f'fb_api_caller_class=RelayModern&fb_api_req_friendly_name=useAdLibraryTypeaheadSuggestionDataSourceQuery&variables=%7B%22queryString%22%3A%22{brand_name}%22%2C%22isMobile%22%3Afalse%2C%22country%22%3A%22IN%22%2C%22adType%22%3A%22ALL%22%7D&server_timestamps=true&doc_id=9333890689970605'
    headers = {
        'origin': 'https://www.facebook.com',
        'x-fb-friendly-name': 'useAdLibraryTypeaheadSuggestionDataSourceQuery',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        # Use proxy only if configured, otherwise direct connection
        if PROXIES:
            try:
                response = requests.request("POST", url, headers=headers, data=payload, proxies=PROXIES, timeout=10)
            except Exception as proxy_error:
                logger.warning(f"Proxy failed, trying direct connection: {proxy_error}")
                response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
        else:
            # Direct connection when no proxy configured
            response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
        
        json_data = response.json()
        pages = json_data["data"]["ad_library_main"]["typeahead_suggestions"]["page_results"]
        result = []
        for page in pages:
            result.append({
                "adlibrary_url": page.get("page_id"),
                "brand_name": page.get("name"),
                "category": page.get("category"),
                "avatar_url": page.get("image_uri"),
                "likes": page.get("likes"),
                "verification": page.get("verification"),
                "page_alias": page.get("page_alias"),
                "ig_username": page.get("ig_username"),
                "ig_followers": page.get("ig_followers"),
                "ig_verification": page.get("ig_verification"),
            })
        return {"suggestions": result}
    except Exception as e:
        logger.error(f"Error in suggestion_adsbase_for_brand_name: {str(e)}")
        return {"error": str(e), "suggestions": []}

# Legacy functions for backward compatibility
def get_ads(keyword: str):
    """Legacy function for getting ads by keyword"""
    # This is a placeholder - in real implementation, you might want to call scrape_keyword_ads
    # For now, return mock data
    return []

def generate_image(image_url: str, description: str):
    """Legacy function for image generation"""
    # Placeholder implementation
    return f"/static/generated/{uuid.uuid4()}.jpg"

def clone_ad(new_image_url: str, new_description: str):
    """Legacy function for ad cloning"""
    image_url = generate_image(new_image_url, new_description)
    return {"image_url": image_url} 
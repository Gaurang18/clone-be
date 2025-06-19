from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import asyncio
from dto.ad import AdOut, KeywordRequest, CloneRequest, ImageResponse
from views.auth_view import get_current_user
from views.ad_view import get_ads, clone_ad, scrape_keyword_ads, scrape_facebook_ads, suggestion_adsbase_for_brand_name
from views.credit_view import update_credits

router = APIRouter()

@router.post("/", response_model=List[AdOut])
def fetch_ads(req: KeywordRequest, user=Depends(get_current_user)):
    return get_ads(req.keyword)

@router.post("/clone", response_model=ImageResponse)
def clone_ad_route(req: CloneRequest, user=Depends(get_current_user)):
    # Update credits
    update_credits(user, "image", -1)
    # Generate new image
    return clone_ad(req.new_image_url, req.new_description)

@router.get("/get-live-research-data")
async def get_live_research_data(
    keyword: Optional[str] = Query(None),
    page_id: Optional[str] = Query(None),
    cursor: Optional[str] = Query(None),
):
    try:
        if keyword:
            return await asyncio.wait_for(
                scrape_keyword_ads(keyword=keyword, cursor=cursor, max_pages=2),
                timeout=290
            )
        elif page_id:
            return await asyncio.wait_for(
                scrape_facebook_ads(brand_id=None, page_id=page_id, cursor=cursor, max_pages=2),
                timeout=290
            )
        else:
            raise HTTPException(status_code=400, detail="Either keyword or page_id must be provided")
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="The request took too long to complete. Try with fewer pages or try again later."
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request"
        )

@router.get("/suggestion-brand-name")
def get_suggestion_brand_name(
    brand_name: str,
    # user=Depends(JWTBearer())  # Uncomment if you have JWT auth
):
    data = suggestion_adsbase_for_brand_name(brand_name)
    return data 
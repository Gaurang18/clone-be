import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Supabase settings
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    
    # Database settings (optional for now)
    database_url: Optional[str] = None
    
    # Stripe settings
    stripe_secret_key: Optional[str] = None
    stripe_price_starter: Optional[str] = None
    stripe_price_pro: Optional[str] = None
    stripe_price_enterprise: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    
    # Domain settings
    domain: Optional[str] = "http://localhost:3000"
    
    # Development settings
    vite_supabase_url: Optional[str] = None
    vite_supabase_key: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields

settings = Settings() 
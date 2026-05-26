# backend/app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:****@localhost:5432/jira_ai_agent"
    
    # JWT
    jwt_secret_key: str = "your-secret-key-here-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 10080  # 7 days
    
    # OTP    
    otp_code: str = "1234"
    
    # Jira  
    jira_base_url: str = "http://172.21.0.1:8080"
    jira_username: str = "***"
    jira_password: str = "**"
    Cookie: str = "***"
    
    # n8n
    n8n_base_url: str = "http://172.21.0.1:5678/webhook/chat-intelligence"
    n8n_webhook_url: str = "http://172.21.0.1:5678/webhook/chat-intelligence"
    dummy_mode: bool = True
    
    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()



#    from dotenv import load_dotenv
#     import os

#     # This command looks for a file named '.env' and loads the variables into os.environ
#     load_dotenv() 

#     # Now you can access them like this:
#     JIRA_URL = os.getenv("JIRA_URL")
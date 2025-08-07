#!/usr/bin/env python3
"""
Gemini AI Parser for Instagram Data Extraction

This module provides AI-powered parsing capabilities using Google's Gemini AI
to extract structured data from HTML or GraphQL responses when traditional
parsing methods fail or are insufficient.
"""

import os
import json
import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Google Generative AI not installed. Install with: pip install google-generativeai")

from .content_parser import UserProfile, PostMedia, Comment

logger = logging.getLogger(__name__)


@dataclass
class GeminiParseResult:
    """Result of Gemini AI parsing operation"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    confidence: float = 0.0
    parsing_method: str = "gemini_ai"


class GeminiAIParser:
    """
    AI-powered parser using Google's Gemini AI to extract structured data
    from HTML or GraphQL responses when traditional parsing fails.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini AI Parser
        
        Args:
            api_key: Gemini API key. If not provided, will try to load from GEMINI_API_KEY env var
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        self.is_initialized = False
        
        if not self.api_key:
            logger.warning("No Gemini API key found. Set GEMINI_API_KEY environment variable.")
            return
            
        if not GEMINI_AVAILABLE:
            logger.warning("Google Generative AI library not available.")
            return
            
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize the Gemini AI client"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.is_initialized = True
            logger.info("✅ Gemini AI initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini AI: {e}")
            self.is_initialized = False
    
    async def parse_user_profile(self, raw_data: Dict[str, Any], username: str) -> Optional[UserProfile]:
        """
        Parse user profile data using Gemini AI when traditional parsing fails
        
        Args:
            raw_data: Raw data containing HTML, GraphQL responses, etc.
            username: Target username for context
            
        Returns:
            Parsed UserProfile object or None if parsing fails
        """
        if not self.is_initialized:
            logger.warning("Gemini AI not initialized, skipping AI parsing")
            return None
            
        try:
            # Prepare context for Gemini
            context = self._prepare_profile_context(raw_data, username)
            
            # Create prompt for profile extraction
            prompt = self._create_profile_prompt(username, context)
            
            # Get AI response
            response = await self._get_ai_response(prompt)
            
            if not response:
                return None
                
            # Parse the AI response
            profile_data = self._parse_ai_profile_response(response)
            
            if not profile_data:
                return None
                
            # Create UserProfile object
            return self._create_user_profile(profile_data, username)
            
        except Exception as e:
            logger.error(f"❌ Gemini AI profile parsing failed: {e}")
            return None
    
    async def parse_post_data(self, raw_data: Dict[str, Any], post_id: str) -> Optional[PostMedia]:
        """
        Parse post data using Gemini AI when traditional parsing fails
        
        Args:
            raw_data: Raw data containing HTML, GraphQL responses, etc.
            post_id: Target post ID for context
            
        Returns:
            Parsed PostMedia object or None if parsing fails
        """
        if not self.is_initialized:
            logger.warning("Gemini AI not initialized, skipping AI parsing")
            return None
            
        try:
            # Prepare context for Gemini
            context = self._prepare_post_context(raw_data, post_id)
            
            # Create prompt for post extraction
            prompt = self._create_post_prompt(post_id, context)
            
            # Get AI response
            response = await self._get_ai_response(prompt)
            
            if not response:
                return None
                
            # Parse the AI response
            post_data = self._parse_ai_post_response(response)
            
            if not post_data:
                return None
                
            # Create PostMedia object
            return self._create_post_media(post_data, post_id)
            
        except Exception as e:
            logger.error(f"❌ Gemini AI post parsing failed: {e}")
            return None
    
    def _prepare_profile_context(self, raw_data: Dict[str, Any], username: str) -> str:
        """Prepare context data for profile parsing"""
        context_parts = []
        
        # Add HTML content if available
        if 'html_content' in raw_data and raw_data['html_content']:
            html_sample = raw_data['html_content'][:2000]  # Limit size
            context_parts.append(f"HTML Content (sample):\n{html_sample}")
        
        # Add GraphQL data if available
        if 'graphql_data' in raw_data and raw_data['graphql_data']:
            graphql_sample = json.dumps(list(raw_data['graphql_data'].values())[:2], indent=2)[:2000]
            context_parts.append(f"GraphQL Data (sample):\n{graphql_sample}")
        
        # Add script data if available
        if 'script_data' in raw_data and raw_data['script_data']:
            script_sample = json.dumps(raw_data['script_data'], indent=2)[:2000]
            context_parts.append(f"Script Data:\n{script_sample}")
        
        # Add page analysis if available
        if 'page_analysis' in raw_data and raw_data['page_analysis']:
            page_analysis = json.dumps(raw_data['page_analysis'], indent=2)
            context_parts.append(f"Page Analysis:\n{page_analysis}")
        
        return "\n\n".join(context_parts) if context_parts else "No structured data available"
    
    def _prepare_post_context(self, raw_data: Dict[str, Any], post_id: str) -> str:
        """Prepare context data for post parsing"""
        context_parts = []
        
        # Add HTML content if available
        if 'html_content' in raw_data and raw_data['html_content']:
            html_sample = raw_data['html_content'][:2000]  # Limit size
            context_parts.append(f"HTML Content (sample):\n{html_sample}")
        
        # Add GraphQL data if available
        if 'graphql_data' in raw_data and raw_data['graphql_data']:
            graphql_sample = json.dumps(list(raw_data['graphql_data'].values())[:2], indent=2)[:2000]
            context_parts.append(f"GraphQL Data (sample):\n{graphql_sample}")
        
        # Add script data if available
        if 'script_data' in raw_data and raw_data['script_data']:
            script_sample = json.dumps(raw_data['script_data'], indent=2)[:2000]
            context_parts.append(f"Script Data:\n{script_sample}")
        
        return "\n\n".join(context_parts) if context_parts else "No structured data available"
    
    def _create_profile_prompt(self, username: str, context: str) -> str:
        """Create a prompt for profile data extraction"""
        return f"""
You are an expert data extraction assistant. Your task is to extract Instagram user profile information from the provided data.

Target Username: @{username}

Available Data:
{context}

Please extract the following profile information and return it as a valid JSON object:

{{
    "id": "string (user ID, can be username if not found)",
    "username": "string (the Instagram username)",
    "full_name": "string (full name of the user)",
    "biography": "string (user's bio text)",
    "profile_pic_url": "string (URL to profile picture)",
    "profile_pic_url_hd": "string (URL to high-definition profile picture)",
    "is_private": boolean (true if account is private),
    "is_verified": boolean (true if account is verified),
    "is_business_account": boolean (true if business account),
    "followers_count": integer (number of followers),
    "following_count": integer (number of accounts following),
    "posts_count": integer (number of posts),
    "external_url": "string (external website URL if any)"
}}

Important:
- If a field is not found, use null for that field
- Ensure all boolean values are true/false, not strings
- Ensure all count values are integers (e.g., 1000 not "1000")
- If multiple values are found for the same field, use the most likely correct one
- Focus on accuracy over completeness - better to return null than incorrect data
- For followers_count, following_count, posts_count: return actual numbers, not strings

Return only the JSON object, no additional text or explanation.
"""
    
    def _create_post_prompt(self, post_id: str, context: str) -> str:
        """Create a prompt for post data extraction"""
        return f"""
You are an expert data extraction assistant. Your task is to extract Instagram post information from the provided data.

Target Post ID: {post_id}

Available Data:
{context}

Please extract the following post information and return it as a valid JSON object:

{{
    "id": "string (post ID, can be shortcode if not found)",
    "shortcode": "string (post shortcode)",
    "display_url": "string (URL to the main image/video)",
    "thumbnail_src": "string (URL to thumbnail)",
    "is_video": boolean (true if post is a video),
    "caption": "string (post caption text)",
    "taken_at_timestamp": integer (Unix timestamp when post was taken),
    "likes_count": integer (number of likes),
    "comments_count": integer (number of comments),
    "video_url": "string (video URL if is_video is true)",
    "video_view_count": integer (video view count if applicable)
}}

Important:
- If a field is not found, use null for that field
- Ensure all boolean values are true/false, not strings
- Ensure all count values are integers (e.g., 1000 not "1000")
- If multiple values are found for the same field, use the most likely correct one
- Focus on accuracy over completeness - better to return null than incorrect data
- For likes_count, comments_count: return actual numbers, not strings

Return only the JSON object, no additional text or explanation.
"""
    
    async def _get_ai_response(self, prompt: str) -> Optional[str]:
        """Get response from Gemini AI with timeout"""
        try:
            # Add timeout to prevent hanging
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.model.generate_content,
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,  # Low temperature for consistent parsing
                        max_output_tokens=2048,
                    )
                ),
                timeout=30.0  # 30 second timeout
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                logger.warning("Empty response from Gemini AI")
                return None
                
        except asyncio.TimeoutError:
            logger.error("❌ Gemini AI request timed out after 30 seconds")
            return None
        except Exception as e:
            logger.error(f"❌ Gemini AI request failed: {e}")
            return None
    
    def _parse_ai_profile_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse the AI response for profile data"""
        try:
            # Try to extract JSON from the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("No JSON found in AI response")
                return None
                
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            
            # Validate required fields
            if not data.get('username'):
                logger.warning("No username found in AI response")
                return None
                
            # Ensure id field exists
            if not data.get('id'):
                data['id'] = data.get('username', 'unknown')
                
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse AI response as JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Failed to parse AI profile response: {e}")
            return None
    
    def _parse_ai_post_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse the AI response for post data"""
        try:
            # Try to extract JSON from the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("No JSON found in AI response")
                return None
                
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            
            # Validate required fields - be more lenient for posts
            if not data.get('shortcode') and not data.get('display_url'):
                logger.warning("No shortcode or display_url found in AI response")
                logger.debug(f"Available fields in AI response: {list(data.keys())}")
                # Try to create a minimal post with available data
                if data.get('id') or data.get('caption'):
                    logger.info("Creating minimal post with available data")
                    return data
                return None
                
            # Ensure id field exists
            if not data.get('id'):
                data['id'] = data.get('shortcode', 'unknown')
                
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse AI response as JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Failed to parse AI post response: {e}")
            return None
    
    def _create_user_profile(self, data: Dict[str, Any], username: str) -> UserProfile:
        """Create UserProfile object from parsed data"""
        # Convert string numbers to integers, handle None values
        def safe_int(value, default=0):
            if value is None:
                return default
            try:
                return int(value) if isinstance(value, (int, str)) else default
            except (ValueError, TypeError):
                return default
        
        return UserProfile(
            id=data.get('id', f'ai_parsed_{username}'),
            username=data.get('username', username),
            full_name=data.get('full_name', ''),
            biography=data.get('biography', ''),
            profile_pic_url=data.get('profile_pic_url', ''),
            profile_pic_url_hd=data.get('profile_pic_url_hd', ''),
            is_private=data.get('is_private', False),
            is_verified=data.get('is_verified', False),
            is_business_account=data.get('is_business_account', False),
            followers_count=safe_int(data.get('followers_count')),
            following_count=safe_int(data.get('following_count')),
            posts_count=safe_int(data.get('posts_count')),
            external_url=data.get('external_url')
        )
    
    def _create_post_media(self, data: Dict[str, Any], post_id: str) -> PostMedia:
        """Create PostMedia object from parsed data"""
        # Convert string numbers to integers, handle None values
        def safe_int(value, default=0):
            if value is None:
                return default
            try:
                return int(value) if isinstance(value, (int, str)) else default
            except (ValueError, TypeError):
                return default
        
        return PostMedia(
            id=data.get('id', f'ai_parsed_{post_id}'),
            shortcode=data.get('shortcode', post_id),
            display_url=data.get('display_url', ''),
            thumbnail_src=data.get('thumbnail_src', ''),
            is_video=data.get('is_video', False),
            caption=data.get('caption', ''),
            taken_at_timestamp=safe_int(data.get('taken_at_timestamp'), int(time.time())),
            likes_count=safe_int(data.get('likes_count')),
            comments_count=safe_int(data.get('comments_count')),
            video_url=data.get('video_url'),
            video_view_count=safe_int(data.get('video_view_count')) if data.get('video_view_count') else None
        )
    
    def is_available(self) -> bool:
        """Check if Gemini AI is available and properly configured"""
        return self.is_initialized and self.api_key is not None


# Convenience function for quick parsing
async def parse_with_gemini(raw_data: Dict[str, Any], target_id: str, data_type: str = "profile") -> Optional[Union[UserProfile, PostMedia]]:
    """
    Convenience function to parse data using Gemini AI
    
    Args:
        raw_data: Raw data to parse
        target_id: Username or post ID
        data_type: "profile" or "post"
        
    Returns:
        Parsed UserProfile or PostMedia object, or None if parsing fails
    """
    parser = GeminiAIParser()
    
    if data_type == "profile":
        return await parser.parse_user_profile(raw_data, target_id)
    elif data_type == "post":
        return await parser.parse_post_data(raw_data, target_id)
    else:
        logger.error(f"❌ Unknown data type: {data_type}")
        return None 
"""
AI Service for generating repository summaries and issue explanations using OpenAI
"""
import json
import logging
import time
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

import openai
from openai import OpenAI, RateLimitError, APIError, APIConnectionError
from sqlalchemy.orm import Session
import redis

from app.core.config import settings
from app.models.repository import Repository
from app.models.issue import Issue
from app.schemas.ai import DifficultyLevel, LearningResource


logger = logging.getLogger(__name__)


class AIServiceException(Exception):
    """Base exception for AI service errors"""
    pass


class RateLimitException(AIServiceException):
    """Exception raised when rate limit is exceeded"""
    pass


class AIService:
    """Service for AI-powered content generation"""
    
    def __init__(self, db: Session, redis_client: Optional[redis.Redis] = None):
        """
        Initialize AI service
        
        Args:
            db: Database session
            redis_client: Redis client for caching (optional)
        """
        self.db = db
        self.redis_client = redis_client
        
        # Initialize OpenAI client
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured")
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Rate limiting configuration
        self.rate_limit_key = "ai_service:rate_limit"
        self.max_requests_per_minute = 20
        self.cache_ttl_days = 30  # Cache AI responses for 30 days
    
    def _check_rate_limit(self) -> bool:
        """
        Check if rate limit is exceeded
        
        Returns:
            True if request is allowed, False otherwise
        """
        if not self.redis_client:
            return True
        
        try:
            current_count = self.redis_client.get(self.rate_limit_key)
            if current_count and int(current_count) >= self.max_requests_per_minute:
                return False
            
            # Increment counter
            pipe = self.redis_client.pipeline()
            pipe.incr(self.rate_limit_key)
            pipe.expire(self.rate_limit_key, 60)  # Reset after 1 minute
            pipe.execute()
            
            return True
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True  # Allow request if Redis fails
    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """
        Get cached AI response
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached response or None
        """
        if not self.redis_client:
            return None
        
        try:
            cached = self.redis_client.get(cache_key)
            if cached:
                logger.info(f"Cache hit for key: {cache_key}")
                return cached.decode('utf-8')
        except Exception as e:
            logger.error(f"Error retrieving from cache: {e}")
        
        return None
    
    def _set_cached_response(self, cache_key: str, response: str) -> None:
        """
        Cache AI response
        
        Args:
            cache_key: Cache key
            response: Response to cache
        """
        if not self.redis_client:
            return
        
        try:
            ttl_seconds = self.cache_ttl_days * 24 * 60 * 60
            self.redis_client.setex(cache_key, ttl_seconds, response)
            logger.info(f"Cached response for key: {cache_key}")
        except Exception as e:
            logger.error(f"Error caching response: {e}")
    
    def _call_openai(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """
        Call OpenAI API with error handling and retries
        
        Args:
            messages: List of message dictionaries
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            Generated text
            
        Raises:
            AIServiceException: If API call fails
            RateLimitException: If rate limit is exceeded
        """
        if not self.client:
            raise AIServiceException("OpenAI client not initialized. Check API key configuration.")
        
        # Check rate limit
        if not self._check_rate_limit():
            raise RateLimitException("Rate limit exceeded. Please try again later.")
        
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                return response.choices[0].message.content.strip()
            
            except RateLimitError as e:
                logger.warning(f"OpenAI rate limit hit: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    raise RateLimitException("OpenAI rate limit exceeded")
            
            except APIConnectionError as e:
                logger.error(f"OpenAI connection error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    raise AIServiceException(f"Failed to connect to OpenAI: {str(e)}")
            
            except APIError as e:
                logger.error(f"OpenAI API error: {e}")
                raise AIServiceException(f"OpenAI API error: {str(e)}")
            
            except Exception as e:
                logger.error(f"Unexpected error calling OpenAI: {e}")
                raise AIServiceException(f"Unexpected error: {str(e)}")
        
        raise AIServiceException("Max retries exceeded")
    
    def generate_repository_summary(
        self,
        repository_id: int,
        force_regenerate: bool = False
    ) -> str:
        """
        Generate AI-powered repository summary
        
        Args:
            repository_id: Repository ID
            force_regenerate: Force regeneration even if cached
            
        Returns:
            Repository summary text
            
        Raises:
            AIServiceException: If generation fails
        """
        # Get repository from database
        repo = self.db.query(Repository).filter(Repository.id == repository_id).first()
        if not repo:
            raise AIServiceException(f"Repository {repository_id} not found")
        
        # Check cache first
        cache_key = f"ai:repo_summary:{repository_id}"
        if not force_regenerate:
            cached = self._get_cached_response(cache_key)
            if cached:
                return cached
        
        # Build prompt
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that explains open source projects to beginners. "
                    "Create clear, concise summaries that help new developers understand what the project does, "
                    "what technologies it uses, and why it might be interesting to contribute to."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Please provide a beginner-friendly summary of this repository:\n\n"
                    f"Repository: {repo.full_name}\n"
                    f"Description: {repo.description or 'No description available'}\n"
                    f"Primary Language: {repo.primary_language or 'Unknown'}\n"
                    f"Topics: {', '.join(repo.topics) if repo.topics else 'None'}\n"
                    f"Stars: {repo.stars}\n\n"
                    f"Include:\n"
                    f"1. What the project does (2-3 sentences)\n"
                    f"2. Key technologies used\n"
                    f"3. Why it's interesting for new contributors\n\n"
                    f"Keep it under 200 words and beginner-friendly."
                )
            }
        ]
        
        # Generate summary
        try:
            summary = self._call_openai(messages, max_tokens=500, temperature=0.7)
            
            # Cache the result
            self._set_cached_response(cache_key, summary)
            
            # Update database
            repo.ai_summary = summary
            self.db.commit()
            
            logger.info(f"Generated summary for repository {repository_id}")
            return summary
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error generating repository summary: {e}")
            raise
    
    def explain_issue(
        self,
        issue_id: int,
        force_regenerate: bool = False
    ) -> str:
        """
        Generate AI-powered issue explanation
        
        Args:
            issue_id: Issue ID
            force_regenerate: Force regeneration even if cached
            
        Returns:
            Issue explanation text
            
        Raises:
            AIServiceException: If generation fails
        """
        # Get issue and repository from database
        issue = self.db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            raise AIServiceException(f"Issue {issue_id} not found")
        
        repo = self.db.query(Repository).filter(Repository.id == issue.repository_id).first()
        if not repo:
            raise AIServiceException(f"Repository {issue.repository_id} not found")
        
        # Check cache first
        cache_key = f"ai:issue_explanation:{issue_id}"
        if not force_regenerate:
            cached = self._get_cached_response(cache_key)
            if cached:
                return cached
        
        # Build prompt with repository context
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that explains GitHub issues to beginners. "
                    "Break down what needs to be done in simple terms, explain any technical concepts, "
                    "and provide guidance on how to approach the task."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Please explain this GitHub issue to a beginner developer:\n\n"
                    f"Repository: {repo.full_name}\n"
                    f"Repository Description: {repo.description or 'No description'}\n"
                    f"Primary Language: {repo.primary_language or 'Unknown'}\n\n"
                    f"Issue Title: {issue.title}\n"
                    f"Issue Description: {issue.description or 'No description provided'}\n"
                    f"Labels: {', '.join(issue.labels) if issue.labels else 'None'}\n\n"
                    f"Please provide:\n"
                    f"1. What needs to be done (in simple terms)\n"
                    f"2. Key concepts or technologies involved\n"
                    f"3. Suggested approach or steps to solve it\n"
                    f"4. Any prerequisites or things to learn first\n\n"
                    f"Keep it beginner-friendly and under 300 words."
                )
            }
        ]
        
        # Generate explanation
        try:
            explanation = self._call_openai(messages, max_tokens=800, temperature=0.7)
            
            # Cache the result
            self._set_cached_response(cache_key, explanation)
            
            # Update database
            issue.ai_explanation = explanation
            self.db.commit()
            
            logger.info(f"Generated explanation for issue {issue_id}")
            return explanation
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error generating issue explanation: {e}")
            raise
    
    def analyze_difficulty(self, issue_id: int) -> DifficultyLevel:
        """
        Analyze issue difficulty level using AI
        
        Args:
            issue_id: Issue ID
            
        Returns:
            Difficulty level
            
        Raises:
            AIServiceException: If analysis fails
        """
        # Get issue from database
        issue = self.db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            raise AIServiceException(f"Issue {issue_id} not found")
        
        # Check cache first
        cache_key = f"ai:issue_difficulty:{issue_id}"
        cached = self._get_cached_response(cache_key)
        if cached:
            try:
                return DifficultyLevel(cached)
            except ValueError:
                pass  # Invalid cached value, regenerate
        
        # Build prompt
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert at assessing the difficulty of GitHub issues for beginners. "
                    "Analyze the issue and respond with ONLY one word: easy, medium, or hard."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Assess the difficulty of this issue for a beginner developer:\n\n"
                    f"Title: {issue.title}\n"
                    f"Description: {issue.description or 'No description'}\n"
                    f"Labels: {', '.join(issue.labels) if issue.labels else 'None'}\n"
                    f"Language: {issue.programming_language or 'Unknown'}\n\n"
                    f"Consider:\n"
                    f"- Technical complexity\n"
                    f"- Required knowledge\n"
                    f"- Scope of changes needed\n\n"
                    f"Respond with ONLY: easy, medium, or hard"
                )
            }
        ]
        
        # Analyze difficulty
        try:
            response = self._call_openai(messages, max_tokens=10, temperature=0.3)
            difficulty_str = response.lower().strip()
            
            # Map response to enum
            difficulty_map = {
                "easy": DifficultyLevel.EASY,
                "medium": DifficultyLevel.MEDIUM,
                "hard": DifficultyLevel.HARD
            }
            
            difficulty = difficulty_map.get(difficulty_str, DifficultyLevel.UNKNOWN)
            
            # Cache the result
            self._set_cached_response(cache_key, difficulty.value)
            
            # Update database
            issue.difficulty_level = difficulty.value
            self.db.commit()
            
            logger.info(f"Analyzed difficulty for issue {issue_id}: {difficulty.value}")
            return difficulty
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error analyzing issue difficulty: {e}")
            raise
    
    def suggest_learning_resources(self, issue_id: int) -> List[LearningResource]:
        """
        Suggest learning resources for an issue
        
        Args:
            issue_id: Issue ID
            
        Returns:
            List of learning resources
            
        Raises:
            AIServiceException: If suggestion fails
        """
        # Get issue from database
        issue = self.db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            raise AIServiceException(f"Issue {issue_id} not found")
        
        # Check cache first
        cache_key = f"ai:issue_resources:{issue_id}"
        cached = self._get_cached_response(cache_key)
        if cached:
            try:
                resources_data = json.loads(cached)
                return [LearningResource(**r) for r in resources_data]
            except (json.JSONDecodeError, ValueError):
                pass  # Invalid cached value, regenerate
        
        # Build prompt
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that suggests learning resources for developers. "
                    "Provide 3-5 relevant resources in JSON format."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Suggest learning resources for someone working on this issue:\n\n"
                    f"Title: {issue.title}\n"
                    f"Description: {issue.description or 'No description'}\n"
                    f"Language: {issue.programming_language or 'Unknown'}\n"
                    f"Labels: {', '.join(issue.labels) if issue.labels else 'None'}\n\n"
                    f"Provide 3-5 resources in this JSON format:\n"
                    f'{{"resources": [{{"title": "...", "url": "...", "type": "documentation|tutorial|video", "description": "..."}}]}}\n\n'
                    f"Focus on official documentation, tutorials, and beginner-friendly resources."
                )
            }
        ]
        
        # Generate suggestions
        try:
            response = self._call_openai(messages, max_tokens=800, temperature=0.7)
            
            # Parse JSON response
            try:
                data = json.loads(response)
                resources_data = data.get("resources", [])
                resources = [LearningResource(**r) for r in resources_data]
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse learning resources JSON: {e}")
                resources = []
            
            # Cache the result
            if resources:
                self._set_cached_response(cache_key, json.dumps([r.dict() for r in resources]))
            
            logger.info(f"Generated {len(resources)} learning resources for issue {issue_id}")
            return resources
        
        except Exception as e:
            logger.error(f"Error suggesting learning resources: {e}")
            raise

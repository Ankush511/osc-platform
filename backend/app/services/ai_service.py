"""
AI Service for generating repository summaries and issue explanations
using AWS Bedrock with Claude.
"""
import json
import logging
import time
from typing import Optional, List, Dict, Any

import boto3
from botocore.exceptions import ClientError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.repository import Repository
from app.models.issue import Issue
from app.schemas.ai import DifficultyLevel, LearningResource
from app.services.cache_service import cache_service


logger = logging.getLogger(__name__)


class AIServiceException(Exception):
    """Base exception for AI service errors"""
    pass


class RateLimitException(AIServiceException):
    """Exception raised when rate limit is exceeded"""
    pass


class AIService:
    """Service for AI-powered content generation using AWS Bedrock Claude"""

    def __init__(self, db: Session):
        self.db = db
        self.client = None
        self.model_id = settings.BEDROCK_MODEL_ID

        # Initialize Bedrock client
        try:
            session_kwargs = {"region_name": settings.AWS_REGION}
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                session_kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
                session_kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY

            session = boto3.Session(**session_kwargs)
            self.client = session.client("bedrock-runtime")
            logger.info(f"Bedrock client initialized (region={settings.AWS_REGION}, model={self.model_id})")
        except Exception as e:
            logger.warning(f"Failed to initialize Bedrock client: {e}")

        # Rate limiting
        self.rate_limit_key = "ai_service:rate_limit"
        self.max_requests_per_minute = 20
        self.cache_ttl_seconds = 30 * 24 * 60 * 60  # 30 days

    def _check_rate_limit(self) -> bool:
        try:
            current_count = cache_service.get(self.rate_limit_key)
            if current_count and int(current_count) >= self.max_requests_per_minute:
                return False
            cache_service.increment(self.rate_limit_key)
            if current_count is None:
                cache_service.set(self.rate_limit_key, 1, 60)
            return True
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True

    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        cached = cache_service.get(cache_key)
        if cached:
            logger.info(f"Cache hit for key: {cache_key}")
            return cached
        return None

    def _set_cached_response(self, cache_key: str, response: str) -> None:
        cache_service.set(cache_key, response, self.cache_ttl_seconds)
        logger.info(f"Cached response for key: {cache_key}")

    def _call_bedrock(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> str:
        """
        Call AWS Bedrock Claude via the Converse API.

        Args:
            messages: List of {"role": ..., "content": ...} dicts.
                      The first message with role "system" is extracted
                      and passed as the system prompt.
            max_tokens: Maximum tokens in response.
            temperature: Sampling temperature.

        Returns:
            Generated text.
        """
        if not self.client:
            raise AIServiceException(
                "Bedrock client not initialized. "
                "Check AWS credentials / region configuration."
            )

        if not self._check_rate_limit():
            raise RateLimitException("Rate limit exceeded. Please try again later.")

        # Separate system prompt from conversation messages
        system_prompt = None
        converse_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                converse_messages.append({
                    "role": msg["role"],
                    "content": [{"text": msg["content"]}],
                })

        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                kwargs = {
                    "modelId": self.model_id,
                    "messages": converse_messages,
                    "inferenceConfig": {
                        "maxTokens": max_tokens,
                        "temperature": temperature,
                    },
                }
                if system_prompt:
                    kwargs["system"] = [{"text": system_prompt}]

                response = self.client.converse(**kwargs)

                # Extract text from response
                output_message = response["output"]["message"]
                result_parts = []
                for block in output_message["content"]:
                    if "text" in block:
                        result_parts.append(block["text"])
                return "\n".join(result_parts).strip()

            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code == "ThrottlingException":
                    logger.warning(f"Bedrock throttled (attempt {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))
                    else:
                        raise RateLimitException("Bedrock rate limit exceeded")
                elif error_code in ("ModelTimeoutException", "ServiceUnavailableException"):
                    logger.error(f"Bedrock transient error (attempt {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))
                    else:
                        raise AIServiceException(f"Bedrock unavailable: {str(e)}")
                else:
                    raise AIServiceException(f"Bedrock API error: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error calling Bedrock: {e}")
                raise AIServiceException(f"Unexpected error: {str(e)}")

        raise AIServiceException("Max retries exceeded")

    def generate_repository_summary(
        self, repository_id: int, force_regenerate: bool = False
    ) -> str:
        repo = self.db.query(Repository).filter(Repository.id == repository_id).first()
        if not repo:
            raise AIServiceException(f"Repository {repository_id} not found")

        cache_key = f"ai:repo_summary:{repository_id}"
        if not force_regenerate:
            cached = self._get_cached_response(cache_key)
            if cached:
                return cached

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that explains open source projects to beginners. "
                    "Create clear, concise summaries that help new developers understand what the project does, "
                    "what technologies it uses, and why it might be interesting to contribute to."
                ),
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
                ),
            },
        ]

        try:
            summary = self._call_bedrock(messages, max_tokens=500, temperature=0.7)
            self._set_cached_response(cache_key, summary)
            repo.ai_summary = summary
            self.db.commit()
            logger.info(f"Generated summary for repository {repository_id}")
            return summary
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error generating repository summary: {e}")
            raise

    def explain_issue(self, issue_id: int, force_regenerate: bool = False) -> str:
        issue = self.db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            raise AIServiceException(f"Issue {issue_id} not found")

        repo = self.db.query(Repository).filter(Repository.id == issue.repository_id).first()
        if not repo:
            raise AIServiceException(f"Repository {issue.repository_id} not found")

        cache_key = f"ai:issue_explanation:{issue_id}"
        if not force_regenerate:
            cached = self._get_cached_response(cache_key)
            if cached:
                return cached

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that explains GitHub issues to beginners. "
                    "Break down what needs to be done in simple terms, explain any technical concepts, "
                    "and provide guidance on how to approach the task."
                ),
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
                ),
            },
        ]

        try:
            explanation = self._call_bedrock(messages, max_tokens=800, temperature=0.7)
            self._set_cached_response(cache_key, explanation)
            issue.ai_explanation = explanation
            self.db.commit()
            logger.info(f"Generated explanation for issue {issue_id}")
            return explanation
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error generating issue explanation: {e}")
            raise

    def analyze_difficulty(self, issue_id: int) -> DifficultyLevel:
        issue = self.db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            raise AIServiceException(f"Issue {issue_id} not found")

        cache_key = f"ai:issue_difficulty:{issue_id}"
        cached = self._get_cached_response(cache_key)
        if cached:
            try:
                return DifficultyLevel(cached)
            except ValueError:
                pass

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert at assessing the difficulty of GitHub issues for beginner "
                    "open-source contributors — typically computer science students with about 1 year "
                    "of coding experience who have never contributed to open source before. "
                    "Consider the scope of changes required, the number of files likely involved, "
                    "how much domain knowledge is needed, and whether the issue is well-scoped. "
                    "Respond with ONLY one word: easy, medium, or hard."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Assess the difficulty of this issue for a beginner open-source contributor:\n\n"
                    f"Title: {issue.title}\n"
                    f"Description: {issue.description or 'No description'}\n"
                    f"Labels: {', '.join(issue.labels) if issue.labels else 'None'}\n"
                    f"Language: {issue.programming_language or 'Unknown'}\n\n"
                    f"Respond with ONLY: easy, medium, or hard"
                ),
            },
        ]

        try:
            response = self._call_bedrock(messages, max_tokens=10, temperature=0.3)
            difficulty_str = response.lower().strip()
            difficulty_map = {
                "easy": DifficultyLevel.EASY,
                "medium": DifficultyLevel.MEDIUM,
                "hard": DifficultyLevel.HARD,
            }
            difficulty = difficulty_map.get(difficulty_str, DifficultyLevel.UNKNOWN)
            self._set_cached_response(cache_key, difficulty.value)
            issue.difficulty_level = difficulty.value
            self.db.commit()
            logger.info(f"Analyzed difficulty for issue {issue_id}: {difficulty.value}")
            return difficulty
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error analyzing issue difficulty: {e}")
            raise

    def suggest_learning_resources(self, issue_id: int) -> List[LearningResource]:
        issue = self.db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            raise AIServiceException(f"Issue {issue_id} not found")

        cache_key = f"ai:issue_resources:{issue_id}"
        cached = self._get_cached_response(cache_key)
        if cached:
            try:
                resources_data = json.loads(cached)
                return [LearningResource(**r) for r in resources_data]
            except (json.JSONDecodeError, ValueError):
                pass

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that suggests learning resources for developers. "
                    "Provide 3-5 relevant resources in JSON format."
                ),
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
                ),
            },
        ]

        try:
            response = self._call_bedrock(messages, max_tokens=800, temperature=0.7)
            try:
                data = json.loads(response)
                resources_data = data.get("resources", [])
                resources = [LearningResource(**r) for r in resources_data]
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse learning resources JSON: {e}")
                resources = []

            if resources:
                self._set_cached_response(cache_key, json.dumps([r.dict() for r in resources]))

            logger.info(f"Generated {len(resources)} learning resources for issue {issue_id}")
            return resources
        except Exception as e:
            logger.error(f"Error suggesting learning resources: {e}")
            raise

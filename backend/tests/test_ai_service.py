"""
Tests for AI service functionality
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.services.ai_service import AIService, AIServiceException, RateLimitException
from app.models.repository import Repository
from app.models.issue import Issue, IssueStatus
from app.schemas.ai import DifficultyLevel, LearningResource


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    redis_mock = Mock()
    redis_mock.get.return_value = None
    redis_mock.setex.return_value = True
    redis_mock.incr.return_value = 1
    redis_mock.expire.return_value = True
    redis_mock.pipeline.return_value = redis_mock
    redis_mock.execute.return_value = [1, True]
    return redis_mock


@pytest.fixture
def sample_repository(db_session):
    """Create a sample repository"""
    repo = Repository(
        github_repo_id=12345,
        full_name="test-org/test-repo",
        name="test-repo",
        description="A test repository for unit testing",
        primary_language="Python",
        topics=["testing", "python", "open-source"],
        stars=100,
        forks=20,
        is_active=True
    )
    db_session.add(repo)
    db_session.commit()
    db_session.refresh(repo)
    return repo


@pytest.fixture
def sample_issue(db_session, sample_repository):
    """Create a sample issue"""
    issue = Issue(
        github_issue_id=67890,
        repository_id=sample_repository.id,
        title="Add unit tests for authentication module",
        description="We need comprehensive unit tests for the authentication module to improve code coverage.",
        labels=["good first issue", "testing", "help wanted"],
        programming_language="Python",
        status=IssueStatus.AVAILABLE,
        github_url="https://github.com/test-org/test-repo/issues/1"
    )
    db_session.add(issue)
    db_session.commit()
    db_session.refresh(issue)
    return issue


@pytest.fixture
def ai_service(db_session, mock_redis):
    """Create AI service instance with mocked dependencies"""
    with patch('app.services.ai_service.settings') as mock_settings:
        mock_settings.OPENAI_API_KEY = "test-api-key"
        service = AIService(db=db_session, redis_client=mock_redis)
        return service


class TestAIServiceInitialization:
    """Test AI service initialization"""
    
    def test_init_with_api_key(self, db_session, mock_redis):
        """Test initialization with valid API key"""
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-api-key"
            service = AIService(db=db_session, redis_client=mock_redis)
            assert service.client is not None
            assert service.db == db_session
            assert service.redis_client == mock_redis
    
    def test_init_without_api_key(self, db_session, mock_redis):
        """Test initialization without API key"""
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = ""
            service = AIService(db=db_session, redis_client=mock_redis)
            assert service.client is None
    
    def test_init_without_redis(self, db_session):
        """Test initialization without Redis"""
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-api-key"
            service = AIService(db=db_session, redis_client=None)
            assert service.redis_client is None


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limit_check_allowed(self, ai_service, mock_redis):
        """Test rate limit check when requests are allowed"""
        mock_redis.get.return_value = b"5"
        assert ai_service._check_rate_limit() is True
        mock_redis.incr.assert_called_once()
    
    def test_rate_limit_check_exceeded(self, ai_service, mock_redis):
        """Test rate limit check when limit is exceeded"""
        mock_redis.get.return_value = b"20"
        assert ai_service._check_rate_limit() is False
        mock_redis.incr.assert_not_called()
    
    def test_rate_limit_without_redis(self, db_session):
        """Test rate limit check without Redis (should always allow)"""
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-api-key"
            service = AIService(db=db_session, redis_client=None)
            assert service._check_rate_limit() is True
    
    def test_rate_limit_redis_error(self, ai_service, mock_redis):
        """Test rate limit check when Redis fails"""
        mock_redis.get.side_effect = Exception("Redis connection error")
        assert ai_service._check_rate_limit() is True  # Should allow on error


class TestCaching:
    """Test caching functionality"""
    
    def test_get_cached_response_hit(self, ai_service, mock_redis):
        """Test cache hit"""
        mock_redis.get.return_value = b"Cached response"
        result = ai_service._get_cached_response("test_key")
        assert result == "Cached response"
        mock_redis.get.assert_called_once_with("test_key")
    
    def test_get_cached_response_miss(self, ai_service, mock_redis):
        """Test cache miss"""
        mock_redis.get.return_value = None
        result = ai_service._get_cached_response("test_key")
        assert result is None
    
    def test_set_cached_response(self, ai_service, mock_redis):
        """Test setting cached response"""
        ai_service._set_cached_response("test_key", "Test response")
        mock_redis.setex.assert_called_once()
        args = mock_redis.setex.call_args[0]
        assert args[0] == "test_key"
        assert args[2] == "Test response"
    
    def test_cache_without_redis(self, db_session):
        """Test caching without Redis"""
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-api-key"
            service = AIService(db=db_session, redis_client=None)
            result = service._get_cached_response("test_key")
            assert result is None
            service._set_cached_response("test_key", "value")  # Should not raise


class TestRepositorySummaryGeneration:
    """Test repository summary generation"""
    
    def test_generate_summary_success(self, ai_service, sample_repository, mock_redis):
        """Test successful repository summary generation"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is a test repository for Python development."
        
        with patch.object(ai_service.client.chat.completions, 'create', return_value=mock_response):
            summary = ai_service.generate_repository_summary(sample_repository.id)
            
            assert summary == "This is a test repository for Python development."
            assert sample_repository.ai_summary == summary
            mock_redis.setex.assert_called_once()
    
    def test_generate_summary_from_cache(self, ai_service, sample_repository, mock_redis):
        """Test repository summary retrieval from cache"""
        cached_summary = "Cached repository summary"
        mock_redis.get.return_value = cached_summary.encode('utf-8')
        
        summary = ai_service.generate_repository_summary(sample_repository.id)
        
        assert summary == cached_summary
        # Should not call OpenAI if cached
        assert not hasattr(ai_service.client.chat.completions, 'create') or \
               not ai_service.client.chat.completions.create.called
    
    def test_generate_summary_force_regenerate(self, ai_service, sample_repository, mock_redis):
        """Test forced regeneration of repository summary"""
        mock_redis.get.return_value = b"Old cached summary"
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "New generated summary"
        
        with patch.object(ai_service.client.chat.completions, 'create', return_value=mock_response):
            summary = ai_service.generate_repository_summary(
                sample_repository.id,
                force_regenerate=True
            )
            
            assert summary == "New generated summary"
    
    def test_generate_summary_repository_not_found(self, ai_service):
        """Test summary generation for non-existent repository"""
        with pytest.raises(AIServiceException, match="Repository .* not found"):
            ai_service.generate_repository_summary(99999)
    
    def test_generate_summary_no_api_key(self, db_session, sample_repository, mock_redis):
        """Test summary generation without API key"""
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = ""
            service = AIService(db=db_session, redis_client=mock_redis)
            
            with pytest.raises(AIServiceException, match="OpenAI client not initialized"):
                service.generate_repository_summary(sample_repository.id)
    
    def test_generate_summary_rate_limit_exceeded(self, ai_service, sample_repository, mock_redis):
        """Test summary generation when rate limit is exceeded"""
        mock_redis.get.return_value = b"25"  # Exceeds limit
        
        with pytest.raises(RateLimitException, match="Rate limit exceeded"):
            ai_service.generate_repository_summary(sample_repository.id)


class TestIssueExplanationGeneration:
    """Test issue explanation generation"""
    
    def test_explain_issue_success(self, ai_service, sample_issue, mock_redis):
        """Test successful issue explanation generation"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This issue requires adding unit tests for authentication."
        
        with patch.object(ai_service.client.chat.completions, 'create', return_value=mock_response):
            explanation = ai_service.explain_issue(sample_issue.id)
            
            assert explanation == "This issue requires adding unit tests for authentication."
            assert sample_issue.ai_explanation == explanation
            mock_redis.setex.assert_called_once()
    
    def test_explain_issue_from_cache(self, ai_service, sample_issue, mock_redis):
        """Test issue explanation retrieval from cache"""
        cached_explanation = "Cached issue explanation"
        mock_redis.get.return_value = cached_explanation.encode('utf-8')
        
        explanation = ai_service.explain_issue(sample_issue.id)
        
        assert explanation == cached_explanation
    
    def test_explain_issue_not_found(self, ai_service):
        """Test explanation generation for non-existent issue"""
        with pytest.raises(AIServiceException, match="Issue .* not found"):
            ai_service.explain_issue(99999)
    
    def test_explain_issue_force_regenerate(self, ai_service, sample_issue, mock_redis):
        """Test forced regeneration of issue explanation"""
        mock_redis.get.return_value = b"Old cached explanation"
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "New generated explanation"
        
        with patch.object(ai_service.client.chat.completions, 'create', return_value=mock_response):
            explanation = ai_service.explain_issue(sample_issue.id, force_regenerate=True)
            
            assert explanation == "New generated explanation"


class TestDifficultyAnalysis:
    """Test difficulty analysis"""
    
    def test_analyze_difficulty_easy(self, ai_service, sample_issue, mock_redis):
        """Test difficulty analysis returning easy"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "easy"
        
        with patch.object(ai_service.client.chat.completions, 'create', return_value=mock_response):
            difficulty = ai_service.analyze_difficulty(sample_issue.id)
            
            assert difficulty == DifficultyLevel.EASY
            assert sample_issue.difficulty_level == "easy"
    
    def test_analyze_difficulty_medium(self, ai_service, sample_issue, mock_redis):
        """Test difficulty analysis returning medium"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "medium"
        
        with patch.object(ai_service.client.chat.completions, 'create', return_value=mock_response):
            difficulty = ai_service.analyze_difficulty(sample_issue.id)
            
            assert difficulty == DifficultyLevel.MEDIUM
    
    def test_analyze_difficulty_hard(self, ai_service, sample_issue, mock_redis):
        """Test difficulty analysis returning hard"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "hard"
        
        with patch.object(ai_service.client.chat.completions, 'create', return_value=mock_response):
            difficulty = ai_service.analyze_difficulty(sample_issue.id)
            
            assert difficulty == DifficultyLevel.HARD
    
    def test_analyze_difficulty_unknown(self, ai_service, sample_issue, mock_redis):
        """Test difficulty analysis with invalid response"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "invalid"
        
        with patch.object(ai_service.client.chat.completions, 'create', return_value=mock_response):
            difficulty = ai_service.analyze_difficulty(sample_issue.id)
            
            assert difficulty == DifficultyLevel.UNKNOWN
    
    def test_analyze_difficulty_from_cache(self, ai_service, sample_issue, mock_redis):
        """Test difficulty analysis retrieval from cache"""
        mock_redis.get.return_value = b"medium"
        
        difficulty = ai_service.analyze_difficulty(sample_issue.id)
        
        assert difficulty == DifficultyLevel.MEDIUM
    
    def test_analyze_difficulty_issue_not_found(self, ai_service):
        """Test difficulty analysis for non-existent issue"""
        with pytest.raises(AIServiceException, match="Issue .* not found"):
            ai_service.analyze_difficulty(99999)


class TestLearningResourceSuggestions:
    """Test learning resource suggestions"""
    
    def test_suggest_resources_success(self, ai_service, sample_issue, mock_redis):
        """Test successful learning resource suggestions"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        resources_json = {
            "resources": [
                {
                    "title": "Python Testing Guide",
                    "url": "https://docs.python.org/3/library/unittest.html",
                    "type": "documentation",
                    "description": "Official Python unittest documentation"
                },
                {
                    "title": "Pytest Tutorial",
                    "url": "https://pytest.org/",
                    "type": "tutorial",
                    "description": "Getting started with pytest"
                }
            ]
        }
        mock_response.choices[0].message.content = json.dumps(resources_json)
        
        with patch.object(ai_service.client.chat.completions, 'create', return_value=mock_response):
            resources = ai_service.suggest_learning_resources(sample_issue.id)
            
            assert len(resources) == 2
            assert resources[0].title == "Python Testing Guide"
            assert resources[0].type == "documentation"
            assert resources[1].title == "Pytest Tutorial"
            mock_redis.setex.assert_called_once()
    
    def test_suggest_resources_from_cache(self, ai_service, sample_issue, mock_redis):
        """Test learning resource retrieval from cache"""
        cached_resources = [
            {
                "title": "Cached Resource",
                "url": "https://example.com",
                "type": "tutorial",
                "description": "A cached resource"
            }
        ]
        mock_redis.get.return_value = json.dumps(cached_resources).encode('utf-8')
        
        resources = ai_service.suggest_learning_resources(sample_issue.id)
        
        assert len(resources) == 1
        assert resources[0].title == "Cached Resource"
    
    def test_suggest_resources_invalid_json(self, ai_service, sample_issue, mock_redis):
        """Test resource suggestions with invalid JSON response"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Invalid JSON"
        
        with patch.object(ai_service.client.chat.completions, 'create', return_value=mock_response):
            resources = ai_service.suggest_learning_resources(sample_issue.id)
            
            assert len(resources) == 0
    
    def test_suggest_resources_issue_not_found(self, ai_service):
        """Test resource suggestions for non-existent issue"""
        with pytest.raises(AIServiceException, match="Issue .* not found"):
            ai_service.suggest_learning_resources(99999)


class TestOpenAIErrorHandling:
    """Test OpenAI API error handling"""
    
    def test_api_connection_error_with_retry(self, ai_service, sample_repository, mock_redis):
        """Test handling of API connection errors with retry"""
        from openai import APIConnectionError
        
        mock_error = APIConnectionError("Connection failed")
        
        with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
            # Fail twice, then succeed
            mock_success = Mock()
            mock_success.choices = [Mock()]
            mock_success.choices[0].message.content = "Success after retry"
            
            mock_create.side_effect = [
                mock_error,
                mock_error,
                mock_success
            ]
            
            summary = ai_service.generate_repository_summary(sample_repository.id)
            
            assert summary == "Success after retry"
            assert mock_create.call_count == 3
    
    def test_api_connection_error_max_retries(self, ai_service, sample_repository, mock_redis):
        """Test handling of API connection errors exceeding max retries"""
        from openai import APIConnectionError
        
        mock_error = APIConnectionError("Connection failed")
        
        with patch.object(ai_service.client.chat.completions, 'create', side_effect=mock_error):
            with pytest.raises(AIServiceException, match="Failed to connect to OpenAI"):
                ai_service.generate_repository_summary(sample_repository.id)
    
    def test_rate_limit_error_with_retry(self, ai_service, sample_repository, mock_redis):
        """Test handling of rate limit errors with retry"""
        from openai import RateLimitError
        
        mock_error = RateLimitError("Rate limit exceeded")
        
        with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
            mock_success = Mock()
            mock_success.choices = [Mock()]
            mock_success.choices[0].message.content = "Success after rate limit"
            
            mock_create.side_effect = [mock_error, mock_success]
            
            summary = ai_service.generate_repository_summary(sample_repository.id)
            
            assert summary == "Success after rate limit"
    
    def test_rate_limit_error_max_retries(self, ai_service, sample_repository, mock_redis):
        """Test handling of rate limit errors exceeding max retries"""
        from openai import RateLimitError
        
        mock_error = RateLimitError("Rate limit exceeded")
        
        with patch.object(ai_service.client.chat.completions, 'create', side_effect=mock_error):
            with pytest.raises(RateLimitException, match="OpenAI rate limit exceeded"):
                ai_service.generate_repository_summary(sample_repository.id)
    
    def test_api_error(self, ai_service, sample_repository, mock_redis):
        """Test handling of general API errors"""
        from openai import APIError
        
        mock_error = APIError("API error occurred")
        
        with patch.object(ai_service.client.chat.completions, 'create', side_effect=mock_error):
            with pytest.raises(AIServiceException, match="OpenAI API error"):
                ai_service.generate_repository_summary(sample_repository.id)

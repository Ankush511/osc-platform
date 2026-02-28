"""
Unit tests for AI service core functionality (without database)
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from app.services.ai_service import AIService, AIServiceException, RateLimitException
from app.schemas.ai import DifficultyLevel


class TestAIServiceCoreLogic:
    """Test AI service core logic without database dependencies"""
    
    def test_rate_limit_check_with_redis(self):
        """Test rate limit checking with Redis"""
        mock_redis = Mock()
        mock_redis.get.return_value = b"5"
        mock_redis.incr.return_value = 6
        mock_redis.expire.return_value = True
        mock_redis.pipeline.return_value = mock_redis
        mock_redis.execute.return_value = [6, True]
        
        mock_db = Mock()
        
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            service = AIService(db=mock_db, redis_client=mock_redis)
            
            result = service._check_rate_limit()
            assert result is True
            mock_redis.incr.assert_called_once()
    
    def test_rate_limit_exceeded(self):
        """Test rate limit exceeded scenario"""
        mock_redis = Mock()
        mock_redis.get.return_value = b"25"  # Exceeds limit of 20
        
        mock_db = Mock()
        
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            service = AIService(db=mock_db, redis_client=mock_redis)
            
            result = service._check_rate_limit()
            assert result is False
            mock_redis.incr.assert_not_called()
    
    def test_cache_operations(self):
        """Test cache get and set operations"""
        mock_redis = Mock()
        mock_redis.get.return_value = b"cached_value"
        mock_redis.setex.return_value = True
        
        mock_db = Mock()
        
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            service = AIService(db=mock_db, redis_client=mock_redis)
            
            # Test get
            result = service._get_cached_response("test_key")
            assert result == "cached_value"
            mock_redis.get.assert_called_once_with("test_key")
            
            # Test set
            service._set_cached_response("test_key", "new_value")
            mock_redis.setex.assert_called_once()
            args = mock_redis.setex.call_args[0]
            assert args[0] == "test_key"
            assert args[2] == "new_value"
    
    def test_openai_call_success(self):
        """Test successful OpenAI API call"""
        mock_redis = Mock()
        mock_redis.get.return_value = None
        mock_redis.incr.return_value = 1
        mock_redis.expire.return_value = True
        mock_redis.pipeline.return_value = mock_redis
        mock_redis.execute.return_value = [1, True]
        
        mock_db = Mock()
        
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            service = AIService(db=mock_db, redis_client=mock_redis)
            
            # Mock OpenAI response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test response from AI"
            
            with patch.object(service.client.chat.completions, 'create', return_value=mock_response):
                messages = [{"role": "user", "content": "Test prompt"}]
                result = service._call_openai(messages)
                
                assert result == "Test response from AI"
                service.client.chat.completions.create.assert_called_once()
    
    def test_openai_call_rate_limit_error(self):
        """Test OpenAI rate limit error handling"""
        from openai import RateLimitError
        
        mock_redis = Mock()
        mock_redis.get.return_value = None
        mock_redis.incr.return_value = 1
        mock_redis.expire.return_value = True
        mock_redis.pipeline.return_value = mock_redis
        mock_redis.execute.return_value = [1, True]
        
        mock_db = Mock()
        
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            service = AIService(db=mock_db, redis_client=mock_redis)
            
            # Mock OpenAI rate limit error with proper initialization
            mock_response = Mock()
            mock_response.status_code = 429
            error = RateLimitError("Rate limit", response=mock_response, body={})
            
            with patch.object(service.client.chat.completions, 'create', side_effect=error):
                messages = [{"role": "user", "content": "Test prompt"}]
                
                with pytest.raises(RateLimitException):
                    service._call_openai(messages)
    
    def test_openai_call_with_retry(self):
        """Test OpenAI API call with retry on connection error"""
        from openai import APIConnectionError
        
        mock_redis = Mock()
        mock_redis.get.return_value = None
        mock_redis.incr.return_value = 1
        mock_redis.expire.return_value = True
        mock_redis.pipeline.return_value = mock_redis
        mock_redis.execute.return_value = [1, True]
        
        mock_db = Mock()
        
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            service = AIService(db=mock_db, redis_client=mock_redis)
            
            # Mock OpenAI to fail twice then succeed
            mock_success = Mock()
            mock_success.choices = [Mock()]
            mock_success.choices[0].message.content = "Success after retry"
            
            # Create proper APIConnectionError instances
            error1 = APIConnectionError(request=Mock())
            error2 = APIConnectionError(request=Mock())
            
            with patch.object(service.client.chat.completions, 'create') as mock_create:
                mock_create.side_effect = [
                    error1,
                    error2,
                    mock_success
                ]
                
                messages = [{"role": "user", "content": "Test prompt"}]
                result = service._call_openai(messages)
                
                assert result == "Success after retry"
                assert mock_create.call_count == 3
    
    def test_no_api_key_initialization(self):
        """Test initialization without API key"""
        mock_db = Mock()
        mock_redis = Mock()
        
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = ""
            service = AIService(db=mock_db, redis_client=mock_redis)
            
            assert service.client is None
            
            # Should raise exception when trying to call OpenAI
            with pytest.raises(AIServiceException, match="OpenAI client not initialized"):
                service._call_openai([{"role": "user", "content": "test"}])
    
    def test_cache_without_redis(self):
        """Test caching operations without Redis"""
        mock_db = Mock()
        
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            service = AIService(db=mock_db, redis_client=None)
            
            # Should return None for cache get
            result = service._get_cached_response("test_key")
            assert result is None
            
            # Should not raise error for cache set
            service._set_cached_response("test_key", "value")  # Should not raise
    
    def test_rate_limit_without_redis(self):
        """Test rate limiting without Redis (should always allow)"""
        mock_db = Mock()
        
        with patch('app.services.ai_service.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            service = AIService(db=mock_db, redis_client=None)
            
            # Should always return True without Redis
            result = service._check_rate_limit()
            assert result is True


def test_ai_service_imports():
    """Test that AI service can be imported successfully"""
    from app.services.ai_service import AIService, AIServiceException, RateLimitException
    from app.schemas.ai import DifficultyLevel, LearningResource
    
    assert AIService is not None
    assert AIServiceException is not None
    assert RateLimitException is not None
    assert DifficultyLevel is not None
    assert LearningResource is not None


def test_difficulty_level_enum():
    """Test DifficultyLevel enum values"""
    assert DifficultyLevel.EASY.value == "easy"
    assert DifficultyLevel.MEDIUM.value == "medium"
    assert DifficultyLevel.HARD.value == "hard"
    assert DifficultyLevel.UNKNOWN.value == "unknown"

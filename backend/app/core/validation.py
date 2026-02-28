"""
Input validation and sanitization utilities for security hardening.
"""
import re
from typing import Any, Optional
from urllib.parse import urlparse
import html
import bleach


class InputValidator:
    """Comprehensive input validation and sanitization."""
    
    # Regex patterns for validation
    GITHUB_USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$')
    GITHUB_REPO_PATTERN = re.compile(r'^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$')
    GITHUB_URL_PATTERN = re.compile(r'^https://github\.com/[\w-]+/[\w.-]+/(issues|pull)/\d+$')
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # Allowed HTML tags for user content (very restrictive)
    ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'code', 'pre', 'a']
    ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}
    
    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize string input by removing dangerous characters.
        
        Args:
            value: Input string
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            raise ValueError("Input must be a string")
        
        # Strip whitespace
        value = value.strip()
        
        # Enforce max length
        if max_length and len(value) > max_length:
            raise ValueError(f"Input exceeds maximum length of {max_length}")
        
        # HTML escape to prevent XSS
        value = html.escape(value)
        
        return value
    
    @staticmethod
    def sanitize_html(value: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize HTML content allowing only safe tags.
        
        Args:
            value: HTML string
            max_length: Maximum allowed length
            
        Returns:
            Sanitized HTML string
        """
        if not isinstance(value, str):
            raise ValueError("Input must be a string")
        
        # Enforce max length
        if max_length and len(value) > max_length:
            raise ValueError(f"Input exceeds maximum length of {max_length}")
        
        # Clean HTML with bleach
        cleaned = bleach.clean(
            value,
            tags=InputValidator.ALLOWED_TAGS,
            attributes=InputValidator.ALLOWED_ATTRIBUTES,
            strip=True
        )
        
        return cleaned
    
    @staticmethod
    def validate_github_username(username: str) -> str:
        """
        Validate and sanitize GitHub username.
        
        Args:
            username: GitHub username
            
        Returns:
            Validated username
            
        Raises:
            ValueError: If username is invalid
        """
        username = username.strip()
        
        if not InputValidator.GITHUB_USERNAME_PATTERN.match(username):
            raise ValueError(
                "Invalid GitHub username. Must be 1-39 characters, "
                "alphanumeric or hyphens, cannot start/end with hyphen"
            )
        
        return username
    
    @staticmethod
    def validate_github_repo(repo_name: str) -> str:
        """
        Validate GitHub repository name (owner/repo format).
        
        Args:
            repo_name: Repository name in owner/repo format
            
        Returns:
            Validated repository name
            
        Raises:
            ValueError: If repository name is invalid
        """
        repo_name = repo_name.strip()
        
        if not InputValidator.GITHUB_REPO_PATTERN.match(repo_name):
            raise ValueError(
                "Invalid repository name. Must be in format 'owner/repo'"
            )
        
        return repo_name
    
    @staticmethod
    def validate_github_url(url: str) -> str:
        """
        Validate GitHub issue or PR URL.
        
        Args:
            url: GitHub URL
            
        Returns:
            Validated URL
            
        Raises:
            ValueError: If URL is invalid
        """
        url = url.strip()
        
        if not InputValidator.GITHUB_URL_PATTERN.match(url):
            raise ValueError(
                "Invalid GitHub URL. Must be a valid GitHub issue or PR URL"
            )
        
        return url
    
    @staticmethod
    def validate_email(email: str) -> str:
        """
        Validate email address.
        
        Args:
            email: Email address
            
        Returns:
            Validated email
            
        Raises:
            ValueError: If email is invalid
        """
        email = email.strip().lower()
        
        if not InputValidator.EMAIL_PATTERN.match(email):
            raise ValueError("Invalid email address format")
        
        return email
    
    @staticmethod
    def validate_url(url: str, allowed_schemes: Optional[list] = None) -> str:
        """
        Validate URL and ensure it uses allowed schemes.
        
        Args:
            url: URL to validate
            allowed_schemes: List of allowed schemes (default: ['http', 'https'])
            
        Returns:
            Validated URL
            
        Raises:
            ValueError: If URL is invalid
        """
        if allowed_schemes is None:
            allowed_schemes = ['http', 'https']
        
        url = url.strip()
        
        try:
            parsed = urlparse(url)
            
            if not parsed.scheme:
                raise ValueError("URL must include a scheme (http/https)")
            
            if parsed.scheme not in allowed_schemes:
                raise ValueError(f"URL scheme must be one of: {', '.join(allowed_schemes)}")
            
            if not parsed.netloc:
                raise ValueError("URL must include a domain")
            
            return url
        except Exception as e:
            raise ValueError(f"Invalid URL: {str(e)}")
    
    @staticmethod
    def validate_integer(value: Any, min_value: Optional[int] = None, 
                        max_value: Optional[int] = None) -> int:
        """
        Validate integer input with optional range checking.
        
        Args:
            value: Value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Validated integer
            
        Raises:
            ValueError: If value is invalid
        """
        try:
            int_value = int(value)
        except (TypeError, ValueError):
            raise ValueError("Value must be an integer")
        
        if min_value is not None and int_value < min_value:
            raise ValueError(f"Value must be at least {min_value}")
        
        if max_value is not None and int_value > max_value:
            raise ValueError(f"Value must be at most {max_value}")
        
        return int_value
    
    @staticmethod
    def validate_list(value: Any, item_type: type = str, 
                     max_items: Optional[int] = None) -> list:
        """
        Validate list input.
        
        Args:
            value: Value to validate
            item_type: Expected type of list items
            max_items: Maximum number of items allowed
            
        Returns:
            Validated list
            
        Raises:
            ValueError: If value is invalid
        """
        if not isinstance(value, list):
            raise ValueError("Value must be a list")
        
        if max_items and len(value) > max_items:
            raise ValueError(f"List cannot contain more than {max_items} items")
        
        for item in value:
            if not isinstance(item, item_type):
                raise ValueError(f"All list items must be of type {item_type.__name__}")
        
        return value
    
    @staticmethod
    def sanitize_sql_like_pattern(pattern: str) -> str:
        """
        Sanitize SQL LIKE pattern to prevent injection.
        
        Args:
            pattern: Search pattern
            
        Returns:
            Sanitized pattern
        """
        # Escape special SQL LIKE characters
        pattern = pattern.replace('\\', '\\\\')
        pattern = pattern.replace('%', '\\%')
        pattern = pattern.replace('_', '\\_')
        
        return pattern

"""
LinkedIn Engagement Automation for Enhanced Reach & Followers

Enterprise-grade engagement system that:
- Comments on trending DevOps posts with AI-generated insights
- Engages with influential people's content intelligently
- Sends targeted connection requests to HRs and professionals
- Implements advanced reach enhancement strategies

Author: LinkedIn DevOps Growth System
Date: December 26, 2025
"""

import requests
import os
import sys
import json
import random
import re
import logging
import time
import shutil
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple
import hashlib
import urllib3
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# Production-grade HTTP configuration
REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", "30"))
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))
RETRY_BACKOFF_FACTOR = float(os.environ.get("RETRY_BACKOFF_FACTOR", "2.0"))
RATE_LIMIT_DELAY = int(os.environ.get("RATE_LIMIT_DELAY", "2"))
MAX_REQUESTS_PER_HOUR = int(os.environ.get("MAX_REQUESTS_PER_HOUR", "100"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Production-grade HTTP configuration
REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", "30"))
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))
RETRY_BACKOFF_FACTOR = float(os.environ.get("RETRY_BACKOFF_FACTOR", "2.0"))
RATE_LIMIT_DELAY = int(os.environ.get("RATE_LIMIT_DELAY", "2"))

# Import for retry logic
import urllib3
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# Environment variables
ACCESS_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN")
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"
MAX_COMMENTS_PER_RUN = int(os.environ.get("MAX_COMMENTS_PER_RUN", "15"))
MAX_CONNECTIONS_PER_RUN = int(os.environ.get("MAX_CONNECTIONS_PER_RUN", "10"))
MAX_LIKES_PER_RUN = int(os.environ.get("MAX_LIKES_PER_RUN", "25"))

# AI API Keys for intelligent commenting
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# =====================================================
# FEATURE TOGGLES - Enable/Disable specific features
# Set to "true" to enable, "false" to disable
# ⚠️ IMPORTANT: Features marked NOT SUPPORTED use unofficial API endpoints
#    that LinkedIn does not provide. They are disabled by default.
# =====================================================
# ⚠️ NOT SUPPORTED by LinkedIn API (disabled by default)
ENABLE_TRENDING_COMMENTS = os.environ.get("ENABLE_TRENDING_COMMENTS", "false").lower() == "true"
ENABLE_INFLUENCER_ENGAGEMENT = os.environ.get("ENABLE_INFLUENCER_ENGAGEMENT", "false").lower() == "true"
ENABLE_HR_CONNECTIONS = os.environ.get("ENABLE_HR_CONNECTIONS", "false").lower() == "true"
ENABLE_STRATEGIC_LIKES = os.environ.get("ENABLE_STRATEGIC_LIKES", "false").lower() == "true"
# ✅ SUPPORTED features (enabled by default)
ENABLE_AI_COMMENTS = os.environ.get("ENABLE_AI_COMMENTS", "true").lower() == "true"
ENABLE_CONTENT_POSTING = os.environ.get("ENABLE_CONTENT_POSTING", "true").lower() == "true"
ENABLE_AUTO_REPLY_COMMENTS = os.environ.get("ENABLE_AUTO_REPLY_COMMENTS", "true").lower() == "true"  # Reply to comments on YOUR posts
MAX_REPLIES_PER_RUN = int(os.environ.get("MAX_REPLIES_PER_RUN", "10"))

logger.info(f"""
╔════════════════════════════════════════════════════════════════════════╗
║                    FEATURE TOGGLE STATUS                               ║
╠════════════════════════════════════════════════════════════════════════╣
║  ⚠️  UNSUPPORTED FEATURES (LinkedIn API does not provide these)        ║
║  ──────────────────────────────────────────────────────────────────────║
║  Trending Comments:      {'✅ ENABLED' if ENABLE_TRENDING_COMMENTS else '❌ DISABLED':25} (⚠️ API N/A) ║
║  Influencer Engagement:  {'✅ ENABLED' if ENABLE_INFLUENCER_ENGAGEMENT else '❌ DISABLED':25} (⚠️ API N/A) ║
║  HR Connections:         {'✅ ENABLED' if ENABLE_HR_CONNECTIONS else '❌ DISABLED':25} (⚠️ API N/A) ║
║  Strategic Likes:        {'✅ ENABLED' if ENABLE_STRATEGIC_LIKES else '❌ DISABLED':25} (⚠️ API N/A) ║
║  ──────────────────────────────────────────────────────────────────────║
║  ✅ SUPPORTED FEATURES (Official LinkedIn API)                         ║
║  ──────────────────────────────────────────────────────────────────────║
║  AI Comments:            {'✅ ENABLED' if ENABLE_AI_COMMENTS else '❌ DISABLED':25} (✅ Local)    ║
║  Content Posting:        {'✅ ENABLED' if ENABLE_CONTENT_POSTING else '❌ DISABLED':25} (✅ Official) ║
║  Auto-Reply Comments:    {'✅ ENABLED' if ENABLE_AUTO_REPLY_COMMENTS else '❌ DISABLED':25} (✅ Official) ║
║  Dry Run Mode:           {'✅ ENABLED' if DRY_RUN else '❌ DISABLED':25} (Test Mode)  ║
╚════════════════════════════════════════════════════════════════════════╝
""")

class LinkedInEngagementBot:
    """Advanced LinkedIn engagement automation for DevOps professionals."""
    
    def __init__(self):
        self.access_token = ACCESS_TOKEN
        if not self.access_token:
            raise ValueError("LinkedIn access token is required but not provided")
            
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0',
            'User-Agent': 'LinkedIn-DevOps-Automation/1.0'
        }
        self.base_url = "https://api.linkedin.com/v2"
        self.engagement_cache_file = "engagement_cache.json"
        
        # Production-grade HTTP session with timeouts and retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=RETRY_BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Rate limiting tracking
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_window_start = time.time()
        
        self.load_engagement_cache()
        
    def load_engagement_cache(self):
        """Load engagement history to avoid duplicate actions."""
        try:
            with open(self.engagement_cache_file, 'r') as f:
                self.engagement_cache = json.load(f)
        except FileNotFoundError:
            self.engagement_cache = {
                "commented_posts": [],
                "connected_profiles": [],
                "liked_posts": [],
                "replied_comments": [],  # Track comments we've replied to
                "my_posts": [],  # Track our own posts
                "last_run": None
            }
        # Ensure new keys exist in older cache files
        if "replied_comments" not in self.engagement_cache:
            self.engagement_cache["replied_comments"] = []
        if "my_posts" not in self.engagement_cache:
            self.engagement_cache["my_posts"] = []

    # =====================================================
    # ✅ SUPPORTED: YOUR OWN POSTS MANAGEMENT (Official API)
    # =====================================================
    
    def get_my_profile_id(self) -> Optional[str]:
        """Get the authenticated user's LinkedIn profile ID (OFFICIAL API)."""
        try:
            url = f"{self.base_url}/userinfo"  # OpenID Connect endpoint
            response = self._make_request('GET', url)
            
            if response.status_code == 200:
                profile_id = response.json().get("sub")  # OpenID uses "sub" field
                logger.info(f"✅ Got profile ID: {profile_id}")
                return profile_id
            else:
                logger.error(f"❌ Failed to get profile ID: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"❌ Error getting profile ID: {e}")
            return None
    
    def get_my_posts(self, limit: int = 10) -> List[Dict]:
        """Get YOUR recent posts (OFFICIAL API - ✅ SUPPORTED)."""
        try:
            profile_id = self.get_my_profile_id()
            if not profile_id:
                return []
            
            url = f"{self.base_url}/ugcPosts"
            params = {
                "q": "authors",
                "authors": f"List(urn:li:person:{profile_id})",
                "count": limit
            }
            
            response = self._make_request('GET', url, params=params)
            
            if response.status_code == 200:
                posts = response.json().get("elements", [])
                logger.info(f"✅ Retrieved {len(posts)} of your posts")
                return posts
            else:
                logger.warning(f"⚠️ Failed to get your posts: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error getting your posts: {e}")
            return []
    
    def get_comments_on_my_post(self, post_urn: str) -> List[Dict]:
        """Get comments on YOUR post (OFFICIAL API - ✅ SUPPORTED)."""
        try:
            # URL encode the post URN
            encoded_urn = requests.utils.quote(post_urn, safe='')
            url = f"{self.base_url}/socialActions/{encoded_urn}/comments"
            
            response = self._make_request('GET', url)
            
            if response.status_code == 200:
                comments = response.json().get("elements", [])
                logger.info(f"✅ Found {len(comments)} comments on post")
                return comments
            else:
                logger.debug(f"No comments or error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error getting comments: {e}")
            return []
    
    def reply_to_comment(self, post_urn: str, parent_comment_urn: str, reply_text: str) -> bool:
        """Reply to a comment on YOUR post (OFFICIAL API - ✅ SUPPORTED)."""
        try:
            if DRY_RUN:
                logger.info(f"🔍 [DRY RUN] Would reply: {reply_text[:50]}...")
                return True
            
            profile_id = self.get_my_profile_id()
            if not profile_id:
                return False
            
            encoded_urn = requests.utils.quote(post_urn, safe='')
            url = f"{self.base_url}/socialActions/{encoded_urn}/comments"
            
            payload = {
                "actor": f"urn:li:person:{profile_id}",
                "message": {
                    "text": reply_text
                },
                "parentComment": parent_comment_urn
            }
            
            response = self._make_request('POST', url, json=payload)
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Replied to comment successfully")
                return True
            else:
                logger.warning(f"⚠️ Failed to reply: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error replying to comment: {e}")
            return False
    
    def generate_reply_to_comment(self, comment_text: str, post_content: str = "") -> str:
        """Generate an AI-powered reply to a comment on YOUR post."""
        
        prompt = f"""
        As a DevOps expert, write a friendly, helpful reply to this comment on your LinkedIn post.
        
        Your post was about: {post_content[:200] if post_content else 'DevOps best practices'}
        
        Comment received: {comment_text}
        
        Requirements:
        - Be appreciative and professional
        - Add value with a brief insight or tip
        - Keep it under 150 characters
        - Sound natural and conversational
        - End with engagement (question or call to action)
        
        Example good replies:
        "Thanks for sharing your experience! That's a great point about monitoring. What metrics have been most valuable for you?"
        "Appreciate the feedback! We've seen similar results. Have you tried combining this with GitOps workflows?"
        "Great question! The key is starting small. I'd recommend beginning with one service and iterating from there."
        """
        
        # Try AI generation if enabled
        if ENABLE_AI_COMMENTS and GROQ_API_KEY:
            try:
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-70b-versatile",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 100,
                        "temperature": 0.7
                    },
                    timeout=REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    ai_reply = response.json()["choices"][0]["message"]["content"].strip()
                    if len(ai_reply) > 20 and len(ai_reply) <= 300:
                        logger.info("✅ Generated AI reply to comment")
                        return ai_reply
                        
            except Exception as e:
                logger.warning(f"⚠️ AI reply generation failed: {e}")
        
        # Fallback replies
        fallback_replies = [
            "Thanks for sharing your thoughts! What's been your experience with this approach?",
            "Great point! I've seen similar patterns. Would love to hear more about your setup.",
            "Appreciate the feedback! This is exactly the kind of discussion that helps us all learn.",
            "Thanks for the insight! Have you tried combining this with other DevOps practices?",
            "Really appreciate you taking the time to comment! Let's connect and discuss further."
        ]
        
        return random.choice(fallback_replies)
    
    def auto_reply_to_comments(self) -> Dict[str, int]:
        """Auto-reply to comments on YOUR posts (OFFICIAL API - ✅ SUPPORTED)."""
        stats = {"posts_checked": 0, "comments_found": 0, "replies_sent": 0}
        
        try:
            logger.info("💬 Starting auto-reply to comments on YOUR posts...")
            
            # Get your recent posts
            my_posts = self.get_my_posts(limit=5)
            
            for post in my_posts:
                stats["posts_checked"] += 1
                post_urn = post.get("id", "")
                post_content = post.get("specificContent", {}).get("com.linkedin.ugc.ShareContent", {}).get("shareCommentary", {}).get("text", "")
                
                # Get comments on this post
                comments = self.get_comments_on_my_post(post_urn)
                
                for comment in comments:
                    comment_urn = comment.get("$URN", comment.get("urn", ""))
                    comment_text = comment.get("message", {}).get("text", "")
                    commenter_id = comment.get("actor", "")
                    
                    # Skip if we've already replied to this comment
                    if comment_urn in self.engagement_cache.get("replied_comments", []):
                        continue
                    
                    # Skip if this is our own comment
                    profile_id = self.get_my_profile_id()
                    if profile_id and profile_id in commenter_id:
                        continue
                    
                    stats["comments_found"] += 1
                    
                    # Check if we've hit the reply limit
                    if stats["replies_sent"] >= MAX_REPLIES_PER_RUN:
                        logger.info(f"⏸️ Reached max replies per run ({MAX_REPLIES_PER_RUN})")
                        break
                    
                    # Generate and send reply
                    reply_text = self.generate_reply_to_comment(comment_text, post_content)
                    
                    if self.reply_to_comment(post_urn, comment_urn, reply_text):
                        stats["replies_sent"] += 1
                        self.engagement_cache["replied_comments"].append(comment_urn)
                        
                        # Store reply details for notifications
                        if "reply_details" not in self.engagement_cache:
                            self.engagement_cache["reply_details"] = []
                        self.engagement_cache["reply_details"].append({
                            "original_comment": comment_text[:100],
                            "our_reply": reply_text[:150],
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        logger.info(f"💬 Replied to comment: '{comment_text[:50]}...'")
                        logger.info(f"   └─ Our reply: '{reply_text[:80]}...'")
                    
                    # Rate limiting between replies
                    time.sleep(random.uniform(3, 6))
                
                if stats["replies_sent"] >= MAX_REPLIES_PER_RUN:
                    break
                    
                time.sleep(2)  # Rate limiting between posts
            
            logger.info(f"""
            ✅ Auto-reply completed:
            • Posts checked: {stats['posts_checked']}
            • Comments found: {stats['comments_found']}
            • Replies sent: {stats['replies_sent']}
            """)
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error in auto-reply: {e}")
            return stats

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Production-grade HTTP request with rate limiting and error handling."""
        
        # Rate limiting - ensure minimum delay between requests
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < RATE_LIMIT_DELAY:
            sleep_time = RATE_LIMIT_DELAY - time_since_last_request
            logger.info(f"Rate limiting: sleeping {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        # Track requests per hour for LinkedIn API limits
        if current_time - self.rate_limit_window_start > 3600:  # Reset hourly
            self.request_count = 0
            self.rate_limit_window_start = current_time
        
        self.request_count += 1
        if self.request_count > 100:  # Conservative LinkedIn API limit
            logger.warning(f"Approaching rate limit: {self.request_count} requests in current hour")
        
        try:
            # Set default timeout if not provided
            kwargs.setdefault('timeout', REQUEST_TIMEOUT)
            kwargs.setdefault('headers', self.headers)
            
            response = self.session.request(method, url, **kwargs)
            self.last_request_time = time.time()
            
            # Handle LinkedIn-specific rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', '300'))
                logger.warning(f"Rate limited by LinkedIn. Waiting {retry_after} seconds")
                time.sleep(retry_after)
                # Retry the request once after rate limit
                response = self.session.request(method, url, **kwargs)
            
            response.raise_for_status()  # Raise exception for HTTP errors
            return response
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout after {REQUEST_TIMEOUT} seconds: {url}")
            raise
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error to: {url}")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {response.status_code} for {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error making request to {url}: {e}")
            raise
    
    def save_engagement_cache(self):
        """Save engagement history."""
        try:
            with open(self.engagement_cache_file, 'w') as f:
                json.dump(self.engagement_cache, f, indent=2)
            logger.info("Engagement cache saved")
        except Exception as e:
            logger.error(f"Failed to save engagement cache: {e}")

    # =====================================================
    # TRENDING POSTS DISCOVERY & ENGAGEMENT
    # =====================================================
    
    DEVOPS_HASHTAGS = [
        "#devops", "#kubernetes", "#docker", "#aws", "#azure", "#gcp", 
        "#cicd", "#jenkins", "#terraform", "#ansible", "#monitoring",
        "#sre", "#cloudnative", "#microservices", "#observability",
        "#infrastructure", "#automation", "#containerization",
        "#platformengineering", "#gitops", "#iac", "#helm", "#prometheus"
    ]
    
    DEVOPS_KEYWORDS = [
        "kubernetes", "docker", "jenkins", "terraform", "ansible", 
        "aws", "azure", "gcp", "devops", "sre", "cicd", "microservices",
        "observability", "monitoring", "infrastructure", "automation",
        "cloud native", "containerization", "platform engineering",
        "gitops", "infrastructure as code", "helm", "prometheus",
        "grafana", "datadog", "splunk"
    ]
    
    def search_trending_devops_posts(self, limit: int = 20) -> List[Dict]:
        """Search for trending DevOps posts using LinkedIn search."""
        trending_posts = []
        
        # Search by hashtags
        for hashtag in random.sample(self.DEVOPS_HASHTAGS, min(5, len(self.DEVOPS_HASHTAGS))):
            try:
                search_url = f"{self.base_url}/posts"
                params = {
                    "q": "relevance",
                    "keywords": hashtag,
                    "sortBy": "RECENCY",
                    "count": 10
                }
                
                response = requests.get(search_url, headers=self.headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get("elements", [])
                    
                    for post in posts:
                        # Filter for high-engagement posts
                        if self.is_high_engagement_post(post):
                            trending_posts.append(post)
                            
                        if len(trending_posts) >= limit:
                            break
                            
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to search posts with hashtag {hashtag}: {e}")
                continue
                
            if len(trending_posts) >= limit:
                break
        
        # Sort by engagement metrics
        trending_posts.sort(key=lambda x: self.calculate_engagement_score(x), reverse=True)
        return trending_posts[:limit]
    
    def is_high_engagement_post(self, post: Dict) -> bool:
        """Check if post has high engagement potential."""
        try:
            # Check content relevance
            content = post.get("commentary", {}).get("text", "").lower()
            title = post.get("content", {}).get("title", "").lower()
            
            # Must contain DevOps keywords
            text_to_check = f"{content} {title}"
            if not any(keyword in text_to_check for keyword in self.DEVOPS_KEYWORDS):
                return False
            
            # Check engagement metrics
            social_counts = post.get("socialDetail", {})
            likes = social_counts.get("totalSocialActivityCounts", {}).get("numLikes", 0)
            comments = social_counts.get("totalSocialActivityCounts", {}).get("numComments", 0)
            shares = social_counts.get("totalSocialActivityCounts", {}).get("numShares", 0)
            
            # Minimum engagement threshold
            return likes > 10 or comments > 3 or shares > 2
            
        except Exception:
            return False
    
    def calculate_engagement_score(self, post: Dict) -> int:
        """Calculate engagement score for post ranking."""
        try:
            social_counts = post.get("socialDetail", {})
            likes = social_counts.get("totalSocialActivityCounts", {}).get("numLikes", 0)
            comments = social_counts.get("totalSocialActivityCounts", {}).get("numComments", 0)
            shares = social_counts.get("totalSocialActivityCounts", {}).get("numShares", 0)
            
            # Weighted engagement score
            return likes * 1 + comments * 3 + shares * 5
            
        except Exception:
            return 0

    # =====================================================
    # AI-POWERED INTELLIGENT COMMENTING
    # =====================================================
    
    def generate_intelligent_comment(self, post_content: str, post_title: str = "") -> str:
        """Generate contextual, valuable comments using AI."""
        
        # If AI comments are disabled, use fallback immediately
        if not ENABLE_AI_COMMENTS:
            logger.info("⏭️ AI comments DISABLED - using fallback")
            return self.get_fallback_comment(post_content, post_title)
        
        prompt = f"""
        As a senior DevOps engineer, write a thoughtful, professional comment for this LinkedIn post. 
        
        Post Title: {post_title}
        Post Content: {post_content[:500]}
        
        Requirements:
        - Be genuinely helpful and insightful
        - Share relevant technical experience
        - Ask a thoughtful follow-up question
        - Keep it under 150 characters
        - Sound natural and conversational
        - Avoid generic responses
        - Focus on practical value
        
        Example good comments:
        "Great insight! I've seen similar patterns with K8s scaling. How are you handling resource quotas in multi-tenant clusters?"
        "This resonates with our recent migration. The observability piece was crucial. Which metrics proved most valuable?"
        "Solid approach! We implemented something similar with Terraform. Have you experimented with policy as code validation?"
        """
        
        # Try Groq first (fastest) with production error handling
        if GROQ_API_KEY:
            try:
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-70b-versatile",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 100,
                        "temperature": 0.7
                    },
                    timeout=REQUEST_TIMEOUT
                )
                
                response.raise_for_status()  # Raise exception for HTTP errors
                
                if response.status_code == 200:
                    ai_comment = response.json()["choices"][0]["message"]["content"].strip()
                    # Validate AI response quality
                    if len(ai_comment) > 20 and len(ai_comment) <= 300 and not any(
                        spam_word in ai_comment.lower() for spam_word in ["generic", "placeholder", "lorem"]
                    ):
                        logger.info("Generated high-quality AI comment")
                        return ai_comment
                    else:
                        logger.warning("⚠️ AI comment quality check failed, using fallback")
                        
            except requests.exceptions.Timeout:
                logger.error(f"Groq API timeout after {REQUEST_TIMEOUT} seconds")
            except requests.exceptions.HTTPError as e:
                logger.error(f"Groq API HTTP error: {e}")
            except Exception as e:
                logger.error(f"Groq API unexpected error: {e}")
        
        # Fallback to pre-written intelligent comments
        return self.get_fallback_comment(post_content, post_title)
    
    def get_fallback_comment(self, content: str, title: str) -> str:
        """Generate contextual fallback comments based on content analysis."""
        
        content_lower = f"{content} {title}".lower()
        
        # Kubernetes/Container comments
        if any(word in content_lower for word in ["kubernetes", "k8s", "docker", "container"]):
            return random.choice([
                "Great insights on K8s! How are you handling resource optimization in your clusters?",
                "This resonates with our container journey. What's your approach to security scanning?",
                "Solid containerization strategy! Have you experimented with multi-stage builds?",
                "Love the K8s perspective! How do you handle persistent storage in production?"
            ])
        
        # CI/CD comments
        elif any(word in content_lower for word in ["cicd", "ci/cd", "jenkins", "github actions", "pipeline"]):
            return random.choice([
                "Excellent CI/CD insights! What's your testing strategy in the pipeline?",
                "This mirrors our deployment approach. How do you handle rollback scenarios?",
                "Great pipeline thinking! Have you integrated security scanning into your workflow?",
                "Solid automation! What metrics do you track for deployment success?"
            ])
        
        # Cloud/Infrastructure comments  
        elif any(word in content_lower for word in ["aws", "azure", "gcp", "cloud", "terraform", "infrastructure"]):
            return random.choice([
                "Smart infrastructure approach! How do you manage cost optimization?",
                "This aligns with our cloud strategy. What's your disaster recovery plan?",
                "Great IaC thinking! How do you handle environment consistency?",
                "Solid cloud architecture! Have you implemented policy as code?"
            ])
        
        # Monitoring/Observability comments
        elif any(word in content_lower for word in ["monitoring", "observability", "prometheus", "grafana"]):
            return random.choice([
                "Excellent observability approach! What SLIs do you prioritize?",
                "This resonates with our monitoring journey. How do you handle alert fatigue?",
                "Great metrics strategy! What's your approach to distributed tracing?",
                "Solid observability! How do you correlate logs with performance data?"
            ])
        
        # SRE/Reliability comments
        elif any(word in content_lower for word in ["sre", "reliability", "incident", "outage", "postmortem"]):
            return random.choice([
                "Valuable SRE insights! How do you balance reliability with feature velocity?",
                "This matches our reliability approach. What's your blameless postmortem process?",
                "Great reliability thinking! How do you measure and improve MTTR?",
                "Solid SRE practices! What chaos engineering tools do you recommend?"
            ])
        
        # Generic but valuable DevOps comments
        else:
            return random.choice([
                "Valuable insights! How has this approach impacted your deployment frequency?",
                "Great perspective! What challenges did you face during implementation?",
                "This resonates with our DevOps journey. What metrics prove the most value?",
                "Excellent approach! How do you measure the success of these practices?",
                "Solid thinking! Have you seen this scale across different team sizes?",
                "Great insights! What would you do differently knowing what you know now?"
            ])

    def comment_on_post(self, post_id: str, comment_text: str) -> bool:
        """Post a comment on a LinkedIn post."""
        
        if post_id in self.engagement_cache["commented_posts"]:
            logger.info(f"⏭️ Already commented on post {post_id}, skipping")
            return False
            
        if DRY_RUN:
            logger.info(f"🔍 [DRY RUN] Would comment on post {post_id}: {comment_text}")
            return True
        
        try:
            comment_url = f"{self.base_url}/socialActions/{post_id}/comments"
            
            payload = {
                "actor": f"urn:li:person:{self.get_profile_id()}",
                "message": {
                    "text": comment_text
                }
            }
            
            response = self._make_request('POST', comment_url, json=payload)
            
            if response.status_code in [200, 201]:
                self.engagement_cache["commented_posts"].append(post_id)
                logger.info(f"Successfully commented on post {post_id}")
                return True
            else:
                logger.warning(f"⚠️ Failed to comment on post {post_id}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error commenting on post {post_id}: {e}")
            return False

    # =====================================================
    # INFLUENTIAL PEOPLE ENGAGEMENT
    # =====================================================
    
    DEVOPS_INFLUENCERS = [
        # Add LinkedIn profile IDs of influential DevOps people
        # Format: {"name": "Name", "profile_id": "linkedin_person_id", "specialty": "area"}
        {"name": "Kelsey Hightower", "keywords": ["kubernetes", "google", "cloud native"]},
        {"name": "Jessie Frazelle", "keywords": ["containers", "docker", "security"]},  
        {"name": "Brendan Gregg", "keywords": ["performance", "observability", "linux"]},
        {"name": "Nicole Forsgren", "keywords": ["dora", "metrics", "research"]},
        {"name": "Gene Kim", "keywords": ["devops", "phoenix project", "unicorn project"]},
        {"name": "John Allspaw", "keywords": ["resilience", "incident response", "sre"]},
        {"name": "Charity Majors", "keywords": ["observability", "honeycomb", "debugging"]},
        {"name": "Adrian Cockcroft", "keywords": ["microservices", "netflix", "cloud"]},
        {"name": "Martin Fowler", "keywords": ["architecture", "microservices", "ci/cd"]},
        {"name": "Jez Humble", "keywords": ["continuous delivery", "lean", "devops"]}
    ]
    
    def find_influencer_posts(self, limit: int = 10) -> List[Dict]:
        """Find recent posts from DevOps influencers."""
        influencer_posts = []
        
        # Search for posts mentioning influencers or their content
        for influencer in random.sample(self.DEVOPS_INFLUENCERS, min(5, len(self.DEVOPS_INFLUENCERS))):
            try:
                # Search for posts mentioning the influencer's keywords
                keywords = " OR ".join(influencer["keywords"])
                
                search_url = f"{self.base_url}/posts"
                params = {
                    "q": "relevance", 
                    "keywords": keywords,
                    "sortBy": "RECENCY",
                    "count": 5
                }
                
                response = requests.get(search_url, headers=self.headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get("elements", [])
                    
                    for post in posts:
                        if self.is_influencer_related_post(post, influencer):
                            influencer_posts.append({
                                **post,
                                "influencer": influencer["name"],
                                "specialty": influencer["keywords"][0]
                            })
                            
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to search posts for {influencer['name']}: {e}")
                continue
                
            if len(influencer_posts) >= limit:
                break
        
        return influencer_posts[:limit]
    
    def is_influencer_related_post(self, post: Dict, influencer: Dict) -> bool:
        """Check if post is related to the influencer's expertise."""
        try:
            content = post.get("commentary", {}).get("text", "").lower()
            title = post.get("content", {}).get("title", "").lower()
            text = f"{content} {title}"
            
            # Check if post mentions influencer's keywords
            return any(keyword.lower() in text for keyword in influencer["keywords"])
            
        except Exception:
            return False

    # =====================================================
    # HR CONNECTION AUTOMATION
    # =====================================================
    
    HR_JOB_TITLES = [
        "HR Manager", "Human Resources", "Talent Acquisition", "Recruiter", 
        "Technical Recruiter", "Senior Recruiter", "Talent Partner",
        "People Operations", "Head of People", "Chief People Officer",
        "Talent Manager", "Recruitment Lead", "HR Business Partner",
        "Technical Talent Acquisition", "DevOps Recruiter", "Tech Recruiter",
        "Senior Technical Recruiter", "Principal Recruiter", "Director of Talent"
    ]
    
    HR_COMPANIES = [
        "Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix", "Uber", 
        "Airbnb", "Spotify", "Slack", "Atlassian", "Docker", "HashiCorp",
        "DataDog", "New Relic", "Splunk", "Elastic", "MongoDB", "Redis",
        "Confluent", "Snowflake", "Databricks", "GitLab", "GitHub"
    ]
    
    def search_hr_professionals(self, limit: int = 15) -> List[Dict]:
        """Search for HR professionals in tech companies."""
        hr_profiles = []
        
        # Search for HR professionals by job title and company
        for job_title in random.sample(self.HR_JOB_TITLES, min(3, len(self.HR_JOB_TITLES))):
            for company in random.sample(self.HR_COMPANIES, min(2, len(self.HR_COMPANIES))):
                try:
                    search_url = f"{self.base_url}/people"
                    params = {
                        "q": "relevance",
                        "keywords": f"{job_title} {company}",
                        "count": 5
                    }
                    
                    response = requests.get(search_url, headers=self.headers, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        profiles = data.get("elements", [])
                        
                        for profile in profiles:
                            if self.is_relevant_hr_profile(profile):
                                hr_profiles.append(profile)
                                
                    time.sleep(3)  # Increased rate limiting for people search
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to search HR profiles for {job_title} at {company}: {e}")
                    continue
                    
                if len(hr_profiles) >= limit:
                    break
                    
            if len(hr_profiles) >= limit:
                break
        
        return hr_profiles[:limit]
    
    def is_relevant_hr_profile(self, profile: Dict) -> bool:
        """Check if profile is a relevant HR professional."""
        try:
            # Check job title
            headline = profile.get("headline", "").lower()
            if not any(title.lower() in headline for title in self.HR_JOB_TITLES):
                return False
            
            # Check if they work at tech companies or have DevOps/tech focus
            company_info = profile.get("positions", {}).get("values", [])
            if company_info:
                company_name = company_info[0].get("company", {}).get("name", "").lower()
                if any(company.lower() in company_name for company in self.HR_COMPANIES):
                    return True
            
            # Check for tech/DevOps keywords in headline or summary
            tech_keywords = ["tech", "software", "devops", "engineering", "cloud", "saas"]
            return any(keyword in headline for keyword in tech_keywords)
            
        except Exception:
            return False
    
    def send_connection_request(self, profile_id: str, message: str = None) -> bool:
        """Send a connection request to a LinkedIn profile."""
        
        if profile_id in self.engagement_cache["connected_profiles"]:
            logger.info(f"⏭️ Already sent connection to {profile_id}, skipping")
            return False
        
        if DRY_RUN:
            logger.info(f"🔍 [DRY RUN] Would send connection request to {profile_id}")
            return True
        
        try:
            connection_url = f"{self.base_url}/people/invitations"
            
            payload = {
                "invitee": {
                    "com.linkedin.voyager.growth.invitation.InviteeProfile": {
                        "profileId": profile_id
                    }
                }
            }
            
            if message:
                payload["message"] = message
            
            response = requests.post(connection_url, headers=self.headers, json=payload)
            
            if response.status_code in [200, 201]:
                self.engagement_cache["connected_profiles"].append(profile_id)
                logger.info(f"Successfully sent connection request to {profile_id}")
                return True
            else:
                logger.warning(f"⚠️ Failed to send connection to {profile_id}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending connection request to {profile_id}: {e}")
            return False

    def generate_connection_message(self, profile: Dict) -> str:
        """Generate personalized connection messages for HR professionals."""
        
        messages = [
            "Hi! I'm a DevOps engineer passionate about building scalable systems. I'd love to connect and stay updated on opportunities in your network.",
            
            "Hello! I noticed your expertise in technical recruitment. I'm always interested in connecting with talent professionals who understand the DevOps space.",
            
            "Hi there! As a DevOps professional, I'd appreciate connecting with you to learn more about the evolving landscape of technical roles.",
            
            "Hello! I'm actively building my network with talent acquisition professionals. Would love to connect and share insights about the DevOps market.",
            
            "Hi! I see you work in technical recruitment. I'm always interested in connecting with HR professionals who specialize in engineering roles.",
            
            "Hello! I'd love to add you to my professional network. Your experience in talent acquisition would bring valuable perspective to my connections."
        ]
        
        return random.choice(messages)

    # =====================================================
    # ADDITIONAL REACH ENHANCEMENT STRATEGIES
    # =====================================================
    
    def like_strategic_posts(self, posts: List[Dict]) -> int:
        """Like posts strategically to increase visibility."""
        likes_count = 0
        
        for post in posts[:MAX_LIKES_PER_RUN]:
            post_id = post.get("id")
            if not post_id or post_id in self.engagement_cache["liked_posts"]:
                continue
                
            if DRY_RUN:
                logger.info(f"🔍 [DRY RUN] Would like post {post_id}")
                likes_count += 1
                continue
            
            try:
                like_url = f"{self.base_url}/socialActions/{post_id}/likes"
                payload = {
                    "actor": f"urn:li:person:{self.get_profile_id()}"
                }
                
                response = requests.post(like_url, headers=self.headers, json=payload)
                
                if response.status_code in [200, 201]:
                    self.engagement_cache["liked_posts"].append(post_id)
                    likes_count += 1
                    logger.info(f"👍 Liked post {post_id}")
                    
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to like post {post_id}: {e}")
                continue
        
        return likes_count
    
    def get_profile_id(self) -> str:
        """Get the current user's LinkedIn profile ID."""
        try:
            profile_url = f"{self.base_url}/people/~"
            response = requests.get(profile_url, headers=self.headers)
            
            if response.status_code == 200:
                profile_data = response.json()
                return profile_data.get("id", "")
            else:
                logger.warning("⚠️ Failed to get profile ID, using placeholder")
                return "placeholder"
                
        except Exception as e:
            logger.error(f"Error getting profile ID: {e}")
            return "placeholder"

    # =====================================================
    # MAIN EXECUTION ENGINE
    # =====================================================
    
    def run_engagement_automation(self):
        """Main execution function for engagement automation."""
        
        logger.info("Starting LinkedIn Engagement Automation")
        
        if not self.access_token:
            logger.error("LinkedIn access token not provided")
            return False
        
        start_time = datetime.now()
        stats = {
            "comments": 0,
            "connections": 0, 
            "likes": 0,
            "errors": 0
        }
        
        try:
            # 1. Find and comment on trending DevOps posts
            trending_posts = []
            if ENABLE_TRENDING_COMMENTS:
                logger.info("🔍 Searching for trending DevOps posts...")
                trending_posts = self.search_trending_devops_posts(MAX_COMMENTS_PER_RUN)
            else:
                logger.info("⏭️ Trending comments DISABLED - skipping")
            
            for post in trending_posts[:MAX_COMMENTS_PER_RUN]:
                try:
                    post_content = post.get("commentary", {}).get("text", "")
                    post_title = post.get("content", {}).get("title", "")
                    
                    if post_content or post_title:
                        comment = self.generate_intelligent_comment(post_content, post_title)
                        
                        if self.comment_on_post(post.get("id"), comment):
                            stats["comments"] += 1
                            
                    time.sleep(random.uniform(2, 5))  # Natural pacing
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error processing trending post: {e}")
                    stats["errors"] += 1
                    continue
            
            # 2. Engage with influencer posts
            influencer_posts = []
            if ENABLE_INFLUENCER_ENGAGEMENT:
                logger.info("🔍 Finding influencer posts...")
                influencer_posts = self.find_influencer_posts(5)
            else:
                logger.info("⏭️ Influencer engagement DISABLED - skipping")
            
            for post in influencer_posts:
                try:
                    post_content = post.get("commentary", {}).get("text", "")
                    post_title = post.get("content", {}).get("title", "")
                    
                    if post_content or post_title:
                        # More thoughtful comments for influencer posts
                        comment = self.generate_intelligent_comment(
                            f"Expert insights from {post['influencer']}: {post_content}",
                            post_title
                        )
                        
                        if self.comment_on_post(post.get("id"), comment):
                            stats["comments"] += 1
                            logger.info(f"💬 Commented on {post['influencer']}'s post")
                            
                    time.sleep(random.uniform(3, 6))  # Extra respectful pacing for influencers
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error processing influencer post: {e}")
                    stats["errors"] += 1
                    continue
            
            # 3. Send connection requests to HR professionals
            hr_professionals = []
            if ENABLE_HR_CONNECTIONS:
                logger.info("🤝 Searching for HR professionals...")
                hr_professionals = self.search_hr_professionals(MAX_CONNECTIONS_PER_RUN)
            else:
                logger.info("⏭️ HR connections DISABLED - skipping")
            
            for hr_profile in hr_professionals:
                try:
                    profile_id = hr_profile.get("id")
                    if profile_id:
                        message = self.generate_connection_message(hr_profile)
                        
                        if self.send_connection_request(profile_id, message):
                            stats["connections"] += 1
                            logger.info(f"🤝 Sent connection request to HR professional")
                            
                    time.sleep(random.uniform(10, 20))  # Conservative pacing for connections
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error processing HR profile: {e}")
                    stats["errors"] += 1
                    continue
            
            # 4. Strategic liking for visibility
            if ENABLE_STRATEGIC_LIKES:
                logger.info("👍 Liking strategic posts for visibility...")
                all_posts = trending_posts + influencer_posts
                liked_count = self.like_strategic_posts(all_posts)
                stats["likes"] = liked_count
            else:
                logger.info("⏭️ Strategic likes DISABLED - skipping")
            
            # 5. ✅ Auto-reply to comments on YOUR posts (SUPPORTED - Official API)
            reply_stats = {"replies_sent": 0}
            if ENABLE_AUTO_REPLY_COMMENTS:
                logger.info("💬 Auto-replying to comments on YOUR posts...")
                reply_stats = self.auto_reply_to_comments()
                stats["replies"] = reply_stats.get("replies_sent", 0)
            else:
                logger.info("⏭️ Auto-reply to comments DISABLED - skipping")
                stats["replies"] = 0
            
            # Save engagement history
            self.engagement_cache["last_run"] = datetime.now().isoformat()
            self.save_engagement_cache()
            
            # Log results
            duration = datetime.now() - start_time
            logger.info(f"""
╔════════════════════════════════════════════════════════════════════════╗
║           ENGAGEMENT AUTOMATION COMPLETED                              ║
╠════════════════════════════════════════════════════════════════════════╣
║  Duration: {duration.total_seconds():.1f} seconds                                                ║
╠════════════════════════════════════════════════════════════════════════╣
║  ⚠️ UNSUPPORTED FEATURES (API not available):                          ║
║  • Comments on others' posts: {stats['comments']}                                        ║
║  • Connection requests sent: {stats['connections']}                                       ║
║  • Posts liked: {stats['likes']}                                                   ║
║  ──────────────────────────────────────────────────────────────────────║
║  ✅ SUPPORTED FEATURES (Official API):                                 ║
║  • Replies to comments on YOUR posts: {stats.get('replies', 0)}                            ║
║  ──────────────────────────────────────────────────────────────────────║
║  Errors encountered: {stats['errors']}                                             ║
╚════════════════════════════════════════════════════════════════════════╝
            """)
            
            return True
            
        except Exception as e:
            logger.error(f"Fatal error in engagement automation: {e}")
            return False


def main():
    """Main entry point for the engagement automation."""
    
    if not ACCESS_TOKEN:
        print("ERROR: LINKEDIN_ACCESS_TOKEN environment variable not set")
        sys.exit(1)
    
    bot = LinkedInEngagementBot()
    success = bot.run_engagement_automation()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
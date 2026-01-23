# Minimal stubs for digest post templates and footer_question (must be top-level)
cta_templates = ["Check it out!"]
subscribe_templates = ["Subscribe for more insights."]
playbook_templates = ["See the full playbook."]
hashtag_templates = ["#DevOps #Cloud"]
footer_question = "What are your thoughts?"
# =====================
# MISSING CONSTANTS & DEFAULTS
# =====================
ENABLE_AI_ENHANCE = True
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
HF_API_KEY = os.environ.get("HF_API_KEY", "")
MAX_POST_CHARS = 1300
PERSONA_LINE = "Industry leader perspective."
USE_DYNAMIC_PERSONA = False
DYNAMIC_PERSONAS = {}
FREE_AI_PROVIDERS = {}
AI_SUMMARIZATION_MODELS = []
AI_GENERATION_MODELS = []
API_VERSION = "202401"
ALWAYS_INCLUDE_LINKS = True
INCLUDE_LINKS = True

# Provide minimal stubs for undefined helpers if missing
def remix_title(title):
    return title
def summarize_snippet(snippet):
    return snippet
def get_enabled_providers():
    return []
import itertools
import os
import feedparser
import requests
import sys
import json
import random
import re
import logging
import hashlib
import time
import tempfile
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Import fcntl for Unix systems only
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False

# -------------------------------------------------
# LOGGING SETUP
# -------------------------------------------------

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# -------------------------------------------------
# ENV
# -------------------------------------------------

ACCESS_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN")


# =====================
# CONFIG & CONSTANTS
# =====================

def safe_int(val, default=0, minval=None, maxval=None):
    try:
        v = int(val)
        if minval is not None:
            v = max(minval, v)
        if maxval is not None:
            v = min(maxval, v)
        return v
    except Exception:
        return default

DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"
MAX_ITEMS = safe_int(os.environ.get("MAX_ITEMS", "8"), 8, 1, 20)

KEYWORDS_INCLUDE = [
    k.strip().lower()
    for k in os.environ.get(
        "KEYWORDS_INCLUDE",
        "devops,devsecops,sre,kubernetes,cloud,platform,terraform,helm,gitops,cicd,observability,incident,reliability,aws,gcp,azure,docker,containers,monitoring,security,vulnerability,iam,rbac,policy,compliance,shift-left,sast,dast,sbom,supply-chain",
    ).split(",")
    if k.strip()
]

KEYWORDS_EXCLUDE = [
    k.strip().lower()
    for k in os.environ.get(
        "KEYWORDS_EXCLUDE",
        "sponsored,advertisement,marketing,webinar,press release",
    ).split(",")
    if k.strip()
]

MIN_ARTICLE_AGE_HOURS = safe_int(os.environ.get("MIN_ARTICLE_AGE_HOURS", "0"), 0, 0, 168)
MAX_ARTICLE_AGE_HOURS = safe_int(os.environ.get("MAX_ARTICLE_AGE_HOURS", "72"), 72, 1, 720)

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")

# ...existing code...

def main():
    try:
        post_type = None
        post_text = None
        # Minimal stubs for digest post templates and footer_question
        cta_templates = ["Check it out!"]
        subscribe_templates = ["Subscribe for more insights."]
        playbook_templates = ["See the full playbook."]
        hashtag_templates = ["#DevOps #Cloud"]
        footer_question = "What are your thoughts?"
        logger.info("🚀 Starting LinkedIn DevOps post automation...")
        # 1. Try growth plan content first
        idea = get_growth_plan_content()
        if __name__ == "__main__":
            main()
        # 3. Print or post
        if DRY_RUN:
            logger.info(f"[DRY RUN] Would post the following {post_type} content:")
            print(f"\n===== [DRY RUN] LinkedIn Post Content ({post_type}) =====\n")
            print(post_text)
            print("\n===== [END OF POST] =====\n")
            # Optionally, send to Slack for preview if enabled
            if SLACK_WEBHOOK_URL:
                try:
                    http_request(
                        "POST",
                        SLACK_WEBHOOK_URL,
                        json_body={"text": f"[DRY RUN] LinkedIn Post Preview ({post_type}):\n\n{post_text}"},
                        timeout=10
                    )
                    logger.info("[DRY RUN] Sent post preview to Slack.")
                except Exception as e:
                    logger.warning(f"[DRY RUN] Failed to send Slack preview: {e}")
            return

        # 4. Actually post to LinkedIn (implement as needed)
        logger.info(f"[LIVE RUN] Would post to LinkedIn ({post_type}). Printing post:")
        print(f"\n===== [LIVE RUN] LinkedIn Post Content ({post_type}) =====\n")
        print(post_text)
        print("\n===== [END OF POST] =====\n")
        # TODO: Add LinkedIn posting logic here

    except Exception as e:
        logger.error(f"❌ Unhandled exception in main: {e}")
        print(f"❌ Unhandled exception: {e}")



if __name__ == "__main__":
    main()

def generate_ai_persona(post_format: str = None, content: str = None, title: str = None) -> Optional[str]:
    """Generate a dynamic persona using AI based on content context."""
    if not ENABLE_AI_ENHANCE:
        return None
    
    # Build context for AI
    context_info = ""
    if title:
        context_info += f"Article title: {title}\n"
    if content:
        context_info += f"Content snippet: {content[:300]}\n"
    if post_format:
        context_info += f"Post format: {post_format}\n"
    
    prompt = f"""Generate a single, compelling intro line for a DevOps thought leader sharing content on LinkedIn.

{context_info}

Requirements:
- CRITICAL: Do NOT use first-person pronouns (I, me, my, we, our). Write in authoritative third-person.
- 10-20 words maximum
- Sound like an industry expert sharing insights
- Match the content topic/format
- Professional, authoritative tone
- End with a transition phrase like "Here's..." or "This matters."

Example good intro lines:
- "Enterprise-scale systems reveal deep insights from the trenches. Here's what matters."
- "Security at scale demands constant vigilance. This is significant."
- "Container orchestration patterns reveal key trends. Worth understanding."
- "Simplifying complex DevOps challenges with hands-on expertise. Here's the breakdown."

Return ONLY the intro line, nothing else."""

    # Try AI providers
    if GROQ_API_KEY:
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 60,
                    "temperature": 0.7
                },
                timeout=10
            )
            if response.status_code == 200:
                ai_persona = response.json()["choices"][0]["message"]["content"].strip()
                # Clean up - remove quotes if present
                ai_persona = ai_persona.strip('"\'')
                # Reject if it starts with first-person pronouns
                if ai_persona.lower().startswith(("i ", "i'", "we ", "my ", "our ")):
                    logger.debug("AI persona rejected - contains first-person pronouns")
                    return None
                if 15 <= len(ai_persona) <= 200:
                    logger.info(f"✅ AI-generated persona: {ai_persona[:50]}...")
                    return ai_persona
        except Exception as e:
            logger.debug(f"AI persona generation failed: {e}")
    
    return None


# Fallback personas by post format - Authoritative third-person style
FALLBACK_PERSONAS_BY_FORMAT = {
    "deep_dive": "Enterprise-scale systems reveal deep insights from the trenches.",
    "case_study": "This pattern plays out repeatedly in production environments.",
    "lessons": "Hard-earned lessons from the field - so teams avoid the same mistakes.",
    "hot_take": "Unpopular opinion: conventional wisdom doesn't always serve engineering teams.",
    "quick_tip": "Practical techniques that actually work in production.",
    "digest": "Curating the signals that matter in DevOps."
}

# Fallback personas by content topic - Authoritative third-person style
FALLBACK_PERSONAS_BY_TOPIC = {
    "kubernetes": [
        "Container orchestration in production reveals key patterns.",
        "Enterprise-scale Kubernetes clusters teach valuable lessons.",
        "Container orchestration strategies worth understanding.",
        "Cloud-native systems and Kubernetes updates reveal trends.",
        "Resilient container infrastructure shows what works."
    ],
    "security": [
        "Secure systems at scale demand constant vigilance.",
        "Enterprise security implementations reveal key patterns.",
        "Defense-in-depth strategies show what works."
    ],
    "observability": [
        "Understanding system behavior requires proper instrumentation.",
        "Monitoring that matters avoids vanity metrics.",
        "Telemetry strategies for complex systems reveal patterns."
    ],
    "incident": [
        "Production incidents reveal patterns worth studying.",
        "Reliability programs and failure patterns offer insights.",
        "Outages become learning opportunities."
    ],
    "cloud": [
        "Cloud-native solutions and platform evolution show patterns.",
        "Cloud migration and scale optimization reveal what matters.",
        "Multi-cloud strategies and vendor moves show trends."
    ],
    "terraform": [
        "Infrastructure as code at scale reveals key patterns.",
        "Terraform provisioning automation teaches valuable lessons.",
        "Reusable infrastructure modules show what works."
    ],
    "cicd": [
        "Deployment pipelines that ship code safely reveal patterns.",
        "CI/CD optimization for speed and reliability matters.",
        "Automated testing and deployment workflows show trends."
    ],
    "docker": [
        "Containerized applications optimized for production show patterns.",
        "Efficient container images and orchestration reveal insights.",
        "Container security and networking strategies matter."
    ],
    "monitoring": [
        "System visibility to catch issues before users do is critical.",
        "Comprehensive monitoring and alerting reveals patterns.",
        "Observability platforms for complex systems show trends."
    ],
    "devops": [
        "Bridging development and operations delivers value faster.",
        "DevOps practices at scale reveal key patterns.",
        "DevOps culture transformation shows what works."
    ]
}


def get_dynamic_persona(post_format=None, content=None, title=None, items=None):
    """Generate context-aware persona line using AI with smart fallbacks."""
    if not USE_DYNAMIC_PERSONA:
        return PERSONA_LINE
    
    # Step 1: Try AI-generated persona first
    ai_persona = generate_ai_persona(post_format, content, title)
    if ai_persona:
        return ai_persona
    
    logger.info("⚡ Using fallback persona system...")
    
    # Step 2: Try content topic-specific fallback
    if content or title:
        text = f"{title or ''} {content or ''}".lower()
        for keyword, personas in FALLBACK_PERSONAS_BY_TOPIC.items():
            if keyword in text:
                # Choose random persona from the list
                persona = random.choice(personas)
                # Add variety with random ending
                endings = [
                    " Here's the signal.",
                    " This matters.",
                    " Worth understanding.",
                    " Pay attention to this.",
                    " Let's break this down."
                ]
                logger.info(f"📝 Using topic fallback for: {keyword}")
                return persona + random.choice(endings)
    
    # Step 3: Try format-specific fallback
    if post_format and post_format in FALLBACK_PERSONAS_BY_FORMAT:
        endings = [
            " Here's what stands out.",
            " This is worth your time.",
            " Let's dive in.",
            " Here's the signal."
        ]
        logger.info(f"📝 Using format fallback for: {post_format}")
        return FALLBACK_PERSONAS_BY_FORMAT[post_format] + random.choice(endings)
    
    # Step 4: Try random from extended persona lists
    if post_format and post_format in DYNAMIC_PERSONAS:
        # Dynamic industry-leader style intro/header lines
        # Context-aware intro and subheader
        main_topics = []
        tools_techs = []
        # Common DevOps/cloud tools and technologies for detection
        KNOWN_TOOLS_TECHS = [
            "Kubernetes", "Docker", "Terraform", "Ansible", "Prometheus", "Grafana", "Jenkins", "GitHub", "GitLab", "Azure", "AWS", "GCP", "ArgoCD", "Helm", "Istio", "Linkerd", "Vault", "Consul", "OpenShift", "CircleCI", "PagerDuty", "Slack", "Snyk", "SonarQube", "Datadog", "Splunk", "ELK", "Fluentd", "Cloudflare", "Fastly", "New Relic", "ServiceNow", "Bitbucket", "Trivy", "Sysdig", "Falco", "CloudFormation", "Pulumi", "Octopus Deploy", "Opsgenie", "Sumo Logic", "AppDynamics", "Dynatrace", "Nagios", "Zabbix", "SaltStack", "Chef", "Puppet"
        ]
        for item in (items or []):
            title = item.get("title", "")
            summary = item.get("summary", "")
            text = f"{title} {summary}"
            # Extract main keywords (simple heuristic: first 2-3 words)
            words = [w for w in re.split(r'\W+', title) if len(w) > 2][:3]
            main_topics.extend(words)
            # Detect tools/technologies
            for tool in KNOWN_TOOLS_TECHS:
                if tool.lower() in text.lower() and tool not in tools_techs:
                    tools_techs.append(tool)
        main_topics = list(dict.fromkeys(main_topics))  # Remove duplicates, preserve order
        tools_techs = list(dict.fromkeys(tools_techs))
        topics_str = ", ".join(main_topics[:3]) if main_topics else "DevOps, Cloud, Security"
        tools_str = ", ".join(tools_techs[:4]) if tools_techs else "modern platforms"
        # Paraphrase and synonym variations for intro/subheader
        intro_templates = [
            f"🛠️ **This week's signal:** {topics_str} | 🧰 **Tools:** {tools_str}",
            f"🛠️ **Key signals this week:** {topics_str} | 🧰 **Stack:** {tools_str}",
            f"🛠️ **Spotlight:** {topics_str} | 🧰 **Featured tech:** {tools_str}",
            f"🛠️ **Trending now:** {topics_str} | 🧰 **Ecosystem:** {tools_str}",
            f"🛠️ **Weekly highlights:** {topics_str} | 🧰 **Focus:** {tools_str}"
        ]
        subheader_templates = [
            f"👀 **Industry leaders are watching:** {topics_str} | {tools_str}.",
            f"👀 **What experts are tracking:** {topics_str} | {tools_str}.",
            f"👀 **Signals shaping the field:** {topics_str} | {tools_str}.",
            f"👀 **Strategic trends:** {topics_str} | {tools_str}.",
            f"👀 **What matters for teams:** {topics_str} | {tools_str}."
        ]
        intro = random.choice(intro_templates)
        subheader = random.choice(subheader_templates)
        lines = [intro, subheader, ""]

        if items is None:
            items = []
        section_emojis = ["🚀", "🔒", "☁️", "📈", "🧩", "⚡", "🔍", "🧠", "🛡️", "📦", "🧰", "🛠️", "💡", "📊", "🌐"]
        used_impact_lines = set()
        # Shuffle the order of items for extra uniqueness
        shuffled_items = list(items) if items else []
        random.shuffle(shuffled_items)
        impact_templates = [
            "Why it matters:",
            "Key takeaway:",
            "Industry impact:",
            "Strategic insight:",
            "For your roadmap:",
            "Leadership lens:",
            "What to watch:",
            "Actionable insight:",
            "Signal for teams:",
            "Consider this:"
        ]
        for i, item in enumerate(shuffled_items, 1):
            emoji = section_emojis[(i-1) % len(section_emojis)]
            takeaway = remix_title(item["title"])
            snippet = summarize_snippet(item.get("summary", ""))
            # Try to generate a unique impact line for each section
            attempts = 0
            value = ai_generate_value_line(item.get("title", ""), snippet)
            while value in used_impact_lines and attempts < 5:
                value = ai_generate_value_line(item.get("title", "") + f" {random.randint(0,9999)}", snippet)
                attempts += 1
            used_impact_lines.add(value)
            impact_label = random.choice(impact_templates)
            lines.append(f"{emoji} **{i}. {takeaway}**\n👉 _Context:_ {snippet}\n💡 _{impact_label}_ {value}\n🔗 {item.get('link', '')}\n")

        # Context-aware footer question
        if main_topics or tools_techs:
            topic = main_topics[0].lower() if main_topics else "devops"
            tool = tools_techs[0] if tools_techs else "modern platforms"
            footer_templates = [
                f"How is your team approaching {topic} and {tool} this quarter?",
                f"Which {topic} or {tool} trend will impact your roadmap most?",
                f"What challenges are you seeing in {topic} or {tool}?",
                f"How are you measuring success in {topic} or {tool} initiatives?",
                f"What would you add to this {topic} and {tool} watchlist?"
            ]
        else:
            footer_templates = [
                "What would your team prioritize?",
                "Which of these trends will shape your roadmap?",
                "What are your thoughts on these developments?",
                "How is your organization responding to these signals?",
                "Which signal resonates most with your strategy?"
            ]
        global _USED_FOOTER_QUESTIONS
        available_questions = [q for q in footer_templates if q not in _USED_FOOTER_QUESTIONS]
        if not available_questions:
            _USED_FOOTER_QUESTIONS = []
            available_questions = footer_templates.copy()
        footer_question = random.choice(available_questions)
        _USED_FOOTER_QUESTIONS.append(footer_question)
        cta_templates = [
            "💌 **Get weekly DevOps insights delivered to your inbox – subscribe to stay ahead!**",
            "💌 **Stay ahead: subscribe for weekly DevOps insights!**",
            "💌 **Don’t miss out – get DevOps news in your inbox!**",
            "💌 **Level up your DevOps game – subscribe now!**"
        ]
        subscribe_templates = [
            "👉 **Subscribe:** https://lnkd.in/g_mZKwxY",
            "👉 **Join here:** https://lnkd.in/g_mZKwxY",
            "👉 **Sign up:** https://lnkd.in/g_mZKwxY"
        ]
        playbook_templates = [
            "📖 **DevOps LinkedIn Playbook:** https://lnkd.in/gzTACvZf",
            "📖 **Get the Playbook:** https://lnkd.in/gzTACvZf",
            "📖 **LinkedIn Playbook:** https://lnkd.in/gzTACvZf"
        ]
        hashtag_templates = [
            "#Infrastructure #DevOps #Security #CloudNative #Kubernetes #Engineering #DevSecOps",
            "#DevOps #Cloud #SRE #Platform #Security #Kubernetes #Engineering",
            "#CloudNative #DevSecOps #Observability #Platform #Infra #Kubernetes #DevOps"
        ]
        lines.extend([
            "",
            random.choice(cta_templates),
            random.choice(subscribe_templates),
            random.choice(playbook_templates),
            "",
            random.choice(hashtag_templates),
            "",
            f"❓ {footer_question}"
        ])
        post = "\n".join(lines)
        return clip(post, MAX_POST_CHARS)
    enabled = []
    for provider_id, config in FREE_AI_PROVIDERS.items():
        is_enabled = config.get("enabled", lambda: False)()
        logger.debug(f"Provider {provider_id} ({config.get('name', provider_id)}): {'enabled' if is_enabled else 'disabled'}")
        if is_enabled:
            enabled.append((config.get("priority", 0), provider_id, config))
    sorted_providers = [item[1:] for item in sorted(enabled)]
    logger.debug(f"Final enabled providers (priority order): {[(pid, config.get('name', pid)) for pid, config in sorted_providers]}")
    return sorted_providers

def call_groq_api(api_key: str, model: str, prompt: str, max_tokens: int = 150, task_type: str = "summarization") -> Optional[str]:
    """Call Groq API for text generation/summarization."""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Optimize prompt for task
        if task_type == "summarization":
            system_prompt = "You are a technical content summarizer. Provide a concise, clear summary in 2-3 sentences maximum."
            user_prompt = f"Summarize this DevOps/SRE content concisely:\n\n{prompt}"
        else:
            system_prompt = "You are a DevOps expert. Explain technical concepts clearly and concisely."
            user_prompt = prompt
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt[:2000]}  # Groq token limit
            ],
            "max_tokens": min(max_tokens, 200),
            "temperature": 0.3,
            "top_p": 0.9
        }
        
        response = http_request(
            "POST",
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json_body=payload,
            timeout=10,
            retries=2
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            if content:
                logger.debug(f"✓ Groq API success with {model}")
                return content
        else:
            logger.debug(f"Groq API error: {response.status_code}")
            
    except Exception as e:
        logger.debug(f"Groq API exception: {e}")
    
    return None

def call_gemini_api(api_key: str, model: str, prompt: str, max_tokens: int = 150, task_type: str = "summarization") -> Optional[str]:
    """Call Google Gemini API for text generation/summarization."""
    try:
        # Optimize prompt for task
        if task_type == "summarization":
            full_prompt = f"Summarize this DevOps/SRE content in 2-3 clear, concise sentences:\n\n{prompt}"
        else:
            full_prompt = prompt
        
        payload = {
            "contents": [
                {
                    "parts": [{"text": full_prompt[:4000]}]  # Gemini context limit
                }
            ],
            "generationConfig": {
                "maxOutputTokens": min(max_tokens, 300),
                "temperature": 0.4,
                "topP": 0.8
            }
        }
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        response = http_request(
            "POST",
            url,
            json_body=payload,
            timeout=15,
            retries=2
        )
        
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates and "content" in candidates[0]:
                content = candidates[0]["content"]["parts"][0]["text"].strip()
                if content:
                    logger.debug(f"✓ Gemini API success with {model}")
                    return content
        else:
            logger.debug(f"Gemini API error: {response.status_code}")
            
    except Exception as e:
        logger.debug(f"Gemini API exception: {e}")
    
    return None

def call_openrouter_api(api_key: str, model: str, prompt: str, max_tokens: int = 150, task_type: str = "summarization") -> Optional[str]:
    """Call OpenRouter API with free models."""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-repo",  # Required by OpenRouter
            "X-Title": "LinkedIn DevOps Automation"
        }
        
        # Optimize prompt for task
        if task_type == "summarization":
            system_prompt = "You are a technical content summarizer for DevOps professionals. Be concise and clear."
            user_prompt = f"Summarize this DevOps/SRE content in 2-3 sentences:\n\n{prompt}"
        else:
            system_prompt = "You are a DevOps expert explaining technical concepts clearly."
            user_prompt = prompt
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt[:1500]}
            ],
            "max_tokens": min(max_tokens, 200),
            "temperature": 0.3
        }
        
        response = http_request(
            "POST",
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json_body=payload,
            timeout=12,
            retries=2
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            if content:
                logger.debug(f"✓ OpenRouter API success with {model}")
                return content
        else:
            logger.debug(f"OpenRouter API error: {response.status_code}")
            
    except Exception as e:
        logger.debug(f"OpenRouter API exception: {e}")
    
    return None

def call_huggingface_api(api_key: str, model: str, prompt: str, max_tokens: int = 150, task_type: str = "summarization") -> Optional[str]:
    """Call Hugging Face API (legacy support)."""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        
        if task_type == "summarization":
            payload = {
                "inputs": prompt[:1024],
                "parameters": {
                    "max_length": max_tokens,
                    "min_length": 30,
                    "do_sample": False,
                }
            }
        else:
            payload = {
                "inputs": prompt[:1024],
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "do_sample": False,
                    "return_full_text": False,
                },
            }
        
        response = http_request(
            "POST",
            f"https://api-inference.huggingface.co/models/{model}",
            headers=headers,
            json_body=payload,
            timeout=10,
            retries=1
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                text = (
                    result[0].get("summary_text", "") or 
                    result[0].get("generated_text", "") or
                    result[0].get("text", "")
                ).strip()
                if text:
                    logger.debug(f"✓ HuggingFace API success with {model}")
                    return text
        else:
            logger.debug(f"HuggingFace API error: {response.status_code}")
            
    except Exception as e:
        logger.debug(f"HuggingFace API exception: {e}")
    
    return None

def try_multi_provider_ai(prompt: str, task_type: str = "summarization", max_tokens: int = 150) -> Optional[str]:
    """Try multiple AI providers until one succeeds."""
    if not ENABLE_AI_ENHANCE:
        logger.debug("AI enhancement disabled")
        return None
    
    enabled_providers = get_enabled_providers()
    logger.debug(f"Enabled providers: {[(pid, config['name']) for pid, config in enabled_providers]}")
    
    if not enabled_providers:
        logger.warning("⚠ No AI providers enabled - add API keys to enable AI features")
        return None
    
    providers_tried = []
    
    for provider_id, config in enabled_providers:
        models = config["models"].get(task_type, [])
        if not models:
            logger.debug(f"No {task_type} models for provider {provider_id}")
            continue
            
        api_key = config["api_key"]()
        if not api_key:
            logger.debug(f"No API key for provider {provider_id}")
            continue
            
        for model in models:
            try:
                providers_tried.append(f"{provider_id}:{model}")
                logger.info(f"Trying {config['name']} with {model}")
                
                result = None
                if provider_id == "groq":
                    result = call_groq_api(api_key, model, prompt, max_tokens, task_type)
                elif provider_id == "gemini":
                    result = call_gemini_api(api_key, model, prompt, max_tokens, task_type)
                elif provider_id == "openrouter":
                    result = call_openrouter_api(api_key, model, prompt, max_tokens, task_type)
                elif provider_id == "huggingface":
                    result = call_huggingface_api(api_key, model, prompt, max_tokens, task_type)
                
                if result and result.strip():
                    logger.info(f"✓ AI success: {config['name']} ({model}) - tried {len(providers_tried)}")
                    return result.strip()
                    
            except Exception as e:
                logger.debug(f"Provider {provider_id} model {model} failed: {e}")
                continue
    
    logger.warning(f"⚠ All AI providers failed. Tried: {', '.join(providers_tried[:5])}")
    return None

def get_available_ai_models(model_type="summarization"):
    """Get list of available AI models based on type (legacy function)."""
    if model_type == "summarization":
        return AI_SUMMARIZATION_MODELS.copy()
    elif model_type == "generation":
        return AI_GENERATION_MODELS.copy()
    else:
        return AI_SUMMARIZATION_MODELS.copy()

def try_ai_model_with_fallback(model_list, payload, timeout=10, model_type="summarization"):
    """Legacy function for backward compatibility - now uses multi-provider system."""
    if not model_list or not ENABLE_AI_ENHANCE:
        return None
        
    # Convert legacy payload to prompt
    prompt = ""
    if isinstance(payload, dict):
        prompt = payload.get("inputs", "")
        max_tokens = payload.get("parameters", {}).get("max_length", 80)
        if not prompt:
            # Try to extract from generation format
            max_tokens = payload.get("parameters", {}).get("max_new_tokens", 80)
    else:
        prompt = str(payload)
        max_tokens = 80
    
    if prompt:
        return try_multi_provider_ai(prompt, model_type, max_tokens)
    
    return None

KEYWORDS_INCLUDE = [
    k.strip().lower()
    for k in os.environ.get(
        "KEYWORDS_INCLUDE",
        "devops,devsecops,sre,kubernetes,cloud,platform,terraform,helm,gitops,cicd,observability,incident,reliability,aws,gcp,azure,docker,containers,monitoring,security,vulnerability,iam,rbac,policy,compliance,shift-left,sast,dast,sbom,supply-chain",
    ).split(",")
    if k.strip()
]

KEYWORDS_EXCLUDE = [
    k.strip().lower()
    for k in os.environ.get(
        "KEYWORDS_EXCLUDE",
        "sponsored,advertisement,marketing,webinar,press release",
    ).split(",")
    if k.strip()
]

# Article filtering
MIN_ARTICLE_AGE_HOURS = safe_int(os.environ.get("MIN_ARTICLE_AGE_HOURS", "0"), 0, 0, 168)
MAX_ARTICLE_AGE_HOURS = safe_int(os.environ.get("MAX_ARTICLE_AGE_HOURS", "72"), 72, 1, 720)

# Post styling
EMOJI_STYLE = os.environ.get("EMOJI_STYLE", "moderate")  # none, minimal, moderate, heavy
TONE = os.environ.get("TONE", "professional")  # professional, casual, bold, educational
HASHTAGS_ENV = os.environ.get("HASHTAGS", "")  # Custom hashtags (space-separated with #)
MAX_HASHTAGS = safe_int(os.environ.get("MAX_HASHTAGS", "5"), 5, 1, 20)
ROTATE_HASHTAGS = os.environ.get("ROTATE_HASHTAGS", "true").lower() == "true"
INCLUDE_PERSONA = os.environ.get("INCLUDE_PERSONA", "true").lower() == "true"

# Post formats
POST_FORMATS_STR = os.environ.get("POST_FORMATS", "digest,deep_dive,quick_tip,case_study,hot_take,lessons")
AVAILABLE_POST_FORMATS = [f.strip() for f in POST_FORMATS_STR.split(",") if f.strip()]
FORCE_FORMAT = os.environ.get("FORCE_FORMAT", "auto")  # auto, or specific format name
CUSTOM_MESSAGE = os.environ.get("CUSTOM_MESSAGE", "")  # Override with custom message

# Growth Plan Integration
USE_GROWTH_PLAN = os.environ.get("USE_GROWTH_PLAN", "true").lower() == "true"
GROWTH_PLAN_FILE = os.environ.get("GROWTH_PLAN_FILE", "weekly_growth_plan.json")
GROWTH_PLAN_PROBABILITY = float(os.environ.get("GROWTH_PLAN_PROBABILITY", "0.4"))  # 40% growth plan (intelligent), 60% RSS news

# Rate limiting
# Rate limiting and timing controls
# Allow bypassing for testing by setting MIN_POST_INTERVAL_HOURS=0
MIN_POST_INTERVAL_HOURS = safe_int(os.environ.get("MIN_POST_INTERVAL_HOURS", "4"), 4, 0, 48)
BYPASS_RATE_LIMITS = os.environ.get("BYPASS_RATE_LIMITS", "false").lower() == "true"

# Feed parsing configuration
FEED_TIMEOUT_SECONDS = int(os.environ.get("FEED_TIMEOUT_SECONDS", "15"))
SKIP_MALFORMED_FEEDS = os.environ.get("SKIP_MALFORMED_FEEDS", "true").lower() == "true"
MAX_FEED_RETRIES = int(os.environ.get("MAX_FEED_RETRIES", "2"))
MAX_FEED_LIMIT = int(os.environ.get("MAX_FEED_LIMIT", "30"))
MAX_POSTS_PER_DAY = safe_int(os.environ.get("MAX_POSTS_PER_DAY", "3"), 3, 1, 24)
COOLDOWN_ON_ERROR_MINUTES = safe_int(os.environ.get("COOLDOWN_ON_ERROR_MINUTES", "30"), 30, 5, 1440)

# Duplicate detection
BLOCK_DUPLICATE_TOPICS = os.environ.get("BLOCK_DUPLICATE_TOPICS", "true").lower() == "true"
DUPLICATE_WINDOW_DAYS = safe_int(os.environ.get("DUPLICATE_WINDOW_DAYS", "7"), 7, 1, 90)

# Metrics tracking
TRACK_METRICS = os.environ.get("TRACK_METRICS", "true").lower() == "true"
METRICS_FILE = os.environ.get("METRICS_FILE", "metrics.json")

# Notifications
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")
NOTIFY_ON_SUCCESS = os.environ.get("NOTIFY_ON_SUCCESS", "false").lower() == "true"
NOTIFY_ON_FAILURE = os.environ.get("NOTIFY_ON_FAILURE", "true").lower() == "true"

# Link processing
ADD_UTM_PARAMS = os.environ.get("ADD_UTM_PARAMS", "false").lower() == "true"
SHORTEN_LINKS = os.environ.get("SHORTEN_LINKS", "false").lower() == "true"
UTM_SOURCE = os.environ.get("UTM_SOURCE", "linkedin")
UTM_MEDIUM = os.environ.get("UTM_MEDIUM", "social")
UTM_CAMPAIGN = os.environ.get("UTM_CAMPAIGN", "devops-automation")

# Safety controls
KILL_SWITCH = os.environ.get("KILL_SWITCH", "false").lower() == "true"
REQUIRE_MANUAL_APPROVAL = os.environ.get("REQUIRE_MANUAL_APPROVAL", "false").lower() == "true"

SESSION = requests.Session()

# --- Helper: clip ---
def clip(text, max_chars, preserve_hashtags=False):
    """Clip text to max_chars, optionally preserving hashtags at the end."""
    if len(text) <= max_chars:
        return text
    if preserve_hashtags:
        parts = text.split("\n")
        hashtags = [line for line in parts if line.strip().startswith("#")]
        non_hashtags = [line for line in parts if not line.strip().startswith("#")]
        clipped = "\n".join(non_hashtags)
        if len(clipped) > max_chars:
            clipped = clipped[:max_chars].rstrip()
        if hashtags:
            return f"{clipped}\n" + "\n".join(hashtags)
        return clipped
    return text[:max_chars].rstrip()

# --- Helper: get_hashtags ---
def get_hashtags(max_count=None, context_tags=None):
    """Return a string of hashtags, optionally including context-specific tags."""
    tags = list(HASHTAGS)
    if context_tags:
        tags = list(dict.fromkeys(context_tags + tags))
    random.shuffle(tags)
    if max_count:
        tags = tags[:max_count]
    return " ".join(tags)

# --- Helper: get_emoji ---
def get_emoji(name):
    emoji_map = {
        "hook": "🚀",
        "arrow": "➡️",
        "bullet": "•",
        "star": "⭐",
        "fire": "🔥",
        "lightbulb": "💡",
        "thread": "🧵",
    }
    return emoji_map.get(name, "")

# --- Helper: build_digest_post ---
def build_digest_post(items):
    """Build the classic multi-link digest post with varied, dynamic, and engaging styles."""
    hook = random.choice(FORMAT_HOOKS.get("digest", HOOKS))
    cta = random.choice(FORMAT_CTAS.get("digest", CTAS))
    why_line = random.choice(WHY_LINES)
    post_style = get_random_post_style()
    style_config = POST_STYLES[post_style] if 'POST_STYLES' in globals() else {}
    digest_styles = ["numbered", "bulleted", "themed", "brief", "detailed"]
    digest_style = random.choice(digest_styles)
    if digest_style == "brief":
        chosen = items[:min(3, len(items))]
        show_snippets = False
    elif digest_style == "detailed":
        chosen = items[:min(4, len(items))]
        show_snippets = True
    else:
        chosen = items[:min(5, len(items))]
        show_snippets = random.random() > 0.5
    lines = [hook, get_dynamic_persona("digest", " ".join([item["title"] for item in items[:5]])), ""]
    section_headers = [
        "Today's high-signal reads:",
        "This week's standouts:",
        "What stands out:",
        "Signal vs noise:",
        "Worth your time:",
        "Key developments:",
        "Industry pulse:"
    ]
    lines.append(random.choice(section_headers))
    for i, item in enumerate(chosen, 1):
        takeaway = remix_title(item["title"]) if 'remix_title' in globals() else item["title"]
        source = item.get("source", "").strip()
        if digest_style == "numbered":
            if show_snippets:
                snippet = summarize_snippet(item.get("summary", "")) if 'summarize_snippet' in globals() else item.get("summary", "")
                if snippet:
                    value = ai_generate_value_line(item.get("title", ""), snippet)
                    src = ""
                    link_display = f"\n   🔗 {item.get('link', '')}" if item.get('link') and style_config.get("include_links", True) else ""
                    lines.append(f"{i}. {takeaway}{src}\n   ↳ {snippet}\n   ↳ {value}{link_display}\n")
                else:
                    value = ai_generate_value_line(item.get("title", ""), "")
                    src = ""
                    link_display = f"\n   🔗 {item.get('link', '')}" if item.get('link') and style_config.get("include_links", True) else ""
                    lines.append(f"{i}. {takeaway}{src}\n   ↳ {value}{link_display}\n")
            else:
                value = ai_generate_value_line(item.get("title", ""), "")
                src = ""
                link_display = f"\n   🔗 {item.get('link', '')}" if item.get('link') and style_config.get("include_links", True) else ""
                lines.append(f"{i}. {takeaway}{src}\n   → {value}{link_display}\n")
        elif digest_style == "bulleted":
            value = ai_generate_value_line(item.get("title", ""), item.get("summary", ""))
            bullet = get_emoji("bullet")
            src = ""
            link_display = f"\n   🔗 {item.get('link', '')}" if item.get('link') and style_config.get("include_links", True) else ""
            lines.append(f"{bullet} {takeaway}{src}\n   {value}{link_display}\n")
        elif digest_style == "themed":
            emoji_map = {
                "kubernetes": "☸️", "security": "🛡️", "cloud": "☁️", 
                "observability": "📊", "devops": "🔧", "sre": "🚨"
            }
            theme_emoji = ""
            for theme, emoji in emoji_map.items():
                if theme in (item.get("title", "") + item.get("summary", "")).lower():
                    theme_emoji = emoji + " "
                    break
            value = ai_generate_value_line(item.get("title", ""), "")
            src = ""
            link_display = f"\n🔗 {item.get('link', '')}" if item.get('link') and style_config.get("include_links", True) else ""
            lines.append(f"{theme_emoji}{takeaway}{src}\n{value}{link_display}\n")
        elif digest_style == "brief":
            src = ""
            link_display = f" {item.get('link', '')}" if item.get('link') and style_config.get("include_links", True) else ""
            lines.append(f"• {takeaway}{src}{link_display}\n")
        else:  # detailed
            snippet = summarize_snippet(item.get("summary", "")) if 'summarize_snippet' in globals() else item.get("summary", "")
            value = ai_generate_value_line(item.get("title", ""), snippet)
            src = ""
            link_display = f"\n   🔗 {item.get('link', '')}" if item.get('link') and style_config.get("include_links", True) else ""
            if snippet:
                lines.append(f"{i}. {takeaway}{src}\n   Context: {snippet}\n   Impact: {value}{link_display}\n")
            else:
                lines.append(f"{i}. {takeaway}{src}\n   {value}{link_display}\n")
    if digest_style != "brief" and random.random() > 0.3:
        lines.extend(["", f"Why this matters: {why_line}"])
    lines.extend([
        "",
        random.choice(cta_templates),
        random.choice(subscribe_templates),
        random.choice(playbook_templates),
        "",
        random.choice(hashtag_templates),
        "",
        f"❓ {footer_question}"
    ])
    post = "\n".join(lines)
    return clip(post, MAX_POST_CHARS)

# -------------------------------------------------
# GROWTH PLAN INTEGRATION
# -------------------------------------------------

def load_growth_plan() -> Optional[Dict]:
    """Load the weekly growth plan generated by advanced_growth_strategies.py"""
    try:
        if not os.path.exists(GROWTH_PLAN_FILE):
            logger.info(f"No growth plan file found at {GROWTH_PLAN_FILE}")
            return None
        
        with open(GROWTH_PLAN_FILE, 'r', encoding='utf-8') as f:
            plan = json.load(f)
        
        logger.info(f"✅ Loaded growth plan with {len(plan.get('post_ideas', []))} post ideas")
        return plan
    except Exception as e:
        logger.warning(f"Failed to load growth plan: {e}")
        return None


def get_growth_plan_content() -> Optional[Dict]:
    """Get content from growth plan for posting.
    
    Returns a dict with:
    - title: Post title/topic
    - hook: Engagement hook
    - cta: Call to action
    - hashtags: List of hashtags
    - category: Content category
    - content_framework: Structure for the post
    """
    if not USE_GROWTH_PLAN:
        return None
    
    # Random chance to use growth plan (to maintain variety with RSS content)
    if random.random() > GROWTH_PLAN_PROBABILITY:
        logger.info(f"Skipping growth plan this run (probability: {GROWTH_PLAN_PROBABILITY})")
        return None
    
    plan = load_growth_plan()
    if not plan:
        return None
    
    post_ideas = plan.get('post_ideas', [])
    if not post_ideas:
        logger.info("No post ideas in growth plan")
        return None
    
    # Pick a random idea from the plan
    idea = random.choice(post_ideas)
    
    logger.info(f"📝 Using growth plan idea: {idea.get('title', 'Unknown')}")
    logger.info(f"   Category: {idea.get('category', 'Unknown')}")
    logger.info(f"   Hook: {idea.get('hook', 'None')[:50]}...")
    
    return idea


def format_post_content(text: str) -> str:
    """Clean up and standardize post formatting for LinkedIn.
    
    Ensures consistent:
    - Bullet point style using configured emoji style
    - Proper spacing between sections
    - No excessive blank lines
    - Clean paragraph breaks
    - Proper emoji placement
    """
    if not text:
        return text
    
    # Get the bullet style from emoji settings
    bullet = get_emoji("bullet") if 'get_emoji' in dir() else "•"
    if not bullet:
        bullet = "•"
    
    lines = text.split('\n')
    formatted_lines = []
    prev_was_blank = False
    
    for line in lines:
        stripped = line.strip()
        
        # Standardize bullet points to configured style
        if stripped.startswith(('- ', '* ', '– ', '— ', '• ')):
            content = stripped[2:].strip()
            stripped = f'{bullet} {content}'
        elif stripped.startswith('-') and len(stripped) > 1 and stripped[1] not in '-=':
            content = stripped[1:].strip()
            stripped = f'{bullet} {content}'
        # Handle emoji bullets like 📍, 🔹, ▪️ - keep them as-is
        elif len(stripped) > 2 and stripped[0] in '📍🔹▪️✓✅→➡️🔸◾◽▫️':
            pass  # Keep emoji bullets as-is
        
        # Prevent more than one consecutive blank line
        if not stripped:
            if prev_was_blank:
                continue  # Skip extra blank lines
            prev_was_blank = True
            formatted_lines.append('')
        else:
            prev_was_blank = False
            formatted_lines.append(stripped)
    
    # Remove leading/trailing blank lines
    while formatted_lines and not formatted_lines[0]:
        formatted_lines.pop(0)
    while formatted_lines and not formatted_lines[-1]:
        formatted_lines.pop()
    
    return '\n'.join(formatted_lines)


def clean_ai_hashtags(text: str) -> str:
    """Remove improperly formatted hashtags from AI-generated content.
    
    AI models sometimes output 'hashtag#tag' instead of just '#tag'.
    This function cleans up such formatting issues and removes any
    hashtag lines since they'll be added separately.
    """
    if not text:
        return text
    
    # Replace 'hashtag#word' with just '#word'
    text = re.sub(r'\bhashtag#(\w+)', r'#\1', text, flags=re.IGNORECASE)
    
    # Remove lines that are only hashtags (we add them separately)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Skip lines that are only hashtags
        if stripped and all(word.startswith('#') for word in stripped.split()):
            continue
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def remove_first_person_pronouns(text: str) -> str:
    """Remove first-person pronouns from AI-generated content for authoritative tone.
    
    Replaces common first-person patterns with third-person alternatives.
    """
    if not text:
        return text
    
    # Replace common first-person patterns with authoritative alternatives
    replacements = [
        # "I" patterns - comprehensive coverage
        (r'\bI recall\b', 'Consider'),
        (r'\bI remember\b', 'Consider'),
        (r'\bI\'ve seen\b', 'Experience shows'),
        (r'\bI have seen\b', 'Experience shows'),
        (r'\bI\'ve learned\b', 'The lesson is clear:'),
        (r'\bI have learned\b', 'The lesson is clear:'),
        (r'\bI\'ve found\b', 'Evidence shows'),
        (r'\bI have found\b', 'Evidence shows'),
        (r'\bI\'ve noticed\b', 'It\'s notable that'),
        (r'\bI have noticed\b', 'It\'s notable that'),
        (r'\bI\'ve observed\b', 'Observations show'),
        (r'\bI\'ve worked\b', 'Working'),
        (r'\bI have worked\b', 'Working'),
        (r'\bI\'ve been\b', 'Having been'),
        (r'\bI\'ve helped\b', 'Helping teams'),
        (r'\bI\'ve built\b', 'Building'),
        (r'\bI\'ve implemented\b', 'Implementing'),
        (r'\bI believe\b', 'The reality is'),
        (r'\bI think\b', 'The evidence suggests'),
        (r'\bI know\b', 'It\'s clear'),
        (r'\bI love\b', 'The best part:'),
        (r'\bI hate\b', 'The downside:'),
        (r'\bI recommend\b', 'The recommendation:'),
        (r'\bI suggest\b', 'The suggestion:'),
        (r'\bI prefer\b', 'The preference:'),
        (r'\bI use\b', 'Teams use'),
        (r'\bI used\b', 'Teams have used'),
        (r'\bI would\b', 'One would'),
        (r'\bI could\b', 'One could'),
        (r'\bI should\b', 'One should'),
        (r'\bI can\b', 'One can'),
        (r'\bI will\b', 'This will'),
        (r'\bI want\b', 'The goal is'),
        (r'\bI need\b', 'The need is'),
        (r'\bI realized\b', 'It became clear'),
        (r'\bIn my experience\b', 'In practice'),
        (r'\bIn my view\b', 'The data shows'),
        (r'\bIn my opinion\b', 'The evidence suggests'),
        (r'\bFrom my experience\b', 'From real-world experience'),
        (r'\bFrom my perspective\b', 'From a practical perspective'),
        (r'\bI\'m\b', 'One is'),
        (r'\bI am\b', 'One is'),
        (r'\bI was\b', 'The situation was'),
        (r'\bI had\b', 'There was'),
        (r'\bI did\b', 'The approach was'),
        (r'\bwhat I\b', 'what teams'),
        (r'\bWhat I\b', 'What teams'),
        (r'\bthat I\b', 'that teams'),
        (r'\bThat I\b', 'That teams'),
        (r'\bwhen I\b', 'when teams'),
        (r'\bWhen I\b', 'When teams'),
        (r'\bif I\b', 'if teams'),
        (r'\bIf I\b', 'If teams'),
        (r'\bbefore I\b', 'before teams'),
        (r'\bafter I\b', 'after teams'),
        (r'\btells me\b', 'indicates'),
        (r'\bshowed me\b', 'demonstrated'),
        (r'\btaught me\b', 'demonstrated'),
        (r'\bhelped me\b', 'proved helpful'),
        
        # "We/Our/Us" patterns  
        (r'\bWe implemented\b', 'The implementation'),
        (r'\bWe realized\b', 'It became clear'),
        (r'\bWe identified\b', 'Analysis identified'),
        (r'\bWe found\b', 'The findings show'),
        (r'\bWe learned\b', 'The lesson:'),
        (r'\bWe needed\b', 'The need was'),
        (r'\bWe were\b', 'The team was'),
        (r'\bWe had\b', 'There was'),
        (r'\bWe built\b', 'Building'),
        (r'\bWe created\b', 'Creating'),
        (r'\bWe use\b', 'Teams use'),
        (r'\bWe used\b', 'Teams used'),
        (r'\bWe can\b', 'Teams can'),
        (r'\bWe should\b', 'Teams should'),
        (r'\bWe need\b', 'Teams need'),
        (r'\bWe want\b', 'The goal is'),
        (r'\bWe recommend\b', 'The recommendation:'),
        (r'\bWe suggest\b', 'The suggestion:'),
        (r'\bwe\'ve\b', 'teams have'),
        (r'\bWe\'ve\b', 'Teams have'),
        (r'\bour team\b', 'the team'),
        (r'\bOur team\b', 'The team'),
        (r'\bour process\b', 'the process'),
        (r'\bOur process\b', 'The process'),
        (r'\bour approach\b', 'the approach'),
        (r'\bOur approach\b', 'The approach'),
        (r'\bour solution\b', 'the solution'),
        (r'\bOur solution\b', 'The solution'),
        (r'\bour experience\b', 'industry experience'),
        (r'\bOur experience\b', 'Industry experience'),
        (r'\bour data\b', 'the data'),
        (r'\bOur data\b', 'The data'),
        (r'\bour findings\b', 'the findings'),
        (r'\bOur findings\b', 'The findings'),
        (r'\bfor us\b', 'for teams'),
        (r'\bFor us\b', 'For teams'),
        (r'\bto us\b', 'to teams'),
        (r'\bhelps us\b', 'helps teams'),
        (r'\bshows us\b', 'shows'),
        (r'\btells us\b', 'indicates'),
        (r'\bgave us\b', 'provided'),
        
        # "My" patterns
        (r'\bmy experience\b', 'industry experience'),
        (r'\bMy experience\b', 'Industry experience'),
        (r'\bmy team\b', 'the team'),
        (r'\bMy team\b', 'The team'),
        (r'\bmy approach\b', 'the approach'),
        (r'\bMy approach\b', 'The approach'),
        (r'\bmy recommendation\b', 'the recommendation'),
        (r'\bMy recommendation\b', 'The recommendation'),
        (r'\bmy advice\b', 'the advice'),
        (r'\bMy advice\b', 'The advice'),
        (r'\bmy take\b', 'the take'),
        (r'\bMy take\b', 'The take'),
        (r'\bmy view\b', 'the view'),
        (r'\bMy view\b', 'The view'),
        (r'\bmy opinion\b', 'the opinion'),
        (r'\bMy opinion\b', 'The opinion'),
        (r'\bmy perspective\b', 'a practical perspective'),
        (r'\bMy perspective\b', 'A practical perspective'),
        (r'\bmy observation\b', 'the observation'),
        (r'\bMy observation\b', 'The observation'),
        
        # "Me" patterns
        (r'\bto me\b', 'notably'),
        (r'\bfor me\b', 'in practice'),
        (r'\basks me\b', 'the question arises:'),
        (r'\basked me\b', 'the question arose:'),
    ]
    
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE if pattern[0] != '(' else 0)
    
    return text


def build_growth_plan_post(idea: Dict) -> str:
    """Build a LinkedIn post from a growth plan idea using AI."""
    
    title = idea.get('title', 'DevOps Insights')
    hook = idea.get('hook', '')
    cta = idea.get('cta', 'What are your thoughts?')
    hashtags = idea.get('hashtags', ['#devops', '#sre'])
    category = idea.get('category', 'thought_leadership')
    framework = idea.get('content_framework', {})
    
    # Generate the full post content using AI
    structure = framework.get('structure', [])
    tone = framework.get('tone', 'professional')
    
    prompt = f"""Write a compelling LinkedIn post about: "{title}"

Opening Hook: {hook}

Structure to follow:
{chr(10).join(f"- {point}" for point in structure)}

FORMATTING REQUIREMENTS:
- Start with the opening hook as the FIRST line
- Add ONE blank line between each section/paragraph
- Use short paragraphs (2-3 sentences max)
- For lists, use bullet points with "•" symbol (not dashes or asterisks)
- Each bullet point should be on its own line
- Add a blank line before and after any list
- End with the call-to-action on its own line

CONTENT REQUIREMENTS:
- Tone: {tone}, authoritative, industry-leader perspective
- Length: 800-1200 characters total
- CRITICAL: NEVER use first-person pronouns. FORBIDDEN words: I, I'm, I've, I'll, me, my, mine, we, we're, we've, our, ours, us
- Write from an objective, authoritative third-person perspective ONLY
- Use phrases like: "Teams often find...", "The data shows...", "Experience reveals...", "Evidence suggests...", "The reality is...", "Production experience shows..."
- NEVER start sentences with "I" or use phrases like "In my experience", "I believe", "I think", "I've seen"
- End with the call-to-action: {cta}
- Do NOT include hashtags (they'll be added separately)

Write the post now:"""

    # Try AI providers to generate the full post
    ai_content = None
    
    if GROQ_API_KEY:
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8,
                    "max_tokens": 800
                },
                timeout=30
            )
            if response.status_code == 200:
                ai_content = response.json()['choices'][0]['message']['content'].strip()
                logger.info("✅ Generated post content using Groq AI")
        except Exception as e:
            logger.warning(f"Groq AI generation failed: {e}")
    
    # Try Gemini as fallback
    if not ai_content and GEMINI_API_KEY:
        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )
            if response.status_code == 200:
                ai_content = response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
                logger.info("✅ Generated post content using Gemini AI")
        except Exception as e:
            logger.warning(f"Gemini AI generation failed: {e}")
    
    # Build the post
    if ai_content:
        # Clean up improperly formatted hashtags from AI output
        ai_content = clean_ai_hashtags(ai_content)
        # Remove first-person pronouns for authoritative tone
        ai_content = remove_first_person_pronouns(ai_content)
        # AI generated content - split into lines to preserve formatting
        post_lines = ai_content.split('\n')
        # Clean up: remove leading/trailing whitespace from each line, but keep empty lines for spacing
        post_lines = [line.rstrip() for line in post_lines]
        # Remove completely empty lines at start and end
        while post_lines and not post_lines[0].strip():
            post_lines.pop(0)
        while post_lines and not post_lines[-1].strip():
            post_lines.pop()
    else:
        # Fallback: Build post manually from components
        logger.warning("Using fallback post generation (no AI response)")
        post_lines = [
            hook,
            "",
            f"Key insights on {title.lower()}:",
            ""
        ]
        
        # Add structure points as bullet points with proper formatting
        for i, point in enumerate(structure[:4], 1):
            post_lines.append(f"• {point}")
        
        post_lines.extend([
            "",
            cta
        ])
    
    # Add persona if enabled
    if INCLUDE_PERSONA:
        persona = get_dynamic_persona(category, content=title)
        if persona:
            post_lines.insert(0, persona)
            post_lines.insert(1, "")
    
    # Add subscription CTA
    subscription_cta = get_subscription_cta()
    if subscription_cta:
        post_lines.extend(["", subscription_cta])
    
    # Add hashtags
    if isinstance(hashtags, list):
        hashtag_str = " ".join(hashtags[:MAX_HASHTAGS])
    else:
        hashtag_str = get_hashtags()
    post_lines.extend(["", hashtag_str])
    
    post_text = "\n".join(post_lines)
    # Apply final formatting cleanup
    post_text = format_post_content(post_text)
    return clip(post_text, MAX_POST_CHARS)


def normalize_author_urn(value: str) -> str:
    """Normalize any author identifier into a usable URN.

    - Accepts full URNs for member/person.
    - Accepts raw numeric IDs (coerced to member URN).
    - Accepts non-numeric IDs (e.g., OpenID `sub`) and coerces to person URN.
    """
    if not value:
        return ""
    v = str(value).strip().strip('"').strip("'")
    if v.startswith("urn:li:member:") or v.startswith("urn:li:person:"):
        return v
    if v.isdigit():
        return f"urn:li:member:{v}"
    # Non-numeric identifiers (like OpenID sub) work with person URNs
    return f"urn:li:person:{v}"


def resolve_author_urn(access_token: str) -> str:
    """Resolve LinkedIn author URN.
    
    Priority:
    1) LINKEDIN_AUTHOR_URN override (full URN)
    2) LINKEDIN_MEMBER_ID override (numeric)
    3) Auto-detect from token via /v2/me or /v2/userinfo
    """
    explicit_urn = normalize_author_urn(os.environ.get("LINKEDIN_AUTHOR_URN"))
    member_urn = normalize_author_urn(os.environ.get("LINKEDIN_MEMBER_ID"))

    token_id = get_token_member_id()
    token_urn = normalize_author_urn(token_id) if token_id else ""

    if explicit_urn:
        print(f"Using LINKEDIN_AUTHOR_URN override: {explicit_urn}")
        if token_urn and explicit_urn != token_urn:
            print(f"⚠️  Override URN mismatches token member {token_id}. Using token to avoid 403.")
            return token_urn
        return explicit_urn

    if member_urn:
        print(f"Using LINKEDIN_MEMBER_ID override: {member_urn}")
        if token_urn and member_urn != token_urn:
            print(f"⚠️  LINKEDIN_MEMBER_ID mismatches token member {token_id}. Using token to avoid 403.")
            return token_urn
        return member_urn

    if token_urn:
        return token_urn

    # Return a safe fallback instead of crashing
    logger.error("❌ ERROR: Could not resolve author URN")
    logger.error("   - No LINKEDIN_MEMBER_ID or LINKEDIN_AUTHOR_URN set")
    logger.error("   - Token detection failed (needs 'openid' and 'profile' scopes)")
    logger.error("   - Set LINKEDIN_MEMBER_ID as a GitHub secret with your numeric member ID")
    
    # Try to use a default format - this prevents crashes
    if ACCESS_TOKEN:
        logger.warning("⚠️  Using fallback URN format - this may cause API failures")
        return "urn:li:member:0"  # Fallback that won't crash the app
    
    raise RuntimeError("Cannot resolve LinkedIn author URN - check token scopes and configuration")


# Try to detect token's member ID from /v2/me
def get_token_member_id():
    """Try /v2/me then /v2/userinfo to get token's member ID."""
    try:
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": API_VERSION,
        }
        
        # Try /v2/me first
        r = requests.get(
            "https://api.linkedin.com/v2/me?projection=(id)",
            headers=headers,
            timeout=5,
        )
        if r.status_code == 200:
            data = r.json()
            token_id = data.get("id")
            if token_id:
                print(f"✓ Detected identifier from /v2/me: {token_id}")
                return str(token_id)
        else:
            print(f"⚠️  /v2/me returned {r.status_code}, trying /v2/userinfo...")

        # Fallback to /v2/userinfo for tokens with openid
        r = requests.get(
            "https://api.linkedin.com/v2/userinfo",
            headers=headers,
            timeout=5,
        )
        if r.status_code == 200:
            data = r.json()
            name = data.get("name", "Unknown")
            sub_val = data.get("sub", "")
            if sub_val:
                print(f"✓ Detected identifier from /v2/userinfo for user {name}: {sub_val}")
                return str(sub_val)
        else:
            print(f"❌ /v2/userinfo returned {r.status_code}: {r.text}")
    except Exception as e:
        print(f"❌ Token detection failed: {e}")
    return None

# Resolve author URN (from overrides or auto-detect)
print("Resolving LinkedIn author...")
try:
    AUTHOR_URN = resolve_author_urn(ACCESS_TOKEN)
    print(f"✓ Using author URN: {AUTHOR_URN}\n")
except Exception as e:
    logger.error(f"❌ Failed to resolve author URN: {e}")
    logger.error("LinkedIn posting will not work without proper URN configuration")
    AUTHOR_URN = None  # Will cause graceful failure later

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0",
    "LinkedIn-Version": API_VERSION,
}

# -------------------------------------------------
# CONFIG
# -------------------------------------------------

STATE_FILE = "posted_links.json"

NEWS_SOURCES = [
    "https://kubernetes.io/feed.xml",
    "https://www.cncf.io/feed/",
    "https://aws.amazon.com/blogs/devops/feed/",
    "https://azure.microsoft.com/en-us/blog/feed/",
    "https://www.hashicorp.com/blog/feed.xml",
    "https://netflixtechblog.medium.com/feed",
    "https://engineering.atspotify.com/feed/",
    "https://about.gitlab.com/atom.xml",
    "https://martinfowler.com/feed.atom",
    "https://www.docker.com/blog/feed/",
    # Major Tech Companies
    "https://github.blog/feed/",
    "https://blog.jetbrains.com/feed/",
    "https://stackoverflow.blog/feed/",
    "https://blog.cloudflare.com/rss/",
    "https://blog.mongodb.com/rss.xml",
    "https://redis.io/blog/rss.xml",
    "https://blog.elastic.co/rss.xml",
    "https://blog.nginx.org/feed.xml",
    # News & Industry Sites
    "https://techcrunch.com/category/enterprise/feed/",
    "https://www.infoq.com/rss/rss.xml",
    "https://devclass.com/feed/",
    "https://thenewstack.io/feed/",
    "https://www.darkreading.com/rss_simple.asp",
    "https://www.zdnet.com/topic/security/rss.xml",
    "https://www.bleepingcomputer.com/feed/"
]

# Curated RSS packs (reliable engineering sources). You can add/override via EXTRA_NEWS_SOURCES.
PACK_SOURCES: Dict[str, list] = {
    "kubernetes": [
        "https://kubernetes.io/feed.xml",
        "https://www.cncf.io/feed/",
        "https://blog.helm.sh/rss.xml",
        "https://istio.io/latest/blog/index.xml",
        "https://linkerd.io/blog/index.xml",
        "https://fluxcd.io/blog/index.xml",
        "https://argo-cd.readthedocs.io/en/latest/blog/rss.xml",
        "https://blog.kubesphere.io/rss.xml",
    ],
    "sre": [
        "https://aws.amazon.com/blogs/mt/feed/",
        "https://blog.google/products/google-cloud/rss/",
        "https://grafana.com/blog/index.xml",
        "https://prometheus.io/blog/index.xml",
        "https://blog.datadog.com/rss.xml",
        "https://blog.newrelic.com/feed/",
        "https://www.honeycomb.io/blog/rss.xml",
        "https://blog.pagerduty.com/feed/",
        "https://blog.uptimerobot.com/rss/",
    ],
    "platform": [
        "https://www.cncf.io/feed/",
        "https://www.hashicorp.com/blog/feed.xml",
        "https://engineering.atspotify.com/feed/",
        "https://netflixtechblog.medium.com/feed/",
        "https://about.gitlab.com/atom.xml",
        "https://eng.uber.com/rss/",
        "https://medium.com/airbnb-engineering/feed",
        "https://blog.x.com/engineering/en_us.rss",
        "https://engineering.fb.com/feed/",
        "https://eng.lyft.com/feed",
        "https://medium.com/pinterest-engineering/feed",
        "https://slack.engineering/feed/",
        "https://dropbox.tech/feed",
        "https://blog.coinbase.com/feed",
        "https://medium.com/paypal-tech/feed",
        "https://medium.com/shopify-engineering/feed",
        "https://github.blog/category/engineering/feed/",
    ],
    "devops": [
        "https://aws.amazon.com/blogs/devops/feed/",
        "https://azure.microsoft.com/en-us/blog/feed/",
        "https://www.docker.com/blog/feed/",
        "https://cloud.google.com/blog/products/devops-sre/rss",
        "https://blog.jenkins.io/rss.xml",
        "https://about.gitlab.com/blog/categories/ci-cd/atom.xml",
        "https://github.blog/category/engineering/feed/",
        "https://blog.circleci.com/feed.xml",
        "https://www.atlassian.com/blog/rss.xml",
        "https://blog.terraform.io/rss.xml",
        "https://blog.ansible.com/rss.xml",
        "https://blog.chef.io/feed/",
        "https://puppet.com/blog/rss.xml",
    ],
    "architecture": [
        "https://martinfowler.com/feed.atom",
        "https://www.infoq.com/feed/",
        "https://blog.pragmaticengineer.com/rss/",
        "https://highscalability.com/rss.xml",
        "https://microservices.io/feed.xml",
        "https://12factor.net/feed.xml",
        "https://blog.cleancoder.com/uncle-bob/feed.xml",
        "https://blog.acolyer.org/feed/",
        "https://architecturenotes.co/feed/",
        "https://blog.systemdesign.one/feed",
    ],
    "security": [
        "https://www.cisa.gov/news.xml",
        "https://krebsonsecurity.com/feed/",
        "https://blog.cloudflare.com/tag/security/rss/",
        "https://blog.qualys.com/feed",
        "https://blog.rapid7.com/rss/",
        "https://blog.checkpoint.com/feed/",
        "https://www.trendmicro.com/en_us/research/rss.xml",
        "https://www.crowdstrike.com/blog/feed/",
        "https://unit42.paloaltonetworks.com/feed/",
        "https://blogs.microsoft.com/microsoftsecure/feed/",
        "https://googleprojectzero.blogspot.com/feeds/posts/default?alt=rss",
        "https://blog.mozilla.org/security/feed/",
        "https://www.csoonline.com/index.rss",
        "https://feeds.feedburner.com/eset/blog",
    ],
    "devsecops": [
        "https://snyk.io/blog/feed/",
        "https://www.aquasec.com/feed/",
        "https://www.paloaltonetworks.com/blog/prisma-cloud/feed/",
        "https://www.sonarsource.com/blog/rss.xml",
        "https://www.veracode.com/blog/rss.xml",
        "https://www.mend.io/blog/feed/",
        "https://checkmarx.com/blog/feed/",
        "https://blog.gitguardian.com/feed/",
        "https://blog.sigstore.dev/rss.xml",
        "https://falco.org/blog/rss.xml",
        "https://blog.openpolicyagent.org/feed",
    ],
    "finops": [
        "https://www.finops.org/feed/",
        "https://blog.kubecost.com/rss.xml",
        "https://aws.amazon.com/blogs/mt/feed/",
    ],
    "observability": [
        "https://grafana.com/blog/index.xml",
        "https://prometheus.io/blog/index.xml",
        "https://blog.datadog.com/rss.xml",
        "https://blog.newrelic.com/feed/",
        "https://www.honeycomb.io/blog/rss.xml",
        "https://blog.lightstep.com/feed",
        "https://blog.jaegertracing.io/rss.xml",
        "https://blog.elastic.co/category/observability/rss.xml",
        "https://blog.splunk.com/feed.xml",
        "https://blog.logz.io/feed",
    ],
    "cicd": [
        "https://blog.jenkins.io/rss.xml",
        "https://about.gitlab.com/blog/categories/ci-cd/atom.xml",
        "https://github.blog/category/actions/feed/",
        "https://blog.circleci.com/feed.xml",
        "https://blog.travis-ci.com/feed.xml",
        "https://blog.buildkite.com/feed.xml",
        "https://codefresh.io/blog/feed/",
        "https://blog.drone.io/feed.xml",
        "https://blog.tekton.dev/rss.xml",
    ],
    "cloud_native": [
        "https://www.cncf.io/feed/",
        "https://blog.openshift.com/feed/",
        "https://blog.rancher.com/rss.xml",
        "https://blog.vmware.com/cloudnative/rss.xml",
        "https://blog.crossplane.io/rss.xml",
        "https://blog.knative.dev/rss.xml",
        "https://blog.dapr.io/rss.xml",
        "https://blog.openfaas.com/rss.xml",
    ],
}

# Post style variations for more diversity
POST_STYLES = {
    "minimal": {
        "include_links": False,
        "include_source": False,
        "short_form": True,
        "focus_insights": True
    },
    "detailed": {
        "include_links": True,
        "include_source": True,
        "short_form": False,
        "focus_insights": False
    },
    "link_heavy": {
        "include_links": True,
        "include_source": True,
        "inline_links": True,
        "multiple_sources": True
    },
    "discussion": {
        "include_links": False,
        "focus_question": True,
        "conversational": True
    },
    "news_brief": {
        "include_links": True,
        "news_style": True,
        "brief_summary": True
    }
}

# Different ways to present links
LINK_STYLES = [
    "Read more: {link}",
    "Full story: {link}", 
    "Deep dive: {link}",
    "Source: {link}",
    "Details here: {link}",
    "Continue reading: {link}",
    "📖 {link}",
    "🔗 {link}",
    "Learn more → {link}",
    "👉 {link}"
]

# Alternative post endings (sometimes no links at all)
POST_ENDINGS = [
    "links",  # Include links
    "discussion",  # Just end with question
    "call_to_action",  # Strong CTA
    "minimal",  # Just hashtags
    "community"  # Ask for community input
]

def get_random_post_style():
    """Get a random post style configuration."""
    return random.choice(list(POST_STYLES.keys()))

def should_include_links(style_name, post_format):
    """Determine if links should be included based on style and format."""
    # If ALWAYS_INCLUDE_LINKS is True (default), guarantee every post has links
    if ALWAYS_INCLUDE_LINKS:
        return True
    
    # Fallback to high probability (but not 100%) for variety when disabled
    style = POST_STYLES.get(style_name, POST_STYLES["detailed"])
    
    # Higher probabilities than original, but still some randomness
    if post_format in ["digest", "case_study"]:
        return random.random() > 0.05  # 95% chance (was 70%)
    elif post_format in ["deep_dive"]:
        return random.random() > 0.10  # 90% chance (was 60%)
    elif post_format in ["hot_take", "lessons"]:
        return random.random() > 0.15  # 85% chance (was 50%)
    # Default to style setting or True
    return style.get("include_links", True)

def format_links_section(links, style_name):
    """Format links section with variety."""
    if not links:
        return []
    
    ending_style = random.choice(POST_ENDINGS)
    
    # Always include links, but still respect the INCLUDE_LINKS global setting
    if not INCLUDE_LINKS:
        return []  # Only skip if explicitly disabled
    
    lines = []
    
    # If ending_style is "minimal", use a simple link format instead of no links
    if ending_style == "minimal":
        link_style = random.choice(LINK_STYLES)
        lines.append("")
        if len(links) == 1:
            lines.append(link_style.format(link=links[0]))
        else:
            lines.append("Sources:")
            for i, link in enumerate(links[:3], 1):
                lines.append(f"{i}. {link}")
        return lines
    
    if ending_style == "links":
        # Traditional link style with variation
        link_style = random.choice(LINK_STYLES)
        lines.append("")
        if len(links) == 1:
            lines.append(link_style.format(link=links[0]))
        else:
            lines.append("Sources:")
            for i, link in enumerate(links[:3], 1):
                lines.append(f"{i}. {link}")
    
    elif ending_style == "discussion":
        # End with strong discussion focus, always include key link
        if links:
            lines.extend(["", f"📚 Key resource: {links[0]}"])
    
    elif ending_style == "call_to_action":
        # Strong CTA with embedded link
        if links:
            lines.extend(["", f"💡 Dive deeper into this topic: {links[0]}"])
    
    elif ending_style == "community":
        # Community focused, always include link
        if links:
            lines.extend(["", f"🤝 Join the discussion: {links[0]}"])
    
    # Fallback: if no links were added by the specific ending style, add a default link
    if not lines and links:
        link_style = random.choice(LINK_STYLES)
        lines.extend(["", link_style.format(link=links[0])])
    
    return lines

# Post format types for variety
POST_FORMATS = [
    "digest",        # Classic multi-link digest
    "deep_dive",     # Single topic, longer explanation
    "quick_tip",     # One actionable tip
    "case_study",    # Framed as a case study
    "hot_take",      # Opinion/perspective piece
    "lessons",       # Lessons learned format
]

# Templates for different formats
FORMAT_HOOKS = {
    "digest": [
        "🚀 Signals that move the reliability needle.",
        "🛠️ What high-perf teams are watching this week.",
        "🔥 Cut noise, keep signal: your DevOps digest.",
        "📡 Industry signals worth your attention.",
        "⚡ Latest developments in DevOps and cloud.",
        "🎯 What matters in platform engineering this week.",
        "🌊 Current trends in infrastructure and operations.",
        "📊 Data-driven insights for builders and operators.",
    ],
    "deep_dive": [
        "🔬 Deep dive: one concept worth your time today.",
        "📖 Let's unpack this one properly.",
        "🎓 Today's learning: going deeper on what matters.",
    ],
    "quick_tip": [
        "💡 Quick tip that saves hours.",
        "⚡ 60-second insight for your toolkit.",
        "🎯 One thing to try this week.",
    ],
    "case_study": [
        "📊 Case study: what worked (and what didn't).",
        "🏗️ Real-world example worth studying.",
        "🔍 Breaking down how teams actually solved this.",
    ],
    "hot_take": [
        "🔥 Hot take: unpopular opinion incoming.",
        "💭 Perspective shift on a common practice.",
        "🤔 Rethinking what we thought we knew.",
    ],
    "lessons": [
        "📝 Lessons learned the hard way.",
        "🎯 What teams wish they knew earlier.",
        "💡 Patterns that keep showing up in incidents.",
    ],
}

FORMAT_CTAS = {
    "digest": [
        "What would you prioritize first?",
        "Which one caught your attention?",
        "What did we miss?",
    ],
    "deep_dive": [
        "Have you tried this approach?",
        "What's your experience with this?",
        "How would you adapt this for your team?",
    ],
    "quick_tip": [
        "What's your go-to tip for this?",
        "Drop your favorite shortcut below.",
        "What would you add?",
    ],
    "case_study": [
        "Would this work in your environment?",
        "What's the gap between this and your reality?",
        "Have you seen similar patterns?",
    ],
    "hot_take": [
        "Agree or disagree? Let's debate.",
        "What's the counter-argument?",
        "Is this wrong? Share your perspective.",
    ],
    "lessons": [
        "What's a lesson that changed how you work?",
        "What would you add to this list?",
        "Share your hard-won wisdom below.",
    ],
}

# Context-aware insights based on content topic
CONTEXT_INSIGHTS = {
    "kubernetes": {
        "insights": [
            "Start with resource limits and requests - they're your safety net",
            "RBAC isn't optional - design permissions early and defensively",
            "Monitor cluster state drift - declarative doesn't mean maintenance-free",
            "Network policies before production - assume breach mentality",
            "Pod security standards are table stakes now"
        ],
        "ctas": [
            "How are you handling cluster security at scale?",
            "What's your biggest K8s operational challenge?",
            "Which networking model works best in your environment?",
            "How do you manage multi-tenancy safely?",
            "What monitoring gaps have bitten you?"
        ]
    },
    "security": {
        "insights": [
            "Shift-left security means making security decisions automatic",
            "Identity is the new perimeter - zero trust from day one",
            "Compliance auditing should be continuous, not annual",
            "Threat modeling beats penetration testing every time",
            "Security tooling integration matters more than individual tools"
        ],
        "ctas": [
            "How do you balance security with development velocity?",
            "What security automation has saved you the most time?",
            "Where does your security boundary really exist?",
            "Which compliance requirements drive your architecture?",
            "How do you handle secrets at scale?"
        ]
    },
    "observability": {
        "insights": [
            "Metrics without context are just numbers - add business meaning",
            "Distributed tracing reveals what metrics can't show you",
            "Alert on symptoms, not causes - let humans do root cause analysis",
            "Cardinality explosion will kill your monitoring budget",
            "SLOs drive better architecture than uptime percentages"
        ],
        "ctas": [
            "What observability blind spots have surprised you?",
            "How do you prevent alert fatigue in your team?",
            "Which metrics actually correlate with user experience?",
            "What's your strategy for handling high-cardinality data?",
            "How do you make observability data actionable?"
        ]
    },
    "incident": {
        "insights": [
            "Incident response is about coordination, not just technical fixes",
            "Blameless culture requires deliberate practice and reinforcement",
            "Runbooks should be executable, not just documentation",
            "Communication during incidents needs automation and structure",
            "Post-incident reviews drive more reliability than monitoring"
        ],
        "ctas": [
            "What incident taught you the most about your system?",
            "How do you prevent coordination failures during outages?",
            "What runbook automation has saved you the most time?",
            "How do you balance speed vs thorough incident response?",
            "What patterns do you see in recurring incidents?"
        ]
    },
    "cloud": {
        "insights": [
            "Cloud costs optimize themselves when architecture drives decisions",
            "Multi-cloud means multi-complexity - go deep before going wide",
            "Infrastructure as code is about repeatability, not just automation",
            "Cloud-native patterns work best when you embrace failure",
            "Managed services reduce toil but increase vendor coupling"
        ],
        "ctas": [
            "Which cloud services create the most operational overhead?",
            "How do you handle cross-region complexity?",
            "What cloud costs caught you off guard?",
            "How do you balance managed services vs control?",
            "What multi-cloud challenges have you solved?"
        ]
    },
    "cicd": {
        "insights": [
            "Pipeline as code prevents configuration drift and bus factor issues",
            "Deployment frequency correlates with stability when done right",
            "Feature flags decouple deployment risk from feature risk",
            "Progressive delivery beats blue-green for complex systems",
            "CI/CD observability matters as much as application observability"
        ],
        "ctas": [
            "What CI/CD bottleneck slows your team down most?",
            "How do you handle deployment rollbacks at scale?",
            "Which testing strategy gives you the most confidence?",
            "How do you balance deployment speed with safety?",
            "What pipeline failures taught you the most?"
        ]
    },
    "architecture": {
        "insights": [
            "Distributed systems fail in ways you haven't thought of yet",
            "Conway's Law shapes your architecture more than you realize",
            "Microservices solve organizational problems, not just technical ones",
            "Event-driven architectures require different mental models",
            "System boundaries need continuous reevaluation as teams grow"
        ],
        "ctas": [
            "What architectural decision would you reverse with hindsight?",
            "How do you handle distributed system complexity?",
            "Which architectural patterns work best for your team size?",
            "How do you balance consistency with availability?",
            "What system boundaries have caused the most friction?"
        ]
    },
    "security": {
        "insights": [
            "Security at scale demands constant vigilance. This is significant.",
            "Enterprise security implementations reveal key patterns. Pay attention.",
            "Defense-in-depth strategies show what works."
        ],
        "ctas": [
            "How do you balance security with development velocity?",
            "What security automation has saved you the most time?",
            "Where does your security boundary really exist?",
            "Which compliance requirements drive your architecture?",
            "How do you handle secrets at scale?"
        ]
    },
    "devsecops": {
        "insights": [
            "Shift-left security means making security decisions automatic",
            "Identity is the new perimeter - zero trust from day one",
            "Compliance auditing should be continuous, not annual",
            "Threat modeling beats penetration testing every time",
            "Security tooling integration matters more than individual tools"
        ],
        "ctas": [
            "How do you balance security with development velocity?",
            "What security automation has saved you the most time?",
            "Where does your security boundary really exist?",
            "Which compliance requirements drive your architecture?",
            "How do you handle secrets at scale?"
        ]
    },
    "finops": {
        "insights": [
            "Cloud costs optimize themselves when architecture drives decisions",
            "Multi-cloud means multi-complexity - go deep before going wide",
            "Infrastructure as code is about repeatability, not just automation",
            "Cloud-native patterns work best when you embrace failure",
            "Managed services reduce toil but increase vendor coupling"
        ],
        "ctas": [
            "Which cloud services create the most operational overhead?",
            "How do you handle cross-region complexity?",
            "What cloud costs caught you off guard?",
            "How do you balance managed services vs control?",
            "What multi-cloud challenges have you solved?"
        ]
    },
    "observability": {
        "insights": [
            "Metrics without context are just numbers - add business meaning",
            "Distributed tracing reveals what metrics can't show you",
            "Alert on symptoms, not causes - let humans do root cause analysis",
            "Cardinality explosion will kill your monitoring budget",
            "SLOs drive better architecture than uptime percentages"
        ],
        "ctas": [
            "What observability blind spots have surprised you?",
            "How do you prevent alert fatigue in your team?",
            "Which metrics actually correlate with user experience?",
            "What's your strategy for handling high-cardinality data?",
            "How do you make observability data actionable?"
        ]
    },
    "incident": {
        "insights": [
            "Incident response is about coordination, not just technical fixes",
            "Blameless culture requires deliberate practice and reinforcement",
            "Runbooks should be executable, not just documentation",
            "Communication during incidents needs automation and structure",
            "Post-incident reviews drive more reliability than monitoring"
        ],
        "ctas": [
            "What incident taught you the most about your system?",
            "How do you prevent coordination failures during outages?",
            "What runbook automation has saved you the most time?",
            "How do you balance speed vs thorough incident response?",
            "What patterns do you see in recurring incidents?"
        ]
    },
    "cloud": {
        "insights": [
            "Cloud costs optimize themselves when architecture drives decisions",
            "Multi-cloud means multi-complexity - go deep before going wide",
            "Infrastructure as code is about repeatability, not just automation",
            "Cloud-native patterns work best when you embrace failure",
            "Managed services reduce toil but increase vendor coupling"
        ],
        "ctas": [
            "Which cloud services create the most operational overhead?",
            "How do you handle cross-region complexity?",
            "What cloud costs caught you off guard?",
            "How do you balance managed services vs control?",
            "What multi-cloud challenges have you solved?"
        ]
    },
    "cicd": {
        "insights": [
            "Pipeline as code prevents configuration drift and bus factor issues",
            "Deployment frequency correlates with stability when done right",
            "Feature flags decouple deployment risk from feature risk",
            "Progressive delivery beats blue-green for complex systems",
            "CI/CD observability matters as much as application observability"
        ],
        "ctas": [
            "What CI/CD bottleneck slows your team down most?",
            "How do you handle deployment rollbacks at scale?",
            "Which testing strategy gives you the most confidence?",
            "How do you balance deployment speed with safety?",
            "What pipeline failures taught you the most?"
        ]
    },
    "architecture": {
        "insights": [
            "Distributed systems fail in ways you haven't thought of yet",
            "Conway's Law shapes your architecture more than you realize",
            "Microservices solve organizational problems, not just technical ones",
            "Event-driven architectures require different mental models",
            "System boundaries need continuous reevaluation as teams grow"
        ],
        "ctas": [
            "What architectural decision would you reverse with hindsight?",
            "How do you handle distributed system complexity?",
            "Which architectural patterns work best for your team size?",
            "How do you balance consistency with availability?",
            "What system boundaries have caused the most friction?"
        ]
    },
    "default": {
        "insights": [
            "Production systems teach you things documentation never will",
            "Operational simplicity beats architectural elegance every time",
            "Automate the boring stuff so humans can focus on the interesting problems",
            "System evolution requires continuous learning and adaptation",
            "The best architectures optimize for change, not just current requirements"
        ],
        "ctas": [
            "What production experience changed how you design systems?",
            "How do you balance technical debt with new feature development?",
            "Which operational practices have scaled best for your team?",
            "What would you do differently if you started over today?",
            "How do you keep learning while managing operational load?"
        ]
    }
}

def get_context_aware_insights(title: str, summary: str) -> tuple:
    """Get context-aware insights and CTA based on article content."""
    content = f"{title} {summary}".lower()
    
    # Define keyword mapping to contexts
    context_keywords = {
        "kubernetes": ["kubernetes", "k8s", "cluster", "pods", "helm", "kubectl", "container orchestration"],
        "security": ["security", "vulnerability", "threat", "attack", "breach", "cve", "compliance", "rbac", "iam", "zero trust"],
        "observability": ["monitoring", "observability", "metrics", "logs", "tracing", "alerting", "slo", "dashboard", "grafana", "prometheus"],
        "incident": ["incident", "outage", "mttr", "pager", "on-call", "downtime", "postmortem", "runbook"],
        "cloud": ["aws", "gcp", "azure", "cloud", "serverless", "lambda", "s3", "ec2", "terraform", "cloudformation"],
        "cicd": ["ci/cd", "pipeline", "deployment", "release", "jenkins", "github actions", "gitlab ci", "continuous"],
        "architecture": ["architecture", "microservices", "distributed", "api", "design patterns", "scalability", "event-driven"],
        "reliability": ["sre", "reliability", "availability", "redundancy", "failover", "disaster recovery", "chaos engineering"],
        "platform": ["platform", "internal tools", "developer experience", "self-service", "infrastructure", "backstage"]
    }
    
    # Find best matching context
    best_context = "default"
    max_matches = 0
    
    for context, keywords in context_keywords.items():
        matches = sum(1 for keyword in keywords if keyword in content)
        if matches > max_matches:
            max_matches = matches
            best_context = context
    
    insights_data = CONTEXT_INSIGHTS[best_context]
    selected_insights = random.sample(insights_data["insights"], min(3, len(insights_data["insights"])))
    selected_cta = random.choice(insights_data["ctas"])
    
    return selected_insights, selected_cta

QUICK_TIPS = [
    "Always version your infrastructure. Terraform state + git = time machine for your cloud.",
    "Set up alerts on error budget burn rate, not just SLO breaches. Catch problems before they become incidents.",
    "Use feature flags for deployments. Decouple deploy from release. Sleep better.",
    "Automate your runbooks. If you're copy-pasting commands during an incident, you're doing it wrong.",
    "Shift security left: run SAST in CI, not just before prod. Find vulns when they're cheap to fix.",
    "Implement progressive rollouts. 1% → 10% → 50% → 100%. Your users will thank you.",
    "Always have a rollback plan. If you can't roll back in under 5 minutes, you're not ready to deploy.",
    "Use structured logging from day one. Your future self debugging at 3am will be grateful.",
    "Chaos engineering isn't optional at scale. Break things on purpose before they break you.",
    "Document your on-call handoffs. Context switching is the silent killer of incident response.",
    "Treat secrets like radioactive material: rotate often, audit always, never commit to git.",
    "Container image scanning in CI is table stakes. SBOM generation is the next level.",
    "Golden signals: latency, traffic, errors, saturation. Start there, expand later.",
    "Blameless postmortems aren't optional. If people hide mistakes, you can't learn from them.",
    "GitOps isn't just for Kubernetes. Apply the pattern everywhere: git as source of truth.",
]

LESSONS_TEMPLATES = [
    "Lesson learned: {topic}\n\nThe pattern: {pattern}\n\nWhy it matters: {value}\n\nHow to apply it: Start small, measure impact, iterate.",
    "What {topic} taught us:\n\n→ The problem: overconfidence in manual processes\n→ The fix: {pattern}\n→ The result: {value}",
    "Hard-won insight on {topic}:\n\n❌ What didn't work: hoping for the best\n✅ What worked: {pattern}\n📈 Impact: {value}",
]


def is_valid_feed_url(url: str) -> bool:
    u = (url or "").strip()
    if not u:
        return False
    return u.startswith("http://") or u.startswith("https://")

# Add more sources without changing code (comma-separated RSS/Atom URLs)
EXTRA_NEWS_SOURCES = [u.strip() for u in os.environ.get("EXTRA_NEWS_SOURCES", "").split(",") if u.strip()]

HOOKS = [
    "🚀 Signals that move the reliability needle.",
    "🛠️ What high-perf teams are watching this week.",
    "🔥 Cut noise, keep signal: your DevOps digest.",
    "💡 The reliability reads that matter.",
    "⚙️ Infrastructure signals you can't ignore.",
    "🎯 What's moving production systems forward.",
    "🌊 This week's current in platform engineering.",
    "📡 Industry developments worth tracking.",
    "⚡ Latest insights from the DevOps frontier.",
]

CTAS = [
    "What would you prioritize first?",
    "Would you ship this to prod today?",
    "Where does this break in your stack?",
    "What did we miss that you’re tracking?",
    "Which one made you rethink your approach?",
    "How would you apply this in your team?",
    "What's your hot take on #1?",
    "Drop your experience with this in comments.",
]

WHY_LINES = [
    "Faster feedback, calmer incidents, happier on-call.",
    "Better observability, fewer surprises in prod.",
    "Ship often, recover quickly, learn continuously.",
]

HASHTAGS = [
    "#DevOps", "#SRE", "#Cloud", "#Kubernetes",
    "#PlatformEngineering", "#Observability", "#IncidentManagement",
    "#ReliabilityEngineering", "#InfraAsCode", "#CICD", "#FinOps",
    "#Resilience", "#SiteReliability", "#Automation"
]

# -------------------------------------------------
# SMALL HELPERS
# -------------------------------------------------

def validate_post_content(content: str) -> Tuple[bool, str]:
    """Validate post content for quality and compliance."""
    if not content or not content.strip():
        return False, "Empty content"
    
    # Check character limits
    if len(content) > MAX_POST_CHARS:
        return False, f"Content too long: {len(content)} > {MAX_POST_CHARS} chars"
    
    # Check for minimum content quality
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    # Must have substantial content (not just hashtags)
    content_lines = [line for line in lines if not line.startswith('#')]
    if len(content_lines) < 3:
        return False, "Insufficient content - too few lines"
    
    # Check for common content issues
    content_lower = content.lower()
    
    # Avoid repetitive content
    words = content_lower.split()
    word_count = {}
    for word in words:
        if len(word) > 3:  # Only count meaningful words
            word_count[word] = word_count.get(word, 0) + 1
    
    # Flag if any word appears too frequently
    max_word_count = max(word_count.values()) if word_count else 0
    if max_word_count > 8:  # Arbitrary threshold for repetition
        return False, "Content appears repetitive"
    
    # Check for required elements in lessons format
    if "Topic:" in content and "The pattern:" in content:
        # Must have numbered lessons
        if not any(emoji in content for emoji in ["1️⃣", "2️⃣", "3️⃣", "1.", "2.", "3."]):
            return False, "Lessons format missing numbered points"
    
    return True, "Valid content"


# Remove duplicate clip function and keep the improved version above


# -------------------------------------------------
# METRICS TRACKING
# -------------------------------------------------

def load_metrics() -> Dict[str, Any]:
    """Load metrics from file."""
    if not os.path.exists(METRICS_FILE):
        return {
            "total_posts": 0,
            "posts_today": 0,
            "last_post_date": None,
            "formats_used": {},
            "sources_used": {},
            "errors": [],
            "daily_history": [],
        }
    try:
        with open(METRICS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"total_posts": 0, "posts_today": 0, "last_post_date": None, "formats_used": {}, "sources_used": {}, "errors": [], "daily_history": []}


def save_metrics(metrics: Dict[str, Any]) -> None:
    """Save metrics to file."""
    if not TRACK_METRICS:
        return
    try:
        with open(METRICS_FILE, "w") as f:
            json.dump(metrics, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save metrics: {e}")


def update_metrics(post_format: str, sources: List[str], success: bool, error_msg: str = "") -> None:
    """Update metrics after a post attempt."""
    if not TRACK_METRICS:
        return
    
    metrics = load_metrics()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # Reset daily counter if new day
    if metrics.get("last_post_date") != today:
        metrics["posts_today"] = 0
        metrics["last_post_date"] = today
    
    if success:
        metrics["total_posts"] = metrics.get("total_posts", 0) + 1
        metrics["posts_today"] = metrics.get("posts_today", 0) + 1
        
        # Track format usage
        formats = metrics.get("formats_used", {})
        formats[post_format] = formats.get(post_format, 0) + 1
        metrics["formats_used"] = formats
        
        # Track source usage
        src_counts = metrics.get("sources_used", {})
        for src in sources:
            src_counts[src] = src_counts.get(src, 0) + 1
        metrics["sources_used"] = src_counts
        
        # Add to daily history
        history = metrics.get("daily_history", [])
        history.append({
            "date": today,
            "time": datetime.now(timezone.utc).isoformat(),
            "format": post_format,
            "sources": sources,
        })
        # Keep last 30 days
        metrics["daily_history"] = history[-90:]
        
        # Track posts created count
        metrics["posts_created"] = metrics.get("posts_created", 0) + 1
    else:
        errors = metrics.get("errors", [])
        errors.append({
            "date": today,
            "time": datetime.now(timezone.utc).isoformat(),
            "error": error_msg[:200],
        })
        metrics["errors"] = errors[-50:]  # Keep last 50 errors
    
    save_metrics(metrics)


def get_posts_today() -> int:
    """Get number of posts made today."""
    metrics = load_metrics()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if metrics.get("last_post_date") == today:
        return metrics.get("posts_today", 0)
    return 0


# -------------------------------------------------
# CONTENT HELPERS
# -------------------------------------------------

def get_contextual_hashtags(topic: str, max_count: int = None) -> str:
    """Generate context-aware hashtags based on topic content."""
    topic_lower = topic.lower()
    context_tags = []
    
    # Add context-specific hashtags based on content
    if any(keyword in topic_lower for keyword in ["kubernetes", "k8s", "container", "helm"]):
        context_tags.extend(["#Kubernetes", "#ContainerOrchestration", "#CloudNative"])
    elif any(keyword in topic_lower for keyword in ["security", "vulnerability", "cve", "zero-trust"]):
        context_tags.extend(["#DevSecOps", "#Security", "#CyberSecurity"])
    elif any(keyword in topic_lower for keyword in ["observability", "monitoring", "metrics", "tracing"]):
        context_tags.extend(["#Observability", "#Monitoring", "#SRE"])
    elif any(keyword in topic_lower for keyword in ["aws", "azure", "gcp", "cloud"]):
        context_tags.extend(["#Cloud", "#CloudArchitecture", "#CloudNative"])
    elif any(keyword in topic_lower for keyword in ["terraform", "iac", "infrastructure"]):
        context_tags.extend(["#InfrastructureAsCode", "#Terraform", "#Automation"])
    elif any(keyword in topic_lower for keyword in ["incident", "outage", "reliability"]):
        context_tags.extend(["#SRE", "#IncidentResponse", "#Reliability"])
    
    return get_hashtags(max_count, context_tags)


# -------------------------------------------------
# SUBSCRIPTION CALL-TO-ACTION
# -------------------------------------------------

def get_subscription_cta() -> str:
    """Get subscription call-to-action for Beehiiv newsletter.
    
    Respects EMOJI_STYLE setting for consistent branding.
    """
    # Environment variable to control subscription CTA
    INCLUDE_SUBSCRIPTION = os.environ.get("INCLUDE_SUBSCRIPTION", "true").lower() == "true"
    
    if not INCLUDE_SUBSCRIPTION:
        return ""
    
    # Get emoji based on style setting
    if EMOJI_STYLE == "none":
        subscribe_emoji = ""
        link_emoji = ""
        book_emoji = ""
    elif EMOJI_STYLE == "minimal":
        subscribe_emoji = "→"
        link_emoji = "→"
        book_emoji = "→"
    else:  # moderate or heavy
        subscribe_emoji = "📩"
        link_emoji = "👉"
        book_emoji = "📖"
    
    # Subscription CTA messages - vary based on emoji style
    if EMOJI_STYLE == "none":
        subscription_messages = [
            "Want more DevOps insights like this? Subscribe to my newsletter for weekly updates!",
            "Get weekly DevOps insights delivered to your inbox - subscribe to stay ahead!",
            "Subscribe for more deep dives into DevOps, SRE, and platform engineering!",
            "Never miss a DevOps update - join my weekly newsletter!",
        ]
    else:
        subscription_messages = [
            f"{subscribe_emoji} Want more DevOps insights like this? Subscribe to my newsletter!",
            f"{subscribe_emoji} Get weekly DevOps insights delivered to your inbox!",
            f"{subscribe_emoji} Subscribe to my newsletter for deep dives into DevOps, SRE, and platform engineering!",
            f"{subscribe_emoji} Never miss a DevOps update - join my weekly newsletter!",
            f"{subscribe_emoji} Join thousands of DevOps professionals - subscribe to my newsletter for weekly insights!",
        ]
    
    # Newsletter subscription URL
    subscription_url = os.environ.get("NEWSLETTER_URL", "https://subscribe-forms.beehiiv.com/8c55da26-5925-46d6-9877-47c84af2c18a")
    
    # DevOps LinkedIn Playbook URL
    playbook_url = os.environ.get("PLAYBOOK_URL", "https://ajayverse34.gumroad.com/l/the-devops-linkedin-authority-playbook")
    include_playbook = os.environ.get("INCLUDE_PLAYBOOK", "true").lower() == "true"

    # Pick a random message and build the CTA
    message = random.choice(subscription_messages)
    
    # Build the CTA with proper emoji formatting
    if link_emoji:
        cta = f"{message}\n{link_emoji} Subscribe: {subscription_url}"
    else:
        cta = f"{message}\nSubscribe: {subscription_url}"
    
    if include_playbook and playbook_url:
        if book_emoji:
            cta += f"\n{book_emoji} Grab my DevOps LinkedIn Playbook: {playbook_url}"
        else:
            cta += f"\nGrab my DevOps LinkedIn Playbook: {playbook_url}"
    
    return cta

def http_request(
    method: str,
    url: str,
    *,
    headers: Optional[Dict[str, str]] = None,
    json_body: Optional[Dict[str, Any]] = None,
    timeout: int = 10,
    retries: int = 3,
    backoff_seconds: float = 1.5,
    retry_statuses: Tuple[int, ...] = (429, 500, 502, 503, 504),
) -> requests.Response:
    import time

    last_exc: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            r = SESSION.request(
                method,
                url,
                headers=headers,
                json=json_body,
                timeout=timeout,
            )
            if r.status_code not in retry_statuses:
                return r

            # Respect Retry-After when present (rate limiting)
            retry_after = r.headers.get("Retry-After")
            if retry_after:
                try:
                    sleep_s = float(retry_after)
                    time.sleep(min(sleep_s, 30.0))
                except Exception:
                    pass
            else:
                time.sleep(min(backoff_seconds * attempt, 10.0))

            if attempt == retries:
                return r
        except Exception as e:
            last_exc = e
            time.sleep(min(backoff_seconds * attempt, 10.0))

    raise RuntimeError(f"HTTP request failed after retries: {last_exc}")


def ai_enhance_text(text: str, max_length: int = 150) -> str:
    """Use AI API to enhance/summarize text with multi-provider fallback system."""
    if not ENABLE_AI_ENHANCE or not text:
        return text
    
    # Clean and prepare text for AI processing
    clean_text = re.sub(r'\s+', ' ', text.strip())[:2000]  # Limit length for API
    
    # Try multi-provider AI system first
    enhanced_text = try_multi_provider_ai(
        clean_text, 
        task_type="summarization", 
        max_tokens=max_length
    )
    
    if enhanced_text and enhanced_text.strip():
        # Clean and format the response
        txt = enhanced_text.strip()
        # Remove common AI response prefixes
        txt = re.sub(r'^(Summary:|Here\'s a summary:|In summary:)\s*', '', txt, flags=re.IGNORECASE)
        return txt if txt else text
    
    # Final fallback to heuristic summarization
    logger.debug("Using heuristic fallback for text enhancement")
    sentences = text.split('.')[:3]  # Take first 3 sentences
    return '.'.join(sentences).strip() + ('.' if not text.endswith('.') else '')


def ai_generate_value_line(title: str, snippet: str) -> str:
    """Generate a short, unique value line for each item, avoiding static 'Why it matters' phrasing."""
    title_clean = re.sub(r"\s+", " ", (title or "").strip())
    snippet_clean = re.sub(r"\s+", " ", (snippet or "").strip())
    # Heuristic fallback (fast, free, always available)
    def fallback() -> str:
        t = (title_clean + " " + snippet_clean).lower()
        options = []
        if any(k in t for k in ("incident", "outage", "mttr", "pager", "on-call")):
            options = [
                "Reduces incident risk and improves MTTR.",
                "Minimizes downtime and accelerates recovery.",
                "Boosts reliability and on-call confidence.",
            ]
        elif any(k in t for k in ("kubernetes", "cluster", "container", "helm", "gitops")):
            options = [
                "Helps you run clusters more reliably and efficiently.",
                "Streamlines container operations for better uptime.",
                "Empowers scalable, resilient infrastructure.",
            ]
        elif any(k in t for k in ("cicd", "pipeline", "deployment", "release")):
            options = [
                "Improves delivery speed without sacrificing safety.",
                "Enables faster, safer deployments.",
                "Accelerates release cycles and reduces risk.",
            ]
        elif any(k in t for k in ("observability", "monitoring", "tracing", "metrics", "logs")):
            options = [
                "Improves visibility, debugging speed, and reliability.",
                "Makes troubleshooting faster and more effective.",
                "Enhances system transparency and incident response.",
            ]
        elif any(k in t for k in ("aws", "gcp", "azure", "cloud")):
            options = [
                "Optimizes cloud reliability and cost.",
                "Drives better cloud performance and savings.",
                "Strengthens multi-cloud resilience and efficiency.",
            ]
        elif any(k in t for k in ("security", "vulnerability", "cve", "sast", "dast")):
            options = [
                "Strengthens security posture and reduces risk.",
                "Mitigates vulnerabilities before they impact production.",
                "Elevates your defense against emerging threats.",
            ]
        elif any(k in t for k in ("terraform", "iac", "infrastructure", "automation")):
            options = [
                "Improves infrastructure reliability and consistency.",
                "Automates operations for fewer manual errors.",
                "Prevents configuration drift and boosts stability.",
            ]
        else:
            options = [
                "Practical signal for building reliable systems.",
                "Empowers teams to deliver with confidence.",
                "Drives operational excellence and learning.",
            ]
        return random.choice(options)
    if not ENABLE_AI_ENHANCE:
        return fallback()
    context = clip((snippet_clean or title_clean), 500)
    prompt = (
        f"Write a unique, actionable impact line (max 15 words) for this DevOps/SRE topic. Do NOT use the phrase 'Why it matters'.\n"
        f"Topic: {title_clean}\n"
        f"Context: {context}\n"
        f"Example: 'Reduces deployment risk and improves recovery time.'\n"
        f"Your answer:"
    )
    generated_text = try_multi_provider_ai(
        prompt,
        task_type="generation",
        max_tokens=50
    )
    if generated_text and generated_text.strip():
        txt = generated_text.replace("\n", " ").strip().strip('"').strip("'")
        # Ensure it does NOT start with 'Why it matters'
        if txt.lower().startswith("why it matters"):
            txt = txt[len("why it matters"):].lstrip(':').strip()
        # Clip to reasonable length
        if txt and len(txt) > 8:
            return clip(txt, 120)
    return fallback()


# =============================
# SCRIPT ENTRYPOINT
# =============================
def main():
    try:
        logger.info("🚀 Starting LinkedIn DevOps post automation...")
        # 1. Get content idea (growth plan or RSS)
        idea = get_growth_plan_content()
        if not idea:
            logger.info("No growth plan idea found, falling back to RSS/news content.")
            # Fallback: Use a digest post from RSS/news (implement as needed)
            # For now, just log and exit
            logger.error("No post idea available. Exiting.")
            print("❌ No post idea available. Nothing to post.")
            return

        # 2. Build post content
        post_text = build_growth_plan_post(idea)
        is_valid, reason = validate_post_content(post_text)
        if not is_valid:
            logger.error(f"Generated post is invalid: {reason}")
            print(f"❌ Generated post is invalid: {reason}")
            return

        # 3. Print or post
        if DRY_RUN:
            logger.info("[DRY RUN] Would post the following content:")
            print("\n===== [DRY RUN] LinkedIn Post Content =====\n")
            print(post_text)
            print("\n===== [END OF POST] =====\n")
            # Optionally, send to Slack for preview if enabled
            if SLACK_WEBHOOK_URL:
                try:
                    http_request(
                        "POST",
                        SLACK_WEBHOOK_URL,
                        json_body={"text": f"[DRY RUN] LinkedIn Post Preview:\n\n{post_text}"},
                        timeout=10
                    )
                    logger.info("[DRY RUN] Sent post preview to Slack.")
                except Exception as e:
                    logger.warning(f"[DRY RUN] Failed to send Slack preview: {e}")
            return

        # 4. Actually post to LinkedIn (implement as needed)
        # This is a placeholder; actual posting logic should be implemented here
        logger.info("[LIVE RUN] Would post to LinkedIn (posting logic not implemented in this patch). Printing post:")
        print("\n===== [LIVE RUN] LinkedIn Post Content =====\n")
        print(post_text)
        print("\n===== [END OF POST] =====\n")
        # TODO: Add LinkedIn posting logic here

    except Exception as e:
        logger.error(f"❌ Unhandled exception in main: {e}")
        print(f"❌ Unhandled exception: {e}")


if __name__ == "__main__":
    main()


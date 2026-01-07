#!/usr/bin/env python3
"""
AI Provider Test Script - Verify your free AI APIs are working
Usage: python test_ai_providers.py
"""

import os
import sys
import requests
import json
from typing import Dict, List, Optional

# Test configuration
TEST_PROMPT = """
DevOps teams are increasingly adopting GitOps workflows for Kubernetes deployments. 
This approach uses Git repositories as the single source of truth for declarative infrastructure and applications.
GitOps enables better security, auditability, and faster rollbacks compared to traditional CI/CD pipelines.
"""

EXPECTED_SUMMARY_KEYWORDS = ["gitops", "kubernetes", "git", "deployment", "devops"]

class AIProviderTester:
    def __init__(self):
        self.results = {}
        
    def test_groq_api(self) -> Dict:
        """Test Groq API"""
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return {"status": "skipped", "reason": "No GROQ_API_KEY found"}
            
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are a technical content summarizer. Provide a concise summary in 2-3 sentences."},
                    {"role": "user", "content": f"Summarize this DevOps content:\n\n{TEST_PROMPT}"}
                ],
                "max_tokens": 150,
                "temperature": 0.3
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if content and len(content) > 20:
                    return {
                        "status": "success",
                        "model": "llama-3.3-70b-versatile",
                        "response": content[:200] + "..." if len(content) > 200 else content,
                        "speed": "⚡⚡⚡⚡⚡ Excellent"
                    }
            
            return {"status": "failed", "reason": f"HTTP {response.status_code}", "response": response.text[:200]}
            
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    
    def test_gemini_api(self) -> Dict:
        """Test Google Gemini API"""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return {"status": "skipped", "reason": "No GEMINI_API_KEY found"}
            
        try:
            payload = {
                "contents": [
                    {
                        "parts": [{"text": f"Summarize this DevOps content in 2-3 clear sentences:\n\n{TEST_PROMPT}"}]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": 150,
                    "temperature": 0.4
                }
            }
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            
            response = requests.post(url, json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    content = candidates[0]["content"]["parts"][0]["text"]
                    if content and len(content) > 20:
                        return {
                            "status": "success",
                            "model": "gemini-2.5-flash",
                            "response": content[:200] + "..." if len(content) > 200 else content,
                            "speed": "⚡⚡⚡⚡ Very Good"
                        }
            
            return {"status": "failed", "reason": f"HTTP {response.status_code}", "response": response.text[:200]}
            
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    
    def test_openrouter_api(self) -> Dict:
        """Test OpenRouter free models"""
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            return {"status": "skipped", "reason": "No OPENROUTER_API_KEY found"}
            
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/your-repo",
                "X-Title": "LinkedIn DevOps Automation"
            }
            
            payload = {
                "model": "xiaomi/mimo-v2-flash:free",
                "messages": [
                    {"role": "system", "content": "You are a technical content summarizer for DevOps professionals."},
                    {"role": "user", "content": f"Summarize this DevOps content in 2-3 sentences:\n\n{TEST_PROMPT}"}
                ],
                "max_tokens": 150,
                "temperature": 0.3
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=12
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if content and len(content) > 20:
                    return {
                        "status": "success",
                        "model": "xiaomi/mimo-v2-flash:free",
                        "response": content[:200] + "..." if len(content) > 200 else content,
                        "speed": "⚡⚡⚡ Good"
                    }
            
            return {"status": "failed", "reason": f"HTTP {response.status_code}", "response": response.text[:200]}
            
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    
    def test_huggingface_api(self) -> Dict:
        """Test Hugging Face API"""
        api_key = os.environ.get("HF_API_KEY")
        if not api_key:
            return {"status": "skipped", "reason": "No HF_API_KEY found"}
            
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            
            payload = {
                "inputs": TEST_PROMPT,
                "parameters": {
                    "max_length": 150,
                    "min_length": 30,
                    "do_sample": False,
                }
            }
            
            response = requests.post(
                "https://api-inference.huggingface.co/models/facebook/bart-large-cnn",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    text = result[0].get("summary_text", "")
                    if text and len(text) > 20:
                        return {
                            "status": "success", 
                            "model": "facebook/bart-large-cnn",
                            "response": text[:200] + "..." if len(text) > 200 else text,
                            "speed": "⚡⚡ Fair"
                        }
            
            return {"status": "failed", "reason": f"HTTP {response.status_code}", "response": response.text[:200]}
            
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    
    def run_all_tests(self):
        """Run all provider tests"""
        print("🤖 AI Provider Test Suite")
        print("=" * 50)
        
        tests = [
            ("Groq API (Primary)", self.test_groq_api),
            ("Google Gemini (Secondary)", self.test_gemini_api), 
            ("OpenRouter Free (Tertiary)", self.test_openrouter_api),
            ("Hugging Face (Fallback)", self.test_huggingface_api)
        ]
        
        working_providers = []
        
        for name, test_func in tests:
            print(f"\n🧪 Testing {name}...")
            result = test_func()
            
            if result["status"] == "success":
                print(f"   ✅ SUCCESS - Model: {result['model']}")
                print(f"   📊 Speed: {result['speed']}")
                print(f"   📝 Sample: {result['response'][:100]}...")
                working_providers.append(name)
            elif result["status"] == "skipped":
                print(f"   ⏭️  SKIPPED - {result['reason']}")
            elif result["status"] == "failed":
                print(f"   ❌ FAILED - {result['reason']}")
            else:
                print(f"   🚨 ERROR - {result['reason']}")
        
        print("\n" + "=" * 50)
        print("📊 SUMMARY")
        print("=" * 50)
        
        if working_providers:
            print(f"✅ Working Providers ({len(working_providers)}/4):")
            for i, provider in enumerate(working_providers, 1):
                print(f"   {i}. {provider}")
            
            print(f"\n🎉 AI Enhancement Status: {'EXCELLENT' if len(working_providers) >= 3 else 'GOOD' if len(working_providers) >= 2 else 'BASIC' if len(working_providers) >= 1 else 'DISABLED'}")
            
            if len(working_providers) >= 2:
                print("💪 You have redundancy - system will be highly reliable!")
            elif len(working_providers) == 1:
                print("⚠️  Consider adding a backup provider for better reliability")
            
        else:
            print("❌ No AI providers working")
            print("💡 Add at least one API key to enable AI features:")
            print("   • GROQ_API_KEY (recommended)")
            print("   • GEMINI_API_KEY (high quality)")
            print("   • OPENROUTER_API_KEY (free models)")
            print("   • HF_API_KEY (fallback)")
        
        return len(working_providers)

def main():
    """Main test runner"""
    tester = AIProviderTester()
    working_count = tester.run_all_tests()
    
    print(f"\n🔧 Setup Instructions:")
    print("   See AI_PROVIDERS_SETUP.md for detailed setup guide")
    
    sys.exit(0 if working_count > 0 else 1)

if __name__ == "__main__":
    main()
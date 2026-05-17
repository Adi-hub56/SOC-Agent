
"""
LLM Agent Service - Flexible multi-LLM support
Supports: Groq (primary), Claude (fallback), Mistral (future)
"""

import json
import os
from typing import Dict, List
from app.utils.logger import log_info, log_error

class LLMAgent:
    """Multi-LLM agent that can switch between Groq, Claude, Mistral"""
    
    def __init__(self, provider="groq"):
        self.provider = provider.lower()
        
        if self.provider == "groq":
            from groq import Groq
            groq_key = os.getenv("GROQ_API_KEY")
            if not groq_key:
                raise ValueError("GROQ_API_KEY not set in environment")
            self.client = Groq(api_key=groq_key)
            self.model = "llama-3.3-70b-versatile"
            log_info("Using Groq API", model=self.model)
            
        elif self.provider == "claude":
            from anthropic import Anthropic
            claude_key = os.getenv("ANTHROPIC_API_KEY")
            if not claude_key:
                raise ValueError("ANTHROPIC_API_KEY not set in environment")
            self.client = Anthropic(api_key=claude_key)
            self.model = "claude-opus-4-20250514"
            log_info("Using Claude API", model=self.model)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    def analyze_alert_multi_step(self, alert_data):
        """5-step analysis using multi-turn conversation"""
        conversation_history = []
        results = {}
        
        try:
            # STEP 1: Classification
            log_info("Step 1: Classification", event_id=alert_data.get("event_id"))
            
            step1_prompt = f"""You are a senior SOC analyst. Analyze this security alert.

RAW ALERT:
{json.dumps(alert_data, indent=2)}

Respond ONLY with valid JSON (no markdown):
{{"attack_type": "type", "mitre_technique": "T1234.567", "category": "category", "brief_description": "desc"}}"""
            
            conversation_history.append({"role": "user", "content": step1_prompt})
            response = self._call_llm(conversation_history)
            step1_result = self._parse_json_response(response)
            results["step_1_classification"] = step1_result
            conversation_history.append({"role": "assistant", "content": response})
            
            # STEP 2: Threat Assessment
            log_info("Step 2: Threat Assessment")
            
            step2_prompt = f"""Given this is a {step1_result.get('attack_type', 'security incident')}:

Target: {alert_data.get('dest_host')}
Source: {alert_data.get('src_ip')}

Assess threat level. Respond ONLY with JSON:
{{"severity": "CRITICAL/HIGH/MEDIUM/LOW", "threat_score": "1-10", "reasoning": "explanation", "factors": ["f1", "f2"]}}"""
            
            conversation_history.append({"role": "user", "content": step2_prompt})
            response = self._call_llm(conversation_history)
            step2_result = self._parse_json_response(response)
            results["step_2_threat_assessment"] = step2_result
            conversation_history.append({"role": "assistant", "content": response})
            
            # STEP 3: Investigation
            log_info("Step 3: Investigation Plan")
            
            step3_prompt = f"""Given {step1_result.get('attack_type')} with {step2_result.get('severity')} severity:

What investigation steps? Respond ONLY with JSON:
{{"investigation_steps": ["step1", "step2"], "priority_checks": ["check1"], "estimated_time": "X minutes"}}"""
            
            conversation_history.append({"role": "user", "content": step3_prompt})
            response = self._call_llm(conversation_history)
            step3_result = self._parse_json_response(response)
            results["step_3_investigation_plan"] = step3_result
            conversation_history.append({"role": "assistant", "content": response})
            
            # STEP 4: Root Cause
            log_info("Step 4: Root Cause Analysis")
            
            step4_prompt = f"""Root cause of {step1_result.get('attack_type')}?

Respond ONLY with JSON:
{{"root_cause": "explanation", "attack_chain": ["step1", "step2"], "vulnerability": "CVE or type"}}"""
            
            conversation_history.append({"role": "user", "content": step4_prompt})
            response = self._call_llm(conversation_history)
            step4_result = self._parse_json_response(response)
            results["step_4_root_cause"] = step4_result
            conversation_history.append({"role": "assistant", "content": response})
            
            # STEP 5: Remediation
            log_info("Step 5: Remediation Strategy")
            
            step5_prompt = f"""Remediate {step1_result.get('attack_type')} ({step2_result.get('severity')})?

Respond ONLY with JSON:
{{"immediate_actions": [{{"action": "name", "time": "5 min", "command": "cmd"}}], "short_term": [], "long_term": []}}"""
            
            conversation_history.append({"role": "user", "content": step5_prompt})
            response = self._call_llm(conversation_history)
            step5_result = self._parse_json_response(response)
            results["step_5_remediation"] = step5_result
            conversation_history.append({"role": "assistant", "content": response})
            
            log_info("All 5 steps complete")
            
            results["conversation_history"] = conversation_history
            results["provider"] = self.provider
            results["model"] = self.model
            
            return results
            
        except Exception as e:
            log_error("Analysis failed", error=str(e))
            raise
    
    def _call_llm(self, messages):
        """Call the LLM"""
        try:
            if self.provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=1000,
                )
                return response.choices[0].message.content
            
            elif self.provider == "claude":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    messages=messages,
                )
                return response.content[0].text
                
        except Exception as e:
            log_error(f"LLM call failed", error=str(e))
            raise
    
    def _parse_json_response(self, response):
        """Extract JSON from response"""
        try:
            response = response.replace("```json", "").replace("```", "").strip()
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            log_error("Failed to parse JSON", response=response[:100])
            return {"raw_response": response}


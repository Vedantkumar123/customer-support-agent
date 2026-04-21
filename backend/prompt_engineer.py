from typing import Dict
from enum import Enum


class SupportMode(Enum):
    STRICT_POLICY = "strict"
    FRIENDLY = "friendly"
    FALLBACK = "fallback"


class PromptEngineer:
    
    SCENARIO_CONFIG = {
        SupportMode.STRICT_POLICY: {
            'temperature': 0.2,
            'max_tokens': 150,
            'description': 'Strict Policy Mode - Deterministic, policy-focused responses'
        },
        SupportMode.FRIENDLY: {
            'temperature': 0.7,
            'max_tokens': 200,
            'description': 'Friendly Mode - Empathetic, natural, friendly responses'
        },
        SupportMode.FALLBACK: {
            'temperature': 0.5,
            'max_tokens': 100,
            'description': 'Fallback Mode - No matching policy found'
        }
    }
    
    @staticmethod
    def get_prompt(
        mode: SupportMode,
        context: str,
        query: str
    ) -> str:
        
        if mode == SupportMode.STRICT_POLICY:
            return PromptEngineer._strict_policy_prompt(context, query)
        elif mode == SupportMode.FRIENDLY:
            return PromptEngineer._friendly_tone_prompt(context, query)
        elif mode == SupportMode.FALLBACK:
            return PromptEngineer._fallback_prompt(query)
        else:
            return PromptEngineer._friendly_tone_prompt(context, query)
    
    @staticmethod
    def _strict_policy_prompt(context: str, query: str) -> str:
        return f"""You are a professional customer support assistant for an Indian e-commerce company.

INSTRUCTIONS:
- Use ONLY the provided policy context below
- Do not add assumptions or information not in the policies
- Be clear, concise, and direct
- If the policy doesn't cover the issue, say so explicitly
- Maintain a professional tone

COMPANY POLICIES:
{context}

CUSTOMER ISSUE:
{query}

RESPONSE:
"""
    
    @staticmethod
    def _friendly_tone_prompt(context: str, query: str) -> str:
        return f"""You are a polite and empathetic customer support agent for an Indian e-commerce company.

INSTRUCTIONS:
- Use the provided policy context to guide your response
- Be friendly, warm, and understanding
- Acknowledge the customer's concern and show empathy
- Explain policies in simple, easy-to-understand language
- End with an offer to help further if needed

COMPANY POLICIES:
{context}

CUSTOMER ISSUE:
{query}

RESPONSE:
"""
    
    @staticmethod
    def _fallback_prompt(query: str) -> str:
        return f"""You are a customer support agent. The customer's issue does not match our standard policies.

CUSTOMER ISSUE:
{query}

RESPONSE:
Your issue requires specialized attention. Please escalate this to our senior support team for proper resolution. 
Our team will contact you within 24 hours to assist you further.
Thank you for your patience.
"""
    
    @staticmethod
    def get_config_for_mode(mode: SupportMode) -> Dict:
        return PromptEngineer.SCENARIO_CONFIG.get(
            mode,
            PromptEngineer.SCENARIO_CONFIG[SupportMode.FRIENDLY]
        )
    
    @staticmethod
    def get_all_modes() -> Dict:
        return {
            mode.value: {
                'name': mode.name,
                'value': mode.value,
                **config
            }
            for mode, config in PromptEngineer.SCENARIO_CONFIG.items()
        }

"""LLM client for Cloudflare Workers AI REST API.

Model-agnostic client with structured output validation, retry logic,
and robust JSON parsing for the 70B model's response patterns.
"""

import json
import re
import logging
from typing import Optional

import httpx

from .prompts import SYSTEM_PROMPT, validate_llm_response

logger = logging.getLogger(__name__)

# Cloudflare Workers AI REST endpoint template
AI_RUN_URL = "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"


class LLMClient:
    """Async client for Cloudflare Workers AI LLM inference.

    Wraps the Workers AI REST API to run structured evidence analysis
    prompts and parse the JSON response. Handles:
    - Workers AI auto-parsing (response may be dict or string)
    - Markdown code fences in model output
    - Trailing commas in JSON
    - Partial/malformed responses with schema enforcement
    - Transient failures with retry logic
    """

    def __init__(
        self,
        api_token: str,
        account_id: str,
        model: str = "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
        timeout: int = 60,
        max_concurrency: int = 5,
    ):
        """Initialize the LLM client.

        Args:
            api_token: Cloudflare API token (CF_API_TOKEN)
            account_id: Cloudflare account ID (CF_ACCOUNT_ID)
            model: Workers AI model identifier
            timeout: HTTP timeout in seconds per request
            max_concurrency: Maximum concurrent API calls

        Raises:
            ValueError: If api_token or account_id is empty.
        """
        if not api_token:
            raise ValueError(
                "CF_API_TOKEN is not set. Configure it in your .env file."
            )
        if not account_id:
            raise ValueError(
                "CF_ACCOUNT_ID is not set. Configure it in your .env file."
            )

        self._api_token = api_token
        self._account_id = account_id
        self._model = model
        self._timeout = timeout
        self._url = AI_RUN_URL.format(account_id=account_id, model=model)
        self._semaphore = __import__("asyncio").Semaphore(max_concurrency)

        logger.info("LLM client initialized: model=%s, timeout=%ds, concurrency=%d",
                     model, timeout, max_concurrency)

    async def analyze(self, prompt: str) -> dict:
        """Send a prompt to the LLM and parse the structured JSON response.

        Args:
            prompt: The full user prompt (evidence evaluation instructions).

        Returns:
            A validated dict with keys:
                - reasoning (str|None): Chain-of-thought analysis
                - is_compliant (bool|None): Whether the evidence is met
                - confidence (float): LLM's confidence (0.0-1.0)
                - justification (str): Explanation with verbatim quotes

            On failure or invalid response, returns a safe fallback
            with is_compliant=None and confidence=0.0.
        """
        async with self._semaphore:
            return await self._analyze_single(prompt)

    async def _analyze_single(self, prompt: str) -> dict:
        """Execute a single LLM API call without concurrency control."""
        headers = {
            "Authorization": f"Bearer {self._api_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 1024,
            "temperature": 0.1,  # Low temperature for consistent audit judgments
        }

        # One retry on transient failure
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.post(
                        self._url, headers=headers, json=payload
                    )
                    response.raise_for_status()
                    data = response.json()

                if not data.get("success"):
                    errors = data.get("errors", [])
                    logger.error("Workers AI API error: %s", errors)
                    return self._fallback()

                raw = data.get("result", {}).get("response")
                if raw is None:
                    logger.warning("Empty response from Workers AI")
                    return self._fallback()

                # Workers AI auto-parses JSON model output.
                # When the model emits valid JSON, `response` is already a dict.
                # When the model emits plain text, `response` is a string.
                if isinstance(raw, dict):
                    parsed = raw
                elif isinstance(raw, str):
                    parsed = self._parse_json_text(raw)
                else:
                    logger.warning("Unexpected response type: %s", type(raw).__name__)
                    return self._fallback()

                # Validate and normalize the response against our schema
                return validate_llm_response(parsed)

            except httpx.TimeoutException:
                logger.warning(
                    "LLM request timed out (attempt %d/2)", attempt + 1
                )
                if attempt == 0:
                    continue
                return self._fallback()

            except httpx.HTTPStatusError as e:
                logger.error(
                    "LLM HTTP error %d (attempt %d/2): %s",
                    e.response.status_code,
                    attempt + 1,
                    e.response.text[:200],
                )
                if attempt == 0 and e.response.status_code >= 500:
                    continue
                return self._fallback()

            except (httpx.RequestError, json.JSONDecodeError) as e:
                logger.error("LLM request failed: %s", e)
                return self._fallback()

            except Exception as e:
                logger.error("Unexpected LLM error: %s", e)
                return self._fallback()

        return self._fallback()

    def _parse_json_text(self, raw: str) -> dict:
        """Parse a JSON string from the LLM text response.

        Multi-layer extraction strategy:
        1. Direct json.loads()
        2. Strip markdown code fences
        3. Extract first {...} block via regex
        4. Fix trailing commas

        Returns a dict (possibly empty on failure).
        """
        cleaned = raw.strip()

        # Layer 1: Try direct parse
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Layer 2: Strip markdown code fences
        if cleaned.startswith("```"):
            # Remove opening fence line
            cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
            # Remove closing fence
            cleaned = re.sub(r"\n?```\s*$", "", cleaned)
            cleaned = cleaned.strip()
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                pass

        # Layer 3: Extract first {...} block via regex
        brace_match = re.search(r"\{[\s\S]*\}", raw)
        if brace_match:
            candidate = brace_match.group(0)
            # Fix trailing commas before closing braces/brackets
            candidate = re.sub(r",\s*}", "}", candidate)
            candidate = re.sub(r",\s*\]", "]", candidate)
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        # Layer 4: Aggressive cleanup — fix all trailing commas in the brace match
        if brace_match:
            candidate = brace_match.group(0)
            # More aggressive: remove all commas followed by whitespace and then } or ]
            candidate = re.sub(r",(\s*[}\]])", r"\1", candidate)
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        logger.warning(
            "Failed to parse LLM JSON response after all layers.\nRaw (first 300 chars): %.300s",
            raw,
        )
        return {}

    def _fallback(self) -> dict:
        """Return a safe fallback response (no override)."""
        return {
            "reasoning": None,
            "is_compliant": None,
            "confidence": 0.0,
            "justification": "",
        }

"""LLM client for Cloudflare Workers AI REST API."""

import json
import logging
from typing import Optional, Union

import httpx

logger = logging.getLogger(__name__)

# Cloudflare Workers AI REST endpoint template
AI_RUN_URL = "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"

# Default system prompt for evidence analysis
SYSTEM_PROMPT = (
    "You are a precise NABH compliance audit assistant. "
    "Analyze the given document text against the specified evidence requirement. "
    "Respond with valid JSON only — no markdown, no extra text. "
    "Use null for is_compliant when you are uncertain or the evidence is ambiguous."
)


class LLMClient:
    """Async client for Cloudflare Workers AI LLM inference.

    Wraps the Workers AI REST API to run structured evidence analysis
    prompts and parse the JSON response. Handles the fact that Workers AI
    auto-parses JSON model output — so response body may be a dict or a string.
    """

    def __init__(
        self,
        api_token: str,
        account_id: str,
        model: str = "@cf/meta/llama-3.1-8b-instruct",
        timeout: int = 30,
        max_concurrency: int = 3,
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

    async def analyze(self, prompt: str) -> dict:
        """Send a prompt to the LLM and parse the structured JSON response.

        Args:
            prompt: The full prompt (system + user content) to send.

        Returns:
            A dict with keys:
                - is_compliant (bool or None): Whether the evidence is met
                - confidence (float): LLM's confidence (0.0–1.0)
                - justification (str): Explanation from the LLM

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
                parsed = raw if isinstance(raw, dict) else self._parse_json_text(raw)
                return self._extract_fields(parsed)

            except httpx.TimeoutException:
                logger.warning(
                    "LLM request timed out (attempt %d/2)", attempt + 1
                )
                if attempt == 0:
                    continue  # retry once
                return self._fallback()

            except httpx.HTTPStatusError as e:
                logger.error(
                    "LLM HTTP error %d (attempt %d/2): %s",
                    e.response.status_code,
                    attempt + 1,
                    e.response.text[:200],
                )
                if attempt == 0 and e.response.status_code >= 500:
                    continue  # retry on server errors
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

        Handles common formatting quirks (markdown fences, trailing commas).
        Returns a dict (possibly empty on failure).
        """
        cleaned = raw.strip()

        # Remove markdown code fences if present
        if cleaned.startswith("```"):
            start = cleaned.find("{")
            if start == -1:
                start = cleaned.find("[")
            if start != -1:
                end = cleaned.rfind("```")
                if end > start:
                    cleaned = cleaned[start:end]
                else:
                    cleaned = cleaned[start:]

        # Remove trailing commas before closing braces (common LLM issue)
        import re as _re
        cleaned = _re.sub(r",\s*}", "}", cleaned)
        cleaned = _re.sub(r",\s*\]", "]", cleaned)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.warning(
                "Failed to parse LLM JSON response: %s\nRaw: %.200s", e, raw
            )
            return {}

    def _extract_fields(self, parsed: dict) -> dict:
        """Extract standard fields from a parsed JSON dict.

        Args:
            parsed: Dict from LLM response (may be empty on failure).

        Returns:
            Normalized dict with is_compliant, confidence, justification.
        """
        if not parsed:
            return self._fallback()

        is_compliant = parsed.get("is_compliant")
        # Preserve None (JSON null = uncertainty) — bool(None) is False which
        # would conflate "uncertain" with "false". Only coerce true/false.
        if is_compliant is not None:
            is_compliant = bool(is_compliant)

        confidence = float(parsed.get("confidence", 0.0))
        confidence = max(0.0, min(1.0, confidence))

        justification = str(parsed.get("justification", ""))[:500]

        return {
            "is_compliant": is_compliant,
            "confidence": confidence,
            "justification": justification,
        }

    def _fallback(self) -> dict:
        """Return a safe fallback response (no override)."""
        return {
            "is_compliant": None,
            "confidence": 0.0,
            "justification": "",
        }

import json
import os
from typing import Optional
from anthropic import Anthropic
from app.schemas import CodeReviewResponse, ReviewIssue, ReviewCategory, SeverityLevel


class ClaudeCodeReviewer:
    """Service to review code using Claude API"""
    
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = Anthropic()
    
    def review_code(
        self, 
        code: str, 
        language: str = "python", 
        context: Optional[str] = None
    ) -> CodeReviewResponse:
        system_prompt = """You are an expert code reviewer with deep knowledge of software engineering best practices.
Your job is to review code and provide constructive feedback.

When reviewing code, analyze for:
1. Bugs - Logic errors, null reference issues, race conditions, unhandled exceptions
2. Style - Code formatting, naming conventions, readability, best practices
3. Performance - Inefficient algorithms, memory leaks, unnecessary operations, O(n²) loops
4. Security - SQL injection, XSS, authentication issues, credential exposure, input validation

Return your response ONLY as valid JSON (no markdown, no extra text, no code blocks).
The JSON must match this exact structure:
{
  "summary": "2-3 sentence high-level summary of the code and review",
  "issues": {
    "bugs": [{"severity": "critical|high|medium|low|info", "title": "...", "description": "...", "line_number": null_or_number, "suggestion": "..."}],
    "style": [...same structure...],
    "performance": [...same structure...],
    "security": [...same structure...]
  },
  "overall_quality_score": 0-100,
  "main_recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"]
}

Rules:
- Be thorough but constructive
- Prioritize critical issues
- Provide specific, actionable suggestions
- All severity fields must be one of: critical, high, medium, low, info
- overall_quality_score must be a number 0-100
- suggestion field can be null if not applicable
- line_number can be null if not specific to a line"""

        user_prompt = f"""Review this {language} code{' (context: ' + context + ')' if context else ''}:

```{language}
{code}
```

Provide a detailed review in the JSON format specified. Return ONLY valid JSON, nothing else."""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            response_text = message.content[0].text
            review_data = json.loads(response_text)
            issues = ReviewCategory(
                bugs=[
                    ReviewIssue(**issue)
                    for issue in review_data.get("issues", {}).get("bugs", [])
                ],
                style=[
                    ReviewIssue(**issue)
                    for issue in review_data.get("issues", {}).get("style", [])
                ],
                performance=[
                    ReviewIssue(**issue)
                    for issue in review_data.get("issues", {}).get("performance", [])
                ],
                security=[
                    ReviewIssue(**issue)
                    for issue in review_data.get("issues", {}).get("security", [])
                ]
            )
            response = CodeReviewResponse(
                summary=review_data.get("summary", "Code review completed."),
                issues=issues,
                overall_quality_score=float(review_data.get("overall_quality_score", 50)),
                main_recommendations=review_data.get("main_recommendations", [])
            )
            return response
        except json.JSONDecodeError as e:
            return self._create_fallback_response(
                f"Error parsing Claude response: {str(e)}",
                code
            )
        except Exception as e:
            raise Exception(f"Error calling Claude API: {str(e)}")
    
    def _create_fallback_response(self, error_msg: str, code: str) -> CodeReviewResponse:
        return CodeReviewResponse(
            summary=f"Review encountered an issue: {error_msg}. Please try again.",
            issues=ReviewCategory(),
            overall_quality_score=0.0,
            main_recommendations=["Retry the review request"]
        )

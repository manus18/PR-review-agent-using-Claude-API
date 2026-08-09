from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class SeverityLevel(str, Enum):
    """Issue severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ReviewIssue(BaseModel):
    """Individual issue found during code review"""
    severity: SeverityLevel = Field(
        ..., 
        description="Severity of the issue"
    )
    title: str = Field(
        ..., 
        description="Short title of the issue"
    )
    description: str = Field(
        ..., 
        description="Detailed description of the issue"
    )
    line_number: Optional[int] = Field(
        None, 
        description="Line number where issue occurs (optional)"
    )
    suggestion: Optional[str] = Field(
        None, 
        description="How to fix the issue (optional)"
    )


class ReviewCategory(BaseModel):
    """Categories of issues found in code"""
    bugs: List[ReviewIssue] = Field(
        default_factory=list,
        description="Logic errors, null references, race conditions"
    )
    style: List[ReviewIssue] = Field(
        default_factory=list,
        description="Formatting, naming, readability issues"
    )
    performance: List[ReviewIssue] = Field(
        default_factory=list,
        description="Inefficient algorithms, memory leaks"
    )
    security: List[ReviewIssue] = Field(
        default_factory=list,
        description="Security vulnerabilities"
    )


class CodeReviewRequest(BaseModel):
    """Request to review code"""
    code: str = Field(
        ..., 
        description="Code snippet or PR diff to review"
    )
    language: str = Field(
        default="python", 
        description="Programming language (python, javascript, etc.)"
    )
    context: Optional[str] = Field(
        default=None, 
        description="Additional context about what the code does"
    )

    class Config:
        example = {
            "code": "def add(a, b):\n    return a + b",
            "language": "python",
            "context": "Simple addition function"
        }


class CodeReviewResponse(BaseModel):
    """Complete code review response"""
    summary: str = Field(
        ..., 
        description="High-level summary of the review"
    )
    issues: ReviewCategory = Field(
        ..., 
        description="Issues categorized by type"
    )
    overall_quality_score: float = Field(
        ..., 
        ge=0.0, 
        le=100.0,
        description="Overall quality score (0-100)"
    )
    main_recommendations: List[str] = Field(
        ..., 
        description="Top 3-5 recommendations for improvement"
    )


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(
        default="healthy",
        description="Service status"
    )
    service: str = Field(
        default="PR Review Agent API",
        description="Service name"
    )
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from app.schemas import CodeReviewRequest, CodeReviewResponse, HealthResponse
from app.services.claude_reviewer import ClaudeCodeReviewer

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="PR Review Agent",
    description="AI-powered code review using Claude",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    """Return no favicon to avoid browser 404 noise."""
    return JSONResponse(status_code=204, content=None)


# Initialize Claude reviewer
try:
    reviewer = ClaudeCodeReviewer()
except ValueError as e:
    print(f"Warning: {e}")
    reviewer = None


@app.get("/", tags=["Health"])
async def root():
    """Welcome endpoint with instructions"""
    return {
        "message": "PR Review Agent API",
        "version": "1.0.0",
        "endpoints": {
            "review": "POST /review - Submit code for review",
            "health": "GET /health - Health check",
            "docs": "GET /docs - Interactive API documentation"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse()


@app.post("/review", response_model=CodeReviewResponse, tags=["Review"])
async def review_code(request: CodeReviewRequest):
    """
    Review code using Claude AI
    
    **Request body:**
    - `code`: The code snippet or PR diff to review (required)
    - `language`: Programming language (default: "python")
    - `context`: Optional context about what the code does
    
    **Response:**
    Returns a detailed code review with:
    - Summary of the code and review
    - Issues categorized by type (bugs, style, performance, security)
    - Overall quality score (0-100)
    - Main recommendations for improvement
    """
    
    if not reviewer:
        raise HTTPException(
            status_code=500,
            detail="Claude reviewer not initialized. Check ANTHROPIC_API_KEY environment variable."
        )
    
    try:
        # Validate code is not empty
        if not request.code or len(request.code.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Code cannot be empty"
            )
        
        # Call Claude reviewer
        review = reviewer.review_code(
            code=request.code,
            language=request.language,
            context=request.context
        )
        
        return review
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reviewing code: {str(e)}"
        )


@app.post("/review/batch", tags=["Review"])
async def review_multiple_files(files: list[CodeReviewRequest]):
    """
    Review multiple code files at once
    
    Returns a list of reviews for each file
    """
    
    if not reviewer:
        raise HTTPException(
            status_code=500,
            detail="Claude reviewer not initialized"
        )
    
    reviews = []
    for file_request in files:
        try:
            review = reviewer.review_code(
                code=file_request.code,
                language=file_request.language,
                context=file_request.context
            )
            reviews.append(review)
        except Exception as e:
            reviews.append({
                "error": f"Failed to review file: {str(e)}"
            })
    
    return {"reviews": reviews}


@app.get("/docs-example", tags=["Help"])
async def example():
    """Example of how to use the API"""
    return {
        "example_request": {
            "code": "def hello():\n    print('Hello world')",
            "language": "python",
            "context": "Simple greeting function"
        },
        "curl_example": "curl -X POST 'http://localhost:8000/review' -H 'Content-Type: application/json' -d '{\"code\": \"def add(a, b):\\n    return a + b\", \"language\": \"python\"}'",
        "python_example": "import requests\nresponse = requests.post('http://localhost:8000/review', json={'code': 'def add(a, b):\\n    return a + b', 'language': 'python'})\nprint(response.json())"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
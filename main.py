from fastapi import FastAPI, APIRouter, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from datetime import datetime
from typing import Optional
import uvicorn

from schema import (
    SigninSchema, SignupSchema, UserUpdateSchema,
    ResourceCreateSchema, ResourceUpdateSchema, BookingCreateSchema
)

app = FastAPI(title="API Gateway for Resource Booking System", version="1.0.0")
router = APIRouter()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# OPTIONS handler for CORS preflight

@app.options("/{path:path}")
async def options_handler(path: str):
    return JSONResponse(content={"message": "OK"}, status_code=200)

# Backend URLs
SPRING_BOOT_URL = "https://microservices-xdy6.onrender.com"  # PostgreSQL - Users
NODE_JS_URL = "https://server-dz33.onrender.com"       # MongoDB - Resources & Bookings

# ==================== Root Endpoints ====================
@app.get("/")
def welcome():
    return {"message": "API Gateway for Resource Booking System"}

@app.get("/test")
def test():
    return {"message": "API Gateway is running"}

@app.get("/health")
async def health_check():
    """Health Check Endpoint"""
    services = {
        "gateway": "healthy",
        "spring_boot": "unknown",
        "node_js": "unknown"
    }
    
    # Check Spring Boot
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(f"{SPRING_BOOT_URL}/authservice/")
            if response.status_code == 200:
                services["spring_boot"] = "healthy"
            else:
                services["spring_boot"] = "unhealthy"
        except Exception as e:
            services["spring_boot"] = f"unhealthy"
    
    # Check Node.js
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(f"{NODE_JS_URL}/test")
            if response.status_code == 200:
                services["node_js"] = "healthy"
            else:
                services["node_js"] = "unhealthy"
        except Exception as e:
            services["node_js"] = "unhealthy"
    
    return services

# ==================== AUTH ROUTES -> Spring Boot (PostgreSQL) ====================
@router.post("/authservice/signin")
async def signin(user: SigninSchema):
    print(f"📝 [AUTH] Signin: {user.username} -> Spring Boot")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{SPRING_BOOT_URL}/authservice/signin", json=user.dict())
        return JSONResponse(content=response.json(), status_code=response.status_code)

@router.post("/authservice/signup")
async def signup(user: SignupSchema):
    print(f"📝 [AUTH] Signup: {user.fullname} -> Spring Boot")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{SPRING_BOOT_URL}/authservice/signup", json=user.dict())
        return JSONResponse(content=response.json(), status_code=response.status_code)

@router.get("/authservice/uinfo")
async def uinfo(Token: str = Header(...)):
    print(f"🔐 [AUTH] User info -> Spring Boot")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{SPRING_BOOT_URL}/authservice/uinfo", headers={"Token": Token})
        return JSONResponse(content=response.json(), status_code=response.status_code)

@router.get("/authservice/profile")
async def profile(Token: str = Header(...)):
    print(f"👤 [AUTH] Profile -> Spring Boot")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{SPRING_BOOT_URL}/authservice/profile", headers={"Token": Token})
        return JSONResponse(content=response.json(), status_code=response.status_code)

@router.get("/authservice/getallusers/{page}/{limit}")
async def get_all_users(page: int, limit: int, Token: str = Header(...)):
    print(f"📋 [AUTH] Get all users - page: {page}, limit: {limit} -> Spring Boot")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{SPRING_BOOT_URL}/authservice/getallusers/{page}/{limit}", headers={"Token": Token})
        return JSONResponse(content=response.json(), status_code=response.status_code)

@router.get("/authservice/getuser/{id}")
async def get_user_by_id(id: int, Token: str = Header(...)):
    print(f"👤 [AUTH] Get user by id: {id} -> Spring Boot")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{SPRING_BOOT_URL}/authservice/getuser/{id}", headers={"Token": Token})
        return JSONResponse(content=response.json(), status_code=response.status_code)

@router.post("/authservice/saveuser")
async def save_user(user: SignupSchema, Token: str = Header(...)):
    print(f"💾 [AUTH] Save user: {user.fullname} -> Spring Boot")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{SPRING_BOOT_URL}/authservice/saveuser", json=user.dict(), headers={"Token": Token})
        return JSONResponse(content=response.json(), status_code=response.status_code)

@router.put("/authservice/updateuser/{id}")
async def update_user(id: int, user: SignupSchema, Token: str = Header(...)):
    print(f"✏️ [AUTH] Update user id: {id} -> Spring Boot")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.put(f"{SPRING_BOOT_URL}/authservice/updateuser/{id}", json=user.dict(), headers={"Token": Token})
        return JSONResponse(content=response.json(), status_code=response.status_code)

@router.delete("/authservice/deleteuser/{id}")
async def delete_user(id: int, Token: str = Header(...)):
    print(f"🗑️ [AUTH] Delete user id: {id} -> Spring Boot")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.delete(f"{SPRING_BOOT_URL}/authservice/deleteuser/{id}", headers={"Token": Token})
        return JSONResponse(content=response.json(), status_code=response.status_code)

# ==================== RESOURCE ROUTES -> Node.js (MongoDB) ====================
@router.post("/resource/add")
async def add_resource(request: Request, Token: str = Header(...)):
    """Add new resource - Node.js MongoDB"""
    try:
        body = await request.json()
        print(f"➕ [RESOURCE] Add resource -> Node.js: {body.get('resource_name')}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{NODE_JS_URL}/api/createresource",
                json=body,
                headers={"token": Token, "Content-Type": "application/json"}
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(status_code=500, content={"code": 500, "message": str(e)})

@router.get("/resource/getall")
async def get_all_resources(Token: str = Header(...)):
    """Get all resources - Node.js MongoDB"""
    print(f"📦 [RESOURCE] Get all resources -> Node.js")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{NODE_JS_URL}/api/getallresources/1/100",
            headers={"token": Token}
        )
        return JSONResponse(content=response.json(), status_code=response.status_code)

@router.get("/resource/available")
async def get_available_resources(Token: str = Header(...)):
    """Get available resources - Node.js MongoDB"""
    print(f"✅ [RESOURCE] Get available resources -> Node.js")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{NODE_JS_URL}/api/getavailableresources/1/100",
            headers={"token": Token}
        )
        return JSONResponse(content=response.json(), status_code=response.status_code)

@router.get("/resource/getbyid/{resource_id}")
async def get_resource_by_id(resource_id: str, Token: str = Header(...)):
    """Get resource by ID - Node.js MongoDB"""
    print(f"🔍 [RESOURCE] Get resource by id: {resource_id} -> Node.js")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{NODE_JS_URL}/api/getresource/{resource_id}",
            headers={"token": Token}
        )
        return JSONResponse(content=response.json(), status_code=response.status_code)

@router.put("/resource/update/{resource_id}")
async def update_resource(resource_id: str, request: Request, Token: str = Header(...)):
    """Update resource - Node.js MongoDB"""
    try:
        body = await request.json()
        print(f"✏️ [RESOURCE] Update resource {resource_id} -> Node.js")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.put(
                f"{NODE_JS_URL}/api/updateresource/{resource_id}",
                json=body,
                headers={"token": Token, "Content-Type": "application/json"}
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(status_code=500, content={"code": 500, "message": str(e)})

@router.delete("/resource/delete/{resource_id}")
async def delete_resource(resource_id: str, Token: str = Header(...)):
    """Delete resource - Node.js MongoDB"""
    print(f"🗑️ [RESOURCE] Delete resource: {resource_id} -> Node.js")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.delete(
            f"{NODE_JS_URL}/api/deleteresource/{resource_id}",
            headers={"token": Token}
        )
        return JSONResponse(content=response.json(), status_code=response.status_code)

# Vector Search - Node.js MongoDB
@router.get("/resource/search/{query}/{limit}")
async def search_resources(query: str, limit: int = 10, Token: str = Header(...)):
    """Semantic search resources using vector embeddings - Node.js MongoDB"""
    print(f"🔍 [SEARCH] Searching for: {query} -> Node.js")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{NODE_JS_URL}/api/searchresources/{query}/{limit}",
            headers={"token": Token}
        )
        return JSONResponse(content=response.json(), status_code=response.status_code)

# Bulk create embeddings
@router.post("/resource/bulkembeddings")
async def bulk_embeddings(Token: str = Header(...)):
    """Create vector embeddings for all resources - Node.js MongoDB"""
    print(f"🧠 [EMBEDDINGS] Creating bulk embeddings -> Node.js")
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{NODE_JS_URL}/api/bulkembeddings",
            headers={"token": Token}
        )
        return JSONResponse(content=response.json(), status_code=response.status_code)

# ==================== BOOKING ROUTES -> Node.js (MongoDB) ====================
@router.post("/booking/book")
async def book_resource(request: Request, Token: str = Header(...)):
    """Book a resource - Node.js MongoDB"""
    try:
        body = await request.json()
        print(f"📖 [BOOKING] Book resource -> Node.js: {body}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{NODE_JS_URL}/api/createbooking",
                json=body,
                headers={"token": Token, "Content-Type": "application/json"}
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse(status_code=500, content={"code": 500, "message": str(e)})

@router.get("/booking/mybookings")
async def get_my_bookings(Token: str = Header(...)):
    """Get my bookings - Node.js MongoDB"""
    print(f"📋 [BOOKING] Get my bookings -> Node.js")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{NODE_JS_URL}/api/getmybookings/1/100",
            headers={"token": Token}
        )
        return JSONResponse(content=response.json(), status_code=response.status_code)

@router.put("/booking/cancel/{booking_id}")
async def cancel_booking(booking_id: str, Token: str = Header(...)):
    """Cancel booking - Node.js MongoDB"""
    print(f"❌ [BOOKING] Cancel booking: {booking_id} -> Node.js")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.put(
            f"{NODE_JS_URL}/api/cancelbooking/{booking_id}",
            headers={"token": Token}
        )
        return JSONResponse(content=response.json(), status_code=response.status_code)

@router.get("/booking/all")
async def get_all_bookings(Token: str = Header(...)):
    """Get all bookings (Admin only) - Node.js MongoDB"""
    print(f"📊 [BOOKING] Get all bookings -> Node.js")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{NODE_JS_URL}/api/getallbookings/1/100",
            headers={"token": Token}
        )
        return JSONResponse(content=response.json(), status_code=response.status_code)

@router.get("/booking/get/{booking_id}")
async def get_booking_by_id(booking_id: str, Token: str = Header(...)):
    """Get booking by ID - Node.js MongoDB"""
    print(f"🔍 [BOOKING] Get booking by id: {booking_id} -> Node.js")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{NODE_JS_URL}/api/getbooking/{booking_id}",
            headers={"token": Token}
        )
        return JSONResponse(content=response.json(), status_code=response.status_code)

# ==================== API Documentation ====================
@router.get("/api-docs")
async def api_docs():
    return {
        "gateway": "http://localhost:8000",
        "backends": {
            "spring_boot": SPRING_BOOT_URL,
            "node_js": NODE_JS_URL
        },
        "databases": {
            "users": "PostgreSQL (Spring Boot)",
            "resources": "MongoDB (Node.js)",
            "bookings": "MongoDB (Node.js)"
        },
        "endpoints": {
            "authentication": [
                {"method": "POST", "path": "/authservice/signin", "description": "User signin"},
                {"method": "POST", "path": "/authservice/signup", "description": "User signup"},
                {"method": "GET", "path": "/authservice/profile", "description": "Get user profile"}
            ],
            "resources": [
                {"method": "POST", "path": "/resource/add", "description": "Add resource"},
                {"method": "GET", "path": "/resource/getall", "description": "Get all resources"},
                {"method": "GET", "path": "/resource/search/{query}/{limit}", "description": "Semantic search"},
                {"method": "PUT", "path": "/resource/update/{id}", "description": "Update resource"},
                {"method": "DELETE", "path": "/resource/delete/{id}", "description": "Delete resource"}
            ],
            "bookings": [
                {"method": "POST", "path": "/booking/book", "description": "Book resource"},
                {"method": "GET", "path": "/booking/mybookings", "description": "Get my bookings"},
                {"method": "PUT", "path": "/booking/cancel/{id}", "description": "Cancel booking"},
                {"method": "GET", "path": "/booking/all", "description": "Get all bookings (Admin)"}
            ]
        }
    }

app.include_router(router)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    
    print("=" * 60)
    print("🚀 API Gateway for Resource Booking System")
    print("=" * 60)
    print(f"📡 Gateway URL: http://0.0.0.0:{port}")
    print(f"🔗 Spring Boot (Users): {SPRING_BOOT_URL}")
    print(f"🔗 Node.js (Resources/Bookings): {NODE_JS_URL}")
    print("=" * 60)
    print("📊 Database Distribution:")
    print("   - Users → PostgreSQL (Spring Boot)")
    print("   - Resources → MongoDB (Node.js)")
    print("   - Bookings → MongoDB (Node.js)")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=port)
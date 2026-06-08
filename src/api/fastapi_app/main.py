from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Ortak veri kaynağı
from src.api.shared_data import (
    CATALOG, get_products_by_category, get_product_by_id,
    authenticate, register_user, get_recommendations,
    add_to_cart, get_cart, remove_from_cart,
    create_order, get_user_orders, cancel_order,
    log_interaction, get_system_stats, users_db,
    update_user_details, change_user_password, delete_user_account
)

app = FastAPI(
    title="ShopAI — Akıllı E-Ticaret Öneri Sistemi API",
    description="Müşteri davranışlarını analiz ederek kişiselleştirilmiş ürün önerileri sunan REST API.",
    version="1.0.0"
)

# CORS — Frontend'in API'ye erişimi için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic Modeller ──

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "user"

class CartAddRequest(BaseModel):
    product_id: int
    qty: int = 1

class InteractionRequest(BaseModel):
    user_id: int
    product_id: int
    type: str  # "view", "cart", "purchase", "favorite"

class OrderRequest(BaseModel):
    user_email: str

class OrderCreateRequest(BaseModel):
    shipping_address: Optional[dict] = None
    payment_method: Optional[str] = None

class UpdateProfileRequest(BaseModel):
    name: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


# ═══════════════════════════════════════════════
# HEALTH
# ═══════════════════════════════════════════════

@app.get("/api/health", tags=["Sistem"])
def health_check():
    """Sistem sağlık kontrolü"""
    stats = get_system_stats()
    return {
        "status": "ok",
        "message": "ShopAI API çalışıyor",
        **stats
    }

# ═══════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════

@app.post("/api/v1/auth/login", tags=["Kimlik Doğrulama"])
def api_login(req: LoginRequest):
    """Kullanıcı girişi"""
    result = authenticate(req.email, req.password)
    if result:
        return result
    raise HTTPException(status_code=401, detail="Geçersiz e-posta veya şifre.")

@app.post("/api/v1/auth/register", tags=["Kimlik Doğrulama"])
def api_register(req: RegisterRequest):
    """Yeni kullanıcı kaydı"""
    result = register_user(req.name, req.email, req.password, req.role)
    if "error" in result:
        raise HTTPException(status_code=409, detail=result["error"])
    return result

# ═══════════════════════════════════════════════
# PRODUCTS
# ═══════════════════════════════════════════════

@app.get("/api/v1/products", tags=["Ürünler"])
def list_products(category: Optional[str] = Query(None, description="Kategori filtresi")):
    """Tüm ürünleri listele, isteğe bağlı kategori filtresi"""
    products = get_products_by_category(category)
    return {
        "count": len(products),
        "products": products
    }

@app.get("/api/v1/products/{product_id}", tags=["Ürünler"])
def get_product_detail(product_id: int):
    """Ürün detay bilgisi"""
    product = get_product_by_id(product_id)
    if product:
        return product
    raise HTTPException(status_code=404, detail="Ürün bulunamadı.")

# ═══════════════════════════════════════════════
# RECOMMENDATIONS
# ═══════════════════════════════════════════════

@app.get("/api/v1/recommendations/{user_id}", tags=["Öneriler"])
def api_recommendations(user_id: int, top_n: int = Query(8, ge=1, le=18)):
    """Kullanıcıya özel kişiselleştirilmiş ürün önerileri"""
    recommendations = get_recommendations(user_id, top_n)
    return {
        "user_id": user_id,
        "optimization_status": "High Accuracy Mode",
        "results_count": len(recommendations),
        "recommendations": recommendations
    }

# ═══════════════════════════════════════════════
# INTERACTIONS
# ═══════════════════════════════════════════════

@app.post("/api/v1/interactions", tags=["Etkileşimler"])
def api_log_interaction(req: InteractionRequest):
    """Kullanıcı etkileşimi kaydet (görüntüleme, sepet, satın alma)"""
    log_interaction(req.user_id, req.product_id, req.type)
    return {"status": "logged", "type": req.type}

# ═══════════════════════════════════════════════
# USERS (Admin)
# ═══════════════════════════════════════════════

@app.get("/api/v1/users", tags=["Kullanıcılar"])
def list_users():
    """Kayıtlı kullanıcıları listele (Admin paneli için)"""
    safe_users = [{k: v for k, v in u.items() if k != "password"} for u in users_db]
    return {
        "count": len(safe_users),
        "users": safe_users
    }

# ═══════════════════════════════════════════════
# CART
# ═══════════════════════════════════════════════

@app.get("/api/v1/cart/{user_email}", tags=["Sepet"])
def api_get_cart(user_email: str):
    """Kullanıcının sepetini getir"""
    return get_cart(user_email)

@app.post("/api/v1/cart/{user_email}", tags=["Sepet"])
def api_add_to_cart(user_email: str, req: CartAddRequest):
    """Sepete ürün ekle"""
    product = get_product_by_id(req.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı.")
    return add_to_cart(user_email, req.product_id, req.qty)

@app.delete("/api/v1/cart/{user_email}/{product_id}", tags=["Sepet"])
def api_remove_from_cart(user_email: str, product_id: int):
    """Sepetten ürün çıkar"""
    return remove_from_cart(user_email, product_id)

# ═══════════════════════════════════════════════
# ORDERS
# ═══════════════════════════════════════════════

@app.get("/api/v1/orders/{user_email}", tags=["Siparişler"])
def api_get_orders(user_email: str):
    """Kullanıcının siparişlerini listele"""
    orders = get_user_orders(user_email)
    return {
        "count": len(orders),
        "orders": orders
    }

@app.post("/api/v1/orders/{user_email}", tags=["Siparişler"])
def api_create_order(user_email: str, req: Optional[OrderCreateRequest] = None):
    """Sepetteki ürünlerden sipariş oluştur"""
    shipping = req.shipping_address if req else None
    payment = req.payment_method if req else None
    result = create_order(user_email, shipping, payment)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/api/v1/orders/{user_email}/cancel/{order_id}", tags=["Siparişler"])
def api_cancel_order(user_email: str, order_id: str):
    """Siparişi iptal et"""
    result = cancel_order(user_email, order_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

# ═══════════════════════════════════════════════
# PROFILE & ACCOUNT MANAGEMENT
# ═══════════════════════════════════════════════

@app.post("/api/v1/users/profile/update-details/{email}", tags=["Profil"])
def api_update_details(email: str, req: UpdateProfileRequest):
    """Kullanıcı ad soyad bilgilerini güncelle"""
    result = update_user_details(email, req.name)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.post("/api/v1/users/profile/change-password/{email}", tags=["Profil"])
def api_change_password(email: str, req: ChangePasswordRequest):
    """Kullanıcı şifresini değiştir"""
    result = change_user_password(email, req.old_password, req.new_password)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.delete("/api/v1/users/profile/{email}", tags=["Profil"])
def api_delete_account(email: str):
    """Kullanıcı hesabını kalıcı olarak sil"""
    result = delete_user_account(email)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ═══════════════════════════════════════════════
# ROOT — Frontend serve
# ═══════════════════════════════════════════════


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "ShopAI API'sine Hoş Geldiniz!",
        "docs": "/docs",
        "health": "/api/health"
    }

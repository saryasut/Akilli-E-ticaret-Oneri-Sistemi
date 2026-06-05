# ═══════════════════════════════════════════════
# Shared Data Module — Ortak Veri Kaynağı
# FastAPI ve Flask tarafından kullanılır
# ═══════════════════════════════════════════════

from datetime import datetime
import hashlib
import secrets

# ── Ürün Kataloğu (Frontend CATALOG ile senkron) ──
CATALOG = [
    {"id": 101, "name": "Premium Kablosuz Kulaklık",  "category": "Elektronik", "price": 1499, "stock": 45, "icon": "🎧", "desc": "Aktif gürültü engelleme özellikli, 30 saat pil ömrü."},
    {"id": 102, "name": "Mekanik Klavye Pro",          "category": "Elektronik", "price": 2199, "stock": 22, "icon": "⌨️", "desc": "Cherry MX Blue switch, RGB aydınlatma, alüminyum gövde."},
    {"id": 103, "name": "Ergonomik Mouse",             "category": "Elektronik", "price": 899,  "stock": 38, "icon": "🖱️", "desc": "Dikey tasarım, bilek desteği, kablosuz bağlantı."},
    {"id": 104, "name": "4K Monitör 27\"",              "category": "Elektronik", "price": 8499, "stock": 12, "icon": "🖥️", "desc": "IPS panel, HDR10, %99 sRGB renk doğruluğu."},
    {"id": 105, "name": "Taşınabilir SSD 1TB",         "category": "Elektronik", "price": 1899, "stock": 55, "icon": "💾", "desc": "USB-C, 1050MB/s okuma hızı, şok dayanıklı."},
    {"id": 201, "name": "Yoga Matı ve Seti",           "category": "Spor",       "price": 349,  "stock": 80, "icon": "🧘", "desc": "6mm kalınlık, kaymaz yüzey, taşıma çantası dahil."},
    {"id": 202, "name": "Akıllı Fitness Bilekliği",    "category": "Spor",       "price": 1299, "stock": 33, "icon": "⌚", "desc": "Nabız ölçer, uyku takibi, 7 gün pil ömrü."},
    {"id": 203, "name": "Dambıl Seti 20kg",            "category": "Spor",       "price": 699,  "stock": 28, "icon": "🏋️", "desc": "Ayarlanabilir ağırlık, neopren kaplama."},
    {"id": 204, "name": "Koşu Bandı",                  "category": "Spor",       "price": 4999, "stock": 8,  "icon": "🏃", "desc": "Katlanabilir, 12 program, eğim ayarı."},
    {"id": 301, "name": "Bestseller Kitap Seti",       "category": "Hobi",       "price": 249,  "stock": 95, "icon": "📚", "desc": "2026 çok satanlar, 5 kitaplık özel set."},
    {"id": 302, "name": "Puzzle 1000 Parça",           "category": "Hobi",       "price": 179,  "stock": 60, "icon": "🧩", "desc": "Doğa manzarası, parlak baskı kalitesi."},
    {"id": 303, "name": "Suluboya Seti Premium",       "category": "Hobi",       "price": 449,  "stock": 42, "icon": "🎨", "desc": "48 renk, profesyonel fırçalar, ahşap kutu."},
    {"id": 401, "name": "Akıllı Ev Aydınlatma Seti",   "category": "Ev",         "price": 599,  "stock": 35, "icon": "💡", "desc": "Wi-Fi kontrol, 16M renk, ses asistanı uyumlu."},
    {"id": 402, "name": "Robot Süpürge",               "category": "Ev",         "price": 3499, "stock": 15, "icon": "🤖", "desc": "Lazer navigasyon, otomatik boşaltma, uygulama kontrolü."},
    {"id": 403, "name": "Kahve Makinesi",              "category": "Ev",         "price": 2799, "stock": 20, "icon": "☕", "desc": "Espresso ve filtre kahve, dahili öğütücü."},
    {"id": 501, "name": "Pamuklu T-Shirt",             "category": "Giyim",      "price": 199,  "stock": 120,"icon": "👕", "desc": "Organik pamuk, rahat kesim, 5 renk seçeneği."},
    {"id": 502, "name": "Deri Cüzdan",                 "category": "Giyim",      "price": 449,  "stock": 50, "icon": "👛", "desc": "El yapımı, RFID koruma, hediye kutusunda."},
    {"id": 503, "name": "Spor Ayakkabı",               "category": "Giyim",      "price": 1599, "stock": 40, "icon": "👟", "desc": "Hafif taban, nefes alan kumaş, yürüyüş ve koşu."},
]

# ── Varsayılan Kullanıcılar ──
DEFAULT_USERS = [
    {"id": 1, "name": "İsmail Özdemir", "email": "admin@shopai.com",  "password": "123456", "role": "admin", "date": "2026-01-15"},
    {"id": 2, "name": "Ayşe Demir",     "email": "ayse@shopai.com",   "password": "123456", "role": "user",  "date": "2026-06-01"},
    {"id": 3, "name": "Fatma Yılmaz",   "email": "fatma@shopai.com",  "password": "123456", "role": "user",  "date": "2026-06-02"},
    {"id": 4, "name": "Ali Yücel",      "email": "ali@shopai.com",    "password": "123456", "role": "user",  "date": "2026-06-03"},
]

# ── In-Memory State ──
users_db = list(DEFAULT_USERS)
carts_db = {}      # {user_email: [{product_id, qty}]}
orders_db = []     # [{id, date, items, total, user_email, status}]
interactions_db = []  # [{user_id, product_id, type, timestamp}]
_next_user_id = 5

# ── Yardımcı Fonksiyonlar ──

def get_categories():
    """Benzersiz kategori listesi"""
    return list(set(p["category"] for p in CATALOG))


def get_products_by_category(category=None):
    """Kategoriye göre filtrelenmiş ürün listesi"""
    if category and category != "Tümü":
        return [p for p in CATALOG if p["category"] == category]
    return CATALOG


def get_product_by_id(product_id):
    """ID'ye göre ürün bul"""
    return next((p for p in CATALOG if p["id"] == product_id), None)


def authenticate(email, password):
    """Kullanıcı doğrulama — başarılıysa kullanıcı dict döner"""
    user = next(
        (u for u in users_db if u["email"].lower() == email.lower() and u["password"] == password),
        None
    )
    if user:
        token = secrets.token_hex(16)
        return {
            "token": token,
            "user": {k: v for k, v in user.items() if k != "password"}
        }
    return None


def register_user(name, email, password, role="user"):
    """Yeni kullanıcı kaydı"""
    global _next_user_id
    if any(u["email"].lower() == email.lower() for u in users_db):
        return {"error": "Bu e-posta adresi zaten kayıtlı."}
    
    new_user = {
        "id": _next_user_id,
        "name": name,
        "email": email,
        "password": password,
        "role": role,
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    _next_user_id += 1
    users_db.append(new_user)
    return {"success": True, "user_id": new_user["id"]}


def get_recommendations(user_id, top_n=8):
    """Basit öneri motoru — kategori bazlı benzerlik skoru"""
    import random
    random.seed(user_id)
    
    scored = []
    for p in CATALOG:
        # Kullanıcı ID'sine göre deterministik skor üret
        score_base = hash(f"{user_id}-{p['id']}") % 100 / 100
        score = max(0.55, min(0.99, score_base * 0.4 + 0.6))
        scored.append({**p, "similarity_score": round(score, 2)})
    
    scored.sort(key=lambda x: x["similarity_score"], reverse=True)
    return scored[:top_n]


def add_to_cart(user_email, product_id, qty=1):
    """Sepete ürün ekle"""
    if user_email not in carts_db:
        carts_db[user_email] = []
    
    cart = carts_db[user_email]
    existing = next((item for item in cart if item["product_id"] == product_id), None)
    
    if existing:
        existing["qty"] += qty
    else:
        cart.append({"product_id": product_id, "qty": qty})
    
    return get_cart(user_email)


def get_cart(user_email):
    """Kullanıcının sepetini ürün detaylarıyla birlikte döndür"""
    raw_cart = carts_db.get(user_email, [])
    detailed = []
    for item in raw_cart:
        product = get_product_by_id(item["product_id"])
        if product:
            detailed.append({
                **product,
                "qty": item["qty"],
                "line_total": product["price"] * item["qty"]
            })
    
    subtotal = sum(d["line_total"] for d in detailed)
    shipping = 0 if subtotal > 500 else 29.90
    
    return {
        "items": detailed,
        "subtotal": subtotal,
        "shipping": shipping,
        "total": subtotal + shipping
    }


def remove_from_cart(user_email, product_id):
    """Sepetten ürün çıkar"""
    if user_email in carts_db:
        carts_db[user_email] = [i for i in carts_db[user_email] if i["product_id"] != product_id]
    return get_cart(user_email)


def create_order(user_email):
    """Sepetteki ürünlerden sipariş oluştur"""
    cart_data = get_cart(user_email)
    if not cart_data["items"]:
        return {"error": "Sepet boş."}
    
    order = {
        "id": f"SHP-{secrets.token_hex(4).upper()}",
        "date": datetime.now().isoformat(),
        "items": [{"name": i["name"], "qty": i["qty"], "price": i["price"], "icon": i["icon"]} for i in cart_data["items"]],
        "subtotal": cart_data["subtotal"],
        "shipping": cart_data["shipping"],
        "total": cart_data["total"],
        "status": "processing",
        "user_email": user_email
    }
    
    orders_db.insert(0, order)
    carts_db[user_email] = []  # Sepeti temizle
    
    return order


def get_user_orders(user_email):
    """Kullanıcının siparişlerini getir"""
    return [o for o in orders_db if o["user_email"] == user_email]


def log_interaction(user_id, product_id, interaction_type):
    """Kullanıcı etkileşimi kaydet"""
    interactions_db.append({
        "user_id": user_id,
        "product_id": product_id,
        "type": interaction_type,
        "timestamp": datetime.now().isoformat()
    })
    return True


def get_system_stats():
    """Admin paneli için sistem istatistikleri"""
    return {
        "total_users": len(users_db),
        "total_products": len(CATALOG),
        "total_orders": len(orders_db),
        "total_interactions": len(interactions_db),
        "categories": get_categories(),
        "api_version": "1.0.0",
        "python_version": "3.14.3",
        "uptime": datetime.now().isoformat()
    }

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

from src.api.shared_data import (
    CATALOG, get_products_by_category, get_product_by_id,
    authenticate, register_user, get_recommendations,
    add_to_cart, get_cart, remove_from_cart,
    create_order, get_user_orders, cancel_order,
    log_interaction, get_system_stats, users_db,
    update_user_details, change_user_password, delete_user_account
)

app = Flask(__name__)
CORS(app)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# ═══════════════════════════════════════════════
# HEALTH
# ═══════════════════════════════════════════════

@app.route('/api/health')
def health_check():
    """Sistem sağlık kontrolü"""
    stats = get_system_stats()
    return jsonify({"status": "ok", "message": "ShopAI Flask API çalışıyor", **stats})

# ═══════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════

@app.route('/api/v1/auth/login', methods=['POST'])
def api_login():
    """Kullanıcı girişi"""
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "E-posta ve şifre gereklidir."}), 400

    result = authenticate(data["email"], data["password"])
    if result:
        app.logger.info(f"Kullanıcı giriş yaptı: {data['email']}")
        return jsonify(result)
    return jsonify({"error": "Geçersiz e-posta veya şifre."}), 401

@app.route('/api/v1/auth/register', methods=['POST'])
def api_register():
    """Yeni kullanıcı kaydı"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Geçersiz istek."}), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    role = data.get("role", "user")

    if not all([name, email, password]):
        return jsonify({"error": "Tüm alanlar zorunludur."}), 400

    result = register_user(name, email, password, role)
    if "error" in result:
        return jsonify(result), 409

    app.logger.info(f"Yeni kullanıcı kaydı: {email}")
    return jsonify(result), 201

# ═══════════════════════════════════════════════
# PRODUCTS
# ═══════════════════════════════════════════════

@app.route('/api/v1/products')
def list_products():
    """Tüm ürünleri listele"""
    category = request.args.get("category")
    products = get_products_by_category(category)
    return jsonify({"count": len(products), "products": products})

@app.route('/api/v1/products/<int:product_id>')
def get_product_detail(product_id):
    """Ürün detay bilgisi"""
    product = get_product_by_id(product_id)
    if product:
        return jsonify(product)
    return jsonify({"error": "Ürün bulunamadı."}), 404

# ═══════════════════════════════════════════════
# RECOMMENDATIONS
# ═══════════════════════════════════════════════

@app.route('/api/v1/recommendations/<int:user_id>')
def api_recommendations(user_id):
    """Kullanıcıya özel ürün önerileri"""
    top_n = request.args.get("top_n", 8, type=int)
    recommendations = get_recommendations(user_id, min(max(top_n, 1), 18))

    app.logger.info(f"Kullanıcı {user_id} için {len(recommendations)} öneri üretildi.")
    return jsonify({
        "user_id": user_id,
        "optimization_status": "High Accuracy Mode",
        "results_count": len(recommendations),
        "recommendations": recommendations
    })

# ═══════════════════════════════════════════════
# INTERACTIONS
# ═══════════════════════════════════════════════

@app.route('/api/v1/interactions', methods=['POST'])
def api_log_interaction():
    """Kullanıcı etkileşimi kaydet"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Geçersiz istek."}), 400

    log_interaction(data.get("user_id"), data.get("product_id"), data.get("type", "view"))
    return jsonify({"status": "logged", "type": data.get("type")})

# ═══════════════════════════════════════════════
# USERS (Admin)
# ═══════════════════════════════════════════════

@app.route('/api/v1/users')
def list_users():
    """Kayıtlı kullanıcıları listele"""
    safe_users = [{k: v for k, v in u.items() if k != "password"} for u in users_db]
    return jsonify({"count": len(safe_users), "users": safe_users})

# ═══════════════════════════════════════════════
# CART
# ═══════════════════════════════════════════════

@app.route('/api/v1/cart/<user_email>', methods=['GET'])
def api_get_cart(user_email):
    """Kullanıcının sepetini getir"""
    return jsonify(get_cart(user_email))

@app.route('/api/v1/cart/<user_email>', methods=['POST'])
def api_add_to_cart(user_email):
    """Sepete ürün ekle"""
    data = request.get_json()
    if not data or "product_id" not in data:
        return jsonify({"error": "product_id gereklidir."}), 400

    product = get_product_by_id(data["product_id"])
    if not product:
        return jsonify({"error": "Ürün bulunamadı."}), 404

    return jsonify(add_to_cart(user_email, data["product_id"], data.get("qty", 1)))

@app.route('/api/v1/cart/<user_email>/<int:product_id>', methods=['DELETE'])
def api_remove_from_cart(user_email, product_id):
    """Sepetten ürün çıkar"""
    return jsonify(remove_from_cart(user_email, product_id))

# ═══════════════════════════════════════════════
# ORDERS
# ═══════════════════════════════════════════════

@app.route('/api/v1/orders/<user_email>', methods=['GET'])
def api_get_orders(user_email):
    """Kullanıcının siparişlerini listele"""
    orders = get_user_orders(user_email)
    return jsonify({"count": len(orders), "orders": orders})

@app.route('/api/v1/orders/<user_email>', methods=['POST'])
def api_create_order(user_email):
    """Sipariş oluştur"""
    data = request.get_json(silent=True) or {}
    shipping = data.get("shipping_address")
    payment = data.get("payment_method")
    result = create_order(user_email, shipping, payment)
    if "error" in result:
        return jsonify(result), 400

    app.logger.info(f"Sipariş oluşturuldu: {result['id']} — {user_email}")
    return jsonify(result), 201

@app.route('/api/v1/orders/<user_email>/cancel/<order_id>', methods=['POST'])
def api_cancel_order(user_email, order_id):
    """Siparişi iptal et"""
    result = cancel_order(user_email, order_id)
    if "error" in result:
        return jsonify(result), 400
    
    app.logger.info(f"Sipariş iptal edildi: {order_id} — {user_email}")
    return jsonify(result), 200

# ═══════════════════════════════════════════════
# PROFILE & ACCOUNT MANAGEMENT
# ═══════════════════════════════════════════════

@app.route('/api/v1/users/profile/update-details/<email>', methods=['POST'])
def api_update_details(email):
    """Kullanıcı ad soyad bilgilerini güncelle"""
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "İsim alanı zorunludur."}), 400
    
    result = update_user_details(email, data["name"])
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)

@app.route('/api/v1/users/profile/change-password/<email>', methods=['POST'])
def api_change_password(email):
    """Kullanıcı şifresini değiştir"""
    data = request.get_json()
    if not data or "old_password" not in data or "new_password" not in data:
        return jsonify({"error": "Eski ve yeni şifre gereklidir."}), 400
    
    result = change_user_password(email, data["old_password"], data["new_password"])
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

@app.route('/api/v1/users/profile/<email>', methods=['DELETE'])
def api_delete_account(email):
    """Kullanıcı hesabını kalıcı olarak sil"""
    result = delete_user_account(email)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)


# ═══════════════════════════════════════════════
# ROOT
# ═══════════════════════════════════════════════


@app.route('/')
def home():
    app.logger.info("Ana sayfa ziyaret edildi.")
    return jsonify({
        "message": "ShopAI Flask API'sine Hoş Geldiniz!",
        "health": "/api/health"
    })

# ═══════════════════════════════════════════════
# ERROR HANDLERS
# ═══════════════════════════════════════════════

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "İstenen kaynak bulunamadı."}), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error("Sunucu iç hatası (500) oluştu.")
    return jsonify({"error": "Sunucu iç hatası."}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)

import logging
import joblib
import os
import sys
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

# ── Loglama: hem dosyaya hem terminale ──
log_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

file_handler = logging.FileHandler('api_logs.log', encoding='utf-8')
file_handler.setFormatter(log_formatter)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_formatter)

app.logger.addHandler(file_handler)
app.logger.addHandler(stream_handler)
app.logger.setLevel(logging.INFO)

# Werkzeug loglarını da terminale yönlendir
logging.getLogger('werkzeug').addHandler(stream_handler)
logging.getLogger('werkzeug').setLevel(logging.INFO)

# ── Model Yükleme ──
recommender = None

def load_model():
    global recommender
    try:
        if os.path.exists("recommender_model.pkl"):
            import recommender as rec_module
            globals()['ProductRecommender'] = rec_module.ProductRecommender
            recommender = joblib.load("recommender_model.pkl")
            app.logger.info("Model basariyla yuklendi.")
            print("✅ Model yuklendi!")
        else:
            app.logger.warning("Model dosyasi bulunamadi, fallback aktif.")
            print("⚠️  Model bulunamadi, fallback kullanilacak.")
    except Exception as e:
        app.logger.error(f"Model yukleme hatasi: {e}")
        print(f"❌ Model hatasi: {e}")

load_model()

# ── Fallback Öneriler ──
FALLBACK = [
    {"product_id": 1, "product_name": "Kablosuz Kulaklık",  "price": 1299, "category": "Teknoloji"},
    {"product_id": 2, "product_name": "Bluetooth Hoparlör", "price": 850,  "category": "Teknoloji"},
    {"product_id": 4, "product_name": "Laptop Standı",      "price": 450,  "category": "Aksesuar"},
]

# ── Endpointler ──

@app.route('/')
def home():
    # templates/ klasörü varsa render_template, yoksa kök dizinden sun
    templates_dir = os.path.join(app.root_path, 'templates')
    if os.path.exists(os.path.join(templates_dir, 'index.html')):
        return render_template('index.html')
    return send_from_directory(app.root_path, 'index.html')


@app.route('/api/v1/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations_v1(user_id):
    try:
        threshold = float(request.args.get('threshold', 0.70))
        top_n     = int(request.args.get('top_n', 5))
    except (ValueError, TypeError):
        return jsonify({"hata": "Geçersiz parametre: threshold float, top_n int olmalıdır."}), 400

    if recommender:
        try:
            results = recommender.recommend(user_id, threshold=threshold, top_n=top_n)
            source  = "scikit-learn"
        except Exception as e:
            app.logger.error(f"Model tahmin hatasi (user_id={user_id}): {e}")
            results = FALLBACK
            source  = "fallback"
    else:
        results = FALLBACK
        source  = "fallback"

    app.logger.info(f"Kullanici {user_id} icin {len(results)} oneri donduruldu ({source}).")

    return jsonify({
        "user_id":         user_id,
        "source":          source,
        "threshold":       threshold,
        "results_count":   len(results),
        "recommendations": results
    })


@app.route('/recommendations/<int:user_id>', methods=['GET'])
def get_ui_recommendations(user_id):
    app.logger.info(f"UI öneri isteği: user_id={user_id}")

    ornek_oneriler = [
        {
            "product_id":   101,
            "product_name": "Kablosuz Kulak İçi Kulaklık",
            "price":        1299,
            "category":     "Ses Sistemleri",
            "resim_url":    "https://picsum.photos/200/200?random=1"
        },
        {
            "product_id":   102,
            "product_name": "Akıllı Saat v2",
            "price":        3499,
            "category":     "Giyilebilir Teknoloji",
            "resim_url":    "https://picsum.photos/200/200?random=2"
        },
        {
            "product_id":   103,
            "product_name": "Ergonomik Oyuncu Mouse",
            "price":        750,
            "category":     "Bilgisayar Bileşenleri",
            "resim_url":    "https://picsum.photos/200/200?random=3"
        },
        {
            "product_id":   104,
            "product_name": "Mekanik Klavye (RGB)",
            "price":        1850,
            "category":     "Bilgisayar Bileşenleri",
            "resim_url":    "https://picsum.photos/200/200?random=4"
        }
    ]
    return jsonify(ornek_oneriler)


@app.route('/track-action', methods=['POST'])
def track_action():
    veri = request.get_json()

    if not veri:
        return jsonify({"hata": "Geçersiz veya boş JSON gövdesi."}), 400

    user_id     = veri.get('user_id')
    product_id  = veri.get('product_id')
    # DÜZELTME: Frontend 'type' gönderiyor, 'action' değil — ikisini de kabul et
    action_type = veri.get('type') or veri.get('action')

    if user_id is None or product_id is None or action_type is None:
        return jsonify({"hata": "Eksik alan: user_id, product_id ve type zorunludur."}), 400

    app.logger.info(f"Etkilesim: user={user_id} | product={product_id} | action={action_type}")

    return jsonify({"status": "success", "message": "Etkileşim başarıyla kaydedildi."})


# ── Hata Yönetimi ──
@app.errorhandler(404)
def not_found(error):
    return jsonify({"hata": "Kaynak bulunamadi"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"hata": "Sunucu hatasi"}), 500


if __name__ == "__main__":
    print("FLASK BAŞLADI")
    print("Sunucu adresi: http://127.0.0.1:8000")
    app.run(host="127.0.0.1", port=8000, debug=False, use_reloader=False)
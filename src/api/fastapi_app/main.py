from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

app = FastAPI(title="E-Ticaret Oneri Sistemi")

# CORS (Cross-Origin Resource Sharing) Ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Canlıda buraya kendi domaininizi yazmanız güvenlidir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sahte veri seti (İleride veritabanından gelecek)
urunler = [
    {"id": 1, "name": "Kablosuz Kulaklık", "category": "Elektronik", "similarity_score": 0.95},
    {"id": 2, "name": "Akıllı Saat", "category": "Elektronik", "similarity_score": 0.85},
    {"id": 3, "name": "Sırt Çantası", "category": "Moda", "similarity_score": 0.72},
    {"id": 4, "name": "Bluetooth Hoparlör", "category": "Elektronik", "similarity_score": 0.82}
]

@app.get("/")
def ana_sayfa():
    # Frontend arayüzünü ana sayfada göster
    html_path = os.path.join("frontend", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"mesaj": "Oneri API'sine Hos Geldiniz (Arayüz bulunamadı)"}

@app.get("/api/v1/recommendations/{user_id}")
def get_recommendations(user_id: int):
    # Şimdilik herkese tüm ürünleri öneren basit bir mantık
    return {
        "user_id": user_id,
        "optimization_status": "High Accuracy Mode",
        "results_count": len(urunler),
        "recommendations": urunler
    }

@app.get("/api/v1/products/{product_id}")
def get_product_detail(product_id: int):
    # Ürün listesinde arama yap
    urun = next((item for item in urunler if item["id"] == product_id), None)
    if urun:
        return urun
    return {"hata": "Urun bulunamadi"}

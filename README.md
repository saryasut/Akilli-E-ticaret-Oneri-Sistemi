# 🚀 Akıllı E-Ticaret Öneri Sistemi

Müşteri davranışlarını ve ürün özelliklerini analiz ederek kişiselleştirilmiş ürün önerileri sunan, kullanıcı deneyimini iyileştiren ve satışları artıran bir yapay zeka destekli e-ticaret platformu.

---

## 📂 Proje Yapısı

```
├── src/                          # Ana kaynak kodları
│   ├── api/
│   │   ├── fastapi_app/          # FastAPI web servisi (Production)
│   │   │   └── main.py           # API endpoint'leri
│   │   ├── flask_app/            # Flask web servisi (Alternatif)
│   │   │   └── app.py            # API endpoint'leri
│   │   └── shared_data.py        # Ortak veri tabanı simülasyonu ve state yönetimi
│   └── models/
│       └── evaluation.py         # Model eğitim ve metrik hesaplama
│
├── frontend/                     # Kullanıcı arayüzü
│   ├── index.html                # Ana sayfa + rol tabanlı SPA
│   ├── css/style.css             # Pastel tema ve bileşen stilleri
│   └── js/app.js                 # Uygulama mantığı ve durum yönetimi
│
├── notebooks/                    # Veri bilimi analizleri
│   ├── e_commerce_predict_system.ipynb
│   ├── recommendation_system_with_amazon.ipynb
│   └── feature_engineering_improvements.ipynb
│
├── db/                           # Veritabanı şemaları ve diyagramlar
│   ├── database.sql              # PostgreSQL tablo tanımları
│   ├── database_schema.png       # PostgreSQL admin şema görünümü
│   ├── er_diagram_current.png    # Güncel ER diyagramı
│   └── er_diagram_v1.png         # İlk versiyon ER diyagramı
│
├── docs/                         # Proje dokümantasyonu
│   ├── proje_sunumu.pdf          # Final Proje Sunumu
│   ├── oneri_algoritmasi_raporu.md
│   ├── model_performance_report.md
│   ├── rest_api_tasarimi.pdf
│   ├── database_optimization.md
│   ├── flask_api.md
│   ├── ui_entegrasyon_plani.md
│   ├── ui_ux_wireframe.md
│   ├── veri_seti_kesfi_ve_on_isleme.md
│   ├── veri_on_isleme_modulu.md
│   ├── veri_on_isleme_iyilestirme.pdf
│   └── akilli_e_ticaret_grafigi.pdf
│
├── proje_akisi.md                # Haftalık ilerleme raporu ve proje akış planı
├── README.md                     # Ana dökümantasyon (şu anki dosya)
├── requirements.txt              # Python bağımlılıkları
├── render.yaml                   # Render.com dağıtım (IaC) yapılandırması
├── .python-version               # Python sürümü (3.14.3)
└── .gitignore                    # Git yoksayma kuralları
```

---

## 🛠️ Teknoloji Yığını

| Katman | Teknoloji | Sürüm |
|--------|-----------|-------|
| **Dil** | Python | 3.14.3 |
| **Backend (Production)** | FastAPI + Uvicorn | 0.136.3 / 0.49.0 |
| **Backend (Alternatif)** | Flask | 3.1.3 |
| **Deployment** | Gunicorn + Render.com | 26.0.0 |
| **Veri Bilimi** | Pandas, NumPy, Scikit-learn | 3.0.3 / 2.4.6 / 1.9.0 |
| **Veritabanı** | PostgreSQL | — |
| **Frontend** | Vanilla HTML/CSS/JS | — |

---

## 📦 Teslim Edilecekler

- ✅ Ürün öneri algoritması (`src/models/evaluation.py`)
- ✅ Veri analiz raporları (`docs/`, `notebooks/`)
- ✅ REST API (`src/api/fastapi_app/`, `src/api/flask_app/`)
- ✅ Kullanıcı arayüzü entegrasyonu (`frontend/`)

---

## 💻 Kurulum ve Çalıştırma

### 1. Depoyu Klonlayın

```bash
git clone https://github.com/250542024/Akilli-E-ticaret-Oneri-Sistemi.git
cd Akilli-E-ticaret-Oneri-Sistemi
```

### 2. Sanal Ortam Oluşturun

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 4. API'yi Başlatın

```bash
# FastAPI (Production — önerilen)
uvicorn src.api.fastapi_app.main:app --reload

# Flask (Alternatif)
python -m src.api.flask_app.app
```

API çalıştıktan sonra:
- **Swagger UI:** http://localhost:8000/docs
- **Frontend:** http://localhost:8000 veya `python -m http.server 8080` ile `frontend/` klasöründen

### 5. Frontend'i Bağımsız Çalıştırın

```bash
cd frontend
python -m http.server 8080
```

Tarayıcıda http://localhost:8080 adresine gidin.

**Varsayılan Hesaplar:**
| Rol | İsim | E-posta | Şifre |
|-----|------|---------|-------|
| **Admin** | İsmail Özdemir | admin@shopai.com | 123456 |
| **Kullanıcı** | Ayşe Demir | ayse@shopai.com | 123456 |
| **Kullanıcı** | Fatma Yılmaz | fatma@shopai.com | 123456 |
| **Kullanıcı** | Ali Yücel | ali@shopai.com | 123456 |

---

## 🌐 Deployment (Render.com)

Proje `render.yaml` ile otomatik deploy edilecek şekilde yapılandırılmıştır:

1. Repoyu GitHub'a push edin
2. Render.com → **New > Blueprint** → Bu repoyu bağlayın
3. Backend API ve Frontend otomatik olarak ayağa kalkacaktır

---

## 🧠 Kullanıcı Arayüzü

### Rol Tabanlı Erişim

| Rol | Özellikler |
|-----|-----------|
| **Admin** | Genel bakış, kayıtlı kullanıcılar, sistem durumu, ürün önerileri analizi, davranış analizi |
| **Kullanıcı** | Ürün kataloğu (6 kategori, 18 ürün), sepet yönetimi, satın alma, sipariş takibi |

### Model Performansı

| Metrik | Değer |
|--------|-------|
| Accuracy | %90 |
| Precision | %70 |
| Recall | %60 |
| F1 Score | %64 |

---

## 📚 Dokümantasyon

| Dosya | İçerik |
|-------|--------|
| `docs/oneri_algoritmasi_raporu.md` | Öneri motorunun matematiksel altyapısı |
| `docs/model_performance_report.md` | Algoritma performans raporları |
| `docs/ui_entegrasyon_plani.md` | API-Frontend haberleşme dokümanı |
| `docs/proje_akisi.md` | Haftalık ilerleme ve görev dağılımı |
| `docs/rest_api_tasarimi.pdf` | REST API tasarım ve belgelendirme |
| `docs/flask_api.md` | Flask API geliştirme detayları |
| `docs/database_optimization.md` | Veritabanı şema tasarımı ve optimizasyonu |

---

## 👥 Ekip

| İsim |
|------|
| İsmail Özdemir |
| Sarya Su Toğyıldız |
| AbdulKadir Demir |
| Elif Babürhan |
| Sema Elmahmud |
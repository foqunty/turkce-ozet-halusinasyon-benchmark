"""Gizli soru setini Hugging Face'e erişim istekli (gated, manual approval) dataset olarak yükler.

Kart (hf/README.md) herkese açık kalır; sorulara yalnızca onaylanan kişiler ulaşır.

Bir kez:
  pip install -U huggingface_hub
  hf auth login            # token'ı kendin gir (write yetkili)
Sonra (benchmark klasöründen):
  python3 scripts/hf_yukle.py                      # repo adı: <kullanıcı>/turkce-ozet-halusinasyon
  python3 scripts/hf_yukle.py baska-ad             # farklı repo adı
"""
import sys

from huggingface_hub import HfApi

from ortak import DATA, ROOT, oku

ad = sys.argv[1] if len(sys.argv) > 1 else "turkce-ozet-halusinasyon"
api = HfApi()
kullanici = api.whoami()["name"]
repo = f"{kullanici}/{ad}"

dosyalar = sorted(DATA.glob("sorular*.csv"))
if not dosyalar:
    sys.exit("data/ altında sorular*.csv yok")
for p in dosyalar:
    print(f"{p.name}: {len(oku(p))} soru")

api.create_repo(repo, repo_type="dataset", private=False, exist_ok=True)
api.update_repo_settings(repo, repo_type="dataset", gated="manual")
api.upload_file(path_or_fileobj=str(ROOT / "hf" / "README.md"), path_in_repo="README.md",
                repo_id=repo, repo_type="dataset", commit_message="Update dataset card")
for p in dosyalar:
    api.upload_file(path_or_fileobj=str(p), path_in_repo=f"data/{p.name}",
                    repo_id=repo, repo_type="dataset", commit_message=f"Upload {p.name}")

ayar = api.dataset_info(repo)
print(f"\nhttps://huggingface.co/datasets/{repo}  · gated={ayar.gated}")
print("Kontrol: tarayıcıda çıkış yapmışken dosyalar görünmemeli, kart görünmeli.")

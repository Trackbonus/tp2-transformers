"""Predice la puntuación de una reseña individual de Metal Archives."""

from pathlib import Path
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = (
    BASE_DIR
    / "resultados"
    / "distilbert"
    / "optimizacion_6_experimentos"
    / "mejor_modelo"
)
MAX_LENGTH = 512
SITE_HOST = "www.metal-archives.com"
TIMEOUT_SECONDS = 20


class AccessForbiddenError(RuntimeError):
    """Metal Archives rechazó la solicitud directa con HTTP 403."""


def validate_review_url(raw_url):
    url = raw_url.strip()
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or parsed.hostname not in {
        SITE_HOST,
        "metal-archives.com",
    }:
        raise ValueError("La URL debe pertenecer a https://www.metal-archives.com/.")
    if not parsed.path.startswith("/reviews/"):
        raise ValueError("La URL no corresponde a la sección de reseñas de álbumes.")
    # Las URLs individuales contienen ID de lanzamiento y, normalmente, ID de reseña.
    if len([part for part in parsed.path.split("/") if part]) < 4:
        raise ValueError("La URL parece ser un listado, no una reseña individual.")
    return url


def extract_review(html):
    """Extrae y valida datos con la misma lógica para HTML web o local."""
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.select_one("h1.album_name, h1")
    band_tag = soup.select_one("h2.band_name, h2")
    if not title_tag or not band_tag:
        raise RuntimeError(
            "No pude identificar los encabezados de álbum y banda; "
            "la estructura HTML puede haber cambiado."
        )
    album = title_tag.get_text(" ", strip=True)
    band = band_tag.get_text(" ", strip=True)

    review_boxes = soup.select("div.reviewBox")
    if not review_boxes:
        raise RuntimeError(
            "No encontré bloques div.reviewBox con reseñas; "
            "la página puede no ser una reseña individual o su HTML cambió."
        )

    # En Metal Archives, la nota está en h3.reviewTitle dentro de cada
    # div.reviewBox (p. ej. "Their best in over a decade - 80%"); el texto
    # completo está en el div.reviewContent hermano, no junto a la nota.
    # Evaluar cada caja mantiene asociadas la nota y su propia reseña.
    candidates = []
    explicit_ratings = 0
    review_texts = 0
    for review_box in review_boxes:
        title = review_box.select_one("h3.reviewTitle")
        content = review_box.select_one("div.reviewContent")
        title_text = title.get_text(" ", strip=True) if title else ""
        text = content.get_text("\n", strip=True) if content else ""
        rating_match = re.search(
            r"[-–—]\s*(\d{1,3}(?:\.\d+)?)\s*%\s*$",
            title_text,
            flags=re.IGNORECASE,
        )
        if rating_match:
            explicit_ratings += 1
            rating = float(rating_match.group(1))
            if not 0 <= rating <= 100:
                continue
            if text:
                review_texts += 1
                candidates.append((text, rating))

    if explicit_ratings == 0:
        raise RuntimeError(
            "No encontré una puntuación explícita en el título "
            "h3.reviewTitle (formato, por ejemplo, '- 80%'). "
            "No se estimará la puntuación real."
        )
    if review_texts == 0:
        raise RuntimeError("No encontré texto de reseña asociado a la puntuación.")
    if len(candidates) != 1:
        raise RuntimeError(
            "Encontré varias reseñas con puntuación en el HTML y no puedo "
            "determinar cuál corresponde a la URL. Usa el HTML de una reseña individual."
        )
    review_text, real_score = candidates[0]
    return {"banda": band, "album": album, "texto": review_text, "real": real_score}


def fetch_review(url):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; ReviewScoreResearch/1.0)"}
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        raise RuntimeError(f"No se pudo conectar con Metal Archives: {exc}") from exc

    if response.status_code == 403:
        raise AccessForbiddenError(
            "Metal Archives rechazó la solicitud automatizada (HTTP 403). "
            "No se intentará eludir esa protección."
        )
    if response.status_code == 404:
        raise RuntimeError("La página de reseña no existe (HTTP 404).")
    if response.status_code == 429:
        raise RuntimeError(
            "Metal Archives limitó la solicitud (HTTP 429). "
            "No se intentará eludir esa protección."
        )
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise RuntimeError(f"Metal Archives respondió con error: {exc}") from exc

    return extract_review(response.content)


def read_local_review(path_text):
    """Lee HTML guardado manualmente; la ruta debe existir en el entorno actual."""
    path_text = path_text.strip().strip('"')
    if not path_text:
        raise ValueError("No se indicó una ruta para el archivo HTML.")
    html_path = Path(path_text).expanduser()
    try:
        html_bytes = html_path.read_bytes()
    except (OSError, ValueError) as exc:
        raise RuntimeError(f"No se pudo leer el archivo HTML '{html_path}': {exc}") from exc
    try:
        return extract_review(html_bytes)
    except RuntimeError as exc:
        raise RuntimeError(f"El HTML local no contiene datos válidos: {exc}") from exc


def predict_text(text, tokenizer, model, device):
    # Igual que evaluar_modelos_finales.py: texto faltante se sustituye por "",
    # truncation, padding max_length y escala de salida multiplicada por 100.
    encoded = tokenizer(
        text or "",
        truncation=True,
        max_length=MAX_LENGTH,
        padding="max_length",
        return_tensors="pt",
    )
    encoded = {key: value.to(device) for key, value in encoded.items()}
    with torch.no_grad():
        score_normalized = model(**encoded).logits.squeeze(-1).item()
    return score_normalized * 100


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Dispositivo:", device)
    print("Cargando tokenizer y checkpoint final…")
    try:
        tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
        model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_DIR))
        model.to(device)
        model.eval()
    except Exception as exc:
        raise RuntimeError(f"No se pudo cargar el checkpoint {MODEL_DIR}: {exc}") from exc

    print("Introduce una URL de reseña individual de Metal Archives (escribe 'salir' para terminar).")
    while True:
        try:
            raw_url = input("URL: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nFinalizando.")
            break
        if raw_url.lower() in {"salir", "exit", "quit"}:
            break
        if not raw_url:
            continue
        try:
            url = validate_review_url(raw_url)
            try:
                review = fetch_review(url)
            except AccessForbiddenError as exc:
                print(f"{exc}")
                print(
                    "Guarda la página de reseña desde el navegador y proporciona "
                    "la ruta al archivo HTML."
                )
                local_path = input("Ruta del archivo HTML (Enter para omitir): ")
                if not local_path.strip():
                    print("Se omitió esta reseña.\n")
                    continue
                review = read_local_review(local_path)
            predicted = predict_text(review["texto"], tokenizer, model, device)
            signed_error = predicted - review["real"]
            print("\n" + "=" * 65)
            print(f"Banda: {review['banda']}")
            print(f"Álbum: {review['album']}")
            print(f"Puntuación real:     {review['real']:.2f}")
            print(f"Puntuación predicha: {predicted:.2f}")
            print(f"Error con signo:     {signed_error:+.2f}")
            print(f"Error absoluto:      {abs(signed_error):.2f}")
            print("=" * 65 + "\n")
        except (ValueError, RuntimeError) as exc:
            print(f"Error: {exc}\n")


if __name__ == "__main__":
    main()

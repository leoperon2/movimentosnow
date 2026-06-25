from flask import Flask, request, jsonify, send_file
import tempfile, os, base64, io, uuid
from gerar_guia import dados_pet, gerar_pdf

app = Flask(__name__)
LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo.png")

# Armazena PDFs temporários em memória {token: bytes}
_pdf_cache = {}

def _build_pet(body):
    import gerar_guia
    gerar_guia.LOGO_PATH = LOGO_PATH
    tutor   = body.get("tutor_nome", "Tutor")
    nome    = body.get("nome_pet", "Pet")
    especie = body.get("especie", "Cão")
    peso    = float(body.get("peso_kg", 10))
    fase    = body.get("fase_vida", "Adulto")
    ativ    = body.get("atividade", "Moderada")
    pet = dados_pet(nome, especie, especie, peso, fase, ativ)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        caminho = tmp.name
    gerar_pdf(pet, tutor_nome=tutor, caminho_saida=caminho)
    with open(caminho, "rb") as f:
        pdf_bytes = f.read()
    os.unlink(caminho)
    return pet, nome, pdf_bytes

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "Snow Dog PDF API"})

@app.route("/gerar-pdf", methods=["POST"])
def gerar():
    try:
        body = request.get_json(force=True)
        pet, nome, pdf_bytes = _build_pet(body)
        token = str(uuid.uuid4())
        _pdf_cache[token] = pdf_bytes
        filename = f"plano_{nome.lower().replace(' ','_')}.pdf"
        host = request.host_url.rstrip("/")
        return jsonify({
            "success": True,
            "filename": filename,
            "download_url": f"{host}/pdf/{token}/{filename}",
            "porcao_g":   pet["porcao_g"],
            "porcao_div": pet["porcao_div"],
            "meta":       pet["meta"]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/pdf/<token>/<filename>", methods=["GET"])
def download_pdf(token, filename):
    pdf_bytes = _pdf_cache.get(token)
    if not pdf_bytes:
        return jsonify({"error": "not found"}), 404
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

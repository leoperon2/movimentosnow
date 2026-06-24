from flask import Flask, request, jsonify
import tempfile, os, base64
from gerar_guia import dados_pet, gerar_pdf

app = Flask(__name__)

LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo.png")

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "Snow Dog PDF API"})

@app.route("/gerar-pdf", methods=["POST"])
def gerar():
    try:
        body = request.get_json(force=True)

        tutor   = body.get("tutor_nome", "Tutor")
        nome    = body.get("nome_pet", "Pet")
        especie = body.get("especie", "Cão")
        raca    = body.get("raca", especie)
        peso    = float(body.get("peso_kg", 10))
        fase    = body.get("fase_vida", "Adulto")
        ativ    = body.get("atividade", "Moderada")

        import gerar_guia
        gerar_guia.LOGO_PATH = LOGO_PATH

        pet = dados_pet(nome, especie, raca, peso, fase, ativ)

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            caminho = tmp.name

        gerar_pdf(pet, tutor_nome=tutor, caminho_saida=caminho)

        with open(caminho, "rb") as f:
            pdf_b64 = base64.b64encode(f.read()).decode("utf-8")

        os.unlink(caminho)

        return jsonify({
            "success": True,
            "filename": f"plano_{nome.lower().replace(' ', '_')}.pdf",
            "pdf_base64": pdf_b64,
            "porcao_g": pet["porcao_g"],
            "porcao_div": pet["porcao_div"],
            "meta": pet["meta"]
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

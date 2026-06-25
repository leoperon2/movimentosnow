from flask import Flask, request, jsonify
import tempfile, os, smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from gerar_guia import dados_pet, gerar_pdf

app = Flask(__name__)
LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo.png")

# Credenciais Gmail via variáveis de ambiente
GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_PASS = os.environ.get("GMAIL_PASS", "")

def enviar_email(destinatario, tutor, nome_pet, porcao_div, pdf_bytes, filename):
    msg = MIMEMultipart()
    msg["From"] = f"Snow Dog <{GMAIL_USER}>"
    msg["To"] = destinatario
    msg["Subject"] = f"🐾 Plano de Movimento do {nome_pet} chegou!"

    corpo = f"""Olá {tutor}!

Seu Plano de Movimento personalizado para o {nome_pet} está em anexo.

Porção diária recomendada Snow Dog: {porcao_div}

Onde houver um cão em movimento, haverá Snow Dog. 🐾

Equipe Movimento Snow Dog
"""
    msg.attach(MIMEText(corpo, "plain", "utf-8"))

    part = MIMEBase("application", "pdf")
    part.set_payload(pdf_bytes)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
    msg.attach(part)

    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()
        smtp.starttls(context=context)
        smtp.login(GMAIL_USER, GMAIL_PASS)
        smtp.sendmail(GMAIL_USER, destinatario, msg.as_bytes())

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "Snow Dog PDF API"})

@app.route("/gerar-pdf", methods=["POST"])
def gerar():
    try:
        import gerar_guia
        gerar_guia.LOGO_PATH = LOGO_PATH

        body       = request.get_json(force=True)
        tutor      = body.get("tutor_nome", "Tutor")
        nome       = body.get("nome_pet", "Pet")
        especie    = body.get("especie", "Cão")
        peso       = float(body.get("peso_kg", 10))
        fase       = body.get("fase_vida", "Adulto")
        ativ       = body.get("atividade", "Moderada")
        email_dest = body.get("email", "")

        pet = dados_pet(nome, especie, especie, peso, fase, ativ)

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            caminho = tmp.name
        gerar_pdf(pet, tutor_nome=tutor, caminho_saida=caminho)
        with open(caminho, "rb") as f:
            pdf_bytes = f.read()
        os.unlink(caminho)

        filename = f"plano_{nome.lower().replace(' ', '_')}.pdf"

        if email_dest and GMAIL_USER and GMAIL_PASS:
            enviar_email(email_dest, tutor, nome, pet["porcao_div"], pdf_bytes, filename)
            email_sent = True
        else:
            email_sent = False

        return jsonify({
            "success":    True,
            "email_sent": email_sent,
            "filename":   filename,
            "porcao_g":   pet["porcao_g"],
            "porcao_div": pet["porcao_div"],
            "meta":       pet["meta"]
        })

    except Exception as e:
        import traceback
        return jsonify({"success": False, "error": str(e), "trace": traceback.format_exc()}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

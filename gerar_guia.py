from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import sys

import os as _os
LOGO_PATH = _os.path.join(_os.path.dirname(__file__), "logo.png")

# ── Cores da marca ──────────────────────────────────────────────
VERDE      = colors.HexColor("#00E676")   # verde neon
ROXO       = colors.HexColor("#4A148C")   # roxo escuro
AZUL_ESC   = colors.HexColor("#0D2137")   # fundo header
CINZA_CLR  = colors.HexColor("#F5F5F5")
BRANCO     = colors.white
PRETO      = colors.HexColor("#1A1A1A")

# ── Estilos ──────────────────────────────────────────────────────
def estilos():
    return {
        "titulo_capa": ParagraphStyle("titulo_capa",
            fontName="Helvetica-Bold", fontSize=28, textColor=VERDE,
            alignment=TA_CENTER, leading=34, spaceAfter=6),
        "sub_capa": ParagraphStyle("sub_capa",
            fontName="Helvetica", fontSize=14, textColor=BRANCO,
            alignment=TA_CENTER, leading=20, spaceAfter=4),
        "nome_pet": ParagraphStyle("nome_pet",
            fontName="Helvetica-Bold", fontSize=20, textColor=VERDE,
            alignment=TA_CENTER, leading=26, spaceAfter=2),
        "secao": ParagraphStyle("secao",
            fontName="Helvetica-Bold", fontSize=13, textColor=ROXO,
            spaceAfter=6, spaceBefore=14),
        "corpo": ParagraphStyle("corpo",
            fontName="Helvetica", fontSize=10.5, textColor=PRETO,
            leading=16, spaceAfter=6, alignment=TA_JUSTIFY),
        "bullet": ParagraphStyle("bullet",
            fontName="Helvetica", fontSize=10.5, textColor=PRETO,
            leading=16, spaceAfter=4, leftIndent=14,
            bulletIndent=4, bulletFontName="Helvetica", bulletFontSize=10),
        "destaque": ParagraphStyle("destaque",
            fontName="Helvetica-Bold", fontSize=11, textColor=ROXO,
            leading=16, spaceAfter=4, alignment=TA_CENTER),
        "rodape": ParagraphStyle("rodape",
            fontName="Helvetica", fontSize=8, textColor=colors.HexColor("#888888"),
            alignment=TA_CENTER),
        "label_tabela": ParagraphStyle("label_tabela",
            fontName="Helvetica-Bold", fontSize=10, textColor=BRANCO,
            alignment=TA_CENTER),
        "val_tabela": ParagraphStyle("val_tabela",
            fontName="Helvetica", fontSize=10, textColor=PRETO,
            alignment=TA_CENTER),
    }

# ── Dados do pet (entrada) ────────────────────────────────────────
def dados_pet(nome, especie, raca, peso_kg, fase, atividade):
    """Retorna dict com plano calculado."""
    peso = float(peso_kg)

    # ── Plano de movimento por perfil ────────────────────────────
    if fase in ("Filhote", "filhote"):
        semanas = [
            ("Semana 1–2", "Passeios curtos de 5 a 10 min, 2x por dia",     "Exploração e socialização"),
            ("Semana 3–4", "Passeios de 10 a 15 min, 2x por dia",           "Construir ritmo e confiança"),
            ("Semana 5–8", "Passeios de 15 a 20 min, 2–3x por dia",         "Desenvolver resistência leve"),
        ]
        obs = ("Filhotes têm ossos em formação — evite impacto alto como corrida ou saltos. "
               "Priorize chão macio (grama, terra) e muita socialização.")
        meta = "Criar hábito de movimento e confiança no ambiente externo."

    elif fase in ("Adulto", "adulto"):
        if atividade in ("Baixa", "baixa"):
            semanas = [
                ("Semana 1–2", "Caminhadas de 20 min, 1x por dia",               "Criar rotina"),
                ("Semana 3–4", "Caminhadas de 30 min, 1–2x por dia",             "Aumentar distância"),
                ("Semana 5–8", "Caminhadas de 40 min ou trote leve de 20 min",   "Elevar intensidade"),
            ]
            obs = "Cães sedentários precisam de progressão gradual. Observe a respiração: se ofegar muito, reduza o ritmo."
            meta = "Estabelecer rotina ativa de pelo menos 40 min diários ao final de 8 semanas."
        elif atividade in ("Moderada", "moderada"):
            semanas = [
                ("Semana 1–2", "Trote leve de 20–25 min, 1x por dia",            "Aquecer a musculatura"),
                ("Semana 3–4", "Trote de 30 min + brincadeira livre 10 min",     "Combinar ritmo e diversão"),
                ("Semana 5–8", "Corrida leve 25 min ou canicross iniciante",     "Introduzir esporte conjunto"),
            ]
            obs = "Seu cão já tem base ativa. O foco agora é consistência e variar os estímulos (cheiros, terrenos, velocidades)."
            meta = "Evoluir para 45–60 min de atividade diária combinando trote, jogo e exploração."
        else:  # Alta
            semanas = [
                ("Semana 1–2", "Corrida de 30 min ou canicross 4–5x/semana",     "Manter base de performance"),
                ("Semana 3–4", "Corrida 35–40 min + treino de obediência",       "Evolução técnica"),
                ("Semana 5–8", "Planeje uma corrida ou evento com seu cão",      "Objetivo concreto"),
            ]
            obs = "Cão com alta atividade precisa de recuperação. Inclua 1–2 dias de descanso ativo (passeio leve) por semana."
            meta = "Participar de um evento de canicross ou corrida com pets nos próximos 60 dias."

    else:  # Sênior
        semanas = [
            ("Semana 1–2", "Passeios calmos de 10–15 min, 2x por dia",      "Mobilidade e bem-estar"),
            ("Semana 3–4", "Passeios de 15–20 min, ritmo do cão",            "Respeitar o pace natural"),
            ("Semana 5–8", "20 min de caminhada + 5 min de natação (se disp.)", "Movimento sem impacto"),
        ]
        obs = ("Cães seniores se beneficiam muito do movimento regular, mas com baixo impacto. "
               "Evite superfícies escorregadias e observe sinais de dor ou cansaço excessivo.")
        meta = "Manter mobilidade, qualidade de vida e vínculo com o tutor através do movimento diário."

    # ── Porção Snow Dog (estimativa orientativa) ─────────────────
    # Base: ~2.5% do peso corporal para adulto moderado
    mult = {"Baixa": 0.020, "baixa": 0.020,
            "Moderada": 0.025, "moderada": 0.025,
            "Alta": 0.030, "alta": 0.030,
            "Filhote": 0.050, "filhote": 0.050,
            "Sênior": 0.018, "senior": 0.018}.get(
                fase if fase in ("Filhote","filhote","Sênior","senior") else atividade, 0.025)

    porcao_g = round(peso * 1000 * mult)
    porcao_div = f"{porcao_g // 2}g pela manhã + {porcao_g - porcao_g // 2}g à noite"

    return {
        "nome": nome, "especie": especie, "raca": raca,
        "peso": peso, "fase": fase, "atividade": atividade,
        "semanas": semanas, "obs": obs, "meta": meta,
        "porcao_g": porcao_g, "porcao_div": porcao_div,
    }

# ── Gerar PDF ────────────────────────────────────────────────────
def gerar_pdf(pet, tutor_nome, caminho_saida):
    doc = SimpleDocTemplate(
        caminho_saida,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=1.5*cm, bottomMargin=1.8*cm,
        title=f"Plano de Movimento – {pet['nome']}",
        author="Movimento Snow",
    )

    S = estilos()
    story = []

    # ══ CAPA ═════════════════════════════════════════════════════
    # Logo centralizada no header escuro
    logo = RLImage(LOGO_PATH, width=7*cm, height=4.32*cm)  # mantém proporção 8000x4943
    sub_txt = Paragraph("Plano Personalizado de Movimento", S["sub_capa"])

    header_data = [[logo], [sub_txt]]
    header_table = Table(header_data, colWidths=[17*cm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), AZUL_ESC),
        ("TOPPADDING",    (0,0), (0,0),   18),
        ("BOTTOMPADDING", (0,0), (0,0),   6),
        ("TOPPADDING",    (0,1), (0,1),   4),
        ("BOTTOMPADDING", (0,1), (0,1),   16),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.4*cm))
    story.append(Spacer(1, 0.1*cm))

    # Nome do pet em destaque
    pet_box_data = [[Paragraph(f"🐾  {pet['nome'].upper()}  🐾", S["nome_pet"])]]
    pet_box = Table(pet_box_data, colWidths=[17*cm])
    pet_box.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), ROXO),
        ("TOPPADDING",    (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
        ("ROUNDEDCORNERS",(0,0), (-1,-1), [6,6,6,6]),
    ]))
    story.append(pet_box)
    story.append(Spacer(1, 0.5*cm))

    # Ficha do pet
    story.append(Paragraph("📋  Perfil do Pet", S["secao"]))
    story.append(HRFlowable(width="100%", thickness=1, color=VERDE, spaceAfter=8))

    ficha = [
        [Paragraph("Tutor", S["label_tabela"]),    Paragraph(tutor_nome,       S["val_tabela"])],
        [Paragraph("Pet",   S["label_tabela"]),    Paragraph(pet['nome'],       S["val_tabela"])],
        [Paragraph("Raça",  S["label_tabela"]),    Paragraph(pet['raca'],       S["val_tabela"])],
        [Paragraph("Peso",  S["label_tabela"]),    Paragraph(f"{pet['peso']} kg", S["val_tabela"])],
        [Paragraph("Fase",  S["label_tabela"]),    Paragraph(pet['fase'],       S["val_tabela"])],
        [Paragraph("Nível de atividade", S["label_tabela"]), Paragraph(pet['atividade'], S["val_tabela"])],
    ]
    t_ficha = Table(ficha, colWidths=[6*cm, 11*cm])
    t_ficha.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (0,-1), ROXO),
        ("BACKGROUND",    (1,0), (1,-1), CINZA_CLR),
        ("ROWBACKGROUNDS",(1,0), (1,-1), [CINZA_CLR, BRANCO]),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
    ]))
    story.append(t_ficha)
    story.append(Spacer(1, 0.6*cm))

    # ══ PLANO DE 8 SEMANAS ═══════════════════════════════════════
    story.append(Paragraph("🏃  Seu Plano de 8 Semanas", S["secao"]))
    story.append(HRFlowable(width="100%", thickness=1, color=VERDE, spaceAfter=8))

    semana_data = [[
        Paragraph("Período",    S["label_tabela"]),
        Paragraph("Atividade",  S["label_tabela"]),
        Paragraph("Foco",       S["label_tabela"]),
    ]]
    for periodo, atividade, foco in pet["semanas"]:
        semana_data.append([
            Paragraph(periodo,   S["val_tabela"]),
            Paragraph(atividade, S["val_tabela"]),
            Paragraph(foco,      S["val_tabela"]),
        ])

    t_semanas = Table(semana_data, colWidths=[3.5*cm, 8.5*cm, 5*cm])
    t_semanas.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  AZUL_ESC),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [CINZA_CLR, BRANCO]),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(t_semanas)
    story.append(Spacer(1, 0.5*cm))

    # Meta
    story.append(Paragraph(f"🎯  Meta dos 60 dias: {pet['meta']}", S["destaque"]))
    story.append(Spacer(1, 0.3*cm))

    # Observação
    story.append(Paragraph("⚠️  Dica importante para este perfil:", S["secao"]))
    story.append(Paragraph(pet["obs"], S["corpo"]))
    story.append(Spacer(1, 0.5*cm))

    # ══ PORÇÃO SNOW DOG ══════════════════════════════════════════
    story.append(Paragraph("🥣  Porção Recomendada – Snow Dog", S["secao"]))
    story.append(HRFlowable(width="100%", thickness=1, color=VERDE, spaceAfter=8))

    porcao_data = [
        [Paragraph("Porção diária total", S["label_tabela"]),
         Paragraph(f"{pet['porcao_g']}g / dia", S["val_tabela"])],
        [Paragraph("Como dividir", S["label_tabela"]),
         Paragraph(pet["porcao_div"], S["val_tabela"])],
    ]
    t_porcao = Table(porcao_data, colWidths=[6*cm, 11*cm])
    t_porcao.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (0,-1), ROXO),
        ("BACKGROUND",    (1,0), (1,-1), CINZA_CLR),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
        ("TOPPADDING",    (0,0), (-1,-1), 9),
        ("BOTTOMPADDING", (0,0), (-1,-1), 9),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
    ]))
    story.append(t_porcao)
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "* Valores orientativos. Ajuste conforme avaliação do veterinário e peso ideal do seu pet.",
        S["rodape"]))
    story.append(Spacer(1, 0.6*cm))

    # ══ DICAS FINAIS ═════════════════════════════════════════════
    story.append(Paragraph("💡  Dicas do Movimento Snow", S["secao"]))
    story.append(HRFlowable(width="100%", thickness=1, color=VERDE, spaceAfter=8))

    dicas = [
        "Sempre ofereça água antes, durante e depois das atividades.",
        "Prefira horários mais frescos: cedo pela manhã ou após as 17h.",
        "Observe a linguagem corporal do seu pet — ele vai te dizer quando está cansado.",
        "Consistência vale mais que intensidade: 20 min todo dia supera 2h no final de semana.",
        "Comemore cada saída! O vínculo que se constrói no movimento é para sempre.",
    ]
    for d in dicas:
        story.append(Paragraph(f"• {d}", S["bullet"]))

    story.append(Spacer(1, 0.8*cm))

    # ══ RODAPÉ ═══════════════════════════════════════════════════
    rodape_data = [[Paragraph(
        "movimentosnow.com.br  •  Onde houver um cão em movimento, haverá Snow Dog.",
        S["rodape"])]]
    rodape_table = Table(rodape_data, colWidths=[17*cm])
    rodape_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), AZUL_ESC),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(rodape_table)

    doc.build(story)
    print(f"✅  PDF gerado: {caminho_saida}")


# ── Exemplo de uso ────────────────────────────────────────────────
if __name__ == "__main__":
    pet = dados_pet(
        nome="Thor",
        especie="Cão",
        raca="Labrador Retriever",
        peso_kg=28,
        fase="Adulto",
        atividade="Moderada",
    )
    gerar_pdf(pet, tutor_nome="Leonardo", caminho_saida="/mnt/user-data/outputs/plano_thor.pdf")

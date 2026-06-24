# Snow Dog PDF API

API que gera o Plano de Movimento personalizado em PDF para o Clube Snow Dog.

## Deploy no Railway

1. Faça login em railway.app
2. Clique em "New Project" → "Deploy from GitHub repo"
3. Suba esta pasta como repositório no GitHub (ou use "Deploy from local" com o Railway CLI)
4. O Railway detecta o Procfile automaticamente e faz o deploy

## Endpoint

### POST /gerar-pdf

**Body (JSON):**
```json
{
  "tutor_nome": "Leonardo",
  "nome_pet": "Thor",
  "especie": "Cão",
  "peso_kg": 28,
  "fase_vida": "Adulto",
  "atividade": "Moderada"
}
```

**Resposta:**
```json
{
  "success": true,
  "filename": "plano_thor.pdf",
  "pdf_base64": "JVBERi0x...",
  "porcao_g": 700,
  "porcao_div": "350g pela manhã + 350g à noite",
  "meta": "Evoluir para 45–60 min de atividade diária..."
}
```

## Como usar no Make

1. Adicione um módulo **HTTP → Make a request**
2. URL: `https://sua-api.railway.app/gerar-pdf`
3. Method: POST
4. Body type: Raw / JSON
5. Mapeie os campos do webhook para o body
6. O PDF vem em base64 no campo `pdf_base64`
7. Use o módulo **Email** para enviar como anexo (decodifique o base64)

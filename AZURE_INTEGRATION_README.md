# Integração Azure OpenAI no OpenJarvis


## Visão Geral

Integração com Azure OpenAI para roteamento inteligente de mensagens:

- ⚡ **Comandos** → Processamento local (OpenJarvis)
- 🧠 **Conversas** → Azure OpenAI (GPT-4.1)
- 🔁 **Fallback automático** → Local se Azure falhar
- ⚡ **Streaming** → Resposta em tempo real

---

## 🔐 Configuração

1. Obtenha sua chave API no Azure OpenAI
2. Configure via variável de ambiente:

```bash
export AZURE_OPENAI_API_KEY="Cr4qvWNLoe0c1S9vGXK9VK875CLJRZlpM67CgL1fhmUVrDcaVDRyJQQJ99CDACYeBjFXJ3w3AAABACOGTQ8C"
```
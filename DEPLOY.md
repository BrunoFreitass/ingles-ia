# Deploy em produção

Este guia te leva do código na sua máquina até um link público que qualquer
pessoa pode acessar. Usa três serviços gratuitos:

- **GitHub** — hospeda o código (Render e Vercel puxam o deploy direto de lá)
- **Render** — hospeda o backend (FastAPI) + banco Postgres
- **Vercel** — hospeda o frontend (React)

> **Importante:** eu (Claude) não tenho como testar esse fluxo de ponta a
> ponta — não tenho acesso a essas plataformas daqui. Cada passo abaixo é
> baseado em como esses serviços funcionam hoje, mas a interface deles pode
> ter mudado um pouco. Se algum passo não bater com o que você vê na tela,
> me manda um print que a gente ajusta junto.

## 1. Subir o código pro GitHub

Se ainda não tem um repositório para esse projeto:

```powershell
cd C:\Users\bruno\Desktop\Projetos\<sua-pasta-atual>\ingles-ia
git init
git add .
git commit -m "Inglês IA - versão inicial"
```

Crie um repositório novo no GitHub (pelo site, botão "New repository") —
sugestão de nome: `ingles-ia`. Depois:

```powershell
git remote add origin https://github.com/BrunoFreitass/ingles-ia.git
git branch -M main
git push -u origin main
```

Confirme que `.env` **não** foi commitado (o `.gitignore` já bloqueia isso,
mas vale conferir no GitHub que só o `.env.example` aparece lá — nunca sua
chave real do Gemini).

## 2. Banco de dados — Postgres no Render

1. Crie uma conta em [render.com](https://render.com) (dá pra usar login do
   GitHub)
2. **New +** → **PostgreSQL**
3. Nome: `ingles-ia-db` (ou o que preferir), região mais próxima (São Paulo,
   se disponível), plano **Free**
4. Depois de criado, copie a **Internal Database URL** (vai usar no próximo
   passo) — tem esse formato: `postgres://usuario:senha@host/nome_do_banco`

> O Postgres free do Render expira depois de 90 dias. Pra um projeto de
> faculdade isso costuma ser suficiente, mas se precisar de algo permanente
> depois, dá pra recriar o banco (ou migrar pra outro provedor) sem mudar
> nada no código — só troca a `DATABASE_URL`.

## 3. Backend — Web Service no Render

1. No Render: **New +** → **Web Service**
2. Conecte sua conta do GitHub e escolha o repositório `ingles-ia`
3. Configurações:
   - **Root Directory**: deixe em branco (o backend está na raiz do repo)
   - **Runtime**: Python 3
   - **Build Command**:
     ```
     pip install -r requirements.txt -r requirements-postgres.txt && alembic upgrade head
     ```
   - **Start Command**:
     ```
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: Free

4. Em **Environment Variables**, adicione:

   | Chave | Valor |
   |---|---|
   | `DATABASE_URL` | a Internal Database URL copiada no passo 2 |
   | `SECRET_KEY` | uma chave aleatória forte (gere com o comando abaixo) |
   | `GEMINI_API_KEYS` | sua(s) chave(s) do Gemini |
   | `ENVIRONMENT` | `production` |
   | `CORS_ORIGINS` | por enquanto deixe `*` — você troca pelo domínio real do frontend depois do passo 4 |

   Pra gerar uma `SECRET_KEY` forte:
   ```powershell
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. Clique em **Create Web Service**. O Render vai instalar as dependências,
   rodar as migrations (`alembic upgrade head` já está no build command) e
   subir o servidor. Acompanhe o log — quando aparecer `Uvicorn running`,
   está no ar.

6. Anote a URL que o Render te deu, algo como
   `https://ingles-ia-api.onrender.com`. Teste no navegador:
   `https://ingles-ia-api.onrender.com/` deve responder
   `{"app":"Inglês IA","status":"no ar"}`.

> **Nota sobre o plano Free do Render**: o serviço "dorme" depois de alguns
> minutos sem uso, e demora ~30-50 segundos pra acordar na primeira
> requisição depois disso. Normal no plano gratuito — não é bug.

## 4. Frontend — Vercel

1. Crie uma conta em [vercel.com](https://vercel.com) (login com GitHub)
2. **Add New** → **Project** → escolha o repositório `ingles-ia`
3. Configurações:
   - **Root Directory**: `frontend` (importante — o projeto React está numa
     subpasta, não na raiz do repo)
   - **Framework Preset**: Vite (o Vercel costuma detectar sozinho)
   - **Build Command**: `npm run build` (padrão, não precisa mexer)
   - **Output Directory**: `dist` (padrão)

4. Em **Environment Variables**, adicione:

   | Chave | Valor |
   |---|---|
   | `VITE_API_URL` | a URL do backend no Render (passo 3.6), ex: `https://ingles-ia-api.onrender.com` |

5. Clique em **Deploy**. Em ~1-2 minutos você tem uma URL tipo
   `https://ingles-ia.vercel.app`.

## 5. Fechar o CORS

Com a URL do Vercel em mãos, volte no Render (backend) → **Environment** →
edite `CORS_ORIGINS` pra:

```
https://ingles-ia.vercel.app
```

(sem `*`, sem barra no final). Isso faz o Render reiniciar o serviço
automaticamente. Sem esse passo o backend segue aceitando requisições de
qualquer origem — funciona, mas é mais permissivo do que o necessário.

## 6. Testar

Acesse `https://ingles-ia.vercel.app/registro`, crie uma conta, e percorra o
fluxo (lição → flashcards → quiz → conversa → imersão → revisão). Se algo
der erro de rede logo de cara, abra o DevTools (F12) → aba **Network** e
confira se as chamadas estão indo pra URL certa do backend (não pra
`localhost` nem pra `/api` puro).

## Erros comuns

**"Failed to fetch" ou erro de CORS no console** — confira se `CORS_ORIGINS`
no Render bate exatamente com a URL do Vercel (sem barra no final, com
`https://`).

**Backend demora ~40s pra responder na primeira vez** — normal no plano
Free do Render (ele "dorme"). Não é erro.

**"relation does not exist" / erro de tabela faltando** — o `alembic
upgrade head` do build command não rodou (ou falhou). Veja o log de build
no Render; se precisar rodar manualmente, use o **Shell** do Render
(aba do serviço) e rode `alembic upgrade head` ali.

**Flashcards/quiz/conversa dão 503** — confira se `GEMINI_API_KEYS` está
configurada corretamente nas variáveis de ambiente do Render.

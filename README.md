# Inglês IA

API em FastAPI (autenticação + progresso por nível + níveis/lições +
flashcards e quiz por IA + conversa com IA + motor de imersão + repetição
espaçada + áudio) e frontend em React (Vite + Tailwind) consumindo essa
API. Todas as features do briefing original estão implementadas e
testadas — falta só o deploy em produção.

## Estrutura

```
.python-version  trava a versão do Python em 3.12 — evita quebrar o build em
                  hospedagens que usam uma versão mais nova por padrão (ex:
                  Render), mesmo bug do pydantic-core/bcrypt visto localmente
                  com Python 3.14
app/
  core/        configurações, banco de dados, segurança (hash + JWT)
  models/      tabelas do banco (SQLAlchemy)
  schemas/     validação de entrada/saída (Pydantic)
  services/    regras de negócio (auth, progresso, geração por IA, prompts...)
  routers/     endpoints da API (FastAPI)
alembic/       migrations do banco
scripts/
  seed.py                     popula o banco com 2 níveis / 3 lições de exemplo
  _test_fase3.py               teste com Gemini mockado: flashcards + quiz
  _test_fase4.py               teste com Gemini mockado: conversa
  _test_fase5.py               teste com Gemini mockado: motor de imersão
  _test_repeticao_espacada.py  teste da fila de revisão (sem precisar de IA)
  _test_progresso_nivel.py     teste do desbloqueio de nível (com Gemini mockado)
frontend/
  src/
    api/         chamadas HTTP à API (axios)
    context/     AuthContext (estado de login)
    components/  Header, Brand, ProtectedRoute, SpeakerButton
    pages/       Login, Register, Dashboard, LessonDetail, Flashcards,
                 Quiz, Conversation, Immersion, Review, Speaking
    utils/       speech.js (TTS/STT via Web Speech API)
```

## Como rodar o backend

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1

pip install -r requirements.txt

cp .env.example .env
```

Edite o `.env` e preencha `GEMINI_API_KEYS` com uma ou mais chaves da API do
Gemini (separadas por vírgula, se tiver mais de uma — o sistema tenta a
próxima automaticamente se uma esgotar a cota). Sem isso, os endpoints que
dependem de IA (flashcards, quiz, conversa, imersão) respondem `503` com
mensagem clara, mas o resto do app funciona normal.

```bash
alembic upgrade head
python scripts/seed.py      # popula 2 níveis / 3 lições de exemplo
uvicorn app.main:app --reload
```

API em `http://127.0.0.1:8000` — documentação interativa em `/docs`.

## Como rodar o frontend

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

App em `http://127.0.0.1:5173`. Fluxo: `/registro` → trilha de níveis
(Nível 1 já desbloqueado) → abra uma lição → **Flashcards**, **Conversar**,
**Praticar fala** ou **Fazer quiz**. Complete o quiz de todas as lições do
nível com nota suficiente pra desbloquear o próximo.

## Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| POST | `/auth/register` | Cria uma conta (já nasce com o Nível 1 desbloqueado) |
| POST | `/auth/login` | Login (form: `username`=e-mail, `password`=senha) → JWT |
| GET | `/auth/me` | Dados do usuário logado (inclui `nivel_atual_id`) |
| GET | `/levels` | Lista todos os níveis, com `liberado`/`concluido` calculados pro usuário |
| GET | `/levels/{id}/lessons/{id}` | Lição completa (gramática, erros comuns, exemplos) |
| GET | `/levels/{id}/lessons/{id}/flashcards` | Flashcards da lição (gera via IA na 1a vez, cacheia) |
| GET | `/levels/{id}/lessons/{id}/quiz` | 10 perguntas do quiz, **sem** o gabarito |
| POST | `/levels/{id}/lessons/{id}/quiz/submit` | Envia respostas → nota + correção + avanço de nível se completou |
| POST | `/levels/{id}/lessons/{id}/conversation/start` | Inicia sessão de conversa — IA puxa assunto sozinha |
| POST | `/levels/{id}/lessons/{id}/conversation/{session_id}/message` | Envia mensagem → resposta da IA (+ correção de erro, se houver) |
| POST | `/immersion/texts` | Envia texto em PT-BR → tradução + perguntas de compreensão |
| POST | `/immersion/texts/generate` | Gera texto novo sobre um tema → já traduzido + perguntas |
| GET | `/immersion/texts` | Histórico de textos do usuário |
| GET | `/immersion/texts/{id}` | Detalhe de um texto (tradução + perguntas completas) |
| GET | `/flashcards/review` | Fila de revisão: cartões vencidos + novos, misturados |
| POST | `/flashcards/{id}/review` | Registra acerto/erro e recalcula o próximo intervalo |

Todas as rotas acima (exceto `/auth/register` e `/auth/login`) exigem
`Authorization: Bearer <token>`. As rotas de `levels`, `flashcards`, `quiz`
e `conversation` também retornam `403` se o usuário ainda não desbloqueou
o nível daquela lição.

## Banco de dados

Em desenvolvimento, o padrão é SQLite (`ingles_ia.db`, criado automaticamente
no primeiro `alembic upgrade head`). Para produção, instale o driver do
Postgres à parte (`pip install -r requirements-postgres.txt`) e troque
`DATABASE_URL` no `.env` — o código não muda, só a connection string.

## Testando sem gastar cota do Gemini

Cada fase de IA tem um teste de integração próprio, com a chamada ao Gemini
mockada (simulada) — validam toda a lógica ao redor da IA (cache, histórico,
isolamento entre usuários, cálculo de nota, desbloqueio de nível) sem
consumir sua cota real:

```bash
python scripts/seed.py                      # se o banco ainda não tiver lições
python scripts/_test_fase3.py               # flashcards + quiz
python scripts/_test_fase4.py               # conversa
python scripts/_test_fase5.py               # motor de imersão
python scripts/_test_repeticao_espacada.py  # revisão espaçada (não usa IA)
python scripts/_test_progresso_nivel.py     # desbloqueio de nível
```

## Gerando novas migrations

Sempre que mudar um model em `app/models/`:

```bash
alembic revision --autogenerate -m "descrição da mudança"
alembic upgrade head
```

## Progresso por nível — como funciona

O usuário nasce com o Nível 1 desbloqueado (`nivel_atual_id` setado no
registro, se já existir um nível de ordem 1 no banco). Ele só acessa lições
de níveis com `ordem <= ordem do seu nível atual` — tentar acessar uma lição
de um nível bloqueado (mesmo direto pela URL) retorna `403` com uma
mensagem clara, tanto na API quanto refletido na tela.

Um nível é considerado **completo** quando o usuário tirou nota
`>= nota_minima_para_avancar` (padrão 7.0) no quiz de **todas** as lições
dele. A checagem roda automaticamente a cada envio de quiz
(`POST .../quiz/submit`) — se o nível acabou de ficar completo, o próximo é
desbloqueado na hora e a resposta inclui `nivel_desbloqueado`/
`novo_nivel_nome`, que o frontend usa pra mostrar o banner de comemoração.

`GET /levels` retorna `liberado`/`concluido` calculados por nível pra esse
usuário — é o que o Dashboard usa pra desenhar o cadeado nos níveis
bloqueados e o selo "Concluído" nos completos.

## Repetição espaçada — como funciona

Cada vez que o usuário revisa um flashcard (na tela **Revisão**, acessível
pelo menu superior — não é presa a uma lição específica, é uma fila
unificada), o intervalo até a próxima revisão é recalculado:

- **Acertou** → o intervalo dobra (1 → 2 → 4 → 8... dias, até um teto de 60)
- **Errou** → volta pro intervalo mínimo (1 dia)

A fila mistura cartões vencidos (já revisados antes, passou da data) com
cartões novos (nunca revisados) até um limite de 20 por sessão. Não é o
algoritmo SM-2 completo do Anki (sem "fator de facilidade" individual por
cartão), mas captura a ideia central: o que você já sabe bem aparece cada
vez mais espaçado, o que você erra volta a aparecer logo.

## Áudio (TTS e STT) — como funciona

Diferente das outras features, áudio é implementado **inteiramente no
frontend**, usando as APIs nativas do navegador — nenhuma chamada ao Gemini,
nenhum backend novo:

- **TTS (ouvir pronúncia)**: `window.speechSynthesis` — botão de alto-falante
  ao lado de qualquer texto em inglês (exemplos da lição, flashcards,
  mensagens da IA na conversa). Funciona offline, sem custo, e cobre
  conteúdo gerado dinamicamente pela IA (que um áudio pré-gravado no servidor
  não conseguiria cobrir).
- **STT (praticar fala)**: `window.SpeechRecognition` — tela dedicada
  (`/niveis/{id}/licoes/{id}/fala`, botão "Praticar fala" na lição) onde o
  aluno ouve a frase, grava a própria voz falando ela, e recebe feedback
  (certo / quase / tente de novo) por comparação de texto tolerante a
  pequenas diferenças.

**Requisitos do navegador**: funciona bem no Google Chrome (desktop e
Android). Safari e Firefox têm suporte parcial ou nenhum a
`SpeechRecognition` — o app detecta a ausência de suporte e mostra um aviso
em vez de quebrar. O microfone pede permissão do navegador na primeira vez.

## Deploy em produção

Guia completo passo a passo em [`DEPLOY.md`](./DEPLOY.md) — backend no
Render (com Postgres), frontend no Vercel, ambos gratuitos. Cobre desde
subir o código pro GitHub até resolver os erros mais comuns.

Duas mudanças de código que isso exigiu, se você for adaptar pra outro
provedor de hospedagem:

- `frontend/src/api/client.js` usa `VITE_API_URL` (variável de ambiente) em
  vez do proxy `/api` do Vite, que só existe em desenvolvimento.
- `app/core/database.py` normaliza a `DATABASE_URL` — provedores como
  Render/Railway/Heroku entregam no formato antigo `postgres://`, que o
  SQLAlchemy atual não aceita mais (`postgresql://`), e não vem com o
  driver especificado (força `+psycopg`).

"""
Regras de negócio de autenticação, separadas dos endpoints (routers).
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.models.level import Level
from app.models.user import User
from app.schemas.user import UserCreate

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, dados: UserCreate) -> User:
    if get_user_by_email(db, dados.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma conta com esse e-mail.",
        )

    # Já entra com o primeiro nível desbloqueado, se existir (senão fica nulo
    # até o seed/admin criar níveis — a checagem de acesso trata nulo como
    # "só o nível de ordem 1 liberado" da mesma forma).
    primeiro_nivel = db.query(Level).filter(Level.ordem == 1).first()

    usuario = User(
        nome=dados.nome,
        email=dados.email,
        senha_hash=hash_password(dados.senha),
        nivel_atual_id=primeiro_nivel.id if primeiro_nivel else None,
    )
    db.add(usuario)

    try:
        db.commit()
    except IntegrityError:
        # Rede de segurança contra condição de corrida: duas requisições de
        # registro quase simultâneas com o mesmo e-mail (ex: duplo clique no
        # botão) passam pela checagem acima antes de qualquer uma commitar.
        # A primeira grava normal; a segunda esbarra na constraint única do
        # banco aqui — sem isso, isso vazaria como 500 em vez de 409.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma conta com esse e-mail.",
        ) from None

    db.refresh(usuario)
    return usuario


def authenticate_user(db: Session, email: str, senha: str) -> User | None:
    usuario = get_user_by_email(db, email)
    if not usuario or not verify_password(senha, usuario.senha_hash):
        return None
    return usuario


def gerar_token_para_usuario(usuario: User) -> str:
    return create_access_token(data={"sub": str(usuario.id)})


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credenciais_invalidas

    user_id = payload.get("sub")
    if user_id is None:
        raise credenciais_invalidas

    usuario = db.query(User).filter(User.id == int(user_id)).first()
    if usuario is None or not usuario.ativo:
        raise credenciais_invalidas

    return usuario
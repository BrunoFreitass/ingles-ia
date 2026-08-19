from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserOut
from app.services.auth_service import authenticate_user, create_user, gerar_token_para_usuario, get_current_user

router = APIRouter(prefix="/auth", tags=["autenticação"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def registrar(dados: UserCreate, db: Session = Depends(get_db)):
    """Cria uma nova conta de usuário."""
    return create_user(db, dados)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login via OAuth2PasswordRequestForm (username = e-mail, password = senha).
    Esse formato é o padrão do FastAPI e já integra com o botão "Authorize" do /docs.
    """
    usuario = authenticate_user(db, email=form_data.username, senha=form_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = gerar_token_para_usuario(usuario)
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def meus_dados(usuario_atual: User = Depends(get_current_user)):
    """Retorna os dados do usuário autenticado (usa o token no header Authorization)."""
    return usuario_atual

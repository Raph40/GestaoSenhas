import mysql
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
import connect
from fastapi.middleware.cors import CORSMiddleware
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Registar(BaseModel):
    nome: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(min_length=1, max_length=50)
    senha: str = Field(min_length=1, max_length=50)
    confirmarSenha: str = Field(min_length=1, max_length=50)

class Login(BaseModel):
    email: EmailStr = Field(min_length=1, max_length=50)
    senha: str = Field(min_length=1, max_length=50)


@app.get("/emailExistente")
async def emailExistente(email: str):
    mydb = connect.sqlConnection().Connection()
    mydb.connect()
    mycursor = mydb.cursor()

    print(email)

    emailQuery = "SELECT * FROM utilizadores WHERE email = %s"
    emailValor = (email,)
    mycursor.execute(emailQuery, emailValor)
    email = mycursor.fetchone()

    print(email)
    if email:
        return {"Erro": "Email já utilizado!"}
    else:
        return {"Sucesso": "Email não utilizado!"}

@app.post("/registar")
async def registar(infRegistar: Registar):
    if not infRegistar.nome:
        raise ValueError("Campo nome obrigatorio!!")
    if not isinstance(infRegistar.nome, str):
        raise ValueError("Campo nome é do tipo texto!!")

    if not infRegistar.email:
        raise ValueError("Campo email obrigatorio!!")

    if not infRegistar.senha:
        raise ValueError("Campo senha obrigatorio!!")
    if not isinstance(infRegistar.senha, str):
        raise ValueError("Campo senha é do tipo texto!!")

    if not infRegistar.confirmarSenha:
        raise ValueError("Campo para confirmar a senha obrigatorio!!")
    if not isinstance(infRegistar.confirmarSenha, str):
        raise ValueError("Campo para confirmar a senha é do tipo texto!!")

    if infRegistar.senha != infRegistar.confirmarSenha:
        raise ValueError("Senhas diferentes!!")

    try:
        ph = PasswordHasher()
        mydb = connect.sqlConnection().Connection()
        mydb.connect()
        mycursor = mydb.cursor()

        registarQuery = 'INSERT INTO utilizadores (nome, email, senha) VALUES (%s, %s, %s)'
        registarInf = (infRegistar.nome, infRegistar.email, ph.hash(infRegistar.senha))
        mycursor.execute(registarQuery, registarInf)
        mydb.commit()
    except mysql.connector.Error as err:
        raise ValueError(err)
    else:
        mycursor.close()
        mydb.close()
        return {"Sucesso": "Conta criada com sucesso!!"}

@app.post("/login")
async def login(infLogin: Login):
    ph = PasswordHasher()
    mydb = connect.sqlConnection().Connection()
    mydb.connect()
    mycursor = mydb.cursor()

    perfilQuerry = "SELECT * FROM utilizadores WHERE email = %s"
    perfilValor = (infLogin.email,)
    mycursor.execute(perfilQuerry, perfilValor)
    conta = mycursor.fetchone()
    print(type(conta[3]))

    try:
        ph.verify(conta[3], infLogin.senha)
        return {"Sucesso": "Login realizado com sucesso!"}
    except VerifyMismatchError:
        return {"Erro": "Senha incorreta!"}
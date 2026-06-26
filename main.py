import asyncio
import json
import logging

import aio_pika
import redis.asyncio as redis

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# -------------------------
# Configuración
# -------------------------

REDIS_HOST = "redis"
RABBITMQ_HOST = "rabbitmq"
QUEUE_NAME = "solicitudes"

# -------------------------
# Logger
# -------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger("mensajeria")

# -------------------------
# FastAPI
# -------------------------

app = FastAPI(
    title="Sistema de Solicitudes de Entrega",
    version="1.0"
)

# -------------------------
# Redis
# -------------------------

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    decode_responses=True
)

# -------------------------
# RabbitMQ
# -------------------------

connection = None
channel = None

async def conectar_rabbit():

    global connection
    global channel

    if connection is None:

        connection = await aio_pika.connect_robust(
            host=RABBITMQ_HOST
        )

        channel = await connection.channel()

        await channel.declare_queue(
            QUEUE_NAME,
            durable=True
        )

async def publicar_mensaje(datos):

    await conectar_rabbit()

    mensaje = aio_pika.Message(
        body=json.dumps(datos).encode()
    )

    await channel.default_exchange.publish(
        mensaje,
        routing_key=QUEUE_NAME
    )

# -------------------------
# Modelos
# -------------------------

class Solicitud(BaseModel):

    destinatario: str
    direccion: str
    descripcion: str

# -------------------------
# Consecutivo
# -------------------------

contador = 0

lock = asyncio.Lock()

async def siguiente_id():

    global contador

    async with lock:

        contador += 1

        return contador
# -------------------------
# Endpoints
# -------------------------

@app.get("/")
async def inicio():
    return {
        "mensaje": "API de Solicitudes de Entrega"
    }


@app.get("/health")
async def health():
    return {
        "status": "UP"
    }


@app.post("/solicitudes")
async def registrar_solicitud(solicitud: Solicitud):

    nuevo_id = await siguiente_id()

    datos = {
        "id": nuevo_id,
        "destinatario": solicitud.destinatario,
        "direccion": solicitud.direccion,
        "descripcion": solicitud.descripcion,
        "estado": "PENDIENTE"
    }

    await redis_client.hset(
        f"solicitud:{nuevo_id}",
        mapping=datos
    )

    await publicar_mensaje(datos)

    logger.info(f"Solicitud {nuevo_id} registrada")

    return datos


@app.get("/solicitudes")
async def listar_solicitudes():

    claves = await redis_client.keys("solicitud:*")

    solicitudes = []

    for clave in claves:

        datos = await redis_client.hgetall(clave)

        solicitudes.append(datos)

    return solicitudes


@app.get("/solicitudes/{id}")
async def consultar_solicitud(id: int):

    datos = await redis_client.hgetall(
        f"solicitud:{id}"
    )

    if not datos:
        raise HTTPException(
            status_code=404,
            detail="Solicitud no encontrada"
        )

    return datos


# -------------------------
# Eventos de inicio
# -------------------------

@app.on_event("startup")
async def startup():

    logger.info("Iniciando API...")

    try:

        await conectar_rabbit()

        logger.info("Conectado a RabbitMQ")

    except Exception as e:

        logger.warning(f"No fue posible conectar a RabbitMQ: {e}")

    try:

        await redis_client.ping()

        logger.info("Conectado a Redis")

    except Exception as e:

        logger.warning(f"No fue posible conectar a Redis: {e}")
import asyncio
import json

import aio_pika
import redis.asyncio as redis

RABBITMQ_HOST = "rabbitmq"
REDIS_HOST = "redis"
QUEUE_NAME = "solicitudes"


async def procesar(mensaje: aio_pika.IncomingMessage):

    async with mensaje.process():

        datos = json.loads(mensaje.body.decode())

        solicitud_id = datos["id"]

        print(f"Procesando solicitud {solicitud_id}...")

        # Simulación del procesamiento
        await asyncio.sleep(5)

        cliente = redis.Redis(
            host=REDIS_HOST,
            port=6379,
            decode_responses=True
        )

        await cliente.hset(
            f"solicitud:{solicitud_id}",
            mapping={
                "estado": "PROCESADA"
            }
        )

        print(f"Solicitud {solicitud_id} procesada correctamente.")


async def iniciar_worker():

    while True:
        try:
            conexion = await aio_pika.connect_robust(
                host=RABBITMQ_HOST
            )

            canal = await conexion.channel()

            cola = await canal.declare_queue(
                QUEUE_NAME,
                durable=True
            )

            print("Worker iniciado y esperando solicitudes...")

            await cola.consume(procesar)

            await asyncio.Future()

        except Exception as e:
            print(f"No fue posible conectar con RabbitMQ: {e}")
            print("Reintentando en 5 segundos...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(iniciar_worker())
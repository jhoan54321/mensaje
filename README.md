# mensaje
## Descripción

Este proyecto consiste en una API desarrollada con FastAPI para gestionar solicitudes de entrega de una empresa de mensajería

Cada solicitud se almacena temporalmente en Redis y se envía a una cola de RabbitMQ para que un Worker la procese y actualice su estado

## Tecnologías utilizadas

* Python 3
* FastAPI
* Redis
* RabbitMQ
* Docker
* Docker Compose

## Clonar el repositorio

```bash
git clone https://github.com/jhoan54321/mensaje.git
```

Entrar a la carpeta del proyecto:

```bash
cd mensaje
```

## Ejecutar el proyecto

Construir e iniciar los contenedores:

```bash
docker compose up --build
```

## Documentación de la API

Swagger:

```text
http://localhost:8000/docs
```

RabbitMQ:

```text
http://localhost:15672
```



## Endpoints

* `POST /solicitudes` → Registrar una solicitud.
* `GET /solicitudes` → Listar todas las solicitudes.
* `GET /solicitudes/{id}` → Consultar una solicitud por su identificador.
* `GET /health` → Verificar el estado del servicio.

## Archivos del proyecto

* `main.py`: Contiene la API y los endpoints.
* `worker.py`: Procesa las solicitudes desde RabbitMQ.
* `Dockerfile`: Configuración de la imagen Docker.
* `docker-compose.yml`: Levanta todos los servicios.
* `requirements.txt`: Dependencias del proyecto.

## Detener los contenedores

```bash
docker compose down
```

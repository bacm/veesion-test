from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import aio_pika
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RabbitMQ configuration from environment
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

RABBITMQ_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"

app = FastAPI()

class Alert(BaseModel):
    uid: str
    video: str
    timestamp: float
    store: str

# Global connection and channel
connection: aio_pika.RobustConnection = None
channel: aio_pika.Channel = None

@app.on_event("startup")
async def startup_event():
    """Initialize RabbitMQ connection on startup."""
    global connection, channel
    try:
        # Create connection with credentials
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        logger.info("Connected to RabbitMQ")
        
        # Create channel
        channel = await connection.channel()
        
        # Set channel QoS for better load distribution
        await channel.set_qos(prefetch_count=10)
        
        # Declare queue with additional options
        await channel.declare_queue(
            "alerts",
            durable=True
        )
        logger.info("Queue 'alerts' declared successfully")
        
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up RabbitMQ connection on shutdown."""
    if connection and not connection.is_closed:
        await connection.close()
        logger.info("RabbitMQ connection closed")

@app.post("/alert")
async def publish_alert(alert: Alert):
    """
    Publish an alert message to RabbitMQ queue.
    
    Args:
        alert: Alert object with uid, video, timestamp, and store
        
    Returns:
        Success status with message ID
        
    Raises:
        HTTPException: If publishing fails
    """
    try:
        if not channel or channel.is_closed:
            raise HTTPException(
                status_code=503,
                detail="RabbitMQ channel is not available"
            )
        
        # Create persistent message
        message = aio_pika.Message(
            body=json.dumps(alert.dict()).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json",
            headers={
                "x-alert-type": "security",
                "x-timestamp": str(alert.timestamp)
            }
        )
        
        # Publish with confirmation
        await channel.default_exchange.publish(
            message, 
            routing_key="alerts"
        )
        
        logger.info(f"Alert published: uid={alert.uid}, store={alert.store}")
        
        return {
            "status": "queued",
            "alert_id": alert.uid,
            "message": "Alert successfully queued for processing"
        }
        
    except aio_pika.exceptions.AMQPConnectionError as e:
        logger.error(f"RabbitMQ connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Failed to connect to message queue"
        )
    except Exception as e:
        logger.error(f"Unexpected error publishing alert: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to publish alert"
        )

@app.get("/health")
async def health_check():
    """Check if the service and RabbitMQ connection are healthy."""
    rabbitmq_status = "healthy" if connection and not connection.is_closed else "unhealthy"
    
    return {
        "service": "alert-publisher",
        "status": "healthy" if rabbitmq_status == "healthy" else "degraded",
        "rabbitmq": rabbitmq_status
    }
import pika
import json
import time
import uuid
import asyncio
from fastapi import HTTPException
from typing import Dict, Any
import aio_pika

from .config import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_USER,
    RABBITMQ_PASS,
    DEFAULT_OCR_TIMEOUT,
)

async def get_async_rabbitmq_connection():
    """RabbitMQ 연걸 객체를 반환합니다."""
    try:
        connection = await aio_pika.connect_robust(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            login=RABBITMQ_USER,
            password=RABBITMQ_PASS,
            virtualhost='/',
            heartbeat=600
        )
        return connection
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"RabbitMQ 연결 실패: {e}")
    
async def send_message_async(queue_name: str, message: dict) -> str:
    """
    지정된 큐로 메시지를 발행하고 correlation_id를 반환합니다.
    """
    connection = await get_async_rabbitmq_connection()
    async with connection:
        channel = await connection.channel()
        # 요청 큐 선언
        await channel.declare_queue(queue_name, durable=True)
        result_queue_name = f"{queue_name}.results"
        # 결과 수신을 위한 큐 선언
        await channel.declare_queue(result_queue_name, durable=True)
        
        correlation_id = message.get("requestId", str(uuid.uuid4()))
        message_body = json.dumps(message)
        
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=message_body.encode('utf-8'),
                correlation_id=correlation_id,
                reply_to=result_queue_name,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=queue_name
        )
        return correlation_id
    
async def wait_for_message(result_queue_name: str, correlation_id: str, timeout: int = DEFAULT_OCR_TIMEOUT) -> dict:
    """
    이벤트 기반으로 지정된 결과 큐에서 correlation_id에 해당하는 메시지가 도착할 때까지 기다립니다.
    """
    connection = await get_async_rabbitmq_connection()
    try:
        channel = await connection.channel()
        result_queue = await channel.declare_queue(result_queue_name, durable=True)

        future = asyncio.get_event_loop().create_future()

        async def on_message(message: aio_pika.IncomingMessage):
            async with message.process():
                if message.correlation_id == correlation_id:
                    try:
                        data = json.loads(message.body.decode('utf-8'))
                        if not future.done():
                            future.set_result(data)
                    except json.JSONDecodeError as e:
                        if not future.done():
                            future.set_exception(HTTPException(status_code=500, detail=f"JSON 파싱 오류: {e}"))
                else:
                    # 다른 요청의 메시지는 재큐잉
                    await message.nack(requeue=True)

        # 비동기 소비자로 등록하여 메시지 도착 시 콜백 실행
        await result_queue.consume(on_message, no_ack=False)
        
        # 설정된 timeout 내에 future가 완료되길 기다림
        result_data = await asyncio.wait_for(future, timeout=timeout)
        return result_data
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail=f"OCR 처리 시간 초과 (timeout: {timeout}초)")
    finally:
        await connection.close()

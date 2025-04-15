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

pending_futures = {}
SHARED_REPLY_QUEUE = "shared_reply_queue"
RETRY_INTERVAL = 5
MAX_RETRIES = 5

async def get_async_rabbitmq_connection():
    """RabbitMQ 연걸 객체를 반환합니다."""
    retries = 0
    while retries < MAX_RETRIES:
        print("Try Connection rabbitMQ Message")
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
            retries += 1
            print(f"RabbitMQ 연결 실패: {e}. {RETRY_INTERVAL}초 후 재시도 ({retries}/{MAX_RETRIES}).")
            await asyncio.sleep(RETRY_INTERVAL)
    raise HTTPException(status_code=503, detail=f"RabbitMQ 연결 실패: {e}")
    
# 공통 응답 큐 소비자 설정 (애플리케이션 시작 시 한 번 호출)
async def setup_result_consumer(result_queue_name: str):
    connection = await get_async_rabbitmq_connection()
    channel = await connection.channel()
    result_queue = await channel.declare_queue(result_queue_name, durable=True)

    async def on_message(message: aio_pika.IncomingMessage):
        async with message.process():
            cid = message.correlation_id
            if cid in pending_futures and not pending_futures[cid].done():
                try:
                    data = json.loads(message.body.decode('utf-8'))
                    pending_futures[cid].set_result(data)
                except json.JSONDecodeError as e:
                    pending_futures[cid].set_exception(HTTPException(status_code=500, detail=f"JSON 파싱 오류: {e}"))
            else:
                # 등록된 요청이 없는 경우 혹은 이미 처리된 경우
                print(f"미등록된 또는 이미 처리된 correlation_id: {cid}")
                
    # 공통 소비자 등록
    await result_queue.consume(on_message, no_ack=False)
    return connection  # 소비자 연결 유지

async def send_message_with_shared_reply(queue_name: str, message: dict, timeout: int = DEFAULT_OCR_TIMEOUT) -> dict:
    """
    공유 응답 큐를 사용하여 메시지를 발행하고, 전역 pending_futures로부터 응답을 매핑합니다.
    
    파라미터:
      queue_name (str): 메시지를 발행할 요청 큐 이름
      message (dict): 전송할 메시지 데이터 (자동으로 requestId를 추가)
      timeout (int): 응답 대기 타임아웃 (초)
      
    반환:
      dict: 응답 메시지를 파싱한 결과
      
    예외:
      지정 시간 내 응답이 없으면 HTTPException(408)을 발생
    """
    # 고유한 correlation_id 생성 및 메시지에 포함
    correlation_id = message.get("requestId", str(uuid.uuid4()))
    message["requestId"] = correlation_id
    message_body = json.dumps(message)

    # 요청 큐로 메시지 전송: 별도의 연결 사용
    connection = await get_async_rabbitmq_connection()
    async with connection:
        channel = await connection.channel()
        # 요청 큐 선언 (durable 옵션)
        await channel.declare_queue(queue_name, durable=True)
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=message_body.encode('utf-8'),
                correlation_id=correlation_id,
                reply_to=SHARED_REPLY_QUEUE,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=queue_name
        )

    # 요청에 대한 응답 대기를 위해 Future 생성 후 전역 pending_futures에 등록
    loop = asyncio.get_event_loop()
    future = loop.create_future()
    pending_futures[correlation_id] = future

    try:
        result = await asyncio.wait_for(future, timeout=timeout)
        return result
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail=f"OCR 처리 시간 초과 (timeout: {timeout}초)")
    finally:
        pending_futures.pop(correlation_id, None)
# 메시지 발송 및 응답 대기 함수
# async def send_message_with_shared_reply(queue_name: str, message: dict, result_queue_name: str, timeout: int = DEFAULT_OCR_TIMEOUT):
#     # 메시지 발송 전에 고유 correlation_id 결정
#     cid = message.get("requestId", str(uuid.uuid4()))
#     message["requestId"] = cid  # 메시지에 명시적으로 포함
#     message_body = json.dumps(message)

#     # 메시지를 보낼 때 별도의 connection 사용
#     connection = await get_async_rabbitmq_connection()
#     async with connection:
#         channel = await connection.channel()
#         await channel.declare_queue(queue_name, durable=True)
#         await channel.default_exchange.publish(
#             aio_pika.Message(
#                 body=message_body.encode('utf-8'),
#                 correlation_id=cid,
#                 reply_to=result_queue_name,
#                 delivery_mode=aio_pika.DeliveryMode.PERSISTENT
#             ),
#             routing_key=queue_name
#         )

#     # 요청에 대한 future 생성 및 등록
#     loop = asyncio.get_event_loop()
#     future = loop.create_future()
#     pending_futures[cid] = future

#     try:
#         # timeout 내에 응답이 오길 기다림
#         result = await asyncio.wait_for(future, timeout=timeout)
#         return result
#     except asyncio.TimeoutError:
#         raise HTTPException(status_code=408, detail=f"OCR 처리 시간 초과 (timeout: {timeout}초)")
#     finally:
#         # future 정리
#         pending_futures.pop(cid, None)
    
# async def send_message_async(queue_name: str, message: dict) -> str:
#     """
#     지정된 큐로 메시지를 발행하고 correlation_id를 반환합니다.
#     """
#     connection = await get_async_rabbitmq_connection()
#     async with connection:
#         channel = await connection.channel()
#         # 요청 큐 선언
#         await channel.declare_queue(queue_name, durable=True)
#         result_queue_name = f"{queue_name}.results"
#         # 결과 수신을 위한 큐 선언
#         await channel.declare_queue(result_queue_name, durable=True)
        
#         correlation_id = message.get("requestId", str(uuid.uuid4()))
#         message_body = json.dumps(message)
        
#         await channel.default_exchange.publish(
#             aio_pika.Message(
#                 body=message_body.encode('utf-8'),
#                 correlation_id=correlation_id,
#                 reply_to=result_queue_name,
#                 delivery_mode=aio_pika.DeliveryMode.PERSISTENT
#             ),
#             routing_key=queue_name
#         )
#         return correlation_id
    
# async def wait_for_message(result_queue_name: str, correlation_id: str, timeout: int = DEFAULT_OCR_TIMEOUT) -> dict:
#     """
#     이벤트 기반으로 지정된 결과 큐에서 correlation_id에 해당하는 메시지가 도착할 때까지 기다립니다.
#     """
#     connection = await get_async_rabbitmq_connection()
#     try:
#         channel = await connection.channel()
#         result_queue = await channel.declare_queue(result_queue_name, durable=True)

#         future = asyncio.get_event_loop().create_future()

#         async def on_message(message: aio_pika.IncomingMessage):
#             async with message.process():
#                 if message.correlation_id == correlation_id:
#                     try:
#                         data = json.loads(message.body.decode('utf-8'))
#                         if not future.done():
#                             future.set_result(data)
#                     except json.JSONDecodeError as e:
#                         if not future.done():
#                             future.set_exception(HTTPException(status_code=500, detail=f"JSON 파싱 오류: {e}"))
#                 else:
#                     # 다른 요청의 메시지는 재큐잉
#                     await message.nack(requeue=True)

#         # 비동기 소비자로 등록하여 메시지 도착 시 콜백 실행
#         await result_queue.consume(on_message, no_ack=False)
        
#         # 설정된 timeout 내에 future가 완료되길 기다림
#         result_data = await asyncio.wait_for(future, timeout=timeout)
#         return result_data
#     except asyncio.TimeoutError:
#         raise HTTPException(status_code=408, detail=f"OCR 처리 시간 초과 (timeout: {timeout}초)")
#     finally:
#         await connection.close()

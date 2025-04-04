import pika
import json
import time
import uuid
from fastapi import HTTPException
from typing import Dict, Any

from .config import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_USER,
    RABBITMQ_PASS,
    DEFAULT_OCR_TIMEOUT,
)

def get_rabbitmq_connection():
    """RabbitMQ 연결 객체를 반환합니다."""
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        RABBITMQ_HOST,
        RABBITMQ_PORT,
        '/',
        credentials,
        heartbeat=600, # 하트비트 설정으로 연결 안정성 향상
        blocked_connection_timeout=300
    )
    print("RABBITMQ_USER :", RABBITMQ_USER, "RABBITMQ_PASS :", RABBITMQ_PASS)
    print("RABBITMQ_HOST :", RABBITMQ_HOST, "RABBITMQ_PORT :", RABBITMQ_PORT)
    try:
        connection = pika.BlockingConnection(parameters)
        return connection
    except pika.exceptions.AMQPConnectionError as e:
        print(f"RabbitMQ 연결 실패: {e}")
        print(f"pika.exceptions.AMQPConnectionError : {pika.exceptions.AMQPConnectionError}")
        raise HTTPException(status_code=503, detail=f"RabbitMQ 서비스에 연결할 수 없습니다: {e}")

def send_message(queue_name: str, message: Dict[str, Any]) -> str:
    """지정된 큐에 메시지를 전송하고 correlation_id를 반환합니다."""
    connection = None
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()

        # 요청 큐 선언 (durable=True로 서버 재시작 시에도 유지)
        channel.queue_declare(queue=queue_name, durable=True)

        # 결과 큐 이름 생성 및 선언
        result_queue = f"{queue_name}.results"
        channel.queue_declare(queue=result_queue, durable=True)

        correlation_id = message.get("requestId", str(uuid.uuid4()))

        # 메시지 발행
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message), # 메시지를 JSON 문자열로 직렬화
            properties=pika.BasicProperties(
                delivery_mode=2,  # 메시지 영속성
                correlation_id=correlation_id,
                reply_to=result_queue  # 응답받을 큐 지정
            )
        )
        print(f"메시지 발행 성공: queue={queue_name}, correlation_id={correlation_id}, reply_to={result_queue}")
        return correlation_id
    except Exception as e:
        print(f"메시지 발행 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"메시지 발행 중 오류 발생: {e}")
    finally:
        if connection and not connection.is_closed:
            connection.close()

def poll_result(queue_name: str, correlation_id: str, timeout: int = DEFAULT_OCR_TIMEOUT) -> Dict[str, Any]:
    """결과 큐에서 특정 correlation_id를 가진 메시지를 폴링합니다."""
    result_queue = f"{queue_name}.results"
    print(f"결과 폴링 시작: queue={result_queue}, correlation_id={correlation_id}, timeout={timeout}초")
    connection = None
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()

        # 결과 큐 선언 (이미 선언되었을 수 있지만 안전하게 다시 선언)
        channel.queue_declare(queue=result_queue, durable=True)

        start_time = time.time()
        while time.time() - start_time < timeout:
            # basic_get으로 메시지 논블로킹 조회
            method_frame, properties, body = channel.basic_get(queue=result_queue, auto_ack=False)

            if method_frame:
                received_correlation_id = properties.correlation_id if properties else None
                print(f"메시지 수신: correlation_id={received_correlation_id}")

                if received_correlation_id == correlation_id:
                    print(f"일치하는 결과 수신: correlation_id={correlation_id}")
                    channel.basic_ack(delivery_tag=method_frame.delivery_tag) # 메시지 확인 (ack)
                    try:
                        response_data = json.loads(body.decode('utf-8')) # 바이트를 UTF-8로 디코딩 후 JSON 파싱
                        return response_data
                    except json.JSONDecodeError as e:
                        print(f"결과 JSON 파싱 오류: {e}, body={body[:100]}...")
                        raise HTTPException(status_code=500, detail="엔진 응답 처리 중 오류 발생 (JSON 파싱 실패)")
                    except Exception as e:
                        print(f"결과 처리 중 예외 발생: {e}")
                        raise HTTPException(status_code=500, detail=f"엔진 응답 처리 중 오류 발생: {e}")
                else:
                    # 요청한 ID와 다른 메시지인 경우, 큐에 다시 넣거나 (nack) 버림
                    print(f"다른 ID의 메시지 수신 (무시): {received_correlation_id} (기대: {correlation_id})")
                    # 중요: 다른 요청의 결과일 수 있으므로 버리지 않고 Nack 처리하여 큐에 다시 넣음 (requeue=True)
                    # 하지만 무한 루프 방지를 위해 특정 횟수 이상 재시도 시 버리는 로직 추가 필요할 수 있음
                    channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=True)

            # CPU 사용량을 줄이기 위해 짧은 대기 시간 추가
            time.sleep(0.5)
            print(f"폴링 중... 경과 시간: {time.time() - start_time:.1f}초")

        # 타임아웃 발생
        print(f"결과 폴링 타임아웃: correlation_id={correlation_id}")
        raise HTTPException(status_code=408, detail=f"OCR 처리 시간 초과 (timeout: {timeout}초)")

    except pika.exceptions.ConnectionClosedByBroker:
        print("RabbitMQ 연결이 브로커에 의해 닫혔습니다.")
        raise HTTPException(status_code=503, detail="RabbitMQ 연결 오류 (Broker)")
    except pika.exceptions.AMQPChannelError as err:
        print(f"RabbitMQ 채널 오류: {err}")
        raise HTTPException(status_code=503, detail=f"RabbitMQ 채널 오류: {err}")
    except pika.exceptions.AMQPConnectionError as err:
        print(f"RabbitMQ 연결 오류: {err}")
        raise HTTPException(status_code=503, detail=f"RabbitMQ 연결 오류: {err}")
    except Exception as e:
        print(f"결과 폴링 중 예상치 못한 오류 발생: {e}")
        # HTTP 예외가 아닌 경우, 일반 예외로 다시 발생시키거나 로깅 처리
        raise HTTPException(status_code=500, detail=f"결과 폴링 중 오류 발생: {e}")
    finally:
        if connection and not connection.is_closed:
            connection.close() 
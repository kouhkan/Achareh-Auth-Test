from datetime import timedelta
from random import randint

import redis as rd
from django.conf import settings

redis = rd.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)


def generate_prefix(identity: str) -> str:
    return f"identity:{identity}"


def generate_token() -> int:
    return randint(100000, 999999)


def set_user_token(identity: str) -> int:
    token = generate_token()
    redis.set(generate_prefix(identity), token, ex=timedelta(seconds=120))
    return token


def get_user_wait_time_token(identity: str) -> int:
    if redis.exists(generate_prefix(identity)):
        return redis.ttl(generate_prefix(identity))
    return 0


def check_user_token(identity: str, token: str) -> bool:
    if result := redis.get(generate_prefix(identity)):
        return result.decode("UTF-8") == token
    return False


def remove_token_user(identity: str) -> bool:
    redis.delete(generate_prefix(identity))
    return True


def generate_prefix_attemption(ip: str) -> str:
    return f"ip:{ip}"


def get_ip_attemption(ip: str) -> int:
    return redis.get(generate_prefix_attemption(ip))


def is_blocking_ip(ip: str) -> int:
    if (wait_time := redis.ttl(generate_prefix_attemption(ip))) > 0:
        return wait_time


def increase_attemption(ip: str) -> int:
    if not redis.exists(generate_prefix_attemption(ip)):
        redis.set(generate_prefix_attemption(ip), 0)

    current_count = int(get_ip_attemption(ip).decode('UTF-8'))

    if current_count != 3:
        current_count += 1
        redis.set(generate_prefix_attemption(ip), current_count)
        return 3 - current_count

    if redis.ttl(generate_prefix_attemption(ip)) == -1 and current_count == 3:
        redis.expire(generate_prefix_attemption(ip), time=timedelta(hours=1))
    return redis.ttl(generate_prefix_attemption(ip))


def remove_ip_from_redis(ip: str) -> None:
    redis.delete(generate_prefix_attemption(ip))

import json
import time
from pathlib import Path


def load_health():

    if not HEALTH_FILE.exists():
        return {}

    try:

        with open(
            HEALTH_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    except Exception:

        return {}
    
    
    
    
    
def save_health(data):

    HEALTH_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        HEALTH_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
        )
        
        
        
def mark_online(
    alias,
    latency,
    reliability,
):

    health = load_health()

    health[alias] = {

        "status": "healthy",

        "latency": latency,

        "reliability": reliability,

        "last_checked": int(
            time.time()
        ),

    }

    save_health(health)
    
    
    
    
    
def mark_offline(
    alias,
    reason,
):

    health = load_health()

    previous = health.get(
        alias,
        {},
    )

    health[alias] = {

        **previous,

        "status": "offline",

        "reason": reason,

        "last_checked": int(
            time.time()
        ),

    }

    save_health(health)
    
    
    
def get_health(alias):

    health = load_health()

    return health.get(
        alias,
        {},
    )
    
    
    
def is_healthy(alias):

    info = get_health(alias)

    return (
        info.get("status")
        == "healthy"
    )
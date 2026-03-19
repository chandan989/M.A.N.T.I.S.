"""
M.A.N.T.I.S. — API Routes
REST endpoints for the web dashboard.
"""

from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from mantis.agent.runtime import get_runtime
from mantis.config import get_settings
from mantis.types import LendingPosition, RiskProfile, StatusResponse

router = APIRouter(prefix="/api")


# ── Request Models ───────────────────────────────────────────────────────────

class RiskProfileUpdate(BaseModel):
    risk_profile: RiskProfile


class OverrideRequest(BaseModel):
    vault_id: str | None = None


# ── Status & Info ────────────────────────────────────────────────────────────

@router.get("/status")
async def get_status() -> StatusResponse:
    """Agent status + vault summary."""
    runtime = get_runtime()
    settings = get_settings()
    meta = await runtime.memory.get_agent_meta()

    vault_state = None
    vault_ids = settings.vault_id_list
    if vault_ids:
        cached = await runtime.memory.get_cached_vault_state(vault_ids[0])
        if cached:
            from mantis.types import VaultState
            vault_state = VaultState(**cached)

    # ── Lending position ─────────────────────────────────────────────
    lending_summary = None
    if settings.bonzo_lending_enabled:
        cached_lending = await runtime.memory.get_cached_vault_state("bonzo_lend")
        if cached_lending:
            lending_summary = LendingPosition(**cached_lending)

    return StatusResponse(
        agent_running=runtime.is_running,
        execution_paused=meta.execution_paused,
        last_action=meta.last_action,
        last_action_ts=meta.last_action_ts,
        risk_profile=RiskProfile(settings.risk_profile),
        vault_summary=vault_state,
        lending_summary=lending_summary,
        uptime_seconds=runtime.uptime if runtime.is_running else 0,
    )


@router.get("/health")
async def health():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "mantis-backend", "timestamp": time.time()}


# ── Vault ────────────────────────────────────────────────────────────────────

@router.get("/vault/{vault_id}")
async def get_vault(vault_id: str):
    """Detailed vault position."""
    runtime = get_runtime()
    cached = await runtime.memory.get_cached_vault_state(vault_id)
    if cached:
        return cached

    # Try live read
    try:
        vault = await runtime.hedera.collect()
        return vault.model_dump()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Logs ─────────────────────────────────────────────────────────────────────

@router.get("/logs")
async def get_logs(limit: int = 50):
    """Recent agent action logs."""
    runtime = get_runtime()
    logs = await runtime.memory.get_recent_logs(limit=limit)
    return {"logs": logs, "count": len(logs)}


# ── APY History ──────────────────────────────────────────────────────────────

@router.get("/apy-history")
async def get_apy_history(vault_id: str | None = None, limit: int = 100):
    """APY snapshots over time."""
    runtime = get_runtime()
    settings = get_settings()
    vid = vault_id or (settings.vault_id_list[0] if settings.vault_id_list else "")
    if not vid:
        return {"history": [], "count": 0}

    history = await runtime.memory.get_apy_history(vid, limit=limit)
    return {"history": [h.model_dump() for h in history], "count": len(history)}


# ── Config ───────────────────────────────────────────────────────────────────

@router.get("/config")
async def get_config():
    """Current risk profile & thresholds."""
    settings = get_settings()
    return {
        "risk_profile": settings.risk_profile,
        "volatility_threshold_widen": settings.volatility_threshold_widen,
        "volatility_threshold_tighten": settings.volatility_threshold_tighten,
        "volatility_threshold_emergency": settings.volatility_threshold_emergency,
        "sentiment_threshold_harvest": settings.sentiment_threshold_harvest,
        "sentiment_threshold_swap": settings.sentiment_threshold_swap,
        "min_harvest_interval_hours": settings.min_harvest_interval_hours,
        "sentry_interval_seconds": settings.sentry_interval_seconds,
    }


@router.put("/config/risk-profile")
async def update_risk_profile(body: RiskProfileUpdate):
    """Update the active risk profile."""
    settings = get_settings()
    settings.risk_profile = body.risk_profile.value
    return {"risk_profile": settings.risk_profile, "updated": True}


# ── Override Controls ────────────────────────────────────────────────────────

@router.post("/override/harvest")
async def trigger_harvest(body: OverrideRequest | None = None):
    """Trigger an immediate manual harvest (bypasses interval guard)."""
    runtime = get_runtime()
    settings = get_settings()

    vault_id = (
        (body.vault_id if body else None)
        or (settings.vault_id_list[0] if settings.vault_id_list else "")
    )
    if not vault_id:
        raise HTTPException(status_code=400, detail="No vault ID configured")

    result = await runtime.hedera.harvest(vault_id)
    if result.success:
        await runtime.memory.log_action(
            action="HARVEST",
            message=f"Manual harvest triggered via dashboard — {result.message}",
            tx_id=result.tx_id,
        )
    return result.model_dump()


@router.post("/override/pause")
async def pause_execution():
    """Pause agent execution."""
    runtime = get_runtime()
    meta = await runtime.memory.get_agent_meta()
    meta.execution_paused = True
    await runtime.memory.update_agent_meta(meta)
    return {"execution_paused": True, "message": "Agent execution paused"}


@router.post("/override/resume")
async def resume_execution():
    """Resume agent execution."""
    runtime = get_runtime()
    meta = await runtime.memory.get_agent_meta()
    meta.execution_paused = False
    await runtime.memory.update_agent_meta(meta)
    return {"execution_paused": False, "message": "Agent execution resumed"}


# ── Bootstrap (worldmonitor-inspired batch endpoint) ─────────────────────────

BOOTSTRAP_CACHE_KEYS = {
    "status": "bootstrap:status",
    "market": "bootstrap:market",
    "sentiment": "bootstrap:sentiment",
    "vault": "bootstrap:vault",
    "lending": "bootstrap:lending",
    "logs": "bootstrap:logs",
    "config": "bootstrap:config",
}


@router.get("/bootstrap")
async def bootstrap(keys: str | None = None):
    """
    Batch-read all cached data in one call.
    Inspired by worldmonitor's bootstrap.js — reduces startup API calls.

    Query params:
      ?keys=status,market,sentiment  — fetch specific keys only
    """
    from mantis.data.cache import get_cache

    runtime = get_runtime()
    settings = get_settings()
    cache = get_cache()

    # Determine which keys to fetch
    if keys:
        requested = [k.strip() for k in keys.split(",") if k.strip()]
        registry = {k: v for k, v in BOOTSTRAP_CACHE_KEYS.items() if k in requested}
    else:
        registry = BOOTSTRAP_CACHE_KEYS

    data = {}
    missing = []

    for name, cache_key in registry.items():
        cached = cache.get(cache_key)
        if cached is not None:
            data[name] = cached
        else:
            missing.append(name)

    # Fill missing data from live sources
    if "status" in missing:
        meta = await runtime.memory.get_agent_meta()
        data["status"] = {
            "agent_running": runtime.is_running,
            "execution_paused": meta.execution_paused,
            "last_action": meta.last_action.value if meta.last_action else "NO_OP",
            "uptime_seconds": runtime.uptime if runtime.is_running else 0,
        }
        cache.set(BOOTSTRAP_CACHE_KEYS["status"], data["status"])
        missing.remove("status")

    if "config" in missing:
        data["config"] = {
            "risk_profile": settings.risk_profile,
            "network": settings.hedera_network,
            "sentry_interval": settings.sentry_interval_seconds,
        }
        cache.set(BOOTSTRAP_CACHE_KEYS["config"], data["config"])
        missing.remove("config")

    if "logs" in missing:
        logs = await runtime.memory.get_recent_logs(limit=20)
        data["logs"] = logs
        cache.set(BOOTSTRAP_CACHE_KEYS["logs"], logs)
        missing.remove("logs")

    from fastapi.responses import JSONResponse
    return JSONResponse(
        content={"data": data, "missing": missing},
        headers={
            "Cache-Control": "public, s-maxage=30, stale-while-revalidate=60",
        },
    )


# ── Signals Feed ─────────────────────────────────────────────────────────────

@router.get("/signals")
async def get_signals():
    """
    Structured signal feed from the Sentry skill.
    Inspired by worldmonitor's enrichment/signals.js.
    """
    from mantis.data.cache import get_cache
    cache = get_cache()

    # Check if we have cached signals from the latest sentry run
    cached = cache.get("sentry:all_signals")
    if cached:
        return {"signals": cached, "count": len(cached), "cached": True}

    # Otherwise trigger a fresh collect
    runtime = get_runtime()
    try:
        sentry_data = await runtime.sentry.collect()
        return {
            "signals": sentry_data.top_signals,
            "count": len(sentry_data.top_signals),
            "sentiment": sentry_data.score,
            "label": sentry_data.label.value,
            "cached": False,
        }
    except Exception as exc:
        return {"signals": [], "count": 0, "error": str(exc)}


# ── Cache Stats ──────────────────────────────────────────────────────────────

@router.get("/cache/stats")
async def cache_stats():
    """Cache statistics for monitoring."""
    from mantis.data.cache import get_cache
    cache = get_cache()
    return cache.stats()


# ── Balance ──────────────────────────────────────────────────────────────────

@router.get("/balance")
async def get_balance():
    """Get operator account HBAR and token balances."""
    runtime = get_runtime()
    return await runtime.hedera.get_balance()


# ── Bonzo Lend Endpoints ─────────────────────────────────────────────────

@router.get("/lending/position")
async def get_lending_position():
    """Current Bonzo Lend position (health factor, collateral, debt)."""
    runtime = get_runtime()
    settings = get_settings()

    if not settings.bonzo_lending_enabled:
        return {"enabled": False, "message": "Bonzo Lend integration is disabled"}

    # Try cached first
    cached = await runtime.memory.get_cached_vault_state("bonzo_lend")
    if cached:
        return {"position": cached, "cached": True}

    # Fresh read
    try:
        position = await runtime.bonzo_lend.collect()
        return {"position": position.model_dump(), "cached": False}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/lending/reserves")
async def get_lending_reserves():
    """Available lending markets and APYs."""
    runtime = get_runtime()
    settings = get_settings()

    if not settings.bonzo_lending_enabled:
        return {"enabled": False, "reserves": []}

    try:
        reserves = await runtime.bonzo_lend.get_reserves()
        return {
            "reserves": [r.model_dump() for r in reserves],
            "count": len(reserves),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


class LendingActionRequest(BaseModel):
    asset: str = "WHBAR"
    amount: float = 0.0
    rate_mode: int = 2  # 1=stable, 2=variable


@router.post("/override/supply")
async def trigger_supply(body: LendingActionRequest):
    """Trigger a manual supply into Bonzo Lend."""
    runtime = get_runtime()
    settings = get_settings()

    if not settings.bonzo_lending_enabled:
        raise HTTPException(status_code=400, detail="Bonzo Lend is disabled")

    result = await runtime.bonzo_lend.supply(asset=body.asset, amount=body.amount)
    if result.success:
        await runtime.memory.log_action(
            action="SUPPLY",
            message=f"Manual supply: {body.amount} {body.asset} — {result.message}",
            tx_id=result.tx_id,
        )
    return result.model_dump()


@router.post("/override/repay")
async def trigger_repay(body: LendingActionRequest):
    """Trigger a manual repay on Bonzo Lend."""
    runtime = get_runtime()
    settings = get_settings()

    if not settings.bonzo_lending_enabled:
        raise HTTPException(status_code=400, detail="Bonzo Lend is disabled")

    result = await runtime.bonzo_lend.repay(
        asset=body.asset, amount=body.amount, rate_mode=body.rate_mode
    )
    if result.success:
        await runtime.memory.log_action(
            action="REPAY",
            message=f"Manual repay: {body.amount} {body.asset} — {result.message}",
            tx_id=result.tx_id,
        )
    return result.model_dump()


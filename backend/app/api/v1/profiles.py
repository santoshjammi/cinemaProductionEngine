"""Production profile routes for GENESIS.

Exposes the available production profiles (runtime targets, scene
policies, scene classes) so the frontend can present a profile
selector before story generation begins.
"""

from fastapi import APIRouter, HTTPException

from backend.app.services.profile_service import (
    get_profile,
    list_profiles,
    get_scene_classes,
)

router = APIRouter(prefix="/api/v1/profiles", tags=["profiles"])


@router.get("")
async def get_profiles():
    return {"profiles": list_profiles(), "scene_classes": get_scene_classes()}


@router.get("/{profile_id}")
async def get_profile_detail(profile_id: str):
    profile = get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile
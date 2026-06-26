import os
import glob
import json
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from auth import verify_password, create_access_token, get_current_user_from_cookie
from init_db import init_db

init_db()

app = FastAPI(title="Dynamic OCR Staging Dashboard Engine")
templates = Jinja2Templates(directory="templates")

CONFIG_PATH = "pools.json"
BASE_DATA_DIR = "/data"

def load_dynamic_pools_config() -> dict:
    """Loads pools from json configuration file."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

# 1. Mount the dynamic pools discovered in the JSON configuration file
pools_config = load_dynamic_pools_config()
for pool_id, config in pools_config.items():
    dir_path = config.get("directory_path")
    if dir_path and os.path.exists(dir_path):
        # Dynamically mount each path securely
        app.mount(f"/mount_{pool_id}", StaticFiles(directory=dir_path), name=f"mount_{pool_id}")

# 2. Keep the default fallback /data subfolder mounting system active
if os.path.exists(BASE_DATA_DIR):
    app.mount("/static_assets", StaticFiles(directory=BASE_DATA_DIR), name="static_assets")


def scan_and_sort_images(directory_path: str, url_route_prefix: str) -> list:
    """Scans visual disk metrics and orders entries latest first."""
    if not os.path.exists(directory_path):
        return []
    
    extensions = ("*.png", "*.jpg", "*.jpeg")
    found_files = []
    for ext in extensions:
        found_files.extend(glob.glob(os.path.join(directory_path, ext)))
        
    found_files.sort(key=os.path.getmtime, reverse=True)
    
    image_list = []
    for f in found_files:
        filename = os.path.basename(f)
        mtime = int(os.stat(f).st_mtime)
        formatted_time = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        
        image_list.append({
            "filename": filename,
            "timestamp": formatted_time,
            "web_url": f"/{url_route_prefix}/{filename}"
        })
    return image_list


@app.get("/", response_class=HTMLResponse)
async def main_dashboard(request: Request):
    try:
        get_current_user_from_cookie(request)
    except Exception:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    dynamic_pools = {}

    # Gather data from the configuration file
    current_config = load_dynamic_pools_config()
    for pool_id, config in current_config.items():
        dir_path = config.get("directory_path")
        if os.path.exists(dir_path):
            dynamic_pools[pool_id] = {
                "display_name": config.get("display_name", pool_id),
                "images": scan_and_sort_images(dir_path, f"mount_{pool_id}")
            }

    # Gather all fallback baseline subfolders inside the legacy data volume mount
    if os.path.exists(BASE_DATA_DIR):
        for entry in os.listdir(BASE_DATA_DIR):
            full_path = os.path.join(BASE_DATA_DIR, entry)
            if os.path.isdir(full_path) and entry not in dynamic_pools:
                display_name = entry.replace("_", " ").title()
                dynamic_pools[entry] = {
                    "display_name": display_name,
                    "images": scan_and_sort_images(full_path, f"static_assets/{entry}")
                }

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "pools": dynamic_pools
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
async def login_action(request: Request, username: str = Form(...), password: str = Form(...)):
    if not verify_password(username, password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid System Credentials"})
    
    token = create_access_token(data={"sub": username})
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=token, httponly=True, samesite="lax")
    return response

@app.get("/logout")
async def logout_action():
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response
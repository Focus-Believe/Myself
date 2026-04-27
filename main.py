import json
import os
from datetime import datetime
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from db import DB
from manager import Manager

app = FastAPI()
db = DB()
mgr = Manager()

# static এবং templates ফোল্ডার সেটআপ
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    # এটি templates/index.html ফাইলটি লোড করবে
    return templates.TemplateResponse("index.html", {"request": request})

async def send_users():
    users = mgr.users()
    for ws in mgr.name_to_ws.values():
        await ws.send_text(json.dumps({
            "type": "users",
            "data": users
        }))

@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = json.loads(await websocket.receive_text())
            t = data["type"]

            # REGISTER
            if t == "register":
                ok = db.register(data["name"], data["password"])
                await websocket.send_text(json.dumps({
                    "type": "register_ok" if ok else "register_fail"
                }))

            # LOGIN
            elif t == "login":
                ok = db.login(data["name"], data["password"])

                if ok:
                    await mgr.connect(data["name"], websocket)
                    await send_users()

                await websocket.send_text(json.dumps({
                    "type": "login_ok" if ok else "login_fail"
                }))

            # DM (FAST O(1))
            elif t == "dm":
                sender = mgr.get_name(websocket)
                target = mgr.get_ws(data["to"])
                time = datetime.now().strftime("%H:%M")

                db.save_msg(sender, data["to"], None, data["msg"], time)

                if target:
                    await target.send_text(json.dumps({
                        "type": "msg",
                        "from": sender,
                        "msg": data["msg"],
                        "time": time
                    }))

            # ROOM
            elif t == "room":
                sender = mgr.get_name(websocket)
                time = datetime.now().strftime("%H:%M")

                db.save_msg(sender, None, data["room"], data["msg"], time)

                msg = json.dumps({
                    "type": "room",
                    "from": sender,
                    "msg": data["msg"],
                    "time": time
                })

                for ws in mgr.name_to_ws.values():
                    await ws.send_text(msg)

    except WebSocketDisconnect:
        mgr.disconnect(websocket)
        await send_users()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
        

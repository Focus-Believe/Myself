import uvicorn
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from db import DataB
app=FastAPI()
db=DataB()
clients={}
html='''
<h1>CHAT APP</h1>
<h4>UPDATE</h4>
<input id ='name' placeholder ='Enter Name'>
<br>
<input id ='msg' placeholder ='Write Message'>
<br>
<button onclick='send()'>Send</button>
<br>
<h3> User List </h3>
<ul id ='user'></ul>
<h3>Message </h3>
<ul id ='chat'></ul>
<script>
let ws = new WebSocket(
  (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws'
);
function send(){
let user=document.getElementById('name').value;
let message =document.getElementById('msg').value;
ws.send(JSON.stringify({
name:user,
msg:message}));
document.getElementById('msg').value='';
}
ws.onmessage=function(event){
let data=JSON.parse(event.data);
if(data.type==='users'){
let ul=document.getElementById('user');
ul.innerHTML='';
data.data.forEach(u=>{
let li=document.createElement('li');
li.textContent=u;
ul.appendChild(li);})
}
if(data.type ==='message'){
let li=document.createElement('li');
li.textContent= data.name + ':' + data.msg;
document.getElementById('chat').appendChild(li);
}}
</script>

'''
@app.get('/')
def home():
	return HTMLResponse(html)
@app.websocket('/ws')
async def webb(websocket: WebSocket):
	await websocket.accept()
	try:
		while True:
			data =await websocket.receive_text()
			mst=json.loads(data)
			name=mst.get('name')
			msg=mst.get('msg')
			if websocket not in clients and name:
				clients[websocket]=name
				await svup()
				rows=db.sh()
				for row in rows:
					await websocket.send_text(json.dumps({
					'type': 'message',
					'name': row[0],
					'msg': row[1]}))
			if name and msg:
				db.sv(name, msg)
				await brodc({'type': 'message',
				'name': name,
				'msg': msg})
	except WebSocketDisconnect:
		clients.pop(websocket, None)
		await svup()
async def brodc(message):
	for client in list(clients):
		try:
			await client.send_text(json.dumps(message))
		except:
			clients.pop(client, None)

async def svup():
	name=list(clients.values())
	for client in list(clients):
		try:
			await client.send_text(json.dumps({'type': 'users',
			'data': name}))
		except:
			clients.pop(client, None)
		
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)

import json,sys,time,subprocess,urllib.request
parts=[
"¿Te ha pasado que te despiertas justo un minuto antes de que suene la alarma? No es casualidad. Tu cerebro tiene un reloj interno, una zona llamada núcleo supraquiasmático, que decide cuándo duermes y cuándo despiertas.",
"Y aquí viene lo increíble: en un experimento, a un grupo de personas les dijeron a qué hora las iban a despertar... y su cuerpo empezó a liberar hormonas para despertarse casi una hora antes. Sí: tu cuerpo se prepara para despertar antes que tú.",
"Por eso, si te levantas siempre a la misma hora, tu reloj interno aprende el horario y te despierta solo. Pero ojo: si cambias tu horario cada día, lo confundes, y por eso te levantas cansado. Así que ya sabes: misma hora, todos los días. ¿A ti te pasa? Cuéntamelo en los comentarios."]
def curl(args): return subprocess.run(["curl","-sS","-m","30"]+args,capture_output=True,text=True).stdout
ids=[]
for p in parts:
    body=json.dumps({"text":p,"provider":"elevenlabs","model_id":"eleven_v3","language_code":"es","voice_settings":{"stability":0.5,"speed":1.08}})
    r=json.loads(curl(["-X","POST","https://api.vibi.pro/v1/text-to-speech/ojGau167OE7nUATM1xDa","-H","Content-Type: application/json","-d",body]))
    print(r,flush=True); ids.append(r["id"])
done={}
t0=time.time()
while len(done)<len(ids) and time.time()-t0<420:
    for i,id in enumerate(ids):
        if i in done: continue
        d=json.loads(curl([f"https://api.vibi.pro/v1/history/{id}"]))
        if d["status"] in("completed","failed"):
            done[i]=d; print(i,d["status"],d.get("credits_deducted"),flush=True)
            if d["status"]=="completed": subprocess.run(["curl","-sS","-o",f"p{i}.mp3",d["result"]["audio_url"]])
    time.sleep(5)
print("pending:",[i for i in range(len(ids)) if i not in done])

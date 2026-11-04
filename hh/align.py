"""Alinha as frases do roteiro (timing.json) com a narração (narr.mp3) pelas pausas da fala.
Uso: python3 -m hh.align videos/<pasta>
Escreve start/end/chunks em cada segmento e o tail do vídeo. Programação dinâmica:
agrupa os trechos de fala consecutivos de modo que a duração de cada frase fique
proporcional ao número de caracteres."""
import os, sys
os.chdir(sys.argv[1])
import json, re, subprocess, sys
r = subprocess.run(["ffmpeg","-i","narr.mp3","-af","silencedetect=noise=-38dB:d=0.18","-f","null","-"],capture_output=True,text=True).stderr
ss=[float(x) for x in re.findall(r"silence_start: ([\d.]+)",r)]; se=[float(x) for x in re.findall(r"silence_end: ([\d.]+)",r)]
dur=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0","narr.mp3"],capture_output=True,text=True).stdout)
sil=list(zip(ss,se))
chunks=[]; prev=0.0
for a,b in sil:
    if a-prev>0.05: chunks.append((prev,a))
    prev=b
if dur-prev>0.05: chunks.append((prev,dur))
T=json.load(open("timing.json")); sents=[s["t"] for s in T["segments"]]
L=[len(s) for s in sents]; n,m=len(sents),len(chunks)
tot=sum(b-a for a,b in chunks); rate=tot/sum(L)
INF=1e18; dp=[[INF]*(m+1) for _ in range(n+1)]; bk=[[0]*(m+1) for _ in range(n+1)]; dp[0][0]=0
for i in range(1,n+1):
    exp=rate*L[i-1]
    for j in range(i,m+1):
        for k in range(i-1,j):
            if dp[i-1][k]>=INF: continue
            d=chunks[j-1][1]-chunks[k][0]   # span incluindo pausas internas
            c=dp[i-1][k]+(d-exp)**2/exp
            if c<dp[i][j]: dp[i][j]=c; bk[i][j]=k
j=m; out=[]
for i in range(n,0,-1):
    k=bk[i][j]; out.append((chunks[k][0],chunks[j-1][1],chunks[k:j])); j=k
out.reverse()
for (a,b,_),s in zip(out,sents): print(f"{a:6.2f}-{b:6.2f} ({b-a:4.2f} exp {rate*len(s):4.2f})  {s}")
T["lead_in"]=0
for seg,(a,b,ch) in zip(T["segments"],out):
    seg["start"]=round(a,3); seg["end"]=round(b,3); seg["chunks"]=[[round(x,3),round(y,3)] for x,y in ch]
T["audio_dur"]=dur; T["tail"]=round(max(3.0,dur-out[-1][1]+2.2),2)
json.dump(T,open("timing.json","w"),ensure_ascii=False,indent=1)

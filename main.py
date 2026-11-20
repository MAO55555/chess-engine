import os,sys,urllib.request,json
V=[0,100,320,330,500,900,0]
def parse(f):
 b=[0]*64;sq=0
 for c in f.split()[0]:
  if c=='/':continue
  elif c.isdigit():sq+=int(c)
  else:b[sq]=({'p':1,'n':2,'b':3,'r':4,'q':5,'k':6}[c.lower()]<<1)|(1 if c.isupper()else 0);sq+=1
 return b,1 if f.split()[1]=='w'else 0
def att(b,sq,by):
 r=sq>>3;f=sq&7;pr=r+(1 if by else-1)
 if 0<=pr<8:
  for d in(-1,1):
   if 0<=f+d<8 and b[pr*8+f+d]==(2|by):return 1
 for dr,df in[(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
  nr=r+dr;nf=f+df
  if 0<=nr<8 and 0<=nf<8 and b[nr*8+nf]==(4|by):return 1
 for dr in(-1,0,1):
  for df in(-1,0,1):
   if dr|df:
    nr=r+dr;nf=f+df
    if 0<=nr<8 and 0<=nf<8 and b[nr*8+nf]==(12|by):return 1
 for dr,df in[(-1,-1),(-1,1),(1,-1),(1,1),(0,-1),(0,1),(-1,0),(1,0)]:
  nr=r+dr;nf=f+df;dg=dr and df
  while 0<=nr<8 and 0<=nf<8:
   p=b[nr*8+nf]
   if p:
    if p&1==by and((dg and p>>1 in(3,5))or(not dg and p>>1 in(4,5))):return 1
    break
   nr+=dr;nf+=df
 return 0
def kp(b,s):
 for i in range(64):
  if b[i]==(12|s):return i
 return 0
def ev(b,s):
 e=0
 for i in range(64):
  p=b[i]
  if p:e+=(1 if p&1==s else-1)*V[p>>1]
 return e
def gen(b,s):
 mv=[]
 for sq in range(64):
  p=b[sq]
  if not p or p&1!=s:continue
  t=p>>1;r=sq>>3;f=sq&7
  if t==1:
   dr=-1 if s else 1;sr=6 if s else 1
   ns=sq+dr*8
   if 0<=ns<64 and not b[ns]:
    mv.append((sq,ns))
    if r==sr and not b[sq+dr*16]:mv.append((sq,sq+dr*16))
   for df in(-1,1):
    nf=f+df
    if 0<=nf<8:
     ns=sq+dr*8+df
     if 0<=ns<64 and b[ns]and b[ns]&1!=s:mv.append((sq,ns))
  elif t==2:
   for dr2,df in[(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
    nr=r+dr2;nf=f+df
    if 0<=nr<8 and 0<=nf<8:
     ns=nr*8+nf
     if not b[ns]or b[ns]&1!=s:mv.append((sq,ns))
  elif t==6:
   for dr2 in(-1,0,1):
    for df in(-1,0,1):
     if dr2|df:
      nr=r+dr2;nf=f+df
      if 0<=nr<8 and 0<=nf<8:
       ns=nr*8+nf
       if not b[ns]or b[ns]&1!=s:mv.append((sq,ns))
  else:
   ds=[]
   if t in(3,5):ds+=[(-1,-1),(-1,1),(1,-1),(1,1)]
   if t in(4,5):ds+=[(0,-1),(0,1),(-1,0),(1,0)]
   for dr2,df in ds:
    nr=r+dr2;nf=f+df
    while 0<=nr<8 and 0<=nf<8:
     ns=nr*8+nf
     if b[ns]:
      if b[ns]&1!=s:mv.append((sq,ns))
      break
     mv.append((sq,ns));nr+=dr2;nf+=df
 return mv
def mk(b,fr,to):
 nb=b[:];nb[to]=nb[fr];nb[fr]=0
 if nb[to]>>1==1 and(to>>3)==(0 if nb[to]&1 else 7):nb[to]=10|(nb[to]&1)
 return nb
def srch(b,s,d,a,bt):
 if d<=0:return ev(b,s)
 mv=gen(b,s);found=0
 mv.sort(key=lambda m:-(V[b[m[1]]>>1]if b[m[1]]else 0))
 for m in mv:
  nb=mk(b,m[0],m[1])
  if att(nb,kp(nb,s),s^1):continue
  found=1;sc=-srch(nb,s^1,d-1,-bt,-a)
  if sc>=bt:return bt
  if sc>a:a=sc
 if not found:return-30000 if att(b,kp(b,s),s^1)else 0
 return a
def fsq(s):return(8-int(s[1]))*8+ord(s[0])-97
def run():
 url=os.environ.get('MAKEFUN_ENV_URL')
 if not url:sys.exit(1)
 while True:
  rq=urllib.request.Request(url+'/game',method='POST',headers={'Content-Type':'application/json'},data=b'{}')
  d=json.loads(urllib.request.urlopen(rq,timeout=30).read().decode())
  if d.get('status')=='done':sys.stderr.write('done\n');sys.exit(0)
  fen=d['fen'];leg=d['legal_moves'];gid=d['game']
  if not leg:continue
  b,s=parse(fen);best=leg[0];bs=-999999
  for u in leg:
   fr=fsq(u[:2]);to=fsq(u[2:4])
   nb=b[:];nb[to]=nb[fr];nb[fr]=0
   t=nb[to]>>1;c=nb[to]&1
   if t==1 and(to>>3)==(0 if c else 7):nb[to]=10|c
   if len(u)==5:nb[to]=({'q':5,'r':4,'b':3,'n':2}.get(u[4],5)<<1)|c
   sc=-srch(nb,s^1,2,-999999,999999)
   if sc>bs:bs=sc;best=u
  rq=urllib.request.Request(url+'/move',method='POST',headers={'Content-Type':'application/json'},data=json.dumps({'game':gid,'move':best}).encode())
  rd=json.loads(urllib.request.urlopen(rq,timeout=30).read().decode())
  if rd.get('status')=='done':sys.stderr.write('done\n');sys.exit(0)
if __name__=='__main__':run()

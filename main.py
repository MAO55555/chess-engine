import os,sys,urllib.request as U,json as J
V=[0,100,320,330,500,900,0]
N=[(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
B=[(-1,-1),(-1,1),(1,-1),(1,1)];R=[(0,-1),(0,1),(-1,0),(1,0)];A=B+R
Q=lambda s:(8-int(s[1]))*8+ord(s[0])-97
kp=lambda b,s:b.index(12|s)
ev=lambda b,s:sum((1 if p&1==s else-1)*V[p>>1]for p in b)
def parse(f):
 p=f.split();b=[0]*64;q=0
 for c in p[0]:
  if c=='/':continue
  if c.isdigit():q+=int(c)
  else:b[q]=('_pnbrqk'.find(c.lower())<<1)|c.isupper();q+=1
 s=int(p[1]=='w');cr=sum(1<<i for i,c in enumerate('KQkq')if c in p[2])
 ep=Q(p[3])if len(p)>3 and p[3]!='-'else-1
 return b,s,cr,ep
def att(b,sq,by):
 r=sq>>3;f=sq&7;pr=r+(1 if by else-1)
 if 0<=pr<8:
  for d in(-1,1):
   if 0<=f+d<8 and b[pr*8+f+d]==(2|by):return 1
 for dr,df in N:
  nr=r+dr;nf=f+df
  if 0<=nr<8 and 0<=nf<8 and b[nr*8+nf]==(4|by):return 1
 for dr,df in A:
  nr=r+dr;nf=f+df
  if 0<=nr<8 and 0<=nf<8:
   if b[nr*8+nf]==(12|by):return 1
   dg=dr and df
   while 0<=nr<8 and 0<=nf<8:
    p=b[nr*8+nf]
    if p:
     if p&1==by and((dg and p>>1 in(3,5))or(not dg and p>>1 in(4,5))):return 1
     break
    nr+=dr;nf+=df
 return 0
def gen(b,s,cr,ep):
 mv=[]
 for sq in range(64):
  p=b[sq]
  if not p or p&1!=s:continue
  t=p>>1;r=sq>>3;f=sq&7
  if t==1:
   dr=-1 if s else 1;ns=sq+dr*8
   if 0<=ns<64 and not b[ns]:
    mv+=[(sq,ns,-1)]
    if r==(6 if s else 1)and not b[sq+dr*16]:mv+=[(sq,sq+dr*16,-1)]
   for df in(-1,1):
    nf=f+df
    if 0<=nf<8:
     ns=sq+dr*8+df
     if 0<=ns<64:
      if b[ns]and b[ns]&1!=s:mv+=[(sq,ns,-1)]
      elif ns==ep:mv+=[(sq,ns,sq+df)]
  elif t==2:
   for dr2,df in N:
    nr=r+dr2;nf=f+df
    if 0<=nr<8 and 0<=nf<8:
     ns=nr*8+nf
     if not b[ns]or b[ns]&1!=s:mv+=[(sq,ns,-1)]
  elif t==6:
   for dr2,df in A:
    nr=r+dr2;nf=f+df
    if 0<=nr<8 and 0<=nf<8:
     ns=nr*8+nf
     if not b[ns]or b[ns]&1!=s:mv+=[(sq,ns,-1)]
   ks=60 if s else 4;o=s^1
   if sq==ks:
    if cr&(1 if s else 4)and not(b[ks+1]or b[ks+2])and b[ks+3]==(8|s)and not(att(b,ks,o)or att(b,ks+1,o)or att(b,ks+2,o)):mv+=[(ks,ks+2,-1)]
    if cr&(2 if s else 8)and not(b[ks-1]or b[ks-2]or b[ks-3])and b[ks-4]==(8|s)and not(att(b,ks,o)or att(b,ks-1,o)or att(b,ks-2,o)):mv+=[(ks,ks-2,-1)]
  else:
   ds=B if t==3 else R if t==4 else A
   for dr2,df in ds:
    nr=r+dr2;nf=f+df
    while 0<=nr<8 and 0<=nf<8:
     ns=nr*8+nf
     if b[ns]:
      if b[ns]&1!=s:mv+=[(sq,ns,-1)]
      break
     mv+=[(sq,ns,-1)];nr+=dr2;nf+=df
 return mv
def mk(b,s,cr,ep,fr,to,epc):
 nb=b[:];nb[to]=nb[fr];nb[fr]=0;nc=cr;ne=-1
 if epc>=0:nb[epc]=0
 t=nb[to]>>1;c=nb[to]&1
 if t==1:
  if(to>>3)==(0 if c else 7):nb[to]=10|c
  if abs(fr-to)==16:ne=(fr+to)//2
 if t==6:
  nc&=~(3 if c else 12);d=to-fr
  if d==2:nb[to-1]=nb[to+1];nb[to+1]=0
  elif d==-2:nb[to+1]=nb[to-2];nb[to-2]=0
 for x,m in[(0,8),(7,4),(56,2),(63,1)]:
  if fr==x or to==x:nc&=~m
 return nb,nc,ne
def srch(b,s,cr,ep,d,a,bt):
 if d<=0:return ev(b,s)
 mv=gen(b,s,cr,ep);fd=0
 mv.sort(key=lambda m:-V[b[m[1]]>>1])
 for m in mv:
  nb,nc,ne=mk(b,s,cr,ep,m[0],m[1],m[2])
  if att(nb,kp(nb,s),s^1):continue
  fd=1;sc=-srch(nb,s^1,nc,ne,d-1,-bt,-a)
  if sc>=bt:return bt
  if sc>a:a=sc
 if not fd:return-(30000+d)if att(b,kp(b,s),s^1)else 0
 return a
PM={'q':10,'r':8,'b':6,'n':4}
def run():
 u=os.environ.get('MAKEFUN_ENV_URL')
 if not u:sys.exit(1)
 H={'Content-Type':'application/json'}
 def post(p,d):return J.loads(U.urlopen(U.Request(u+p,method='POST',headers=H,data=J.dumps(d).encode()),timeout=30).read())
 while True:
  d=post('/game',{})
  if d.get('status')=='done':sys.exit(0)
  fen=d['fen'];leg=d['legal_moves'];gid=d['game']
  if not leg:continue
  b,s,cr,ep=parse(fen);best=leg[0];bs=-999999
  for m in leg:
   fr=Q(m[:2]);to=Q(m[2:4]);epc=-1
   t=b[fr]>>1;c=b[fr]&1
   if t==1 and to==ep:epc=to+(8 if c else-8)
   nb,nc,ne=mk(b,s,cr,ep,fr,to,epc)
   if len(m)==5:nb[to]=PM.get(m[4],10)|c
   sc=-srch(nb,s^1,nc,ne,4,-999999,999999)
   if sc>bs:bs=sc;best=m
  d=post('/move',{'game':gid,'move':best})
  if d.get('status')=='done':sys.exit(0)
if __name__=='__main__':run()

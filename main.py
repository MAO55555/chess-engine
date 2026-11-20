import os,urllib.request,json,sys
def idx(r,c):return r*8+c
def rc(i):return(i//8,i%8)
def p(f):
    b=[0]*64;r=f.split();s=0;p=0
    for ch in r[0]:
        if ch=='/':continue
        if ch.isdigit():
            for _ in range(int(ch)):b[_+p]=0
            p+=int(ch)-1
        else:
            pc=0;c=1 if ch.isupper()else 0
            ch=ch.lower()
            pc={'p':1,'n':2,'b':3,'r':4,'q':5,'k':6}.get(ch,0)
            b[p]=(pc<<3)|c;p+=1
    return b,1 if r[1]=='b'else 0
S={1:100,2:320,3:330,4:500,5:900}
def E(b,s):
    r=0
    for i in range(64):
        pc=b[i]>>3;c=b[i]&7
        if pc in S:r+=(1 if c==s else -1)*S[pc]
    return r
def N(b,s,d,a,b_):
    if d==0:return E(b,s)
    m=[]
    #pawns
    for sq in range(64):
        pc=b[sq]>>3;c=b[sq]&7
        if pc!=1 or c!=s:continue
        mp=8 if s==0 else -8
        for dn in [-1,1]:
            ns=sq+mp+dn
            if 0<=ns<64 and ns//8!=7 and b[ns]and b[ns]>>3!=c:m.append((sq,ns))
        ns=sq+mp
        if 0<=ns<64 and not b[ns]:
            if ns//8==7:m.append((sq,ns,1))
            else:m.append((sq,ns))
        if sq//8==(1 if s==0 else 7) and not b[sq+mp]and not b[sq+2*mp]:m.append((sq,sq+2*mp))
    #knights
    for sq in range(64):
        pc=b[sq]>>3;c=b[sq]&7
        if pc!=2 or c!=s:continue
        for kx,ky in [(1,2),(2,1),(-1,2),(-2,1),(1,-2),(2,-1),(-1,-2),(-2,1)]:
            ns=sq+8*ky+kx
            if 0<=ns<64:m.append((sq,ns))
    #sliders
    for sq in range(64):
        pc=b[sq]>>3;c=b[sq]&7
        if pc not in(3,4,5)or c!=s:continue
        for dx,dy in [(1,1),(1,-1),(-1,1),(-1,-1),(1,0),(-1,0),(0,1),(0,-1)]:
            ns=sq
            while True:
                ns+=8*dx+dy
                if not(0<=ns<64):break
                if b[ns]:
                    if b[ns]>>3!=c:m.append((sq,ns))
                    break
                else:m.append((sq,ns))
                break
    #king
    for sq in range(64):
        pc=b[sq]>>3;c=b[sq]&7
        if pc!=6 or c!=s:continue
        for kx,ky in [(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]:
            ns=sq+8*ky+kx
            if 0<=ns<64:m.append((sq,ns))
    #search
    if not m:return E(b,s)-100000
    for u in m:
        nb=b.copy();fr,to=u[0],u[1];nf=idx(*fr);nt=idx(*to);nb[nt]=nb[nf];nb[nf]=0
        if len(u)>2 and u[2]==1:nb[nt]=5|(nb[nt]&7)
        s_=-N(nb,s^1,d-1,-b_,b_)
        if s_>=b_:return b_
        if s_>a:a=s_
    return a
def run():
    url=os.environ.get('MAKEFUN_ENV_URL')
    if not url:sys.stderr.write('missing env\n');sys.exit(1)
    while True:
        r=urllib.request.Request(url+'/game',method='POST',headers={'Content-Type':'application/json'},data=b'{}')
        d=json.loads(urllib.request.urlopen(r,timeout=30).read().decode())
        if d.get('status','')=='done':sys.stderr.write('done\n');sys.exit(0)
        fen=d.get('fen','');leg=d.get('legal_moves',[])
        if not leg:continue
        b,s=p(fen)
        best=leg[0];best_s=-10**9
        for u in leg:
            try:
                fr,to=ord(u[0])-97+8*(int(u[1])-1),ord(u[2])-97+8*(int(u[3])-1)
                nf=idx(*((fr//8,fr%8)));nt=idx(*((to//8,to%8)))
                nb=b.copy();nb[nt]=nb[nf];nb[nf]=0
                s_=-N(nb,s^1,3,-10**9,10**9)
                if s_>best_s:best_s=s_;best=u
            except:pass
        uci=best
        r=urllib.request.Request(url+'/move',method='POST',headers={'Content-Type':'application/json'},data=json.dumps({'game':d['game'],'move':uci}).encode())
        R=json.loads(urllib.request.urlopen(r,timeout=30).read().decode())
        if R.get('status','')=='done':sys.stderr.write('done\n');sys.exit(0)
if __name__=='__main__':run()
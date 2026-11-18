import os,urllib.request,json,sys

def idx(r,c):return r*8+c
def rc(i):return(i//8,i%8)

def is_attacked(b,k,c):
    o=1-c
    kr,kc=rc(k)
    for i in range(64):
        p=b[i]
        if not p or(p>>3)!=o:continue
        pc=p&0xF;r,c=rc(i)
        if pc==1:
            for dr,dc in((-1,-1),(-1,1),(0,1),(0,-1),(1,-1),(1,1)):
                if r+dr==kr and c+dc==kc:return True
            for dr in((-1,0),(1,0)):
                for _ in range(2):
                    if r+dr[0]==kr and c+dr[1]==kc:return True
                    r+=dr[0];c+=dr[1]
        elif pc==2:
            for dr,dc in((-1,-1),(-1,1),(1,-1),(1,1)):
                if r+dr==kr and c+dc==kc:return True
        elif pc==3:
            for dr,dc in((-1,0),(1,0),(0,-1),(0,1)):
                if r+dr==kr and c+dc==kc:return True
        elif pc==4:
            for dr,dc in((-1,0),(1,0),(0,-1),(0,1)):
                if r+dr==kr and c+dc==kc:return True
        elif pc==5:
            for dr,dc in((-1,-1),(-1,1),(1,-1),(1,1)):
                if r+dr==kr and c+dc==kc:return True
        elif pc==6:
            for dr,dc in((0,1),(0,-1),(1,0),(-1,0)):
                if r+dr==kr and c+dc==kc:return True
    return False

def gen_moves(b,c):
    m=[]
    o=1-c
    for i in range(64):
        p=b[i]
        if not p or(p>>3)!=c:continue
        pc=p&0xF;r,c=rc(i)
        if pc==1:
            for dr,dc in((0,-2),(0,2)):
                nr,nc=r+dr,c+dc
                ti=idx(nr,nc)
                if 0<=nr<8 and 0<=nc<8 and not b[ti]:
                    m.append((i,ti,pc<<3,0))
            for dr,dc in((-1,-1),(-1,1),(1,-1),(1,1),(0,1),(0,-1)):
                nr,nc=r+dr,c+dc
                ti=idx(nr,nc)
                if 0<=nr<8 and 0<=nc<8 and(b[ti]>>3)==o:
                    m.append((i,ti,pc<<3,0))
        elif pc==2:
            for dr,dc in((-1,-1),(-1,1),(1,-1),(1,1)):
                for k in range(1,8):
                    nr,nc=r+dr*k,c+dc*k
                    ti=idx(nr,nc)
                    if not(0<=nr<8 and 0<=nc<8):break
                    if not b[ti]:m.append((i,ti,pc<<3,0))
                    else:
                        if(b[ti]>>3)==o:m.append((i,ti,pc<<3,0))
                        break
        elif pc==3:
            for dr,dc in((-1,0),(1,0),(0,-1),(0,1)):
                for k in range(1,8):
                    nr,nc=r+dr*k,c+dc*k
                    ti=idx(nr,nc)
                    if not(0<=nr<8 and 0<=nc<8):break
                    if not b[ti]:m.append((i,ti,pc<<3,0))
                    else:
                        if(b[ti]>>3)==o:m.append((i,ti,pc<<3,0))
                        break
        elif pc==4:
            for dr,dc in((-1,0),(1,0),(0,-1),(0,1)):
                for k in range(1,8):
                    nr,nc=r+dr*k,c+dc*k
                    ti=idx(nr,nc)
                    if not(0<=nr<8 and 0<=nc<8):break
                    if not b[ti]:m.append((i,ti,pc<<3,0))
                    else:
                        if(b[ti]>>3)==o:m.append((i,ti,pc<<3,0))
                        break
        elif pc==5:
            for dr,dc in((-1,-1),(-1,1),(1,-1),(1,1)):
                for k in range(1,8):
                    nr,nc=r+dr*k,c+dc*k
                    ti=idx(nr,nc)
                    if not(0<=nr<8 and 0<=nc<8):break
                    if not b[ti]:m.append((i,ti,pc<<3,0))
                    else:
                        if(b[ti]>>3)==o:m.append((i,ti,pc<<3,0))
                        break
        elif pc==6:
            for dr,dc in((0,1),(0,-1),(1,0),(-1,0)):
                nr,nc=r+dr,c+dc
                ti=idx(nr,nc)
                if 0<=nr<8 and 0<=nc<8 and(b[ti]>>3)==o:
                    m.append((i,ti,pc<<3,0))
            for dr,dc in((-1,0),(1,0)):
                nr,nc=r+dr,c+dc
                if nr==0 or nr==7:
                    for prom in range(1,6):
                        m.append((i,ti,prom<<3,0))
    return m

def make_move(b,move,c):
    i1,i2,prom=move>>12,move&0xFFF,(move>>20)&0xF
    r1,c1=rc(i1);r2,c2=rc(i2)
    piece=b[i1]
    b[i1]=0
    b[i2]=piece
    if piece&0xF==1 and abs(r2-r1)==2 and c1==c2:
        br=r1
        if r2==r1+2:b[rc_to_idx(br,c2+1)]=0x2<<3
        else:b[rc_to_idx(br,c2-1)]=0x2<<3
    if prom:b[i2]=prom<<3
    en=(move>>16)&0x3F
    if en:en=en<<3
    return en

def unmake_move(b,move,enp,c):
    i1,i2,prom=move>>12,move&0xFFF,(move>>20)&0xF
    r1,c1=rc(i1);r2,c2=rc(i2)
    piece=b[i2]
    b[i1]=piece
    b[i2]=0
    if piece&0xF==1 and abs(r2-r1)==2 and c1==c2:
        br=r1
        if r2==r1+2:b[rc_to_idx(br,c2+1)]=0x2<<3
        else:b[rc_to_idx(br,c2-1)]=0x2<<3
    if prom:b[i1]=prom<<3
    b[i2]=0

def rc_to_idx(r,c):return r*8+c

def legal_filter(b,moves,king,c):
    fl=[]
    for mv in moves:
        en=b[mv[3]&0xFFF]if mv[3]else0
        make_move(b,mv[0]<<12|mv[1],c)
        if not is_attacked(b,king,c):fl.append(mv)
        unmake_move(b,mv[0]<<12|mv[1],en,c)
    return fl

def evaluate(b,c):
    mg=0
    for i in range(64):
        p=b[i]
        if not p:continue
        pc=p&0xF
        mg+= {1:100,2:320,3:330,4:500,5:900}[pc]
        if pc==2:
            r,c=rc(i)
            mg+=(1 if r==1 else0)+(1 if r==6 else0)
    return mg

def negamax(b,d,a,bta,c,d0):
    if d==0:return evaluate(b,c)
    moves=gen_moves(b,c)
    best=-0x10000000
    for mv in moves:
        en=b[mv[3]&0xFFF]if mv[3]else0
        make_move(b,mv[0]<<12|mv[1],c)
        val=-negamax(b,d-1,-bta,-a,1-c,d0)
        unmake_move(b,mv[0]<<12|mv[1],en,c)
        if val>best:best=val;a=max(a,val)
        if a>=bta:break
    return best

def make_uci(mv):
    i1,i2,prom=mv[0],mv[1],mv[2]>>3
    r1,c1=rc(i1);r2,c2=rc(i2)
    return f"{chr(97+c1)}{r1+1}{chr(97+c2)}{r2+1}"+(f"{chr(97+prom-1)}"if prom else"")

def main():
    url=os.environ.get('MAKEFUN_ENV_URL')
    if not url:
        sys.stderr.write('Missing MAKEFUN_ENV_URL\n')
        sys.exit(1)
    game=None
    while True:
        req=urllib.request.Request(url+'/game',data=b'{}',headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req)as resp:
            data=json.loads(resp.read().decode())
        st=data.get('status')
        if st=='done':
            sys.stderr.write('done\n')
            sys.exit(0)
        if st=='your_move':
            board=data.get('board',[])
            legal=data.get('legal_moves',[])
            best=-0x10000000
            best_mv=None
            for ml in legal:
                moves=gen_moves(board,0)
                move=None
                for m in moves:
                    if make_uci(m)==ml:
                        move=m[0]<<12|m[1]|(m[2]<<20)
                        break
                if not move:continue
                en=board[ml[3]&0xFFF]if ml[3]else0
                make_move(board,move,0)
                val=-negamax(board,3,-0x10000000,0x10000000,1,3)
                unmake_move(board,move,en,0)
                if val>best:best=val;best_mv=ml
            if best_mv:
                urllib.request.urlopen(urllib.request.Request(
                    url+'/move',data=json.dumps({'game':game,'move':best_mv}).encode(),headers={'Content-Type':'application/json'}).read())
            else:break
        else:break
        game=data.get('game')

if __name__=='__main__':main()
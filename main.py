import os,urllib.request,json,sys

def idx(r,c):return r*8+c
def rc(i):return(i//8,i%8)

def pawn_moves(b,i,c):
    m=[]
    r,c_=rc(i)
    dr=c_==0 and 1 or -1
    for nr in(r+dr):
        ti=idx(nr,c_)
        if 0<=nr<8 and 0<=c_<8:
            if not b[ti]:m.append((i,ti,0,0))
            elif (b[i]>>3)!=c and b[ti]>>3==c:
                m.append((i,ti,1,0))
    if c_==4:
        ti=idx(r,0)
        if b[ti]==0:m.append((i,ti,1,0))
        ti=idx(r,7)
        if b[ti]==0:m.append((i,ti,1,0))
    return m

def knight_moves(b,i,c):
    m=[]
    r,c_=rc(i)
    for dr,dc in((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)):
        nr,nc=r+dr,c_+dc
        if 0<=nr<8 and 0<=nc<8:
            ti=idx(nr,nc)
            if not b[ti]:m.append((i,ti,0,0))
            elif (b[i]>>3)!=c:m.append((i,ti,1,0))
    return m

def bishop_moves(b,i,c):
    m=[]
    r,c_=rc(i)
    for dr,dc in((-1,-1),(-1,1),(1,-1),(1,1)):
        for step in range(1,8):
            nr,nc=r+dr*step,c_+dc*step
            if not 0<=nr<8 or not 0<=nc<8:break
            ti=idx(nr,nc)
            if b[ti]==0:m.append((i,ti,0,0))
            elif (b[i]>>3)!=c:m.append((i,ti,1,0))
            break
    return m

def rook_moves(b,i,c):
    m=[]
    r,c_=rc(i)
    for dr,dc in((-1,0),(1,0),(0,-1),(0,1)):
        for step in range(1,8):
            nr,nc=r+dr*step,c_+dc*step
            if not 0<=nr<8 or not 0<=nc<8:break
            ti=idx(nr,nc)
            if b[ti]==0:m.append((i,ti,0,0))
            elif (b[i]>>3)!=c:m.append((i,ti,1,0))
            break
    return m

def queen_moves(b,i,c):
    return bishop_moves(b,i,c)+rook_moves(b,i,c)

def king_moves(b,i,c):
    m=[]
    r,c_=rc(i)
    for dr,dc in((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)):
        nr,nc=r+dr,c_+dc
        if 0<=nr<8 and 0<=nc<8:
            ti=idx(nr,nc)
            if not b[ti]:m.append((i,ti,0,0))
            elif (b[i]>>3)!=c:m.append((i,ti,1,0))
    return m

def gen_moves(b,c):
    m=[]
    for i,p in enumerate(b):
        if p==0:continue
        if (p>>3)!=c:continue
        pc=p&0xF
        if pc==1:m+=pawn_moves(b,i,c)
        elif pc==2:m+=knight_moves(b,i,c)
        elif pc==3:m+=bishop_moves(b,i,c)
        elif pc==4:m+=rook_moves(b,i,c)
        elif pc==5:m+=queen_moves(b,i,c)
        elif pc==6:m+=king_moves(b,i,c)
    return m

def make_move(b,move):
    i,ti,capture,_=move
    b[ti],b[i]=b[i],0
    return capture

def unmake_move(b,i,ti,capture):
    b[i],b[ti]=b[ti],(b[i]>>3)^1 if b[i]>>3 else b[i]
    return b

def mg(pc):return 1+pc>2

def eval_board(b,c):
    sq=0
    for p in b:
        if p and (p>>3)==c:sq+=mg(p&0xF)
    return sq

def ab(b,pl,pr,depth,me,tt,delta):
    if depth<=0:return eval_board(b,me)
    best=-99999
    mn=99999
    for move in tt:
        capture=make_move(b,move)
        sc=-ab(b,pr-1,depth-1,me,-pl,tt[-1] if sc>delta else tt,delta)
        unmake_move(b,move[0],move[1],capture)
        if sc>best:
            best=sc
            if sc>delta:
                tt=tt[:]
                break
        if sc<mn:mn=sc
    return best

def to_uci(i,ti):
    fr=chr(97+rc(i)[1])+'12345678'[rc(i)[0]]
    to=chr(97+rc(ti)[1])+'12345678'[rc(ti)[0]]
    return fr+to

def run():
    url=os.environ.get('MAKEFUN_ENV_URL')
    if not url:return
    while True:
        req=urllib.request.Request(url+'/game',method='POST',headers={'Content-Type':'application/json'})
        data=json.loads(urllib.request.urlopen(req,timeout=30).read().decode())
        fen=data.get('fen','')
        legal=data.get('legal_moves',[])
        if not legal:
            if data.get('status','')=='done':
                sys.stderr.write('done\n')
                sys.exit(0)
            continue
        board=[0]*64
        ranks=fen.split()
        if len(ranks)<2:break
        sq=ranks[0]
        pos=0
        for ch in sq:
            if ch=='/':continue
            if ch.isdigit():
                for _ in range(int(ch)):board[pos]=0
                pos+=int(ch)-1
            else:
                pc=0
                c=1 if ch.isupper() else 0
                ch=ch.lower()
                if ch=='p':pc=1
                elif ch=='n':pc=2
                elif ch=='b':pc=3
                elif ch=='r':pc=4
                elif ch=='q':pc=5
                elif ch=='k':pc=6
                board[pos]=(pc<<3)|c
                pos+=1
        move=ab(board,c,c,3,c,gen_moves(board,c),-1)
        if not move:continue
        uci=to_uci(move[0],move[1])
        if uci not in legal:uci=legal[0]
        req=urllib.request.Request(url+'/move',method='POST',headers={'Content-Type':'application/json'},data=json.dumps({'game':data['game'],'move':uci}).encode())
        resp=json.loads(urllib.request.urlopen(req,timeout=30).read().decode())
        if resp.get('status','')=='done':
            sys.stderr.write('done\n')
            sys.exit(0)

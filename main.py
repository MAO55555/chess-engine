import os,urllib.request,json,sys

def idx(r,c):return r*8+c
def rc(i):return(i//8,i%8)

def parse_fen(fen):
    board=[0]*64
    ranks=fen.split()
    side=0
    if len(ranks)<2:
        return board,side
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
    return board,c

def uci_to_move(uci):
    fr=rc(ord(uci[0])-97+8*(int(uci[1])-1))
    to=rc(ord(uci[2])-97+8*(int(uci[3])-1))
    return fr,to

def run():
    url=os.environ.get('MAKEFUN_ENV_URL')
    if not url:
        sys.stderr.write('missing env\n')
        sys.exit(1)
    while True:
        req=urllib.request.Request(url+'/game',method='POST',headers={'Content-Type':'application/json'},data=b'{}')
        data=json.loads(urllib.request.urlopen(req,timeout=30).read().decode())
        status=data.get('status','')
        if status=='done':
            sys.stderr.write('done\n')
            sys.exit(0)
        fen=data.get('fen','')
        legal=data.get('legal_moves',[])
        if not legal:
            continue
        board,side=parse_fen(fen)
        uci=legal[0]
        fr,to=uci_to_move(uci)
        fi=idx(*fr)
        ti=idx(*to)
        board[ti]=board[fi]
        board[fi]=0
        req=urllib.request.Request(url+'/move',method='POST',headers={'Content-Type':'application/json'},data=json.dumps({'game':data['game'],'move':uci}).encode())
        resp=json.loads(urllib.request.urlopen(req,timeout=30).read().decode())
        if resp.get('status','')=='done':
            sys.stderr.write('done\n')
            sys.exit(0)
if __name__=='__main__':
    run()
"""The clickable demo page served by the router itself (same origin, no CORS)."""

PAGE = """<!doctype html><html lang=en><meta charset=utf-8>
<title>Control Tower — live demo</title>
<meta name=viewport content="width=device-width,initial-scale=1">
<style>
:root{--bg:#0d1117;--panel:#161b22;--line:#30363d;--fg:#c9d1d9;--dim:#8b949e;
--green:#3fb950;--red:#f85149;--yellow:#d29922;--blue:#58a6ff;--white:#f0f6fc}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.6 ui-monospace,"DejaVu Sans Mono",monospace}
header{padding:28px 32px;border-bottom:1px solid var(--line)}
h1{margin:0;font-size:30px;color:var(--white);letter-spacing:.5px}
.sub{color:var(--blue);margin-top:6px;font-size:16px}
.rule{margin-top:14px;color:var(--dim);font-size:14px}
.rule b{color:var(--green)}.rule i{color:var(--yellow);font-style:normal}
main{display:grid;grid-template-columns:390px 1fr;gap:0;min-height:calc(100vh - 132px)}
#steps{border-right:1px solid var(--line);padding:20px}
button{display:block;width:100%;text-align:left;margin-bottom:10px;padding:12px 14px;
background:var(--panel);color:var(--fg);border:1px solid var(--line);border-radius:8px;
font:inherit;cursor:pointer;transition:.12s}
button:hover{border-color:var(--blue);background:#1c2333}
button b{display:block;color:var(--white);margin-bottom:2px}
button span{color:var(--dim);font-size:13px}
#run{background:#1f6feb;border-color:#1f6feb;color:#fff;text-align:center;margin-bottom:18px}
#run b{color:#fff}
#out{padding:20px 26px;overflow:auto}
.card{border:1px solid var(--line);border-left-width:4px;border-radius:8px;
padding:14px 16px;margin-bottom:12px;background:var(--panel);white-space:pre-wrap;
word-break:break-word;font-size:14px}
.MATCH{border-left-color:var(--green)}.REFUSED{border-left-color:var(--red)}
.NO_MATCH{border-left-color:var(--yellow)}.INFO{border-left-color:var(--blue)}
.tag{font-weight:700;letter-spacing:.5px}
.MATCH .tag{color:var(--green)}.REFUSED .tag{color:var(--red)}
.NO_MATCH .tag{color:var(--yellow)}.INFO .tag{color:var(--blue)}
.meta{color:var(--dim);font-size:13px;margin-top:6px}
#score{position:sticky;top:0;background:var(--bg);padding-bottom:14px;
border-bottom:1px solid var(--line);margin-bottom:16px}
.nums{display:flex;gap:26px;flex-wrap:wrap;margin-top:8px}
.num{min-width:120px}
.num u{display:block;text-decoration:none;font-size:28px;color:var(--white)}
.num s{display:block;text-decoration:none;color:var(--dim);font-size:12px}
.g u{color:var(--green)}.y u{color:var(--yellow)}.r u{color:var(--red)}
</style>
<header>
<h1>CONTROL TOWER</h1>
<div class=sub>A deterministic front door for an agent fleet</div>
<div class=rule>Known capability &rarr; <b>circuit runs, zero model calls</b>
&nbsp;·&nbsp; No match &rarr; <i>Google Gemini decides</i></div>
</header>
<main>
<div id=steps>
<button id=run><b>&#9654; Run the whole flight</b></button>
<button data-k=read_carte><b>1 · read_carte</b><span>known capability</span></button>
<button data-k=create_task><b>2 · create_task</b><span>a write, unconfirmed</span></button>
<button data-k=create_task data-c=1><b>3 · create_task + confirm</b><span>a write, confirmed</span></button>
<button data-k=drop_database><b>4 · drop_database</b><span>on the deny list</span></button>
<button data-k=send_invoice_to_client data-a=1><b>5 · send_invoice_to_client</b><span>unknown &rarr; the model</span></button>
<button data-v=1><b>6 · verify(17)</b><span>independent oracle</span></button>
</div>
<div id=out>
<div id=score>
<div class=meta>MEASURED, NOT ASSERTED &nbsp;·&nbsp; GET /metrics</div>
<div class=nums>
<div class="num g"><u id=nDet>0</u><s>deterministic · 0 model calls</s></div>
<div class="num y"><u id=nLlm>0</u><s>model path</s></div>
<div class="num r"><u id=nRef>0</u><s>refused by guardrail</s></div>
<div class="num g"><u id=tDet>—</u><s>deterministic answer</s></div>
<div class="num y"><u id=tLlm>—</u><s>model answer</s></div>
<div class="num"><u id=ratio>—</u><s>speed difference</s></div>
</div></div>
<div id=log></div>
</div>
</main>
<script>
const log=document.getElementById('log');
function card(kind,title,body,meta){
  const d=document.createElement('div');d.className='card '+kind;
  d.innerHTML='<span class=tag>'+kind+'</span>  '+title+'\\n\\n'+body+
    (meta?'<div class=meta>'+meta+'</div>':'');
  log.prepend(d);
}
async function call(path,payload){
  const t0=performance.now();
  const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify(payload)});
  const j=await r.json();
  return [j,Math.round(performance.now()-t0)];
}
async function refresh(){
  const m=await (await fetch('/metrics')).json();
  nDet.textContent=m.deterministic;nLlm.textContent=m.llm;nRef.textContent=m.refused;
  const d=m.trace.filter(t=>t.route==='deterministic').map(t=>t.ms);
  const l=m.trace.filter(t=>t.route==='llm').map(t=>t.ms);
  if(d.length){tDet.textContent=Math.min(...d)+' ms';}
  if(l.length){tLlm.textContent=Math.max(...l)+' ms';}
  if(d.length&&l.length){ratio.textContent=Math.round(Math.max(...l)/Math.max(Math.min(...d),1))+'\\u00d7';}
}
async function step(name,args){
  const [j]=await call('/mcp/tour',{name:name,args:args||{}});
  const kind=j.decision||'INFO';
  card(kind,name,JSON.stringify(j,null,2),
       'model calls: '+(j.model_calls!==undefined?j.model_calls:'?')+
       (j.ms!==undefined?'   ·   '+j.ms+' ms':''));
  await refresh();
}
async function oracle(){
  const [j]=await call('/verify',{input:17});
  card('INFO','verify(17) — independent oracle',JSON.stringify(j,null,2),
       'model calls: 0');
  await refresh();
}
document.querySelectorAll('#steps button').forEach(b=>{
  if(b.id==='run')return;
  b.onclick=()=>{b.disabled=true;
    (b.dataset.v?oracle():step(b.dataset.k,
      b.dataset.c?{confirm:true}:(b.dataset.a?{client:'ACME'}:{})))
    .finally(()=>b.disabled=false);};
});
document.getElementById('run').onclick=async e=>{
  const b=e.currentTarget;b.disabled=true;log.innerHTML='';
  const wait=ms=>new Promise(r=>setTimeout(r,ms));
  await step('read_carte');            await wait(900);
  await step('create_task');           await wait(900);
  await step('create_task',{confirm:true}); await wait(900);
  await step('drop_database');         await wait(900);
  await step('send_invoice_to_client',{client:'ACME'}); await wait(900);
  await oracle();
  b.disabled=false;
};
refresh();
</script>
</html>"""

# -*- coding: utf-8 -*-
"""Genera index.html estatico con 2 tabs:
  - Proveedores: tabla de resultados de Alibaba (con foto ampliable)
  - Keywords: keywords descubiertos en Amazon (keyword + mecanismo)
Abrir via dev server: python -m http.server 8000  ->  localhost:8000/index.html
"""
import csv, json, re

SUPPLIERS_CSV = "reporte_sourcing_alibaba.csv"
KEYWORDS_CSV = "keywords_amazon.csv"
OUT = "index.html"
try:
    import amz_keywords
    SEED = amz_keywords.SEED
except Exception:
    SEED = "squishy toys"

FICHAS = {
 1601740234896: {"resp": "<=2h", "ontime": ">=93%"}, 1601799533956: {"resp": "<=1h", "ontime": ">=99%"},
 1601716075635: {"resp": "<=3h", "ontime": ">=99%"}, 1601295293535: {"resp": "<=4h", "ontime": ">=93%"},
 1601424414588: {"resp": "<=2h", "ontime": ">=99%"}, 1601023310453: {"resp": "<=3h", "ontime": ">=98%"},
 1601758712138: {"resp": "<=4h", "ontime": ">=90%"}, 1601765195031: {"resp": "<=3h", "ontime": ">=91%"},
 1601718581780: {"resp": "<=3h", "ontime": ">=91%"}, 1600238919442: {"resp": "<=2h", "ontime": ">=96%"},
}

def num(s, d=0):
    m = re.search(r"[\d.]+", str(s).replace(",", "")); return float(m.group()) if m else d

def pid(url):
    m = re.search(r"_(\d+)\.html", url); return int(m.group(1)) if m else None

# --- Proveedores ---
suppliers, seen = [], set()
with open(SUPPLIERS_CSV, encoding="utf-8-sig", newline="") as f:
    for r in csv.DictReader(f):
        u = r.get("url", "").strip()
        if not u or u in seen: continue
        seen.add(u); fi = FICHAS.get(pid(u), {})
        suppliers.append({
            "url": u, "img": r.get("image", ""), "title": r.get("title", ""),
            "company": r.get("company", ""), "country": r.get("country", ""),
            "years": int(num(r.get("years"))), "rating": num(r.get("rating")),
            "reviews": int(num(r.get("reviews"))), "service": num(r.get("service")),
            "price": r.get("price", ""), "priceMin": num(r.get("price"), 1e9),
            "moq": r.get("moq", "").replace("Min. order:", "").strip(),
            "resp": fi.get("resp", ""), "ontime": fi.get("ontime", ""),
        })
suppliers.sort(key=lambda x: (-x["reviews"], -x["years"]))

# --- Keywords (datos crudos; el "mecanismo" se arma en JS) ---
keywords = []
try:
    with open(KEYWORDS_CSV, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            keywords.append({"kw": r.get("keyword", ""),
                             "a": int(num(r.get("autocomplete"))),
                             "t": int(num(r.get("titulo"))),
                             "score": int(num(r.get("score")))})
    keywords.sort(key=lambda x: -x["score"])
except FileNotFoundError:
    keywords = []

# --- Candidatos Alibaba (Fase 1 del bridge) ---
try:
    import amz_bridge
    candidatos = amz_bridge.generar_candidatos(keywords)
except Exception:
    candidatos = []

payload_s = json.dumps(suppliers, ensure_ascii=False)
payload_k = json.dumps(keywords, ensure_ascii=False)
payload_c = json.dumps(candidatos, ensure_ascii=False)

HTML = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sourcing Squishy - Alibaba + Amazon</title>
<style>
  :root{--b:#1F4E78;}
  *{box-sizing:border-box;} body{font-family:system-ui,Segoe UI,Arial;margin:0;background:#f4f6f9;color:#222;}
  header{background:var(--b);color:#fff;padding:14px 20px;}
  header h1{margin:0;font-size:19px;} header p{margin:3px 0 0;opacity:.85;font-size:12.5px;}
  .tabs{display:flex;gap:4px;background:#153a5c;padding:0 16px;}
  .tab{padding:11px 20px;color:#cdd8e6;cursor:pointer;font-size:14px;font-weight:600;border-bottom:3px solid transparent;}
  .tab:hover{color:#fff;} .tab.active{color:#fff;border-bottom-color:#ffd24a;background:#1f4e78;}
  .panel{display:none;} .panel.active{display:block;}
  .bar{background:#fff;border-bottom:1px solid #e2e6ea;padding:10px 20px;display:flex;gap:14px;flex-wrap:wrap;align-items:center;}
  .bar label{font-size:13px;color:#555;} .bar input{padding:7px 9px;border:1px solid #cbd2d9;border-radius:8px;font-size:13px;}
  .bar button{padding:7px 16px;background:var(--b);color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:13px;font-weight:600;}
  .bar button:disabled{opacity:.55;cursor:default;}
  .seedbox{font-size:13px;color:#333;} .seedbox b{color:var(--b);}
  .count{margin-left:auto;font-size:13px;color:#666;}
  .wrap{padding:14px 20px;overflow-x:auto;}
  table{border-collapse:collapse;width:100%;background:#fff;font-size:13px;box-shadow:0 1px 3px rgba(0,0,0,.06);}
  th,td{border:1px solid #e6e9ed;padding:7px 9px;text-align:left;white-space:nowrap;}
  thead th{position:sticky;top:0;background:var(--b);color:#fff;cursor:pointer;user-select:none;font-weight:600;z-index:4;box-shadow:0 2px 0 var(--b);}
  thead th:hover{background:#2a5f92;} th .arrow{opacity:.6;font-size:10px;margin-left:3px;}
  tbody tr:nth-child(even){background:#f7f9fb;} tbody tr:hover{background:#eef4ff;}
  td.prod{white-space:normal;max-width:280px;} td.company{color:#3a6bd6;}
  td.price{font-weight:700;color:#1a7a3c;} .num{text-align:right;}
  td.ficha{background:#eef4ff;font-weight:600;}
  td.foto{padding:3px;} td.foto img{width:62px;height:62px;object-fit:cover;border-radius:6px;background:#eef1f4;cursor:pointer;}
  td.foto img:hover{outline:2px solid var(--b);}
  a.lnk{color:#1F4E78;text-decoration:none;} a.lnk:hover{text-decoration:underline;}
  /* keywords */
  td.kw{font-weight:600;font-size:13.5px;white-space:normal;max-width:320px;cursor:pointer;color:#146eb4;}
  #bodyK tr:hover td.kw{text-decoration:underline;}
  td.cand{font-weight:600;font-size:13.5px;white-space:normal;max-width:280px;cursor:pointer;color:#e07000;}
  #bodyC tr:hover td.cand{text-decoration:underline;}
  td.mec, td.deriv{white-space:normal;color:#555;font-size:12px;}
  .badge{font-size:11px;padding:2px 8px;border-radius:20px;}
  .badge.variante{background:#e7f6ec;color:#1a7a3c;} .badge.adyacente{background:#fff3cd;color:#8a6d00;}
  .badge.generico{background:#eef2f7;color:#556;}
  td.mec{white-space:normal;color:#444;font-size:12.5px;}
  .rank{color:#888;text-align:right;width:36px;}
  #preview{position:fixed;pointer-events:none;z-index:999;display:none;}
  #preview img{width:340px;height:340px;object-fit:contain;background:#fff;border:1px solid #ccc;border-radius:10px;box-shadow:0 10px 34px rgba(0,0,0,.32);padding:4px;}
</style></head>
<body>
<header><h1>Sourcing Squishy &mdash; Alibaba + Amazon</h1>
<p>Proveedores filtrados de Alibaba &middot; Keywords descubiertos en Amazon</p></header>

<div class="tabs">
  <div class="tab active" data-p="keywords">Productos AMZ</div>
  <div class="tab" data-p="candidatos">Candidatos</div>
  <div class="tab" data-p="suppliers">Proveedores</div>
</div>

<!-- PANEL PROVEEDORES -->
<div class="panel" id="p-suppliers">
  <div class="bar">
    <label>Buscar: <input id="q" placeholder="proveedor o producto..."></label>
    <label><input type="checkbox" id="onlyFicha"> Solo con datos de ficha</label>
    <span class="count" id="countS"></span>
  </div>
  <div class="wrap"><table><thead><tr id="headS"></tr></thead><tbody id="bodyS"></tbody></table></div>
</div>

<!-- PANEL PRODUCTOS AMZ (keywords) -->
<div class="panel active" id="p-keywords">
  <div class="bar">
    <label>Semilla: <input id="seed" value="__SEED__" placeholder="ej. squishy toys" size="22"></label>
    <button id="btnSearch">Buscar</button>
    <button id="btnForce" title="Recalcular ignorando cache (gasta creditos)">&#8635;</button>
    <span class="seedbox" id="statusK"></span>
    <label>Filtrar: <input id="qk" placeholder="filtrar keyword..."></label>
    <span class="count" id="countK"></span>
  </div>
  <div class="wrap"><table>
    <thead><tr><th class="rank">#</th><th>Keyword</th><th class="num">Score</th><th>Mecanismo (c&oacute;mo se determin&oacute;)</th></tr></thead>
    <tbody id="bodyK"></tbody>
  </table></div>
</div>

<!-- PANEL CANDIDATOS (bridge Amazon -> Alibaba, Fase 1) -->
<div class="panel" id="p-candidatos">
  <div class="bar">
    <span class="seedbox">Candidatos de b&uacute;squeda para <b>Alibaba</b>, derivados de los t&eacute;rminos de Amazon (sin modificadores + t&eacute;rminos de f&aacute;brica). <i>Score = demanda agregada.</i></span>
    <label>Filtrar: <input id="qc" placeholder="filtrar candidato..."></label>
    <span class="count" id="countC"></span>
  </div>
  <div class="wrap"><table>
    <thead><tr><th class="rank">#</th><th>Candidato (Amazon)</th><th>Traducci&oacute;n Alibaba</th><th class="num">Score</th><th>Tipo</th><th>Derivado de</th></tr></thead>
    <tbody id="bodyC"></tbody>
  </table></div>
</div>

<div id="preview"><img alt=""></div>
<script>
const SUPPLIERS=__SUPPLIERS__; let KEYWORDS=__KEYWORDS__; let CANDIDATOS=__CANDIDATOS__;

// ---- tabs ----
document.querySelectorAll('.tab').forEach(t=>t.addEventListener('click',()=>{
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(x=>x.classList.remove('active'));
  t.classList.add('active'); document.getElementById('p-'+t.dataset.p).classList.add('active');
}));

// ---- proveedores ----
const COLS=[["idx","#","idx"],["company","Proveedor","text"],["title","Producto","prod"],
 ["country","Pais","text"],["rating","Rating","num"],["reviews","Reviews","num"],
 ["years","Anios","num"],["service","Service","num"],["priceMin","Precio USD","price"],
 ["moq","MOQ","text"],["resp","Response","ficha"],["ontime","On-time","ficha"],["img","Foto","foto"]];
let sortKey="reviews", sortDir=-1;
const headS=document.getElementById('headS'), bodyS=document.getElementById('bodyS'), countS=document.getElementById('countS');
const q=document.getElementById('q'), onlyF=document.getElementById('onlyFicha');
headS.innerHTML=COLS.map(c=>`<th data-k="${c[0]}">${c[1]}<span class="arrow"></span></th>`).join('');
headS.querySelectorAll('th').forEach(th=>th.addEventListener('click',()=>{
  const k=th.dataset.k; if(k==='img')return;
  if(sortKey===k) sortDir*=-1; else {sortKey=k; sortDir=(k==='priceMin')?1:-1;} renderS();
}));
function cell(r,c){const [k,,t]=c;
  if(t==='foto') return `<td class="foto"><a href="${r.url}" target="_blank" rel="noopener"><img loading="lazy" src="${r.img||''}" onerror="this.style.opacity=.25"></a></td>`;
  if(t==='prod') return `<td class="prod"><a class="lnk" href="${r.url}" target="_blank" rel="noopener">${r.title||''}</a></td>`;
  if(t==='price') return `<td class="price num">$${r.price||'-'}</td>`;
  if(t==='company') return `<td class="company">${r.company||''}</td>`;
  if(t==='ficha') return `<td class="${r[k]?'ficha':''}">${r[k]||''}</td>`;
  if(t==='num') return `<td class="num">${r[k]}</td>`;
  if(t==='idx') return `<td class="num">${r._i}</td>`;
  return `<td>${r[k]||''}</td>`;}
function renderS(){
  let rows=SUPPLIERS.slice(); const term=q.value.toLowerCase().trim();
  if(term) rows=rows.filter(r=>(r.company+' '+r.title).toLowerCase().includes(term));
  if(onlyF.checked) rows=rows.filter(r=>r.resp);
  rows.sort((a,b)=>{let x=a[sortKey],y=b[sortKey];
    if(typeof x==='string'){x=x.toLowerCase();y=(y||'').toLowerCase();return x<y?-sortDir:x>y?sortDir:0;}
    return (x-y)*sortDir;});
  rows.forEach((r,i)=>r._i=i+1);
  bodyS.innerHTML=rows.map(r=>'<tr>'+COLS.map(c=>cell(r,c)).join('')+'</tr>').join('');
  countS.textContent=rows.length+' proveedores';
  headS.querySelectorAll('th').forEach(th=>{th.querySelector('.arrow').textContent=th.dataset.k===sortKey?(sortDir<0?'▼':'▲'):'';});
}
[q,onlyF].forEach(el=>el.addEventListener('input',renderS));

// ---- keywords ----
const bodyK=document.getElementById('bodyK'), countK=document.getElementById('countK'), qk=document.getElementById('qk');
const seedInput=document.getElementById('seed'), btn=document.getElementById('btnSearch'), statusK=document.getElementById('statusK');
function mecanismo(a,t){
  const p=[];
  if(a) p.push(`Autocomplete de Amazon &mdash; aparece en ${a} sugerencia${a>1?'s':''} (recursivo, 2 niveles)`);
  if(t) p.push(`N-grama de títulos &mdash; se repite en ${t} título${t>1?'s':''} de resultados`);
  return p.join(' &nbsp;·&nbsp; ')||'&mdash;';
}
function renderK(){
  let rows=KEYWORDS.slice(); const term=qk.value.toLowerCase().trim();
  if(term) rows=rows.filter(r=>r.kw.toLowerCase().includes(term));
  bodyK.innerHTML=rows.map((r,i)=>`<tr data-kw="${r.kw.replace(/"/g,'&quot;')}"><td class="rank">${i+1}</td><td class="kw" title="Doble clic: ver en Amazon">${r.kw}</td><td class="num">${r.score}</td><td class="mec">${mecanismo(r.a,r.t)}</td></tr>`).join('');
  countK.textContent=rows.length+' keywords';
}
qk.addEventListener('input',renderK);
// doble clic en la keyword -> busqueda en Amazon
bodyK.addEventListener('dblclick',e=>{
  const tr=e.target.closest('tr[data-kw]'); if(!tr)return;
  window.open('https://www.amazon.com/s?k='+encodeURIComponent(tr.dataset.kw),'_blank','noopener');
});
// buscar: recalcula la tabla en vivo (necesita app.py / Flask)
const btnForce=document.getElementById('btnForce');
async function buscar(force){
  const seed=seedInput.value.trim(); if(!seed)return;
  statusK.textContent=force?'Recalculando (gasta créditos)...':'Buscando...'; btn.disabled=true; btnForce.disabled=true;
  try{
    const res=await fetch('/api/keywords?seed='+encodeURIComponent(seed)+(force?'&force=1':''));
    if(!res.ok) throw new Error('HTTP '+res.status);
    const data=await res.json();
    if(data.error) throw new Error(data.error);
    KEYWORDS=data.keywords.map(k=>({kw:k.keyword,a:k.autocomplete,t:k.titulo,score:k.score}));
    CANDIDATOS=data.candidatos||[];
    const fuente = data.cached ? '📁 desde caché (0 créditos)' : '🌐 nuevo (gastó créditos)';
    statusK.textContent=KEYWORDS.length+' keywords para "'+data.seed+'" · '+fuente;
    qk.value=''; qc.value=''; renderK(); renderC();
  }catch(e){
    statusK.textContent='Error: '+e.message+' (¿corriste "python app.py"?)';
  }finally{ btn.disabled=false; btnForce.disabled=false; }
}
btn.addEventListener('click',()=>buscar(false));
btnForce.addEventListener('click',()=>buscar(true));
seedInput.addEventListener('keydown',e=>{ if(e.key==='Enter') buscar(false); });

// ---- candidatos (bridge fase 1) ----
const bodyC=document.getElementById('bodyC'), countC=document.getElementById('countC'), qc=document.getElementById('qc');
function renderC(){
  let rows=CANDIDATOS.slice(); const term=qc.value.toLowerCase().trim();
  if(term) rows=rows.filter(r=>(r.candidato+' '+(r.traduccion||'')).toLowerCase().includes(term));
  bodyC.innerHTML=rows.map((r,i)=>{
    const deriv = r.ejemplos&&r.ejemplos.length ? r.ejemplos.join(', ') : ('<i>'+(r.origen||'')+'</i>');
    const trad = r.traduccion||r.candidato;
    return `<tr data-cand="${trad.replace(/"/g,'&quot;')}"><td class="rank">${i+1}</td>`+
      `<td>${r.candidato}</td>`+
      `<td class="cand" title="Doble clic: buscar en Alibaba">${trad}</td>`+
      `<td class="num">${r.score}</td>`+
      `<td><span class="badge ${r.tipo}">${r.tipo}</span></td>`+
      `<td class="deriv">${deriv}</td></tr>`;
  }).join('');
  countC.textContent=rows.length+' candidatos';
}
qc.addEventListener('input',renderC);
bodyC.addEventListener('dblclick',e=>{
  const tr=e.target.closest('tr[data-cand]'); if(!tr)return;
  window.open('https://www.alibaba.com/trade/search?SearchText='+encodeURIComponent(tr.dataset.cand),'_blank','noopener');
});

// ---- preview de foto ----
const prev=document.getElementById('preview'), prevImg=prev.querySelector('img'); const SZ=352;
bodyS.addEventListener('mouseover',e=>{const img=e.target.closest('td.foto img'); if(!img||!img.src)return; prevImg.src=img.src; prev.style.display='block'; place(e);});
bodyS.addEventListener('mousemove',e=>{ if(prev.style.display==='block') place(e); });
bodyS.addEventListener('mouseout',e=>{ if(e.target.closest('td.foto img')) prev.style.display='none'; });
function place(e){let x=e.clientX-SZ-18; if(x<8)x=e.clientX+18; let y=Math.min(Math.max(e.clientY-SZ/2,8),innerHeight-SZ-8); prev.style.left=x+'px'; prev.style.top=y+'px';}

renderS(); renderK(); renderC();
</script></body></html>"""

html = (HTML.replace("__SUPPLIERS__", payload_s)
            .replace("__KEYWORDS__", payload_k)
            .replace("__CANDIDATOS__", payload_c)
            .replace("__SEED__", SEED))
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print(f"OK -> {OUT}  ({len(suppliers)} proveedores, {len(keywords)} keywords)")

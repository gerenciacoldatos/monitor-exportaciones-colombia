import json, pickle, unicodedata, re
import pandas as pd, numpy as np
# Rutas: carpeta de trabajo con cons.pkl (consulta de exportaciones leída con pandas, una hoja por clave)
# y la carpeta npm con @svg-maps/colombia, world-atlas e i18n-iso-countries descomprimidos.
import os
S = os.environ.get('CED_TRABAJO', './')
N = os.environ.get('CED_NPM', S + 'npmchk/')
d = pickle.load(open(S + 'cons.pkl', 'rb'))
M = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
months = [(y, m) for y in range(2023, 2027) for m in range(1, 13) if not (y == 2026 and m > 8)]
idx = {ym: i for i, ym in enumerate(months)}
T = len(months)

def cube(df, col, fill='Sin dato'):
    df = df.copy(); df['m'] = df.Mes.map(M.index) + 1
    df[col] = df[col].fillna(fill).astype(str)
    df['i'] = [idx[(y, m)] for y, m in zip(df.Año, df.m)]
    out = {}
    for c, g in df.groupby(col):
        v = np.zeros(T); k = np.zeros(T)
        np.add.at(v, g.i.values, g.VALOR_FOB_USD.values / 1e6)
        np.add.at(k, g.i.values, g.PESO_NETO_KGS.values / 1e6)  # miles de toneladas
        out[c] = [[round(x, 3) for x in v], [round(x, 2) for x in k]]
    # sort by 2023-2026 total value
    return dict(sorted(out.items(), key=lambda kv: -sum(kv[1][0])))

pm = d['Por_Mes_Año'].copy(); pm['m'] = pm.Mes.map(M.index) + 1
tv = np.zeros(T); tk = np.zeros(T)
for _, r in pm.iterrows():
    tv[idx[(r.Año, r.m)]] = r.VALOR_FOB_USD / 1e6; tk[idx[(r.Año, r.m)]] = r.PESO_NETO_KGS / 1e6
D = {'months': [f'{y}-{m:02d}' for y, m in months],
     'total': [[round(x, 3) for x in tv], [round(x, 2) for x in tk]]}
D['tipo'] = cube(d['Por_Tipo'], 'Minero_No_Minero')
D['grupo'] = cube(d['Por_Grupo_Productos'], 'Grupo_Productos')
D['tec'] = cube(d['Por_Tecnologia'], 'Tecnologia')
D['modo'] = cube(d['Por_Modo_Transporte'], 'MODO_TRANSPORTE')
D['depto'] = cube(d['Por_Departamento'], 'REGION_DE_ORIGEN')
D['pais'] = cube(d['Por_Pais'], 'PAIS_DESTINO_FINAL', fill='País no declarado')

# Productos: capítulo arancelario (2 dígitos) y subpartidas principales
x = d['Por_Descripcion'].copy()
x['sp'] = x.SUBPARTIDA.astype(str).str.zfill(10)
x['cap'] = x.sp.str[:2]
CAP = {'01':'Animales vivos','02':'Carne','03':'Pescados y crustáceos','04':'Lácteos, huevos y miel','05':'Otros productos de origen animal','06':'Plantas vivas y flores','07':'Hortalizas','08':'Frutas','09':'Café, té y especias','10':'Cereales','11':'Productos de molinería','12':'Semillas y frutos oleaginosos','13':'Gomas y resinas vegetales','14':'Materias trenzables','15':'Grasas y aceites','16':'Preparaciones de carne o pescado','17':'Azúcares y confitería','18':'Cacao y sus preparaciones','19':'Preparaciones de cereales','20':'Preparaciones de hortalizas y frutas','21':'Preparaciones alimenticias diversas','22':'Bebidas y alcohol','23':'Residuos de la industria alimentaria','24':'Tabaco','25':'Sal, azufre, tierras, cemento','26':'Minerales metalíferos','27':'Combustibles minerales y petróleo','28':'Químicos inorgánicos','29':'Químicos orgánicos','30':'Productos farmacéuticos','31':'Abonos','32':'Tintas, pinturas y colorantes','33':'Aceites esenciales y cosméticos','34':'Jabones y detergentes','35':'Materias albuminoideas y colas','36':'Pólvoras y explosivos','37':'Productos fotográficos','38':'Productos químicos diversos','39':'Plásticos','40':'Caucho','41':'Pieles y cueros','42':'Manufacturas de cuero','43':'Peletería','44':'Madera','45':'Corcho','46':'Cestería','47':'Pasta de madera','48':'Papel y cartón','49':'Productos editoriales','50':'Seda','51':'Lana','52':'Algodón','53':'Otras fibras vegetales','54':'Filamentos sintéticos','55':'Fibras sintéticas discontinuas','56':'Guata y cordelería','57':'Alfombras','58':'Tejidos especiales','59':'Tejidos técnicos','60':'Tejidos de punto','61':'Prendas de punto','62':'Prendas excepto de punto','63':'Otros artículos textiles','64':'Calzado','65':'Sombreros','66':'Paraguas','67':'Plumas y flores artificiales','68':'Manufacturas de piedra y cemento','69':'Productos cerámicos','70':'Vidrio','71':'Oro, piedras y metales preciosos','72':'Fundición, hierro y acero','73':'Manufacturas de hierro o acero','74':'Cobre','75':'Níquel','76':'Aluminio','78':'Plomo','79':'Cinc','80':'Estaño','81':'Otros metales comunes','82':'Herramientas','83':'Manufacturas de metal común','84':'Máquinas y aparatos mecánicos','85':'Máquinas y aparatos eléctricos','86':'Material ferroviario','87':'Vehículos','88':'Aeronaves','89':'Barcos','90':'Instrumentos de óptica y medicina','91':'Relojería','92':'Instrumentos musicales','93':'Armas y municiones','94':'Muebles y colchones','95':'Juguetes y artículos deportivos','96':'Manufacturas diversas','97':'Objetos de arte','98':'Mercancías especiales','99':'Otros'}
x['capn'] = x.cap.map(lambda c: f'{c} · ' + CAP.get(c, 'Capítulo ' + c))
D['capitulo'] = cube(x.rename(columns={'capn': 'C'}), 'C')
tot = x[x.Año >= 2025].groupby('sp').VALOR_FOB_USD.sum().sort_values(ascending=False)
top = list(tot.index[:250])
desc = x.drop_duplicates('sp').set_index('sp').Descripcion_Arancelaria
def short(s):
    s = re.sub(r'\s+', ' ', str(s)).strip().rstrip('.')
    return s[:95] + ('…' if len(s) > 95 else '')
x['P'] = np.where(x.sp.isin(top), x.sp + ' · ' + x.sp.map(desc).map(short), 'Resto de subpartidas')
D['producto'] = cube(x, 'P')

# Empresas (top 10 por tipo y mes en la fuente)
e = d['TOP_Empresas'].dropna(subset=['Minero_No_Minero']).copy()
e['m'] = e.Mes.map(M.index) + 1
def norm_emp(s):
    s = re.sub(r'\s+', ' ', str(s)).strip()
    s = s.replace('ECOPETROL S.A.', 'ECOPETROL S A').replace('C.I. TRAFIGURA PETROLEUM COLOMBIA S.A.S.', 'C.I TRAFIGURA PETROLEUM COLOMBIA SAS')
    return s
e['E'] = e.RAZON_SOCIAL_EXPORTADOR.map(norm_emp)
emp = {}
for (c, t), g in e.groupby(['E', 'Minero_No_Minero']):
    v = [None] * T
    for _, r in g.iterrows(): v[idx[(r.Año, r.m)]] = round(r.VALOR_FOB_USD / 1e6, 3)
    emp[c] = {'t': 'M' if t.startswith('Minero') else 'N', 'v': v}
D['empresas'] = emp

# IHH
def ihh(sh):
    t = d[sh]; out = {}
    for _, r in t.iterrows(): out.setdefault(r.REGION_DE_ORIGEN, {})[int(r.Año)] = [round(r.IHH, 4), r.Clasificacion]
    return out
D['ihh_prod'] = ihh('IHH_Subpartidas'); D['ihh_pais'] = ihh('IHH_Paises')

# ---------- Mapas
# Colombia SVG -> nombres de la base
js = open(N + 'package/index.js').read()
cm = json.loads(js[js.index('{'):js.rindex('}') + 1])
fix = {'Bogotá': 'Bogotá D.C.', 'Guaviar': 'Guaviare', 'North Santander': 'Norte de Santander', 'San Andrés y Providencia': 'Archipiélago de San Andrés'}
paths = ''.join(f'<path name="{fix.get(l["name"], l["name"])}" d="{l["path"]}"/>' for l in cm['locations'])
D['col_svg'] = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{cm["viewBox"]}">{paths}</svg>'
assert all(fix.get(l['name'], l['name']) in D['depto'] for l in cm['locations']), [l['name'] for l in cm['locations'] if fix.get(l['name'], l['name']) not in D['depto']]

# Mundo: topojson -> geojson con nombres en español de la base
topo = json.load(open(N + 'wa/package/countries-110m.json'))
sc, tr = topo['transform']['scale'], topo['transform']['translate']
arcs = []
for a in topo['arcs']:
    xx = yy = 0; pts = []
    for p in a:
        xx += p[0]; yy += p[1]; pts.append([round(xx * sc[0] + tr[0], 2), round(yy * sc[1] + tr[1], 2)])
    arcs.append(pts)
def ring(ix):
    pts = []
    for i in ix:
        a = arcs[i] if i >= 0 else arcs[~i][::-1]
        pts += a if not pts else a[1:]
    return pts
def nrm(s): return ''.join(ch for ch in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(ch) != 'Mn').strip()
es = json.load(open(N + 'i18n/package/langs/es.json'))['countries']
codes = json.load(open(N + 'i18n/package/codes.json'))
a2num = {c[0]: c[2] for c in codes}
lut = {}
for a2, names in es.items():
    for nm in (names if isinstance(names, list) else [names]): lut[nrm(nm)] = a2
extra = {'Bangladés': 'BD', 'Baréin': 'BH', 'Belarús': 'BY', 'Corea del Sur': 'KR', 'Curazao': 'CW', 'Fiyi': 'FJ', 'Irak': 'IQ', 'Qatar': 'QA',
         'República Democrática del Congo': 'CD', 'San Cristóbal y Nieves': 'KN', 'Siria': 'SY', 'Surinam': 'SR', 'Guinea-Bisáu': 'GW', 'Botsuana': 'BW', 'Brunéi': 'BN', 'Laos': 'LA'}
num2base = {}
for p in D['pais']:
    a2 = extra.get(p) or lut.get(nrm(p))
    if a2: num2base[a2num[a2]] = p
feats = []
for g in topo['objects']['countries']['geometries']:
    if g.get('type') is None: continue
    nm = num2base.get(g.get('id'), g['properties']['name'])
    if g['type'] == 'Polygon': coords = [[ring(r) for r in g['arcs']]]; typ = 'MultiPolygon'
    else: coords = [[ring(r) for r in poly] for poly in g['arcs']]; typ = 'MultiPolygon'
    if g['properties']['name'] == 'Antarctica': continue
    feats.append({'type': 'Feature', 'properties': {'name': nm}, 'geometry': {'type': typ, 'coordinates': coords}})
D['world'] = {'type': 'FeatureCollection', 'features': feats}
matched = sum(1 for p in D['pais'] if p in {f['properties']['name'] for f in feats})
print('paises en mapa', matched, 'de', len(D['pais']))
s = json.dumps(D, ensure_ascii=False, separators=(',', ':'))
open(S + 'work/dashdata.json', 'w').write(s)
print(len(s) / 1e6, 'MB', {k: len(v) for k, v in D.items() if isinstance(v, dict)})

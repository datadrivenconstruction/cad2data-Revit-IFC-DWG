"""Standalone three.js viewer page (three.js r128, MIT, from cdnjs). GLB is embedded as base64."""
from __future__ import annotations
import base64
import html

THREE_URL = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"

_JS = r"""
const b64=document.getElementById('glb').textContent.trim();
const bin=Uint8Array.from(atob(b64),c=>c.charCodeAt(0)).buffer;
const dv=new DataView(bin);
const jl=dv.getUint32(12,true);
const J=JSON.parse(new TextDecoder().decode(new Uint8Array(bin,20,jl)));
const bo=20+jl+8;
const CT={5126:Float32Array,5125:Uint32Array,5123:Uint16Array};
const NC={SCALAR:1,VEC3:3};
function acc(i){const a=J.accessors[i],v=J.bufferViews[a.bufferView];
 const T=CT[a.componentType];return new T(bin.slice(bo+(v.byteOffset||0),bo+(v.byteOffset||0)+a.count*NC[a.type]*T.BYTES_PER_ELEMENT));}
const sc=new THREE.Scene();sc.background=new THREE.Color(0xf4f4f2);
const cam=new THREE.PerspectiveCamera(45,1,0.01,5000);
const rd=new THREE.WebGLRenderer({antialias:true});document.getElementById('v').appendChild(rd.domElement);
sc.add(new THREE.HemisphereLight(0xffffff,0x888888,0.9));
const dl=new THREE.DirectionalLight(0xffffff,0.6);dl.position.set(1,2,1.5);sc.add(dl);
const grp=new THREE.Group();sc.add(grp);const byName={};
J.nodes.forEach(n=>{const p=J.meshes[n.mesh].primitives[0];
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(acc(p.attributes.POSITION),3));
 g.setIndex(new THREE.BufferAttribute(acc(p.indices),1));g.computeVertexNormals();
 const c=J.materials[p.material].pbrMetallicRoughness.baseColorFactor;
 const m=new THREE.MeshStandardMaterial({color:new THREE.Color(c[0],c[1],c[2]),transparent:c[3]<1,opacity:c[3],side:THREE.DoubleSide,depthWrite:c[3]>=1});
 const me=new THREE.Mesh(g,m);me.name=n.name;grp.add(me);byName[n.name]=me;});
const box=new THREE.Box3().setFromObject(grp),ctr=new THREE.Vector3(),sz=new THREE.Vector3();box.getCenter(ctr);box.getSize(sz);
const R=Math.max(sz.x,sz.y,sz.z,1)*1.2;let th=0.8,ph=1.0,rad=R*1.6,tgt=ctr.clone();
function upd(){cam.position.set(tgt.x+rad*Math.sin(ph)*Math.cos(th),tgt.y+rad*Math.cos(ph),tgt.z+rad*Math.sin(ph)*Math.sin(th));cam.lookAt(tgt);rd.render(sc,cam);}
function rs(){const w=innerWidth,h=innerHeight-40;rd.setSize(w,h);cam.aspect=w/h;cam.updateProjectionMatrix();upd();}
addEventListener('resize',rs);rs();
let dn=null;const cv=rd.domElement;
cv.addEventListener('pointerdown',e=>{dn={x:e.clientX,y:e.clientY,b:e.button};cv.setPointerCapture(e.pointerId);});
cv.addEventListener('pointerup',()=>dn=null);
cv.addEventListener('pointermove',e=>{if(!dn)return;const dx=e.clientX-dn.x,dy=e.clientY-dn.y;dn.x=e.clientX;dn.y=e.clientY;
 if(dn.b===0){th-=dx*0.005;ph=Math.min(3.1,Math.max(0.05,ph-dy*0.005));}
 else{const k=rad*0.001,r=new THREE.Vector3().setFromMatrixColumn(cam.matrix,0),u=new THREE.Vector3().setFromMatrixColumn(cam.matrix,1);tgt.addScaledVector(r,-dx*k).addScaledVector(u,dy*k);}upd();});
cv.addEventListener('wheel',e=>{e.preventDefault();rad*=Math.exp(e.deltaY*0.001);upd();},{passive:false});
cv.addEventListener('contextmenu',e=>e.preventDefault());
document.querySelectorAll('input[data-k]').forEach(cb=>cb.addEventListener('change',()=>{
 grp.children.forEach(m=>{if(m.name.startsWith(cb.dataset.k+':'))m.visible=cb.checked;});upd();}));
"""


def viewer_html(glb_path, title, counts, out_path):
    b64 = base64.b64encode(open(glb_path, "rb").read()).decode()
    leg = "".join(
        '<label><input type="checkbox" data-k="%s" checked><span class="sw" style="background:%s"></span>%s (%d)</label>'
        % (k, col, k, counts.get(k, 0)) for k, col in
        (("added", "#2ca02c"), ("removed", "#d62728"), ("changed", "#f2c500"), ("unchanged", "#b0b0b0")))
    page = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(t)s</title><style>
html,body{margin:0;height:100%%;font:14px system-ui,sans-serif;background:#f4f4f2;color:#222}
#bar{height:40px;display:flex;gap:18px;align-items:center;padding:0 16px;background:#fff;border-bottom:1px solid #ddd;overflow-x:auto;white-space:nowrap}
.sw{display:inline-block;width:12px;height:12px;margin:0 6px;border-radius:2px;vertical-align:-1px}
#v{height:calc(100%% - 41px)}canvas{display:block}
</style></head><body><div id="bar"><b>%(t)s</b>%(leg)s<span>drag: rotate, right-drag: pan, wheel: zoom</span></div><div id="v"></div>
<script type="text/plain" id="glb">%(b)s</script>
<script src="%(u)s"></script><script>%(js)s</script></body></html>""" % {
        "t": html.escape(title), "leg": leg, "b": b64, "u": THREE_URL, "js": _JS}
    open(out_path, "w", encoding="utf-8").write(page)

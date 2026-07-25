"""Interactive 3D assembly viewer -> single self-contained HTML file.

Open in any browser: orbit/zoom/pan, per-part visibility, exploded view,
half-section, and kinematic animation (each part can carry a sinusoidal
motion spec: axis, amplitude, phase - the free-piston motion model).
"""
import base64
import json
from pathlib import Path

TEMPLATE = r"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>__TITLE__</title>
<style>
 body{margin:0;background:#14181d;color:#dfe6ee;font-family:system-ui,sans-serif;overflow:hidden}
 #panel{position:fixed;top:0;left:0;bottom:0;width:230px;background:#1b2129;padding:14px;
   box-sizing:border-box;overflow-y:auto;border-right:1px solid #2c3644;z-index:2}
 h1{font-size:15px;margin:0 0 12px} h2{font-size:11px;text-transform:uppercase;color:#8fa1b5;margin:16px 0 6px}
 label.part{display:flex;align-items:center;gap:7px;font-size:13px;margin:4px 0;cursor:pointer}
 .dot{width:10px;height:10px;border-radius:50%;display:inline-block}
 input[type=range]{width:100%} .row{font-size:12px;margin:6px 0}
 button{background:#2d6cdf;border:0;color:#fff;padding:6px 12px;border-radius:5px;cursor:pointer;font-size:13px}
 #hint{position:fixed;bottom:8px;right:12px;font-size:11px;color:#66778c;z-index:2}
 #info{position:fixed;top:12px;right:12px;width:250px;background:#1b2129;border:1px solid #2c3644;
   border-radius:8px;padding:12px 14px;z-index:3;display:none;font-size:13px}
 #info h3{margin:0 0 6px;font-size:14px} #info .kv{color:#8fa1b5;font-size:12px;margin:3px 0}
 #info .kv b{color:#dfe6ee;font-weight:500}
 #info button{margin-top:8px;background:#3a4656}
 .pname{cursor:pointer} .pname:hover{color:#7db4ff;text-decoration:underline}
</style></head><body>
<div id="panel">
 <h1>__TITLE__</h1>
 <button id="anim">&#9654; Run</button>
 <h2>Motion speed</h2><input type="range" id="speed" min="0.1" max="3" step="0.1" value="1">
 <h2>Explode</h2><input type="range" id="explode" min="0" max="1" step="0.01" value="0">
 <h2>Half section</h2><div class="row"><label class="part"><input type="checkbox" id="section"> Cut at Y=0</label></div>
 <h2>Gas flow</h2><div class="row"><label class="part"><input type="checkbox" id="gas" checked> Particles (run to animate)</label></div>
 <h2>Cooling water</h2><div class="row"><label class="part"><input type="checkbox" id="water" checked> Circulation</label></div>
 <h2>Parts</h2><div id="parts"></div>
</div>
<div id="hint">drag: orbit &nbsp; wheel: zoom &nbsp; right-drag: pan &nbsp; click part: inspect</div>
<div id="info"><h3 id="i-title"></h3>
 <div class="kv">drawing <b id="i-dwg"></b></div>
 <div class="kv">material <b id="i-mat"></b></div>
 <div class="kv">stock <b id="i-stock"></b></div>
 <button id="i-close">&#10005; back to assembly (Esc)</button></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const DATA = __DATA__;
function parseSTL(b64){
  const bin=atob(b64), n=bin.length, buf=new ArrayBuffer(n), u8=new Uint8Array(buf);
  for(let i=0;i<n;i++) u8[i]=bin.charCodeAt(i);
  const dv=new DataView(buf), tri=dv.getUint32(80,true), pos=new Float32Array(tri*9);
  let o=84;
  for(let t=0;t<tri;t++){ o+=12;
    for(let v=0;v<9;v++){ pos[t*9+v]=dv.getFloat32(o,true); o+=4; } o+=2; }
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.BufferAttribute(pos,3));
  g.computeVertexNormals(); return g;
}
const scene=new THREE.Scene(); scene.background=new THREE.Color(0x14181d);
const renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setSize(innerWidth,innerHeight); renderer.localClippingEnabled=false;
document.body.appendChild(renderer.domElement);
const camera=new THREE.PerspectiveCamera(45,innerWidth/innerHeight,1,50000);
camera.up.set(0,0,1);
scene.add(new THREE.HemisphereLight(0xdfe8ff,0x30281e,0.9));
const dl=new THREE.DirectionalLight(0xffffff,0.8); dl.position.set(300,-500,600); scene.add(dl);
const dl2=new THREE.DirectionalLight(0x88aaff,0.25); dl2.position.set(-400,300,-200); scene.add(dl2);
const clip=new THREE.Plane(new THREE.Vector3(0,-1,0),0);
const meshes=[], bbox=new THREE.Box3();
for(const p of DATA.parts){
  const g=parseSTL(p.stl);
  const m=new THREE.Mesh(g,new THREE.MeshStandardMaterial({color:p.color,metalness:0.35,
    roughness:0.45,side:THREE.DoubleSide,clippingPlanes:[clip],clipShadows:true}));
  m.userData=p; m.position.set(...p.pos);
  if(p.rot) m.rotation.set(p.rot[0]*Math.PI/180,p.rot[1]*Math.PI/180,p.rot[2]*Math.PI/180);
  scene.add(m); meshes.push(m);
  bbox.expandByObject(m);
  const lab=document.createElement('label'); lab.className='part';
  lab.innerHTML=`<input type="checkbox" checked><span class="dot" style="background:${p.color}"></span><span class="pname">${p.name}</span>`;
  lab.querySelector('input').onchange=e=>{ m.visible=e.target.checked; };
  lab.querySelector('.pname').onclick=e=>{ e.preventDefault(); inspect(m); };
  document.getElementById('parts').appendChild(lab);
}
// ---- click-to-inspect: isolate one part, fit camera, show its meta card
let inspecting=null, visSnap=null, camSnap=null;
function fitTo(m){
  const bb=new THREE.Box3().setFromObject(m);
  target=bb.getCenter(new THREE.Vector3());
  dist=Math.max(bb.getSize(new THREE.Vector3()).length()*1.6, 60);
  setCam();
}
function inspect(m){
  if(inspecting===m){ closeInspect(); return; }
  if(!inspecting){
    visSnap=meshes.map(x=>x.visible);
    camSnap={t:target.clone(),d:dist,th:theta,ph:phi};
  }
  inspecting=m;
  for(const x of meshes) x.visible=(x===m);
  const md=m.userData.meta||{};
  document.getElementById('i-title').textContent=md.title||m.userData.name;
  document.getElementById('i-dwg').textContent=md.dwg||'-';
  document.getElementById('i-mat').textContent=md.material||'-';
  document.getElementById('i-stock').textContent=md.stock||'-';
  document.getElementById('info').style.display='block';
  fitTo(m);
}
function closeInspect(){
  if(!inspecting) return;
  meshes.forEach((x,i)=>x.visible=visSnap[i]);
  target=camSnap.t; dist=camSnap.d; theta=camSnap.th; phi=camSnap.ph;
  setCam(); inspecting=null;
  document.getElementById('info').style.display='none';
}
document.getElementById('i-close').onclick=closeInspect;
addEventListener('keydown',e=>{ if(e.key==='Escape') closeInspect(); });
// click (not drag) picks a part
const ray=new THREE.Raycaster(); let downAt=null;
renderer.domElement.addEventListener('pointerdown',e=>{downAt={x:e.clientX,y:e.clientY,t:Date.now()};});
renderer.domElement.addEventListener('pointerup',e=>{
  if(!downAt) return;
  const moved=Math.hypot(e.clientX-downAt.x,e.clientY-downAt.y);
  const dt=Date.now()-downAt.t; downAt=null;
  if(moved>6||dt>400) return;
  const nd=new THREE.Vector2((e.clientX/innerWidth)*2-1,-(e.clientY/innerHeight)*2+1);
  ray.setFromCamera(nd,camera);
  const hits=ray.intersectObjects(meshes.filter(x=>x.visible));
  if(hits.length) inspect(hits[0].object);
});
const ctr=bbox.getCenter(new THREE.Vector3()), R=bbox.getSize(new THREE.Vector3()).length();
let theta=0.8, phi=1.15, dist=R*1.4, target=ctr.clone();
function setCam(){
  camera.position.set(target.x+dist*Math.sin(phi)*Math.cos(theta),
    target.y+dist*Math.sin(phi)*Math.sin(theta), target.z+dist*Math.cos(phi));
  camera.lookAt(target);
}
setCam();
let drag=null;
renderer.domElement.addEventListener('contextmenu',e=>e.preventDefault());
renderer.domElement.addEventListener('pointerdown',e=>{drag={x:e.clientX,y:e.clientY,b:e.button,sh:e.shiftKey};});
addEventListener('pointerup',()=>drag=null);
addEventListener('pointermove',e=>{
  if(!drag) return; const dx=e.clientX-drag.x, dy=e.clientY-drag.y;
  if(drag.b===2||drag.sh){ const s=dist/800;
    const right=new THREE.Vector3().setFromMatrixColumn(camera.matrix,0);
    const up=new THREE.Vector3().setFromMatrixColumn(camera.matrix,1);
    target.addScaledVector(right,-dx*s).addScaledVector(up,dy*s);
  } else { theta-=dx*0.006; phi=Math.min(3.05,Math.max(0.08,phi-dy*0.006)); }
  drag.x=e.clientX; drag.y=e.clientY; setCam();
});
renderer.domElement.addEventListener('wheel',e=>{dist*=(1+Math.sign(e.deltaY)*0.09); setCam();});
addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;
  camera.updateProjectionMatrix(); renderer.setSize(innerWidth,innerHeight);});
// ---- gas-flow particles: oscillating streams along the loop centreline
let gasPts=null;
if(DATA.gas){
  const G=DATA.gas;
  // arc-length LUT over the (s,r) polyline
  const seg=[0]; let Lt=0;
  for(let i=1;i<G.pts.length;i++){
    const ds=G.pts[i][0]-G.pts[i-1][0], dr=G.pts[i][1]-G.pts[i-1][1];
    Lt+=Math.hypot(ds,dr); seg.push(Lt);
  }
  function posAt(u){                     // u in [0,1] -> (s,r)
    const d=Math.min(Math.max(u,0),1)*Lt;
    let i=1; while(i<seg.length-1 && seg[i]<d) i++;
    const f=(d-seg[i-1])/(seg[i]-seg[i-1]);
    return [G.pts[i-1][0]+f*(G.pts[i][0]-G.pts[i-1][0]),
            G.pts[i-1][1]+f*(G.pts[i][1]-G.pts[i-1][1])];
  }
  const N=G.streams*G.per*2, pos=new Float32Array(N*3), col=new Float32Array(N*3);
  const meta=[];                         // per particle: side, theta, u0
  for(const sgn of [1,-1])
    for(let j=0;j<G.streams;j++)
      for(let k=0;k<G.per;k++)
        meta.push([sgn, 2*Math.PI*(j+0.5*(k%2))/G.streams, (k+Math.random()*0.7)/G.per]);
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.BufferAttribute(pos,3));
  g.setAttribute('color',new THREE.BufferAttribute(col,3));
  const mat=new THREE.PointsMaterial({size:3.2,vertexColors:true,
    sizeAttenuation:false,clippingPlanes:[clip],transparent:true,opacity:0.95});
  gasPts=new THREE.Points(g,mat); gasPts.userData={};
  scene.add(gasPts);
  const cHot=new THREE.Color(0xff5238), cCold=new THREE.Color(0x3fa0ff);
  gasPts.tick=function(t){
    const w=2*Math.PI*DATA.freq;
    for(let i=0;i<meta.length;i++){
      const [sgn,th,u0]=meta[i];
      const u=u0+G.amp*Math.sin(w*t+G.phase);
      const [s,r]=posAt(u);
      pos[3*i]=sgn*s; pos[3*i+1]=r*Math.cos(th); pos[3*i+2]=r*Math.sin(th);
      let f;                             // 0 hot .. 1 cold, by axial position
      if(s<=G.hot_end_s) f=0;
      else if(s>=G.cool_span[1]) f=1;
      else f=(s-G.cool_span[0])/(G.cool_span[1]-G.cool_span[0]);
      f=Math.min(Math.max(f,0),1);
      const c=cHot.clone().lerp(cCold,f);
      col[3*i]=c.r; col[3*i+1]=c.g; col[3*i+2]=c.b;
    }
    g.attributes.position.needsUpdate=true;
    g.attributes.color.needsUpdate=true;
  };
  gasPts.tick(0);
  document.getElementById('gas').onchange=e=>{gasPts.visible=e.target.checked;};
}
// ---- cooling-water particles: steady circulation boss -> gallery -> boss
let waterPts=null;
if(DATA.water){
  const W=DATA.water, per=W.per;
  const N=per*2*2, pos=new Float32Array(N*3), col=new Float32Array(N*3);
  const meta=[];
  for(const sgn of [1,-1]) for(const b of [1,-1])
    for(let k=0;k<per;k++) meta.push([sgn,b,(k+Math.random()*0.8)/per]);
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.BufferAttribute(pos,3));
  g.setAttribute('color',new THREE.BufferAttribute(col,3));
  waterPts=new THREE.Points(g,new THREE.PointsMaterial({size:2.8,
    vertexColors:true,sizeAttenuation:false,clippingPlanes:[clip],
    transparent:true,opacity:0.9}));
  scene.add(waterPts);
  const cIn=new THREE.Color(0x35d0f0), cOut=new THREE.Color(0x3f7fd9);
  waterPts.tick=function(t){
    for(let i=0;i<meta.length;i++){
      const [sgn,b,u0]=meta[i];
      const u=(u0+0.22*t)%1;
      let th,r;
      if(u<0.15){ th=0; r=W.r_boss-(W.r_boss-W.r_gal)*(u/0.15); }
      else if(u<0.85){ th=b*Math.PI*(u-0.15)/0.7; r=W.r_gal; }
      else { th=Math.PI; r=W.r_gal+(W.r_boss-W.r_gal)*((u-0.85)/0.15); }
      pos[3*i]=sgn*W.s; pos[3*i+1]=r*Math.cos(th); pos[3*i+2]=r*Math.sin(th);
      const c=cIn.clone().lerp(cOut,u);
      col[3*i]=c.r; col[3*i+1]=c.g; col[3*i+2]=c.b;
    }
    g.attributes.position.needsUpdate=true;
    g.attributes.color.needsUpdate=true;
  };
  waterPts.tick(0);
  document.getElementById('water').onchange=e=>{waterPts.visible=e.target.checked;};
}
let running=false,t0=0,tAcc=0;
document.getElementById('anim').onclick=function(){
  running=!running; this.innerHTML=running?'&#10074;&#10074; Pause':'&#9654; Run';
  if(running) t0=performance.now();
};
document.getElementById('section').onchange=e=>{renderer.localClippingEnabled=e.target.checked;};
function frame(now){
  requestAnimationFrame(frame);
  const speed=+document.getElementById('speed').value;
  const ex=+document.getElementById('explode').value;
  if(running){ tAcc+=(now-t0)*0.001*speed; t0=now; } else t0=now;
  const w=2*Math.PI*DATA.freq;
  for(const m of meshes){
    const p=m.userData; m.position.set(...p.pos);
    if(p.motion){ const q=p.motion.amp*Math.sin(w*tAcc+p.motion.phase);
      m.position.addScaledVector(new THREE.Vector3(...p.motion.axis),q); }
    if(p.explode) m.position.addScaledVector(new THREE.Vector3(...p.explode),ex);
  }
  if(gasPts && gasPts.visible) gasPts.tick(tAcc);
  if(waterPts && waterPts.visible) waterPts.tick(tAcc);
  renderer.render(scene,camera);
}
requestAnimationFrame(frame);
</script></body></html>"""


def build_viewer(parts, out_html, title="Assembly", freq=0.5, gas=None,
                 water=None):
    """parts: [{name, stl (Path), color '#hex', pos [x,y,z],
               motion {axis,amp,phase} | None, explode [x,y,z] | None}]
    gas / water: optional particle-flow specs (see assembly.GAS_PATH /
    assembly.WATER_PATH)"""
    data = {"freq": freq, "parts": [], "gas": gas, "water": water}
    for p in parts:
        data["parts"].append({
            "name": p["name"],
            "meta": p.get("meta"),
            "color": p.get("color", "#8aa2b8"),
            "pos": list(p.get("pos", (0, 0, 0))),
            "rot": list(p.get("rot", (0, 0, 0))),
            "motion": p.get("motion"),
            "explode": list(p["explode"]) if p.get("explode") else None,
            "stl": base64.b64encode(Path(p["stl"]).read_bytes()).decode(),
        })
    html = TEMPLATE.replace("__TITLE__", title).replace("__DATA__", json.dumps(data))
    out = Path(out_html)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    return out

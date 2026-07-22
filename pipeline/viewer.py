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
</style></head><body>
<div id="panel">
 <h1>__TITLE__</h1>
 <button id="anim">&#9654; Run</button>
 <h2>Motion speed</h2><input type="range" id="speed" min="0.1" max="3" step="0.1" value="1">
 <h2>Explode</h2><input type="range" id="explode" min="0" max="1" step="0.01" value="0">
 <h2>Half section</h2><div class="row"><label class="part"><input type="checkbox" id="section"> Cut at Y=0</label></div>
 <h2>Parts</h2><div id="parts"></div>
</div>
<div id="hint">drag: orbit &nbsp; wheel: zoom &nbsp; right-drag: pan</div>
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
  m.userData=p; m.position.set(...p.pos); scene.add(m); meshes.push(m);
  bbox.expandByObject(m);
  const lab=document.createElement('label'); lab.className='part';
  lab.innerHTML=`<input type="checkbox" checked><span class="dot" style="background:${p.color}"></span>${p.name}`;
  lab.querySelector('input').onchange=e=>{ m.visible=e.target.checked; };
  document.getElementById('parts').appendChild(lab);
}
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
  renderer.render(scene,camera);
}
requestAnimationFrame(frame);
</script></body></html>"""


def build_viewer(parts, out_html, title="Assembly", freq=0.5):
    """parts: [{name, stl (Path), color '#hex', pos [x,y,z],
               motion {axis,amp,phase} | None, explode [x,y,z] | None}]"""
    data = {"freq": freq, "parts": []}
    for p in parts:
        data["parts"].append({
            "name": p["name"],
            "color": p.get("color", "#8aa2b8"),
            "pos": list(p.get("pos", (0, 0, 0))),
            "motion": p.get("motion"),
            "explode": list(p["explode"]) if p.get("explode") else None,
            "stl": base64.b64encode(Path(p["stl"]).read_bytes()).decode(),
        })
    html = TEMPLATE.replace("__TITLE__", title).replace("__DATA__", json.dumps(data))
    out = Path(out_html)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    return out

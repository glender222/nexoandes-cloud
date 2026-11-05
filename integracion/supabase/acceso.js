"use strict";
const estado=document.querySelector('#estado'), formulario=document.querySelector('#login'), cuenta=document.querySelector('#cuenta');
let sesion=null;
const configurar=()=>{formulario.hidden=Boolean(sesion);cuenta.hidden=!sesion;document.querySelector('#identidad').textContent=sesion?.user?.email||'';};
async function auth(path,body,token){
  const headers={'Content-Type':'application/json','apikey':NEXO_SUPABASE.publicKey};
  if(token)headers.Authorization='Bearer '+token;
  const r=await fetch(NEXO_SUPABASE.url+'/auth/v1/'+path,{method:'POST',headers,body:JSON.stringify(body||{})});
  const data=await r.json().catch(()=>({}));if(!r.ok)throw new Error('No se pudo completar la autenticación. Revisa tus credenciales o inténtalo de nuevo.');return data;
}
formulario.addEventListener('submit',async e=>{
  e.preventDefault();const boton=formulario.querySelector('button');boton.disabled=true;estado.textContent='Comprobando acceso…';
  try{sesion=await auth('token?grant_type=password',{email:document.querySelector('#email').value.trim(),password:document.querySelector('#password').value});document.querySelector('#password').value='';configurar();estado.textContent='Acceso correcto.';}
  catch(error){estado.textContent=error.message;}finally{boton.disabled=false;}
});
document.querySelector('#comprobar').addEventListener('click',async()=>{
  try{const r=await fetch('/api/privado',{headers:{Authorization:'Bearer '+sesion.access_token}});const d=await r.json();if(!r.ok)throw new Error('La sesión venció o el servicio no está disponible.');estado.textContent=d.mensaje;}
  catch(error){estado.textContent=error.message;}
});
document.querySelector('#salir').addEventListener('click',async()=>{
  try{await auth('logout',{},sesion.access_token);estado.textContent='Sesión cerrada.';}catch(error){estado.textContent='Se cerró la sesión de este navegador; el servidor no confirmó la revocación.';}
  sesion=null;configurar();
});
// El token permanece solo en memoria. Recargar exige iniciar sesión de nuevo.
configurar();

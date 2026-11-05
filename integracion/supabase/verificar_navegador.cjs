/* Prueba de interfaz real; pin de la clave TLS académica, sin ignorar otros certificados. */
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium}=require(process.env.NEXO_PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(__dirname,'../..');
const proof=JSON.parse(fs.readFileSync(path.join(root,'integracion/evidencias/20261104/supabase/pruebas-auth.json')));
const demo=JSON.parse(fs.readFileSync(path.join(root,'integracion/privado/supabase/acceso-demo.json')));
const cert=new crypto.X509Certificate(fs.readFileSync(path.join(root,'integracion/privado/tls/alb.crt')));
const pin=crypto.createHash('sha256').update(cert.publicKey.export({type:'spki',format:'der'})).digest('base64');
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--ignore-certificate-errors-spki-list='+pin]});
 try{
  const page=await browser.newPage({viewport:{width:1200,height:900}});
  await page.goto(proof.login,{waitUntil:'networkidle'});
  await page.screenshot({path:path.join(root,'integracion/evidencias/20261104/supabase/login.png'),fullPage:true});
  await page.fill('#email',demo.email);await page.fill('#password',demo.password);
  await page.click('button[type=submit]');
  await page.waitForFunction(()=>document.querySelector('#estado').textContent==='Acceso correcto.');
  await page.click('#comprobar');
  await page.waitForFunction(()=>document.querySelector('#estado').textContent==='Sesión validada en el backend de NexoAndes');
  await page.screenshot({path:path.join(root,'integracion/evidencias/20261104/supabase/sesion-validada.png'),fullPage:true});
  await page.click('#salir');
  await page.waitForFunction(()=>document.querySelector('#estado').textContent==='Sesión cerrada.');
  await page.setViewportSize({width:390,height:844});
  await page.screenshot({path:path.join(root,'integracion/evidencias/20261104/supabase/login-movil.png'),fullPage:true});
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
  if(overflow)throw new Error('La vista móvil desborda horizontalmente');
  const result={utc:new Date().toISOString(),login:true,endpoint_privado:true,logout:true,movil_sin_desbordamiento:true,tls:'Excepción acotada al pin SPKI del certificado académico; validación nombre/CA acreditada por prueba HTTP separada',capturas:['login.png','sesion-validada.png','login-movil.png']};
  fs.writeFileSync(path.join(root,'integracion/evidencias/20261104/supabase/navegador.json'),JSON.stringify(result,null,2)+'\n');
  process.stdout.write(JSON.stringify(result)+'\n');
 }finally{await browser.close();}
})().catch(error=>{process.stderr.write(error.message+'\n');process.exit(1);});

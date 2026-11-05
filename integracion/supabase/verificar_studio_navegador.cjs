/* Studio real por HTTPS: credenciales solo en memoria y captura inicialmente privada. */
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium}=require(process.env.NEXO_PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(__dirname,'../..');
const admin=JSON.parse(fs.readFileSync(path.join(root,'integracion/privado/supabase/acceso-administracion.json')));
const cert=new crypto.X509Certificate(fs.readFileSync(path.join(root,'integracion/privado/tls/alb.crt')));
const pin=crypto.createHash('sha256').update(cert.publicKey.export({type:'spki',format:'der'})).digest('base64');
(async()=>{
 if(!admin.url_externa)throw new Error('Falta URL externa verificada');
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--ignore-certificate-errors-spki-list='+pin]});
 try{
  const context=await browser.newContext({viewport:{width:1440,height:1000},httpCredentials:{username:admin.usuario,password:admin.password,origin:admin.url_externa}});
  const page=await context.newPage();let jsErrors=0;let api=[];
  page.on('pageerror',()=>jsErrors++);
  page.on('response',r=>{const u=new URL(r.url());if(u.origin===admin.url_externa&&u.pathname.startsWith('/api/'))api.push({ruta:u.pathname,status:r.status()});});
  const response=await page.goto(admin.url_externa,{waitUntil:'domcontentloaded',timeout:60000});
  if(response.status()!==200)throw new Error('Studio no devolvió HTTP 200');
  await page.waitForLoadState('networkidle',{timeout:30000}).catch(()=>{});
  await page.waitForFunction(()=>document.body.innerText.includes('Table Editor')||document.body.innerText.includes('SQL Editor'),{timeout:30000});
  if(new URL(page.url()).origin!==admin.url_externa)throw new Error('Cambio inesperado de origen');
  const screenshot=path.join(root,'integracion/privado/supabase/studio-externo.png');
  await page.screenshot({path:screenshot,fullPage:true});fs.chmodSync(screenshot,0o600);
  const proof={utc:new Date().toISOString(),url:admin.url_externa,ruta_final:new URL(page.url()).pathname,status:response.status(),panel_cargado:true,errores_js:jsErrors,api,tls:'Pin SPKI académico limitado; verificación CA/nombre en prueba HTTP',captura:'Privada hasta inspección visual'};
  fs.writeFileSync(path.join(root,'integracion/evidencias/20261104/supabase/studio-navegador.json'),JSON.stringify(proof,null,2)+'\n');
  process.stdout.write(JSON.stringify(proof)+'\n');
 }finally{await browser.close()}
})().catch(e=>{process.stderr.write(e.message+'\n');process.exit(1)});

// Test du binaire réel, profils/hôtes temporaires uniquement.
// Usage: node tools/validate-native-messaging.mjs /chemin/helium resultat.json
import {mkdtempSync, mkdirSync, writeFileSync, readFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {spawn} from 'node:child_process';
import {generateKeyPairSync, createHash} from 'node:crypto';
const [binary, output] = process.argv.slice(2);
const root=mkdtempSync(join(tmpdir(),'glyphe-native-'));
const ext=join(root,'extension');mkdirSync(ext);
const {publicKey}=generateKeyPairSync('rsa',{modulusLength:2048});
const key=publicKey.export({type:'spki',format:'der'});
const id=[...createHash('sha256').update(key).digest().subarray(0,16)]
 .map(b=>String.fromCharCode(97+(b>>4),97+(b&15))).join('');
writeFileSync(join(ext,'manifest.json'),JSON.stringify({manifest_version:3,name:'Glyphe Native Test',version:'1.0',key:key.toString('base64'),permissions:['nativeMessaging']}));
writeFileSync(join(ext,'test.html'),'<!doctype html><title>Glyphe Native Test</title>');
const host=join(root,'echo.py');
writeFileSync(host,`#!/usr/bin/env python3
import sys,struct,json
size=sys.stdin.buffer.read(4)
if len(size)==4:
 data=json.loads(sys.stdin.buffer.read(struct.unpack('<I',size)[0]))
 result=json.dumps({'echo':data,'origin':sys.argv[1]}).encode()
 sys.stdout.buffer.write(struct.pack('<I',len(result))+result)
 sys.stdout.buffer.flush()
`,{mode:0o755});
const config=join(root,'config');
for(const [browser,name,allowed] of [['chromium','com.glyphe.test',id],['google-chrome','com.glyphe.chrome',id],['chromium','com.glyphe.denied','aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa']]){
 const dir=join(config,browser,'NativeMessagingHosts');mkdirSync(dir,{recursive:true});
 writeFileSync(join(dir,name+'.json'),JSON.stringify({name,description:'Glyphe test',type:'stdio',path:host,allowed_origins:[`chrome-extension://${allowed}/`]}));
}
const port=9355;
const child=spawn(binary,['--headless=new','--enable-unsafe-extension-debugging',`--user-data-dir=${join(root,'profile')}`,`--remote-debugging-port=${port}`,`--load-extension=${ext}`,'--no-first-run','--no-default-browser-check',`chrome-extension://${id}/test.html`],{env:{...process.env,XDG_CONFIG_HOME:config},stdio:'ignore'});
const pause=ms=>new Promise(r=>setTimeout(r,ms));let ws;
try{
 let targets;
 for(let n=0;n<100;n++){try{targets=await(await fetch(`http://127.0.0.1:${port}/json`)).json();if(targets.some(x=>x.url.includes(id)))break;}catch{}await pause(150);}
 const target=targets?.find(x=>x.type==='page'&&x.url.includes(id));if(!target)throw Error('Extension de test non chargée');
 ws=new WebSocket(target.webSocketDebuggerUrl);await new Promise(r=>ws.addEventListener('open',r,{once:true}));let seq=0;const waiting=new Map();
 ws.onmessage=e=>{const msg=JSON.parse(e.data);if(msg.id){waiting.get(msg.id)?.(msg);waiting.delete(msg.id)}};
 const send=(method,params)=>new Promise(r=>{const id=++seq;waiting.set(id,r);ws.send(JSON.stringify({id,method,params}))});
 const results={root,extension:id,cases:{}};
 await pause(1000); await send('Page.reload',{}); await pause(1000);
 if(process.env.GLYPHE_TEST_DEBUG)console.log(await send('Runtime.evaluate',{expression:'document.body.innerText',returnByValue:true}));
 for(const name of ['com.glyphe.test','com.glyphe.chrome','com.glyphe.denied']){
  const expression=`new Promise(resolve=>chrome.runtime.sendNativeMessage(${JSON.stringify(name)}, {glyphe:157}, reply=>resolve({reply,error:chrome.runtime.lastError?.message})))`;
  const response=await Promise.race([send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true}),pause(15000).then(()=>{throw Error('Délai Native Messaging dépassé')})]);
  results.cases[name]=response.result?.exceptionDetails??response.result?.result?.value??response; if(process.env.GLYPHE_TEST_DEBUG)console.log(JSON.stringify(response));
 }
 results.passed=results.cases['com.glyphe.test'].reply?.echo?.glyphe===157&&results.cases['com.glyphe.chrome'].reply?.echo?.glyphe===157&&!!results.cases['com.glyphe.denied'].error;
 writeFileSync(output,JSON.stringify(results,null,2)+'\n');console.log(JSON.stringify(results));if(!results.passed)process.exitCode=1;
}finally{ws?.close();child.kill('SIGTERM');}

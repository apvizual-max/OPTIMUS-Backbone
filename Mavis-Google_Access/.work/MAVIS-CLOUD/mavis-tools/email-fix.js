const k=require('./kit.js');
async function ids(q){const o=[];let p=null;do{const r=await k.req('GET','https://gmail.googleapis.com/gmail/v1/users/me/messages?q='+encodeURIComponent(q)+'&maxResults=500'+(p?'&pageToken='+p:''));o.push(...(r.messages||[]).map(m=>m.id));p=r.nextPageToken||null;}while(p);return o;}
(async()=>{
  const old5=await ids('older_than:5y');
  console.log('5+ ani:',old5.length);
  const th=new Map();
  for(let i=0;i<old5.length;i+=500){
    const rs=await Promise.all(old5.slice(i,i+500).map(id=>k.req('GET',`https://gmail.googleapis.com/gmail/v1/users/me/messages/${id}?format=minimal`).catch(()=>null)));
    rs.forEach((r,j)=>{if(r&&r.threadId){if(!th.has(r.threadId))th.set(r.threadId,[]);th.get(r.threadId).push(old5[i+j]);}});
  }
  const sent=await ids('in:sent older_than:5y');
  const keepT=new Set();
  for(let i=0;i<sent.length;i+=400){
    const rs=await Promise.all(sent.slice(i,i+400).map(id=>k.req('GET',`https://gmail.googleapis.com/gmail/v1/users/me/messages/${id}?format=minimal`).catch(()=>null)));
    rs.forEach(r=>{if(r&&r.threadId)keepT.add(r.threadId);});
  }
  const drop=[];th.forEach((m,t)=>{if(!keepT.has(t))drop.push(...m);});
  console.log('thread-uri 5+ ani:',th.size,'| pastrate (a raspuns):',keepT.size);
  console.log('se trimit in recycle bin:',drop.length);
  for(let i=0;i<drop.length;i+=1000){
    try{ await k.req('POST','https://gmail.googleapis.com/gmail/v1/users/me/messages/batchModify',{ids:drop.slice(i,i+1000),addLabelIds:['TRASH']}); }
    catch(e){ console.log('blocat la',i,String(e.message).slice(0,60)); }
  }
  console.log('GATA - trimise in recycle bin (recuperabile):',drop.length);
})();

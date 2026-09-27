const alertForm=document.getElementById("alert-form");
if(alertForm){
  const list=document.getElementById("alert-list");
  const message=document.getElementById("alert-message");

  async function refreshAlerts(){
    const response=await fetch("/api/alerts");
    const payload=await response.json();
    if(!payload.data?.length){list.textContent="No price alerts yet.";return;}
    list.replaceChildren(...payload.data.map(alert=>{
      const row=document.createElement("div");row.className="alert-row";
      const description=document.createElement("div");
      const drug=document.createElement("b");drug.textContent=alert.drug_name;
      const details=document.createElement("span");details.textContent=`${alert.brand_status} · below $${alert.threshold_price.toFixed(2)} · latest $${alert.current_price?.toFixed(2)??"unavailable"}`;
      description.append(drug,details);
      const status=document.createElement("span");status.className=`badge ${alert.triggered?"alert-triggered":""}`;status.textContent=alert.triggered?"Triggered":"Watching";
      const remove=document.createElement("button");remove.className="icon-button";remove.type="button";remove.title="Delete alert";remove.setAttribute("aria-label",`Delete ${alert.drug_name} alert`);remove.textContent="×";
      remove.addEventListener("click",async()=>{await fetch(`/api/alerts/${alert.id}`,{method:"DELETE"});refreshAlerts();});
      row.append(description,status,remove);return row;
    }));
  }

  alertForm.addEventListener("submit",async event=>{
    event.preventDefault();
    const response=await fetch("/api/alerts",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(Object.fromEntries(new FormData(alertForm)))});
    const payload=await response.json();
    if(!response.ok){message.textContent=payload.error?.message||"Unable to create alert.";return;}
    alertForm.reset();message.textContent="Alert saved.";refreshAlerts();
  });
  refreshAlerts();
}
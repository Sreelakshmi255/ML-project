const search=document.getElementById("history-search");
const filter=document.getElementById("history-filter");
const target=document.getElementById("history-table");
const adminView=target.dataset.adminView==="true";
let rows=[];

async function load(){
	const response=await fetch(target.dataset.historyUrl);
	const payload=await response.json();
	if(!response.ok||payload.success===false){
		target.innerHTML='<div class="empty"><h3>History unavailable</h3><p>Please try again.</p></div>';
		return;
	}
	rows=payload.data;
	render();
}

function render(){
	const query=(search.value||"").toLowerCase();
	const status=filter.value;
	const matches=rows.filter(row=>
		(!query||row.drug_name.toLowerCase().includes(query)||
			(adminView&&`${row.user_name} ${row.user_email}`.toLowerCase().includes(query)))&&
		(!status||row.brand_status===status)
	);
	if(!matches.length){
		target.innerHTML='<div class="empty"><h3>No matching predictions</h3><p>Try a different search.</p></div>';
		return;
	}

	const table=document.createElement("table");
	const head=table.createTHead().insertRow();
	if(adminView)head.insertCell().textContent="User";
	["Drug","Status","Estimate","Date"].forEach(label=>head.insertCell().textContent=label);
	const body=table.createTBody();
	matches.forEach(row=>{
		const tr=body.insertRow();
		if(adminView){
			const owner=tr.insertCell();
			owner.textContent=`${row.user_name} (${row.user_email})`;
		}
		const drug=tr.insertCell();
		const link=document.createElement("a");
		link.href=adminView?`/admin/results/${row.id}`:`/results/${row.id}`;
		link.textContent=row.drug_name;
		const dosage=document.createElement("small");
		dosage.textContent=`${row.dosage} mg`;
		drug.append(link,dosage);
		const statusCell=tr.insertCell();
		const badge=document.createElement("span");
		badge.className="badge";
		badge.textContent=row.brand_status;
		statusCell.append(badge);
		const price=tr.insertCell();
		const estimate=document.createElement("b");
		estimate.textContent=`$${row.predicted_cost.toFixed(2)}`;
		price.append(estimate);
		tr.insertCell().textContent=row.date;
	});
	target.replaceChildren(table);
}

search?.addEventListener("input",render);
filter?.addEventListener("change",render);
load();
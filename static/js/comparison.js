const drugInput=document.getElementById("comparison-drug");
const statusInput=document.getElementById("comparison-status");
const sortInput=document.getElementById("comparison-sort");
const body=document.getElementById("comparison-body");
const notice=document.getElementById("comparison-notice");

async function loadMedicineOptions(){
	const response=await fetch("/api/drugs/search");
	const payload=await response.json();
	document.getElementById("comparison-drugs").replaceChildren(...(payload.data||[]).map(item=>{
		const option=document.createElement("option");option.value=item.name;return option;
	}));
	if(payload.data?.length){drugInput.value=payload.data[0].name;loadOffers();}
}

async function loadOffers(){
	if(!drugInput.value.trim()){body.textContent="Choose a medicine to compare estimates.";return;}
	body.textContent="Loading estimated prices…";
	const params=new URLSearchParams({drug:drugInput.value.trim(),brand_status:statusInput.value,sort:sortInput.value});
	const response=await fetch(`/api/pharmacies?${params}`);
	const payload=await response.json();
	if(!response.ok){body.textContent=payload.error?.message||"No pharmacy estimates available.";notice.textContent="";return;}
	notice.textContent=payload.notice;
	body.replaceChildren(...payload.data.map(offer=>{
		const row=document.createElement("div");row.className="feature-table-row";
		[offer.pharmacy,`$${offer.price.toFixed(2)}`,`$${offer.difference.toFixed(2)}`,offer.available?"Estimated available":"Availability unknown"].forEach(value=>{
			const cell=document.createElement("span");cell.textContent=value;row.append(cell);
		});
		return row;
	}));
}

document.getElementById("comparison-load").addEventListener("click",loadOffers);
statusInput.addEventListener("change",loadOffers);
sortInput.addEventListener("change",loadOffers);
drugInput.addEventListener("change",loadOffers);
loadMedicineOptions();
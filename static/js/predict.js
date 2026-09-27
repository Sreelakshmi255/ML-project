const form=document.getElementById("prediction-form");
if(form){
	const drugInput=document.getElementById("drug-search");
	const statusInput=form.elements.brand_status;
	const detail=document.getElementById("medicine-details");
	let matches=[];
	let searchTimer;

	async function findDrugs(query){
		const response=await fetch(`/api/drugs/search?q=${encodeURIComponent(query)}`);
		const payload=await response.json();
		matches=payload.data||[];
		document.getElementById("drug-suggestions").replaceChildren(...matches.map(item=>{
			const option=document.createElement("option");option.value=item.name;return option;
		}));
		updateDetails();
	}

	function updateDetails(){
		const query=drugInput.value.trim().toLowerCase();
		if(!query){detail.textContent="Search a medicine to view its generic and brand history.";return;}
		const match=matches.find(item=>item.name.toLowerCase()===query)||matches[0];
		if(!match){detail.textContent="Search a medicine to view its generic and brand history.";return;}
		const current=match[statusInput.value.toLowerCase()];
		const prefix=match.name.toLowerCase()===query?"":"Suggestion: ";
		const history=current.history.map(row=>`${row.quarter} ${row.year}: $${row.price.toFixed(2)}`).join(" · ");
		detail.textContent=`${prefix}${match.name} · ${match.historical_records} historical records total. ${statusInput.value}: ${current.records} records${history?"; "+history:"; no historical records available"}.`;
	}

	drugInput.addEventListener("input",()=>{
		clearTimeout(searchTimer);
		searchTimer=setTimeout(()=>findDrugs(drugInput.value.trim()),180);
	});
	statusInput.addEventListener("change",updateDetails);
	findDrugs("");

	form.addEventListener("submit",async event=>{
		event.preventDefault();
		const button=form.querySelector("button");
		const error=document.getElementById("prediction-error");
		error.hidden=true;button.disabled=true;button.textContent="Calculating…";
		try{
			const response=await fetch("/api/predict",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(Object.fromEntries(new FormData(form)))});
			const payload=await response.json();
			if(!response.ok)throw new Error(payload.error?.message||"Prediction failed");
			location.href=`/results/${payload.id}`;
		}catch(exception){
			error.textContent=exception.message;error.hidden=false;button.disabled=false;button.textContent="Calculate forecast →";
		}
	});
}
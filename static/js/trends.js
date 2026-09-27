const drugSelect=document.getElementById("trend-drug");
const statusSelect=document.getElementById("trend-status");
const periodSelect=document.getElementById("trend-period");
const chart=document.getElementById("trend-chart");
const summary=document.getElementById("trend-summary");

async function drawTrend(){
	const params=new URLSearchParams({drug:drugSelect.value,brand_status:statusSelect.value,months:periodSelect.value});
	const response=await fetch(`/api/trends?${params}`);
	const payload=await response.json();
	const rows=payload.data||[];
	if(!rows.length){chart.textContent="No historical records are available for this selection.";summary.replaceChildren();return;}
	const prices=rows.map(row=>row.price);
	const facts=[
		["Average",`$${payload.summary.average.toFixed(2)}`],
		["Highest",`$${payload.summary.highest.toFixed(2)}`],
		["Lowest",`$${payload.summary.lowest.toFixed(2)}`],
		["Change",`${payload.summary.change_pct>0?"+":""}${payload.summary.change_pct.toFixed(1)}%`]
	];
	if(payload.prediction)facts.push(["Predicted",`$${payload.prediction.price.toFixed(2)} (${payload.prediction.low.toFixed(2)}–${payload.prediction.high.toFixed(2)})`]);
	summary.replaceChildren(...facts.map(([label,value])=>{
		const item=document.createElement("div");item.className="feature-stat";
		const caption=document.createElement("span");caption.textContent=label;
		const amount=document.createElement("b");amount.textContent=value;
		item.append(caption,amount);return item;
	}));

	const width=900,height=330,padding=48,values=payload.prediction?[...prices,payload.prediction.price]:prices;
	const maximum=Math.max(...values)*1.15,scale=Math.max(maximum,1),step=(width-padding*2)/Math.max(values.length-1,1);
	const y=value=>height-padding-(value/scale)*(height-padding*2);
	const historical=rows.map((row,index)=>`${padding+index*step},${y(row.price)}`).join(" ");
	const marker=rows.map((row,index)=>`<circle cx="${padding+index*step}" cy="${y(row.price)}" r="5" fill="#126f68"/><text x="${padding+index*step}" y="${height-14}" text-anchor="middle">${row.quarter} ${row.year}</text>`).join("");
	let predictedLine="";
	if(payload.prediction){
		const last=rows.length-1,x1=padding+last*step,x2=padding+(last+1)*step;
		predictedLine=`<line x1="${x1}" y1="${y(rows[last].price)}" x2="${x2}" y2="${y(payload.prediction.price)}" stroke="#c35435" stroke-width="4" stroke-dasharray="8 6"/><circle cx="${x2}" cy="${y(payload.prediction.price)}" r="6" fill="#c35435"/><text x="${x2}" y="${height-14}" text-anchor="middle">Predicted</text>`;
	}
	chart.innerHTML=`<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Quarterly medicine price history with optional prediction"><line x1="${padding}" y1="${height-padding}" x2="${width-padding}" y2="${height-padding}" stroke="currentColor" opacity=".18"/><polyline points="${historical}" fill="none" stroke="#126f68" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>${marker}${predictedLine}</svg>`;
}

async function initTrends(){
	const response=await fetch("/api/drugs/search");
	const payload=await response.json();
	drugSelect.replaceChildren(...(payload.data||[]).map(item=>{
		const option=document.createElement("option");option.value=item.name;option.textContent=item.name;return option;
	}));
	[drugSelect,statusSelect,periodSelect].forEach(control=>control.addEventListener("change",drawTrend));
	if(drugSelect.value)drawTrend();
}
initTrends();
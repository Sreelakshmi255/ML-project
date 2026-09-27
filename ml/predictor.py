from pathlib import Path
import numpy as np, pandas as pd, joblib
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

class Predictor:
    def __init__(self, base):
        self.base=Path(base)
        self.model_path=self.base/"models"/"best_model.joblib"
        self.metrics_path=self.base/"models"/"metrics.joblib"
        self.model=None; self._metrics=None

    def _dataset(self):
        # Synthetic but deterministic demonstration training data.
        drugs=["Atorvastatin","Lisinopril","Metformin","Amlodipine","Levothyroxine","Omeprazole",
               "Losartan","Gabapentin","Sertraline","Montelukast","Pantoprazole","Rosuvastatin"]
        rows=[]
        rng=np.random.default_rng(7)
        for _ in range(900):
            drug=rng.choice(drugs); dosage=float(rng.choice([5,10,20,40,50,75,100]))
            generic=rng.choice(["Generic","Brand"],p=[.72,.28])
            q1=float(rng.uniform(5,75)); growth=float(rng.normal(.025,.02))
            qs=[q1]
            for _q in range(3): qs.append(qs[-1]*(1+growth+rng.normal(0,.025)))
            brand_factor=1 if generic=="Generic" else 2.1
            target=max(1, qs[-1]*(1+rng.normal(.035,.03))*brand_factor/1.15 + dosage*.035)
            rows.append([drug,dosage,generic,*qs,target])
        return pd.DataFrame(rows,columns=["drug","dosage","status","q1","q2","q3","q4","target"])

    def _features(self, df):
        x=df.copy()
        x["mean_price"]=x[["q1","q2","q3","q4"]].mean(axis=1)
        x["trend"]=x["q4"]-x["q1"]
        x["volatility"]=x[["q1","q2","q3","q4"]].std(axis=1).fillna(0)
        return x

    def train(self):
        df=self._features(self._dataset())
        X=df.drop(columns=["target"]); y=df.target
        pre=ColumnTransformer([
            ("drug",TfidfVectorizer(max_features=80,ngram_range=(1,2)), "drug"),
            ("status",OneHotEncoder(handle_unknown="ignore"),["status"]),
            ("num",StandardScaler(),["dosage","q1","q2","q3","q4","mean_price","trend","volatility"])
        ])
        Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,random_state=42)
        candidates={
            "Ridge Regression":Ridge(alpha=1.0),
            "Random Forest Regressor":RandomForestRegressor(n_estimators=180,random_state=42,n_jobs=-1,max_depth=12),
            "Gradient Boosting Regressor":GradientBoostingRegressor(random_state=42,n_estimators=140,max_depth=3)
        }
        scores={}
        best=None; best_rmse=float("inf")
        for name,reg in candidates.items():
            pipe=Pipeline([("prep",pre),("model",reg)])
            pipe.fit(Xtr,ytr); pred=pipe.predict(Xte)
            rmse=float(mean_squared_error(yte,pred)**.5)
            scores[name]={"mae":round(float(mean_absolute_error(yte,pred)),3),
                          "rmse":round(rmse,3),"r2":round(float(r2_score(yte,pred)),3)}
            if rmse<best_rmse: best_rmse=rmse; best=(name,pipe)
        self.model_path.parent.mkdir(exist_ok=True)
        joblib.dump(best[1],self.model_path)
        self._metrics={"selected_model":best[0],"models":scores,"trained_on":len(df)}
        joblib.dump(self._metrics,self.metrics_path)
        self.model=best[1]
        return self._metrics

    def ensure_model(self):
        if self.model_path.exists():
            self.model=joblib.load(self.model_path)
            self._metrics=joblib.load(self.metrics_path) if self.metrics_path.exists() else None
        else:
            self.train()

    def predict(self,d):
        if self.model is None: self.ensure_model()
        row=pd.DataFrame([{"drug":d["drug_name"],"dosage":d["dosage_strength"],"status":d["brand_status"],
                           "q1":d["q1_price"],"q2":d["q2_price"],"q3":d["q3_price"],"q4":d["q4_price"]}])
        row=self._features(row)
        value=float(self.model.predict(row)[0])
        historical=np.array([d["q1_price"],d["q2_price"],d["q3_price"],d["q4_price"]])
        spread=float(max(np.std(historical)*.55, value*.06))
        low=max(0.01,value-spread); high=value+spread
        return {"predicted_cost":round(value,2),"low_cost":round(low,2),"high_cost":round(high,2),
                "model_name":self._metrics.get("selected_model","Regression model")}

    def trend_for(self,*prices):
        delta=(prices[-1]-prices[0])/prices[0]*100
        return {"direction":"up" if delta>1 else "down" if delta<-1 else "stable","change_pct":round(delta,1)}

    def metrics(self):
        if self._metrics is None: self.ensure_model()
        return self._metrics

    def options(self):
        return {"drugs":["Atorvastatin","Lisinopril","Metformin","Amlodipine","Levothyroxine","Omeprazole",
                         "Losartan","Gabapentin","Sertraline","Montelukast","Pantoprazole","Rosuvastatin"],
                "brand_status":["Generic","Brand"]}

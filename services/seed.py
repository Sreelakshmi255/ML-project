from werkzeug.security import generate_password_hash
from random import Random

def seed_database(db, User, HistoricalPrice):
    if not User.query.filter_by(email="demo@example.com").first():
        db.session.add(User(name="Demo Patient", email="demo@example.com",
                            password_hash=generate_password_hash("Demo@12345"), role="user"))
    if not User.query.filter_by(email="admin@example.com").first():
        db.session.add(User(name="System Administrator", email="admin@example.com",
                            password_hash=generate_password_hash("Admin@12345"), role="admin"))
    if HistoricalPrice.query.count() == 0:
        rng=Random(42)
        base={"Atorvastatin":12.0,"Lisinopril":9.5,"Metformin":11.0,"Amlodipine":10.0,"Levothyroxine":13.5,"Omeprazole":8.5}
        year=2024
        for drug,b in base.items():
            for status,mult in [("Generic",1.0),("Brand",2.15)]:
                value=b*mult
                for q in range(1,5):
                    value*=1+rng.uniform(-.03,.07)
                    db.session.add(HistoricalPrice(drug_name=drug,dosage_strength=20,
                        quarter=f"Q{q}",year=year,price=round(value,2),brand_status=status))
        db.session.commit()

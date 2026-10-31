import mysql.connector
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
from datetime import datetime

class HeartDiseaseRiskAnalyzer:
    def __init__(self, host, user, password, database):
        """Initialize database connection"""
        self.db_connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.db_connection.cursor()
        
    def add_patient(self, name, age, gender, contact_info):
        """Add a new patient to the database"""
        query = """
        INSERT INTO Patients (name, age, gender, contact_info)
        VALUES (%s, %s, %s, %s)
        """
        values = (name, age, gender, contact_info)
        self.cursor.execute(query, values)
        self.db_connection.commit()
        return self.cursor.lastrowid
    
    def add_medical_record(self, patient_id, cholesterol, bp_systolic, bp_diastolic, 
                          heart_rate, diabetes, family_history, smoker, obesity, exercise):
        """Add medical record for a patient"""
        query = """
        INSERT INTO MedicalRecords 
        (patient_id, record_date, cholesterol, blood_pressure_systolic, 
         blood_pressure_diastolic, heart_rate, diabetes, family_history, 
         smoker, obesity, exercise)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        record_date = datetime.now().date()
        values = (patient_id, record_date, cholesterol, bp_systolic, bp_diastolic,
                 heart_rate, diabetes, family_history, smoker, obesity, exercise)
        self.cursor.execute(query, values)
        self.db_connection.commit()
        return self.cursor.lastrowid
    
    def calculate_risk(self, record_id):
        """Calculate heart disease risk for a medical record"""
        # Fetch the medical record
        query = """
        SELECT cholesterol, blood_pressure_systolic, blood_pressure_diastolic, 
               heart_rate, diabetes, family_history, smoker, obesity, exercise
        FROM MedicalRecords
        WHERE record_id = %s
        """
        self.cursor.execute(query, (record_id,))
        record = self.cursor.fetchone()
        
        if not record:
            return None
            
        # Unpack record data
        (cholesterol, bp_sys, bp_dias, heart_rate, diabetes, 
         family_history, smoker, obesity, exercise) = record
        
        # Simple risk calculation (can be replaced with ML model)
        risk_score = 0
        
        # Cholesterol (mg/dL)
        if cholesterol > 240: risk_score += 3
        elif cholesterol > 200: risk_score += 2
        elif cholesterol > 180: risk_score += 1
        
        # Blood pressure (mmHg)
        if bp_sys >= 140 or bp_dias >= 90: risk_score += 3
        elif bp_sys >= 130 or bp_dias >= 85: risk_score += 2
        elif bp_sys >= 120 or bp_dias >= 80: risk_score += 1
        
        # Other factors
        if diabetes: risk_score += 2
        if family_history: risk_score += 2
        if smoker: risk_score += 2
        if obesity: risk_score += 1
        if exercise: risk_score -= 1
        
        # Determine risk category
        if risk_score >= 8: risk_category = "High"
        elif risk_score >= 5: risk_category = "Moderate"
        else: risk_category = "Low"
        
        # Store the assessment
        assessment_date = datetime.now().date()
        insert_query = """
        INSERT INTO RiskAssessments 
        (record_id, risk_score, risk_category, assessment_date)
        VALUES (%s, %s, %s, %s)
        """
        self.cursor.execute(insert_query, (record_id, risk_score, risk_category, assessment_date))
        self.db_connection.commit()
        
        return {
            'risk_score': risk_score,
            'risk_category': risk_category,
            'assessment_id': self.cursor.lastrowid
        }
    
    def train_ml_model(self):
        """Train a machine learning model on existing data"""
        # Fetch all medical records with risk assessments
        query = """
        SELECT m.cholesterol, m.blood_pressure_systolic, m.blood_pressure_diastolic,
               m.heart_rate, m.diabetes, m.family_history, m.smoker, m.obesity, m.exercise,
               r.risk_category
        FROM MedicalRecords m
        JOIN RiskAssessments r ON m.record_id = r.record_id
        """
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        
        if not data or len(data) < 100:
            print("Not enough data to train model. Need at least 100 records.")
            return None
            
        # Convert to DataFrame
        columns = ['cholesterol', 'bp_sys', 'bp_dias', 'heart_rate', 'diabetes', 
                   'family_history', 'smoker', 'obesity', 'exercise', 'risk_category']
        df = pd.DataFrame(data, columns=columns)
        
        # Convert risk categories to numerical values
        df['risk_numeric'] = df['risk_category'].map({'Low': 0, 'Moderate': 1, 'High': 2})
        
        # Prepare features and target
        X = df.drop(['risk_category', 'risk_numeric'], axis=1)
        y = df['risk_numeric']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Model trained with accuracy: {accuracy:.2f}")
        
        # Save model
        joblib.dump(model, 'heart_disease_risk_model.joblib')
        return model
    
    def predict_risk_with_ml(self, record_id, model_path='heart_disease_risk_model.joblib'):
        """Predict risk using trained ML model"""
        try:
            model = joblib.load(model_path)
        except:
            print("Model not found. Please train the model first.")
            return None
            
        # Fetch the medical record
        query = """
        SELECT cholesterol, blood_pressure_systolic, blood_pressure_diastolic,
               heart_rate, diabetes, family_history, smoker, obesity, exercise
        FROM MedicalRecords
        WHERE record_id = %s
        """
        self.cursor.execute(query, (record_id,))
        record = self.cursor.fetchone()
        
        if not record:
            return None
            
        # Prepare data for prediction
        data = pd.DataFrame([record], columns=[
            'cholesterol', 'bp_sys', 'bp_dias', 'heart_rate', 
            'diabetes', 'family_history', 'smoker', 'obesity', 'exercise'
        ])
        
        # Make prediction
        prediction = model.predict(data)
        risk_categories = ['Low', 'Moderate', 'High']
        risk_category = risk_categories[prediction[0]]
        
        # Get probabilities
        probabilities = model.predict_proba(data)[0]
        
        # Store the assessment
        assessment_date = datetime.now().date()
        insert_query = """
        INSERT INTO RiskAssessments 
        (record_id, risk_score, risk_category, assessment_date)
        VALUES (%s, %s, %s, %s)
        """
        self.cursor.execute(insert_query, (record_id, probabilities.max(), risk_category, assessment_date))
        self.db_connection.commit()
        
        return {
            'risk_category': risk_category,
            'probabilities': {
                'Low': probabilities[0],
                'Moderate': probabilities[1],
                'High': probabilities[2]
            },
            'assessment_id': self.cursor.lastrowid
        }
    
    def get_patient_history(self, patient_id):
        """Get complete history for a patient"""
        query = """
        SELECT p.name, p.age, p.gender, 
               m.record_date, m.cholesterol, m.blood_pressure_systolic, m.blood_pressure_diastolic,
               r.risk_score, r.risk_category, r.assessment_date
        FROM Patients p
        JOIN MedicalRecords m ON p.patient_id = m.patient_id
        JOIN RiskAssessments r ON m.record_id = r.record_id
        WHERE p.patient_id = %s
        ORDER BY m.record_date DESC
        """
        self.cursor.execute(query, (patient_id,))
        records = self.cursor.fetchall()
        
        if not records:
            return None
            
        columns = ['name', 'age', 'gender', 'record_date', 'cholesterol', 'bp_sys', 
                   'bp_dias', 'risk_score', 'risk_category', 'assessment_date']
        return pd.DataFrame(records, columns=columns)
    
    def close_connection(self):
        """Close database connection"""
        self.cursor.close()
        self.db_connection.close()

# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = HeartDiseaseRiskAnalyzer(
    host="localhost",
    user="root",
    password=None,  # Explicitly set to None
    database="HeartDiseaseRiskDB"
    )
    
    try:
        # Add a patient
        patient_id = analyzer.add_patient(
            name="John Doe",
            age=45,
            gender="Male",
            contact_info="john.doe@example.com"
        )
        
        # Add medical record
        record_id = analyzer.add_medical_record(
            patient_id=patient_id,
            cholesterol=220,
            bp_systolic=135,
            bp_diastolic=85,
            heart_rate=72,
            diabetes=True,
            family_history=True,
            smoker=False,
            obesity=True,
            exercise=True
        )
        
        # Calculate risk (simple method)
        risk_result = analyzer.calculate_risk(record_id)
        print(f"Risk Assessment (Simple Method): {risk_result}")
        
        # Train ML model (requires existing data in database)
        # analyzer.train_ml_model()
        
        # Predict risk with ML model
        # ml_risk_result = analyzer.predict_risk_with_ml(record_id)
        # print(f"Risk Assessment (ML Method): {ml_risk_result}")
        
        # Get patient history
        history = analyzer.get_patient_history(patient_id)
        print("\nPatient History:")
        print(history)
        
    finally:
        analyzer.close_connection()
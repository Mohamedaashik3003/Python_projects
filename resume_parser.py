from flask import Flask, request, jsonify
import pdfplumber
import spacy
import psycopg2

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

def extract_info(text):
    doc = nlp(text)
    name = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    skills = [token.text for token in doc if token.pos_ == "NOUN"]
    return {"name": name[0] if name else "Unknown", "skills": list(set(skills))}

def save_to_db(data):
    conn = psycopg2.connect(dbname="resumes", user="postgres", password="pass")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS candidates (name TEXT, skills TEXT)")
    cursor.execute("INSERT INTO candidates (name, skills) VALUES (%s, %s)", 
                   (data["name"], ', '.join(data["skills"])))
    conn.commit()
    conn.close()

@app.route("/upload", methods=["POST"])
def upload_resume():
    file = request.files["resume"]
    with pdfplumber.open(file) as pdf:
        text = "".join(page.extract_text() for page in pdf.pages if page.extract_text())
    data = extract_info(text)
    save_to_db(data)
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)

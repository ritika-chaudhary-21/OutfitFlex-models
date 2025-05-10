# outfit_api.py
from flask import Flask, request, jsonify
import pandas as pd
from rapidfuzz import fuzz  # faster and easier to install than fuzzywuzzy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Load dataset
OUTFIT_CSV = 'Dataset.csv'
df = pd.read_csv(OUTFIT_CSV)
df.columns = df.columns.str.strip()
df.fillna('', inplace=True)

# Scoring logic
def score_row(row, query):
    score = 0
    if query.get('occasion') and query['occasion'].lower() == row['Occasion'].lower():
        score += 5
    if query.get('style_name'):
        score += fuzz.partial_ratio(query['style_name'].lower(), row['Style Name'].lower())
    for key, col in [('top', 'Top'), ('bottom', 'Bottom'), ('layer', 'Layer'), ('dresses', 'Dresses')]:
        if query.get(key):
            score += fuzz.partial_ratio(query[key].lower(), row[col].lower())
    return score

@app.route('/recommend', methods=['POST'])
def recommend():
    query = request.json
    df['score'] = df.apply(score_row, axis=1, query=query)
    results = df[df['score'] > 0].sort_values(by='score', ascending=False).head(5)

    outfits = results.to_dict(orient='records')
    return jsonify({'results': outfits})

if __name__ == '__main__':
    app.run(debug=True)

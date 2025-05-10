from flask import Flask, request, jsonify
from fuzzywuzzy import fuzz
import pandas as pd

app = Flask(__name__)
df = pd.read_csv('Dataset.csv').fillna('')
df.columns = df.columns.str.strip()

def score_row(row, query):
    score = 0
    if query.get('occasion') and query['occasion'].lower() == row['Occasion'].lower():
        score += 5
    if query.get('style_name'):
        score += fuzz.partial_ratio(query['style_name'].lower(), row['Style Name'].lower())
    for key, colname in [('top', 'Top'), ('bottom', 'Bottom'), ('layer', 'Layer'), ('dresses', 'Dresses')]:
        if query.get(key):
            score += fuzz.partial_ratio(query[key].lower(), row[colname].lower())
    return score

@app.route("/recommend", methods=["POST"])
def recommend():
    query = request.json
    df['score'] = df.apply(score_row, axis=1, query=query)
    results = df[df['score'] > 0].sort_values(by='score', ascending=False).head(5)
    return jsonify(results.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)

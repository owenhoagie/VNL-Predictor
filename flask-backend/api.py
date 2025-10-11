
import sys
import os
from flask import Flask, request, jsonify
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../ML')))
import ml

app = Flask(__name__)

def predict_match_api(teamA, teamB):
    try:
        feats = ml.build_matchup_features(teamA, teamB)
        model_data = ml.joblib.load(ml.MODEL_PATH)
        clf_full = model_data['model']
        columns = model_data['columns']
        X_pred = ml.pd.DataFrame([feats])
        X_pred = X_pred.reindex(columns=columns, fill_value=0)
        X_pred = X_pred.apply(ml.pd.to_numeric, errors='coerce').fillna(0)
        proba = clf_full.predict_proba(X_pred)[0]
        probA, probB = proba[1], proba[0]
        if probA >= probB:
            winner, loser, conf = teamA, teamB, float(probA)
        else:
            winner, loser, conf = teamB, teamA, float(probB)
        set_score = None
        set_score_conf = None
        if os.path.exists(ml.SET_SCORE_MODEL_PATH):
            set_score_data = ml.joblib.load(ml.SET_SCORE_MODEL_PATH)
            set_score_clf = set_score_data['model']
            set_score_columns = set_score_data['columns']
            X_pred_set = X_pred.reindex(columns=set_score_columns, fill_value=0)
            for col in set_score_columns:
                if col.startswith('winner_'):
                    X_pred_set[col] = 1 if col == f'winner_{winner}' else 0
            X_pred_set['win_prob'] = conf
            X_pred_set['feature_diff'] = X_pred.abs().sum(axis=1).values[0]
            set_score_proba = set_score_clf.predict_proba(X_pred_set)[0]
            set_score_classes = set_score_data['set_score_classes'] if 'set_score_classes' in set_score_data else set_score_clf.classes_
            top_idx = set_score_proba.argmax()
            set_score = set_score_classes[top_idx]
            set_score_conf = float(set_score_proba[top_idx])
        return {
            'winner': winner,
            'winner_confidence': conf,
            'set_score': set_score,
            'set_score_confidence': set_score_conf
        }
    except Exception as e:
        return {'error': str(e)}

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.get_json()
    teamA = data.get('teamA')
    teamB = data.get('teamB')
    if not teamA or not teamB:
        return jsonify({'error': 'Both teamA and teamB must be provided.'}), 400
    result = predict_match_api(teamA, teamB)
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)

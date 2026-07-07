from flask import Flask, render_template, request, jsonify
from engine import analyze, run_whatif, WHATIF_SCENARIOS, SEASON_LABELS, GOAL_LABELS
app = Flask(__name__)
SOILS    = ["loamy","sandy","clayey","silty","black cotton",
            "alluvial","red laterite","peaty"]
SEASONS  = list(SEASON_LABELS.keys())
NITROS   = ["low","medium","high"]
WATERS   = ["rainfed","partial","full"]
WATER_LABELS = {"rainfed":"Rainfed Only","partial":"Partial Irrigation","full":"Full Irrigation"}
def parse_form(form):
    return {
        "soil":      form.get("soil","loamy"),
        "season":    form.get("season","kharif"),
        "rainfall":  float(form["rainfall"])  if form.get("rainfall")  else None,
        "temp":      float(form["temp"])       if form.get("temp")      else None,
        "ph":        float(form.get("ph", 6.5)),
        "nitrogen":  form.get("nitrogen","medium"),
        "water":     form.get("water","partial"),
        "farm_size": float(form.get("farm_size", 5) or 5),
        "goal":      form.get("goal","profit"),
    }
@app.route("/")
def index():
    return render_template("index.html",
        soils=SOILS, seasons=SEASONS, season_labels=SEASON_LABELS,
        nitros=NITROS, waters=WATERS, water_labels=WATER_LABELS,
        goal_labels=GOAL_LABELS)
@app.route("/analyze", methods=["POST"])
def analyze_route():
    inp    = parse_form(request.form)
    result = analyze(inp)
    return render_template("results.html", **result,
        water_labels=WATER_LABELS)
@app.route("/whatif", methods=["POST"])
def whatif_route():
    data        = request.get_json()
    inp         = data["inp"]
    inp["rainfall"] = inp["rainfall"] or None
    inp["temp"]     = inp["temp"]     or None
    scenario_id = data["scenario_id"]
    orig_ranked = data["orig_ranked"]
    from engine import CROPS, score_crop, compute_risk, calc_profit
    orig_map = {r["crop_id"]: r["pct"] for r in orig_ranked}
    result = run_whatif(scenario_id, inp, [{"pct": v, "crop": next(c for c in CROPS if c["id"]==k)}
                                            for k,v in orig_map.items()])
    # NOTE: top_mover is the same dict object as one of the entries in
    # result["results"] (max() returns a reference, not a copy), so its
    # "crop" key must be read before the loop below deletes it — and the
    # final cleanup must tolerate it already being gone.
    result["top_mover"]["crop_name"]  = result["top_mover"]["crop"]["name"]
    result["top_mover"]["crop_emoji"] = result["top_mover"]["crop"]["emoji"]
    for r in result["results"]:
        r["crop_name"]  = r["crop"]["name"]
        r["crop_emoji"] = r["crop"]["emoji"]
        r["crop_id"]    = r["crop"]["id"]
        r.pop("crop", None)
    result["top_mover"].pop("crop", None)
    return jsonify(result)
if __name__ == "__main__":
    app.run(debug=True, port=5001)

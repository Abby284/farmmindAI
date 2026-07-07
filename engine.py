"""
FarmMind AI — Core Engine
All AI logic: scoring, risk, rotation, soil memory, what-if
"""

import copy

# ══════════════════════════════════════════════
# CROP DATABASE
# ══════════════════════════════════════════════

CROPS = [
    {"id":"rice",      "name":"Rice",       "emoji":"🌾",
     "soils":["alluvial","loamy","clayey","black cotton"],
     "seasons":["kharif","tropical"],
     "rain":(1000,3000),"temp":(20,40),"ph":(5.5,7.0),
     "nitrogen":["medium","high"],"water":["rainfed","partial","full"],
     "goals":["yield","profit"],"duration":"90-120 days",
     "price_per_qt":2200,"yield_per_acre":20,"cost_per_acre":18000,
     "tags":["Staple crop","Water-intensive","High yield"],
     "soil_effect":"neutral","soil_delta":{"ph":-0.05,"nitrogen_shift":0,"water_demand":"high"}},

    {"id":"wheat",     "name":"Wheat",      "emoji":"🌿",
     "soils":["loamy","alluvial","silty","clayey"],
     "seasons":["rabi"],
     "rain":(300,1000),"temp":(10,25),"ph":(6.0,7.5),
     "nitrogen":["medium","high"],"water":["partial","full"],
     "goals":["yield","profit"],"duration":"100-130 days",
     "price_per_qt":2100,"yield_per_acre":18,"cost_per_acre":14000,
     "tags":["Winter crop","Staple","Stable price"],
     "soil_effect":"neutral","soil_delta":{"ph":0.0,"nitrogen_shift":-1,"water_demand":"medium"}},

    {"id":"maize",     "name":"Maize",      "emoji":"🌽",
     "soils":["loamy","sandy","alluvial","red laterite"],
     "seasons":["kharif","zaid","semi-arid"],
     "rain":(500,1200),"temp":(18,35),"ph":(5.8,7.0),
     "nitrogen":["medium","high"],"water":["rainfed","partial"],
     "goals":["yield","profit"],"duration":"70-90 days",
     "price_per_qt":1900,"yield_per_acre":22,"cost_per_acre":12000,
     "tags":["Versatile","Fast growing","Feed crop"],
     "soil_effect":"neutral","soil_delta":{"ph":-0.05,"nitrogen_shift":-1,"water_demand":"medium"}},

    {"id":"soybean",   "name":"Soybean",    "emoji":"🫘",
     "soils":["loamy","black cotton","alluvial","silty"],
     "seasons":["kharif","tropical"],
     "rain":(500,1000),"temp":(20,30),"ph":(6.0,7.0),
     "nitrogen":["low","medium"],"water":["rainfed","partial"],
     "goals":["profit","soil","organic"],"duration":"80-120 days",
     "price_per_qt":4000,"yield_per_acre":10,"cost_per_acre":9000,
     "tags":["N-fixer","Oil crop","Protein-rich"],
     "soil_effect":"positive","soil_delta":{"ph":0.0,"nitrogen_shift":2,"water_demand":"low"}},

    {"id":"cotton",    "name":"Cotton",     "emoji":"🌸",
     "soils":["black cotton","alluvial","loamy"],
     "seasons":["kharif","semi-arid"],
     "rain":(600,1200),"temp":(25,40),"ph":(6.0,8.0),
     "nitrogen":["medium","high"],"water":["partial","full"],
     "goals":["profit","yield"],"duration":"150-180 days",
     "price_per_qt":6500,"yield_per_acre":6,"cost_per_acre":22000,
     "tags":["Cash crop","High value","Export"],
     "soil_effect":"depleting","soil_delta":{"ph":0.1,"nitrogen_shift":-2,"water_demand":"high"}},

    {"id":"groundnut", "name":"Groundnut",  "emoji":"🥜",
     "soils":["sandy","loamy","red laterite"],
     "seasons":["kharif","zaid","semi-arid"],
     "rain":(400,1000),"temp":(22,35),"ph":(6.0,7.5),
     "nitrogen":["low","medium"],"water":["rainfed","partial"],
     "goals":["profit","soil"],"duration":"90-130 days",
     "price_per_qt":5200,"yield_per_acre":8,"cost_per_acre":10000,
     "tags":["Drought-hardy","Oil seed","N-fixer"],
     "soil_effect":"positive","soil_delta":{"ph":0.0,"nitrogen_shift":1,"water_demand":"low"}},

    {"id":"sunflower", "name":"Sunflower",  "emoji":"🌻",
     "soils":["loamy","alluvial","sandy","silty"],
     "seasons":["rabi","zaid","semi-arid"],
     "rain":(300,800),"temp":(15,35),"ph":(6.0,7.5),
     "nitrogen":["medium"],"water":["rainfed","partial"],
     "goals":["profit","water"],"duration":"85-110 days",
     "price_per_qt":5100,"yield_per_acre":7,"cost_per_acre":8000,
     "tags":["Low water","Fast growing","Oil seed"],
     "soil_effect":"neutral","soil_delta":{"ph":0.0,"nitrogen_shift":-1,"water_demand":"low"}},

    {"id":"lentils",   "name":"Lentils",    "emoji":"🫙",
     "soils":["loamy","silty","clayey","alluvial"],
     "seasons":["rabi"],
     "rain":(200,700),"temp":(8,22),"ph":(6.0,8.0),
     "nitrogen":["low"],"water":["rainfed","partial"],
     "goals":["soil","organic","water"],"duration":"80-100 days",
     "price_per_qt":5500,"yield_per_acre":5,"cost_per_acre":6000,
     "tags":["Legume","N-fixer","Low input"],
     "soil_effect":"positive","soil_delta":{"ph":0.0,"nitrogen_shift":2,"water_demand":"low"}},

    {"id":"chickpea",  "name":"Chickpea",   "emoji":"🟡",
     "soils":["loamy","sandy","alluvial","red laterite"],
     "seasons":["rabi","semi-arid"],
     "rain":(200,700),"temp":(10,30),"ph":(6.0,8.0),
     "nitrogen":["low","medium"],"water":["rainfed","partial"],
     "goals":["soil","water","organic"],"duration":"90-110 days",
     "price_per_qt":5000,"yield_per_acre":6,"cost_per_acre":6500,
     "tags":["Drought-hardy","High protein","N-fixer"],
     "soil_effect":"positive","soil_delta":{"ph":0.0,"nitrogen_shift":1,"water_demand":"low"}},

    {"id":"mustard",   "name":"Mustard",    "emoji":"🌼",
     "soils":["loamy","alluvial","sandy"],
     "seasons":["rabi","semi-arid"],
     "rain":(300,900),"temp":(10,25),"ph":(6.0,7.5),
     "nitrogen":["medium"],"water":["rainfed","partial"],
     "goals":["profit","water"],"duration":"85-110 days",
     "price_per_qt":4800,"yield_per_acre":8,"cost_per_acre":7500,
     "tags":["Cold-tolerant","Oil crop","Quick harvest"],
     "soil_effect":"neutral","soil_delta":{"ph":0.0,"nitrogen_shift":-1,"water_demand":"low"}},

    {"id":"tomato",    "name":"Tomato",     "emoji":"🍅",
     "soils":["loamy","silty","sandy","alluvial"],
     "seasons":["rabi","zaid","tropical"],
     "rain":(400,1000),"temp":(15,32),"ph":(5.5,7.5),
     "nitrogen":["medium","high"],"water":["partial","full"],
     "goals":["profit","yield"],"duration":"70-100 days",
     "price_per_qt":1500,"yield_per_acre":60,"cost_per_acre":28000,
     "tags":["High value","Vegetable","Market crop"],
     "soil_effect":"depleting","soil_delta":{"ph":-0.1,"nitrogen_shift":-2,"water_demand":"high"}},

    {"id":"turmeric",  "name":"Turmeric",   "emoji":"🟠",
     "soils":["loamy","red laterite","alluvial"],
     "seasons":["kharif","tropical"],
     "rain":(1000,2500),"temp":(20,35),"ph":(5.5,7.5),
     "nitrogen":["medium","high"],"water":["partial","full"],
     "goals":["profit","organic"],"duration":"7-10 months",
     "price_per_qt":8000,"yield_per_acre":12,"cost_per_acre":20000,
     "tags":["Spice","Export market","High price"],
     "soil_effect":"neutral","soil_delta":{"ph":-0.05,"nitrogen_shift":-1,"water_demand":"medium"}},

    {"id":"greengram", "name":"Green Gram", "emoji":"🫛",
     "soils":["loamy","sandy","red laterite","alluvial"],
     "seasons":["kharif","zaid","semi-arid"],
     "rain":(400,1000),"temp":(22,38),"ph":(6.0,7.5),
     "nitrogen":["low","medium"],"water":["rainfed","partial"],
     "goals":["soil","water","organic"],"duration":"55-75 days",
     "price_per_qt":7000,"yield_per_acre":4,"cost_per_acre":5500,
     "tags":["Fast growing","N-fixer","Pulse"],
     "soil_effect":"positive","soil_delta":{"ph":0.0,"nitrogen_shift":1,"water_demand":"low"}},
]

NEXT_SEASON = {
    "kharif":"rabi","rabi":"zaid","zaid":"kharif",
    "tropical":"tropical","semi-arid":"semi-arid",
}
SEASON_LABELS = {
    "kharif":"Kharif (Jun–Oct)","rabi":"Rabi (Nov–Mar)",
    "zaid":"Zaid (Apr–Jun)","tropical":"Tropical Year-Round","semi-arid":"Semi-Arid",
}
NITROGEN_LEVELS = ["low","medium","high"]
GOAL_LABELS = {
    "yield":"Maximum Yield","profit":"High Profit","soil":"Soil Health",
    "water":"Water Efficiency","organic":"Organic Farming",
}

# ══════════════════════════════════════════════
# HEURISTIC SCORING
# ══════════════════════════════════════════════

def score_crop(crop, inp):
    params = {}

    if inp["soil"] in crop["soils"]:
        params["Soil"] = {"score":25,"max":25,"note":"Perfect match"}
    elif any(inp["soil"].startswith(s.split()[0]) for s in crop["soils"]):
        params["Soil"] = {"score":12,"max":25,"note":"Partial match"}
    else:
        params["Soil"] = {"score":0,"max":25,"note":"Poor fit"}

    if inp["season"] in crop["seasons"]:
        params["Season"] = {"score":25,"max":25,"note":"Ideal season"}
    else:
        params["Season"] = {"score":2,"max":25,"note":"Off-season"}

    if inp.get("rainfall") is not None:
        lo,hi = crop["rain"]; r = inp["rainfall"]
        if lo <= r <= hi:
            params["Rainfall"] = {"score":15,"max":15,"note":f"{r:.0f}mm — ideal"}
        else:
            dist = min(abs(r-lo),abs(r-hi))
            params["Rainfall"] = {"score":round(max(0,15-dist/100)),"max":15,
                                   "note":"Too dry" if r<lo else "Too wet"}
    else:
        params["Rainfall"] = {"score":7,"max":15,"note":"Not specified"}

    if inp.get("temp") is not None:
        lo,hi = crop["temp"]; t = inp["temp"]
        if lo <= t <= hi:
            params["Temperature"] = {"score":15,"max":15,"note":f"{t:.0f}°C — ideal"}
        else:
            dist = min(abs(t-lo),abs(t-hi))
            params["Temperature"] = {"score":round(max(0,15-dist*2)),"max":15,
                                      "note":"Too cold" if t<lo else "Too hot"}
    else:
        params["Temperature"] = {"score":7,"max":15,"note":"Not specified"}

    lo,hi = crop["ph"]; ph = inp["ph"]
    if lo <= ph <= hi:
        params["pH"] = {"score":10,"max":10,"note":f"pH {ph} — optimal"}
    else:
        dist = min(abs(ph-lo),abs(ph-hi))
        params["pH"] = {"score":round(max(0,10-dist*6)),"max":10,
                         "note":"Too acidic" if ph<lo else "Too alkaline"}

    params["Water"]    = ({"score":5,"max":5,"note":"Compatible"}
                          if inp["water"] in crop["water"]
                          else {"score":1,"max":5,"note":"Mismatch"})
    params["Nitrogen"] = ({"score":3,"max":3,"note":"Compatible"}
                          if inp["nitrogen"] in crop["nitrogen"]
                          else {"score":1,"max":3,"note":"Sub-optimal"})
    params["Goal"]     = ({"score":2,"max":2,"note":"Aligned"}
                          if inp["goal"] in crop["goals"]
                          else {"score":0,"max":2,"note":"Different priority"})

    total     = sum(p["score"] for p in params.values())
    max_total = sum(p["max"]   for p in params.values())
    pct       = round((total / max_total) * 100)
    return pct, params


# ══════════════════════════════════════════════
# RISK ANALYSIS
# ══════════════════════════════════════════════

RISK_MARGIN = 0.15

def compute_risk(crop, inp):
    flags = []

    if inp.get("rainfall") is not None:
        lo,hi = crop["rain"]; r = inp["rainfall"]; span = hi-lo
        if lo <= r <= hi and span > 0:
            if min(r-lo, hi-r)/span < RISK_MARGIN:
                flags.append(f"Rainfall near {'lower' if (r-lo)<(hi-r) else 'upper'} limit ({r:.0f}mm, range {lo}–{hi}mm)")

    if inp.get("temp") is not None:
        lo,hi = crop["temp"]; t = inp["temp"]; span = hi-lo
        if lo <= t <= hi and span > 0:
            if min(t-lo, hi-t)/span < RISK_MARGIN:
                flags.append(f"Temperature at {'cold' if (t-lo)<(hi-t) else 'heat'} edge ({t:.0f}°C, range {lo}–{hi}°C)")

    lo,hi = crop["ph"]; ph = inp["ph"]; span = hi-lo
    if lo <= ph <= hi and span > 0:
        if min(ph-lo, hi-ph)/span < RISK_MARGIN:
            flags.append(f"pH near boundary ({ph}, optimal {lo}–{hi})")

    if inp["water"] == "rainfed"  and crop["soil_delta"]["water_demand"] == "high":
        flags.append("Crop needs high water — rainfed may be insufficient")
    if inp["water"] == "partial"  and crop["soil_delta"]["water_demand"] == "high":
        flags.append("Water-intensive crop — partial irrigation may reduce yield")
    if inp["nitrogen"] == "low"   and "high" in crop["nitrogen"] and "low" not in crop["nitrogen"]:
        flags.append("Crop needs high nitrogen — low soil N may cut yield 20-30%")

    level = "LOW" if len(flags)==0 else ("MEDIUM" if len(flags)<=2 else "HIGH")
    return level, flags


# ══════════════════════════════════════════════
# PROFIT CALCULATION
# ══════════════════════════════════════════════

def calc_profit(crop, farm_size):
    gross    = round(crop["yield_per_acre"] * farm_size * crop["price_per_qt"])
    cost     = round(crop["cost_per_acre"]  * farm_size)
    net      = gross - cost
    roi      = round((net / cost) * 100) if cost else 0
    be_drop  = round(((gross - cost) / gross) * 100) if gross else 0
    return {"gross":gross,"cost":cost,"net":net,"roi":roi,"be_drop":be_drop}


# ══════════════════════════════════════════════
# ROTATION PLANNER
# ══════════════════════════════════════════════

def plan_rotation(ranked, inp):
    top  = ranked[0]["crop"]
    s1   = inp["season"]
    s2   = NEXT_SEASON.get(s1,"rabi")
    s3   = NEXT_SEASON.get(s2,"zaid")
    used = {top["id"]}

    s2c = sorted([c for c in CROPS if s2 in c["seasons"] and c["id"] not in used],
                 key=lambda c: 0 if c["soil_effect"]=="positive" else 1) if top["soil_effect"]=="depleting" \
          else [c for c in CROPS if s2 in c["seasons"] and c["id"] not in used]
    s2_crop = s2c[0] if s2c else CROPS[1]
    used.add(s2_crop["id"])

    s3c = [c for c in CROPS if s3 in c["seasons"] and c["id"] not in used]
    s3_crop = s3c[0] if s3c else CROPS[2]

    rotation = []
    for season, crop, note in [(s1,top,"Primary — highest match"),
                                (s2,s2_crop,"N-fixer restores soil" if s2_crop["soil_effect"]=="positive" else "Best seasonal fit"),
                                (s3,s3_crop,"Completes cycle — breaks pest cycle")]:
        p = calc_profit(crop, inp["farm_size"])
        rotation.append({
            "season": season,
            "season_label": SEASON_LABELS.get(season, season),
            "crop": crop,
            "note": note,
            "net": p["net"],
        })
    return rotation


# ══════════════════════════════════════════════
# SOIL MEMORY
# ══════════════════════════════════════════════

def simulate_soil_memory(inp, seasons=4):
    soil = {"ph": inp["ph"], "nitrogen": inp["nitrogen"],
            "season": inp["season"], "health": 100}
    N_IDX = {"low":0,"medium":1,"high":2}
    history = []
    used = set()

    for _ in range(seasons):
        cur = copy.deepcopy(inp)
        cur["ph"] = soil["ph"]; cur["nitrogen"] = soil["nitrogen"]; cur["season"] = soil["season"]

        candidates = sorted(
            [(score_crop(c,cur)[0],c) for c in CROPS
             if soil["season"] in c["seasons"] and c["id"] not in used],
            key=lambda x: -x[0]
        ) or sorted([(score_crop(c,cur)[0],c) for c in CROPS if soil["season"] in c["seasons"]],
                    key=lambda x: -x[0])

        pct, chosen = candidates[0]
        delta = chosen["soil_delta"]

        new_ph = round(max(4.0, min(9.0, soil["ph"] + delta["ph"])), 2)
        n_idx  = max(0, min(2, N_IDX.get(soil["nitrogen"],1) + delta["nitrogen_shift"]))
        new_n  = NITROGEN_LEVELS[n_idx]

        if   chosen["soil_effect"] == "positive":  soil["health"] = min(100, soil["health"]+8);  status = "restored"
        elif chosen["soil_effect"] == "depleting": soil["health"] = max(0,   soil["health"]-12); status = "depleted"
        else:                                       soil["health"] = max(0,   soil["health"]-3);  status = "neutral"

        history.append({
            "season_label": SEASON_LABELS.get(soil["season"], soil["season"]),
            "crop": chosen,
            "ph": new_ph,
            "nitrogen": new_n,
            "health": soil["health"],
            "status": status,
            "ph_warn": "acidic" if new_ph < 5.5 else ("alkaline" if new_ph > 7.8 else ""),
        })
        soil["ph"] = new_ph; soil["nitrogen"] = new_n
        soil["season"] = NEXT_SEASON.get(soil["season"],"kharif")
        used = {chosen["id"]}

    final = soil["health"]
    advice = ("Critical: Soil severely degraded — grow a nitrogen-fixing legume next season."
              if final < 50 else
              "Caution: Moderate health — intercrop with green manure or legume."
              if final < 75 else
              "Healthy: Soil in good condition — current strategy is sustainable.")
    return history, final, advice


# ══════════════════════════════════════════════
# WHAT-IF ENGINE
# ══════════════════════════════════════════════

WHATIF_SCENARIOS = [
    {"id":"irrigation", "label":"Add full irrigation",          "desc":"Water → full irrigation"},
    {"id":"nitrogen",   "label":"Upgrade nitrogen to high",     "desc":"Nitrogen → high"},
    {"id":"rainfall",   "label":"Increase rainfall +300mm",     "desc":"Rainfall +300mm"},
    {"id":"temp_down",  "label":"Decrease temperature by 5°C",  "desc":"Temperature −5°C"},
    {"id":"soil_goal",  "label":"Change goal to Soil Health",   "desc":"Goal → Soil Health"},
]

def run_whatif(scenario_id, inp, original_ranked):
    mod = copy.deepcopy(inp)
    if   scenario_id == "irrigation": mod["water"]    = "full"
    elif scenario_id == "nitrogen":   mod["nitrogen"] = "high"
    elif scenario_id == "rainfall":   mod["rainfall"] = (mod.get("rainfall") or 500) + 300
    elif scenario_id == "temp_down":  mod["temp"]     = (mod.get("temp") or 28) - 5
    elif scenario_id == "soil_goal":  mod["goal"]     = "soil"

    new_scored = sorted(
        [(score_crop(c,mod)[0],c) for c in CROPS], key=lambda x: -x[0]
    )

    orig_map = {r["crop"]["id"]: r["pct"] for r in original_ranked}
    results  = []
    for new_rank, (new_pct, crop) in enumerate(new_scored[:6]):
        old_pct = orig_map.get(crop["id"], 0)
        results.append({
            "rank":    new_rank+1,
            "crop":    crop,
            "old_pct": old_pct,
            "new_pct": new_pct,
            "delta":   new_pct - old_pct,
        })

    desc = next((s["desc"] for s in WHATIF_SCENARIOS if s["id"]==scenario_id), scenario_id)
    top_mover = max(results, key=lambda x: abs(x["delta"]))
    return {"scenario": desc, "results": results, "top_mover": top_mover}


# ══════════════════════════════════════════════
# MAIN ANALYZE FUNCTION
# ══════════════════════════════════════════════

def analyze(inp):
    """Full analysis — returns structured dict for the Flask template."""
    ranked_raw = sorted(
        [(*(score_crop(c, inp)), c) for c in CROPS], key=lambda x: -x[0]
    )
    ranked = [{"pct": pct, "params": params, "crop": crop,
               "risk_level": compute_risk(crop, inp)[0],
               "risk_flags": compute_risk(crop, inp)[1],
               "profit": calc_profit(crop, inp["farm_size"])}
              for pct, params, crop in ranked_raw]

    rotation       = plan_rotation(ranked, inp)
    soil_history, soil_final, soil_advice = simulate_soil_memory(inp)
    top            = ranked[0]["crop"]
    n_fixer        = next((r["crop"] for r in ranked
                           if r["crop"]["soil_effect"]=="positive" and r["crop"]["id"]!=top["id"]), None)

    return {
        "inp":          inp,
        "ranked":       ranked,
        "rotation":     rotation,
        "soil_history": soil_history,
        "soil_final":   soil_final,
        "soil_advice":  soil_advice,
        "top":          top,
        "n_fixer":      n_fixer,
        "whatif_scenarios": WHATIF_SCENARIOS,
        "season_labels": SEASON_LABELS,
        "goal_labels":   GOAL_LABELS,
    }
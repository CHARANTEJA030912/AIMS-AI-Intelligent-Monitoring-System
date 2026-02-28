def calculate_risk(anomaly_prediction, anomaly_score, cpu, ram, net_sent, net_recv):
    risk_score = 0

    if anomaly_prediction == -1:
        risk_score += 50

    if cpu > 85:
        risk_score += 15

    if ram > 85:
        risk_score += 15

    if net_sent > 50 or net_recv > 50:
        risk_score += 20

    if risk_score < 30:
        severity = "LOW"
    elif risk_score < 70:
        severity = "MEDIUM"
    else:
        severity = "HIGH"

    return risk_score, severity
"use client";

import { Activity, AlertTriangle, Gauge, ShieldCheck, TrendingDown, TrendingUp } from "lucide-react";
import { useEffect, useState } from "react";

type Risk = { demo: boolean; var_95: number; var_99: number; sharpe: number; max_drawdown: number; beta_bist100: number; altman_z_score: number };

export default function StockAssessment({ symbol }: { symbol: string }) {
  const [risk, setRisk] = useState<Risk | null>(null);
  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    fetch(`${apiUrl}/api/v1/stocks/${symbol}/risk`).then((response) => response.json()).then(setRisk).catch(() => undefined);
  }, [symbol]);
  const metric = (label: string, value: string, tone = "") => <div className="assessment-metric"><span className="mono">{label}</span><strong className={tone}>{value}</strong></div>;
  return <aside className="assessment-card panel"><div className="assessment-heading"><div><div className="mono muted-label">HIZLI DEĞERLENDİRME</div><h2>{symbol} görünümü</h2></div><ShieldCheck color="#64e6b3" size={21} /></div><div className="assessment-signal"><div className="signal-gauge"><Gauge size={18} /><strong>{risk ? (risk.sharpe > 1 ? "72" : "48") : "--"}</strong></div><div><b>{risk ? (risk.sharpe > 1 ? "Dengeli momentum" : "Temkinli") : "Analiz hazırlanıyor"}</b><small className="mono">{risk?.demo ? "Sentetik risk serisi" : "API risk serisi"}</small></div></div><div className="assessment-grid">{metric("VaR %95", risk ? `%${risk.var_95.toFixed(2)}` : "--", "negative")}{metric("VaR %99", risk ? `%${risk.var_99.toFixed(2)}` : "--", "negative")}{metric("Sharpe", risk?.sharpe.toFixed(2) ?? "--", "positive")}{metric("Beta / BIST", risk?.beta_bist100.toFixed(2) ?? "--")}{metric("Max drawdown", risk ? `%${risk.max_drawdown.toFixed(2)}` : "--", "negative")}{metric("Altman Z", risk?.altman_z_score.toFixed(2) ?? "--", "positive")}</div><div className="assessment-foot mono"><Activity size={14} /> Risk verisi analiz amaçlıdır; yatırım tavsiyesi değildir.</div></aside>;
}

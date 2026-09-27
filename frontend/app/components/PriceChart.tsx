"use client";

import { useEffect, useState } from "react";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type ChartPoint = { time: string; close: number };
type Period = "day" | "month" | "year";
const periodLabels: { key: Period; label: string }[] = [{ key: "day", label: "Gün" }, { key: "month", label: "Ay" }, { key: "year", label: "Yıl" }];

function fallbackPoints(): ChartPoint[] {
  return Array.from({ length: 24 }, (_, index) => ({ time: `${index + 1}`, close: 100 + Math.sin(index / 2) * 2 + index / 5 }));
}

export default function PriceChart({ symbol, height = 300, compact = false }: { symbol: string; height?: number; compact?: boolean }) {
  const [period, setPeriod] = useState<Period>(compact ? "day" : "month");
  const [points, setPoints] = useState<ChartPoint[]>([]);
  const [source, setSource] = useState("Veri bekleniyor");

  useEffect(() => {
    const controller = new AbortController();
    const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    setPoints([]);
    fetch(`${apiUrl}/api/v1/stocks/${symbol}/prices?period=${period}`, { signal: controller.signal })
      .then((response) => response.json())
      .then((data: { prices?: ChartPoint[]; source?: string }) => { setPoints(data.prices?.length ? data.prices : fallbackPoints()); setSource(data.source ?? "Demo veri"); })
      .catch((error: unknown) => { if (error instanceof DOMException && error.name === "AbortError") return; setPoints(fallbackPoints()); setSource("Demo fallback"); });
    return () => controller.abort();
  }, [period, symbol]);

  return <div className="price-chart-shell"><div className="chart-toolbar"><div className="mono chart-source">{source}</div><div className="period-switcher">{periodLabels.map((item) => <button className={period === item.key ? "active" : ""} key={item.key} onClick={() => setPeriod(item.key)}>{item.label}</button>)}</div></div><div style={{ height }} className="price-chart">{points.length ? <ResponsiveContainer width="100%" height="100%"><AreaChart data={points}><defs><linearGradient id={`price-fill-${symbol}`} x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#64e6b3" stopOpacity={.3} /><stop offset="100%" stopColor="#64e6b3" stopOpacity={0} /></linearGradient></defs><XAxis dataKey="time" tick={{ fill: "#718590", fontSize: 10 }} axisLine={false} tickLine={false} minTickGap={24} /><YAxis tick={{ fill: "#718590", fontSize: 10 }} axisLine={false} tickLine={false} width={48} domain={["auto", "auto"]} /><Tooltip contentStyle={{ background: "#111a22", border: "1px solid #263843", color: "#e6eef1" }} labelStyle={{ color: "#8ca0aa" }} /><Area type="monotone" dataKey="close" stroke="#64e6b3" strokeWidth={2} fill={`url(#price-fill-${symbol})`} dot={false} /></AreaChart></ResponsiveContainer> : <div className="chart-loading mono">VERİ YÜKLENİYOR</div>}</div></div>;
}
